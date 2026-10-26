"""The learned classifier on real YouTube windows (work/ball_v7 caches): blobs -> scores -> arc. Writes a sheet of crops along each found arc to check by eye.
  python tests/ball_apply.py work/ball_data work/ball_comp work/ball_v7 work/ball_apply"""
import glob, os, pickle, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_dataset import examples
from ball_eval_comp import load, fit
from ball_train import feats


def main():
    real, comp, bg, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True)
    items = list(load(real).values()) + list(load(comp).values())
    clf = fit(items); print("trained on", len(items), "files", flush=True)
    for f in sorted(glob.glob(os.path.join(bg, "*.cache.pkl"))):
        tag = os.path.basename(f)[:-10]
        if "_serve" not in tag:
            continue
        w = pickle.load(open(f, "rb")); imgs, boxes, times = w["imgs"], w["boxes"], w["times"]
        z = examples(imgs, boxes, {}, 0)
        if len(z["y"]) == 0:
            print(tag, "no blobs"); continue
        p = clf.predict_proba(feats(z))[:, 1]
        H, W = imgs[0].shape[:2]; ph = z["ph"]
        cands = [[] for _ in imgs]
        for k in np.where(p > 0.5)[0]:
            cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
        tr = ball.link(cands, times, min_inliers=6, tol=max(3.0, 0.012 * ph))
        top = float(np.median([b[1] for b in boxes]))
        ok = False
        if tr:
            moved = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) >= 0.3 * ph
            ok = bool(moved and tr["apex_y"] < top - 0.15 * ph and tr["t1"] - tr["t0"] >= 0.15)
        print(f"{tag:28s} blobs/frame {len(p)/len(imgs):5.1f} p>0.5/frame {np.mean([len(c) for c in cands]):4.1f}  track {tr['n'] if tr else 0:3d}  {'TOSS' if ok else '-'}", flush=True)
        if ok:
            fr = tr["frames"]; sel = [fr[int(k)] for k in np.linspace(0, len(fr) - 1, min(10, len(fr)))]
            pts = dict(zip(tr["frames"], tr["pts"][:len(tr["frames"])]))
            tiles = []
            for i in sel:
                x, y = pts.get(i, (W / 2, H / 2)); r = int(max(30, 2.5 * 0.035 * ph))
                x0, y0 = int(min(max(x - r, 0), W - 2 * r)), int(min(max(y - r, 0), H - 2 * r))
                c = imgs[i][y0:y0 + 2 * r, x0:x0 + 2 * r].copy(); cv2.circle(c, (int(x - x0), int(y - y0)), int(0.035 * ph * 1.0), (0, 0, 255), 1)
                tiles.append(cv2.resize(c, (150, 150)))
            cv2.imwrite(os.path.join(out, tag + ".png"), np.vstack([np.hstack(tiles[:5]), np.hstack(tiles[5:10])]) if len(tiles) >= 10 else np.hstack(tiles))


if __name__ == "__main__":
    main()
