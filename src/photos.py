"""Fetch portrait photos from Pexels for some of the items (free, commercial use allowed)."""
import os, random
import requests

from .util import slug

API = "https://api.pexels.com/v1/search"


def fetch(topic, outdir, api_key, ratio=0.5, seed=None, log=print):
    """Download photos for roughly `ratio` of the items that have a "foto" search term.
    Saves them as <outdir>/<slug(item name)>.jpg, which the renderer picks up as backgrounds."""
    os.makedirs(outdir, exist_ok=True)
    cands = [it for it in topic["maddeler"] if it.get("foto")]
    rnd = random.Random(seed)
    k = max(1, round(len(cands) * ratio)) if cands else 0
    chosen = rnd.sample(cands, min(k, len(cands)))
    # the #1 item gets a photo whenever it has a search term: it is the payoff of the video
    top = min(topic["maddeler"], key=lambda m: m["sira"])
    if top.get("foto") and top not in chosen: chosen.append(top)
    got = []
    for it in chosen:
        try:
            r = requests.get(API, params={"query": it["foto"], "orientation": "portrait", "per_page": 5, "size": "large"},
                             headers={"Authorization": api_key}, timeout=30)
            r.raise_for_status()
            photos = r.json().get("photos") or []
            if not photos:
                log(f"pexels: no result for {it['foto']!r}"); continue
            src = photos[0]["src"]["original"] + "?auto=compress&cs=tinysrgb&h=2200"
            img = requests.get(src, timeout=60); img.raise_for_status()
            with open(os.path.join(outdir, slug(it["ad"]) + ".jpg"), "wb") as f:
                f.write(img.content)
            got.append(it["ad"])
        except Exception as e:  # a missing photo must never stop the daily video
            log(f"pexels: {it['ad']}: {e}")
    return got
