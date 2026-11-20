"""End-to-end test with Telegram, Pexels and Instagram mocked (no network).
Run: PIPER_MODEL=... python -m pytest -q tests  (or python tests/test_pipeline.py)"""
import io, json, os, re, shutil, sys, tempfile
import responses
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import state as S

TG = "https://api.telegram.org/botTEST"


def s_caption():
    t = json.load(open(os.path.join(S.ROOT, "topics", "001-turkiyenin-en-buyuk-10-golu.json"), encoding="utf-8"))
    return (t["aciklama"] + "\n\n" + " ".join(t["etiketler"])).strip()


def jpeg():
    b = io.BytesIO(); Image.new("RGB", (1200, 1800), (40, 120, 160)).save(b, "JPEG"); return b.getvalue()


def run():
    # responses does not validate timeouts; make sure no call passes an invalid one (bug seen in production)
    import requests.adapters as _ad
    _orig_send = _ad.HTTPAdapter.send
    import requests as _rq
    for _m in ("get", "post"):
        _f = getattr(_rq, _m)
        def _wrap(*a, _f=_f, **k):
            t = k.get("timeout")
            assert t is None or (t if not isinstance(t, tuple) else min(t)) > 0, f"invalid timeout {t!r}"
            return _f(*a, **k)
        setattr(_rq, _m, _wrap)
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
    from src import hosting
    hosted = []
    hosting.publish = lambda b, name: (hosted.append(name), f"https://raw.githubusercontent.com/o/r/media/{name}")[1]
    hosting.cleanup = lambda: hosted.append("cleanup")
    os.environ["IG_LOGIN"] = "instagram"
    G = "https://graph.instagram.com/v25.0"
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rs:
        rs.add(responses.POST, f"{TG}/getUpdates", json={"ok": True, "result": [
            {"update_id": 100, "callback_query": {"id": "cbX", "from": {"id": 999}, "data": f"ok|{key}", "message": {"chat": {"id": 999}}}},
            {"update_id": 101, "callback_query": {"id": "cb1", "from": {"id": 42}, "data": f"ok|{key}", "message": {"chat": {"id": 42}}}}]})
        rs.add(responses.POST, f"{TG}/answerCallbackQuery", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/getFile", json={"ok": True, "result": {"file_path": "videos/f.mp4"}})
        rs.add(responses.GET, "https://api.telegram.org/file/botTEST/videos/f.mp4", body=b"\x00" * 1000)
        # resumable is refused on Instagram Login -> must fall back to video_url
        rs.add(responses.POST, f"{G}/1789/media", status=400, json={"error": {"message": "upload_type not supported"}},
               match=[responses.matchers.urlencoded_params_matcher({"media_type": "REELS", "upload_type": "resumable",
                      "caption": s_caption(), "share_to_feed": "true", "access_token": "IGT"})])
        rs.add(responses.POST, f"{G}/1789/media", json={"id": "C1"},
               match=[responses.matchers.urlencoded_params_matcher({"media_type": "REELS",
                      "video_url": f"https://raw.githubusercontent.com/o/r/media/{key}.mp4",
                      "caption": s_caption(), "share_to_feed": "true", "access_token": "IGT"})])
        rs.add(responses.GET, re.compile(G.replace(".", r"\.") + r"/C1\?.*"), json={"status_code": "IN_PROGRESS"})
        rs.add(responses.GET, re.compile(G.replace(".", r"\.") + r"/C1\?.*"), json={"status_code": "FINISHED"})
        rs.add(responses.POST, f"{G}/1789/media_publish", json={"id": "M1"})
        rs.add(responses.GET, re.compile(G.replace(".", r"\.") + r"/M1\?.*"), json={"permalink": "https://instagram.com/reel/X"})
        rs.add(responses.POST, f"{TG}/editMessageReplyMarkup", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/sendMessage", json={"ok": True, "result": {"message_id": 9}})
        approve.main()
        answered = [c.request.body for c in rs.calls if c.request.url.endswith("answerCallbackQuery")]
        assert len(answered) == 1 and "cb1" in answered[0], "stranger's button must be ignored"
    assert hosted == [f"{key}.mp4", "cleanup"], hosted

    # Facebook Login path: resumable upload succeeds, no public URL is made
    hosted.clear()
    os.environ["IG_LOGIN"] = "facebook"
    GF = "https://graph.facebook.com/v25.0"
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rs:
        rs.add(responses.POST, f"{GF}/1789/media", json={"id": "C2", "uri": "https://rupload.facebook.com/ig-api-upload/v25.0/C2"})
        rs.add(responses.POST, "https://rupload.facebook.com/ig-api-upload/v25.0/C2", json={"success": True},
               match=[responses.matchers.header_matcher({"Authorization": "OAuth IGT", "offset": "0", "file_size": "5"})])
        rs.add(responses.GET, re.compile(GF.replace(".", r"\.") + r"/C2\?.*"), json={"status_code": "FINISHED"})
        rs.add(responses.POST, f"{GF}/1789/media_publish", json={"id": "M2"})
        rs.add(responses.GET, re.compile(GF.replace(".", r"\.") + r"/M2\?.*"), json={"permalink": "https://instagram.com/reel/Y"})
        assert instagram.publish_reel(b"12345", "c", public_url_fn=lambda b: hosted.append("x")) == ("M2", "https://instagram.com/reel/Y")
    assert hosted == []
    os.environ["IG_LOGIN"] = "instagram"

    # token refresh: new token is stored as the repo secret
    from src import refresh_token as RT
    stored = {}
    RT.store_secret = lambda n, v: stored.update({n: v})
    os.environ["GH_PAT"] = "PAT"
    with responses.RequestsMock() as rs:
        rs.add(responses.GET, re.compile(r"https://graph\.instagram\.com/refresh_access_token\?.*"),
               json={"access_token": "IGT2", "token_type": "bearer", "expires_in": 5184000})
        RT.main()
    assert stored == {"IG_ACCESS_TOKEN": "IGT2"}, stored
    print("instagram login / facebook login / token refresh ok")

    s = json.load(open(S.PATH))
    assert s["pending"] is None and s["published"][0]["permalink"] == "https://instagram.com/reel/X", s
    assert s["tg_offset"] == 102
    assert S.next_topic(s)[1]["id"] == "dunyanin-en-yuksek-10-dagi"
    print("approve ok →", s["published"][0])

    # waiting mode (daily job): nothing at first, then a ❌ arrives while long polling -> handled, loop exits
    s["pending"] = {"key": "K2", "topic_id": "x", "file_id": "F", "message_id": 5, "caption": "c"}
    S.save(s)
    os.environ["WAIT_SECONDS"] = "120"
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rs:
        rs.add(responses.POST, f"{TG}/getUpdates", json={"ok": True, "result": []})
        rs.add(responses.POST, f"{TG}/getUpdates", json={"ok": True, "result": [
            {"update_id": 200, "callback_query": {"id": "cb9", "from": {"id": 42}, "data": "no|K2", "message": {"chat": {"id": 42}}}}]})
        rs.add(responses.POST, f"{TG}/answerCallbackQuery", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/editMessageReplyMarkup", json={"ok": True, "result": True})
        rs.add(responses.POST, f"{TG}/sendMessage", json={"ok": True, "result": {"message_id": 10}})
        approve.main()
        polls = [c.request.body for c in rs.calls if c.request.url.endswith("getUpdates")]
        assert "timeout=0" in polls[0] and "timeout=50" in polls[1], polls
    s = json.load(open(S.PATH))
    assert s["pending"] is None and s["rejected"][-1]["id"] == "x" and s["tg_offset"] == 201, s
    os.environ["WAIT_SECONDS"] = "0"
    print("wait mode ok")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    run()

def test_pipeline():
    run()
