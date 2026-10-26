"""Held-out-video test of the full chain (classifier + arc) on all work/ball_v7 windows (serve and control). A toss is accepted by the same rule as ball_apply.
Truth: windows with a verified FREE ball in flight (work/ball_judge/judged.json) should give a toss; controls should not.  python tests/ball_yt_arc.py [thr]"""
import glob, json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_dataset import examples
from ball_eval_comp import load
from ball_train import feats
from ball_yt_eval import fitw, sub

def main():
    thr = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    real = load("work/ball_data"); comp = load("work/ball_comp")
    yt = {os.path.basename(f)[:-4]: dict(np.load(f)) for f in sorted(glob.glob("work/ball_yt/*.npz"))}
    ytF = {k: feats(z) for k, z in yt.items()}
    vid = lambda s: s.split("_serve")[0].split("_control")[0]
    m = json.load(open("work/ball_judge/manifest.json")); J = json.load(open("work/ball_judge/judged.json"))["yes"]
    freeset = set(J["free"]); flight = {c["window"] for c in m if c["i"] in freeset}
    rng = np.random.default_rng(0); models = {}
    def model(held):
        if held in models: return models[held]
        X0 = np.concatenate([F for k, (z, F) in comp.items() if not k.startswith(held)] + [F for z, F in real.values()])
        y0 = np.concatenate([z["y"] for k, (z, F) in comp.items() if not k.startswith(held)] + [z["y"] for z, F in real.values()])
        Xa, ya, wa = sub(X0, y0, np.ones(len(y0)), rng)
        trk = [k for k in yt if vid(k) != held]
        Xy = np.concatenate([ytF[k][yt[k]["y"] >= 0] for k in trk]); yy = np.concatenate([yt[k]["y"][yt[k]["y"] >= 0] for k in trk])
        models[held] = fitw(np.concatenate([Xa, Xy]), np.concatenate([ya, yy]), np.concatenate([wa, np.where(yy == 1, 3.0, 1.0)])); return models[held]
    cf = f"work/ball_yt_arc_{thr}.json"; res = {k: tuple(v) for k, v in json.load(open(cf)).items()} if os.path.exists(cf) else {}
    import time; t0 = time.time()
    for f in sorted(glob.glob("work/ball_v7/*.cache.pkl")):
        tag = os.path.basename(f)[:-10]
        if tag in res: continue
        if time.time() - t0 > 75: print("budget reached, rerun to continue"); break
        w = pickle.load(open(f, "rb")); imgs, boxes, times = w["imgs"], w["boxes"], w["times"]
        z = examples(imgs, boxes, {}, 0)
        if len(z["y"]) == 0: res[tag] = (0, False, 0.0, -9.0, 0.0); json.dump(res, open(cf, "w")); continue
        p = model(vid(tag)).predict_proba(feats(z))[:, 1]
        H, W = imgs[0].shape[:2]; ph = z["ph"]
        cands = [[] for _ in imgs]
        for k in np.where(p > thr)[0]:
            cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
        tr = ball.link(cands, times, min_inliers=6, tol=max(3.0, 0.012 * ph)); top = float(np.median([b[1] for b in boxes])); ok = False
        if tr:
            moved = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) >= 0.3 * ph
            ok = bool(moved and tr["apex_y"] < top - 0.15 * ph and tr["t1"] - tr["t0"] >= 0.15)
        st = (float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph, (top - tr["apex_y"]) / ph, tr["t1"] - tr["t0"]) if tr else (0.0, -9.0, 0.0)
        res[tag] = (tr["n"] if tr else 0, ok) + tuple(float(v) for v in st)
        if False: print("   ", tag, "n", tr["n"], "moved/ph %.2f" % (float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph), "apex above head/ph %.2f" % ((top - tr["apex_y"]) / ph), "dur %.2f" % (tr["t1"] - tr["t0"]))
        json.dump(res, open(cf, "w"))
        print(f"{tag:28s} track {res[tag][0]:3d} {'TOSS' if ok else '-':4s} {'<- flight ball verified' if tag in flight else ''}", flush=True)
    sv = {k: v for k, v in res.items() if "_serve" in k}; ct = {k: v for k, v in res.items() if "_control" in k}
    print(f"thr {thr}: serve windows with toss {sum(v[1] for v in sv.values())}/{len(sv)} (flight ball verified in {len(flight)}; toss in those {sum(sv[k][1] for k in flight if k in sv)}); control false tosses {sum(v[1] for v in ct.values())}/{len(ct)}")
if __name__ == "__main__": main()
