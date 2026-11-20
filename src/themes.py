import datetime as dt

THEMES = {
    "okyanus":   dict(top=(6, 22, 48),  bot=(4, 90, 120),  accent=(255, 205, 60),  soft=(170, 225, 240), circle=(60, 200, 230),  ink=(10, 30, 50),  motif="waves"),
    "gunbatimi": dict(top=(28, 8, 46),  bot=(190, 64, 58), accent=(255, 220, 110), soft=(255, 205, 190), circle=(255, 140, 90),  ink=(40, 10, 30),  motif="sun"),
    "zumrut":    dict(top=(3, 26, 22),  bot=(12, 104, 76), accent=(196, 255, 96),  soft=(170, 240, 210), circle=(70, 220, 160),  ink=(5, 35, 25),   motif="hills"),
    "gece":      dict(top=(6, 6, 22),   bot=(36, 22, 84),  accent=(110, 225, 255), soft=(200, 190, 255), circle=(150, 120, 255), ink=(10, 10, 40),  motif="stars"),
    "magma":     dict(top=(18, 5, 6),   bot=(112, 22, 18), accent=(255, 176, 48),  soft=(255, 200, 170), circle=(255, 96, 60),   ink=(40, 10, 5),   motif="embers"),
    "neon":      dict(top=(8, 8, 20),   bot=(20, 36, 84),  accent=(255, 84, 176),  soft=(170, 210, 255), circle=(80, 200, 255),  ink=(20, 5, 25),   motif="grid"),
}


def pick_theme(_topic_id=None, day=None):
    """Rotate through the themes by calendar day, so consecutive days never repeat."""
    day = day or dt.date.today()
    names = list(THEMES)
    return names[day.toordinal() % len(names)]
