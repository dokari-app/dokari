"""Free test: does dropping doubtful training windows help the network, measured on Basile's human tags?
  python tests/humantest_clean.py --variant base --seed 0      (variants: base | A | B | C)
  python tests/humantest_clean.py --eval
A = drop training windows whose old label disagrees with the network's own held-out prediction
B = drop training windows the labeller marked confidence 1
C = both.   Same 5 video-grouped folds as stroke_net.py; the human-tagged windows are scored from the fold that did not train on their video."""
import argparse, collections, glob, json, os, sys, types
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np, torch
import stroke_net as sn
D = "work/humantest"


def baseline_oof():
    Ps = [json.load(open(f"work/stroke_net_preds_c3d_aconv_hnone_pre2.4_ep60_s{i}.json")) for i in range(3)]
    return {k: int(np.argmax(m)) for k, m in zip(Ps[0]["keys"], np.mean([np.array(p["P"]) for p in Ps], 0))}


def run(variant, seed):
    sn.CHAN, sn.ARCH = "3d", "conv"; torch.manual_seed(seed); np.random.seed(seed)
    args = types.SimpleNamespace(hand="none", epochs=60)
    rows = sn.build(); oof = baseline_oof()
    def keep(r):
        a = variant in ("A", "C"); b = variant in ("B", "C")
        if a and oof.get(r["k"], r["y"]) != r["y"]: return False
        if b and r["conf"] < 2: return False
        return True
    vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    P = np.zeros((len(rows), len(sn.CLASSES))); ntr = []
    for f in range(5):
        tr = [r for r in rows if fold[r["vid"]] != f and keep(r)]; ntr.append(len(tr))
        te_i = [i for i, r in enumerate(rows) if fold[r["vid"]] == f]
        P[te_i] = sn.fit_predict(tr, [rows[i] for i in te_i], args); print(f"  fold {f + 1}/5 done, trained on {len(tr)}", flush=True)
    json.dump(dict(keys=[r["k"] for r in rows], P=P.tolist(), y=[r["y"] for r in rows], ntrain=ntr), open(f"{D}/clean_{variant}_s{seed}.json", "w"))


def ev():
    t = json.load(open(f"{D}/tags.json")); K = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}
    hum = {K[i]["key"]: H[h] for i, h in t.items() if h in H}
    names = sorted({os.path.basename(f).split("_")[1] for f in glob.glob(f"{D}/clean_*_s*.json")})
    base_pred = None
    for v in sorted(names, key=lambda x: (x != "base", x)):
        fs = sorted(glob.glob(f"{D}/clean_{v}_s*.json")); R = [json.load(open(f)) for f in fs]
        keys = R[0]["keys"]; Pm = np.mean([np.array(r["P"]) for r in R], 0); pred = {k: int(np.argmax(p)) for k, p in zip(keys, Pm)}
        ks = [k for k in hum if k in pred]
        acc = np.mean([hum[k] == pred[k] for k in ks])
        fb = [k for k in ks if hum[k] in (0, 1) and pred[k] in (0, 1)]
        side = np.mean([hum[k] == pred[k] for k in fb])
        rec = {c: f"{sum(1 for k in ks if hum[k] == i and pred[k] == i)}/{sum(1 for k in ks if hum[k] == i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{v:5s} seeds {len(fs)} trained on ~{int(np.mean(R[0]['ntrain']))} | human windows {len(ks)} | acc {acc:.3f} | fh/bh side acc {side:.3f} (n={len(fb)}) | recall {rec}")
        if v == "base": base_pred = (pred, ks)
        elif base_pred:
            b, ks0 = base_pred; both = [k for k in ks if k in b]
            d = np.mean([hum[k] == pred[k] for k in both]) - np.mean([hum[k] == b[k] for k in both])
            print(f"      vs base on the same {len(both)} windows: {d:+.3f} accuracy (a difference under about 0.05 is within the noise of {len(both)} windows)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    ev() if a.eval else run(a.variant, a.seed)
