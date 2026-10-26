"""Fused-template experiment (forehand). Reads existing skeleton clips + labels; changes nothing in the factory.
Steps: extract labelled forehand attempts -> body-frame normalisation (swing direction, hitting side, scale)
-> phase alignment around peak wrist speed -> template of right demos (mean + spread per phase/joint)
-> score held-out wrong vs right demos (grouped by video)."""
import json, sys, os, collections
import numpy as np
sys.path.insert(0, ".")
from sphere.skeleton import J
from scipy.ndimage import gaussian_filter1d

MODE = sys.argv[3] if len(sys.argv) > 3 else "swing"
ACT = sys.argv[1] if len(sys.argv) > 1 else "tennis_forehand"
STROKE = sys.argv[2] if len(sys.argv) > 2 else "forehand"
W = f"work/{ACT}"
L = json.load(open(f"{W}/labels.json"))
NPH = 40
PRE, POST = 0.9, 0.6          # seconds around peak wrist speed
KEEP = ["nose", "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist",
        "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle"]
KI = [J[k] for k in KEEP]


def smooth(p):
    return gaussian_filter1d(p, 1.5, axis=0, mode="nearest")


def normalise(pose, vis, fps):
    """Return (T,13,3) in a body frame: origin mid-hip at peak time, x = swing direction, y up, z = lateral with the
    hitting arm on +z (mirrors left-handers), scaled by torso length. Also returns peak index, hand ('r'/'l'), info."""
    P = smooth(pose)
    sp = {}
    for side in "lr":
        w = P[:, J[f"{side}_wrist"]]
        v = np.linalg.norm(np.gradient(w, axis=0), axis=1) * fps
        sp[side] = gaussian_filter1d(v, 2)
    side = "r" if sp["r"].max() >= sp["l"].max() else "l"
    pk = int(np.argmax(sp[side]))
    w = P[:, J[f"{side}_wrist"]]
    a, b = max(0, pk - 3), min(len(P) - 1, pk + 3)
    d = w[b] - w[a]
    d[1] = 0
    n = np.linalg.norm(d)
    if n < 1e-6:
        return None
    d /= n
    other = "l_shoulder" if side == "r" else "r_shoulder"
    if MODE == "shoulders":
        # lateral axis from the shoulder + hip lines at the swing peak (hitting side = +z); forward x = z cross y
        lat = (P[pk, J[f"{side}_shoulder"]] - P[pk, J[other]]) + (P[pk, J["r_hip" if side == "r" else "l_hip"]] - P[pk, J["l_hip" if side == "r" else "r_hip"]])
        lat[1] = 0
        nl = np.linalg.norm(lat)
        if nl < 1e-6:
            return None
        lat /= nl
        ang = np.arctan2(-lat[0], lat[2])      # rotate so lat -> +z
    else:
        ang = np.arctan2(d[2], d[0])
    c, s_ = np.cos(ang), np.sin(ang)
    R = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    Q = P @ R.T
    shz = (Q[pk, J[f"{side}_shoulder"]] - Q[pk, J[other]])[2]
    if MODE != "shoulders" and shz < 0:
        Q = Q * np.array([-1, 1, -1])          # swing direction was read backwards: turn the body round
        shz = -shz
    if side == "l":
        Q = Q * (np.array([-1, 1, 1]) if MODE == "shoulders" else np.array([1, 1, -1]))
    mh = (Q[:, J["l_hip"]] + Q[:, J["r_hip"]]) / 2
    ms = (Q[:, J["l_shoulder"]] + Q[:, J["r_shoulder"]]) / 2
    scale = np.median(np.linalg.norm(ms - mh, axis=1))
    if scale < 0.1:
        return None
    Q = (Q - mh[pk]) / scale
    return Q, pk, side, sp[side][pk] / scale, shz


def swap_lr(idx):
    out = []
    for k in KEEP:
        if k.startswith("l_"):
            out.append(KEEP.index("r_" + k[2:]))
        elif k.startswith("r_"):
            out.append(KEEP.index("l_" + k[2:]))
        else:
            out.append(KEEP.index(k))
    return out


SW = swap_lr(None)


def phase_resample(Q, V, pk, fps):
    t = np.arange(len(Q)) / fps
    tp = t[pk]
    ph = np.concatenate([np.linspace(tp - PRE, tp, NPH // 2 * 1, endpoint=False), np.linspace(tp, tp + POST, NPH // 2)])
    out = np.zeros((NPH, len(KEEP), 3))
    vo = np.zeros((NPH, len(KEEP)))
    for j, ji in enumerate(KI):
        for c in range(3):
            out[:, j, c] = np.interp(ph, t, Q[:, ji, c])
        vo[:, j] = np.interp(ph, t, V[:, ji])
    return out, vo


def collect(stroke=None):
    stroke = stroke or STROKE
    rows = []
    for vid, rec in L["clips"].items():
        f = f"{W}/clips/{vid}.npz"
        if not os.path.exists(f):
            continue
        d = np.load(f, allow_pickle=True)
        pose, vis, fps = d["pose"], d["vis"], float(d["fps"])
        for at in rec["attempts"]:
            if at.get("not_an_attempt") or at.get("stroke") != stroke or not at.get("view_clean"):
                continue
            a, b = int(at["window"][0] * fps), int(at["window"][1] * fps)
            if b - a < int(0.8 * fps) or b > len(pose):
                continue
            r = normalise(pose[a:b], vis[a:b], fps)
            if r is None:
                continue
            Q, pk, side, spd, shz = r
            X, V = phase_resample(Q, vis[a:b], pk, fps)
            if side == "l":
                X = X[:, SW]
                V = V[:, SW]
            rows.append(dict(shz=shz if side == 'r' else -shz, vid=vid, seg=at.get("segment", "?"), X=X, V=V, side=side, spd=spd,
                             present=at.get("present", []), absent=at.get("absent", []), faults=at.get("segment_faults", [])))
    return rows


def dist(X, mu, sd, V):
    z = (X - mu) / sd
    w = np.clip(V, 0, 1)[:, :, None]
    return float(np.sqrt((w * z ** 2).sum() / (w.sum() * 3 + 1e-9)))


def auc(pos, neg):
    pos, neg = np.array(pos), np.array(neg)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()))


def main():
    rows = collect()
    c = collections.Counter(r["seg"] for r in rows)
    print("usable", STROKE, "attempts:", len(rows), "videos:", len({r["vid"] for r in rows}), dict(c))
    print("shoulder-line sign (consistency):", collections.Counter(np.sign(r["shz"]) for r in rows))
    print("hitting side:", collections.Counter(r["side"] for r in rows))
    right = [r for r in rows if r["seg"] == "right_demo"]
    wrong = [r for r in rows if r["seg"] == "wrong_demo"]
    other = [r for r in rows if r["seg"] not in ("right_demo", "wrong_demo")]
    print("right", len(right), "videos", len({r['vid'] for r in right}), "| wrong", len(wrong), "videos", len({r['vid'] for r in wrong}))
    vids = sorted({r["vid"] for r in rows})
    rng = np.random.RandomState(0)
    rng.shuffle(vids)
    K = 5
    fold = {v: i % K for i, v in enumerate(vids)}
    sc = collections.defaultdict(list)
    scored_rows = []
    for k in range(K):
        # template: right demos + other swings considered "ordinary" are NOT used; right demos only (train videos)
        tr = [r for r in right if fold[r["vid"]] != k]
        if len(tr) < 5:
            continue
        Xs = np.stack([r["X"] for r in tr])
        mu = np.median(Xs, 0)
        sd = 1.4826 * np.median(np.abs(Xs - mu), 0) + 0.05
        for r in rows:
            if fold[r["vid"]] == k:
                _d = dist(r["X"], mu, sd, r["V"]); sc[r["seg"]].append((r["vid"], _d)); scored_rows.append((r, _d))
    R = [s for _, s in sc["right_demo"]]
    Wn = [s for _, s in sc["wrong_demo"]]
    print("held-out AUC wrong>right:", round(auc(Wn, R), 3), "n", len(Wn), len(R))
    print("median dist right %.2f wrong %.2f" % (np.median(R), np.median(Wn)) if R and Wn else "")
    # within-video pairs
    by = collections.defaultdict(lambda: {"r": [], "w": []})
    for v, s in sc["right_demo"]:
        by[v]["r"].append(s)
    for v, s in sc["wrong_demo"]:
        by[v]["w"].append(s)
    pairs = [(np.mean(d["w"]) > np.mean(d["r"])) for d in by.values() if d["r"] and d["w"]]
    print("within-video pairs:", len(pairs), "wrong farther from template in", sum(pairs))
    # other segments for reference
    for seg in ("mixed_demo", "match_play", "talking", "other"):
        s = [x for _, x in sc[seg]]
        if s:
            print(seg, len(s), "median dist %.2f" % np.median(s))
    # which phase/joint differ most between wrong and right
    if right and wrong:
        XR = np.stack([r["X"] for r in right]); XW = np.stack([r["X"] for r in wrong])
        sdp = 1.4826 * np.median(np.abs(XR - np.median(XR, 0)), 0) + 0.05
        dd = np.abs(np.median(XW, 0) - np.median(XR, 0)) / sdp
        ph, jn = np.unravel_index(np.argsort(-dd.max(2).ravel())[:6], dd.max(2).shape)
        print("largest wrong-vs-right shifts (phase 0-1, joint):", [(round(p / NPH, 2), KEEP[j], round(float(dd[p, j].max()), 2)) for p, j in zip(ph, jn)])
    # strong labels only: coach-confirmed fault present vs right demo with the fault absent
    strong_w = [r for r in wrong if r["present"]]
    strong_r = [r for r in right if not r["present"]]
    Xs = np.stack([r["X"] for r in strong_r]); mu = np.median(Xs, 0); sd = 1.4826 * np.median(np.abs(Xs - mu), 0) + 0.05
    print("strong labels (in-sample template, optimistic):", len(strong_w), len(strong_r))
    # sanity: does the template tell a forehand from other strokes? (held-out by video)
    oth = collect("serve") + collect("backhand")
    fr = [s for _, s in sc["right_demo"]]
    tr_all = [r for r in right]
    Xa = np.stack([r["X"] for r in tr_all]); mua = np.median(Xa, 0); sda = 1.4826 * np.median(np.abs(Xa - mua), 0) + 0.05
    so = [dist(r["X"], mua, sda, r["V"]) for r in oth]
    print("sanity: other strokes", len(oth), "median dist %.2f vs forehand-right %.2f" % (np.median(so), np.median(fr)), "AUC other>forehand", round(auc(so, fr), 3))
    # per fault, held-out template
    fcount = collections.Counter(f for r in wrong for f in r["present"])
    print("faults with >=8 wrong demos:", {k: v for k, v in fcount.items() if v >= 8})
    for f, n in fcount.items():
        if n < 8:
            continue
        sw = [sc2 for r, sc2 in scored_rows if r["seg"] == "wrong_demo" and f in r["present"]]
        print("  ", f, n, "AUC vs right", round(auc(sw, R), 3))
    np.savez(f"work/fuse_{ACT}.npz", X=np.stack([r["X"] for r in rows]), seg=[r["seg"] for r in rows], vid=[r["vid"] for r in rows])


if __name__ == "__main__":
    main()
