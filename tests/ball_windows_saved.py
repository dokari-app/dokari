"""Turn the windows the factory saved (work/<activity>/ballwin/*.win.pkl, made with --ball-windows) into ball caches (imgs, boxes, times) in work/ball_s_<activity>/.
Adds the player boxes (YOLOX) and trims at camera cuts. Resumable.  python tests/ball_windows_saved.py work/tennis_serve [budget_s]"""
import glob, os, pickle, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball, ballwin
act = sys.argv[1].rstrip("/"); budget = float(sys.argv[2]) if len(sys.argv) > 2 else 80
out = f"work/ball_s_{os.path.basename(act).replace('tennis_', '')}"; os.makedirs(out, exist_ok=True); t0 = time.time(); det = None; n = 0
for f in sorted(glob.glob(f"{act}/ballwin/*.win.pkl")):
    tag = os.path.basename(f)[:-8]; o = f"{out}/{tag}.cache.pkl"
    if os.path.exists(o): continue
    if time.time() - t0 > budget: print("budget used; rerun"); break
    try:
        w = ballwin.load(f); imgs, times, tc = w["imgs"], w["times"], w["t_contact"]; det = det or ball.Detector(os.path.expanduser("~/models/yolox_m.onnx"))
        cuts = ball.shot_cuts(imgs); ic = int(np.argmin([abs(t - tc) for t in times])); lo = max([c for c in cuts if c <= ic], default=0); hi = min([c for c in cuts if c > ic], default=len(imgs))
        times, imgs = times[lo:hi], imgs[lo:hi]
        if len(imgs) < 12: open(o + ".skip", "w").write("short"); continue
        pb, prev = {}, None
        for i in range(0, len(imgs), 3):
            prev = ball.player_box(det.run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
        boxes = ball.steady_boxes(pb, len(imgs))
        if boxes is None: open(o + ".skip", "w").write("no player"); continue
        pickle.dump({"times": times, "boxes": boxes, "imgs": imgs, "t_contact": tc}, open(o, "wb")); n += 1; print(tag, flush=True)
    except Exception as e: print(tag, "failed", e)
print("windows this run:", n)
