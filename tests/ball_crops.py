"""Candidate crops of real YouTube windows for a vision model (or a person) to judge: 'is a tennis ball at the centre?'
  python tests/ball_crops.py work/ball_data work/ball_comp work/ball_v7 work/ball_judge [--frames 10] [--top 4]
Per window: --frames frames spread over the window; per frame the --top candidates by classifier score. Writes numbered grids (grid_NN.png) and manifest.json."""
import glob, json, os, pickle, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_dataset import examples
from ball_eval_comp import load, fit
from ball_train import feats

COLS, ROWS, T = 6, 4, 190


def main():
    real, comp, bg, out = sys.argv[1:5]
    nf = int(sys.argv[sys.argv.index("--frames") + 1]) if "--frames" in sys.argv else 10
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 4
    os.makedirs(out, exist_ok=True)
    clf = fit(list(load(real).values()) + list(load(comp).values()))
    man, tiles = [], []
    for f in sorted(glob.glob(os.path.join(bg, "*.cache.pkl"))):
        tag = os.path.basename(f)[:-10]
        if "_serve" not in tag:
            continue
        w = pickle.load(open(f, "rb")); imgs, boxes = w["imgs"], w["boxes"]; H, W = imgs[0].shape[:2]
        z = examples(imgs, boxes, {}, 0)
        if len(z["y"]) == 0:
            continue
        p = clf.predict_proba(feats(z))[:, 1]; d = 0.035 * z["ph"]
        for fr in np.linspace(2, len(imgs) - 3, nf).astype(int):
            m = np.where(z["frame"] == fr)[0]
            for k in m[np.argsort(-p[m])][:top]:
                x, y = z["xy"][k][0] * W, z["xy"][k][1] * H
                r = int(max(24, 3.2 * d)); x0, y0 = int(round(x - r)), int(round(y - r))
                pad = np.zeros((2 * r, 2 * r, 3), np.uint8)
                xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + 2 * r, W), min(y0 + 2 * r, H)
                pad[ya - y0:yb - y0, xa - x0:xb - x0] = imgs[fr][ya:yb, xa:xb]
                t = cv2.resize(pad, (T, T), interpolation=cv2.INTER_CUBIC)
                cv2.circle(t, (T // 2, T // 2), int(T * d / (2 * r)) + 5, (0, 0, 255), 1)
                n = len(man); cv2.putText(t, str(n), (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                tiles.append(t); man.append({"i": n, "window": tag, "frame": int(fr), "x": float(x), "y": float(y), "p": float(p[k]), "d": float(d)})
    per = COLS * ROWS
    for g in range(0, len(tiles), per):
        grid = np.zeros((ROWS * T, COLS * T, 3), np.uint8)
        for j, t in enumerate(tiles[g:g + per]):
            grid[(j // COLS) * T:(j // COLS + 1) * T, (j % COLS) * T:(j % COLS + 1) * T] = t
        cv2.imwrite(os.path.join(out, f"grid_{g // per:02d}.png"), grid)
    json.dump(man, open(os.path.join(out, "manifest.json"), "w"))
    print(len(man), "crops in", (len(tiles) + per - 1) // per, "grids")


if __name__ == "__main__":
    main()
