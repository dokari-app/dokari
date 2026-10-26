"""How well does the automatic judge agree with the crops judged by hand? Runs sphere.balljudge on work/ball_judge/grid_*.png (25 calls) and compares with judged.json.
Needs ANTHROPIC_API_KEY in the Terminal window.  python tests/ball_judge_calibrate.py"""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import balljudge
J = json.load(open("work/ball_judge/judged.json"))["yes"]; hand = {i: k for k in ("free", "held", "static") for i in J[k]}; border = set(J["borderline"])
out = {}; tp = fp = fn = bd = 0
for g in sorted(glob.glob("work/ball_judge/grid_*.png")):
    r = balljudge.judge_grid(g); k = int(os.path.basename(g)[5:7]); tiles = range(k * 24, k * 24 + 24)
    if r is None: print(g, "no answer"); continue
    out.update(r)
    for i in tiles:
        a, b = i in r, i in hand
        if i in border: bd += a; continue
        tp += a and b; fp += a and not b; fn += b and not a
    print(g, "model:", sorted(r), flush=True)
json.dump({str(k): v for k, v in out.items()}, open("work/ball_judge/auto_judged.json", "w"))
print(f"\nagainst my judgements: agree on {tp} balls, model-only {fp}, mine-only {fn} (borderline tiles ignored: {len(border)}, model said yes to {bd})")
print(f"precision {tp / max(tp + fp, 1):.2f}  recall {tp / max(tp + fn, 1):.2f}")
