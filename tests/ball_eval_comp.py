"""Does a learned ball-vs-clutter classifier beat 'most yellow-green blob' where clutter is real? Composite windows (real YouTube clutter, pasted ball, exact truth).
A: trained on your real (degraded) windows only -> tested on composites.   B: trained on composites -> tested on composite windows from OTHER videos.
C: trained on composites + your real windows -> tested on composites from other videos.   python tests/ball_eval_comp.py work/ball_data work/ball_comp"""
import glob, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_train import feats
from sklearn.ensemble import HistGradientBoostingClassifier


def load(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, "*.npz"))):
        z = dict(np.load(f)); out[os.path.basename(f)[:-4]] = (z, feats(z))
    return out


def fit(items):
    X = np.concatenate([F for _, F in items]); y = np.concatenate([z["y"] for z, _ in items])
    rng = np.random.default_rng(0)
    pos = np.where(y == 1)[0]; neg = np.where(y == 0)[0]; neg = rng.choice(neg, min(len(neg), 30000), replace=False); idx = np.concatenate([pos, neg])
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=15, l2_regularization=1.0, class_weight={0: 1.0, 1: 5.0}, random_state=0).fit(X[idx], y[idx])


def ranks(clf, z, F):
    p = clf.predict_proba(F)[:, 1] if clf else None
    colour = z["S"][:, 4] * ((z["S"][:, 3] >= 20) & (z["S"][:, 3] <= 50))
    out = []
    for fr in sorted(set(z["frame"][z["y"] == 1].tolist())):
        m = z["frame"] == fr; yy = z["y"][m]
        rk = lambda s: 1 + int((s[m][yy == 0] > s[m][yy == 1].max()).sum())
        out.append((rk(p) if clf else 0, rk(colour), int(m.sum())))
    return out


def report(name, rs):
    a = np.array(rs)
    print(f"{name:44s} frames {len(a):5d}   model top1 {np.mean(a[:,0]==1):.2f} top3 {np.mean(a[:,0]<=3):.2f}   |  colour top1 {np.mean(a[:,1]==1):.2f} top3 {np.mean(a[:,1]<=3):.2f}   | random top1 {np.mean(1.0/a[:,2]):.2f}")


def main():
    real, comp = load(sys.argv[1]), load(sys.argv[2])
    print(len(real), "real files,", len(comp), "composite files")
    vid = lambda t: t.split("_")[0]
    clf = fit(list(real.values()))
    report("A: train real -> test composites", sum((ranks(clf, z, F) for z, F in comp.values()), []))
    cd = fit(list(comp.values()))
    report("D: train composites -> your REAL windows", sum((ranks(cd, z, F) for z, F in real.values()), []))
    if "--quick" in sys.argv:
        return
    vids = sorted({vid(t) for t in comp}); B, C = [], []
    for v in vids:
        tr = [x for t, x in comp.items() if vid(t) != v]; te = [x for t, x in comp.items() if vid(t) == v]
        cb = fit(tr); cc = fit(tr + list(real.values()))
        for z, F in te:
            B += ranks(cb, z, F); C += ranks(cc, z, F)
        print("held out video", v, flush=True)
    report("B: train composites -> other videos", B)
    report("C: train composites+real -> other videos", C)


if __name__ == "__main__":
    main()
