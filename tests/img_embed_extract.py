"""Feasibility test: can the stroke type be read from the pictures? Embeds 3 frames per labelled window (around the skeleton swing event, as the live app would
have them) with a small pretrained image network (MobileNetV2, ONNX) on a crop around the player. Free, Mac only, resumable.
  python tests/img_embed_extract.py      -> work/img_embed.pkl   (first run downloads the 14 MB network once)"""
import json, os, pickle, random, sys, collections, urllib.request
import numpy as np, cv2
sys.path.insert(0, ".")
from sphere import labelling, ball
URL = "https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-12.onnx"
NET = "models/mobilenetv2-12.onnx"; OUT = "work/img_embed.pkl"
if not os.path.exists(NET):
    print("downloading the image network (14 MB) ...", flush=True); urllib.request.urlretrieve(URL, NET)
import onnx, onnxruntime as ort
m = onnx.load(NET)
gem = [n for n in m.graph.node if n.op_type in ("Gemm", "MatMul")][-1]
feat = gem.input[0]
for n in m.graph.node:                                  # the tensor feeding the classifier = the pooled 1280-d embedding
    pass
m.graph.output.append(onnx.helper.make_tensor_value_info(feat, onnx.TensorProto.FLOAT, None))
sess = ort.InferenceSession(m.SerializeToString(), providers=["CPUExecutionProvider"])
iname = sess.get_inputs()[0].name; oi = [o.name for o in sess.get_outputs()].index(feat)
det = ball.Detector("models/tennis_v8_player_racket_ball.onnx", threads=4)
MEAN = np.array([0.485, 0.456, 0.406], np.float32); STD = np.array([0.229, 0.224, 0.225], np.float32)


def embed(img):
    x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (224, 224)).astype(np.float32) / 255.0
    x = ((x - MEAN) / STD).transpose(2, 0, 1)[None]
    return sess.run(None, {iname: x})[oi].reshape(-1)


lab = json.load(open("work/stroke_labels3.json")); res = pickle.load(open(OUT, "rb")) if os.path.exists(OUT) else {}
rng = random.Random(4); sel = collections.defaultdict(list)
for k, v in lab.items():
    s = "no_stroke" if v["stroke"] == "none" else v["stroke"]
    if s in ("forehand", "backhand", "serve", "no_stroke"): sel[s].append(k)
keys = []
for s, L in sel.items():
    rng.shuffle(L); keys += L[:650] if s == "no_stroke" else L
todo = [k for k in keys if k not in res]; print("windows", len(keys), "| to do", len(todo), flush=True)
for n, k in enumerate(todo, 1):
    act, vid = k.split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
    if not vf: continue
    cap = cv2.VideoCapture(vf); E = []; pb = None
    for o in (-0.15, 0.0, 0.15):
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * max(0, lab[k]["peak"] + o)); ok, fr = cap.read()
        if not ok: E.append(None); continue
        H, W = fr.shape[:2]; pb = ball.player_box(det.run(fr, conf=0.1, classes=(ball.PERSON,)), pb)
        if pb is None: E.append(None); continue
        cx, cy = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2; side = max(pb[2] - pb[0], pb[3] - pb[1]) * 1.35
        x0, y0, x1, y1 = [int(v_) for v_ in (max(0, cx - side / 2), max(0, cy - side / 2), min(W, cx + side / 2), min(H, cy + side / 2))]
        E.append(embed(fr[y0:y1, x0:x1]) if x1 - x0 > 20 and y1 - y0 > 20 else None)
    cap.release(); res[k] = E
    if n % 100 == 0 or n == len(todo):
        pickle.dump(res, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT); print(f"  {n}/{len(todo)}", flush=True)
pickle.dump(res, open(OUT + ".tmp", "wb")); os.replace(OUT + ".tmp", OUT); print("done")
