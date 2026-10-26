"""Turn the judged YouTube crops (work/ball_judge) into labelled blobs. work/ball_yt/<window>.npz (same fields as ball_dataset.examples + y).
Frames holding a verified ball: blobs near it = 1, all other blobs = 0. Frames without one: only blobs at judged-no crops = 0 (the ball may be there unseen)."""
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_dataset import examples

def main(bg="work/ball_v7", jd="work/ball_judge", out="work/ball_yt"):
    os.makedirs(out, exist_ok=True)
    m = json.load(open(f"{jd}/manifest.json")); J = json.load(open(f"{jd}/judged.json"))["yes"]
    yes = set(J["free"] + J["held"] + J["static"])
    wins = sorted({c["window"] for c in m})
    for w in wins:
        w_ = pickle.load(open(f"{bg}/{w}.cache.pkl", "rb")); imgs, boxes = w_["imgs"], w_["boxes"]
        H, W = imgs[0].shape[:2]
        z = examples(imgs, boxes, {}, 0)
        cs = [c for c in m if c["window"] == w]
        xy = np.array([[z["xy"][k][0] * W, z["xy"][k][1] * H] for k in range(len(z["y"]))]).reshape(-1, 2)
        fr = z["frame"]; y = np.full(len(fr), -1, np.int8)   # -1 unlabelled
        r = max(6.0, 0.02 * float(z["ph"].mean() if hasattr(z["ph"], "mean") else z["ph"]))
        for f in sorted({c["frame"] for c in cs}):
            fc = [c for c in cs if c["frame"] == f]; ys = [c for c in fc if c["i"] in yes]; mk = fr == f
            if ys:
                y[mk] = 0
                for c in ys:
                    d = np.hypot(xy[:, 0] - c["x"], xy[:, 1] - c["y"]); y[mk & (d < r)] = 1
            else:
                for c in fc:
                    d = np.hypot(xy[:, 0] - c["x"], xy[:, 1] - c["y"]); y[mk & (d < r) & (y != 1)] = 0
        z2 = dict(z); z2["y"] = y
        np.savez_compressed(f"{out}/{w}.npz", **{k: np.asarray(v) for k, v in z2.items()})
        print(w, "blobs", len(y), "pos", int((y == 1).sum()), "neg", int((y == 0).sum()), "unl", int((y == -1).sum()), flush=True)
main(*sys.argv[1:])
