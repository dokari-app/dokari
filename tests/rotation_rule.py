"""Rule from the coach texts (knowledge.json): 'rotation not started before the racket goes forward', 'shoulder behind at
contact', 'kinetic chain legs, hips, trunk, then arm'. Four measurements fixed in advance from those words (no fitting):
  onset_gap  = when the racket starts forward minus when the hips start turning (ms; larger = rotation earlier = good)
  chain_lag  = shoulder-line peak turn time minus hip-line peak turn time (ms; larger = hips lead = good)
  hip_lead   = wrist peak time minus hip-line peak turn time (ms)
  sho_fwd    = hitting shoulder ahead of the other shoulder along the swing direction at contact (shoulder widths; larger = good)
Test: wrong demos naming rotation vs right demos from the same videos."""
import json, os, sys, collections
import numpy as np
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, ".")
from sphere.skeleton import J

W = "work/tennis_forehand"
L = json.load(open(f"{W}/labels.json"))
FAULT = sys.argv[1] if len(sys.argv) > 1 else "rotation_late_or_blocked"


def feats(P, vis, fps):
    P = gaussian_filter1d(P, 1.5, axis=0, mode="nearest")
    sp = {}
    for s in "lr":
        w = P[:, J[f"{s}_wrist"]]
        sp[s] = gaussian_filter1d(np.linalg.norm(np.gradient(w, axis=0), axis=1) * fps, 2)
    side = "r" if sp["r"].max() >= sp["l"].max() else "l"
    other = "l" if side == "r" else "r"
    v = sp[side]; pk = int(np.argmax(v))
    w = P[:, J[f"{side}_wrist"]]
    a, b = max(0, pk - 3), min(len(P) - 1, pk + 3)
    d = w[b] - w[a]; d[1] = 0
    if np.linalg.norm(d) < 1e-6:
        return None
    d /= np.linalg.norm(d)
    def yaw(j1, j2):
        u = P[:, J[j2]] - P[:, J[j1]]
        return gaussian_filter1d(np.unwrap(np.arctan2(u[:, 2], u[:, 0])), 2)
    hy = yaw("l_hip", "r_hip"); sy = yaw("l_shoulder", "r_shoulder")
    hr = np.abs(np.gradient(hy)) * fps; sr = np.abs(np.gradient(sy)) * fps
    lo, hi = max(0, pk - int(0.9 * fps)), min(len(P), pk + int(0.15 * fps))
    if hi - lo < 8:
        return None
    t = np.arange(len(P)) / fps
    ih = lo + int(np.argmax(hr[lo:hi])); is_ = lo + int(np.argmax(sr[lo:hi]))
    def onset(x, i_pk):
        seg = x[lo:i_pk + 1]
        thr = 0.25 * x[i_pk]
        idx = np.where(seg >= thr)[0]
        # first sustained crossing
        return lo + (idx[0] if len(idx) else len(seg) - 1)
    oh = onset(hr, ih); ow = onset(v, pk)
    shw = np.linalg.norm((P[pk, J["l_shoulder"]] - P[pk, J["r_shoulder"]])[[0, 2]]) + 1e-6
    sho = (P[pk, J[f"{side}_shoulder"]] - P[pk, J[f"{other}_shoulder"]])
    return dict(onset_gap=1000 * (t[ow] - t[oh]), chain_lag=1000 * (t[is_] - t[ih]), hip_lead=1000 * (t[pk] - t[ih]),
                sho_fwd=float(sho[[0, 2]] @ d[[0, 2]] / shw))


rows = []
for vid, rec in L["clips"].items():
    f = f"{W}/clips/{vid}.npz"
    if not os.path.exists(f):
        continue
    dd = np.load(f, allow_pickle=True); pose, vis, fps = dd["pose"], dd["vis"], float(dd["fps"])
    for at in rec["attempts"]:
        if at.get("not_an_attempt") or at.get("stroke") != "forehand" or not at.get("view_clean"):
            continue
        a, b = int(at["window"][0] * fps), int(at["window"][1] * fps)
        if b - a < int(0.8 * fps) or b > len(pose):
            continue
        r = feats(pose[a:b], vis[a:b], fps)
        if r is None:
            continue
        seg = at.get("segment"); sf = at.get("segment_faults", []); pr = at.get("present", []); ab = at.get("absent", [])
        if seg == "wrong_demo" and (FAULT in sf or FAULT in pr):
            y = 1
        elif FAULT in pr:
            y = 1
        elif seg == "right_demo" and (FAULT in sf or not pr) or FAULT in ab:
            y = 0
        else:
            continue
        rows.append(dict(vid=vid, y=y, **r))
print("fault", FAULT, "| wrong", sum(r["y"] for r in rows), "right", sum(1 - r["y"] for r in rows),
      "| videos", len({r["vid"] for r in rows}))


def auc(pos, neg):
    pos, neg = np.array(pos), np.array(neg)
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())) if len(pos) and len(neg) else float("nan")


rng = np.random.RandomState(0)
for k in ("onset_gap", "chain_lag", "hip_lead", "sho_fwd"):
    pos = [r[k] for r in rows if r["y"] == 1]; neg = [r[k] for r in rows if r["y"] == 0]
    a = auc(neg, pos)       # P(right swing scores higher than wrong swing) = expected direction
    nulls = []
    ys = np.array([r["y"] for r in rows]); xs = np.array([r[k] for r in rows])
    for _ in range(500):
        yp = rng.permutation(ys); nulls.append(auc(xs[yp == 0], xs[yp == 1]))
    by = collections.defaultdict(lambda: {0: [], 1: []})
    for r in rows: by[r["vid"]][r["y"]].append(r[k])
    pairs = [np.mean(v[0]) > np.mean(v[1]) for v in by.values() if v[0] and v[1]]
    print(f"{k:10s} AUC right>wrong {a:.3f}  (permutation p={np.mean(np.array(nulls) >= a):.3f})  within-video: right higher in {sum(pairs)}/{len(pairs)}   medians right {np.median(neg):.0f}/{np.median(neg):.2f} wrong {np.median(pos):.2f}")
