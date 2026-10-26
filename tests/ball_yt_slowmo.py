"""Arc search with an unknown time scale (slow-motion replays): gravity-ratio bands, a penalty for leaving the normal band. Same windows and context rules as ball_yt_sweep2."""
import pickle, sys, os, json, itertools, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import ball
d = pickle.load(open("work/ball_yt_cands_bg.pkl", "rb")); J = json.load(open("work/ball_judge/judged.json"))["yes"]; m = json.load(open("work/ball_judge/manifest.json"))
flight = {c["window"] for c in m if c["i"] in set(J["free"])}
BANDS = [(0.4, 2.0), (0.15, 0.4), (0.06, 0.15), (0.02, 0.06)]
CF = "work/ball_yt_slowmo.pkl"; R = pickle.load(open(CF, "rb")) if os.path.exists(CF) else {}
import time; t0 = time.time()
for tag, w in d.items():
    if tag in R: continue
    if time.time() - t0 > 80: print("budget used; rerun"); break
    B = np.array(w["boxes"]); ph = w["ph"]; cands = []
    for i, cs in enumerate(w["cands"]):
        b = B[min(i, len(B) - 1)]; h = b[3] - b[1]; cx = (b[0] + b[2]) / 2; keep = []
        for (x, y, p) in cs:
            inbox = b[0] - 0.1 * h <= x <= b[2] + 0.1 * h and b[1] <= y <= b[3] + 0.1 * h
            if inbox and (y > b[1] + 0.55 * h or abs(x - cx) < 0.22 * h and y > b[1] + 0.2 * h): continue
            keep.append((x, y, p))
        cands.append(keep)
    out = []
    for bi, band in enumerate(BANDS):
        tr = ball.link_soft(cands, w["times"], ph, min_frames=5, a_range=band, iters=4000)
        if tr is None: out.append(None); continue
        x0, y0 = tr["pts"][0]; b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; cx0 = (b0[0] + b0[2]) / 2
        start_ok = abs(x0 - cx0) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0
        mv = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph
        out.append(dict(score=tr["score"], n=tr["n"], travel=mv, apex=(w["top"] - tr["apex_y"]) / ph, dur=tr["t1"] - tr["t0"], start=bool(start_ok)))
    R[tag] = out; pickle.dump(R, open(CF, "wb")); print(tag, flush=True)
if len(R) == len(d):
    sv = {k: v for k, v in R.items() if "_serve" in k}; ct = {k: v for k, v in R.items() if "_control" in k}
    for pen, thr in itertools.product((0, 10, 20, 40), (20, 30)):
        def ok(out):
            best = 0
            for bi, v in enumerate(out):
                if v and v["travel"] >= 0.2 and v["apex"] >= 0.15 and v["dur"] >= 0.2 and v["start"]: best = max(best, v["score"] - pen * bi)
            return best >= thr
        a = [k for k, v in sv.items() if ok(v)]; f = [k for k, v in ct.items() if ok(v)]
        print(f"penalty/band {pen} score>={thr}: serves {len(a)}/15 (verified flight {len([k for k in a if k in flight])}), control false {len(f)}/21 {f}")
