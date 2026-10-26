"""Canonical skeleton format used everywhere in the factory.

A clip is a dict:
  pose: float array (T, J, 3)  joint positions in metres, axes (x, y, z) with y = UP.
  vis:  float array (T, J)     per-joint visibility/confidence in [0, 1].
  fps:  float
  meta: dict (source, id, title, ...)
Joints are indexed by JOINTS below. No axis is assumed to be 'forward' or 'lateral':
the body frame is recovered from the skeleton itself (see features.py).
"""
import numpy as np

JOINTS = [
    "nose",
    "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist",
    "l_hip", "r_hip", "l_knee", "r_knee", "l_ankle", "r_ankle",
    "l_heel", "r_heel", "l_toe", "r_toe",
]
J = {name: i for i, name in enumerate(JOINTS)}

# MediaPipe BlazePose landmark indices for each canonical joint.
MEDIAPIPE_INDEX = {
    "nose": 0, "l_shoulder": 11, "r_shoulder": 12, "l_elbow": 13, "r_elbow": 14,
    "l_wrist": 15, "r_wrist": 16, "l_hip": 23, "r_hip": 24, "l_knee": 25, "r_knee": 26,
    "l_ankle": 27, "r_ankle": 28, "l_heel": 29, "r_heel": 30, "l_toe": 31, "r_toe": 32,
}


def make_clip(pose, vis, fps, meta=None):
    pose = np.asarray(pose, dtype=float)
    vis = np.asarray(vis, dtype=float)
    assert pose.ndim == 3 and pose.shape[1] == len(JOINTS) and pose.shape[2] == 3
    assert vis.shape == pose.shape[:2]
    return {"pose": pose, "vis": vis, "fps": float(fps), "meta": dict(meta or {})}


def save_clip(path, clip):
    import json
    np.savez_compressed(path, pose=clip["pose"], vis=clip["vis"], fps=clip["fps"],
                        meta=json.dumps(clip["meta"]))


def load_clip(path):
    import json
    d = np.load(path, allow_pickle=False)
    return make_clip(d["pose"], d["vis"], float(d["fps"]), json.loads(str(d["meta"])))
