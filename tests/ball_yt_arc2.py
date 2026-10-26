"""Soft arc (ball.link_soft) on held-out-video classifier scores. Step 1 (resumable) caches per-window weak candidates in work/ball_yt_cands.pkl; step 2 sweeps.
  python tests/ball_yt_arc2.py"""
import glob, json, os, pickle, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_dataset import examples
from ball_train import feats
from ball_yt_eval import fitw, sub
CF = "work/ball_yt_cands_bg.pkl"

def build():
    t0 = time.time(); out = pickle.load(open(CF, "rb")) if os.path.exists(CF) else {}
    def load(d, keep=0.12):
        o = {}; r = np.random.default_rng(0)
        for f in sorted(glob.glob(os.path.join(d, "*.npz"))):
            z = dict(np.load(f)); F = feats(z); m = (z["y"] == 1) | (r.random(len(F)) < keep); o[os.path.basename(f)[:-4]] = ({"y": z["y"][m]}, F[m]); del z, F
        return o
    real = load("work/ball_data"); comp = load("work/ball_comp")
    _m = np.load("work/ball_bgneg_feats.npy", mmap_mode="r"); bgF = np.asarray(_m[np.sort(np.random.default_rng(1).choice(len(_m), 40000, replace=False))]); del _m
    yt = {os.path.basename(f)[:-4]: dict(np.load(f)) for f in sorted(glob.glob("work/ball_yt/*.npz"))}; ytF = {k: feats(z) for k, z in yt.items()}
    vid = lambda s: s.split("_serve")[0].split("_control")[0]; rng = np.random.default_rng(0); models = {}
    def model(held):
        if held in models: return models[held]
        X0 = np.concatenate([F for k, (z, F) in comp.items() if not k.startswith(held)] + [F for z, F in real.values()])
        y0 = np.concatenate([z["y"] for k, (z, F) in comp.items() if not k.startswith(held)] + [z["y"] for z, F in real.values()])
        Xa, ya, wa = sub(X0, y0, np.ones(len(y0)), rng); trk = [k for k in yt if vid(k) != held]
        Xy = np.concatenate([ytF[k][yt[k]["y"] >= 0] for k in trk]); yy = np.concatenate([yt[k]["y"][yt[k]["y"] >= 0] for k in trk])
        models[held] = fitw(np.concatenate([Xa, Xy, bgF]), np.concatenate([ya, yy, np.zeros(len(bgF), int)]), np.concatenate([wa, np.where(yy == 1, 3.0, 1.0), np.ones(len(bgF))])); return models[held]
    for f in sorted(glob.glob("work/ball_v7/*.cache.pkl")):
        tag = os.path.basename(f)[:-10]
        if tag in out: continue
        if time.time() - t0 > 70: print("budget used; rerun"); return False
        w = pickle.load(open(f, "rb")); imgs, boxes, times = w["imgs"], w["boxes"], w["times"]; z = examples(imgs, boxes, {}, 0)
        H, W = imgs[0].shape[:2]; cands = [[] for _ in imgs]
        if len(z["y"]):
            p = model(vid(tag)).predict_proba(feats(z))[:, 1]
            for k in np.where(p > 0.03)[0]: cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
        out[tag] = {"boxes": np.array(boxes).tolist(), "cands": cands, "times": times, "ph": float(z["ph"]) if len(z["y"]) else 1.0, "top": float(np.median([b[1] for b in boxes]))}
        pickle.dump(out, open(CF, "wb")); print(tag, flush=True)
    return True

if __name__ == "__main__":
    if build(): print("cands complete")
