"""Light window cache for self-training: for each video, find the shots with the shot's entry (identify), take the frames around the contact,
find the player (YOLOX, every 3rd frame) and save imgs/boxes/times (no ball detector). Resumable: reruns skip finished windows.
  python tests/ball_windows.py --shot tennis_forehand --videos work/tennis_forehand/videos --skeletons work/tennis_forehand/clips --entry work/tennis_forehand/entry.json --out work/ball_s_forehand --budget 80"""
import argparse, glob, json, os, pickle, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from sphere.identify import identify
from sphere.skeleton import load_clip, J

def contacts(shot, entry, skel):
    clip = load_clip(skel); owned, _ = identify({shot: entry}, clip); P = clip["pose"]; fps = clip["fps"]; out = []
    for s, e in owned[shot]:
        a, b = int(s * fps), min(int(e * fps) + 1, len(P))
        if b - a < 4: continue
        if shot in ("tennis_serve", "tennis_overhead_smash"):
            wr = np.nanmax(np.stack([P[a:b, J["l_wrist"], 1], P[a:b, J["r_wrist"], 1]]), axis=0); out.append((a + int(np.nanargmax(wr))) / fps)
        else:
            best = None
            for k in ("l_wrist", "r_wrist"):
                v = np.nan_to_num(np.linalg.norm(np.diff(P[a:b, J[k]], axis=0), axis=1)) * fps
                if v.size and (best is None or v.max() > best[0]): best = (v.max(), a + int(v.argmax()) + 1)
            out.append(best[1] / fps)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", required=True); ap.add_argument("--videos", required=True); ap.add_argument("--skeletons", required=True); ap.add_argument("--entry", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--max-per-video", type=int, default=2); ap.add_argument("--budget", type=float, default=80)
    ap.add_argument("--pre", type=float, default=1.2); ap.add_argument("--post", type=float, default=0.4); ap.add_argument("--pmodel", default=os.path.expanduser("~/models/yolox_m.onnx"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time(); det = None
    entry = json.load(open(a.entry)); n = 0
    for sk in sorted(glob.glob(os.path.join(a.skeletons, "*.npz"))):
        vid = os.path.basename(sk)[:-4]; done = os.path.join(a.out, vid + ".done")
        if os.path.exists(done): continue
        if time.time() - t0 > a.budget: print("budget used; rerun to continue"); return
        vp = [p for p in glob.glob(os.path.join(a.videos, vid + ".*")) if not p.endswith(".part")]
        if not vp: open(done, "w").write("novideo"); continue
        try: cs = contacts(a.shot, entry, sk)
        except Exception as ex: print(vid, "identify failed", ex); open(done, "w").write("fail"); continue
        det = det or ball.Detector(a.pmodel); kept = 0
        for k, tc in enumerate(cs[:a.max_per_video]):
            try:
                fr = list(ball.frames(vp[0], max(0.0, tc - a.pre), a.pre + a.post))
                if len(fr) < 12: continue
                times = [t for t, _ in fr]; imgs = [f for _, f in fr]; cuts = ball.shot_cuts(imgs)
                ic = int(np.argmin([abs(t - tc) for t in times])); lo = max([c for c in cuts if c <= ic], default=0); hi = min([c for c in cuts if c > ic], default=len(imgs))
                times, imgs = times[lo:hi], imgs[lo:hi]
                if len(imgs) < 12: continue
                pb, prev = {}, None
                for i in range(0, len(imgs), 3):
                    prev = ball.player_box(det.run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
                boxes = ball.steady_boxes(pb, len(imgs))
                if boxes is None: continue
                pickle.dump({"times": times, "boxes": boxes, "imgs": imgs, "t_contact": tc}, open(os.path.join(a.out, f"{vid}_{a.shot.split('_')[1]}{k}.cache.pkl"), "wb")); kept += 1; n += 1
            except Exception as ex: print(vid, "window failed", ex)
        open(done, "w").write(str(kept)); print(vid, "windows", kept, f"{time.time()-t0:.0f}s", flush=True)
    print("all done;", n, "windows this run")
main()
