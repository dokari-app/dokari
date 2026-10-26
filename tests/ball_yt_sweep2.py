"""Soft arc + player context. Candidates inside the player's box are dropped when they are low (shoes/legs) or in the torso; the arc must start near the player
(first point within the box width +-0.6 ph horizontally, from 0.3 ph above the head to the waist) and rise above the head."""
import pickle, sys, os, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import ball
d = pickle.load(open("work/ball_yt_cands.pkl", "rb")); J = json.load(open("work/ball_judge/judged.json"))["yes"]; m = json.load(open("work/ball_judge/manifest.json"))
flight = {c["window"] for c in m if c["i"] in set(J["free"])}
def run(ctx_filter, start_rule):
    res = {}
    for tag, w in d.items():
        B = np.array(w["boxes"]); ph = w["ph"]; cands = []
        for i, cs in enumerate(w["cands"]):
            b = B[min(i, len(B) - 1)]; h = b[3] - b[1]; cx = (b[0] + b[2]) / 2; keep = []
            for (x, y, p) in cs:
                inbox = b[0] - 0.1 * h <= x <= b[2] + 0.1 * h and b[1] <= y <= b[3] + 0.1 * h
                if ctx_filter and inbox and (y > b[1] + 0.55 * h or abs(x - cx) < 0.22 * h and y > b[1] + 0.2 * h): continue
                keep.append((x, y, p))
            cands.append(keep)
        tr = ball.link_soft(cands, w["times"], ph, min_frames=5)
        if tr is None: res[tag] = None; continue
        x0, y0 = tr["pts"][0]; b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; cx0 = (b0[0] + b0[2]) / 2
        start_ok = abs(x0 - cx0) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0
        mv = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph
        res[tag] = dict(score=tr["score"], travel=mv, apex=(w["top"] - tr["apex_y"]) / ph, dur=tr["t1"] - tr["t0"], start=start_ok)
    return res
for cf in (False, True):
    res = run(cf, True); sv = {k: v for k, v in res.items() if "_serve" in k}; ct = {k: v for k, v in res.items() if "_control" in k}
    for sr in (False, True):
        for sc in (10, 20, 30):
            f = lambda v: v and v["travel"] >= 0.2 and v["apex"] >= 0.15 and v["dur"] >= 0.2 and v["score"] >= sc and (v["start"] or not sr)
            print(f"ctx_filter={cf} start_rule={sr} score>={sc}: serves {sum(bool(f(v)) for v in sv.values())}/15, control false {sum(bool(f(v)) for v in ct.values())}/21  false in: {[k for k,v in ct.items() if f(v)]}")
res = run(True, True)
acc = [k for k, v in res.items() if "_serve" in k and v and v["travel"] >= 0.2 and v["apex"] >= 0.15 and v["dur"] >= 0.2 and v["score"] >= 20 and v["start"]]
print("accepted", acc); print("accepted with verified flight ball", [k for k in acc if k in flight], "| verified-flight windows missed", [k for k in flight if k not in acc]); print("accepted without verified ball", [k for k in acc if k not in flight])
