"""Background negatives: every blob of the windows in work/ball_s_*/ labelled 0 (one real ball per frame at most among hundreds of blobs: ~1% noise)
-> work/ball_bgneg/<window>.npz. Teaches the classifier foliage, fences, crowds, graphics. Resumable.  python tests/ball_bgneg.py [budget]"""
import glob, os, pickle, sys, time, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ball_dataset import examples
t0 = time.time(); B = float(sys.argv[1]) if len(sys.argv) > 1 else 80; os.makedirs("work/ball_bgneg", exist_ok=True)
for f in sorted(glob.glob("work/ball_s_*/*.cache.pkl")):
    tag = os.path.basename(f)[:-10]; o = f"work/ball_bgneg/{tag}.npz"
    if os.path.exists(o): continue
    if time.time() - t0 > B: print("budget used; rerun"); break
    try: w = pickle.load(open(f, "rb"))
    except Exception: continue
    z = examples(w["imgs"], w["boxes"], {}, 0)
    if len(z["y"]) == 0: continue
    z["y"] = np.zeros(len(z["y"]), np.int8); np.savez_compressed(o, **{k: np.asarray(v) for k, v in z.items()}); print(tag, len(z["y"]), flush=True)
print("files", len(glob.glob("work/ball_bgneg/*.npz")))
