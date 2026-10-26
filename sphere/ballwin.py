"""Keep the ball-ready part of a video before the video is deleted.

The factory deletes each video after its skeleton is extracted (the disk would fill). The ball tracker needs the pictures around each shot,
so this saves, per shot found by the activity's entry, the frames from just before to just after contact as small JPEGs
(about 3-4 MB a window), with their times and the contact time. Player boxes are added later (needs a detector, not needed here).
Only OpenCV is used (the factory already decodes the video with it). Output: <activity dir>/ballwin/<video>_<n>.win.pkl
"""
import json, os, pickle
import numpy as np
import cv2
from .identify import identify
from .skeleton import J

PRE, POST, MAX_SIDE, QUALITY = 1.2, 0.4, 1280, 85
OVERHEAD = ("tennis_serve", "tennis_overhead_smash")


def contacts(shot, entry, clip):
    owned, _ = identify({shot: entry}, clip)
    P = clip["pose"]; fps = clip["fps"]; out = []
    for s, e in owned.get(shot, []):
        a, b = int(s * fps), min(int(e * fps) + 1, len(P))
        if b - a < 4:
            continue
        if shot in OVERHEAD:                                    # contact = the highest wrist (y is up)
            wr = np.nanmax(np.stack([P[a:b, J["l_wrist"], 1], P[a:b, J["r_wrist"], 1]]), axis=0)
            out.append((a + int(np.nanargmax(wr))) / fps)
        else:                                                   # contact = the fastest wrist moment
            best = None
            for k in ("l_wrist", "r_wrist"):
                v = np.nan_to_num(np.linalg.norm(np.diff(P[a:b, J[k]], axis=0), axis=1)) * fps
                if v.size and (best is None or v.max() > best[0]):
                    best = (v.max(), a + int(v.argmax()) + 1)
            if best:
                out.append(best[1] / fps)
    return out


def save(video_path, vid, clip, act_dir, max_per_video=3):
    """-> number of windows written. Silent no-op when the activity has no entry yet or is not a tennis shot."""
    shot = os.path.basename(os.path.normpath(act_dir))
    ep = os.path.join(act_dir, "entry.json")
    if not shot.startswith("tennis_") or not os.path.exists(ep):
        return 0
    cs = contacts(shot, json.load(open(ep)), clip)
    if not cs:
        return 0
    out_dir = os.path.join(act_dir, "ballwin"); os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path); fps = cap.get(cv2.CAP_PROP_FPS) or 30.0; n = 0
    for k, tc in enumerate(cs[:max_per_video]):
        path = os.path.join(out_dir, f"{vid}_{k}.win.pkl")
        if os.path.exists(path):
            continue
        f0 = max(0, int(round((tc - PRE) * fps))); f1 = int(round((tc + POST) * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0); jpgs, times = [], []
        for f in range(f0, f1):
            ok, im = cap.read()
            if not ok:
                break
            h, w = im.shape[:2]; s = min(1.0, MAX_SIDE / max(h, w))
            if s < 1.0:
                im = cv2.resize(im, (int(w * s) // 2 * 2, int(h * s) // 2 * 2), interpolation=cv2.INTER_AREA)
            jpgs.append(cv2.imencode(".jpg", im, [cv2.IMWRITE_JPEG_QUALITY, QUALITY])[1].tobytes()); times.append(f / fps)
        if len(jpgs) >= 12:
            pickle.dump({"jpgs": jpgs, "times": times, "t_contact": tc, "fps": fps, "shot": shot, "video": vid}, open(path, "wb")); n += 1
    cap.release()
    return n


def load(path):
    w = pickle.load(open(path, "rb"))
    w["imgs"] = [cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR) for b in w["jpgs"]]
    return w
