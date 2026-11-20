"""Hourly job: read the Telegram buttons and publish (or drop) the pending video."""
import datetime as dt, os, sys, traceback

from . import state as S
from .telegram import Telegram
from .instagram import publish_reel
from . import hosting


def main():
    tg = Telegram()
    s = S.load()
    updates = tg.get_updates(s.get("tg_offset", 0))
    # started by hand: wait up to WAIT_SECONDS for a button press instead of looking once
    wait_total = int(os.environ.get("WAIT_SECONDS", "0")); waited = 0
    off = s.get("tg_offset", 0)
    while wait_total and waited < wait_total and not any(u.get("callback_query") for u in updates):
        if updates: off = updates[-1]["update_id"] + 1
        print(f"buton bekleniyor… ({waited}/{wait_total} sn)", flush=True)
        more = tg.get_updates(off, wait=min(50, wait_total - waited)); waited += 50
        updates = updates + more
    p0 = s.get("pending")
    print(f"offset {s.get('tg_offset', 0)}: {len(updates)} güncelleme; bekleyen: {p0['key'] + ' ' + p0['topic_id'] if p0 else 'yok'}")
    if not updates:
        try:
            wi = tg.webhook_info()
            print(f"webhook: {'VAR (getUpdates çalışmaz!)' if wi.get('url') else 'yok'}, bekleyen güncelleme: {wi.get('pending_update_count')}, "
                  f"son hata: {wi.get('last_error_message', '-')}, izinli tipler: {wi.get('allowed_updates', '-')}")
        except Exception as e:
            print(f"getWebhookInfo hata: {e}")
    for u in updates:
        s["tg_offset"] = u["update_id"] + 1
        cb = u.get("callback_query")
        if not cb:
            print(f"- {u['update_id']}: buton değil ({', '.join(k for k in u if k != 'update_id')}), atlandı")
            continue
        action, _, key = cb.get("data", "").partition("|")
        from_id = str(cb["from"]["id"]); chat = str(cb.get("message", {}).get("chat", {}).get("id"))
        if from_id != tg.chat_id and chat != tg.chat_id:
            print(f"- {u['update_id']}: {action}|{key} başka birinden (…{from_id[-3:]}), atlandı")
            continue  # only the owner may approve
        print(f"- {u['update_id']}: {action}|{key}")
        p = s.get("pending")
        if not p or p["key"] != key:
            tg.answer_callback(cb["id"], "Bu video artık beklemede değil.")
            continue
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        if action == "no":
            tg.answer_callback(cb["id"], "Reddedildi")
            tg.clear_buttons(p["message_id"])
            s["rejected"].append({"id": p["topic_id"], "date": now})
            s["pending"] = None
            tg.send_message(f"🗑️ Reddedildi, bu konu bir daha gelmeyecek: {p['topic_id']}")
        elif action == "ok":
            tg.answer_callback(cb["id"], "Paylaşılıyor…")
            try:
                video = tg.download(p["file_id"])
                mid, link = publish_reel(video, p["caption"],
                                         public_url_fn=lambda b: hosting.publish(b, f"{p['key']}.mp4"))
            except Exception as e:
                traceback.print_exc()
                tg.send_message(f"❌ Instagram'a yüklenemedi: {e}\nButona tekrar basarsan bir sonraki kontrolde yeniden denenir.")
                continue
            tg.clear_buttons(p["message_id"])
            s["published"].append({"id": p["topic_id"], "date": now, "ig_media_id": mid, "permalink": link})
            s["pending"] = None
            tg.send_message(f"✅ Instagram'da paylaşıldı! {link or ''}".strip())
        hosting.cleanup()
        S.save(s)  # save after every handled button so a later failure can't replay it
    S.save(s)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
