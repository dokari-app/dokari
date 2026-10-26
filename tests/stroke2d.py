"""Stroke classifier on image-plane pose (work/pose2d.pkl), labels work/stroke_labels3.json; compared with the depth-pose features on the same windows.
Role-based features (swing wrist / other wrist), no handedness needed. Grouped CV by video."""
import json, pickle, sys, io, contextlib, collections
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
LAB = json.load(open("work/stroke_labels3.json")); P2 = pickle.load(open("work/pose2d.pkl", "rb"))
PRE, POST, FPS, NS = 0.9, 0.4, 12, 16
# joint index in pose2d: 0 nose,1 lsh,2 rsh,3 lel,4 rel,5 lwr,6 rwr,7 lhip,8 rhip,9 lkn,10 rkn,11 lan,12 ran


def interp(ts, A, t):
    out = np.full((len(t), A.shape[1], 3), np.nan)
    for j in range(A.shape[1]):
        for c in range(3):
            y = A[:, j, c]; m = np.isfinite(y)
            if m.sum() >= 3: out[:, j, c] = np.interp(t, ts[m], y[m], left=np.nan, right=np.nan)
    return out


def feats(key, v):
    ts, A = P2[key]; pk = v["peak"]; t = np.linspace(pk - PRE, pk + POST, NS)
    X = interp(ts, A, t)
    if np.isnan(X[:, [1, 2, 5, 6, 7, 8], :2]).mean() > 0.25: return None
    ms = (X[:, 1] + X[:, 2]) / 2; mh = (X[:, 7] + X[:, 8]) / 2
    torso = np.nanmedian(np.linalg.norm(ms[:, :2] - mh[:, :2], axis=1))
    if not np.isfinite(torso) or torso < 0.05: return None
    sp = {}
    W = {"l": X[:, 5, :2], "r": X[:, 6, :2]}; SH = {"l": X[:, 1, :2], "r": X[:, 2, :2]}
    for s in "lr":
        d = np.diff(W[s], axis=0, prepend=W[s][:1]); sp[s] = np.nan_to_num(np.linalg.norm(d, axis=1)) 
    sw = "l" if np.nansum(sp["l"]) > np.nansum(sp["r"]) else "r"; ot = "r" if sw == "l" else "l"
    f = {}
    for role, s in (("sw", sw), ("ot", ot)):
        o = "r" if s == "l" else "l"
        sgn = np.sign(SH[o][:, 0] - SH[s][:, 0]); sgn[sgn == 0] = 1
        sgn = np.where(np.isfinite(sgn), sgn, np.nanmedian(sgn))
        cross = (W[s][:, 0] - ms[:, 0]) * sgn / torso; up = -(W[s][:, 1] - ms[:, 1]) / torso
        vx = np.gradient(np.nan_to_num(W[s][:, 0])) * sgn / torso * FPS / (NS / (PRE + POST)); 
        for i in range(NS):
            f[f"{role}_cross{i}"] = cross[i]; f[f"{role}_up{i}"] = up[i]; f[f"{role}_vx{i}"] = vx[i]
        f[f"{role}_cross_max"] = np.nanmax(cross); f[f"{role}_cross_min"] = np.nanmin(cross); f[f"{role}_up_max"] = np.nanmax(up)
        f[f"{role}_speed"] = float(np.nansum(sp[s]) / torso)
    sww = np.abs(SH["r"][:, 0] - SH["l"][:, 0]) / torso
    f["shoulder_w_med"] = float(np.nanmedian(sww)); f["shoulder_w_pk"] = float(np.nanmedian(sww[NS // 2 - 2:NS // 2 + 3]))
    f["hands_apart"] = float(np.nanmedian(np.linalg.norm(W["l"] - W["r"], axis=1)) / torso)
    f["nose_up"] = float(np.nanmedian(-(X[:, 0, 1] - ms[:, 1]) / torso))
    f["torso_px"] = float(torso)
    return f


def build(strict=True):
    rows = []
    for k, v in LAB.items():
        if k not in P2: continue
        s = "no_stroke" if v["stroke"] == "none" or v.get("shown") == "not_a_stroke" else v["stroke"]
        if s not in ("forehand", "backhand", "serve", "no_stroke"): continue
        if strict and s in ("forehand", "backhand") and (v.get("contact_in_frames") == "no" or v.get("hit_above_head") == "yes"): continue
        if strict and s == "serve" and v.get("ball_toss_seen") == "no" and v.get("hit_above_head") == "no": continue
        f = feats(k, v)
        if f is None: continue
        rows.append(dict(k=k, vid=k.split("/")[1], y=s, f=f, conf=v.get("confidence", 2)))
    return rows


def cv(rows, names, label):
    X = np.array([[r["f"][n] for n in names] for r in rows], float); y = np.array([r["y"] for r in rows]); g = np.array([r["vid"] for r in rows])
    cls = sorted(set(y)); pred = np.empty(len(y), object)
    for tr, te in GroupKFold(5).split(X, y, g):
        w = np.array([len(tr) / (len(cls) * (y[tr] == c).sum()) for c in y[tr]])
        m = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_leaf_nodes=15, l2_regularization=1.0, random_state=0).fit(X[tr], y[tr], sample_weight=w)
        pred[te] = m.predict(X[te])
    print(f"\n[{label}] n={len(y)} accuracy {np.mean(pred == y):.3f}  recall:", {c: round(float(np.mean(pred[y == c] == c)), 2) for c in cls})
    print("   rows=truth cols=pred", cls)
    for c in cls: print("   %-10s" % c, [int(((y == c) & (pred == d)).sum()) for d in cls])
    fb = np.isin(y, ["forehand", "backhand"]); ok = fb & np.isin(pred, ["forehand", "backhand"])
    print("   forehand-vs-backhand when both called a groundstroke: %.3f (n=%d)" % (np.mean(pred[ok] == y[ok]), ok.sum()))


rows = build()
print("windows", len(rows), collections.Counter(r["y"] for r in rows))
names2d = sorted(rows[0]["f"])
cv(rows, names2d, "image-plane pose, all features")
cv([r for r in rows if r["conf"] >= 2], names2d, "image-plane pose, confidence>=2 labels only")
with contextlib.redirect_stdout(io.StringIO()):
    import stroke_model as M
    R3 = M.load("work/stroke_labels3.json", shifts=(0.0,))
d3 = {f"{r['act']}/{r['vid']}/{r['kind']}/{r['pk']:.2f}": r["f"] for r in R3}
both = [dict(r, f={**r["f"], **{"d3_" + a: b for a, b in d3[r["k"]].items()}}) for r in rows if r["k"] in d3]
n3 = sorted(both[0]["f"])
cv(both, [n for n in n3 if n.startswith("d3_")], "depth pose only, same windows")
cv(both, n3, "image-plane + depth pose")
