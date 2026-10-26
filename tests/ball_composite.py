"""Synthetic training/test examples: a real (sharp-footage) tennis ball, blurred and shrunk, pasted on a real YouTube window along a tossed arc, then the whole
window is re-encoded like video. Truth is exact; the clutter around it is real (neon shirts, strings, signs).
  python tests/ball_composite.py sprites --videos DIR --labels work/ball_labels     (cuts ball sprites from your sharp clips -> work/ball_sprites.npz)
  python tests/ball_composite.py make --bg work/ball_v7 --out work/ball_comp [--per-window 2] [--budget 140]"""
import argparse, glob, json, os, pickle, subprocess, sys, time
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_dataset import examples

SPR = 32          # sprites are stored with the ball 32 px wide


def cut_sprites(videos, labels, out, skip="IMG_2935_2_serve0,IMG_2935_2_serve1,IMG_2935_2_serve2,IMG_2935_2_serve3,IMG_2935_2_serve4"):
    sp_all = []
    for lf in sorted(glob.glob(os.path.join(labels, "*.json"))):
        tag = os.path.basename(lf)[:-5]; lab = json.load(open(lf))
        if tag in skip.split(",") or not lab.get("ok"):
            continue
        vid = tag.rsplit("_serve", 1)[0]; t0 = lab["times"][0]
        imgs = [f for _, f in ball.frames(os.path.join(videos, vid + ".mp4"), t0, lab["times"][-1] - t0 + 0.05, max_side=1920)]
        d = lab["ball_px"]
        for k, (nx, ny) in lab["pts"].items():
            i = int(k)
            if i >= len(imgs):
                continue
            H, W = imgs[i].shape[:2]; x, y = nx * W, ny * H; r = int(1.8 * d)
            x0, y0 = int(x - r), int(y - r)
            if x0 < 0 or y0 < 0 or x0 + 2 * r > W or y0 + 2 * r > H:
                continue
            p = imgs[i][y0:y0 + 2 * r, x0:x0 + 2 * r]
            hsv = cv2.cvtColor(p, cv2.COLOR_BGR2HSV)
            m = ((hsv[..., 0] >= 20) & (hsv[..., 0] <= 50) & (hsv[..., 1] > 60) & (hsv[..., 2] > 80)).astype(np.uint8)
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
            n, lab_, st, cen = cv2.connectedComponentsWithStats(m)
            if n < 2:
                continue
            j = 1 + int(np.argmin([np.hypot(cen[q][0] - r, cen[q][1] - r) for q in range(1, n)]))
            mm = (lab_ == j).astype(np.uint8)
            if st[j, cv2.CC_STAT_AREA] < 0.4 * np.pi * (d / 2) ** 2:
                continue
            mm = cv2.dilate(mm, np.ones((3, 3), np.uint8))
            alpha = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 1.2)
            sc = SPR / d
            sp = cv2.resize(p, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA); al = cv2.resize(alpha, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            cs = SPR * 1.8 * 2
            c = int(cs)
            sp = cv2.resize(sp, (c, c)); al = cv2.resize(al, (c, c))
            sprite = np.concatenate([sp, (al[..., None] * 255).astype(np.uint8)], 2)
            sp_all.append(sprite)
    np.savez_compressed(out, sprites=np.array(sp_all))
    print(len(sp_all), "sprites ->", out)



def recompress(frames, crf):
    h, w = frames[0].shape[:2]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", str(crf),
                            "-preset", "fast", "-pix_fmt", "yuv420p", "/tmp/_comp.mp4"], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for f in frames:
        enc.stdin.write(np.ascontiguousarray(f).tobytes())
    enc.stdin.close(); enc.wait()
    return [f for _, f in ball.frames("/tmp/_comp.mp4", 0.0, len(frames) / 30.0 + 0.2, max_side=max(w, h))][:len(frames)]


def paste(img, sprite, x, y, d, blur_len, ang):
    sc = d / SPR
    s = cv2.resize(sprite, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    if blur_len > 1.5:       # the ball is smeared along its path during the exposure
        k = int(blur_len) | 1
        ker = np.zeros((k, k), np.float32); cv2.line(ker, (0, k // 2), (k - 1, k // 2), 1.0, 1)
        M = cv2.getRotationMatrix2D((k / 2 - 0.5, k / 2 - 0.5), ang, 1.0); ker = cv2.warpAffine(ker, M, (k, k)); ker /= max(ker.sum(), 1e-6)
        s = cv2.filter2D(s, -1, ker)
    h, w = s.shape[:2]
    x0, y0 = int(round(x - w / 2)), int(round(y - h / 2))
    H, W = img.shape[:2]
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya:
        return
    sub = s[ya - y0:yb - y0, xa - x0:xb - x0]
    a = (sub[..., 3:4].astype(np.float32) / 255.0)
    img[ya:yb, xa:xb] = (img[ya:yb, xa:xb].astype(np.float32) * (1 - a) + sub[..., :3].astype(np.float32) * a).astype(np.uint8)


def composite(win, sprites, rng):
    imgs = [f.copy() for f in win["imgs"]]; times = np.asarray(win["times"]); boxes = win["boxes"]
    n = len(imgs); ph = float(np.median([b[3] - b[1] for b in boxes])); d = 0.035 * ph * rng.uniform(0.85, 1.2)
    t_rel = times - times[0]
    ta = rng.uniform(0.55, 0.8); t_rel0 = rng.uniform(0.0, max(0.0, t_rel[-1] - 2 * ta - 0.05)) if t_rel[-1] > 2 * ta + 0.05 else 0.0
    b0 = boxes[int(np.argmin(np.abs(t_rel - t_rel0)))]
    sx = (b0[0] + b0[2]) / 2 + rng.uniform(-0.25, 0.3) * ph; sy = b0[1] + rng.uniform(0.25, 0.5) * ph
    H_apex = rng.uniform(0.9, 1.6) * ph; vx = rng.uniform(-0.12, 0.12) * ph
    xy = {}
    for i, t in enumerate(t_rel):
        u = (t - t_rel0) / ta
        if u < 0 or u > 2.2:
            continue
        y = sy - H_apex * (1 - (u - 1) ** 2); x = sx + vx * (t - t_rel0)
        xy[i] = (x, y)
    ids = sorted(xy)
    for i in ids:
        j = min(i + 1, n - 1); jj = max(i - 1, 0)
        if j in xy and jj in xy:
            dx, dy = xy[j][0] - xy[jj][0], xy[j][1] - xy[jj][1]
        else:
            dx = dy = 0.0
        speed = np.hypot(dx, dy) / 2.0
        paste(imgs[i], sprites[rng.integers(len(sprites))], xy[i][0], xy[i][1], d, 0.6 * speed, float(np.degrees(np.arctan2(dy, dx))))
    imgs = recompress(imgs, int(rng.choice([26, 30, 34])))
    return imgs, {i: xy[i] for i in ids if 0 <= xy[i][0] < imgs[0].shape[1] and 0 <= xy[i][1] < imgs[0].shape[0]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sprites", "make"])
    ap.add_argument("--videos"); ap.add_argument("--labels", default="work/ball_labels"); ap.add_argument("--bg", default="work/ball_v7")
    ap.add_argument("--out", default="work/ball_comp"); ap.add_argument("--per-window", type=int, default=2); ap.add_argument("--budget", type=float, default=1e9)
    ap.add_argument("--sprites", default="work/ball_sprites.npz")
    a = ap.parse_args()
    if a.cmd == "sprites":
        cut_sprites(a.videos, a.labels, a.sprites); return
    sprites = np.load(a.sprites)["sprites"]; os.makedirs(a.out, exist_ok=True); t_start = time.time()
    for f in sorted(glob.glob(os.path.join(a.bg, "*.cache.pkl"))):
        tag = os.path.basename(f)[:-len(".cache.pkl")]
        for k in range(a.per_window):
            outp = os.path.join(a.out, f"{tag}_c{k}.npz")
            if os.path.exists(outp):
                continue
            if time.time() - t_start > a.budget:
                print("budget used; rerun to continue"); return
            win = pickle.load(open(f, "rb"))
            rng = np.random.default_rng(abs(hash((tag, k))) % (2 ** 31))
            imgs, xy = composite(win, sprites, rng)
            r = examples(imgs, win["boxes"], xy, len(xy))
            np.savez_compressed(outp, **r)
            hit = len(set(r["frame"][r["y"] == 1].tolist()))
            print(f"{tag}_c{k}: ball {r['ball_px']:.1f}px, {len(r['y'])} blobs, ball a candidate in {hit}/{len(xy)} frames", flush=True)


if __name__ == "__main__":
    main()
