"""Audio feasibility check: does a ball-strike transient show up in the sound, and does it line up with the skeleton's swing event?
Bandpass 1.2-3.5 kHz, spectral flux (half-wave rectified), peak inside +-0.6 s of the skeleton event. Free. Works on any Mac/VM with ffmpeg.
  python tests/audio_fetch.py --n 60   (Mac, VPN off)  then  python tests/audio_check.py --n 150   -> work/audio_check.txt
Needs ffmpeg to decode the audio (present in the Claude workspace)."""
import argparse, glob, json, os, random, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt, stft
sys.path.insert(0, ".")
from sphere import labelling
SR = 16000


def audio(vf, t0, t1):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t0):.2f}", "-t", f"{t1 - t0:.2f}", "-i", vf, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.int16).astype(np.float32) / 32768.0 if p.returncode == 0 else None


def flux(x, t_start):
    y = sosfilt(butter(4, [1200, 3500], btype="band", fs=SR, output="sos"), x)
    f, t, Z = stft(y, fs=SR, nperseg=256, noverlap=192); M = np.abs(Z)             # 4 ms hop
    sf = np.sum(np.maximum(M[:, 1:] - M[:, :-1], 0) ** 2, 0); return t[1:] + t_start, sf


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=120); a = ap.parse_args()
    lab = json.load(open("work/stroke_labels3.json")); ks = [k for k, v in lab.items() if v["stroke"] in ("forehand", "backhand", "serve") and v.get("confidence", 0) >= 2 and glob.glob(f"work/audio/{k.split('/')[1]}.*")]
    random.Random(4).shuffle(ks); out = []
    print(len(ks), 'windows have an audio file', flush=True)
    for k in ks:
        if len(out) >= a.n: break
        v = lab[k]; act, vid = k.split("/")[:2]; fa = glob.glob(f"work/audio/{vid}.*"); vf = fa[0] if fa else None   # audio files from tests/audio_fetch.py
        if not vf: continue
        pk = v["peak"]; t0 = pk - 3.0; x = audio(vf, t0, pk + 3.0)
        if x is None or len(x) < SR * 4: continue
        t, sf = flux(x, max(0.0, t0)); base = np.median(sf) + 1e-12; m = (t >= pk - 0.6) & (t <= pk + 0.6)
        if not m.any(): continue
        i = np.argmax(np.where(m, sf, -1)); ratio = float(sf[i] / base)
        # a second, stricter test: is the peak the clear winner inside the whole 6 s?
        gl = float(sf[i] / (np.max(sf) + 1e-12))
        out.append(dict(k=k, stroke=v["stroke"], offset=float(t[i] - pk), ratio=ratio, glob=gl))
    R = np.array([o["ratio"] for o in out]); off = np.array([o["offset"] for o in out]); G = np.array([o["glob"] for o in out])
    lines = [f"{len(out)} windows with audio (forehand/backhand/serve, labeller confidence >= 2)",
             f"peak-to-median flux ratio inside +-0.6 s of the skeleton event: median {np.median(R):.0f}, share >= 20x: {np.mean(R >= 20):.2f}, share >= 50x: {np.mean(R >= 50):.2f}",
             f"peak is the strongest of the 6 s: {np.mean(G >= 0.999):.2f}; at least half the 6 s maximum: {np.mean(G >= 0.5):.2f}"]
    for th in (20, 50):
        s = off[R >= th]
        if len(s): lines.append(f"clear peaks (>= {th}x): offset from skeleton event median {np.median(s):+.2f} s, within 0.1 s: {np.mean(np.abs(s) <= 0.1):.2f}, within 0.2 s: {np.mean(np.abs(s) <= 0.2):.2f} (n={len(s)})")
    for c in ("forehand", "backhand", "serve"):
        s = [o["ratio"] for o in out if o["stroke"] == c]
        if s: lines.append(f"{c}: n={len(s)}, share with clear peak (>= 20x) {np.mean(np.array(s) >= 20):.2f}")
    open("work/audio_check.txt", "w").write("\n".join(lines)); json.dump(out, open("work/audio_check.json", "w")); print("\n".join(lines))


if __name__ == "__main__":
    main()
