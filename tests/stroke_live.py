"""Replay your own clips the way the live app sees them: events are found as they happen (overhead reach, wrist-speed peak),
and each is classified 0.4 s later from the past only. Prints the timeline and compares with what was filmed.
  python tests/stroke_live.py [work/stroke_model_handbuilt.pkl]"""
import sys, pickle, os, glob
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, ".")
src = open("tests/stroke_model.py").read().replace("\nmain()\n", "\n"); ns = {}; exec(compile(src, "sm", "exec"), ns)
from sphere.skeleton import J
M = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else "work/stroke_model_handbuilt.pkl", "rb"))
TRUTH = {"IMG_2935 3": [(0, 1e9, "serve")], "IMG_2935": [(0, 1e9, "forehand")], "IMG_2935 2": [(0, 50, "serve")]}
HAND = sys.argv[2] if len(sys.argv) > 2 else "r"
tot = ok = 0
for stem, tr in TRUTH.items():
    f = f"work/check/as_filmed/{stem}.skeleton.npz"
    if not os.path.exists(f):
        continue
    P, vis, fps, torso, sp, dom = ns["clip_arrays"](f)
    nose = P[:, J["nose"]]
    up = np.stack([(P[:, J[f"{s}_wrist"], 1] - nose[:, 1]) / torso for s in "lr"]).max(0)
    spm = np.maximum(sp["l"], sp["r"])
    ov, _ = find_peaks(gaussian_filter1d(up, 2), height=0.45, distance=int(3.0 * fps))
    pk, _ = find_peaks(spm, height=max(3.0, 0.35 * np.percentile(spm, 99)), distance=int(1.5 * fps))
    pk = [p for p in pk if all(abs(p - o) > 1.5 * fps for o in ov) and up[p] < 0.45]
    ev = sorted([(o / fps, "over") for o in ov] + [(p / fps, "swing") for p in pk])
    print(f"\n{stem}: {len(ev)} events")
    preds = []
    for t, kind in ev:
        # causal: only the past up to t + 0.4 s is given
        cut = int((t + 0.4) * fps) + 1
        # dominant side must also be causal: estimated from the past only
        Pc = P[:cut]; spc = {s: sp[s][:cut] for s in "lr"}
        dom_c = HAND                      # the player says which hand (setting in the app)
        r = ns["features"](Pc, vis[:cut], fps, torso, spc, dom_c, t)
        if r is None:
            continue
        x = np.array([[r[0][n] for n in M["names"]]])
        pr = M["model"].predict_proba(x)[0]; k = int(np.argmax(pr)); lab = M["classes"][k]
        preds.append((t, kind, lab, float(pr[k]), {c: float(p) for c, p in zip(M["classes"], pr)}))
    # merge: an overhead stroke (serve/smash) takes the events around it (toss and bounce before, follow-through after)
    # that are not themselves a confident groundstroke on a different beat; an event is dropped when it falls inside
    # [-2.4 s, +0.8 s] of an overhead event or of a serve-classified event, and the stronger serve call is kept.
    anchors = [p for p in preds if (p[1] == "over" or p[2] in ("serve", "smash")) and p[4].get("serve", 0) + p[4].get("smash", 0) >= 0.5]
    anchors.sort(key=lambda p: (p[1] != "over", -p[3]))
    kept, used = [], set()
    for a in anchors:
        if a[0] in used:
            continue
        kept.append(a); used.add(a[0])
        for p in preds:
            if p[0] != a[0] and -0.8 <= p[0] - a[0] <= 2.4 or (p[0] != a[0] and -2.4 <= a[0] - p[0] <= 0.0 and False):
                used.add(p[0])
        for p in preds:
            if -2.4 <= p[0] - a[0] <= 0.8:
                used.add(p[0])
    kept += [p for p in preds if p[0] not in used]
    kept.sort()
    print(f"  after merging: {len(kept)} strokes")
    for t, kind, lab, conf, _ in kept:
        truth = [l for a, b, l in tr if a <= t < b]
        mark = ""
        if truth:
            tot += 1; ok += int(lab == truth[0]); mark = "ok" if lab == truth[0] else f"WRONG (filmed: {truth[0]})"
        print(f"  t={t:6.1f}s {kind:5s} -> {lab:9s} ({conf:.2f})  {mark}")
print(f"\nagainst what was filmed: {ok}/{tot} events correct")
