"""Publish a Reel on Instagram.

IG_LOGIN=instagram (default): Instagram API with Instagram Login (graph.instagram.com, Instagram user token).
IG_LOGIN=facebook:            Instagram API with Facebook Login (graph.facebook.com, Page token).

Upload: first tries the resumable upload (file bytes straight to rupload.facebook.com, no public URL needed).
Meta documents that only for Facebook Login, so if it is refused, the video is put on a temporary public URL
(see hosting.py) and Instagram fetches it from there (video_url).
"""
import os, time
import requests

V = os.environ.get("GRAPH_API_VERSION", "v25.0")


def login_type(token=None):
    """IG_LOGIN if set, otherwise guessed from the token: Instagram user tokens start with IGAA,
    Facebook user/page tokens with EAA."""
    v = os.environ.get("IG_LOGIN", "").strip().lower()
    if v in ("instagram", "facebook"):
        return v
    token = token or os.environ.get("IG_ACCESS_TOKEN", "")
    return "facebook" if token.startswith("EAA") else "instagram"


def _host(token=None):
    return "https://graph.facebook.com" if login_type(token) == "facebook" else "https://graph.instagram.com"


def _check(r):
    try:
        j = r.json()
    except Exception:
        r.raise_for_status(); raise
    if r.status_code >= 400 or (isinstance(j, dict) and "error" in j):
        raise RuntimeError(f"instagram: {j.get('error', j) if isinstance(j, dict) else j}")
    return j


def _wait(G, cid, token, log, poll_every, max_wait):
    waited = 0
    while True:
        st = _check(requests.get(f"{G}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=30))
        code = st.get("status_code")
        if code == "FINISHED": return
        if code in ("ERROR", "EXPIRED"): raise RuntimeError(f"instagram processing failed: {st}")
        if waited >= max_wait: raise RuntimeError(f"instagram processing timed out: {st}")
        time.sleep(poll_every); waited += poll_every


def _resumable(G, ig, token, video, caption, log):
    j = _check(requests.post(f"{G}/{ig}/media", data={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption,
        "share_to_feed": "true", "access_token": token}, timeout=60))
    cid = j["id"]; uri = j.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{V}/{cid}"
    _check(requests.post(uri, data=video, timeout=600, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(video))}))
    return cid


def _by_url(G, ig, token, url, caption):
    j = _check(requests.post(f"{G}/{ig}/media", data={
        "media_type": "REELS", "video_url": url, "caption": caption,
        "share_to_feed": "true", "access_token": token}, timeout=60))
    return j["id"]


def publish_reel(video_bytes, caption, public_url_fn=None, ig_user_id=None, token=None, log=print,
                 poll_every=10, max_wait=900):
    """public_url_fn(video_bytes) -> url  is called only if the direct upload is refused."""
    ig = ig_user_id or os.environ["IG_USER_ID"]
    token = token or os.environ["IG_ACCESS_TOKEN"]
    G = f"{_host(token)}/{V}"
    mode = os.environ.get("IG_UPLOAD_MODE", "auto")  # auto | resumable | url
    cid = None
    if mode in ("auto", "resumable"):
        try:
            cid = _resumable(G, ig, token, video_bytes, caption, log)
            log(f"resumable upload ok, container {cid}")
        except Exception as e:
            if mode == "resumable": raise
            log(f"resumable upload refused ({e}); falling back to video_url")
    if cid is None:
        if not public_url_fn:
            raise RuntimeError("direct upload refused and no public URL available")
        url = public_url_fn(video_bytes)
        log(f"video_url: {url}")
        cid = _by_url(G, ig, token, url, caption)
    _wait(G, cid, token, log, poll_every, max_wait)
    mid = _check(requests.post(f"{G}/{ig}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=60))["id"]
    link = None
    try:
        link = _check(requests.get(f"{G}/{mid}", params={"fields": "permalink", "access_token": token}, timeout=30)).get("permalink")
    except Exception:
        pass
    return mid, link


def refresh_token(token):
    """Instagram Login long-lived tokens last 60 days; refreshing (token must be >24h old) gives 60 more."""
    j = _check(requests.get("https://graph.instagram.com/refresh_access_token",
                            params={"grant_type": "ig_refresh_token", "access_token": token}, timeout=30))
    return j["access_token"], int(j.get("expires_in", 0))
