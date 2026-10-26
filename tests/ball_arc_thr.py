import sys
exec(open("tests/ball_arc_sweep.py").read().split("for name, kw in")[0])
rows = []
for t, (c, T, ph, B, cls) in D.items():
    tr = ball.link_soft(c, list(T), ph, tol=max(3.0, 0.012 * ph) * 3, min_frames=5)
    rows.append((cls, tr["score"] if tr else 0, toss(tr, B, ph, 0), t))
for thr in (20, 40, 60, 80, 100):
    r = {k: [sum(1 for x in rows if x[0] == k and x[2] and x[1] >= thr), sum(1 for x in rows if x[0] == k)] for k in ("moving", "none", "other")}
    print("score>=%d" % thr, r)
print("false alarms:", sorted([(round(x[1]), x[3][:14]) for x in rows if x[0] == "none" and x[2]], reverse=True))
