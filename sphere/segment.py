"""Activity-agnostic segmentation of a clip into attempts.

An attempt is a short sequence of body events, in order, each one an excursion of a feature (it leaves its rest
value, reaches an extreme, and comes back). A squat is one event (the hips fall); a serve is two (the tossing
wrist rises, then the hitting wrist rises). It does not matter whether a clip holds one attempt or fifty. The
activity proposal names the events and their order; the data decides where they happen and how large they are."""
import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.signal import find_peaks, peak_widths


def _fill_nan(F):
    F = F.copy()
    for j in range(F.shape[1]):
        col = F[:, j]
        bad = np.isnan(col)
        if bad.all():
            F[:, j] = 0.0
        elif bad.any():
            idx = np.arange(len(col))
            col[bad] = np.interp(idx[bad], idx[~bad], col[~bad])
    return F


def dominant_mode(F, min_scale=1e-6):
    """Return (pc1 signal, loadings, mean, scale) for features F (T, D)."""
    X = _fill_nan(F)
    mean = X.mean(0)
    scale = X.std(0)
    scale = np.where(scale < min_scale, 1.0, scale)
    Z = (X - mean) / scale
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    load = Vt[0]
    return Z @ load, load, mean, scale


MIN_SWING_DEG = 40.0      # an attempt of a body movement changes some joint angle by at least this much
MIN_SWING_REL = 0.2       # same, for features that are not angles (heights, widths, deviations; body-relative units)
MAX_JUMP_DEG = 70.0       # no joint angle changes by more than this between two frames at 30 fps: more means a
                          # tracking failure or a camera cut, not a body. The elbow of a fast forehand really moves about 50 a frame
                          # (it was 45 before and threw real swings away); single-frame flicker is repaired before this test
MAX_JUMP_REL = 1.0        # same for body-relative positions (torso lengths per frame at 30 fps): the wrist of a fast
                          # swing moves well under this; clean footage stays below about 0.4, failed tracking jumps over 1
MAX_ROUGH_DEG = 10.0      # median angular acceleration (degrees per frame squared at 30 fps) of an attempt. A body
                          # moves smoothly (clean footage 2 to 5); a tracker that flickers does not (6 to 16)
CANDIDATE_LEVEL = 0.8     # an event's level is a coarse filter for candidates, not the judge: a modest performance of the action (a low toss) may sit a little under the level the proposal named.
                          # Whether a candidate really is the action is decided by how well it fits the entry's signature (identify), so candidates are let in at this share of the level.
                          # Only for actions of several events: their order also tells the action apart, while a single event has only its level to do it
MIN_VALID = 0.8           # share of an attempt's frames that must be believable


def valid_mask(F, fps, names, watch=()):
    """True where the pose is physically believable: visible, and not part of a jump no body could make.
    Joint angles are always checked; `watch` names body-relative features (heights, reaches) that are checked too."""
    ang = [i for i, n in enumerate(names) if n.startswith("angle.")]
    T = len(F)
    bad = np.isnan(F[:, ang]).mean(1) > 0.5
    A = _fill_nan(F[:, ang])
    over = (np.abs(np.diff(A, axis=0)).max(1) > MAX_JUMP_DEG * 30.0 / fps) if T > 1 else np.zeros(0, bool)
    rel = [names.index(n) for n in watch if not n.startswith("angle.")]
    if rel and T > 1:
        over = over | (np.abs(np.diff(_fill_nan(F[:, rel]), axis=0)).max(1) > MAX_JUMP_REL * 30.0 / fps)
    bad[1:] |= over
    bad[:-1] |= over
    k = 1
    bad = np.convolve(bad.astype(float), np.ones(2 * k + 1), mode="same") > 0
    return ~bad


def swing_units(F, a, b, cols, thr, need=1):
    """Swing in units of what a real attempt needs (1.0 = just enough), counting only when at least `need`
    of the given columns swing together: the movement is the joints moving as a group, not one joint gesturing."""
    seg = F[a:b + 1][:, cols]
    if len(seg) == 0 or np.isnan(seg).all():
        return 0.0
    u = np.sort(np.nan_to_num((np.nanmax(seg, 0) - np.nanmin(seg, 0)) / thr))[::-1]
    return float(u[min(need, len(u)) - 1])


def roughness(F, a, b, cols, fps):
    """Median angular acceleration (degrees per frame squared at 30 fps) over the angle columns of an attempt."""
    X = _fill_nan(F[a:b + 1][:, cols])
    if len(X) < 4 or not len(cols):
        return 0.0
    d2 = np.abs(np.diff(X, 2, axis=0)) * (30.0 / fps) ** 2
    return float(np.median(np.max(d2, axis=1)))


def excursions(sig, fps, thr):
    """Excursions of a signal whose extreme is a peak: [(start, peak, end, prominence)]. The window runs from where the
    signal leaves its rest value to where it is back, padded by a quarter of its length on each side (the preparation and
    the finish belong to the attempt), never into a neighbour. An excursion the clip ends in the middle of is dropped."""
    T = len(sig)
    k = 2 * max(1, int(round(0.07 * fps))) + 1
    s = gaussian_filter1d(median_filter(sig, size=k, mode="nearest"), sigma=max(1.0, 0.05 * fps))
    pk, pr = find_peaks(s, prominence=thr, distance=max(1, int(0.5 * fps)))
    if len(pk) == 0:
        return []
    w = peak_widths(s, pk, rel_height=0.9, prominence_data=(pr["prominences"], pr["left_bases"], pr["right_bases"]))
    out = []
    for i, p in enumerate(pk):
        l, r = w[2][i], w[3][i]
        floor = s[p] - 0.6 * pr["prominences"][i]
        if s[int(l)] > floor or s[min(T - 1, int(np.ceil(r)))] > floor:
            continue
        pad = 0.25 * (r - l)
        lo = (pk[i - 1] + p) / 2 if i else 0
        hi = (p + pk[i + 1]) / 2 if i + 1 < len(pk) else T - 1
        a, b = int(max(lo, l - pad)), int(min(hi, r + pad))
        if 0.4 * fps <= b - a <= 20 * fps:
            out.append((a, int(p), b, float(pr["prominences"][i])))
    return out


MIN_GAP_S = 0.1           # the events of one action follow each other: a peak at (nearly) the same moment as the previous event's is one gesture, not the next event
MAX_GAP_S = 4.0           # the events of one action follow each other within seconds (a toss and its hit)
PAD_S = 2.5               # the preparation before the first event and the finish after the last: at most this long


def _chain(per_event, fps, secs=None):
    """Attempts as chains of connected excursions, one per event, in the order the events are listed.
    per_event[k] = excursions (start, peak, end, prominence) of event k. A chain ends at an excursion of the last event;
    each earlier event must have an excursion that peaks at least MIN_GAP_S before the next one, within MAX_GAP_S of it, and connected to it
    (its window ends no later than one window length before the next one starts). Returns
    [(start, end, prominence_of_last_event, [peak of each event])].
    `secs[k]` (optional) = how long event k takes, from leaving rest to being back. With it, an attempt is one stroke, not a
    stretch of many: the earlier event is the nearest one before the next (not a bigger one from the previous stroke), the gap
    between two events is at most one and a half times the time they take together, the preparation and finish are no longer than the events themselves, and
    chains that would merge into something much longer than one attempt stay separate."""
    secs = secs if secs and all(x for x in secs) else None
    pad_s = min(PAD_S, 0.75 * max(secs)) if secs else PAD_S
    out = []
    for a, p, b, pr in per_event[-1]:
        lo, hi, ok, peaks, pn = a, b, True, [p], p
        for k in range(len(per_event) - 2, -1, -1):
            gap_s = min(MAX_GAP_S, 1.5 * (secs[k] + secs[k + 1])) if secs else MAX_GAP_S
            cands = [(a2, p2, b2, pr2) for a2, p2, b2, pr2 in per_event[k]
                     if MIN_GAP_S * fps <= pn - p2 <= gap_s * fps and b2 >= lo - (hi - lo) and p2 >= lo - 3 * (hi - lo)]
            if not cands:
                ok = False
                break
            a2, p2, b2, _ = max(cands, key=(lambda c: c[1]) if secs else (lambda c: c[3]))
            lo, hi, pn = min(lo, a2), max(hi, b2), p2
            peaks.insert(0, p2)
        if ok:
            lo = max(lo, peaks[0] - pad_s * fps) if len(peaks) > 1 else lo
            hi = min(hi, peaks[-1] + pad_s * fps) if len(peaks) > 1 else hi
            out.append((lo, hi, pr, peaks))
    out.sort(key=lambda c: c[0])
    longest = (2 * sum(secs) + 2 * pad_s) * fps if secs else None
    merged = []                      # two chains that share an excursion are one attempt
    for c in out:
        if merged and c[0] < merged[-1][1]:
            m = merged[-1]
            if longest and max(m[1], c[1]) - m[0] > longest:          # they would make a stretch of several strokes: keep the clearer one
                if c[2] > m[2]:
                    merged[-1] = c
                continue
            merged[-1] = (m[0], max(m[1], c[1]), max(m[2], c[2]), m[3] if m[2] >= c[2] else c[3])
        else:
            merged.append(c)
    return merged


def segment_attempts(F, fps, names, events, primary=None):
    """Attempts of one clip. `events` = ordered list of {"feature": ..., "direction": "rises"|"falls"}: what a body does,
    in order, in one attempt (a squat: the hips fall; a serve: the tossing wrist rises, then the hitting wrist rises).
    An event may carry "seconds": how long it takes, from leaving its rest value to being back (see _chain).
    `primary` = the features that characterise the movement; an attempt must move them as a group, so gestures
    elsewhere in the body do not count.
    Returns dict(method, attempts=[(start, end)], prominence, rough, duration, signal, valid, valid_share, cols)."""
    primary = list(primary or [])
    for e in events:
        if e["feature"] not in primary:
            primary.append(e["feature"])
    cols = [names.index(n) for n in primary]
    valid = valid_mask(F, fps, names, watch=primary)
    per_event = []
    for e in events:
        sign = 1.0 if e["direction"] == "rises" else -1.0
        sig = _fill_nan(F[:, [names.index(e["feature"])]])[:, 0] * sign
        ex = excursions(sig, fps, MIN_SWING_DEG if e["feature"].startswith("angle.") else MIN_SWING_REL)
        if e.get("peak_at_least") is not None:       # the event must reach this level (e.g. a tossing wrist above the head)
            lvl = sign * float(e["peak_at_least"]) * (CANDIDATE_LEVEL if len(events) > 1 else 1.0)
            ex = [x for x in ex if sig[max(0, x[1] - 2):x[1] + 3].max() >= lvl]
        per_event.append(ex)
    thr = np.array([MIN_SWING_DEG if names[i].startswith("angle.") else MIN_SWING_REL for i in cols])
    need = max(1, int(np.ceil(len(cols) / 2)))
    ang_cols = [i for i in cols if names[i].startswith("angle.")]
    att, prom, rough, dur, pks = [], [], [], [], []
    for a, b, pr, pk in _chain(per_event, fps, [e.get("seconds") for e in events]):
        a, b = max(0, int(a)), min(len(F) - 1, int(b))
        if not 0.4 * fps <= b - a <= 20 * fps:
            continue
        r = roughness(F, a, b, ang_cols, fps)
        if valid[a:b + 1].mean() >= MIN_VALID and swing_units(F, a, b, cols, thr, need) >= 1.0 and r <= MAX_ROUGH_DEG:
            att.append((a, b)); pks.append(pk); prom.append(pr); rough.append(r); dur.append((b - a) / fps)
    first = events[-1]
    return {"method": "events", "attempts": att, "peaks": pks, "prominence": prom, "rough": rough, "duration": dur,
            "signal": _fill_nan(F[:, [names.index(first["feature"])]])[:, 0],
            "valid": valid, "valid_share": float(valid.mean()), "cols": cols}


def resample_anchored(F, a, b, peaks, n=50):
    """Time-normalise F[a:b] to n samples with the events lined up: the window start, each event peak and the window end sit
    at the same fixed positions in every attempt, so the average of many attempts shows the sequence, not a smear of it."""
    seg = _fill_nan(F[a:b + 1])
    k = len(peaks)
    src = np.array([0.0] + [min(max(p - a, 1), len(seg) - 2) for p in peaks] + [len(seg) - 1.0])
    dst = np.concatenate([[0.0], np.linspace(0.35, 0.65, k) if k > 1 else [0.5], [1.0]]) * (n - 1)
    if np.any(np.diff(src) <= 0):
        return resample(F, a, b, n)
    t = np.interp(np.arange(n), dst, src)
    return np.stack([np.interp(t, np.arange(len(seg)), seg[:, j]) for j in range(seg.shape[1])], axis=1)


def resample(F, a, b, n=50):
    """Time-normalise F[a:b] to n samples."""
    seg = _fill_nan(F[a:b + 1])
    x = np.linspace(0, 1, len(seg))
    xi = np.linspace(0, 1, n)
    return np.stack([np.interp(xi, x, seg[:, j]) for j in range(seg.shape[1])], axis=1)
