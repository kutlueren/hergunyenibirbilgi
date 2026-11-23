"""Helper for writing topic files: builds the narration lead-ins ("Onuncu sırada…", "Ve bir numara…")."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIRA = ["Onuncu", "Dokuzuncu", "Sekizinci", "Yedinci", "Altıncı", "Beşinci", "Dördüncü", "Üçüncü", "İkinci"]


def topic(fname, id_, baslik, kanca, kanca_ses, birim, gorsel, items, aciklama, etiketler,
          kapanis_vurgu="biliyordun?", notlar=None, olcek=None, kapanis_ust="Sen hangisini"):
    """items: (ad, deger, yer, [bilgi1, bilgi2], seslendirme, foto[, extra dict]) from smallest to largest."""
    n = len(items)
    maddeler = []
    for i, row in enumerate(items):
        ad, deger, yer, bilgi, ses, foto = row[:6]
        sira = n - i
        lead = "Ve bir numara" if sira == 1 else SIRA[10 - n + i] + (" sırada" if i == 0 else "")
        m = {"sira": sira, "ad": ad, "deger": deger, "yer": yer, "bilgi": bilgi,
             "seslendirme": f"{lead}, {ses}", "foto": foto}
        if len(row) > 6: m.update(row[6])
        maddeler.append(m)
    t = {"id": id_, "baslik": baslik, "kanca": kanca, "kanca_seslendirme": kanca_ses,
         "birim": birim, "gorsel": gorsel, "maddeler": maddeler, "kapanis_ust": kapanis_ust, "kapanis_vurgu": kapanis_vurgu,
         "kapanis_seslendirme": f"{kapanis_ust} {kapanis_vurgu} Yorumlara yaz, ve takip etmeyi unutma!",
         "aciklama": aciklama, "etiketler": etiketler}
    if olcek: t["olcek"] = olcek
    if notlar: t["notlar"] = notlar
    import sys; sys.path.insert(0, ROOT)
    from src.spoilers import find_spoilers
    sp = find_spoilers(t)
    if sp:
        raise ValueError(f"{fname}: the #1 answer leaks outside the #1 scene: {sp}")
    with open(os.path.join(ROOT, "topics", fname), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1); f.write("\n")
