"""Hourly job: read the Telegram buttons and publish (or drop) the pending video."""
import datetime as dt, sys, traceback

from . import state as S
from .telegram import Telegram
from .instagram import publish_reel
from . import hosting


def main():
    tg = Telegram()
    s = S.load()
    updates = tg.get_updates(s.get("tg_offset", 0))
    for u in updates:
        s["tg_offset"] = u["update_id"] + 1
        cb = u.get("callback_query")
        if not cb:
            continue
        if str(cb["from"]["id"]) != tg.chat_id and str(cb.get("message", {}).get("chat", {}).get("id")) != tg.chat_id:
            continue  # only the owner may approve
        action, _, key = cb.get("data", "").partition("|")
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
