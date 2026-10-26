"""Pretrained VIDEO model (Kinetics-400, torchvision r2plus1d_18), frozen, as a feature extractor on the 8 player-crop frames, then a logistic-regression head.
No fine-tuning (the fine-tuned image model memorised the videos). 5 video-grouped folds like everything else; scored on Basile's human tags.
  python tests/vid_probe.py     (needs work/crops.npy; torchvision; downloads ~120 MB of weights once)"""
import json, os, sys
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"; CL = ["forehand", "backhand", "serve", "no_stroke"]


def feats():
    import torch, torchvision, stroke_net as sn
    rows = sn.build(); assert json.load(open("work/crops_keys.json")) == [r["k"] for r in rows]
    arr = np.load("work/crops.npy", mmap_mode="r"); ok = np.load("work/crops_ok.npy").astype(bool)
    f = "work/vid_feats.npz"
    if os.path.exists(f): d = np.load(f); return rows, d["F"], d["Fm"], ok
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = torchvision.models.video.r2plus1d_18(weights=torchvision.models.video.R2Plus1D_18_Weights.KINETICS400_V1); m.fc = torch.nn.Identity(); m = m.to(dev).eval()
    mean = torch.tensor([0.43216, 0.394666, 0.37645], device=dev).view(1, 3, 1, 1, 1); std = torch.tensor([0.22803, 0.22145, 0.216989], device=dev).view(1, 3, 1, 1, 1)
    F = np.zeros((len(rows), 512), np.float32); Fm = np.zeros_like(F)
    with torch.no_grad():
        for i in range(0, len(rows), 16):
            idx = [j for j in range(i, min(i + 16, len(rows))) if ok[j]]
            if not idx: continue
            x = torch.from_numpy(np.stack([arr[j] for j in idx])).to(dev).permute(0, 4, 1, 2, 3).float() / 255.0     # B,3,T,H,W
            x = (x - mean) / std; F[idx] = m(x).cpu().numpy(); Fm[idx] = m(x.flip(-1)).cpu().numpy()
            if (i // 16) % 20 == 0: print(f"  features {i}/{len(rows)}", flush=True)
    np.savez(f, F=F, Fm=Fm); return rows, F, Fm, ok


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import roc_auc_score
    rows, F, Fm, ok = feats(); y = np.array([r["y"] for r in rows]); vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    fo = np.array([fold[r["vid"]] for r in rows]); P = np.zeros((len(rows), 4))
    for C in (0.01, 0.1):
        for f in range(5):
            tr = np.where((fo != f) & ok)[0]; te = np.where((fo == f) & ok)[0]
            sc = StandardScaler().fit(np.vstack([F[tr], Fm[tr]])); clf = LogisticRegression(C=C, max_iter=2000, class_weight="balanced").fit(sc.transform(np.vstack([F[tr], Fm[tr]])), np.concatenate([y[tr], y[tr]]))
            P[te] = (clf.predict_proba(sc.transform(F[te])) + clf.predict_proba(sc.transform(Fm[te]))) / 2
        m = ok; fb = m & np.isin(y, [0, 1])
        print(f"C={C}: accuracy vs labels {np.mean(P[m].argmax(1) == y[m]):.3f} | forehand-vs-backhand AUC {roc_auc_score(y[fb] == 1, P[fb][:, 1] / (P[fb][:, 0] + P[fb][:, 1] + 1e-9)):.3f}   (skeleton network: 0.67 / 0.805)", flush=True)
        json.dump(dict(keys=[r["k"] for r in rows], P=P.tolist(), ok=ok.tolist()), open(f"{D}/vidprobe_C{C}.json", "w"))
    t = json.load(open(f"{D}/tags.json")); K = json.load(open(f"{D}/key_DO_NOT_OPEN.json")); H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {K[i]["key"]: H[h] for i, h in t.items() if h in H}
    for C in (0.01, 0.1):
        R = json.load(open(f"{D}/vidprobe_C{C}.json")); pr = {k: int(np.argmax(p)) for k, p, o in zip(R["keys"], R["P"], R["ok"]) if o}
        ks = [k for k in hum if k in pr]; fb = [k for k in ks if hum[k] in (0, 1) and pr[k] in (0, 1)]
        print(f"human tags, C={C}: {len(ks)} windows | acc {np.mean([hum[k]==pr[k] for k in ks]):.3f} | side acc {np.mean([hum[k]==pr[k] for k in fb]):.3f} (n={len(fb)})   (skeleton: 0.595 / 0.757)")


if __name__ == "__main__":
    main()
