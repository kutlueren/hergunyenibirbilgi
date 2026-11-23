"""Daily job: pick the next topic, render the video and send it to Telegram for approval."""
import datetime as dt, os, shutil, sys, traceback

from . import state as S
from .render import render
from .telegram import Telegram
from .photos import fetch as fetch_photos
from .themes import pick_theme
from .spoilers import find_spoilers, safe_caption
from .render import CAMERA_VISUALS
import random

ROOT = S.ROOT


def caption_for(t):
    """Instagram caption + hashtags. Never contains the #1 answer (see spoilers.py)."""
    return safe_caption(t)


SEND_WINDOW = (dt.time(11, 30), dt.time(13, 30))  # Berlin saati; video ~12:00'de gelsin


def main():
    s = S.load()
    now = dt.datetime.now()  # TZ=Europe/Berlin in the workflow
    today = now.date()
    key = today.strftime("%Y%m%d")
    if os.environ.get("EVENT") == "schedule":
        if not (SEND_WINDOW[0] <= now.time() <= SEND_WINDOW[1]):
            print(f"{now:%H:%M} gönderim penceresinin dışında, atlanıyor."); return
        if s.get("last_daily") == key:
            print("Bugünün videosu zaten gönderildi, atlanıyor."); return
    tg = Telegram()

    old = s.get("pending")
    if old:
        # not answered in time: the topic goes back into the queue
        tg.clear_buttons(old.get("message_id"))
        tg.send_message(f"⌛ Dünkü video onaylanmadı, konu sıraya geri döndü: {old['topic_id']}")
        s["pending"] = None

    path, topic = S.next_topic(s)
    if not topic:
        tg.send_message("⚠️ Konu bankası bitti! Yeni konu dosyaları eklenmeli (topics/ klasörü).")
        S.save(s); return

    work = os.path.join(ROOT, "work"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    img_dir = os.path.join(work, "images")
    got = []
    if os.environ.get("PEXELS_API_KEY"):
        got = fetch_photos(topic, img_dir, os.environ["PEXELS_API_KEY"],
                           ratio=float(os.environ.get("PHOTO_RATIO", "0.5")), seed=key)
    prev = s.get("last_theme") or (s["published"][-1].get("theme") if s.get("published") else None)
    # sometimes the classic scenes, sometimes the continuous camera animation (where the visual supports it)
    anim = random.choice(["kamera", "klasik"]) if topic.get("gorsel") in CAMERA_VISUALS else "klasik"
    theme = render(path, work, theme=pick_theme(exclude=prev), img_dir=img_dir, animasyon=anim)
    s["last_theme"] = theme

    cap = caption_for(topic)
    left = S.remaining(s) - 1
    msg = (f"📅 {today.strftime('%d.%m.%Y')} · {topic['id']}\n🎨 Tema: {theme} · 🎬 Stil: {'animasyonlu' if anim == 'kamera' else 'klasik'} · 📷 Foto: {len(got)}\n"
           f"📚 Kalan konu: {left}\n👉 ✅ Paylaş'a bastığın anda Instagram'a yüklenir.\n\n— Instagram açıklaması —\n{cap}")
    if topic.get("notlar"):
        msg += f"\n\n📝 Not: {topic['notlar']}"
    sp = find_spoilers(topic)
    if sp:
        msg += "\n\n⚠️ Cevabı erken veren yerler (açıklama/hashtag'den otomatik çıkarıldı; videodakileri kontrol et):\n" + \
               "\n".join(f"• {w}: {txt}" for w, txt in sp)
    res = tg.send_video_for_approval(os.path.join(work, "video.mp4"), msg, key)
    s["pending"] = {"key": key, "topic_id": topic["id"], "file_id": res["video"]["file_id"],
                    "message_id": res["message_id"], "caption": cap, "theme": theme,
                    "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    s["last_daily"] = key
    S.save(s)
    if left <= 5:
        tg.send_message(f"📚 Konu bankasında {left} konu kaldı, yenilerini eklemeyi unutma.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        try:
            Telegram().send_message(f"❌ Günlük video üretilemedi: {e}")
        except Exception:
            pass
        sys.exit(1)
