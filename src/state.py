import glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "state", "state.json")


def load():
    if os.path.exists(PATH):
        return json.load(open(PATH, encoding="utf-8"))
    return {"published": [], "rejected": [], "pending": None, "tg_offset": 0}


def save(s):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
        f.write("\n")


def topic_files():
    return sorted(glob.glob(os.path.join(ROOT, "topics", "*.json")))


def next_topic(s):
    done = {x["id"] for x in s["published"]} | {x["id"] for x in s["rejected"]}
    for p in topic_files():
        t = json.load(open(p, encoding="utf-8"))
        if t["id"] not in done:
            return p, t
    return None, None


def remaining(s):
    done = {x["id"] for x in s["published"]} | {x["id"] for x in s["rejected"]}
    return sum(1 for p in topic_files() if json.load(open(p, encoding="utf-8"))["id"] not in done)
