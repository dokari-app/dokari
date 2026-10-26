"""Neural stroke classifier on pose sequences (forehand / backhand / serve / no_stroke).
Input per 0.1 s step around the skeleton swing event: depth-pose joints (3D) + image-plane joints (2D), torso-normalised, both wrists and shoulders, plus the racket hand.
Augmentation: mirror (swaps left/right joints and the racket hand: a left-hander's forehand is a mirrored right-hander's), random shift of the event by +-0.3 s, joint noise.
Grouped 5-fold CV by video.   python tests/stroke_net.py [--oracle-hand|--no-hand] [--epochs 40]"""
import argparse, json, os, pickle, sys, collections
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import torch, torch.nn as nn
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, ".")
from sphere.skeleton import J
torch.manual_seed(0); np.random.seed(0)
P2 = pickle.load(open("work/pose2d.pkl", "rb")); LAB = json.load(open("work/stroke_labels3.json"))
OFFS = np.arange(-float(os.environ.get("PRE", "1.6")), 0.51, 0.1); T = len(OFFS)
J3 = ["nose", "l_shoulder", "r_shoulder", "l_elbow", "r_elbow", "l_wrist", "r_wrist", "l_hip", "r_hip"]
I2 = [0, 1, 2, 3, 4, 5, 6, 7, 8]                    # same joints in pose2d.pkl order
SW = [0, 2, 1, 4, 3, 6, 5, 8, 7]                    # left<->right permutation
CLASSES = ["forehand", "backhand", "serve", "no_stroke"]
CHAN = "both"        # which pose channels the network sees: both | 3d | 2d   (3d = what every MediaPipe world-landmark stream has)
ARCH = "conv"        # conv | gru


def hands():
    out = {}
    for k, fr in json.load(open("work/stroke_hands.json")).items():
        c = collections.Counter(x["racket_hand"] for x in fr if x["racket_hand"] != "unclear")
        if sum(c.values()) >= 2 and c.most_common(1)[0][1] / sum(c.values()) >= 0.67: out[k] = 0 if c.most_common(1)[0][0] == "player_right" else 1
    return out


VH = hands(); CL = {}
HELD = set() if os.environ.get("LOCKED_OFF") or not os.path.exists("work/locked/heldout_videos.json") else set(json.load(open("work/locked/heldout_videos.json")))


def clip(act, vid):
    f = f"work/{act}/clips/{vid}.npz"
    if f not in CL:
        d = np.load(f, allow_pickle=True); CL[f] = (gaussian_filter1d(d["pose"], 1.5, axis=0, mode="nearest"), float(d["fps"]))
    return CL[f]


def sample(key, peak, shift=0.0):
    """-> (T, 9*3 + 9*2 + 2) array: 3D joints, 2D joints, masks (3D ok, 2D ok) ; NaN-free"""
    act, vid = key.split("/")[:2]; P, fps = clip(act, vid); ts, X2 = P2[key]
    t = peak + shift + OFFS
    t3 = np.arange(len(P)) / fps
    A3 = np.stack([np.interp(t, t3, P[:, J[n], c]) for n in J3 for c in range(3)], 1).reshape(T, 9, 3)
    ok3 = ((t >= 0) & (t <= t3[-1])).astype(np.float32)
    A2 = np.full((T, 9, 2), np.nan)
    for j, jj in enumerate(I2):
        for c in range(2):
            y = X2[:, jj, c]; m = np.isfinite(y)
            if m.sum() >= 3: A2[:, j, c] = np.interp(t, ts[m], y[m], left=np.nan, right=np.nan)
    ok2 = np.isfinite(A2).all((1, 2)).astype(np.float32)
    return A3, A2, ok3, ok2


def normalise(A3, A2):
    mh3 = (A3[:, 7] + A3[:, 8]) / 2; ms3 = (A3[:, 1] + A3[:, 2]) / 2; tor3 = np.median(np.linalg.norm(ms3 - mh3, axis=1)) + 1e-6
    A3 = (A3 - np.median(mh3, 0)) / tor3                 # origin: median hip of the window
    mh2 = (A2[:, 7] + A2[:, 8]) / 2; ms2 = (A2[:, 1] + A2[:, 2]) / 2
    tor2 = np.nanmedian(np.linalg.norm(ms2 - mh2, axis=1)); tor2 = tor2 if np.isfinite(tor2) and tor2 > 0.02 else 0.2
    c2 = np.nanmedian(mh2, 0); c2 = np.where(np.isfinite(c2), c2, 0)
    A2 = (A2 - c2) / tor2
    return A3, A2


def build(strict=True):
    rows = []
    for k, v in LAB.items():
        if k not in P2: continue
        s = "no_stroke" if v["stroke"] == "none" or v.get("shown") == "not_a_stroke" else v["stroke"]
        if s not in CLASSES: continue
        if strict and s in ("forehand", "backhand") and (v.get("contact_in_frames") == "no" or v.get("hit_above_head") == "yes"): continue
        if strict and s == "serve" and v.get("ball_toss_seen") == "no" and v.get("hit_above_head") == "no": continue
        act, vid = k.split("/")[:2]
        if not os.path.exists(f"work/{act}/clips/{vid}.npz"): continue
        h = VH.get(f"{act}/{vid}")
        if h is None: h = {"player_right": 0, "player_left": 1}.get(v.get("hand_vis"))
        if vid in HELD: continue                       # locked test videos are never trained on
        rows.append(dict(k=k, vid=vid, y=CLASSES.index(s), peak=v["peak"], hand=h, conf=v.get("confidence", 2)))
    return rows


MEMO = {}
GRID = [-0.3, -0.15, 0.0, 0.15, 0.3]


def base(r, shift):
    key = (r["k"], round(shift, 2))
    if key not in MEMO:
        A3, A2, ok3, ok2 = sample(r["k"], r["peak"], shift); A3, A2 = normalise(A3, A2); MEMO[key] = (A3, np.nan_to_num(A2), ok3, ok2)
    return MEMO[key]


def tensor(r, shift=0.0, mirror=False, noise=0.0, hand_mode="oracle"):
    A3, A2, ok3, ok2 = base(r, shift)
    h = r["hand"] if r["hand"] is not None else 0
    if mirror:
        A3 = A3[:, SW] * np.array([-1, 1, 1]); A2 = A2[:, SW] * np.array([-1, 1]); h = 1 - h
    if noise: A3 = A3 + np.random.randn(*A3.shape) * noise; A2 = A2 + np.random.randn(*A2.shape) * noise
    hv = np.zeros((T, 2), np.float32)
    if hand_mode == "oracle": hv[:, h] = 1.0
    parts = []
    if CHAN in ("both", "3d"): parts.append(A3.reshape(T, -1))
    if CHAN in ("both", "2d"): parts.append(A2.reshape(T, -1))
    if CHAN != "2d": parts.append(ok3[:, None])
    if CHAN != "3d": parts.append(ok2[:, None])
    parts.append(hv)
    return np.clip(np.concatenate(parts, 1).astype(np.float32), -6, 6)


def tensor_from_clip(P, fps, t_peak, hand=None, mirror=False):
    """Live/replay input from a skeleton stream only (depth pose, no image-plane pose). Needs CHAN == '3d'."""
    assert CHAN == "3d"
    t = t_peak + OFFS; t3 = np.arange(len(P)) / fps
    A3 = np.stack([np.interp(t, t3, P[:, J[n], c]) for n in J3 for c in range(3)], 1).reshape(T, 9, 3)
    ok3 = ((t >= 0) & (t <= t3[-1])).astype(np.float32)
    A3, _ = normalise(A3, np.full((T, 9, 2), np.nan)); h = hand
    if mirror:
        A3 = A3[:, SW] * np.array([-1, 1, 1]); h = None if h is None else 1 - h
    hv = np.zeros((T, 2), np.float32)
    if h is not None: hv[:, h] = 1.0              # hand=None: the 'no racket hand given' mode
    return np.clip(np.concatenate([A3.reshape(T, -1), ok3[:, None], hv], 1).astype(np.float32), -6, 6)


class Net(nn.Module):
    def __init__(self, cin, ncls):
        super().__init__()
        if ARCH == "gru":
            self.g = nn.GRU(cin, 80, batch_first=True, bidirectional=True)
            self.h = nn.Sequential(nn.Dropout(0.3), nn.Linear(320, 64), nn.GELU(), nn.Dropout(0.3), nn.Linear(64, ncls)); return
        self.f = nn.Sequential(nn.Conv1d(cin, 96, 5, padding=2), nn.BatchNorm1d(96), nn.GELU(), nn.Dropout(0.2),
                               nn.Conv1d(96, 96, 5, padding=2), nn.BatchNorm1d(96), nn.GELU(), nn.Dropout(0.2),
                               nn.Conv1d(96, 96, 3, padding=1), nn.BatchNorm1d(96), nn.GELU())
        self.h = nn.Sequential(nn.Linear(192, 64), nn.GELU(), nn.Dropout(0.3), nn.Linear(64, ncls))
    def forward(self, x):                    # x: (B, T, C)
        if ARCH == "gru":
            z, _ = self.g(x); return self.h(torch.cat([z.mean(1), z.amax(1)], 1))
        z = self.f(x.transpose(1, 2)); return self.h(torch.cat([z.mean(2), z.amax(2)], 1))


def train(tr, args):
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    cin = tensor(tr[0], hand_mode=args.hand).shape[1]; net = Net(cin, len(CLASSES)).to(dev)
    y = np.array([r["y"] for r in tr]); w = torch.tensor(len(y) / (len(CLASSES) * np.maximum(np.bincount(y, minlength=len(CLASSES)), 1)), dtype=torch.float32).to(dev)
    opt = torch.optim.AdamW(net.parameters(), 2e-3, weight_decay=1e-2); sched = torch.optim.lr_scheduler.OneCycleLR(opt, 4e-3, total_steps=args.epochs * ((len(tr) + 63) // 64))
    lossf = nn.CrossEntropyLoss(weight=w, label_smoothing=0.05)
    for ep in range(args.epochs):
        net.train(); idx = np.random.permutation(len(tr))
        for i in range(0, len(idx), 64):
            b = [tr[j] for j in idx[i:i + 64]]
            X = torch.tensor(np.stack([tensor(r, shift=float(np.random.choice(GRID)), mirror=np.random.rand() < .5, noise=0.02, hand_mode=args.hand) for r in b])).to(dev)
            Y = torch.tensor([r["y"] for r in b]).to(dev); opt.zero_grad(); lossf(net(X), Y).backward(); opt.step(); sched.step()
    return net


def predict(net, te, args):
    dev = next(net.parameters()).device; net.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(te), 128):
            X = torch.tensor(np.stack([tensor(r, hand_mode=args.hand) for r in te[i:i + 128]])).to(dev)
            Xm = torch.tensor(np.stack([tensor(r, mirror=True, hand_mode=args.hand) for r in te[i:i + 128]])).to(dev)
            out.append(((torch.softmax(net(X), 1) + torch.softmax(net(Xm), 1)) / 2).cpu().numpy())      # test-time mirroring
    return np.concatenate(out)


def fit_predict(tr, te, args):
    return predict(train(tr, args), te, args)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hand", default="oracle", choices=["oracle", "none"]); ap.add_argument("--epochs", type=int, default=40); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--tag", default=""); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--frac", type=float, default=1.0, help="learning curve: train on this share of the training videos"); ap.add_argument("--arch", default="conv", choices=["conv", "gru"]); ap.add_argument("--chan", default="both", choices=["both", "3d", "2d"]); ap.add_argument("--final", type=int, default=0, help="train this many seeds on ALL windows and save them to work/net_final/")
    global CHAN, ARCH
    args = ap.parse_args(); CHAN, ARCH = args.chan, args.arch; torch.manual_seed(args.seed); np.random.seed(args.seed); rows = build()
    if args.limit: rows = rows[:args.limit]
    print("windows", len(rows), collections.Counter(CLASSES[r["y"]] for r in rows), "| hand mode:", args.hand, "| channels:", CHAN, "| arch:", ARCH, "| PRE", os.environ.get("PRE", "1.6"), flush=True)
    if args.final:
        os.makedirs("work/net_final", exist_ok=True)
        for i in range(args.final):
            torch.manual_seed(100 + i); np.random.seed(100 + i); net = train(rows, args)
            torch.save(net.state_dict(), f"work/net_final/{args.tag.strip('_') or 'net'}_s{i}.pt"); print("  saved model", i + 1, "of", args.final, flush=True)
        json.dump(dict(chan=CHAN, arch=ARCH, pre=float(os.environ.get("PRE", "1.6")), hand=args.hand, epochs=args.epochs, classes=CLASSES, T=T, cin=tensor(rows[0], hand_mode=args.hand).shape[1], n=args.final, tag=args.tag.strip("_") or "net"),
                  open(f"work/net_final/{args.tag.strip('_') or 'net'}_config.json", "w")); print("final models saved"); return
    vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    P = np.zeros((len(rows), len(CLASSES)))
    for f in range(5):
        tr = [r for r in rows if fold[r["vid"]] != f]
        if args.frac < 1.0:
            tv = sorted({r["vid"] for r in tr}); np.random.RandomState(args.seed * 7 + f).shuffle(tv); keep = set(tv[:max(3, int(len(tv) * args.frac))]); tr = [r for r in tr if r["vid"] in keep]
        te_i = [i for i, r in enumerate(rows) if fold[r["vid"]] == f]
        P[te_i] = fit_predict(tr, [rows[i] for i in te_i], args); print(f"  fold {f + 1}/5 done", flush=True)
    y = np.array([r["y"] for r in rows]); pred = P.argmax(1)
    print(f"\naccuracy {np.mean(pred == y):.3f} | recall", {c: round(float(np.mean(pred[y == i] == i)), 2) for i, c in enumerate(CLASSES)})
    print("rows=truth cols=pred", CLASSES)
    for i, c in enumerate(CLASSES): print("  %-10s" % c, [int(((y == i) & (pred == j)).sum()) for j in range(len(CLASSES))])
    fb = np.isin(y, [0, 1]); s = P[fb][:, 1] / (P[fb][:, 0] + P[fb][:, 1] + 1e-9)
    from sklearn.metrics import roc_auc_score
    print("forehand-vs-backhand AUC (windows that are one of the two): %.3f" % roc_auc_score(y[fb] == 1, s))
    cf = [r["conf"] >= 2 for r in rows]; m = fb & np.array(cf)
    print("   same, confidence>=2 labels: %.3f" % roc_auc_score(y[m] == 1, P[m][:, 1] / (P[m][:, 0] + P[m][:, 1] + 1e-9)))
    json.dump(dict(keys=[r["k"] for r in rows], P=P.tolist(), y=y.tolist()), open(f"work/stroke_net_preds{args.tag}.json", "w"))


if __name__ == "__main__":
    main()
