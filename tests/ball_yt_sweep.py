import pickle, sys, os, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import ball
d = pickle.load(open("work/ball_yt_cands.pkl", "rb")); J = json.load(open("work/ball_judge/judged.json"))["yes"]; m = json.load(open("work/ball_judge/manifest.json"))
flight = {c["window"] for c in m if c["i"] in set(J["free"])}
res = {}
for tag, w in d.items():
    tr = ball.link_soft(w["cands"], w["times"], w["ph"], min_frames=5)
    if tr is None: res[tag] = None; continue
    ph = w["ph"]; mv = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph
    res[tag] = dict(score=tr["score"], n=tr["n"], travel=mv, apex=(w["top"] - tr["apex_y"]) / ph, dur=tr["t1"] - tr["t0"])
sv = {k: v for k, v in res.items() if "_serve" in k}; ct = {k: v for k, v in res.items() if "_control" in k}
for k, v in sv.items(): print(k, "flight" if k in flight else "", v and {a: round(b, 2) for a, b in v.items()})
for tr_ in (0.12, 0.2):
  for ap in (0.15, 0.3):
    for sc in (8, 12, 16, 20):
        f = lambda v: v and v["travel"] >= tr_ and v["apex"] >= ap and v["dur"] >= 0.2 and v["score"] >= sc
        print(f"travel>={tr_} apex>={ap} score>={sc}: serves {sum(bool(f(v)) for v in sv.values())}/15 (of flight {sum(bool(f(sv[k])) for k in flight if k in sv)}/{len([k for k in flight if k in sv])}), control false {sum(bool(f(v)) for v in ct.values())}/21")
