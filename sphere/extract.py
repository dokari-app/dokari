"""Factory stage 3: video -> canonical skeleton clip, using MediaPipe's pose landmarker.

Runs where the model file can be downloaded (needs internet on first use). Output uses the
canonical skeleton format (skeleton.py): metres, y up. Frames where no person is found are
kept with zero visibility."""
import json
import os
import urllib.request
import numpy as np
from .skeleton import JOINTS, MEDIAPIPE_INDEX, make_clip, save_clip

MODEL_URLS = {
    "lite": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
    "full": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task",
    "heavy": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task",
}


def ensure_model(variant="full", cache_dir=os.path.expanduser("~/.cache/sphere")):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"pose_landmarker_{variant}.task")
    if not os.path.exists(path):
        print(f"downloading pose model ({variant}) ...")
        urllib.request.urlretrieve(MODEL_URLS[variant], path)
    return path


def extract_video(video_path, meta=None, variant="full", target_fps=30.0):
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision

    opts = vision.PoseLandmarkerOptions(
        base_options=mpp.BaseOptions(model_asset_path=ensure_model(variant)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1,
        min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(video_path)
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, int(round(src_fps / target_fps)))
    fps = src_fps / step
    poses, viss, i = [], [], 0
    idx = [MEDIAPIPE_INDEX[j] for j in JOINTS]
    with vision.PoseLandmarker.create_from_options(opts) as lm:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(1000 * i / src_fps))
                if res.pose_world_landmarks:
                    w = res.pose_world_landmarks[0]
                    P = np.array([[w[k].x, -w[k].y, -w[k].z] for k in idx])   # image y points down: flip to y up
                    V = np.array([w[k].visibility for k in idx])
                else:
                    P, V = np.zeros((len(idx), 3)), np.zeros(len(idx))
                poses.append(P); viss.append(V)
            i += 1
    cap.release()
    if len(poses) < 10:
        return None
    pose, vis = np.stack(poses), np.stack(viss)
    detect_rate = float((vis.mean(1) > 0.4).mean())
    m = dict(meta or {}); m.update({"detect_rate": round(detect_rate, 3), "n_frames": int(len(poses))})
    clip = make_clip(pose, vis, fps, m)
    return clip if detect_rate >= 0.7 else None          # reject clips where the person is mostly not found


def _analyse(job):
    """One video, in its own process. Returns (video id, clip or None). Each video is analysed exactly as it would be alone."""
    path, meta, variant = job
    try:
        return meta["id"], extract_video(path, meta, variant)
    except Exception as e:                                     # a damaged video must not stop the others
        print(f"  could not read {os.path.basename(path)}: {str(e)[:80]}", flush=True)
        return meta["id"], False


def extract_folder(video_dir, clips_dir, sources=None, delete_video=False, variant="full", tag="unlabelled", workers=3, start_method="spawn", ball_windows=False):
    """Turn every video not yet done into a skeleton clip. `workers` videos are analysed at the same time (the result for
    each video does not depend on how many run together)."""
    os.makedirs(clips_dir, exist_ok=True)
    titles = {s["id"]: s for s in (sources or [])}
    rej_path = os.path.join(os.path.dirname(os.path.abspath(clips_dir)), "rejected.json")      # videos with no usable person are never analysed again
    try:
        rejected = set(json.load(open(rej_path)))
    except Exception:
        rejected = set()
    jobs, files = [], {}
    for fn in sorted(os.listdir(video_dir)):
        if not fn.lower().endswith((".mov", ".mp4", ".m4v", ".webm", ".mkv")) or ".coach." in fn:       # videos the coach wrote are not footage
            continue
        vid = os.path.splitext(fn)[0]
        if os.path.exists(os.path.join(clips_dir, f"{vid}.npz")) or vid in rejected:
            continue
        s = titles.get(vid, {})
        files[vid] = fn
        jobs.append((os.path.join(video_dir, fn), {"id": vid, "source": s.get("url", "local"), "title": s.get("title", ""), "tag": tag}, variant))
    n_ok = 0

    def done(vid, clip):
        nonlocal n_ok
        fn = files[vid]
        if clip is False:                                       # could not be read at all: try again another time, do not rule it out
            return
        if clip is None:
            print(f"  rejected {fn} (person not found often enough)", flush=True)
            rejected.add(vid); json.dump(sorted(rejected), open(rej_path, "w"))
            return
        save_clip(os.path.join(clips_dir, f"{vid}.npz"), clip); n_ok += 1
        print(f"  extracted {fn}: {clip['pose'].shape[0]} frames, detect rate {clip['meta']['detect_rate']}  ({n_ok} done, {len(jobs)} to do)", flush=True)
        if ball_windows:                                        # keep the pictures around each shot for the ball tracker before the video goes
            try:
                from . import ballwin
                k = ballwin.save(os.path.join(video_dir, fn), vid, clip, os.path.dirname(os.path.abspath(clips_dir)))
                if k:
                    print(f"    kept {k} ball window(s)", flush=True)
            except Exception as e:
                print(f"    (ball windows skipped: {str(e)[:80]})", flush=True)
        if delete_video:
            os.remove(os.path.join(video_dir, fn))

    if workers <= 1 or len(jobs) <= 1:
        for job in jobs:
            done(*_analyse(job))
    else:
        import concurrent.futures as cf
        import multiprocessing as mp
        with cf.ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context(start_method)) as ex:
            for fut in cf.as_completed([ex.submit(_analyse, j) for j in jobs]):
                done(*fut.result())
    return n_ok


class Tracker:
    """Frame-by-frame pose tracking for a live camera: image in, (joints (J, 3), visibility (J,)) out, in the canonical skeleton.
    This is the only place the live path touches MediaPipe; an on-phone tracker would be another class with the same call."""

    def __init__(self, variant="full"):
        import mediapipe as mp
        from mediapipe.tasks import python as mpp
        from mediapipe.tasks.python import vision
        self.mp = mp
        self.idx = [MEDIAPIPE_INDEX[j] for j in JOINTS]
        self.lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpp.BaseOptions(model_asset_path=ensure_model(variant)), running_mode=vision.RunningMode.VIDEO, num_poses=1,
            min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5, min_tracking_confidence=0.5))
        self.last_ms = -1

    def __call__(self, frame_bgr, t_seconds):
        import cv2
        ms = max(int(1000 * t_seconds), self.last_ms + 1)          # the tracker needs strictly increasing timestamps
        self.last_ms = ms
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.lm.detect_for_video(self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb), ms)
        if not res.pose_world_landmarks:
            return np.zeros((len(self.idx), 3)), np.zeros(len(self.idx))
        w = res.pose_world_landmarks[0]
        return np.array([[w[k].x, -w[k].y, -w[k].z] for k in self.idx]), np.array([w[k].visibility for k in self.idx])

    def close(self):
        self.lm.close()
