"""python tools/check_topics.py  ->  lists every topic that reveals its #1 answer outside the #1 scene."""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from src.spoilers import find_spoilers
bad = 0
for p in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
    sp = find_spoilers(json.load(open(p, encoding="utf-8")))
    print(("✗ " if sp else "✓ ") + os.path.basename(p) + ("".join(f"\n    {w}: {t}" for w, t in sp)))
    bad += bool(sp)
sys.exit(1 if bad else 0)
