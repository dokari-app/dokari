import sys, pickle, glob, os, json, numpy as np; sys.path.insert(0, "tests"); sys.path.insert(0, ".")
import ball_night as bn; from sphere import ball
R = bn.ROOT = "work/ball_night"; clf = pickle.load(open(f"{R}/clf.pkl", "rb"))
tags = [os.path.basename(f)[:-4] for f in sorted(glob.glob(f"{R}/feat/*.npz"))]
D = {}
for t in tags:
    z = dict(np.load(f"{R}/feat/{t}.npz")); H, W = [int(v) for v in z["HW"]]; B = z["boxes"]; ph = float(z["ph"]); p = clf.predict_proba(bn.feats(z))[:, 1]
    cands = [[] for _ in z["times"]]
    for k in np.where(p > 0.03)[0]: cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
    cands = [bn.context_filter(cs, B[min(i, len(B) - 1)]) for i, cs in enumerate(cands)]
    j = json.load(open(f"{R}/judged/{t}.json")); fr = [j["crops"][int(i)] for i, k in j["yes"].items() if k == "free"]
    cls = "none" if not j["yes"] else ("moving" if len({c[0] for c in fr}) >= 3 and (np.ptp([c[2] for c in fr]) + np.ptp([c[3] for c in fr])) / (j["d"] / 0.035) > 0.4 else "other")
    D[t] = (cands, z["times"], ph, B, cls)
print({c: sum(v[4] == c for v in D.values()) for c in ("moving", "none", "other")}, flush=True)
def toss(tr, B, ph, score=20):
    if not tr: return False
    x0, y0 = tr["pts"][0]; b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; cx0 = (b0[0] + b0[2]) / 2
    start = abs(x0 - cx0) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0
    travel = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph; apex = (float(np.median(B[:, 1])) - tr["apex_y"]) / ph
    return bool(start and travel >= 0.2 and apex >= 0.15 and tr["t1"] - tr["t0"] >= 0.2 and tr["score"] >= score)
for name, kw in [("default", {}), ("tol x2", {"tolx": 2}), ("tol x3", {"tolx": 3}), ("tol x2 minf4", {"tolx": 2, "min_frames": 4}), ("a 0.2-3", {"a_range": (0.2, 3.0)})]:
    kw = dict(kw); tx = kw.pop("tolx", 1); res = {"moving": [0, 0], "none": [0, 0], "other": [0, 0]}
    for t, (c, T, ph, B, cls) in D.items():
        tr = ball.link_soft(c, list(T), ph, tol=max(3.0, 0.012 * ph) * tx, **({"min_frames": 5} | kw)); res[cls][1] += 1; res[cls][0] += toss(tr, B, ph)
    print(name, "| moving found %d/%d | ball-less false %d/%d | other(static etc) %d/%d" % (*res["moving"], *res["none"], *res["other"]), flush=True)
