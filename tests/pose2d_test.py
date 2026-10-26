"""Free test on the 150 pilot windows: does the IMAGE-plane pose (not the estimated-depth world pose) separate forehand from backhand?
Rule: racket hand taken from the frames; at contact, is the racket-hand wrist on the far side of the body midline (backhand) or on its own side (forehand)?
  python tests/pose2d_test.py        (Mac, mediapipe, no API key, no cost)"""
import json, os, sys, collections
import numpy as np, cv2
sys.path.insert(0, ".")
from sphere import labelling, extract
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

d = json.load(open("work/stroke_contact_pilot.json")); lab = json.load(open("work/stroke_labels2.json"))
model = extract.ensure_model("full")
lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_poses=3))
LS, RS, LW, RW = 11, 12, 15, 16
OFFS = [-0.2, -0.1, 0.0, 0.1, 0.2]


def pick(res):
    best, bh = None, 0
    for i, p in enumerate(res.pose_landmarks):
        ys = [q.y for q in p]; h = max(ys) - min(ys)
        if h > bh:
            best, bh = i, h
    return best


rows = []
for k, v in d.items():
    if v["contact_frame"] == 0 or v["stroke"] not in ("forehand", "backhand") or v["swinging_hand"] not in ("player_right", "player_left"):
        continue
    act, vid = k.split("/")[:2]
    vf = labelling.video_file(f"work/{act}/videos", vid)
    w0, w1 = lab[k]["window"]; tc = w0 + (w1 - w0) * ((v["contact_frame"] - 1) / 7)
    cap = cv2.VideoCapture(vf); sv = "r" if v["swinging_hand"] == "player_right" else "l"
    vals = []
    for o in OFFS:
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0, tc + o)); ok, fr = cap.read()
        if not ok: vals.append(None); continue
        res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
        i = pick(res)
        if i is None: vals.append(None); continue
        p = res.pose_landmarks[i]; W, H = fr.shape[1], fr.shape[0]
        xy = lambda j: np.array([p[j].x * W, p[j].y * H])
        own, opp = (xy(RS), xy(LS)) if sv == "r" else (xy(LS), xy(RS))
        wr = xy(RW) if sv == "r" else xy(LW)
        sw = abs(opp[0] - own[0]); torso = np.linalg.norm((xy(LS) + xy(RS)) / 2 - (xy(11 + 12) if False else (xy(23) + xy(24)) / 2))
        sgn = np.sign(opp[0] - own[0]) or 1.0
        vals.append(dict(cross=float((wr[0] - (own[0] + opp[0]) / 2) * sgn / max(sw, 1e-6)), sw=float(sw / max(torso, 1e-6))))
    rows.append(dict(y=int(v["stroke"] == "backhand"), vals=vals, two=v["other_hand_on_racket"], conf=v["confidence"]))
print("windows", len(rows), "with a detected person at contact", sum(1 for r in rows if r["vals"][2]))


def auc(p, n):
    p, n = np.array(p), np.array(n)
    return float(((p[:, None] > n[None, :]).mean() + .5 * (p[:, None] == n[None, :]).mean())) if len(p) and len(n) else float("nan")


def rep(name, sel, f):
    sel = [(r["y"], f(r)) for r in sel]; sel = [(y, c) for y, c in sel if c is not None]
    y = np.array([a for a, _ in sel]); c = np.array([b for _, b in sel])
    if y.sum() < 3 or (1 - y).sum() < 3: print(name, "few", len(sel)); return
    print(name, "n", len(sel), "bh", int(y.sum()), "AUC", round(auc(c[y == 1], c[y == 0]), 3), "median fh/bh", round(float(np.median(c[y == 0])), 2), round(float(np.median(c[y == 1])), 2))


at = lambda r: r["vals"][2]["cross"] if r["vals"][2] else None
mx = lambda r: max([x["cross"] for x in r["vals"] if x], default=None)
wide = lambda r: bool(r["vals"][2]) and r["vals"][2]["sw"] > 0.5
print("--- image-plane rule at contact / best over +-0.2 s")
for nm, sel in [("all", rows), ("shoulders wide in image (front/back view)", [r for r in rows if wide(r)]), ("one hand", [r for r in rows if r["two"] == "no"]), ("one hand + wide", [r for r in rows if r["two"] == "no" and wide(r)])]:
    rep(nm + " [contact]", sel, at); rep(nm + " [max +-0.2 s]", sel, mx)
