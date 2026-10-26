"""Calibration: turn collected attempts into key poses, conventional ranges, recognition
signatures and fault thresholds. Everything here is activity-agnostic and data-driven."""
import numpy as np
from scipy.signal import find_peaks
from .segment import resample_anchored, dominant_mode, resample, segment_attempts, _fill_nan
from .features import compute_features, FEATURES

N_T = 50          # samples per time-normalised attempt


def mad_sigma(x, axis=0):
    med = np.nanmedian(x, axis=axis, keepdims=True)
    return 1.4826 * np.nanmedian(np.abs(x - med), axis=axis)


def _is_trusted(trusted, c, i):
    w = c.get("windows")
    return bool(trusted) and w is not None and i < len(w) and bool(trusted(c["clip_id"], w[i]))


def _pick(c, idx, **more):
    """The collection with only the attempts at positions idx. Everything kept per attempt (the attempt itself, its time
    window in the video, and what was measured about it) stays in step."""
    out = dict(c, **more)
    for k in ("attempts", "windows", "prominence", "rough", "duration"):
        if k in c and len(c[k]) == len(c["attempts"]):
            out[k] = [c[k][i] for i in idx]
    return out


def collect_attempts(clip, events, primary=None, min_attempts=2):
    """Features -> attempts (chains of the activity's events) -> time-normalised attempts for one clip."""
    names, F, info = compute_features(clip)
    seg = segment_attempts(F, clip["fps"], names, events, primary)
    arrs = [resample_anchored(F, a, b, pk, N_T) if len(pk) > 1 else resample(F, a, b, N_T)
            for (a, b), pk in zip(seg["attempts"], seg["peaks"])]
    meta = clip["meta"]
    return {"clip_id": meta.get("id", "?"), "tag": meta.get("tag", "unlabelled"),
            "view_yaw_deg": info["view_yaw_deg"], "method": seg["method"],
            "prominence": seg["prominence"], "rough": seg["rough"], "duration": seg["duration"], "valid_share": seg["valid_share"],
            "attempts": arrs, "windows": [(round(a / clip["fps"], 2), round(b / clip["fps"], 2)) for a, b in seg["attempts"]],
            "usable": len(arrs) >= min_attempts}


def size_gate(collections, frac=0.4, tempo=4.0, min_attempts=2, trusted=None):
    """The last event of a real attempt is large and lasts about as long in every clip. Small bumps of the signal
    (a fidget, a ball bounce, a step) are not attempts, and neither is a position held for many times the usual time.
    The typical excursion is the median over clips of each clip's largest excursion: clips that hold the movement show it
    at full size, and clips that do not cannot pull the reference down. An attempt is kept if its excursion is at least
    `frac` of that and its duration is within a factor `tempo` of the typical duration (median over clips of each clip's
    median), loose enough that shallow, weak, slow or hurried form survives. An attempt in `trusted` (clip id, window) has been confirmed
    as a real attempt by looking at it and is kept whatever its size."""
    have = [c for c in collections if c["prominence"]]
    if not have:
        return collections, {"applied": False}
    ref = float(np.median([max(c["prominence"]) for c in have]))
    ref_d = float(np.median([np.median(c["duration"]) for c in have]))
    out = []
    for c in collections:
        keep = [i for i, (p, d) in enumerate(zip(c["prominence"], c["duration"]))
                if (p >= frac * ref and ref_d / tempo <= d <= ref_d * tempo) or _is_trusted(trusted, c, i)]
        out.append(_pick(c, keep, n_candidates=len(c["attempts"]), usable=len(keep) >= min_attempts or any(_is_trusted(trusted, c, i) for i in keep)))
    return out, {"applied": True, "typical_excursion": round(ref, 3), "minimum": round(frac * ref, 3), "typical_seconds": round(ref_d, 2)}


def stack(collections):
    """-> A (N, N_T, D), and per-attempt meta list."""
    arrs, meta = [], []
    for c in collections:
        if not c["usable"]:
            continue
        base = len(meta)
        for a in c["attempts"]:
            arrs.append(a)
            meta.append({"clip_id": c["clip_id"], "tag": c["tag"], "view_yaw_deg": c["view_yaw_deg"],
                         "window": c["windows"][len(meta) - base] if "windows" in c and len(c["windows"]) == len(c["attempts"]) else None})
    return (np.stack(arrs) if arrs else np.zeros((0, N_T, len(FEATURES)))), meta


def find_landmarks(A, max_landmarks=6):
    """Landmarks (time indices in the normalised attempt) = start, end and the turning points
    of the dominant mode of the mean attempt."""
    mean_curve = np.nanmedian(A, axis=0)                       # (N_T, D)
    sig, *_ = dominant_mode(mean_curve)
    rng = sig.max() - sig.min()
    prom = 0.2 * rng
    hi, ph = find_peaks(sig, prominence=prom)
    lo, pl = find_peaks(-sig, prominence=prom)
    cand = [(int(i), float(p)) for i, p in zip(hi, ph["prominences"])] + \
           [(int(i), float(p)) for i, p in zip(lo, pl["prominences"])]
    cand.sort(key=lambda t: -t[1])
    keep = sorted(i for i, _ in cand[:max_landmarks - 2])
    idx = [0] + [i for i in keep if 2 < i < N_T - 3] + [N_T - 1]
    return idx, sig


def key_poses(A, landmarks, top_k=10):
    """Per-landmark feature statistics, and the features that best characterise the movement."""
    D = A.shape[2]
    stats = []
    for li in landmarks:
        w = A[:, max(0, li - 1):li + 2, :]
        v = np.nanmedian(w, axis=1)                              # (N, D)
        stats.append({"median": np.nanmedian(v, 0), "sigma": mad_sigma(v, 0),
                      "p5": np.nanpercentile(v, 5, 0), "p95": np.nanpercentile(v, 95, 0)})
    med = np.stack([s["median"] for s in stats])                # (L, D)
    sig = np.stack([s["sigma"] for s in stats])
    between = np.nanstd(np.nanmedian(A, axis=0), axis=0)         # variation along the cycle
    within = np.nanmean(sig, axis=0)
    scale = np.nanmedian(np.abs(A - np.nanmedian(A)), axis=(0, 1)) + 1e-6
    importance = between / (within + 0.05 * (np.nanstd(A, axis=(0, 1)) + 1e-6))
    importance = np.nan_to_num(importance)
    top = np.argsort(-importance)[:top_k]
    return stats, top, importance


def events_present(a, events, names):
    """Does one time-normalised attempt contain the events that define the activity, in order? Each event feature must make
    an excursion of the size the attempt finder asks for (and reach its level, if the event has one), and the peaks must
    follow one another (allowing events that happen together). A movement that merely resembles the average attempt,
    but lacks the defining events, is not this activity."""
    from .segment import MIN_SWING_DEG, MIN_SWING_REL
    tol = int(round(0.09 * (len(a) - 1)))
    t_prev = -10 ** 9
    for e in events:
        sign = 1.0 if e["direction"] == "rises" else -1.0
        x = a[:, names.index(e["feature"])] * sign
        if np.isnan(x).all():
            return False
        thr = MIN_SWING_DEG if e["feature"].startswith("angle.") else MIN_SWING_REL
        top, bottom = np.nanmax(x), np.nanmin(x)
        if top - bottom < thr:
            return False
        if e.get("peak_at_least") is not None:
            level = 0.9 * float(e["peak_at_least"]) * sign        # 10% slack: resampling to 50 steps softens a sharp peak
            if top < level:
                return False
        else:
            level = bottom + 0.5 * (top - bottom)
        # the event happens at the first moment (not before the previous event, give or take a few steps) the feature reaches its level
        ok = np.where(np.nan_to_num(x, nan=-1e9) >= level)[0]
        ok = ok[ok >= t_prev - tol]
        if len(ok) == 0:
            return False
        t_prev = int(ok[0])
    return True


class Signature:
    """The average attempt and its spread. How strict the match must be is learned from how far a clip the signature has
    never seen lies from it: with several clips, each is left out in turn, and the threshold covers 97.5% of those
    unseen-clip scores (never stricter than 1.25 times the 95th percentile of the training scores). A different
    camera angle, person or lighting is then expected to land inside; with few clips the older, tighter rule applies."""
    def __init__(self, A, feat_idx, events=None, names=None, clip_ids=None):
        self.events, self.names = events, names
        self.feat_idx = np.asarray(feat_idx)
        self._fit(A)
        scores = np.array([self.score(a) for a in A])
        self.threshold = float(np.nanpercentile(scores, 95) * 1.25 + 1e-6)
        ids = np.asarray(clip_ids) if clip_ids is not None else None
        if ids is not None and len(set(ids)) >= 3:
            inner = []
            for j in sorted(set(ids)):
                tr = ids != j
                sub = Signature(A[tr], feat_idx)
                inner += [sub.score(a) for a in A[~tr]]
            self.threshold = max(self.threshold, float(np.nanpercentile(inner, 97.5)))

    def _fit(self, A):
        X = A[:, :, self.feat_idx]
        self.mean = np.nanmedian(X, axis=0)
        self.std = np.nanstd(X, axis=0)
        rng = np.nanmax(self.mean, axis=0) - np.nanmin(self.mean, axis=0)
        self.floor = 0.15 * rng + 1e-3

    def score(self, a):
        x = a[:, self.feat_idx]
        s = np.maximum(self.std, self.floor)
        return float(np.nanmean(((x - self.mean) / s) ** 2))

    def accepts(self, a):
        return self.score(a) <= self.threshold and (not self.events or events_present(a, self.events, self.names))


def recognition_report(A, meta, others=None, top_k=10, events=None, names=None):
    """Leave-one-clip-out recall on the activity's own clips, false-accept rate on other
    activities' attempts, and recall by viewing angle."""
    _, top, _ = key_poses(A, find_landmarks(A)[0], top_k)
    clip_ids = sorted({m["clip_id"] for m in meta})
    hits, by_view = [], {"front/back (<30)": [], "oblique (30-60)": [], "side (>60)": []}
    if len(clip_ids) >= 2:
        for cid in clip_ids:
            tr = np.array([m["clip_id"] != cid for m in meta])
            sig = Signature(A[tr], top, events, names, [m["clip_id"] for m in meta if m["clip_id"] != cid])
            for a, m in zip(A[~tr], [m for m in meta if m["clip_id"] == cid]):
                ok = sig.accepts(a); hits.append(ok)
                y = m["view_yaw_deg"]
                by_view["front/back (<30)" if y < 30 else "oblique (30-60)" if y <= 60 else "side (>60)"].append(ok)
        recall, mode = float(np.mean(hits)), "leave-one-clip-out"
    else:
        sig = Signature(A, top, events, names)
        hits = [sig.accepts(a) for a in A]
        recall, mode = float(np.mean(hits)), "resubstitution (optimistic; only one clip)"
    sig = Signature(A, top, events, names, [m["clip_id"] for m in meta])
    fa = fa_sig = None
    if others is not None and len(others):
        fa = float(np.mean([sig.accepts(a) for a in others]))
        fa_sig = float(np.mean([sig.score(a) <= sig.threshold for a in others]))      # the average-shape test alone
    return {"recall": recall, "recall_mode": mode, "false_accept_rate_vs_other_activities": fa,
            "false_accept_rate_shape_only": fa_sig,
            "recall_by_view": {k: (float(np.mean(v)) if v else None) for k, v in by_view.items()},
            "n_attempts": int(len(A)), "n_clips": len(clip_ids)}, sig


def _auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if len(pos) == 0 or len(neg) == 0:
        return None
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort() + 1
    u = ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2
    return float(u / (len(pos) * len(neg)))


def _cut(good, bad, sides):
    """The cut that separates labelled good from labelled bad values best (Youden's J) and how well the sides separate them (AUC).
    With both sides the score is the distance from the median of the good ones."""
    if sides == {"above"}:
        s_of, centre = (lambda x: x), None
    elif sides == {"below"}:
        s_of, centre = (lambda x: -x), None
    else:
        centre = float(np.median(good))
        s_of = lambda x: np.abs(x - centre)
    sg, sb = s_of(good), s_of(bad)
    best, bj = None, -1
    for c in np.unique(np.concatenate([sg, sb])):
        j = np.mean(sb >= c) - np.mean(sg >= c)
        if j > bj:
            bj, best = j, float(c)
    return {"best": best, "centre": centre, "auc": _auc(sb, sg), "s_of": s_of}


def _bounds(cut, sides):
    if sides == {"above"}:
        return None, cut["best"]
    if sides == {"below"}:
        return -cut["best"], None
    return cut["centre"] - cut["best"], cut["centre"] + cut["best"]


def _held_out_accuracy(v, cids, gm, bm, sides):
    """Balanced accuracy of the cut on labelled attempts of a video it was not fitted on (leave-one-video-out); None if there is too little to test."""
    hit_g, hit_b = [], []
    for c in sorted(set(cids[gm | bm])):
        tr = cids != c
        g, b = v[gm & tr], v[bm & tr]
        if len(g) < 3 or len(b) < 3:
            continue
        cut = _cut(g, b, sides)
        for sel, hits, want in ((gm & ~tr, hit_g, False), (bm & ~tr, hit_b, True)):
            if sel.any():
                hits += list((cut["s_of"](v[sel]) >= cut["best"]) == want)
    if not hit_g or not hit_b:
        return None
    return (float(np.mean(hit_g)) + float(np.mean(hit_b))) / 2


REF_MIN_CLIPS, REF_MIN_ATTEMPTS = 3, 15          # fewer good-form demonstrations than this cannot say what good looks like


def target_range(values, sides, pct, clips=None):
    """Where a NEW clip of good performance should fall: (low, high), None for a side that does not matter. Each side leaves out
    `pct` percent. Attempts from one video are alike (same person, camera and style), so with `clips` (one id per value) and at
    least three videos the range allows for the spread between videos as well as within them: mean of the video medians plus or
    minus a t-quantile times the spread of a new attempt in a new video. Pooling the attempts as if each were independent gives a range
    that is too narrow for new videos (on real squat footage, held-out demonstrations fell outside it four times as often as it
    claimed). Without enough videos the plain percentiles are used."""
    from scipy.stats import t as t_dist
    v = np.asarray(values, float)
    ok = np.isfinite(v)
    v = v[ok]
    if not len(v):
        return None, None
    ids = np.asarray(clips)[ok] if clips is not None else None
    if ids is not None and len(set(ids)) >= 3:
        groups = [v[ids == c] for c in sorted(set(ids))]
        med = np.array([np.median(g) for g in groups])
        within = [np.var(g) for g in groups if len(g) >= 2]
        n = len(groups)
        spread = float(np.sqrt(med.var(ddof=1) * (1 + 1.0 / n) + (np.mean(within) if within else 0.0)))
        z = float(t_dist.ppf(1 - pct / 100.0, df=n - 1))               # few videos: the spread between them is itself uncertain
        centre = float(med.mean())
        lo, hi = centre - z * spread, centre + z * spread
    else:
        lo, hi = np.percentile(v, [pct, 100 - pct])
    return (float(lo) if "below" in sides else None, float(hi) if "above" in sides else None)


def within_limits(lo, hi, limits):
    """A bound outside what the feature can physically be (an angle below 0 or above 180) can never be crossed: that side drops out."""
    if limits is None:
        return lo, hi
    return (None if lo is not None and lo <= limits[0] else lo), (None if hi is not None and hi >= limits[1] else hi)


def calibrate_objective(A, meta, feat_idx, landmark, sides, reference_clips=None, tag=None, limits=None):
    """The target range for 'feature at landmark stays inside the range', on the sides ('below', 'above') that can be wrong.
    Labelled attempts (tag 'good' versus `tag` or any other tag): the cut that separates them best (Youden's J, AUC); with both
    sides the cut is a distance from the median of the good ones. That cut is used only if it also tells right from wrong on videos it was not
    fitted on; otherwise it is reported (`labelled`) but the range comes from the sources below. Otherwise the range comes from footage of good performances
    (clips in `reference_clips`: the central 90% of what they do, allowing for differences between videos); without enough of that, from everyday footage (central 80%),
    which only says what is typical and is marked as such. Never validated without labels."""
    sides = set(sides)
    v = np.nanmedian(A[:, max(0, landmark - 1):landmark + 2, feat_idx], axis=1)
    tags = np.array([m["tag"] for m in meta])
    cids = np.array([m["clip_id"] for m in meta])
    fin = np.isfinite(v)
    good = v[(tags == "good") & fin]
    bad = v[((tags == tag) if tag else ((tags != "good") & (tags != "unlabelled"))) & fin]
    ref = np.isin(cids, list(reference_clips)) if reference_clips else np.zeros(len(v), bool)
    n_ref_clips = len(set(cids[ref & np.isfinite(v)]))
    out = {"auc": None, "validated": False, "n_good": int(len(good)), "n_bad": int(len(bad)),
           "n_reference_attempts": int((ref & np.isfinite(v)).sum()), "n_reference_clips": n_ref_clips}
    info = None
    if len(good) >= 3 and len(bad) >= 3:
        cut = _cut(good, bad, sides)
        lo, hi = within_limits(*_bounds(cut, sides), limits)
        gm = (tags == "good") & np.isfinite(v)
        bm = ((tags == tag) if tag else ((tags != "good") & (tags != "unlabelled"))) & np.isfinite(v)
        n_gc, n_bc = len(set(cids[gm])), len(set(cids[bm]))
        held = _held_out_accuracy(v, cids, gm, bm, sides)
        ok = cut["auc"] is not None and cut["auc"] >= 0.75 and held is not None and held >= 0.7 and n_gc >= 2 and n_bc >= 2
        info = {"n_good": int(len(good)), "n_bad": int(len(bad)), "n_good_clips": n_gc, "n_bad_clips": n_bc, "auc": cut["auc"],
                "held_out_accuracy": None if held is None else round(held, 3), "validated": bool(ok)}
        if ok:        # a cut from labelled examples replaces the range from demonstrations only when it has shown it works on videos it was not fitted on
            return dict(out, low=lo, high=hi, auc=cut["auc"], validated=True, basis="labelled", n_good_clips=n_gc, n_bad_clips=n_bc,
                        held_out_accuracy=info["held_out_accuracy"], labelled=info)
    if n_ref_clips >= REF_MIN_CLIPS and out["n_reference_attempts"] >= REF_MIN_ATTEMPTS:
        lo, hi = within_limits(*target_range(v[ref], sides, 5, cids[ref]), limits)
        return dict(out, low=lo, high=hi, basis="good_form_demonstrations", **({"labelled": info} if info else {}))
    lo, hi = within_limits(*target_range(v, sides, 10, cids), limits)
    return dict(out, low=lo, high=hi, basis="everyday_footage", **({"labelled": info} if info else {}))


def _shape_dist(a, mean, scale, feat):
    return float(np.nanmean(np.abs(a[:, feat] - mean[:, feat]) / scale[feat]))


def curate(collections, tol_factor=2.0, rounds=4, primary=None, min_travel=0.4, trusted=None):
    """Keep only attempts that look like the repeated movement the clips are about.

    Activity-agnostic, no activity knowledge. Start from the median attempt of everything, then repeat:
    take the closest half of all attempts, recompute the typical attempt from that core, measure every attempt
    against it. Junk (talking, holds, other movement) is the minority and drops out of the core; the typical
    attempt converges on the movement. The final tolerance is loose on purpose: faulty form must survive,
    because faults live in the tails; only things that are not the movement at all are dropped."""
    usable = [c for c in collections if c["usable"]]
    if len(usable) < 2:
        return collections, {"applied": False, "reason": "fewer than two usable clips"}
    items = [(ci, a) for ci, c in enumerate(collections) if c["usable"] for a in c["attempts"]]
    A = np.stack([a for _, a in items])
    gscale = np.maximum(1.4826 * np.nanmedian(np.abs(A - np.nanmedian(A, axis=(0, 1))), axis=(0, 1)),
                        0.05 * np.nanstd(A, axis=(0, 1))) + 1e-3
    cons = np.nanmedian(A, axis=0)
    _, top, _ = key_poses(A, find_landmarks(A)[0], 10)
    for _ in range(rounds):
        d = np.array([_shape_dist(a, cons, gscale, top) for a in A])
        core = A[d <= np.median(d)]
        cons = np.nanmedian(core, axis=0)
        _, top, _ = key_poses(core, find_landmarks(core)[0], 10)
    scale = np.maximum(1.4826 * np.nanmedian(np.abs(core - cons), axis=(0, 1)), 0.05 * np.nanstd(core, axis=(0, 1))) + 1e-3
    d = np.array([_shape_dist(a, cons, scale, top) for a in A])
    d_core = d[d <= np.median(d)]
    tol = max(float(np.percentile(d_core, 95)) * tol_factor, float(np.median(d_core) + 4 * 1.4826 * np.median(np.abs(d_core - np.median(d_core)))))
    keep_flags = d <= tol
    if primary:         # an attempt must travel at least a good fraction of what the typical attempt travels
        cols_ = [FEATURES.index(n) for n in primary]
        ptp = lambda X: np.nanmax(X[..., cols_], axis=-2) - np.nanmin(X[..., cols_], axis=-2)
        ref_sw = np.nanmedian(ptp(core), axis=0) + 1e-6
        travel = np.array([np.nanmedian(ptp(a) / ref_sw) for a in A])
        keep_flags = keep_flags & (travel >= min_travel)
    in_core = d <= np.median(d)
    out, rows = [], []
    for ci, c in enumerate(collections):
        if not c["usable"]:
            out.append(c); continue
        idx = [i for i, (cj, _) in enumerate(items) if cj == ci]
        keep_pos = [j for j, i in enumerate(idx) if keep_flags[i]]
        keep = [items[idx[j]][1] for j in keep_pos]
        sure = [j for j in range(len(idx)) if _is_trusted(trusted, c, j)]
        core_frac = float(np.mean([in_core[i] for i in idx])) if idx else 0.0
        foreign = len(idx) >= 4 and len(keep) < 0.4 * len(idx)      # most of the clip does not look like the movement
        if foreign:                                                  # then the few that passed are chance, not the movement
            keep, keep_pos = [], []
        if sure:                                                     # attempts confirmed by looking at them are never dropped here
            keep_pos = sorted(set(keep_pos) | set(sure))
            keep = [items[idx[j]][1] for j in keep_pos]
        out.append(_pick(c, keep_pos, usable=len(keep) >= 2 or bool(sure), n_before=len(idx)))
        rows.append({"clip": c["clip_id"], "before": len(idx), "kept": len(keep), "seed": core_frac >= 0.5, "foreign": foreign,
                     "dist": round(float(np.median([d[i] for i in idx])), 2) if idx else None})
    return out, {"applied": True, "seed_basis": "typical attempt found by repeatedly keeping the closest half of all attempts",
                 "seed_clips": [r["clip"] for r in rows if r["seed"]], "tolerance": round(tol, 3), "clips": rows,
                 "kept": sum(r["kept"] for r in rows), "total": sum(r["before"] for r in rows)}


def align_cycles(collections):
    """Repetitions are loops, so where one is cut is arbitrary: one clip may start every rep at the top,
    another at the bottom. Rotate each clip's attempts (circular shift in normalised time) so that all clips
    start at the same point of the cycle, using the clip closest to all the others as reference. Applies to
    every clip whose attempts end where they start (loops); a shift is only used if it clearly helps."""
    use = [c for c in collections if c["usable"] and len(c["attempts"]) >= 2]
    if len(use) < 2:
        return collections, {"applied": False}
    allA = np.stack([a for c in use for a in c["attempts"]])
    gscale = np.maximum(1.4826 * np.nanmedian(np.abs(allA - np.nanmedian(allA, axis=(0, 1))), axis=(0, 1)),
                        0.05 * np.nanstd(allA, axis=(0, 1))) + 1e-3

    def closed(c):
        """The attempt ends close to where it started, compared with how far it travelled in between."""
        r = []
        for a in c["attempts"]:
            travel = np.nanmax(np.abs(a - a[0]), axis=0)
            moving = travel > gscale
            if moving.any():
                r.append(np.nanmedian(np.abs(a[0] - a[-1])[moving] / travel[moving]))
        return bool(r) and float(np.median(r)) < 0.3
    cyc = [c for c in use if closed(c)]
    if len(cyc) < 2:
        return collections, {"applied": False}
    med = {id(c): np.nanmedian(np.stack(c["attempts"]), axis=0) for c in cyc}

    def best_shift(m, ref):
        costs = [np.nanmean(np.abs(np.roll(m, k, axis=0) - ref) / gscale) for k in range(N_T)]
        k = int(np.argmin(costs))
        return (k if costs[k] < 0.8 * costs[0] else 0), float(costs[k])
    tot = {id(r): sum(best_shift(med[id(c)], med[id(r)])[1] for c in cyc if c is not r) for r in cyc}
    ref = min(cyc, key=lambda r: tot[id(r)])
    shifts, out = {}, []
    for c in collections:
        if c in cyc and c is not ref:
            k, _ = best_shift(med[id(c)], med[id(ref)])
            shifts[c["clip_id"]] = k
            out.append(dict(c, attempts=[np.roll(a, k, axis=0) for a in c["attempts"]]) if k else c)
        else:
            out.append(c)
    return out, {"applied": True, "reference": ref["clip_id"], "shifts": shifts}


def align_attempts(collections, rounds=2, trusted=None):
    """Second, finer alignment: each loop-like attempt is rotated on its own to best match the consensus
    attempt, because one clip can mix repetitions cut at different points of the cycle."""
    use = [c for c in collections if c["usable"] and c["attempts"]]
    if not use:
        return collections
    allA = np.stack([a for c in use for a in c["attempts"]])
    gscale = np.maximum(1.4826 * np.nanmedian(np.abs(allA - np.nanmedian(allA, axis=(0, 1))), axis=(0, 1)),
                        0.05 * np.nanstd(allA, axis=(0, 1))) + 1e-3

    def is_loop(a):
        travel = np.nanmax(np.abs(a - a[0]), axis=0)
        mv = travel > gscale
        return bool(mv.any()) and float(np.nanmedian(np.abs(a[0] - a[-1])[mv] / travel[mv])) < 0.3
    cons = np.nanmedian(allA, axis=0)
    out = collections
    if np.mean([is_loop(a) for a in allA]) >= 0.6:       # the movement is a loop: attempts that are not cannot be cycles of it
        out = []
        for c in collections:
            if c["usable"]:
                ok = [i for i, a in enumerate(c["attempts"]) if is_loop(a) or _is_trusted(trusted, c, i)]
                c = _pick(c, ok, usable=len(ok) >= 2 or any(_is_trusted(trusted, c, i) for i in ok))
            out.append(c)
        allA = np.stack([a for c in out if c["usable"] for a in c["attempts"]])
        cons = np.nanmedian(allA, axis=0)
    for _ in range(rounds):
        new = []
        for c in out:
            if not c["usable"] or not c["attempts"]:
                new.append(c); continue
            att = []
            for a in c["attempts"]:
                if is_loop(a):
                    costs = [np.nanmean(np.abs(np.roll(a, k, axis=0) - cons) / gscale) for k in range(N_T)]
                    k = int(np.argmin(costs))
                    a = np.roll(a, k, axis=0) if costs[k] < 0.85 * costs[0] else a
                att.append(a)
            new.append(dict(c, attempts=att))
        out = new
        cons = np.nanmedian(np.stack([a for c in out if c["usable"] for a in c["attempts"]]), axis=0)
    return out


def cap_per_clip(collections, cap=15, trusted=None):
    """Clips are the independent samples, so no clip may outweigh the others: keep at most `cap` attempts per
    clip, evenly spread through the clip."""
    out = []
    for c in collections:
        n = len(c["attempts"])
        if n > cap:
            sure = [i for i in range(n) if _is_trusted(trusted, c, i)]
            rest = [i for i in range(n) if i not in sure]
            room = max(0, cap - len(sure))
            pick = [rest[int(j)] for j in np.round(np.linspace(0, len(rest) - 1, room)).astype(int)] if rest and room else []
            c = _pick(c, sorted(set(sure) | set(pick)), n_found=n)
        out.append(c)
    return out
