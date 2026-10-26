"""Player crops for the image model: for every training window, 8 frames (0.2 s apart, -1.2 s .. +0.2 s around the skeleton event),
all cut from ONE square box around the player (found at the event), resized to 112x112.  Free, Mac, resumable.
  python tests/crops_extract.py            -> work/crops.npy (N,8,112,112,3 uint8), work/crops_keys.json, work/crops_ok.npy
  python tests/crops_extract.py --limit 3  (speed test)"""
import argparse, json, os, sys, time
import numpy as np, cv2
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
from sphere import labelling
S = 112; OFFS = np.round(np.arange(-1.2, 0.21, 0.2), 2); NF = len(OFFS)
A = "work/crops.npy"; KEYS = "work/crops_keys.json"; OK = "work/crops_ok.npy"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    import stroke_net as sn
    rows = sn.build(); keys = [r["k"] for r in rows]; N = len(rows)
    if not os.path.exists(KEYS) or json.load(open(KEYS)) != keys:
        json.dump(keys, open(KEYS, "w")); np.save(OK, np.zeros(N, np.uint8))
        np.lib.format.open_memmap(A, mode="w+", dtype=np.uint8, shape=(N, NF, S, S, 3)).flush()
    arr = np.load(A, mmap_mode="r+"); ok = np.load(OK);
    todo = [i for i in range(N) if not ok[i]][:a.limit or None]; print(f"{N} windows, {len(todo)} to do", flush=True); t0 = time.time()
    for n, i in enumerate(todo, 1):
        r = rows[i]; act, vid = r["k"].split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
        if vf:
            cap = cv2.VideoCapture(vf); fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); box = None
            ts, X = sn.P2[r["k"]]; m = np.isfinite(X[:, :, 0]).all(1)
            if m.sum() >= 3 and fh > 0:
                Xm = X[m]; torso_c = np.nanmedian((Xm[:, [1, 2, 7, 8], :2]).mean(1), 0)        # centre of shoulders+hips, in units of frame height
                ht = np.nanmedian(np.nanmean(Xm[:, [11, 12], 1], 1) - Xm[:, 0, 1])               # nose to ankles, frame heights
                ht = ht if np.isfinite(ht) and 0.05 < ht < 1.5 else 3.6 * np.nanmedian(np.linalg.norm(Xm[:, [1, 2], :2].mean(1) - Xm[:, [7, 8], :2].mean(1), axis=1))
                cx, cy, side = torso_c[0] * fh, torso_c[1] * fh, 1.8 * ht * fh
                if np.isfinite([cx, cy, side]).all() and side > 40: box = (cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2)
            if box is not None:
                x0, y0, x1, y1 = box; side = x1 - x0; X0, Y0 = int(round(x0)), int(round(y0)); X1, Y1 = X0 + int(side), Y0 + int(side)
                out = np.zeros((NF, S, S, 3), np.uint8); got = 0
                for j, o in enumerate(OFFS):
                    cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0.0, r["peak"] + o)); good, fr = cap.read()
                    if not good: continue
                    P = int(side) + 2; pad = cv2.copyMakeBorder(fr, P, P, P, P, cv2.BORDER_CONSTANT)
                    c = pad[Y0 + P:Y1 + P, X0 + P:X1 + P]
                    if c.size == 0: continue
                    out[j] = cv2.resize(c, (S, S), interpolation=cv2.INTER_AREA)[:, :, ::-1]; got += 1
                if got >= NF - 1: arr[i] = out; ok[i] = 1
            cap.release()
        if n % 50 == 0 or n == len(todo):
            arr.flush(); np.save(OK, ok); el = time.time() - t0; print(f"  {n}/{len(todo)}, {el/60:.1f} min, about {el/n*(len(todo)-n)/60:.0f} min left; usable so far {int(ok.sum())}", flush=True)
    arr.flush(); np.save(OK, ok); print("done, usable", int(ok.sum()), "of", N)


if __name__ == "__main__":
    main()
