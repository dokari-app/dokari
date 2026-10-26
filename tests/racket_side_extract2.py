"""v2: racket detected INSIDE the player crop (upscaled), 5 frames around contact. Where is the racket head relative to the body at contact? For every forehand/backhand window (contact time from the frames).
Racket box from models/tennis_v8_player_racket_ball.onnx, shoulders/wrists from MediaPipe 2D on the player crop. Free, Mac only, resumable.
  python tests/racket_side_extract.py     -> work/racket_side.json"""
import json, os, sys
import numpy as np, cv2
sys.path.insert(0, ".")
from sphere import labelling, ball, extract
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

OUT = "work/racket_side2.json"
lab = json.load(open("work/stroke_labels3.json")); res = json.load(open(OUT)) if os.path.exists(OUT) else {}
det = ball.Detector("models/tennis_v8_player_racket_ball.onnx", threads=4)
lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=extract.ensure_model("full")), running_mode=vision.RunningMode.IMAGE, num_poses=1))
keys = [k for k, v in lab.items() if v["stroke"] in ("forehand", "backhand") and v.get("contact_frame", 0) > 0 and k not in res]
print("windows", len(keys), flush=True)
for n, k in enumerate(keys, 1):
    v = lab[k]; act, vid = k.split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
    w0, w1 = v["window"]; tc = w0 + (w1 - w0) * ((v["contact_frame"] - 1) / 7); cap = cv2.VideoCapture(vf); out = []
    for o in (-0.1, -0.05, 0.0, 0.05, 0.1):
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0, tc + o)); ok, fr = cap.read()
        if not ok: continue
        H, W = fr.shape[:2]; dets = det.run(fr, conf=0.1); pb = ball.player_box(dets)
        if pb is None: continue
        x0, y0, x1, y1 = [int(max(0, c)) for c in pb]; pw, ph = x1 - x0, y1 - y0
        cx0, cy0, cx1, cy1 = max(0, x0 - pw // 3), max(0, y0 - ph // 10), min(W, x1 + pw // 3), min(H, y1 + ph // 10)
        crop = fr[cy0:cy1, cx0:cx1]
        sc = max(1.0, 640.0 / max(crop.shape[:2])); big = cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
        rk = [(d[0], d[1], d[2] / sc + cx0, d[3] / sc + cy0, d[4] / sc + cx0, d[5] / sc + cy0) for d in det.run(big, conf=0.08, classes=(ball.RACKET,))]
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
        if not r.pose_landmarks: continue
        p = r.pose_landmarks[0]; ch, cw = crop.shape[:2]
        pt = lambda j: [cx0 + p[j].x * cw, cy0 + p[j].y * ch]
        best = max(rk, key=lambda d: d[1]) if rk else None
        out.append(dict(off=o, player=[x0, y0, x1, y1], rk=None if best is None else [float(best[1])] + [float(c) for c in best[2:]], ls=pt(11), rs=pt(12), lw=pt(15), rw=pt(16), lh=pt(23), rh=pt(24), n_rk=len(rk)))
    cap.release(); res[k] = out
    if n % 50 == 0 or n == len(keys):
        json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT); print(f"  {n}/{len(keys)}", flush=True)
json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT); print("done")
