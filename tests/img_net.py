"""Image model: small pretrained CNN (MobileNetV3-small) on 8 player-crop frames + a temporal head, fine-tuned end to end.
Needs: tests/crops_extract.py done, torchvision installed (pip install torchvision).  Free, Mac.
  python tests/img_net.py --seed 0 --epochs 8 --tag a      (5 video-grouped folds, same folds as stroke_net.py) -> work/img_net_preds_a_s0.json
  python tests/img_net.py --eval --tag a                   (score against Basile's human tags; also skeleton+image ensemble)"""
import argparse, collections, glob, json, os, sys, time
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"; CLASSES = ["forehand", "backhand", "serve", "no_stroke"]


def build_net(torch, nn):
    import torchvision
    class Net(nn.Module):
        def __init__(s):
            super().__init__()
            m = torchvision.models.mobilenet_v3_small(weights=torchvision.models.MobileNet_V3_Small_Weights.DEFAULT)
            s.bb = m.features; s.pool = nn.AdaptiveAvgPool2d(1); s.proj = nn.Sequential(nn.Linear(576, 128), nn.GELU(), nn.Dropout(0.2))
            s.tc = nn.Sequential(nn.Conv1d(128, 128, 3, padding=1), nn.BatchNorm1d(128), nn.GELU(), nn.Conv1d(128, 128, 3, padding=1), nn.BatchNorm1d(128), nn.GELU())
            s.head = nn.Sequential(nn.Dropout(0.3), nn.Linear(256, 64), nn.GELU(), nn.Linear(64, len(CLASSES)))
        def forward(s, x):                      # x: (B, T, 3, H, W) normalised
            B, T = x.shape[:2]; z = s.pool(s.bb(x.flatten(0, 1))).flatten(1); z = s.proj(z).view(B, T, -1)
            z = s.tc(z.transpose(1, 2)); return s.head(torch.cat([z.mean(2), z.amax(2)], 1))
        def train(s, mode=True):
            super().train(mode)
            for m in s.bb.modules():
                if isinstance(m, nn.BatchNorm2d): m.eval()      # frozen BN statistics: small batches
            return s
    return Net()


def run(args):
    import torch, torch.nn as nn, torch.nn.functional as F
    import stroke_net as sn
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    rows = sn.build(); keys = [r["k"] for r in rows]
    assert json.load(open("work/crops_keys.json")) == keys, "crops were built for a different window list"
    arr = np.load("work/crops.npy", mmap_mode="r"); ok = np.load("work/crops_ok.npy").astype(bool)
    y = np.array([r["y"] for r in rows]); vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    fo = np.array([fold[r["vid"]] for r in rows]); dev = "mps" if torch.backends.mps.is_available() else "cpu"
    mean = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 1, 3, 1, 1); std = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 1, 3, 1, 1)
    def batch(idx, aug):
        x = torch.from_numpy(np.stack([arr[i] for i in idx])).to(dev).permute(0, 1, 4, 2, 3).float() / 255.0    # B,T,3,H,W
        if aug:
            B = x.shape[0]; out = []
            for b in range(B):
                xb = x[b]
                if np.random.rand() < 0.5: xb = xb.flip(-1)                 # mirror: a left-hander's stroke is a right-hander's, label unchanged
                s = np.random.uniform(0.85, 1.0); h = int(112 * s); oy, ox = np.random.randint(0, 112 - h + 1, 2)
                xb = F.interpolate(xb[:, :, oy:oy + h, ox:ox + h], size=(112, 112), mode="bilinear", align_corners=False)
                xb = (xb * np.random.uniform(0.8, 1.2) + np.random.uniform(-0.08, 0.08)).clamp(0, 1); out.append(xb)
            x = torch.stack(out)
        return (x - mean) / std
    P = np.full((len(rows), len(CLASSES)), np.nan)
    for f in range(5):
        tr = np.where((fo != f) & ok)[0]; te = np.where((fo == f) & ok)[0]
        net = sn_net = build_net(torch, nn).to(dev)
        yy = y[tr]; w = torch.tensor(len(yy) / (len(CLASSES) * np.maximum(np.bincount(yy, minlength=len(CLASSES)), 1)), dtype=torch.float32, device=dev)
        bbp = list(net.bb.parameters()); rest = [p for n, p in net.named_parameters() if not n.startswith("bb.")]
        opt = torch.optim.AdamW([{"params": bbp, "lr": args.lr}, {"params": rest, "lr": args.lr * 6}], weight_decay=1e-2)
        steps = args.epochs * ((len(tr) + args.bs - 1) // args.bs); sched = torch.optim.lr_scheduler.OneCycleLR(opt, [args.lr * 3, args.lr * 18], total_steps=steps)
        lossf = nn.CrossEntropyLoss(weight=w, label_smoothing=0.05); t0 = time.time()
        for ep in range(args.epochs):
            net.train(); perm = np.random.permutation(tr); tot = 0
            for i in range(0, len(perm), args.bs):
                b = perm[i:i + args.bs]; opt.zero_grad(); loss = lossf(net(batch(b, True)), torch.tensor(y[b], device=dev)); loss.backward(); opt.step(); sched.step(); tot += float(loss) * len(b)
            print(f"  fold {f + 1}/5 epoch {ep + 1}/{args.epochs} loss {tot / len(tr):.3f} ({(time.time() - t0) / 60:.1f} min)", flush=True)
        net.eval()
        with torch.no_grad():
            for i in range(0, len(te), 32):
                b = te[i:i + 32]; x = batch(b, False); P[b] = ((torch.softmax(net(x), 1) + torch.softmax(net(x.flip(-1)), 1)) / 2).cpu().numpy()
    m = ok & np.isfinite(P).all(1); pred = P.argmax(1)
    print(f"\naccuracy {np.mean(pred[m] == y[m]):.3f} on {int(m.sum())} windows | recall", {c: round(float(np.mean(pred[m & (y == i)] == i)), 2) for i, c in enumerate(CLASSES)})
    fb = m & np.isin(y, [0, 1])
    from sklearn.metrics import roc_auc_score
    print("forehand-vs-backhand AUC: %.3f" % roc_auc_score(y[fb] == 1, P[fb][:, 1] / (P[fb][:, 0] + P[fb][:, 1] + 1e-9)))
    json.dump(dict(keys=keys, P=np.nan_to_num(P).tolist(), ok=m.tolist(), y=y.tolist()), open(f"work/img_net_preds_{args.tag}_s{args.seed}.json", "w"))


def ev(args):
    tags = json.load(open(f"{D}/tags.json")); key = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {key[i]["key"]: H[h] for i, h in tags.items() if h in H}
    R = [json.load(open(f)) for f in sorted(glob.glob(f"work/img_net_preds_{args.tag}_s*.json"))]
    keys = R[0]["keys"]; ok = np.all([r["ok"] for r in R], 0); Pi = np.mean([np.array(r["P"]) for r in R], 0)
    S = [json.load(open(f"work/stroke_net_preds_c3d_aconv_hnone_pre2.4_ep60_s{i}.json")) for i in range(3)]
    sk = {k: p for k, p in zip(S[0]["keys"], np.mean([np.array(s["P"]) for s in S], 0))}
    img = {k: Pi[i] for i, k in enumerate(keys) if ok[i]}
    common = [k for k in hum if k in img and k in sk]
    def rep(name, f):
        pr = {k: int(np.argmax(f(k))) for k in common}; acc = np.mean([hum[k] == pr[k] for k in common])
        fb = [k for k in common if hum[k] in (0, 1) and pr[k] in (0, 1)]; side = np.mean([hum[k] == pr[k] for k in fb])
        rec = {c: f"{sum(1 for k in common if hum[k]==i and pr[k]==i)}/{sum(1 for k in common if hum[k]==i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{name:24s} acc {acc:.3f} | side acc {side:.3f} (n={len(fb)}) | recall {rec}")
    print(f"{len(R)} seed(s); scored on {len(common)} human-tagged windows (same windows for every row)")
    rep("skeleton network", lambda k: sk[k]); rep("image model", lambda k: img[k]); rep("skeleton + image average", lambda k: sk[k] + img[k])
    for th in (0.7, 0.8):
        s = [k for k in common if (sk[k] + img[k]).max() / 2 >= th]
        if s: print(f"  ensemble confidence >= {th}: covers {len(s)/len(common):.0%}, acc {np.mean([hum[k]==int(np.argmax(sk[k]+img[k])) for k in s]):.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--epochs", type=int, default=8); ap.add_argument("--bs", type=int, default=16); ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--tag", default="a"); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    ev(a) if a.eval else run(a)
