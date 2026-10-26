"""(Gemini-inspired) bone / wrist-distance channels. Variants: bone = bone vectors (elbow-shoulder, wrist-elbow, shoulder line, hip line, neck), wd = two-wrist distance and vector, bonewd = both.
   python tests/humantest_bone.py --variant bone --seed 0 | --eval
(older docstring:) View-robustness tests for the skeleton network, scored on Basile's human tags (same folds/windows as clean_base):
  bf    = extra channels: the joints rotated into the player's own body frame (yaw from the shoulder line in the first part of the window), so lateral/forward mean the same from any camera angle
  yaw   = training augmentation: random rotation of the 3D skeleton about the vertical axis (+-45 degrees)
  bfyaw = both
  python tests/humantest_view.py --variant bf --seed 0   |   --eval"""
import argparse, glob, json, os, sys, types
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"


def run(variant, seed):
    import torch, stroke_net as sn
    sn.CHAN, sn.ARCH = "3d", "conv"; torch.manual_seed(seed); np.random.seed(seed)
    BONE, WD = "bone" in variant, "wd" in variant
    def rot(A, th):
        c, s = np.cos(th), np.sin(th); x, z = A[..., 0].copy(), A[..., 2].copy(); B = A.copy(); B[..., 0] = c * x + s * z; B[..., 2] = -s * x + c * z; return B
    def tensor_v(r, shift=0.0, mirror=False, noise=0.0, hand_mode="none"):
        A3, A2, ok3, ok2 = sn.base(r, shift); A3 = A3.copy(); T = len(A3)
        if mirror: A3 = A3[:, sn.SW] * np.array([-1, 1, 1])
        parts = [A3.reshape(T, -1)]
        if BONE:
            ms = (A3[:, 1] + A3[:, 2]) / 2
            bones = [A3[:, 3] - A3[:, 1], A3[:, 5] - A3[:, 3], A3[:, 4] - A3[:, 2], A3[:, 6] - A3[:, 4], A3[:, 2] - A3[:, 1], A3[:, 8] - A3[:, 7], A3[:, 0] - ms]
            parts.append(np.concatenate(bones, 1))
        if WD:
            d = A3[:, 6] - A3[:, 5]; parts.append(np.concatenate([d, np.linalg.norm(d, axis=1, keepdims=True)], 1))
        if noise: parts[0] = parts[0] + np.random.randn(*parts[0].shape) * noise
        parts += [ok3[:, None], np.zeros((T, 2), np.float32)]
        return np.clip(np.concatenate(parts, 1).astype(np.float32), -6, 6)
    sn.tensor = tensor_v
    rows = sn.build(); args = types.SimpleNamespace(hand="none", epochs=60)
    vids = sorted({r["vid"] for r in rows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    P = np.zeros((len(rows), len(sn.CLASSES)))
    for f in range(5):
        tr = [r for r in rows if fold[r["vid"]] != f]; te_i = [i for i, r in enumerate(rows) if fold[r["vid"]] == f]
        P[te_i] = sn.fit_predict(tr, [rows[i] for i in te_i], args); print(f"  fold {f + 1}/5 done", flush=True)
    json.dump(dict(keys=[r["k"] for r in rows], P=P.tolist(), y=[r["y"] for r in rows]), open(f"{D}/bone_{variant}_s{seed}.json", "w"))


def ev():
    t = json.load(open(f"{D}/tags.json")); K = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {K[i]["key"]: H[h] for i, h in t.items() if h in H}
    sets = {"base": sorted(glob.glob(f"{D}/clean_base_s*.json"))}
    for v in ("bone", "wd", "bonewd"): sets[v] = sorted(glob.glob(f"{D}/bone_{v}_s*.json"))
    preds = {}
    for n, fs in sets.items():
        if not fs: continue
        R = [json.load(open(f)) for f in fs]; Pm = np.mean([np.array(r["P"]) for r in R], 0); preds[n] = {k: int(np.argmax(p)) for k, p in zip(R[0]["keys"], Pm)}
    common = [k for k in hum if all(k in p for p in preds.values())]
    print(f"scored on {len(common)} human windows (identical for every row)")
    for n, pr in preds.items():
        acc = np.mean([hum[k] == pr[k] for k in common]); fb = [k for k in common if hum[k] in (0, 1) and pr[k] in (0, 1)]
        rec = {c: f"{sum(1 for k in common if hum[k]==i and pr[k]==i)}/{sum(1 for k in common if hum[k]==i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{n:6s} seeds {len(sets[n])} | acc {acc:.3f} | side acc {np.mean([hum[k]==pr[k] for k in fb]):.3f} (n={len(fb)}) | recall {rec}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    ev() if a.eval else run(a.variant, a.seed)
