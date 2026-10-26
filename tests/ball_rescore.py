"""Score every cached window again (no detection, seconds): python tests/ball_rescore.py work/ball_v5 [--details]"""
import glob, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import ball_bench as bb

d0 = sys.argv[1]; det = "--details" in sys.argv
rows = []
for f in sorted(glob.glob(os.path.join(d0, "*.cache.pkl"))):
    tag = os.path.basename(f)[:-len(".cache.pkl")]
    r, tr = bb.score_window(pickle.load(open(f, "rb")), 0)
    rows.append((tag, "serve" if "_serve" in tag else "control", r))
    if det:
        print(f"{tag:28s}", "  ".join(f"{m}:{'TOSS' if x['toss_found'] else '-'}({x['above_head_frames']}/{x['frames']})" for m, x in r["methods"].items()))
print("\nmethod      serves with toss found   control with false toss   share of frames with a ball above the head: serves / controls")
for m in ("det_tiled", "motion", "all"):
    s = [r for t, k, r in rows if k == "serve"]; c = [r for t, k, r in rows if k == "control"]
    sh = lambda L: np.mean([r["methods"][m]["above_head_frames"] / r["methods"][m]["frames"] for r in L]) if L else 0
    print(f"{m:10s}  {sum(r['methods'][m]['toss_found'] for r in s)}/{len(s)}                      {sum(r['methods'][m]['toss_found'] for r in c)}/{len(c)}                       {sh(s):.2f} / {sh(c):.2f}")
