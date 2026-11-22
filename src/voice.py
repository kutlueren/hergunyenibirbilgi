"""Turkish narration with the Piper 'Fahrettin' voice (CC0).

The text is cleaned (tts_text.clean), turned into phonemes by espeak, corrected word by word
(see fix_word) and only then synthesised. Corrections:
- espeak's Turkish rules read a "ü" in a closed syllable as "ö": "yüz" -> "yöz", so every year
  ("bin sekiz yüz...") and "yüzde" came out wrong. Those vowels are put back to "ü".
- PHONEMES holds hand-written pronunciations for words espeak gets wrong ("katil" -> KAAtil).
"""
import os, re, wave
import numpy as np

from .tts_text import clean

SPEED = float(os.environ.get("VOICE_SPEED", "1.05"))

# word (lower case, no punctuation) -> phonemes; "ˈ" marks the stressed syllable, "ː" a long vowel
PHONEMES = {
    "katil": "kˈaːtil",
}

_LETTER_VOWELS = "aeıioöuüâîû"
_PHON_VOWELS = set("aæeɛɯiɪoɔøœuʊyʏ")
_TR_LOWER = str.maketrans("İIÂÎÛ", "iıâîû")


def _lower(w):
    return w.translate(_TR_LOWER).lower()


def fix_word(word, phon):
    """word: text word (may carry punctuation); phon: list of phoneme characters for that word."""
    core = re.sub(r"[^\wçğıöşüâîû]", "", _lower(word))
    if core in PHONEMES:
        tail = [ch for ch in phon if ch in ".,!?;:"]
        return list(PHONEMES[core]) + tail
    letters = [ch for ch in core if ch in _LETTER_VOWELS]
    idx = [i for i, ch in enumerate(phon) if ch in _PHON_VOWELS]
    if len(letters) == len(idx):
        phon = list(phon)
        for L, i in zip(letters, idx):
            if L == "ü" and phon[i] in ("ø", "œ"):
                phon[i] = "y"
    return phon


def phonemes_for(pv, text):
    """Returns one phoneme list per sentence, corrected word by word.
    Words are lined up across the whole line (espeak sometimes merges or splits sentences)."""
    text = clean(text)
    sentences = pv.phonemize(text)
    words_per_sent = []
    for sent in sentences:
        pw, cur = [], []
        for ch in sent:
            if ch == " ":
                if cur: pw.append(cur)
                cur = []
            else:
                cur.append(ch)
        if cur: pw.append(cur)
        words_per_sent.append(pw)
    flat = [w for ws in words_per_sent for w in ws]
    tw = text.split()
    if len(tw) == len(flat):
        fixed = iter([fix_word(w, p) for w, p in zip(tw, flat)])
        words_per_sent = [[next(fixed) for _ in ws] for ws in words_per_sent]
    else:
        print(f"[voice] word alignment failed ({len(tw)} vs {len(flat)}), uncorrected: {text[:60]}")
    return [[ch for i, p in enumerate(ws) for ch in (p + ([" "] if i < len(ws) - 1 else []))] for ws in words_per_sent]


def synth(pv, text, cfg):
    sr = pv.config.sample_rate
    parts = []
    for ph in phonemes_for(pv, text):
        audio = pv.phoneme_ids_to_audio(pv.phonemes_to_ids(ph), cfg)
        if isinstance(audio, tuple): audio = audio[0]
        a = np.asarray(audio, dtype=np.float32)
        if a.dtype.kind == "i" or np.abs(a).max() > 1.5: a = a / 32768.0
        parts += [a, np.zeros(int(0.12 * sr), np.float32)]
    return np.concatenate(parts[:-1]), sr


def synthesize_all(lines, outdir, model_path):
    from piper import PiperVoice, SynthesisConfig
    os.makedirs(outdir, exist_ok=True)
    pv = PiperVoice.load(model_path)
    cfg = SynthesisConfig(length_scale=1 / SPEED, noise_scale=0.667, noise_w_scale=0.8)
    durs = {}
    for k, line in lines.items():
        w, sr = synth(pv, line, cfg)
        thr = 0.01 * np.abs(w).max(); idx = np.where(np.abs(w) > thr)[0]
        w = w[max(0, idx[0] - 200): idx[-1] + int(0.08 * sr)]
        w = w / np.abs(w).max() * 0.9
        n = int(len(w) * 44100 / sr)
        w = np.interp(np.linspace(0, len(w) - 1, n), np.arange(len(w)), w)
        with wave.open(os.path.join(outdir, f"{k}.wav"), "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
            f.writeframes((w * 32767).astype(np.int16).tobytes())
        durs[k] = n / 44100
    return durs
