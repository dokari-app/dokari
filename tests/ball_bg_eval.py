import glob, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_eval_comp import load
from ball_train import feats
from ball_yt_eval import fitw, sub
def load(d, keep=0.12):
    out = {}; r = np.random.default_rng(0)
    for f in sorted(glob.glob(os.path.join(d, "*.npz"))):
        z = dict(np.load(f)); F = feats(z); m = (z["y"] == 1) | (r.random(len(F)) < keep); out[os.path.basename(f)[:-4]] = ({"y": z["y"][m]}, F[m]); del z, F
    return out
real = load("work/ball_data"); comp = load("work/ball_comp")
yt = {os.path.basename(f)[:-4]: dict(np.load(f)) for f in sorted(glob.glob("work/ball_yt/*.npz"))}; ytF = {k: feats(z) for k, z in yt.items()}
_m = np.load("work/ball_bgneg_feats.npy", mmap_mode="r"); bgF = np.asarray(_m[np.sort(np.random.default_rng(1).choice(len(_m), 40000, replace=False))]); del _m; print("bg blobs", len(bgF), flush=True)
import json, time; t0 = time.time(); CF = "work/ball_bg_eval.json"; DONE = json.load(open(CF)) if os.path.exists(CF) else {}
vid = lambda s: s.split("_serve")[0]; rng = np.random.default_rng(0); R = {"yt": [], "yt+bg": []}
for held in sorted({vid(k) for k in yt}):
    if held in DONE: continue
    if time.time() - t0 > 55: print("budget used; rerun"); break
    R = {"yt": [], "yt+bg": []}
    test = [k for k in yt if vid(k) == held]
    if not any((yt[k]["y"] == 1).any() for k in test): continue
    X0 = np.concatenate([F for k, (z, F) in comp.items() if not k.startswith(held)] + [F for z, F in real.values()]); y0 = np.concatenate([z["y"] for k, (z, F) in comp.items() if not k.startswith(held)] + [z["y"] for z, F in real.values()])
    Xa, ya, wa = sub(X0, y0, np.ones(len(y0)), rng); trk = [k for k in yt if vid(k) != held]
    Xy = np.concatenate([ytF[k][yt[k]["y"] >= 0] for k in trk]); yy = np.concatenate([yt[k]["y"][yt[k]["y"] >= 0] for k in trk])
    X1 = np.concatenate([Xa, Xy]); y1 = np.concatenate([ya, yy]); w1 = np.concatenate([wa, np.where(yy == 1, 3.0, 1.0)])
    sel = rng.choice(len(bgF), min(len(bgF), 30000), replace=False)
    m1 = fitw(X1, y1, w1); m2 = fitw(np.concatenate([X1, bgF[sel]]), np.concatenate([y1, np.zeros(len(sel), int)]), np.concatenate([w1, np.ones(len(sel))]))
    for k in test:
        z, F = yt[k], ytF[k]; p1, p2 = m1.predict_proba(F)[:, 1], m2.predict_proba(F)[:, 1]
        for fr in sorted(set(z["frame"][z["y"] == 1].tolist())):
            mk = (z["frame"] == fr) & (z["y"] >= 0); yv = z["y"][mk]; rk = lambda s: 1 + int((s[mk][yv == 0] > s[mk][yv == 1].max()).sum())
            R["yt"].append(rk(p1)); R["yt+bg"].append(rk(p2))
    DONE[held] = R; json.dump(DONE, open(CF, "w")); print("held", held, flush=True)
A = {"yt": [], "yt+bg": []}
for r in DONE.values():
    for k in A: A[k] += r[k]
print("held-out videos done:", len(DONE))
for k, v in A.items(): v = np.array(v); print(f"{k:6s} frames {len(v)} top1 {np.mean(v==1):.2f} top3 {np.mean(v<=3):.2f}")
