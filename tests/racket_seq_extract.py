"""Racket position over time, for the racket-as-input test. For each selected window: every 0.1 s from -2.7 s to +0.8 s around the skeleton event,
find the player (full frame), then the racket INSIDE the player crop (upscaled). Stores racket centre/size relative to the player box.
Selection: every human-tagged window + random others up to --n windows (resumable, free, Mac).
  python tests/racket_seq_extract.py --n 900            -> work/racket_seq.pkl
  python tests/racket_seq_extract.py --n 900 --limit 3   (speed test)"""
import argparse, json, os, pickle, random, sys, time
import numpy as np, cv2
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
from sphere import labelling, ball
OUT = "work/racket_seq2.pkl"; GRID = np.round(np.arange(-2.7, 0.81, 0.1), 2)


def selection(n):
    import stroke_net as sn
    key = json.load(open("work/humantest/key_DO_NOT_OPEN.json")); tags = json.load(open("work/humantest/tags.json"))
    hk = {key[i]["key"] for i, h in tags.items() if h in ("forehand", "backhand", "serve", "none")}
    rows = sn.build(); hum = [r for r in rows if r["k"] in hk]; rest = [r for r in rows if r["k"] not in hk]
    random.Random(3).shuffle(rest)
    return hum + rest[:max(0, n - len(hum))]


def feats(det, fr, pb):
    """pb = player box from the skeleton's 2D joints (reliable), not from the detector."""
    H, W = fr.shape[:2]
    x0, y0, x1, y1 = [int(c) for c in pb]; pw, ph = x1 - x0, y1 - y0
    if ph < 20: return None
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    cx0, cy0, cx1, cy1 = max(0, x0 - pw // 3), max(0, y0 - ph // 10), min(W, x1 + pw // 3), min(H, y1 + ph // 10)
    crop = fr[cy0:cy1, cx0:cx1]; sc = max(1.0, 640.0 / max(crop.shape[:2])); big = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
    rk = det.run(big, conf=0.08, classes=(ball.RACKET,))
    if not rk: return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    d = max(rk, key=lambda d: d[1]); bx0, by0, bx1, by1 = d[2] / sc + cx0, d[3] / sc + cy0, d[4] / sc + cx0, d[5] / sc + cy0
    pcx, pcy = (x0 + x1) / 2, (y0 + y1) / 2
    return [1.0, float(d[1]), ((bx0 + bx1) / 2 - pcx) / ph, ((by0 + by1) / 2 - pcy) / ph, (bx1 - bx0) / ph, (by1 - by0) / ph, 1.0]   # present, conf, dx, dy, w, h, player_found


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=900); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    sel = selection(a.n); res = pickle.load(open(OUT, "rb")) if os.path.exists(OUT) else {}
    todo = [r for r in sel if r["k"] not in res][:a.limit or None]
    print(f"selected {len(sel)}, to do {len(todo)} windows x {len(GRID)} frames", flush=True)
    det = ball.Detector("models/tennis_v8_player_racket_ball.onnx", threads=4); t0 = time.time(); nd = 0
    for n, r in enumerate(todo, 1):
        act, vid = r["k"].split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
        if not vf: continue
        import stroke_net as sn
        ts, X = sn.P2[r["k"]]; m = np.isfinite(X[:, :, 0]).all(1)
        if m.sum() < 3: continue
        cap = cv2.VideoCapture(vf); fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); Xm = X[m]
        c = np.nanmedian(Xm[:, [1, 2, 7, 8], :2].mean(1), 0); ht = np.nanmedian(np.nanmean(Xm[:, [11, 12], 1], 1) - Xm[:, 0, 1])
        if not (np.isfinite(ht) and 0.05 < ht < 1.5): ht = 3.6 * np.nanmedian(np.linalg.norm(Xm[:, [1, 2], :2].mean(1) - Xm[:, [7, 8], :2].mean(1), axis=1))
        pb = (c[0] * fh - 0.45 * ht * fh, (c[1] - 0.62 * ht) * fh, c[0] * fh + 0.45 * ht * fh, (c[1] + 0.62 * ht) * fh)   # tall box around the player
        F = np.zeros((len(GRID), 7), np.float32); ok_any = False
        for i, g in enumerate(GRID):
            cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0.0, r["peak"] + g)); ok, fr = cap.read()
            if not ok: continue
            f = feats(det, fr, pb)
            if f is not None: F[i] = f; ok_any = True
        cap.release()
        if ok_any: res[r["k"]] = F; nd += 1
        if n % 10 == 0 or n == len(todo):
            pickle.dump(res, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT)
            el = time.time() - t0; print(f"  {n}/{len(todo)} windows, {el/60:.1f} min, about {el/n*(len(todo)-n)/60:.0f} min left; racket found in {np.mean([x[:, 0].mean() for x in res.values()]):.2f} of frames", flush=True)
    pickle.dump(res, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT); print("done", len(res))


if __name__ == "__main__":
    main()
