"""Ball labels from sharp footage (your phone clips): find the ball in each serve window at 1080x1920, where it is ~15 px, using only colour,
motion and the ballistic arc (no learned detector), and write its position per frame (normalised 0..1, so it carries over to any resolution).
  python tests/ball_label_his.py --videos DIR --skeletons DIR --out work/ball_labels [--clips IMG_2935_3,IMG_2935_2]
Writes per window: <tag>.json (times, ball x/y per frame or null, track stats) and <tag>_sheet.png (crops around the ball for you to check)."""
import argparse, glob, json, os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sphere import ball
from ball_bench import serve_windows


def label_window(pdet, video, t_contact, pre=1.6, post=0.4, max_side=1920):
    imgs, times = [], []
    for t, f in ball.frames(video, max(0.0, t_contact - pre), pre + post, max_side=max_side):
        times.append(t); imgs.append(f)
    if len(imgs) < 20:
        return None
    H, W = imgs[0].shape[:2]
    pb, prev = {}, None
    for i in range(0, len(imgs), 4):
        prev = ball.player_box(pdet.run(imgs[i], conf=0.2, classes=(ball.PERSON,)), prev); pb[i] = prev
    boxes = ball.steady_boxes(pb, len(imgs))
    if boxes is None:
        return None
    ph = float(np.median([b[3] - b[1] for b in boxes]))
    rois = [ball.roi_of(b, W, H, up=3.2, side=1.6) for b in boxes]
    ball_d = 0.035 * ph                                       # expected ball diameter, pixels
    amin, amax = 0.25 * np.pi * (0.5 * ball_d) ** 2, 4.0 * np.pi * (0.5 * ball_d) ** 2
    cands = [[] for _ in imgs]
    for i in range(1, len(imgs) - 1):
        cands[i] = [(x, y, a) for x, y, a in ball.motion_candidates(imgs[i - 1], imgs[i], imgs[i + 1], rois[i], max_area=amax, bright=False, min_area=amin)]
    tol = max(4.0, 0.9 * ball_d)
    tr = ball.link(cands, times, min_inliers=7, tol=tol)
    if tr is None:
        return {"ok": False, "reason": "no arc", "ph": ph, "cands_per_frame": float(np.mean([len(c) for c in cands]))}
    fr, add = ball.extend_track(tr, cands, times, tol)
    pts = {}
    for (x, y), i in zip(tr["pts"][:len(tr["frames"])], tr["frames"]):
        pts[i] = (x, y)
    for i, x, y in add:
        pts[i] = (x, y)
    top = float(np.median([b[1] for b in boxes]))
    travel = float(np.hypot(np.ptp([p[0] for p in pts.values()]), np.ptp([p[1] for p in pts.values()])))
    ok = tr["apex_y"] < top - 0.15 * ph and travel >= 0.5 * ph and len(pts) >= 10
    return {"ok": bool(ok), "ph": ph, "W": W, "H": H, "times": times, "t_contact": t_contact, "n_track": len(pts), "travel_ph": travel / ph,
            "ball_px": ball_d, "pts": {int(i): [float(x) / W, float(y) / H] for i, (x, y) in pts.items()}, "imgs": imgs}


def sheet(res, path, n=10):
    idx = sorted(res["pts"].keys()); idx = [idx[int(k)] for k in np.linspace(0, len(idx) - 1, min(n, len(idx)))]
    r = int(max(40, 2.2 * res["ball_px"])); tiles = []
    for i in idx:
        x, y = res["pts"][i][0] * res["W"], res["pts"][i][1] * res["H"]
        x0, y0 = int(min(max(x - r, 0), res["W"] - 2 * r)), int(min(max(y - r, 0), res["H"] - 2 * r))
        c = res["imgs"][i][y0:y0 + 2 * r, x0:x0 + 2 * r].copy()
        cv2.circle(c, (int(x - x0), int(y - y0)), int(res["ball_px"] * 0.9), (0, 0, 255), 1)
        tiles.append(cv2.resize(c, (160, 160)))
    rows = [np.hstack(tiles[k:k + 5]) for k in range(0, len(tiles) - len(tiles) % 5, 5)]
    if rows:
        cv2.imwrite(path, np.vstack(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", required=True); ap.add_argument("--skeletons", required=True)
    ap.add_argument("--entry", default="work/tennis_serve/entry.json"); ap.add_argument("--out", default="work/ball_labels")
    ap.add_argument("--clips", default=None); ap.add_argument("--pmodel", default=os.path.expanduser("~/models/yolox_m.onnx"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    entry = json.load(open(a.entry)); pdet = ball.Detector(a.pmodel)
    ids = a.clips.split(",") if a.clips else [os.path.basename(p)[:-4] for p in sorted(glob.glob(os.path.join(a.videos, "*.mp4")))]
    for vid in ids:
        wins, dur = serve_windows(entry, os.path.join(a.skeletons, vid + ".npz"))
        for k, (s, e, tc) in enumerate(wins):
            tag = f"{vid}_serve{k}"
            if os.path.exists(os.path.join(a.out, tag + ".json")):
                continue
            r = label_window(pdet, os.path.join(a.videos, vid + ".mp4"), tc)
            if r is None:
                print(tag, "skipped"); continue
            if r["ok"]:
                sheet(r, os.path.join(a.out, tag + "_sheet.png"))
            out = {k_: v for k_, v in r.items() if k_ != "imgs"}
            json.dump(out, open(os.path.join(a.out, tag + ".json"), "w"))
            print(tag, f"t={tc:.1f}", "OK" if r["ok"] else "no", {k_: (round(v, 2) if isinstance(v, float) else v) for k_, v in out.items() if k_ in ("n_track", "travel_ph", "ball_px", "ph", "reason", "cands_per_frame")}, flush=True)


if __name__ == "__main__":
    main()
