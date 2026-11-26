"""The #1 answer may only appear in the #1 scene. This finds every other place that gives it away:
the Instagram caption, the hashtags, the hook, and the scenes before #1."""
import re

STOP = {"gölü", "golu", "çölü", "okyanusu", "dağı", "adası", "ili", "ülkesi", "binası", "havalimanı", "dili",
        "the", "de", "ve", "okyanusya", "mandarin", "gezegen", "kulesi", "merkezi",
        "baraj", "barajı", "stadyumu", "tüneli", "köprüsü", "heykeli", "mont"}


def _low(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def tokens(name):
    t = re.sub(r"[()]", " ", _low(name))
    return [w for w in re.split(r"[\s\-–']+", t) if len(w) > 2 and w not in STOP]


def _hit(text, tks):
    tl = _low(text).replace("#", "")
    joined = tl.replace(" ", "")
    return [w for w in tks if w in tl] or ([" ".join(tks)] if len(tks) > 1 and "".join(tks) in joined else [])


def find_spoilers(topic):
    """Returns [(where, text)] for every place outside the #1 scene that names the #1 item."""
    top = min(topic["maddeler"], key=lambda m: m["sira"])
    tks = tokens(top["ad"])
    out = []
    if _hit(topic.get("aciklama", ""), tks): out.append(("açıklama", topic["aciklama"]))
    for h in topic.get("etiketler", []):
        if _hit(h, tks): out.append(("hashtag", h))
    if _hit(" ".join(topic.get("kanca", [])), tks): out.append(("açılış yazısı", " ".join(topic["kanca"])))
    if _hit(topic.get("kanca_seslendirme", ""), tks): out.append(("açılış seslendirmesi", topic["kanca_seslendirme"]))
    for m in topic["maddeler"]:
        if m is top: continue
        for txt in (" ".join(m.get("bilgi", [])), m.get("seslendirme", ""), m.get("yer", "")):
            if _hit(txt, tks): out.append((f"#{m['sira']} {m['ad']} sahnesi", txt))
    return out


def safe_caption(topic):
    """Caption + hashtags with every trace of the #1 answer removed."""
    top = min(topic["maddeler"], key=lambda m: m["sira"])
    tks = tokens(top["ad"])
    tags = [h for h in topic.get("etiketler", []) if not _hit(h, tks)]
    cap = topic.get("aciklama", "")
    if _hit(cap, tks):
        title = " ".join(topic["baslik"]).replace("  ", " ")
        cap = f"{title.capitalize()} 🤔 Sence 1 numara hangisi? Tahminini yorumlara yaz, cevap videonun sonunda! 👇"
    return (cap + ("\n\n" + " ".join(tags) if tags else "")).strip()
