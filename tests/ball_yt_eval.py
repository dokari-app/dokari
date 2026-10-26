"""Leave-one-video-out on the judged YouTube set: base model (real phone + composites) vs base + other YouTube videos' judged blobs.
Metric: in frames that hold a verified ball, rank of the ball among that frame's blobs (top1/top3), plus the colour baseline."""
import glob, os, sys
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_eval_comp import load
from ball_train import feats

def fitw(X, y, w, seed=0):
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=15, l2_regularization=1.0, class_weight={0: 1.0, 1: 5.0}, random_state=seed).fit(X, y, sample_weight=w)

def sub(X, y, w, rng, nneg=30000):
    pos = np.where(y == 1)[0]; neg = np.where(y == 0)[0]; neg = rng.choice(neg, min(len(neg), nneg), replace=False); i = np.concatenate([pos, neg])
    return X[i], y[i], w[i]

def main(argv):
    real = load("work/ball_data"); comp = load("work/ball_comp")
    yt = {os.path.basename(f)[:-4]: dict(np.load(f)) for f in sorted(glob.glob("work/ball_yt/*.npz"))}
    ytF = {k: feats(z) for k, z in yt.items()}
    vid = lambda s: s.split("_serve")[0].split("_control")[0]
    wins = sorted({vid(k) for k in yt})
    rng = np.random.default_rng(0)
    R = {"base": [], "base+yt": [], "colour": []}
    for held in wins:
        test = [k for k in yt if vid(k) == held]
        if not any((yt[k]["y"] == 1).any() for k in test):
            continue
        X0 = [F for k, (z, F) in comp.items() if not k.startswith(held)] + [F for z, F in real.values()]
        y0 = [z["y"] for k, (z, F) in comp.items() if not k.startswith(held)] + [z["y"] for z, F in real.values()]
        X0 = np.concatenate(X0); y0 = np.concatenate(y0); w0 = np.ones(len(y0))
        Xa, ya, wa = sub(X0, y0, w0, rng)
        base = fitw(Xa, ya, wa)
        trk = [k for k in yt if vid(k) != held]
        Xy = np.concatenate([ytF[k][yt[k]["y"] >= 0] for k in trk]); yy = np.concatenate([yt[k]["y"][yt[k]["y"] >= 0] for k in trk])
        wy = np.where(yy == 1, 3.0, 1.0)
        X1 = np.concatenate([Xa, Xy]); y1 = np.concatenate([ya, yy]); w1 = np.concatenate([wa, wy])
        both = fitw(X1, y1, w1)
        for k in test:
            z, F = yt[k], ytF[k]
            pb, pc = base.predict_proba(F)[:, 1], both.predict_proba(F)[:, 1]
            col = z["S"][:, 4] * ((z["S"][:, 3] >= 20) & (z["S"][:, 3] <= 50))
            for fr in sorted(set(z["frame"][z["y"] == 1].tolist())):
                m = (z["frame"] == fr) & (z["y"] >= 0); yv = z["y"][m]
                rk = lambda s: 1 + int((s[m][yv == 0] > s[m][yv == 1].max()).sum())
                R["base"].append(rk(pb)); R["base+yt"].append(rk(pc)); R["colour"].append(rk(col))
        print("held", held, flush=True)
    for k, v in R.items():
        v = np.array(v); print(f"{k:9s} frames {len(v)}  top1 {np.mean(v==1):.2f}  top3 {np.mean(v<=3):.2f}")
if __name__ == "__main__": main(sys.argv[1:])
