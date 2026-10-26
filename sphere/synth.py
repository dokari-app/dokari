"""Synthetic movement generator, used ONLY to test the pipeline offline.

It produces stick-figure skeletons in the canonical format. It is not training data and
nothing about real movement is learned from it."""
import numpy as np
from .skeleton import JOINTS, J, make_clip

L_THIGH, L_SHIN, L_TORSO = 0.45, 0.43, 0.50
HIP_HALF, SH_HALF = 0.10, 0.19


def _two_link(ankle_zy, hip_zy):
    """Knee position (z, y) for a planar two-link leg, knee bending forward (+z)."""
    d = np.linalg.norm(hip_zy - ankle_zy)
    d = np.minimum(d, L_THIGH + L_SHIN - 1e-6)
    phi = np.arctan2(hip_zy[1] - ankle_zy[1], hip_zy[0] - ankle_zy[0])
    cos_a = (L_SHIN ** 2 + d ** 2 - L_THIGH ** 2) / (2 * L_SHIN * d)
    a = np.arccos(np.clip(cos_a, -1, 1))
    ang = phi - a
    return ankle_zy + L_SHIN * np.array([np.cos(ang), np.sin(ang)])


def _frame(depth, valgus=0.0, lean=0.0, arms=None, yaw=0.0):
    """One pose. depth in [0,1]: 0 standing, 1 deep. Returns (J,3) with x lateral, y up, z forward."""
    H = 0.86 - 0.40 * depth
    zh = -0.14 * depth
    P = np.zeros((len(JOINTS), 3))
    for side, sx in (("l", -1.0), ("r", 1.0)):
        ankle = np.array([sx * HIP_HALF, 0.0, 0.0])
        hip = np.array([sx * HIP_HALF, H, zh])
        kz, ky = _two_link(np.array([0.0, 0.0]), np.array([zh, H]))
        # valgus: knee collapses toward the midline with depth
        kx = sx * (HIP_HALF - valgus * depth)
        P[J[f"{side}_ankle"]] = ankle
        P[J[f"{side}_heel"]] = ankle + [0, 0, -0.05]
        P[J[f"{side}_toe"]] = ankle + [0, 0, 0.12]
        P[J[f"{side}_hip"]] = hip
        P[J[f"{side}_knee"]] = [kx, ky, kz]
        beta = np.radians(10 + 30 * depth + lean)
        sh = hip + [sx * (SH_HALF - HIP_HALF), L_TORSO * np.cos(beta), L_TORSO * np.sin(beta)]
        P[J[f"{side}_shoulder"]] = sh
        if arms is None:        # arms held in front for balance
            P[J[f"{side}_elbow"]] = sh + [0, -0.12, 0.20]
            P[J[f"{side}_wrist"]] = sh + [0, -0.05, 0.40]
        else:                   # arms raised out to the side by angle gamma (deg)
            g = np.radians(arms)
            P[J[f"{side}_elbow"]] = sh + [sx * 0.15 * np.sin(g), -0.15 * np.cos(g), 0]
            P[J[f"{side}_wrist"]] = sh + [sx * 0.30 * np.sin(g), -0.30 * np.cos(g), 0]
    mid = 0.5 * (P[J["l_shoulder"]] + P[J["r_shoulder"]])
    P[J["nose"]] = mid + [0, 0.22, 0.08]
    if yaw:
        c, s_ = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
        R = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
        P = P @ R.T
    return P


def squat_clip(reps=8, period=3.0, depth=1.0, valgus=0.0, fps=30, noise=0.004, yaw=40.0,
               seed=0, tag="good"):
    rng = np.random.default_rng(seed)
    T = int(reps * period * fps) + int(1.0 * fps)
    t = np.arange(T) / fps
    ph = np.clip((t - 0.5) / period, 0, reps)
    u = np.mod(ph, 1.0)                                   # standing pause at the top of each rep
    d = np.where(t < 0.5, 0.0, 0.5 - 0.5 * np.cos(2 * np.pi * np.minimum(u / 0.8, 1.0))) * depth
    d = np.where(ph >= reps, 0.0, d)
    frames = np.stack([_frame(float(x), valgus=valgus) for x in d], axis=0)
    # per-repetition natural variation in depth
    pose = frames + rng.normal(0, noise, frames.shape)
    pose += np.array([0.3, 0.0, 2.5])             # place the person away from the camera
    pose = _apply_yaw(pose, yaw)
    return make_clip(pose, np.full((T, len(JOINTS)), 0.95), fps,
                     {"source": "synthetic", "activity": "squat", "tag": tag, "id": f"syn_squat_{tag}_{seed}"})


def arm_raise_clip(reps=8, period=3.0, fps=30, noise=0.004, yaw=0.0, seed=0):
    rng = np.random.default_rng(seed)
    T = int(reps * period * fps) + int(1.0 * fps)
    t = np.arange(T) / fps
    ph = np.clip((t - 0.5) / period, 0, reps)
    u = np.mod(ph, 1.0)
    g = np.where(t < 0.5, 20.0, 20 + 70 * (0.5 - 0.5 * np.cos(2 * np.pi * np.minimum(u / 0.8, 1.0))))
    g = np.where(ph >= reps, 20.0, g)
    frames = np.stack([_frame(0.0, arms=float(x)) for x in g], axis=0)
    pose = frames + rng.normal(0, noise, frames.shape) + np.array([0.3, 0.0, 2.5])
    pose = _apply_yaw(pose, yaw)
    return make_clip(pose, np.full((T, len(JOINTS)), 0.95), fps,
                     {"source": "synthetic", "activity": "arm_raise", "id": f"syn_arm_{seed}"})


def _apply_yaw(pose, yaw):
    """Rotate about the vertical axis through the person, so the 'camera' sees them at an angle."""
    if not yaw:
        return pose
    c, s_ = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
    R = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    centre = np.array([0.3, 0.0, 2.5])
    return (pose - centre) @ R.T + centre
