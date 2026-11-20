"""Read the Telegram buttons and publish (or drop) the pending video.

WAIT_SECONDS=0     look once and exit (hourly backup run)
WAIT_SECONDS=N     keep listening (Telegram long polling) until the pending video is approved/rejected
                   or N seconds have passed. The daily job runs this right after sending the video,
                   so a button press is handled within seconds.
"""
import datetime as dt, os, sys, time, traceback

from . import state as S
from . import hosting
from .telegram import Telegram
from .instagram import publish_reel


def handle(tg, s, u):
    s["tg_offset"] = u["update_id"] + 1
    cb = u.get("callback_query")
    if not cb:
        print(f"- {u['update_id']}: buton değil ({', '.join(k for k in u if k != 'update_id')}), atlandı", flush=True)
        return
    action, _, key = cb.get("data", "").partition("|")
    from_id = str(cb["from"]["id"]); chat = str(cb.get("message", {}).get("chat", {}).get("id"))
    if from_id != tg.chat_id and chat != tg.chat_id:
        print(f"- {u['update_id']}: {action}|{key} başka birinden (…{from_id[-3:]}), atlandı", flush=True)
        return  # only the owner may approve
    print(f"- {u['update_id']}: {action}|{key}", flush=True)
    p = s.get("pending")
    if not p or p["key"] != key:
        tg.answer_callback(cb["id"], "Bu video artık beklemede değil.")
        return
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if action == "no":
        tg.answer_callback(cb["id"], "Reddedildi")
        tg.clear_buttons(p["message_id"])
        s["rejected"].append({"id": p["topic_id"], "date": now})
        s["pending"] = None
        tg.send_message(f"🗑️ Reddedildi, bu konu bir daha gelmeyecek: {p['topic_id']}")
    elif action == "ok":
        tg.answer_callback(cb["id"], "Paylaşılıyor…")
        tg.clear_buttons(p["message_id"])  # no double taps while uploading
        tg.send_message("⏳ Instagram'a yükleniyor…")
        try:
            video = tg.download(p["file_id"])
            mid, link = publish_reel(video, p["caption"],
                                     public_url_fn=lambda b: hosting.publish(b, f"{p['key']}.mp4"))
        except Exception as e:
            traceback.print_exc()
            tg.send_video_buttons(p["message_id"], p["key"])  # put the buttons back so it can be retried
            tg.send_message(f"❌ Instagram'a yüklenemedi: {e}\nTekrar denemek için ✅ Paylaş'a yeniden basabilirsin.")
            return
        finally:
            hosting.cleanup()
        s["published"].append({"id": p["topic_id"], "date": now, "ig_media_id": mid, "permalink": link})
        s["pending"] = None
        tg.send_message(f"✅ Instagram'da paylaşıldı! {link or ''}".strip())


def main():
    tg = Telegram()
    s = S.load()
    wait_total = int(os.environ.get("WAIT_SECONDS", "0"))
    start = time.monotonic()
    p0 = s.get("pending")
    print(f"bekleyen: {p0['key'] + ' ' + p0['topic_id'] if p0 else 'yok'}; dinleme süresi: {wait_total} sn", flush=True)
    first = True
    while True:
        left = wait_total - (time.monotonic() - start)
        wait = 0 if first else int(max(0, min(50, left)))
        first = False
        updates = tg.get_updates(s.get("tg_offset", 0), wait=wait)
        for u in updates:
            handle(tg, s, u)
            S.save(s)  # after every update, so a crash/cancel can't replay a handled button
        if not s.get("pending") or left <= 0:
            break
    S.save(s)
    print(f"bitti; bekleyen: {s['pending']['topic_id'] if s.get('pending') else 'yok'}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
