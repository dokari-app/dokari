"""Nightly ball loop (steps are resumable, each stops after --budget seconds; rerun to continue).
  label : classifier (phone + composites + judged YouTube) -> weak candidates -> soft arc with player context -> confident tracks become
          pseudo-labels in work/ball_pseudo/<window>.npz (blob near the track = 1, other blobs of those frames = 0, other frames unlabelled)
  eval  : leave-one-video-out on the judged YouTube frames: base+judged (reference) vs base+judged+pseudo. Keeps a history in work/ball_loop_state.json.
Cache dirs (from ball_windows.py): work/ball_s_*/ ."""
import glob, json, os, pickle, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_dataset import examples
from ball_eval_comp import load
from ball_train import feats
from ball_yt_eval import fitw, sub
OUT = "work/ball_pseudo2"; STATE = "work/ball_loop_state.json"
vid = lambda s: s.split("_serve")[0].split("_control")[0].rsplit("_", 1)[0] if False else s.split(".")[0]

def base_data():
    real = load("work/ball_data"); comp = load("work/ball_comp")
    yt = {os.path.basename(f)[:-4]: dict(np.load(f)) for f in sorted(glob.glob("work/ball_yt/*.npz"))}
    return real, comp, yt

def accept(tr, w_ph, top, cands=None, times=None, boxes=None):
    if tr is None: return False
    if cands is not None:
        ps = []
        for fr in tr["frames"]:
            bx, by = np.polyval(tr["cx"], times[fr]), np.polyval(tr["cy"], times[fr]); near = [p for (x, y, p) in cands[fr] if np.hypot(x - bx, y - by) < max(4.0, 0.02 * w_ph)]
            ps.append(max(near) if near else 0.0)
        if float(np.mean(ps)) < 0.5: return False                       # the classifier itself must like the ball along the arc
        B = np.array(boxes); head = float(np.median(B[:, 1]))
        if (head - tr["apex_y"]) < 0.15 * w_ph: return False            # the arc must rise above the head
        b0 = B[min(tr["frames"][0], len(B) - 1)]; h0 = b0[3] - b0[1]; x0, y0 = tr["pts"][0]
        if not (abs(x0 - (b0[0] + b0[2]) / 2) < 0.6 * h0 + (b0[2] - b0[0]) / 2 and b0[1] - 0.3 * h0 <= y0 <= b0[1] + 0.8 * h0): return False   # starts near the player
    travel = float(np.hypot(np.ptp([q[0] for q in tr["pts"]]), np.ptp([q[1] for q in tr["pts"]]))) / w_ph
    return tr["score"] >= 30 and tr["n"] >= 8 and travel >= 0.3 and tr["t1"] - tr["t0"] >= 0.3

def context_filter(cs, b):
    h = b[3] - b[1]; cx = (b[0] + b[2]) / 2; keep = []
    for (x, y, p) in cs:
        inbox = b[0] - 0.1 * h <= x <= b[2] + 0.1 * h and b[1] <= y <= b[3] + 0.1 * h
        if inbox and (y > b[1] + 0.55 * h or abs(x - cx) < 0.22 * h and y > b[1] + 0.2 * h): continue
        keep.append((x, y, p))
    return keep

def label(budget):
    t0 = time.time(); os.makedirs(OUT, exist_ok=True); real, comp, yt = base_data(); rng = np.random.default_rng(0)
    X0 = np.concatenate([F for z, F in comp.values()] + [F for z, F in real.values()]); y0 = np.concatenate([z["y"] for z, F in comp.values()] + [z["y"] for z, F in real.values()])
    Xa, ya, wa = sub(X0, y0, np.ones(len(y0)), rng)
    Xy = np.concatenate([feats(z)[z["y"] >= 0] for z in yt.values()]); yy = np.concatenate([z["y"][z["y"] >= 0] for z in yt.values()])
    clf = fitw(np.concatenate([Xa, Xy]), np.concatenate([ya, yy]), np.concatenate([wa, np.where(yy == 1, 3.0, 1.0)]))
    log = json.load(open(OUT + "/_log.json")) if os.path.exists(OUT + "/_log.json") else {}
    for f in sorted(glob.glob("work/ball_s_*/*.cache.pkl")):
        tag = os.path.basename(f)[:-10]
        if tag in log: continue
        if time.time() - t0 > budget: print("budget used; rerun"); break
        try: w = pickle.load(open(f, "rb"))
        except Exception: log[tag] = "corrupt"; print(tag, "corrupt cache, skipped"); continue
        imgs, boxes, times = w["imgs"], w["boxes"], w["times"]; z = examples(imgs, boxes, {}, 0); H, W = imgs[0].shape[:2]
        if len(z["y"]) == 0: log[tag] = "noblobs"; continue
        p = clf.predict_proba(feats(z))[:, 1]; cands = [[] for _ in imgs]
        for k in np.where(p > 0.03)[0]: cands[int(z["frame"][k])].append((float(z["xy"][k][0] * W), float(z["xy"][k][1] * H), float(p[k])))
        cands = [context_filter(cs, boxes[min(i, len(boxes) - 1)]) for i, cs in enumerate(cands)]
        ph = float(z["ph"]); tr = ball.link_soft(cands, times, ph, min_frames=5)
        if not accept(tr, ph, 0, cands, times, boxes): log[tag] = "rejected" if tr else "none"; json.dump(log, open(OUT + "/_log.json", "w")); continue
        pts = dict(zip(tr["frames"], tr["pts"][:len(tr["frames"])])) if len(tr["pts"]) == len(tr["frames"]) else None
        ty = np.full(len(p), -1, np.int8); xy = z["xy"] * np.array([W, H], np.float32)
        for fr in tr["frames"]:
            m = z["frame"] == fr; ty[m] = 0
            bx, by = np.polyval(tr["cx"], times[fr]), np.polyval(tr["cy"], times[fr]); dd = np.hypot(xy[:, 0] - bx, xy[:, 1] - by)
            ty[m & (dd < max(4.0, 0.02 * ph))] = 1
        zz = dict(z); zz["y"] = ty; np.savez_compressed(f"{OUT}/{tag}.npz", **{k: np.asarray(v) for k, v in zz.items()})
        log[tag] = {"n": tr["n"], "score": round(tr["score"], 1), "pos": int((ty == 1).sum())}; json.dump(log, open(OUT + "/_log.json", "w")); print(tag, log[tag], flush=True)
    json.dump(log, open(OUT + "/_log.json", "w"))
    acc = [v for v in log.values() if isinstance(v, dict)]; print(f"windows {len(log)}, accepted {len(acc)}, pseudo positives {sum(v['pos'] for v in acc)}")

if __name__ == "__main__":
    if sys.argv[1] == "label": label(float(sys.argv[2]) if len(sys.argv) > 2 else 70)
