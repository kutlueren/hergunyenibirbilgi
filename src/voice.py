"""Turkish narration with the Piper 'Fahrettin' voice (CC0)."""
import os, wave
import numpy as np

SPEED = float(os.environ.get("VOICE_SPEED", "1.05"))


def synthesize_all(lines, outdir, model_path):
    from piper import PiperVoice, SynthesisConfig
    os.makedirs(outdir, exist_ok=True)
    pv = PiperVoice.load(model_path)
    cfg = SynthesisConfig(length_scale=1 / SPEED, noise_scale=0.667, noise_w_scale=0.8)
    durs = {}
    for k, line in lines.items():
        chunks = list(pv.synthesize(line, syn_config=cfg))
        sr = chunks[0].sample_rate
        w = np.concatenate([c.audio_float_array for c in chunks]).astype(np.float32)
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
