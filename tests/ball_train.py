"""Train a ball-vs-clutter classifier on work/ball_data and test it on windows it never saw (leave one serve out).
Reports, per video quality, how often the true ball is the classifier's first (or top-3) choice among all moving blobs of its frame, next to two baselines
(random; 'most yellow-green'). python tests/ball_train.py work/ball_data"""
import glob, os, sys
import numpy as np
import cv2
from sklearn.ensemble import HistGradientBoostingClassifier

P = 24


def feats(d):
    X = d["X"].astype(np.float32); n = len(X)
    g = X[:, :3 * P * P].reshape(n, 3, P, P); hs = X[:, 3 * P * P:].reshape(n, 2, P, P)
    small = lambda a: np.stack([cv2.resize(a[i], (12, 12), interpolation=cv2.INTER_AREA) for i in range(n)]).reshape(n, -1)
    parts = [small(g[:, k]) for k in range(3)] + [small(hs[:, 0]), small(hs[:, 1])]
    cur = g[:, 1]; ctr = cur[:, 8:16, 8:16].mean((1, 2)); ring = np.concatenate([cur[:, :4].reshape(n, -1), cur[:, -4:].reshape(n, -1)], 1).mean(1)
    mv = np.abs(g[:, 1] - g[:, 0]).mean((1, 2)) + np.abs(g[:, 1] - g[:, 2]).mean((1, 2))
    return np.concatenate(parts + [d["S"], ctr[:, None], (ctr - ring)[:, None], mv[:, None]], 1).astype(np.float32)


def main():
    files = sorted(glob.glob(os.path.join(sys.argv[1], "*.npz")))
    D = {}
    for f in files:
        d = dict(np.load(f)); tag = os.path.basename(f)[:-4]; win = tag.rsplit("_", 2)[0]
        D[tag] = (win, int(tag.rsplit("_", 2)[1]), d, feats(d))
    wins = sorted({v[0] for v in D.values()})
    print(len(D), "files,", len(wins), "windows:", wins)
    res = {}      # quality -> list of (rank of ball by model, rank by colour, n candidates)
    rng = np.random.default_rng(0)
    for held in wins:
        tr = [v for v in D.values() if v[0] != held]
        Xtr = np.concatenate([v[3] for v in tr]); ytr = np.concatenate([v[2]["y"] for v in tr])
        pos = np.where(ytr == 1)[0]; neg = np.where(ytr == 0)[0]
        neg = rng.choice(neg, min(len(neg), 20000), replace=False)
        idx = np.concatenate([pos, neg])
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=15, l2_regularization=1.0, class_weight={0: 1.0, 1: 5.0}, random_state=0)
        clf.fit(Xtr[idx], ytr[idx])
        for tag, (w, L, d, F) in D.items():
            if w != held:
                continue
            p = clf.predict_proba(F)[:, 1]
            hue, sat = d["S"][:, 3], d["S"][:, 4]
            colour = sat * ((hue >= 20) & (hue <= 50))
            for fr in sorted(set(d["frame"][d["y"] == 1].tolist())):
                m = d["frame"] == fr; yy = d["y"][m]
                rank = lambda s: 1 + int((s[m][yy == 0] > s[m][yy == 1].max()).sum())
                res.setdefault(L, []).append((rank(p), rank(colour), int(m.sum())))
        print("held out", held, "done", flush=True)
    print("\nquality(px)   frames   model top1  top3     most-yellow-green top1  top3     random top1")
    for L in sorted(res, reverse=True):
        a = np.array(res[L]); n = len(a)
        print(f"{L:6d}      {n:6d}      {np.mean(a[:,0]==1):.2f}      {np.mean(a[:,0]<=3):.2f}           {np.mean(a[:,1]==1):.2f}       {np.mean(a[:,1]<=3):.2f}          {np.mean(1.0/a[:,2]):.2f}")


if __name__ == "__main__":
    main()
