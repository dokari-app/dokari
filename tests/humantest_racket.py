"""Does racket position over time help the network?  Same windows, same folds, with vs without 6 racket channels, scored on Basile's human tags.
  python tests/humantest_racket.py --train base|racket --seed 0   |   --eval"""
import argparse, glob, json, os, pickle, sys, types
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"
GRID = np.round(np.arange(-2.7, 0.81, 0.1), 2)


def train(which, seed):
    import torch, stroke_net as sn
    sn.CHAN, sn.ARCH = "3d", "conv"; torch.manual_seed(seed); np.random.seed(seed)
    R = pickle.load(open("work/racket_seq.pkl", "rb")); orig = sn.tensor
    def racket_feats(r, shift, mirror):
        F = R[r["k"]]; idx = np.clip(np.round((sn.OFFS + shift - GRID[0]) / 0.1).astype(int), 0, len(GRID) - 1)
        X = F[idx][:, :6].copy(); X[:, 2] = np.where(X[:, 0] > 0, X[:, 2], 0)
        if mirror: X[:, 2] = -X[:, 2]
        return np.clip(X * np.array([1, 1, 3, 3, 3, 3]), -6, 6).astype(np.float32)
    if which == "racket":
        def tensor_r(r, shift=0.0, mirror=False, noise=0.0, hand_mode="oracle"):
            return np.concatenate([orig(r, shift=shift, mirror=mirror, noise=noise, hand_mode=hand_mode), racket_feats(r, shift, mirror)], 1)
        sn.tensor = tensor_r
    args = types.SimpleNamespace(hand="none", epochs=60)
    allrows = sn.build(); vids = sorted({r["vid"] for r in allrows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    sub = [r for r in allrows if r["k"] in R]
    key = json.load(open(f"{D}/key_DO_NOT_OPEN.json")); tags = json.load(open(f"{D}/tags.json")); hk = {key[i]["key"] for i, h in tags.items() if h in ("forehand", "backhand", "serve", "none")}
    P = {}
    for f in range(5):
        tr = [r for r in sub if fold[r["vid"]] != f]; te = [r for r in sub if fold[r["vid"]] == f and r["k"] in hk]
        if te: p = sn.fit_predict(tr, te, args); P.update({r["k"]: p[i].tolist() for i, r in enumerate(te)})
        print(f"  fold {f + 1}/5 trained on {len(tr)}", flush=True)
    json.dump(dict(P=P, n=len(sub)), open(f"{D}/racket_{which}_s{seed}.json", "w"))


def ev():
    tags = json.load(open(f"{D}/tags.json")); key = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {key[i]["key"]: H[h] for i, h in tags.items() if h in H}
    pred = {}
    for w in ("base", "racket"):
        R = [json.load(open(f)) for f in sorted(glob.glob(f"{D}/racket_{w}_s*.json"))]
        if not R: continue
        ks = set.intersection(*[set(r["P"]) for r in R]); pred[w] = {k: int(np.argmax(np.mean([r["P"][k] for r in R], 0))) for k in ks}
        ks = [k for k in pred[w] if k in hum]; acc = np.mean([hum[k] == pred[w][k] for k in ks])
        fb = [k for k in ks if hum[k] in (0, 1) and pred[w][k] in (0, 1)]; side = np.mean([hum[k] == pred[w][k] for k in fb])
        rec = {c: f"{sum(1 for k in ks if hum[k]==i and pred[w][k]==i)}/{sum(1 for k in ks if hum[k]==i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{w:6s} | seeds {len(R)} | ~{R[0]['n']*4//5} training windows | scored {len(ks)} human windows | acc {acc:.3f} | side acc {side:.3f} (n={len(fb)}) | recall {rec}")
    if len(pred) == 2:
        both = [k for k in pred["base"] if k in pred["racket"] and k in hum]
        d = np.mean([hum[k] == pred["racket"][k] for k in both]) - np.mean([hum[k] == pred["base"][k] for k in both])
        print(f"racket minus base on the same {len(both)} windows: {d:+.3f} accuracy (under about 0.05 = noise)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--train"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    ev() if a.eval else train(a.train, a.seed)
