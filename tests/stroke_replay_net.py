"""Replay recorded streams the way the live app sees them with the trained neural stroke model (depth pose only):
events are found as they happen (overhead reach, wrist-speed peak), each is classified 0.5 s after the event from the past only, then merged
(a serve takes the toss/bounce/follow-through events around it) and compared with what was filmed.
  python tests/stroke_replay_net.py [work/net_final/<tag>_config.json]"""
import sys, os, glob, json
import numpy as np, torch
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
import stroke_net as S
from sphere.skeleton import J
cfgp = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("work/net_final/*_config.json"))[-1]
cfg = json.load(open(cfgp)); S.CHAN, S.ARCH = cfg["chan"], cfg["arch"]; assert S.CHAN == "3d", "replay needs a depth-pose-only model (--chan 3d)"
os.environ["PRE"] = str(cfg["pre"]); S.OFFS = np.arange(-cfg["pre"], 0.51, 0.1); S.T = len(S.OFFS)
dev = "mps" if torch.backends.mps.is_available() else "cpu"; models = []
for f in sorted(glob.glob(f"work/net_final/{cfg['tag']}_s*.pt")):
    m = S.Net(cfg["cin"], len(S.CLASSES)).to(dev); m.load_state_dict(torch.load(f, map_location=dev)); m.eval(); models.append(m)
print("config", cfgp, "| models", len(models), "| classes", S.CLASSES)
TRUTH = {"IMG_2935 3": [(0, 1e9, "serve")], "IMG_2935": [(0, 1e9, "forehand")], "IMG_2935 2": [(0, 50, "serve")]}


def classify(P, fps, t):
    cut = int((t + 0.5) * fps) + 1
    X = torch.tensor(np.stack([S.tensor_from_clip(P[:cut], fps, t), S.tensor_from_clip(P[:cut], fps, t, mirror=True)])).to(dev)
    with torch.no_grad(): pr = np.mean([(torch.softmax(m(X), 1)).mean(0).cpu().numpy() for m in models], 0)
    return pr


def events(P, fps):
    Ps = gaussian_filter1d(P, 1.5, axis=0, mode="nearest")
    ms = (Ps[:, J["l_shoulder"]] + Ps[:, J["r_shoulder"]]) / 2; mh = (Ps[:, J["l_hip"]] + Ps[:, J["r_hip"]]) / 2
    torso = float(np.median(np.linalg.norm(ms - mh, axis=1))) or 0.5
    nose = Ps[:, J["nose"]]
    up = np.stack([(Ps[:, J[f"{s}_wrist"], 1] - nose[:, 1]) / torso for s in "lr"]).max(0)
    sp = np.stack([gaussian_filter1d(np.linalg.norm(np.gradient(Ps[:, J[f"{s}_wrist"]], axis=0), axis=1) * fps / torso, 2) for s in "lr"]).max(0)
    ov, _ = find_peaks(gaussian_filter1d(up, 2), height=0.45, distance=int(3.0 * fps))
    pk, _ = find_peaks(sp, height=max(3.0, 0.35 * np.percentile(sp, 99)), distance=int(1.5 * fps))
    pk = [p for p in pk if all(abs(p - o) > 1.5 * fps for o in ov) and up[p] < 0.45]
    return sorted([(o / fps, "over") for o in ov] + [(p / fps, "swing") for p in pk])


def replay(f, truth=None):
    d = np.load(f, allow_pickle=True); P, fps = d["pose"], float(d["fps"])
    ev = events(P, fps); preds = []
    for t, kind in ev:
        pr = classify(P, fps, t); k = int(np.argmax(pr)); preds.append((t, kind, S.CLASSES[k], float(pr[k]), dict(zip(S.CLASSES, map(float, pr)))))
    anchors = [p for p in preds if (p[1] == "over" or p[2] == "serve") and p[4]["serve"] >= 0.5]
    anchors.sort(key=lambda p: (p[1] != "over", -p[3])); kept, used = [], set()
    for a in anchors:
        if a[0] in used: continue
        kept.append(a); used.add(a[0])
        for p in preds:
            if -2.4 <= p[0] - a[0] <= 0.8: used.add(p[0])
    kept += [p for p in preds if p[0] not in used]; kept = sorted([p for p in kept if p[2] != "no_stroke"])
    cnt = {}
    for p in kept: cnt[p[2]] = cnt.get(p[2], 0) + 1
    print(f"\n{os.path.basename(f)}: {len(ev)} events -> {len(kept)} strokes {cnt}")
    for t, kind, lab, conf, pr in kept:
        tr = [l for a, b, l in truth if a <= t < b] if truth else []
        print(f"   t={t:6.1f}s {kind:5s} -> {lab:9s} ({conf:.2f})" + (("   ok" if tr[0] == lab else f"   WRONG (filmed {tr[0]})") if tr else ""))
    return kept


for stem, tr in TRUTH.items():
    f = f"work/check/as_filmed/{stem}.skeleton.npz"
    if os.path.exists(f): replay(f, tr)
for f in sorted(glob.glob("work/phone/live_*.skeleton.npz")): replay(f)
