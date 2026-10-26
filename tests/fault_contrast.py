"""Per-fault contrast on aligned forehand swings. For each fault: attempts where the coach says it is present vs
absent (plus the paired-demo rule). Pick the phase/joint cells that differ on training videos, score held-out videos."""
import sys, collections
import numpy as np
sys.argv = [sys.argv[0], "tennis_forehand", "forehand", "shoulders"]
sys.path.insert(0, "tests")
import fuse_experiment as fx

rows = fx.collect()
print("attempts", len(rows))
pos, neg = collections.defaultdict(list), collections.defaultdict(list)
for i, r in enumerate(rows):
    for f in fx.L["faults"]:
        if f in r["present"] or (r["seg"] == "wrong_demo" and f in r["faults"]):
            pos[f].append(i)
        elif f in r["absent"] or (r["seg"] == "right_demo" and (f in r["faults"] or not r["present"])):
            neg[f].append(i)
print("fault: positives (videos) / negatives (videos)")
cands = []
for f in fx.L["faults"]:
    pv = len({rows[i]["vid"] for i in pos[f]}); nv = len({rows[i]["vid"] for i in neg[f]})
    print(f"  {f:42s} {len(pos[f]):3d} ({pv:2d}) / {len(neg[f]):3d} ({nv:2d})")
    if len(pos[f]) >= 10 and pv >= 5 and len(neg[f]) >= 10:
        cands.append(f)
rng = np.random.RandomState(1)
X = np.stack([r["X"] for r in rows])          # N, phase, joint, 3
Xf = X.reshape(len(rows), -1)
K = 5
for f in cands:
    idx = pos[f] + neg[f]
    y = np.array([1] * len(pos[f]) + [0] * len(neg[f]))
    vids = sorted({rows[i]["vid"] for i in idx}); rng.shuffle(vids)
    fold = {v: k % K for k, v in enumerate(vids)}
    scores, labels = [], []
    for k in range(K):
        tr = [j for j, i in enumerate(idx) if fold[rows[i]["vid"]] != k]
        te = [j for j, i in enumerate(idx) if fold[rows[i]["vid"]] == k]
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
            continue
        A = Xf[[idx[j] for j in tr]]; ytr = y[tr]
        mp, mn = np.median(A[ytr == 1], 0), np.median(A[ytr == 0], 0)
        sd = 1.4826 * np.median(np.abs(A - np.median(A, 0)), 0) + 0.05
        d = (mp - mn) / sd
        top = np.argsort(-np.abs(d))[:12]
        w = np.sign(d[top]) / sd[top]
        for j in te:
            scores.append(float(((Xf[idx[j]][top] - (mp[top] + mn[top]) / 2) * w).sum())); labels.append(y[j])
    s = np.array(scores); l = np.array(labels)
    a = fx.auc(s[l == 1], s[l == 0])
    # null: same pipeline with labels shuffled across videos
    nulls = []
    for _ in range(20):
        ys = y.copy(); rng.shuffle(ys)
        sc2, lb2 = [], []
        for k in range(K):
            tr = [j for j, i in enumerate(idx) if fold[rows[i]["vid"]] != k]; te = [j for j, i in enumerate(idx) if fold[rows[i]["vid"]] == k]
            if len(set(ys[tr])) < 2 or len(set(ys[te])) < 2: continue
            A = Xf[[idx[j] for j in tr]]; ytr = ys[tr]
            mp, mn = np.median(A[ytr == 1], 0), np.median(A[ytr == 0], 0)
            sd = 1.4826 * np.median(np.abs(A - np.median(A, 0)), 0) + 0.05
            d = (mp - mn) / sd; top = np.argsort(-np.abs(d))[:12]; w = np.sign(d[top]) / sd[top]
            for j in te:
                sc2.append(float(((Xf[idx[j]][top] - (mp[top] + mn[top]) / 2) * w).sum())); lb2.append(ys[j])
        sc2, lb2 = np.array(sc2), np.array(lb2)
        if len(set(lb2)) == 2: nulls.append(fx.auc(sc2[lb2 == 1], sc2[lb2 == 0]))
    A = Xf[idx]; mp, mn = np.median(A[y == 1], 0), np.median(A[y == 0], 0)
    sd = 1.4826 * np.median(np.abs(A - np.median(A, 0)), 0) + 0.05
    d = ((mp - mn) / sd).reshape(fx.NPH, len(fx.KEEP), 3)
    cell = np.unravel_index(np.argsort(-np.abs(d).ravel())[:4], d.shape)
    where = [(round(p / fx.NPH, 2), fx.KEEP[j], "xyz"[c], round(float(d[p, j, c]), 2)) for p, j, c in zip(*cell)]
    print(f"{f}: held-out AUC {a:.3f} (shuffled-label null {np.mean(nulls):.3f} +/- {np.std(nulls):.3f}); n {len(pos[f])}/{len(neg[f])}; biggest cells (phase, joint, axis, effect): {where}")
