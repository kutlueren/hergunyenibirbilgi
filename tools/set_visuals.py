"""Assigns the illustrated visual to each topic file (idempotent)."""
import json, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = {
    "turkiyenin-en-buyuk-10-golu": {"gorsel": "sekil", "stil": "su"},
    "dunyanin-en-yuksek-10-dagi": {"gorsel": "dag"},
    "dunyanin-en-buyuk-10-adasi": {"gorsel": "sekil", "stil": "kara", "items": {"Grönland": "buz"}},
    "turkiyenin-yuzolcumu-en-buyuk-10-ili": {"gorsel": "sekil", "stil": "kara"},
    "dunyanin-en-yuksek-10-binasi": {"gorsel": "bina"},
    "dunyanin-en-buyuk-10-ulkesi": {"gorsel": "sekil", "stil": "kara", "items": {"Cezayir": "col", "Avustralya": "col"}},
    "dunyanin-en-buyuk-10-golu": {"gorsel": "sekil", "stil": "su"},
    "turkiyenin-en-kalabalik-5-ili": {"gorsel": "ikon", "ikon": "insan", "ikon_deger": 1, "ikon_etiket": "1 milyon kişi"},
    "dunyanin-en-cok-turist-alan-5-ulkesi": {"gorsel": "ikon", "ikon": "insan", "ikon_deger": 10, "ikon_etiket": "10 milyon turist"},
    "dunyanin-en-yogun-8-havalimani": {"gorsel": "ikon", "ikon": "ucak", "ikon_deger": 10, "ikon_etiket": "10 milyon yolcu"},
    "dunyanin-en-cok-konusulan-8-dili": {"gorsel": "ikon", "ikon": "balon", "ikon_deger": 0.1, "ikon_etiket": "100 milyon kişi"},
    "dunyanin-en-buyuk-5-colu": {"gorsel": "sekil", "stil": "col", "items": {"Arktik Çölü": "buz", "Antarktika Çölü": "buz"}},
    "dunyanin-5-okyanusu": {"gorsel": "sekil", "stil": "su", "items": {"Arktik Okyanusu": "buz"}},
    "dunyanin-7-kitasi": {"gorsel": "sekil", "stil": "kara", "items": {"Antarktika": "buz", "Avustralya (Okyanusya)": "col"}},
    "gunes-sisteminin-8-gezegeni": {"gorsel": "gezegen"},
}
for p in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
    t = json.load(open(p, encoding="utf-8"))
    c = CFG.get(t["id"])
    if not c: continue
    for k, v in c.items():
        if k != "items": t[k] = v
    for m in t["maddeler"]:
        st = c.get("items", {}).get(m["ad"])
        if st: m["stil"] = st
        else: m.pop("stil", None)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1); f.write("\n")
    print(os.path.basename(p), "->", c["gorsel"])
