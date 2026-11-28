"""Clean up narration text before it goes to the Turkish voice.

- Apostrophes are removed: "Türkiye'nin" -> "Türkiyenin". With the apostrophe the voice
  puts the stress on the suffix ("Türkiye'NİN"); without it the word is read naturally.
- Foreign names are rewritten the way a Turkish speaker says them (the voice reads letters
  with Turkish rules, so "Dhaulagiri" would come out as "d-h-aulagiri").
- Digits are spelled out, so a number that slips into a narration line is still read correctly.
Add new names to SPOKEN as topics need them.
"""
import re

SPOKEN = {
    "Dhaulagiri": "Davlagiri", "Cho Oyu": "Ço Oyu", "Lhotse": "Lotse", "Kangchenjunga": "Kançencunga",
    "Kangçencunga": "Kançencunga", "Guangzhou": "Guançu", "Shenzhen": "Şenzen", "Shanghai": "Şanghay",
    "Tianjin": "Tiencin", "UNESCO": "Yunesko", "TÜİK": "Tüik", "BAE": "Birleşik Arap Emirlikleri",
    "Mississippi": "Misisipi", "Missouri": "Missuri", "Yangtze": "Yangçe", "Ganymede": "Ganimed",
    "Aconcagua": "Akonkagua", "Victoria": "Viktorya", "Superior": "Süperior",
    "Ellesmere": "Ellesmir", "Honshu": "Honşu", "Burj Khalifa": "Burç Halife",
    "ABD": "A Be De", "km²": "kilometrekare", "km": "kilometre",
}

ONES = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def _below_1000(n):
    h, r = divmod(n, 100)
    t, o = divmod(r, 10)
    out = []
    if h: out.append(("" if h == 1 else ONES[h] + " ") + "yüz")
    if t: out.append(TENS[t])
    if o: out.append(ONES[o])
    return " ".join(out)


def number_words(n):
    n = int(n)
    if n == 0: return "sıfır"
    parts = []
    for value, name in ((10**9, "milyar"), (10**6, "milyon"), (1000, "bin")):
        q, n = divmod(n, value)
        if q:
            parts.append("bin" if (value == 1000 and q == 1) else f"{_below_1000(q)} {name}")
    if n: parts.append(_below_1000(n))
    return " ".join(parts)


def _num(m):
    s = m.group(0)
    if "," in s:
        a, b = s.split(",", 1)
        return f"{number_words(a.replace('.', ''))} virgül {number_words(b)}"
    return number_words(s.replace(".", ""))


def clean(text):
    for k in sorted(SPOKEN, key=len, reverse=True):
        text = re.sub(rf"(?<![\wçğıöşüÇĞİÖŞÜ]){re.escape(k)}(?![\wçğıöşüÇĞİÖŞÜ²])", SPOKEN[k], text)
    text = re.sub(r"(?<=[\wçğıöşüÇĞİÖŞÜ])['’](?=[\wçğıöşüÇĞİÖŞÜ])", "", text)
    text = re.sub(r"%\s*(\d)", r"yüzde \1", text)
    text = re.sub(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?", _num, text)
    return text
