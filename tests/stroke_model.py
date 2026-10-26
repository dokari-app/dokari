"""Stroke classifier on skeleton swing windows, trained on work/stroke_labels.json (labels from the frames alone).
Features: hand-built, mirror-free body measurements + the aligned pose window. Evaluated on held-out videos."""
import json, os, sys, glob, collections, pickle
import numpy as np
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, ".")
from sphere.skeleton import J

NPH = 20
PRE, POST = 0.9, 0.4        # causal: the decision is taken 0.4 s after the swing event, using only what has happened by then
KEEP = ["nose", "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist", "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle"]
KI = [J[k] for k in KEEP]
SW = [KEEP.index(("r_" + k[2:]) if k.startswith("l_") else ("l_" + k[2:]) if k.startswith("r_") else k) for k in KEEP]


def clip_arrays(npz):
    d = np.load(npz, allow_pickle=True)
    P = gaussian_filter1d(d["pose"], 1.5, axis=0, mode="nearest")
    fps = float(d["fps"])
    ms = (P[:, J["l_shoulder"]] + P[:, J["r_shoulder"]]) / 2; mh = (P[:, J["l_hip"]] + P[:, J["r_hip"]]) / 2
    torso = float(np.median(np.linalg.norm(ms - mh, axis=1))) or 0.5
    sp = {s: gaussian_filter1d(np.linalg.norm(np.gradient(P[:, J[f"{s}_wrist"]], axis=0), axis=1) * fps / torso, 2) for s in "lr"}
    # dominant (racket) side of the player in this clip: the wrist that reaches the higher speeds, most of the time
    dom = "r" if np.percentile(sp["r"], 97) >= np.percentile(sp["l"], 97) else "l"
    return P, d["vis"], fps, torso, sp, dom


def features(P, vis, fps, torso, sp, dom, pk_t):
    pk = int(round(pk_t * fps))
    lo, hi = pk - int(PRE * fps), pk + int(POST * fps)
    if lo < 0 or hi >= len(P):
        return None
    oth = "l" if dom == "r" else "r"
    W = P[:, J[f"{dom}_wrist"]]; Wo = P[:, J[f"{oth}_wrist"]]
    sh_d, sh_o = P[:, J[f"{dom}_shoulder"]], P[:, J[f"{oth}_shoulder"]]
    ms = (P[:, J["l_shoulder"]] + P[:, J["r_shoulder"]]) / 2; mh = (P[:, J["l_hip"]] + P[:, J["r_hip"]]) / 2
    nose = P[:, J["nose"]]
    lat = sh_d - sh_o; lat[:, 1] = 0
    n = np.linalg.norm(lat, axis=1, keepdims=True) + 1e-6; lat = lat / n          # dominant side direction, per frame
    seg = slice(lo, hi + 1)
    # peak near pk of the dominant wrist (the labelled peak may be the other wrist)
    a, b = max(lo, pk - int(0.2 * fps)), min(hi, pk + int(0.2 * fps))   # (hi = pk + 0.4 s)
    pkd = a + int(np.argmax(sp[dom][a:b + 1]))
    vel = np.gradient(W, axis=0) * fps / torso
    f = {}
    up = (W[:, 1] - nose[:, 1]) / torso
    f["wrist_above_head_max"] = float(up[seg].max())
    f["wrist_above_head_at_peak"] = float(up[pkd])
    f["wrist_above_head_pre"] = float(up[lo:pkd + 1].max())
    f["wrist_height_vs_hip_at_peak"] = float((W[pkd, 1] - mh[pkd, 1]) / torso)
    f["wrist_low_min"] = float(((W[seg, 1] - mh[seg, 1]) / torso).min())
    f["peak_speed_dom"] = float(sp[dom][pkd]); f["peak_speed_oth"] = float(sp[oth][pkd])
    f["speed_ratio"] = f["peak_speed_dom"] / (f["peak_speed_oth"] + 0.5)
    f["vy_at_peak"] = float(vel[pkd, 1]); f["v_lat_at_peak"] = float((vel[pkd] * lat[pkd]).sum())
    f["vy_mean_pm"] = float(vel[max(lo, pkd - 3):pkd + 4, 1].mean())
    f["vlat_mean_pm"] = float((vel[max(lo, pkd - 3):pkd + 4] * lat[max(lo, pkd - 3):pkd + 4]).sum(1).mean())
    f["wrists_apart_mean"] = float(np.linalg.norm(W[seg] - Wo[seg], axis=1).mean() / torso)
    f["wrists_apart_peak"] = float(np.linalg.norm(W[pkd] - Wo[pkd]) / torso)
    f["wrists_apart_min"] = float(np.linalg.norm(W[seg] - Wo[seg], axis=1).min() / torso)
    f["amp_wrist"] = float(np.linalg.norm(W[seg].max(0) - W[seg].min(0)) / torso)
    side = ((W[seg] - mh[seg]) * lat[seg]).sum(1) / torso
    f["wrist_side_min"] = float(side.min()); f["wrist_side_max"] = float(side.max()); f["wrist_side_peak"] = float(((W[pkd] - mh[pkd]) * lat[pkd]).sum() / torso)
    fwd = np.cross(lat, np.array([0, 1.0, 0]))                      # forward direction in the ground plane (sign set by body chirality)
    f["wrist_fwd_peak"] = float(((W[pkd] - mh[pkd]) * fwd[pkd]).sum() / torso)
    f["wrist_fwd_range"] = float(np.ptp(((W[seg] - mh[seg]) * fwd[seg]).sum(1) / torso))
    f["hip_drop"] = float((mh[seg, 1].max() - mh[seg, 1].min()) / torso)
    f["trunk_lean_peak"] = float(np.degrees(np.arctan2(np.linalg.norm((ms[pkd] - mh[pkd])[[0, 2]]), (ms[pkd] - mh[pkd])[1])))
    for nm, (j1, j2, j3) in {"elbow": ("shoulder", "elbow", "wrist")}.items():
        u = P[pkd, J[f"{dom}_shoulder"]] - P[pkd, J[f"{dom}_elbow"]]; v = P[pkd, J[f"{dom}_wrist"]] - P[pkd, J[f"{dom}_elbow"]]
        f["elbow_angle_peak"] = float(np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9), -1, 1))))
    kn = []
    for s in "lr":
        u = P[pkd, J[f"{s}_hip"]] - P[pkd, J[f"{s}_knee"]]; v = P[pkd, J[f"{s}_ankle"]] - P[pkd, J[f"{s}_knee"]]
        kn.append(np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9), -1, 1))))
    f["knee_min_peak"] = float(min(kn))
    f["ankle_spread"] = float(np.linalg.norm((P[pkd, J["l_ankle"]] - P[pkd, J["r_ankle"]])[[0, 2]]) / torso)
    f["nose_to_wrist_peak"] = float(np.linalg.norm(W[pkd] - nose[pkd]) / torso)
    # time from the lowest wrist point to the peak (long wind-up vs punch)
    f["t_low_to_peak"] = float((pkd - (lo + int(np.argmin(W[lo:pkd + 1, 1])))) / fps)
    f["t_speed_gt_half"] = float((sp[dom][seg] > 0.5 * sp[dom][pkd]).sum() / fps)
    L0, L1 = max(0, pk - int(2.4 * fps)), min(len(P) - 1, pk + int(POST * fps))      # long context: a serve takes 2-3 s from toss to contact
    upo = (Wo[:, 1] - nose[:, 1]) / torso
    f["long_dom_above_head_max"] = float(up[L0:L1 + 1].max())
    f["long_oth_above_head_max"] = float(upo[L0:L1 + 1].max())
    f["oth_above_head_max"] = float(upo[seg].max())
    f["long_dom_oth_height_gap"] = float(np.max(up[L0:L1 + 1] - upo[L0:L1 + 1]))
    f["long_wrist_range_y"] = float(np.ptp(W[L0:L1 + 1, 1]) / torso)
    f["long_n_speed_peaks"] = float(len(__import__("scipy.signal", fromlist=["find_peaks"]).find_peaks(sp[dom][L0:L1 + 1], height=2.5, distance=int(0.5 * fps))[0]))
    f["long_hip_drop"] = float(np.ptp(mh[L0:L1 + 1, 1]) / torso)
    # symmetric (hand-free) description of a 3 s window centred on the peak: does not need to know which hand is which
    CPRE = 2.6
    C0, C1 = max(0, pk - int(CPRE * fps)), min(len(P) - 1, pk + int(POST * fps))
    upl, upr = (P[C0:C1 + 1, J["l_wrist"], 1] - nose[C0:C1 + 1, 1]) / torso, (P[C0:C1 + 1, J["r_wrist"], 1] - nose[C0:C1 + 1, 1]) / torso
    hi, lo_ = (upl, upr) if upl.max() >= upr.max() else (upr, upl)
    f["w3_hi_up_max"] = float(hi.max()); f["w3_lo_up_max"] = float(lo_.max())
    f["w3_hi_up_time"] = float((np.argmax(hi) + C0 - pk) / fps)
    f["w3_up_both_gap"] = float(np.max(np.minimum(upl, upr)))               # both hands high together (rare outside a serve toss/smash prep)
    sl, sr_ = sp["l"][C0:C1 + 1], sp["r"][C0:C1 + 1]
    fast, slow = (sl, sr_) if sl.max() >= sr_.max() else (sr_, sl)
    f["w3_fast_peak"] = float(fast.max()); f["w3_slow_peak"] = float(slow.max()); f["w3_fast_over_slow"] = float(fast.max() / (slow.max() + 0.5))
    f["w3_fast_peak_time"] = float((np.argmax(fast) + C0 - pk) / fps)
    ap = np.linalg.norm(P[C0:C1 + 1, J["l_wrist"]] - P[C0:C1 + 1, J["r_wrist"]], axis=1) / torso
    f["w3_apart_min"] = float(ap.min()); f["w3_apart_mean"] = float(ap.mean()); f["w3_apart_at_fast"] = float(ap[int(np.argmax(fast))])
    f["w3_time_both_close"] = float((ap < 0.45).mean())                       # share of the window with hands together (two-handed grip)
    f["w3_n_fast_peaks"] = float(len(__import__("scipy.signal", fromlist=["find_peaks"]).find_peaks(fast, height=2.5, distance=int(0.5 * fps))[0]))
    sw = "l" if sl.max() >= sr_.max() else "r"; swo = "r" if sw == "l" else "l"
    shl = P[:, J[f"{sw}_shoulder"]] - P[:, J[f"{swo}_shoulder"]]; shl[:, 1] = 0; shl = shl / (np.linalg.norm(shl, axis=1, keepdims=True) + 1e-6)
    ip = C0 + int(np.argmax(fast)); vv = np.gradient(P[:, J[f"{sw}_wrist"]], axis=0) * fps / torso
    f["w3_swingwrist_vlat"] = float((vv[ip] * shl[ip]).sum()); f["w3_swingwrist_vy"] = float(vv[ip, 1])
    f["w3_swingwrist_side"] = float(((P[ip, J[f"{sw}_wrist"]] - mh[ip]) * shl[ip]).sum() / torso)
    f["w3_swing_is_dom"] = float(sw == dom)
    f["height_torso_m"] = float(torso)
    # aligned window in a dominant-side body frame (lateral = dominant shoulder direction at the peak), lefties already mirrored by 'dom'
    l0 = lat[pkd]; ang = np.arctan2(-l0[0], l0[2]); c, s_ = np.cos(ang), np.sin(ang)
    R = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    Q = (P[seg] @ R.T - (mh[pkd] @ R.T)) / torso
    if dom == "l":
        Q = Q * np.array([-1, 1, 1]); Q = Q[:, [J[KEEP[i]] for i in SW]] if False else Q
    t = np.linspace(0, len(Q) - 1, NPH)
    A = np.zeros((NPH, len(KEEP), 3))
    for k, ji in enumerate(KI):
        for cc in range(3):
            A[:, k, cc] = np.interp(t, np.arange(len(Q)), Q[:, ji, cc])
    if dom == "l":
        A = A[:, SW]
    return f, A


def hands():
    """racket hand per video from the frames (tests/stroke_hand.py): 'r'/'l', majority of the answered frames, when clear."""
    out = {}
    if os.path.exists("work/stroke_hands.json"):
        for k, fr in json.load(open("work/stroke_hands.json")).items():
            c = collections.Counter(x["racket_hand"] for x in fr if x["racket_hand"] != "unclear" and x.get("one_player", True))
            if sum(c.values()) >= 2 and c.most_common(1)[0][1] / sum(c.values()) >= 0.67:
                out[k] = "r" if c.most_common(1)[0][0] == "player_right" else "l"
    return out


HANDS = {}
GUESS = {}


def load(path="work/stroke_labels2.json", shifts=(0.0,), strict=True):
    lab = json.load(open(path))
    cache, rows = {}, []
    HANDS.update(hands())
    for k, v in lab.items():
        parts = k.split("/")
        act, vid = parts[0], parts[1]
        if v.get("stroke") is None:
            continue
        if v.get("stroke") == "none" or v.get("shown") == "not_a_stroke":
            v = dict(v, stroke="no_stroke", shown="not_a_stroke")
        elif strict and v.get("contact_in_frames") == "no":
            continue
        if v["stroke"] == "no_stroke":
            pass
        elif strict and v["stroke"] == "serve" and v.get("ball_toss_seen") == "no" and v.get("hit_above_head") == "no":
            continue                       # called a serve with neither a toss nor an overhead hit: not trusted
        elif strict and v["stroke"] in ("forehand", "backhand", "slice") and v.get("hit_above_head") == "yes":
            continue
        npz = f"work/{act}/clips/{vid}.npz"
        if npz not in cache:
            cache[npz] = clip_arrays(npz) if os.path.exists(npz) else None
        c = cache[npz]
        if c is None:
            continue
        hk = f"{act}/{vid}"
        GUESS[hk] = c[-1]
        c = c[:-1] + (HANDS.get(hk, "r"),)     # the frames say which hand holds the racket; otherwise assume right-handed (87% of players; no skeleton-speed guess beats that)
        for sh in shifts:
            r = features(*c, v["peak"] + sh)
            if r is None:
                continue
            rows.append(dict(known_hand=hk in HANDS, act=act, vid=vid, pk=v["peak"], shift=sh, kind=v.get("kind", "?"), stroke=v["stroke"], grip=v.get("grip"), shown=v["shown"], conf=v["confidence"], clean=v["view_clean"], f=r[0], A=r[1]))
    return rows


def main():
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import GroupKFold
    path = sys.argv[1] if len(sys.argv) > 1 else "work/stroke_labels2.json"
    shifts = (-0.6, -0.3, 0.0, 0.3, 0.6)
    rows = load(path, shifts)
    base = [r for r in rows if r["shift"] == 0.0]
    both = [k for k in HANDS if k in GUESS]
    print(f"racket hand known from the frames for {len(HANDS)} videos; the skeleton-only guess agrees on {sum(HANDS[k] == GUESS[k] for k in both)}/{len(both)}; right-handed {sum(v == 'r' for v in HANDS.values())}, left-handed {sum(v == 'l' for v in HANDS.values())}")
    print("labelled windows usable:", len(base), dict(collections.Counter(r["stroke"] for r in base)))
    tab = collections.defaultdict(collections.Counter)
    for r in base: tab[r["act"]][r["stroke"]] += 1
    print("what the frames show, by the activity each video was collected for:")
    for a, c in sorted(tab.items()): print("  ", a, dict(c))
    keep = [r for r in rows if r["conf"] >= 2]
    cnt = collections.Counter(r["stroke"] for r in keep if r["shift"] == 0.0)
    classes = sorted(k for k, n in cnt.items() if n >= 20 and k != "other")
    keep = [r for r in keep if r["stroke"] in classes]
    print("classes:", {k: cnt[k] for k in classes}, "| videos", len({r["vid"] for r in keep}))
    if len(classes) < 2:
        return
    names = sorted(keep[0]["f"])
    X = np.array([[r["f"][n] for n in names] for r in keep]); y = np.array([classes.index(r["stroke"]) for r in keep])
    g = np.array([r["vid"] for r in keep]); sh = np.array([r["shift"] for r in keep])
    vids = sorted(set(g)); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    fi = np.array([fold[v] for v in g])
    pred = np.zeros(len(y), int)
    for k in range(5):
        tr, te = fi != k, fi == k
        m = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, class_weight="balanced", random_state=0).fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    def report(mask, label):
        yy, pp = y[mask], pred[mask]
        print(f"\n[{label}] held-out accuracy {np.mean(yy == pp):.3f} on {mask.sum()} windows")
        print("  recall:", {c: round(float(np.mean(pp[yy == i] == i)), 2) for i, c in enumerate(classes) if (yy == i).any()})
        cm = np.zeros((len(classes),) * 2, int)
        for a_, b_ in zip(yy, pp): cm[a_, b_] += 1
        print("  rows = what the frames show, cols = predicted:", classes)
        for i, c in enumerate(classes): print("   ", f"{c:10s}", cm[i])
    report(sh == 0.0, "windows anchored on the detected event")
    report(sh != 0.0, "windows shifted 0.3-0.6 s either way (what a live sliding window sees)")
    m = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, class_weight="balanced", random_state=0).fit(X, y)
    pickle.dump(dict(model=m, names=names, classes=classes), open("work/stroke_model_handbuilt.pkl", "wb"))


main()
