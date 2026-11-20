import datetime as dt
import random

THEMES = {
    "okyanus":   dict(top=(6, 22, 48),  bot=(4, 90, 120),  accent=(255, 205, 60),  soft=(170, 225, 240), circle=(60, 200, 230),  ink=(10, 30, 50),  motif="waves"),
    "gunbatimi": dict(top=(28, 8, 46),  bot=(190, 64, 58), accent=(255, 220, 110), soft=(255, 205, 190), circle=(255, 140, 90),  ink=(40, 10, 30),  motif="sun"),
    "zumrut":    dict(top=(3, 26, 22),  bot=(12, 104, 76), accent=(196, 255, 96),  soft=(170, 240, 210), circle=(70, 220, 160),  ink=(5, 35, 25),   motif="hills"),
    "gece":      dict(top=(6, 6, 22),   bot=(36, 22, 84),  accent=(110, 225, 255), soft=(200, 190, 255), circle=(150, 120, 255), ink=(10, 10, 40),  motif="stars"),
    "magma":     dict(top=(18, 5, 6),   bot=(112, 22, 18), accent=(255, 176, 48),  soft=(255, 200, 170), circle=(255, 96, 60),   ink=(40, 10, 5),   motif="embers"),
    "neon":      dict(top=(8, 8, 20),   bot=(20, 36, 84),  accent=(255, 84, 176),  soft=(170, 210, 255), circle=(80, 200, 255),  ink=(20, 5, 25),   motif="grid"),
    "kutup":     dict(top=(8, 20, 40),  bot=(40, 90, 140), accent=(150, 230, 255), soft=(210, 235, 250), circle=(120, 200, 255), ink=(10, 25, 45),  motif="snow"),
    "col":       dict(top=(30, 14, 6),  bot=(150, 80, 30), accent=(255, 214, 120), soft=(255, 220, 180), circle=(240, 160, 80),  ink=(40, 20, 5),   motif="dunes"),
    "aurora":    dict(top=(4, 10, 20),  bot=(10, 40, 50),  accent=(120, 255, 180), soft=(180, 240, 220), circle=(150, 110, 255), ink=(5, 20, 15),   motif="aurora"),
    "lavanta":   dict(top=(26, 12, 48), bot=(90, 40, 120), accent=(255, 170, 230), soft=(225, 200, 245), circle=(200, 140, 255), ink=(30, 10, 40),  motif="bokeh"),
    "safir":     dict(top=(4, 10, 40),  bot=(20, 50, 140), accent=(255, 200, 80),  soft=(180, 200, 255), circle=(90, 140, 255),  ink=(10, 15, 45),  motif="rings"),
    "mercan":    dict(top=(10, 30, 40), bot=(20, 110, 110), accent=(255, 130, 110), soft=(190, 240, 235), circle=(80, 210, 200),  ink=(10, 30, 35),  motif="waves"),
}


def pick_theme(_topic_id=None, day=None, exclude=None):
    """Random theme for every video, never the same as the previous one (`exclude`)."""
    names = [n for n in THEMES if n != exclude] or list(THEMES)
    return random.choice(names)
