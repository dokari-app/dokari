"""Look at it: draw our pose's RIGHT (red) and LEFT (blue) wrist/shoulder on the contact frame of 20 windows, with what the labeller saw. Mac, free.
  python tests/lr_sheet.py -> work/lr_sheet.jpg"""
import json, random, sys
import numpy as np, cv2
sys.path.insert(0, ".")
from sphere import labelling, ball, extract
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision
lab = json.load(open("work/stroke_labels3.json"))
det = ball.Detector("models/tennis_v8_player_racket_ball.onnx", threads=4)
lm = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_path=extract.ensure_model("full")), running_mode=vision.RunningMode.IMAGE, num_poses=1))
ks = [k for k, v in lab.items() if v["stroke"] in ("forehand", "backhand") and v.get("contact_frame", 0) > 0 and v.get("confidence", 0) >= 2 and v.get("side_vis") in ("player_right_side", "player_left_side")]
random.Random(7).shuffle(ks); tiles = []
for k in ks:
    if len(tiles) >= 20: break
    v = lab[k]; act, vid = k.split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid); w0, w1 = v["window"]
    tc = w0 + (w1 - w0) * ((v["contact_frame"] - 1) / 7); cap = cv2.VideoCapture(vf); cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * tc); ok, fr = cap.read(); cap.release()
    if not ok: continue
    H, W = fr.shape[:2]; pb = ball.player_box(det.run(fr, conf=0.1, classes=(ball.PERSON,)))
    if pb is None: continue
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]; x0, y0, x1, y1 = [int(c) for c in (max(0, pb[0] - pw * .5), max(0, pb[1] - ph * .1), min(W, pb[2] + pw * .5), min(H, pb[3] + ph * .1))]
    crop = fr[y0:y1, x0:x1].copy(); r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
    ch, cw = crop.shape[:2]
    if r.pose_landmarks:
        p = r.pose_landmarks[0]
        for j, nm, col in ((12, "R-sh", (0, 0, 255)), (11, "L-sh", (255, 0, 0)), (16, "R-wr", (0, 0, 255)), (15, "L-wr", (255, 0, 0))):
            c = (int(p[j].x * cw), int(p[j].y * ch)); cv2.circle(crop, c, max(4, cw // 60), col, -1); cv2.putText(crop, nm, (c[0] + 4, c[1] - 4), 0, max(.4, cw / 700), col, 1)
    crop = cv2.resize(crop, (320, 320)); cv2.putText(crop, f"{len(tiles)} {v['stroke'][:2].upper()} hand={v['hand_vis'][7:]} side={v['side_vis'][7:-5]}", (4, 16), 0, .5, (0, 255, 255), 1)
    tiles.append(crop)
while len(tiles) % 5: tiles.append(np.zeros((320, 320, 3), np.uint8))
cv2.imwrite("work/lr_sheet.jpg", np.vstack([np.hstack(tiles[i:i + 5]) for i in range(0, len(tiles), 5)])); print("ok", len(tiles))
