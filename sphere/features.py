"""Body-frame features: the registered, named, scale-free quantities that tests refer to.

Every feature is computed per frame in the body's own frame (not image axes) and is
normalised by a body scale, so it means the same thing for any person, from any camera
angle (to the extent the 3D pose is reliable). Features are the factory's 'signals'.

Sides are 'dom' (the more active arm's side in the clip) and 'non'. For symmetric
activities this assignment is arbitrary but consistent within a clip.
"""
import numpy as np
from .skeleton import J

EPS = 1e-9


def _unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, EPS)


def _angle(a, b, c):
    """Angle at b (degrees) between a-b and c-b."""
    u, v = _unit(a - b), _unit(c - b)
    return np.degrees(np.arccos(np.clip((u * v).sum(-1), -1, 1)))


def assign_dominance(pose):
    """'dom' side = the side whose wrist travels further. Returns ('l'|'r', other)."""
    lw, rw = pose[:, J["l_wrist"]], pose[:, J["r_wrist"]]
    pl = np.linalg.norm(np.diff(lw, axis=0), axis=1).sum()
    pr = np.linalg.norm(np.diff(rw, axis=0), axis=1).sum()
    return ("l", "r") if pl >= pr else ("r", "l")


def body_frame(pose):
    """Per-frame orthonormal frame: lateral (x), up (y), forward (z), origin at hip centre."""
    up = np.array([0.0, 1.0, 0.0])
    lh, rh = pose[:, J["l_hip"]], pose[:, J["r_hip"]]
    lat = rh - lh
    lat = lat - (lat @ up)[:, None] * up          # project onto the horizontal plane
    lat = _unit(lat)
    fwd = np.cross(lat, up)                        # candidate forward
    # fix the sign for the whole clip: toes point forward of heels
    toe = 0.5 * (pose[:, J["l_toe"]] + pose[:, J["r_toe"]])
    heel = 0.5 * (pose[:, J["l_heel"]] + pose[:, J["r_heel"]])
    sign = np.sign(np.median(((toe - heel) * fwd).sum(-1)))
    if sign == 0:
        sign = 1.0
    fwd = fwd * sign
    lat = np.cross(up, fwd)                        # keep right-handed after flip
    lat = lat * np.sign(np.median(((rh - lh) * lat).sum(-1)) or 1.0)
    return lat, np.broadcast_to(up, lat.shape), fwd


def to_body(pose):
    lat, up, fwd = body_frame(pose)
    origin = 0.5 * (pose[:, J["l_hip"]] + pose[:, J["r_hip"]])
    rel = pose - origin[:, None, :]
    return np.stack([(rel * lat[:, None, :]).sum(-1),
                     (rel * up[:, None, :]).sum(-1),
                     (rel * fwd[:, None, :]).sum(-1)], axis=-1)   # (T, J, [lat, up, fwd])


FEATURE_DOC = {}


def _reg(name, doc):
    FEATURE_DOC[name] = doc


for s in ("dom", "non"):
    _reg(f"angle.knee.{s}", "knee flexion angle in degrees (180 = straight)")
    _reg(f"angle.hip.{s}", "hip angle between trunk and thigh in degrees (180 = straight)")
    _reg(f"angle.ankle.{s}", "ankle angle between shin and foot in degrees")
    _reg(f"angle.elbow.{s}", "elbow angle in degrees (180 = straight)")
    _reg(f"angle.shoulder.{s}", "shoulder angle between trunk and upper arm in degrees (0 = arm along trunk)")
    _reg(f"height.knee.{s}", "knee height above ankle / torso length")
    _reg(f"height.wrist.{s}", "wrist height above shoulder / torso length (negative = below shoulder)")
    _reg(f"dev.knee_inward.{s}", "sideways deviation of the knee inward from the hip-ankle line / hip width (positive = knee collapsing inward)")
    _reg(f"fwd.knee_over_toe.{s}", "how far the knee is forward of the toe / torso length")
    _reg(f"reach.wrist.{s}", "wrist distance from shoulder / arm length-ish (torso length)")
_reg("angle.trunk_lean", "trunk angle from vertical in degrees")
_reg("angle.shin_lean", "mean shin angle from vertical in degrees")
_reg("height.hip", "hip centre height above ankle centre / torso length")
_reg("height.wrist_mid", "mean wrist height above shoulder centre / torso length")
_reg("dist.stance_width", "ankle separation / hip width")
_reg("dist.wrist_width", "wrist separation / shoulder width")
_reg("angle.shoulder_hip_twist", "rotation of the shoulder line relative to the hip line in degrees")
_reg("lat.com_shift", "lateral shift of the shoulder centre relative to the ankle centre / hip width")
_reg("fwd.trunk_shift", "forward shift of the shoulder centre relative to the ankle centre / torso length")
for s in ("dom", "non"):
    _reg(f"height.heel.{s}", "heel height above the toe / torso length (positive = heel raised off the floor)")
    _reg(f"rot.foot_turnout.{s}", "direction the foot points relative to the way the body faces, in degrees (0 = straight ahead, positive = toes turned outward)")

FEATURES = list(FEATURE_DOC.keys())


FLICKER_DEG = 30.0      # a frame this far from the middle value of its neighbours (0.1 s each side) is a tracker flicker, not movement
FLICKER_REL = 0.3       # same for positions and distances (in torso lengths, hip or shoulder widths)


def repair_flicker(F, names, fps):
    """Replace single-frame (or two-frame) tracker flicker by the middle value of the neighbouring frames. A real movement, however fast,
    goes one way and is kept: the middle value of a window on a ramp or a step is the value of its own centre. A joint the tracker loses
    for a moment near contact (the racket arm in a fast swing) otherwise makes the whole swing look unbelievable."""
    from scipy.ndimage import median_filter
    w = max(2, int(round(0.1 * fps)))
    out = F.copy()
    for j, n in enumerate(names):
        col = F[:, j]
        ok = ~np.isnan(col)
        if ok.sum() < 2 * w + 1:
            continue
        idx = np.arange(len(col))
        filled = np.interp(idx, idx[ok], col[ok])
        med = median_filter(filled, size=2 * w + 1, mode="nearest")
        thr = FLICKER_DEG if n.startswith(("angle.", "rot.")) else FLICKER_REL
        bad = ok & (np.abs(col - med) > thr)
        out[bad, j] = med[bad]
    return out


def compute_features(clip):
    """Return (names, F[T, D], info). NaN where joints are not visible enough."""
    pose = clip["pose"]
    vis = clip["vis"]
    T = pose.shape[0]
    dom, non = assign_dominance(pose)
    b = to_body(pose)                       # (T, J, 3) with [lat, up, fwd]
    P = lambda name: b[:, J[name]]
    sh_mid = 0.5 * (P("l_shoulder") + P("r_shoulder"))
    hip_mid = np.zeros_like(sh_mid)
    ank_mid = 0.5 * (P("l_ankle") + P("r_ankle"))
    torso = np.median(np.linalg.norm(sh_mid - hip_mid, axis=-1))
    hip_w = np.median(np.linalg.norm(P("l_hip") - P("r_hip"), axis=-1))
    sh_w = np.median(np.linalg.norm(P("l_shoulder") - P("r_shoulder"), axis=-1))
    torso, hip_w, sh_w = max(torso, EPS), max(hip_w, EPS), max(sh_w, EPS)

    out = {}
    for s, side in (("dom", dom), ("non", non)):
        sh, el, wr = P(f"{side}_shoulder"), P(f"{side}_elbow"), P(f"{side}_wrist")
        hp, kn, an, toe = P(f"{side}_hip"), P(f"{side}_knee"), P(f"{side}_ankle"), P(f"{side}_toe")
        out[f"angle.knee.{s}"] = _angle(hp, kn, an)
        out[f"angle.hip.{s}"] = _angle(sh, hp, kn)
        out[f"angle.ankle.{s}"] = _angle(kn, an, toe)
        out[f"angle.elbow.{s}"] = _angle(sh, el, wr)
        out[f"angle.shoulder.{s}"] = _angle(hp, sh, el)
        out[f"height.knee.{s}"] = (kn[:, 1] - an[:, 1]) / torso
        out[f"height.wrist.{s}"] = (wr[:, 1] - sh[:, 1]) / torso
        # inward deviation of knee from the hip-ankle line, in the lateral direction
        t = np.clip((kn[:, 1] - an[:, 1]) / np.where(np.abs(hp[:, 1] - an[:, 1]) < EPS, EPS, hp[:, 1] - an[:, 1]), 0, 1)
        line_lat = an[:, 0] + t * (hp[:, 0] - an[:, 0])
        side_sign = np.sign(np.median(hp[:, 0])) or 1.0     # +1 right hip, -1 left hip
        out[f"dev.knee_inward.{s}"] = side_sign * (line_lat - kn[:, 0]) / hip_w
        out[f"fwd.knee_over_toe.{s}"] = (kn[:, 2] - toe[:, 2]) / torso
        out[f"reach.wrist.{s}"] = np.linalg.norm(wr - sh, axis=-1) / torso
        heel = P(f"{side}_heel")
        out[f"height.heel.{s}"] = (heel[:, 1] - toe[:, 1]) / torso
        foot = toe - heel
        out[f"rot.foot_turnout.{s}"] = np.degrees(np.arctan2(side_sign * foot[:, 0], foot[:, 2]))
    # trunk and shin lean
    trunk = sh_mid - hip_mid
    out["angle.trunk_lean"] = np.degrees(np.arccos(np.clip(_unit(trunk)[:, 1], -1, 1)))
    shinl = P("l_knee") - P("l_ankle"); shinr = P("r_knee") - P("r_ankle")
    out["angle.shin_lean"] = 0.5 * (np.degrees(np.arccos(np.clip(_unit(shinl)[:, 1], -1, 1)))
                                    + np.degrees(np.arccos(np.clip(_unit(shinr)[:, 1], -1, 1))))
    out["height.hip"] = (hip_mid[:, 1] - ank_mid[:, 1]) / torso
    out["height.wrist_mid"] = (0.5 * (P("l_wrist")[:, 1] + P("r_wrist")[:, 1]) - sh_mid[:, 1]) / torso
    out["dist.stance_width"] = np.linalg.norm(P("l_ankle") - P("r_ankle"), axis=-1) / hip_w
    out["dist.wrist_width"] = np.linalg.norm(P("l_wrist") - P("r_wrist"), axis=-1) / sh_w
    sl = P("r_shoulder") - P("l_shoulder"); hl = P("r_hip") - P("l_hip")
    ang_s = np.arctan2(sl[:, 2], sl[:, 0]); ang_h = np.arctan2(hl[:, 2], hl[:, 0])
    out["angle.shoulder_hip_twist"] = np.degrees(np.angle(np.exp(1j * (ang_s - ang_h))))
    out["lat.com_shift"] = (sh_mid[:, 0] - ank_mid[:, 0]) / hip_w
    out["fwd.trunk_shift"] = (sh_mid[:, 2] - ank_mid[:, 2]) / torso

    names = FEATURES
    F = np.stack([out[n] for n in names], axis=1)
    # mask frames where the joints involved are poorly visible (coarse: mean visibility)
    low = vis.mean(axis=1) < 0.4
    F[low] = np.nan
    F = repair_flicker(F, names, float(clip.get("fps", 30.0)))
    info = {"dominant_side": dom, "torso_length": float(torso), "hip_width": float(hip_w),
            "view_yaw_deg": float(_view_yaw(pose))}
    return names, F, info


def _view_yaw(pose):
    """Camera-relative facing direction estimate: yaw of the hip line in the camera's x-z plane.
    0 deg = learner faces the camera or faces away; 90 deg = side-on. Depends on the source's
    axes being camera-aligned (true for MediaPipe world landmarks)."""
    hl = pose[:, J["r_hip"]] - pose[:, J["l_hip"]]
    ang = np.degrees(np.arctan2(np.abs(hl[:, 2]), np.abs(hl[:, 0])))
    return float(np.nanmedian(ang))


def feature_measure(name):
    """Which measurement (M-id) a feature belongs to."""
    p = name.split(".")[0]
    return {"angle": "M02", "height": "M01", "dev": "M01", "fwd": "M01", "lat": "M01",
            "reach": "M03", "dist": "M03", "rot": "M02"}[p]
