"""Training data for a learned ball-vs-clutter classifier, built from the sharp-footage labels (tests/ball_label_his.py).
Each labelled window is re-encoded at YouTube-like quality (smaller, h264) and every small moving blob in it becomes one example:
positive when it lies on the labelled ball, negative otherwise (shirts, strings, leaves, shoes: the false tracks we met). Rerun to continue (budgeted).
  python tests/ball_dataset.py --videos DIR --labels work/ball_labels --out work/ball_data [--budget 140]"""
import argparse, glob, json, os, subprocess, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import ball

VARIANTS = [(1280, 28), (960, 32), (720, 34)]      # longer side in pixels, h264 crf
PATCH = 24


def encode(src, t0, dur, long_side, crf, out):
    w, h = ball.display_size(src)
    k = min(1.0, long_side / max(w, h)); ow, oh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", src, "-t", f"{dur:.3f}", "-vf", f"scale={ow}:{oh}", "-an",
                    "-c:v", "libx264", "-crf", str(crf), "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True, stderr=subprocess.DEVNULL)


def patch(img, x, y, r):
    H, W = img.shape[:2]
    x0, y0 = int(round(x - r)), int(round(y - r)); s = int(2 * r)
    pad = np.zeros((s, s, 3), np.uint8)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + s, W), min(y0 + s, H)
    if xb > xa and yb > ya:
        pad[ya - y0:yb - y0, xa - x0:xb - x0] = img[ya:yb, xa:xb]
    return cv2.resize(pad, (PATCH, PATCH), interpolation=cv2.INTER_AREA)


def build(pdet, src, lab, long_side, crf, tmp):
    t0 = lab["times"][0]; dur = lab["times"][-1] - t0 + 0.1
    encode(src, t0, dur, long_side, crf, tmp)
    imgs = [f for _, f in ball.frames(tmp, 0.0, dur, max_side=long_side)]
    n = min(len(imgs), len(lab["times"]))
    H, W = imgs[0].shape[:2]
    pb, prev = {}, None
    for i in range(0, n, 4):
        prev = ball.player_box(pdet.run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
    boxes = ball.steady_boxes(pb, n)
    return examples(imgs[:n], boxes, {i: (p[0] * W, p[1] * H) for i, p in ((int(k), v) for k, v in lab["pts"].items())}, len(lab["pts"]))


def examples(imgs, boxes, ball_xy, n_labelled):
    """One example per small moving blob of every frame. ball_xy: {frame: (x, y) pixels} of the true ball (positive = a blob within ~a ball width of it)."""
    n = len(imgs); H, W = imgs[0].shape[:2]
    ph = float(np.median([b[3] - b[1] for b in boxes])); d = 0.035 * ph
    X, S, Y, G, F = [], [], [], [], []
    for i in range(1, n - 1):
        roi = ball.roi_of(boxes[i], W, H, up=3.2, side=1.6)
        amin, amax = max(2, 0.12 * np.pi * (d / 2) ** 2), 6 * np.pi * (d / 2) ** 2
        bl = ball.union_blobs(ball.motion_blobs(imgs[i - 1], imgs[i], imgs[i + 1], roi, min_area=amin, max_area=amax), ball.colour_blobs(imgs[i], roi, amin, amax))
        lx, ly = ball_xy.get(i, (None, None))
        b = boxes[i]; cx = (b[0] + b[2]) / 2
        for (x, y, a) in bl[:260]:
            r = max(8.0, 2.0 * d)
            pa = [patch(imgs[i - 1], x, y, r), patch(imgs[i], x, y, r), patch(imgs[i + 1], x, y, r)]
            gray = [cv2.cvtColor(p, cv2.COLOR_BGR2GRAY) for p in pa]
            hsv = cv2.cvtColor(pa[1], cv2.COLOR_BGR2HSV)
            c = hsv[PATCH // 2 - 2:PATCH // 2 + 2, PATCH // 2 - 2:PATCH // 2 + 2]
            X.append(np.concatenate([g.ravel() for g in gray] + [hsv[..., 0].ravel(), hsv[..., 1].ravel()]).astype(np.uint8))
            S.append([a / (np.pi * (d / 2) ** 2), (y - b[1]) / ph, (x - cx) / ph, float(c[..., 0].mean()), float(c[..., 1].mean()), float(c[..., 2].mean())])
            Y.append(int(lx is not None and np.hypot(x - lx, y - ly) < 0.8 * d + 2))
            G.append(i); F.append((x / W, y / H))
    return {"X": np.array(X), "S": np.array(S, np.float32), "y": np.array(Y), "frame": np.array(G), "xy": np.array(F, np.float32), "ball_px": d, "ph": ph,
            "n_labelled": n_labelled}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True); ap.add_argument("--labels", default="work/ball_labels"); ap.add_argument("--out", default="work/ball_data")
    ap.add_argument("--budget", type=float, default=1e9); ap.add_argument("--pmodel", default=os.path.expanduser("~/models/yolox_m.onnx"))
    ap.add_argument("--skip", default="IMG_2935_2_serve0,IMG_2935_2_serve1,IMG_2935_2_serve2,IMG_2935_2_serve3,IMG_2935_2_serve4", help="windows that repeat another clip")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    import time; t_start = time.time()
    pdet = ball.Detector(a.pmodel); skip = set(a.skip.split(","))
    for lf in sorted(glob.glob(os.path.join(a.labels, "*.json"))):
        tag = os.path.basename(lf)[:-5]; lab = json.load(open(lf))
        if tag in skip or not lab.get("ok"):
            continue
        vid = tag.rsplit("_serve", 1)[0]
        for (L, crf) in VARIANTS:
            outp = os.path.join(a.out, f"{tag}_{L}_{crf}.npz")
            if os.path.exists(outp):
                continue
            if time.time() - t_start > a.budget:
                print("budget used; rerun to continue"); return
            r = build(pdet, os.path.join(a.videos, vid + ".mp4"), lab, L, crf, os.path.join(a.out, "_tmp.mp4"))
            np.savez_compressed(outp, **r)
            pos = int(r["y"].sum()); frames_with = len(set(r["frame"][r["y"] == 1].tolist()))
            print(f"{tag} {L}px crf{crf}: ball {r['ball_px']:.1f}px, {len(r['y'])} blobs, {pos} on the ball, ball covered in {frames_with}/{r['n_labelled']} labelled frames", flush=True)


if __name__ == "__main__":
    main()
