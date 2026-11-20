"""Publish a Reel with the Instagram Graph API (Facebook Login for Business, resumable upload).
No public video URL is needed: the file bytes go straight to rupload.facebook.com."""
import os, time
import requests

V = os.environ.get("GRAPH_API_VERSION", "v25.0")
G = f"https://graph.facebook.com/{V}"


def _check(r):
    try:
        j = r.json()
    except Exception:
        r.raise_for_status(); raise
    if r.status_code >= 400 or "error" in j:
        raise RuntimeError(f"instagram: {j.get('error', j)}")
    return j


def publish_reel(video_bytes, caption, ig_user_id=None, token=None, log=print, poll_every=10, max_wait=900):
    ig_user_id = ig_user_id or os.environ["IG_USER_ID"]
    token = token or os.environ["IG_ACCESS_TOKEN"]
    # 1) create a resumable upload container
    j = _check(requests.post(f"{G}/{ig_user_id}/media", data={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption,
        "share_to_feed": "true", "access_token": token}, timeout=60))
    cid = j["id"]; uri = j.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{V}/{cid}"
    log(f"container {cid}")
    # 2) upload the bytes
    _check(requests.post(uri, data=video_bytes, timeout=600, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(video_bytes))}))
    # 3) wait until Instagram has processed the video
    waited = 0
    while True:
        st = _check(requests.get(f"{G}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=30))
        code = st.get("status_code")
        if code == "FINISHED": break
        if code in ("ERROR", "EXPIRED"): raise RuntimeError(f"instagram processing failed: {st}")
        if waited >= max_wait: raise RuntimeError(f"instagram processing timed out: {st}")
        time.sleep(poll_every); waited += poll_every
    # 4) publish
    pub = _check(requests.post(f"{G}/{ig_user_id}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=60))
    mid = pub["id"]
    link = None
    try:
        link = _check(requests.get(f"{G}/{mid}", params={"fields": "permalink", "access_token": token}, timeout=30)).get("permalink")
    except Exception:
        pass
    return mid, link
