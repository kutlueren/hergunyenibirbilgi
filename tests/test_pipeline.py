"""End-to-end test with Telegram, Pexels and Instagram mocked (no network).
Run: PIPER_MODEL=... python -m pytest -q tests  (or python tests/test_pipeline.py)"""
import io, json, os, re, shutil, sys, tempfile
import responses
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import state as S

TG = "https://api.telegram.org/botTEST"


def jpeg():
    b = io.BytesIO(); Image.new("RGB", (1200, 1800), (40, 120, 160)).save(b, "JPEG"); return b.getvalue()


def run():
    tmp = tempfile.mkdtemp()
    S.PATH = os.path.join(tmp, "state.json")
    os.environ.update(TELEGRAM_BOT_TOKEN="TEST", TELEGRAM_CHAT_ID="42", PEXELS_API_KEY="PX",
                      IG_USER_ID="1789", IG_ACCESS_TOKEN="IGT")
    from src import daily, approve, instagram
    sent = {}

    with responses.RequestsMock(assert_all_requests_are_fired=False) as rs:
        rs.add(responses.GET, re.compile(r"https://api\.pexels\.com/v1/search.*"),
               json={"photos": [{"src": {"original": "https://images.pexels.com/p/1.jpg"}}]})
        rs.add(responses.GET, re.compile(r"https://images\.pexels\.com/p/1\.jpg.*"), body=jpeg())

        def send_video(req):
            sent["caption"] = re.search(rb'name="caption"\r\n\r\n(.*?)\r\n--', req.body, re.S).group(1).decode()
            return (200, {}, json.dumps({"ok": True, "result": {"message_id": 7, "video": {"file_id": "FILE1"}}}))
        rs.add_callback(responses.POST, f"{TG}/sendVideo", callback=send_video)
        rs.add(responses.POST, f"{TG}/sendMessage", json={"ok": True, "result": {"message_id": 8}})
        daily.main()

    s = json.load(open(S.PATH))
    assert s["pending"]["topic_id"] == "turkiyenin-en-buyuk-10-golu", s
    assert os.path.getsize(os.path.join(S.ROOT, "work", "video.mp4")) > 500_000
    assert len(os.listdir(os.path.join(S.ROOT, "work", "images"))) >= 3
    key = s["pending"]["key"]
    print("daily ok →", sent["caption"].splitlines()[0])

    instagram.time.sleep = lambda *_: None
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rs:
        rs.add(responses.POST, f"{TG}/getUpdates", json={"ok": True, "result": [
            {"update_id": 100, "callback_query": {"id": "cbX", "from": {"id": 999}, "data": f"ok|{key}", "message": {"chat": {"id": 999}}}},
            {"update_id": 101, "callback_query": {"id": "cb1", "from": {"id": 42}, "data": f"ok|{key}", "message": {"chat": {"id": 42}}}}]})
        rs.add(responses.POST, f"{TG}/answerCallbackQuery", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/getFile", json={"ok": True, "result": {"file_path": "videos/f.mp4"}})
        rs.add(responses.GET, "https://api.telegram.org/file/botTEST/videos/f.mp4", body=b"\x00" * 1000)
        rs.add(responses.POST, "https://graph.facebook.com/v25.0/1789/media",
               json={"id": "C1", "uri": "https://rupload.facebook.com/ig-api-upload/v25.0/C1"})
        rs.add(responses.POST, "https://rupload.facebook.com/ig-api-upload/v25.0/C1", json={"success": True},
               match=[responses.matchers.header_matcher({"Authorization": "OAuth IGT", "offset": "0", "file_size": "1000"})])
        rs.add(responses.GET, re.compile(r"https://graph\.facebook\.com/v25\.0/C1\?.*"), json={"status_code": "IN_PROGRESS"})
        rs.add(responses.GET, re.compile(r"https://graph\.facebook\.com/v25\.0/C1\?.*"), json={"status_code": "FINISHED"})
        rs.add(responses.POST, "https://graph.facebook.com/v25.0/1789/media_publish", json={"id": "M1"})
        rs.add(responses.GET, re.compile(r"https://graph\.facebook\.com/v25\.0/M1\?.*"), json={"permalink": "https://instagram.com/reel/X"})
        rs.add(responses.POST, f"{TG}/editMessageReplyMarkup", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/sendMessage", json={"ok": True, "result": {"message_id": 9}})
        approve.main()
        answered = [c.request.body for c in rs.calls if c.request.url.endswith("answerCallbackQuery")]
        assert len(answered) == 1 and "cb1" in answered[0], "stranger's button must be ignored"

    s = json.load(open(S.PATH))
    assert s["pending"] is None and s["published"][0]["permalink"] == "https://instagram.com/reel/X", s
    assert s["tg_offset"] == 102
    assert S.next_topic(s) == (None, None)
    print("approve ok →", s["published"][0])
    shutil.rmtree(tmp)


if __name__ == "__main__":
    run()

def test_pipeline():
    run()
