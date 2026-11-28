"""Turkish narration with the Piper 'Fahrettin' voice (CC0).

The text is cleaned (tts_text.clean), turned into phonemes by espeak, corrected word by word
(see fix_word) and only then synthesised. Corrections:
- espeak's Turkish rules read a "ü" in a closed syllable as "ö": "yüz" -> "yöz", so every year
  ("bin sekiz yüz...") and "yüzde" came out wrong. Those vowels are put back to "ü".
- PHONEMES holds hand-written pronunciations for words espeak gets wrong ("katil" -> KAAtil).
- English words are read in English: text in braces ({Tokyo Skytree}) and words in EN_WORDS are
  phonemised with espeak's English voice and mapped onto the sounds the Turkish voice knows,
  so the same Fahrettin voice says them the way a Turkish presenter would say English.
"""
import os, re, wave
import numpy as np

from .tts_text import clean

SPEED = float(os.environ.get("VOICE_SPEED", "1.05"))

# word (lower case, no punctuation) -> phonemes; "ˈ" marks the stressed syllable, "ː" a long vowel
PHONEMES = {
    "katil": "kˈaːtil",
}

# words that are always read in English (lower case). Avoid words that also exist in Turkish ("bay", "park").
EN_WORDS = {
    "tower", "towers", "stadium", "international", "airport", "center", "centre", "street", "square",
    "bridge", "building", "state", "empire", "trade", "world", "golden", "gate", "station", "central",
    "island", "lake", "mount", "river", "national", "university", "college", "hall", "house", "times",
    "new", "york", "angeles", "chicago", "atlanta", "dallas", "denver", "heathrow", "ohare", "o'hare",
    "jfk", "fort", "knox", "beaver", "ohio", "michigan", "shakespeare", "skytree", "cn", "pearl", "oriental",
    "washington", "hollywood", "silicon", "valley", "manhattan", "brooklyn", "boston", "seattle",
}

# English espeak phonemes -> sounds the Turkish voice was trained on
_EN_MAP = {
    "ɹ": "ɾ", "ɚ": "ɛɾ", "ɝ": "øɾ", "ɜ": "ø", "ə": "ɛ", "ɐ": "a", "ʌ": "a", "ɑ": "a", "ɒ": "o",
    "ɔ": "o", "ᵻ": "ɪ", "θ": "t", "ð": "d", "w": "v", "ʍ": "v", "ŋ": "nɡ", "ɾ": "d", "ʔ": "",
    "ʲ": "", "ɬ": "l", "x": "h", "ɡ": "ɡ",
}
_EN_DIPH = {"eɪ": "ej", "aɪ": "aj", "ɔɪ": "oj", "oʊ": "o", "aʊ": "av", "ɪə": "ɪɛ", "eə": "eɛ", "ʊə": "ʊɛ"}
_PUNCT = ".,!?;:"
_ESPEAK = None


def _english(word):
    """Phonemes for one English word, mapped onto the Turkish voice's sounds."""
    global _ESPEAK
    if _ESPEAK is None:
        import piper
        from piper.phonemize_espeak import EspeakPhonemizer
        _ESPEAK = EspeakPhonemizer(os.path.join(os.path.dirname(piper.__file__), "espeak-ng-data"))
    raw = "".join(ch for sent in _ESPEAK.phonemize("en-us", word) for ch in sent if ch != " ")
    # the English tap (as in "water") is already "ɾ"; turn it into "d" before "ɹ" becomes "ɾ"
    raw = raw.replace("ɾ", "d")
    for a, b in _EN_DIPH.items():
        raw = raw.replace(a, b)
    out = "".join(_EN_MAP.get(ch, ch) if ch != "ɾ" else ch for ch in raw)
    return list(out)


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


_PLACEHOLDER = "fırfırık"   # a made-up word: never in a narration line, always one espeak word


def _is_english(w):
    w = w.lower()
    return w in EN_WORDS or w.replace("'", "").replace("’", "") in EN_WORDS


def _mark_english(text):
    """Swaps English words for a placeholder word (so the Turkish clean-up and espeak leave them
    alone and word alignment still works). Returns the new text and, in order, (english, suffix)
    pairs; a Turkish suffix after an apostrophe ("O'Hare'da") is kept and read in Turkish."""
    english = []

    def swap(word, forced=False):
        m = re.match(r"^([\"(«]*)(.*?)([.,!?;:)»\"]*)$", word)
        lead, core, tail = m.groups()
        base, suffix = core, ""
        if not (forced or _is_english(core)):
            parts = re.split(r"['’]", core)
            if len(parts) < 2 or not _is_english("'".join(parts[:-1])):
                return word
            base, suffix = "'".join(parts[:-1]), parts[-1]
        elif forced:
            m2 = re.match(r"^(.*)['’](\w+)$", core)
            if m2 and "}" in m2.group(1): base, suffix = m2.group(1), m2.group(2)
        english.append((base.strip("{}"), suffix))
        return lead + _PLACEHOLDER + tail

    def braces(m):
        ws = m.group(1).split()
        if m.group(2): ws[-1] += "'" + m.group(2)
        out = []
        for w in ws:
            parts = re.split(r"['’]", w)
            if m.group(2) and w is ws[-1]:
                english.append(("'".join(parts[:-1]), parts[-1])); out.append(_PLACEHOLDER)
            else:
                english.append((w, "")); out.append(_PLACEHOLDER)
        return " ".join(out)
    text = re.sub(r"\{([^}]*)\}(?:['’](\w+))?", braces, text)
    text = " ".join(swap(w) if _PLACEHOLDER not in w else w for w in text.split())
    return text, english


def phonemes_for(pv, text):
    """Returns one phoneme list per sentence, corrected word by word.
    Words are lined up across the whole line (espeak sometimes merges or splits sentences)."""
    text, english = _mark_english(text)
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
        en = iter(english)
        fixed = []
        for w, p in zip(tw, flat):
            core = re.sub(r"[^\wçğıöşü]", "", _lower(w))
            if core.startswith(_PLACEHOLDER):
                word, suffix = next(en)
                ph = _english(word)
                if suffix:   # Turkish suffix, read with the Turkish voice
                    ph += [ch for sent in pv.phonemize(clean(suffix)) for ch in sent if ch not in " ˈˌ" + _PUNCT]
                fixed.append(ph + [ch for ch in p if ch in _PUNCT])
            else:
                fixed.append(fix_word(w, p))
        fixed = iter(fixed)
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
