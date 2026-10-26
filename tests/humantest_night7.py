"""Free overnight variants of the skeleton network, scored on Basile's human tags (same folds/windows as the clean_* runs):
  tta  = old labels, prediction averaged over time shifts -0.3..+0.3 s (and mirror)  -- robustness to the skeleton's timing error
  mix  = the 600 pilot windows use v2 labels (work/pilot_v2.json), the rest old labels
  mixtta = both
  mix2   = like mix, after the pilot labels were extended to 1200 windows (PILOT_N=1200)
  python tests/humantest_night7.py --variant tta --seed 0   |   --eval"""
import argparse, glob, json, os, sys, types
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"; SH = (-0.3, -0.15, 0.0, 0.15, 0.3)
NEW = {"forehand": "forehand", "backhand": "backhand", "serve": "serve", "none": "no_stroke"}


def run(variant, seed):
    import torch, stroke_net as sn
    sn.CHAN, sn.ARCH = "3d", "conv"; torch.manual_seed(seed); np.random.seed(seed)
    if "tta" in variant:
        def predict_tta(net, te, args):
            dev = next(net.parameters()).device; net.eval(); out = []
            with torch.no_grad():
                for i in range(0, len(te), 64):
                    ch = te[i:i + 64]; acc = 0
                    for s in SH:
                        for m in (False, True):
                            X = torch.tensor(np.stack([sn.tensor(r, shift=s, mirror=m, hand_mode=args.hand) for r in ch])).to(dev); acc = acc + torch.softmax(net(X), 1)
                    out.append((acc / (2 * len(SH))).cpu().numpy())
            return np.concatenate(out)
        sn.predict = predict_tta
    rows = sn.build()
    if "mix" in variant:
        v2 = json.load(open("work/pilot_v2.json"))
        for r in rows:
            v = v2.get(r["k"])
            if v and v["stroke"] in NEW: r["y"] = sn.CLASSES.index(NEW[v["stroke"]])
    args = types.SimpleNamespace(hand="none", epochs=60)
    vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    P = np.zeros((len(rows), len(sn.CLASSES)))
    for f in range(5):
        tr = [r for r in rows if fold[r["vid"]] != f]; te_i = [i for i, r in enumerate(rows) if fold[r["vid"]] == f]
        P[te_i] = sn.fit_predict(tr, [rows[i] for i in te_i], args); print(f"  fold {f + 1}/5 done", flush=True)
    json.dump(dict(keys=[r["k"] for r in rows], P=P.tolist(), y=[r["y"] for r in rows]), open(f"{D}/n7_{variant}_s{seed}.json", "w"))


def ev():
    t = json.load(open(f"{D}/tags.json")); K = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {K[i]["key"]: H[h] for i, h in t.items() if h in H}
    sets = {"base (old labels)": sorted(glob.glob(f"{D}/clean_base_s*.json"))}
    for v in ("tta", "mix", "mixtta", "mix2"): sets[v] = sorted(glob.glob(f"{D}/n7_{v}_s*.json"))
    preds = {}
    for name, fs in sets.items():
        if not fs: continue
        R = [json.load(open(f)) for f in fs]; Pm = np.mean([np.array(r["P"]) for r in R], 0); preds[name] = {k: int(np.argmax(p)) for k, p in zip(R[0]["keys"], Pm)}
    common = [k for k in hum if all(k in p for p in preds.values())]
    print(f"scored on {len(common)} human windows (identical for every row)")
    for name, pr in preds.items():
        acc = np.mean([hum[k] == pr[k] for k in common]); fb = [k for k in common if hum[k] in (0, 1) and pr[k] in (0, 1)]
        rec = {c: f"{sum(1 for k in common if hum[k]==i and pr[k]==i)}/{sum(1 for k in common if hum[k]==i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{name:18s} seeds {len(sets[name])} | acc {acc:.3f} | side acc {np.mean([hum[k]==pr[k] for k in fb]):.3f} (n={len(fb)}) | recall {rec}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    ev() if a.eval else run(a.variant, a.seed)
