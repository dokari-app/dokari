import sys; sys.argv = ["x"]
exec(open("tests/ball_arc_sweep.py").read().split("for name, kw in")[0])
for t, (c, T, ph, B, cls) in D.items():
    if cls != "moving": continue
    tr = ball.link_soft(c, list(T), ph, tol=max(3.0, 0.012 * ph) * 3, min_frames=5)
    if not tr: print(t[:14], "no arc"); continue
    x0, y0 = tr["pts"][0]; b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; cx0 = (b0[0] + b0[2]) / 2
    start = abs(x0 - cx0) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0
    travel = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / ph; apex = (float(np.median(B[:, 1])) - tr["apex_y"]) / ph
    print(t[:14], "score %.0f" % tr["score"], "n", tr["n"], "start", start, "travel %.2f apex %.2f dur %.2f" % (travel, apex, tr["t1"] - tr["t0"]))
