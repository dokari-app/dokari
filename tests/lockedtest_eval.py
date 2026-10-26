"""Score every recogniser on the LOCKED test set (Basile's blind tags on held-out videos).  python tests/lockedtest_eval.py
Reports, for the representative subset, the diagnostic subset and both: 4-class accuracy with a 95% interval (bootstrap over source videos),
per-class precision/recall, confusion matrix, forehand-vs-backhand side accuracy; and the hybrid gate (skeleton + cloud) with coverage."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, ".")
from sphere.stroke_cloud import gate, CLASSES
D = "work/locked"; NAMES = ["forehand", "backhand", "serve", "no_stroke"]
H = {"forehand": "forehand", "backhand": "backhand", "serve": "serve", "none": "no_stroke"}


def cloud_to_cls(s): return {"none": "no_stroke", "volley_or_smash": "other"}.get(s, s)


def main():
    tags = json.load(open(f"{D}/tags.json")); key = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    ids = [i for i, h in tags.items() if h in H and i in key]; truth = {i: H[tags[i]] for i in ids}
    n_other = sum(1 for h in tags.values() if h == "other"); n_uns = sum(1 for h in tags.values() if h == "unsure")
    print(f"locked set: {len(tags)} tagged | scored on {len(ids)} (forehand/backhand/serve/none); excluded: {n_other} 'other' (volley/smash), {n_uns} 'unsure'")
    rec = {}
    if os.path.exists(f"{D}/skel_preds.json"):
        sk = json.load(open(f"{D}/skel_preds.json")); rec["skeleton"] = {i: NAMES[int(np.argmax(sk[i]))] for i in ids if i in sk}
    clouds = {}
    for f in sorted(glob.glob(f"{D}/lab_*.json")):
        L = json.load(open(f)); nm = os.path.basename(f)[4:-5]; clouds[nm] = L
        rec["cloud " + nm] = {i: cloud_to_cls(L[i]["stroke"]) for i in ids if i in L and L[i]["stroke"] != "unclear"}
    rng = np.random.RandomState(0)
    def ci(ii, pred):
        vids = sorted({key[i]["vid"] for i in ii}); by = {v: [i for i in ii if key[i]["vid"] == v] for v in vids}; acc = []
        for _ in range(1000):
            s = [i for v in rng.choice(vids, len(vids)) for i in by[v]]; acc.append(np.mean([truth[i] == pred[i] for i in s]))
        return np.percentile(acc, [2.5, 97.5])
    def report(name, pred, subset, label):
        ii = [i for i in ids if i in pred and (subset is None or key[i]["subset"] == subset)]
        if len(ii) < 5: return
        acc = np.mean([truth[i] == pred[i] for i in ii]); lo, hi = ci(ii, pred)
        fb = [i for i in ii if truth[i] in ("forehand", "backhand") and pred[i] in ("forehand", "backhand")]
        side = np.mean([truth[i] == pred[i] for i in fb]) if fb else float("nan")
        pr = " ".join(f"{c[:2]} {sum(1 for i in ii if pred[i]==c and truth[i]==c)}/{sum(1 for i in ii if pred[i]==c)}" for c in NAMES)
        rc = " ".join(f"{c[:2]} {sum(1 for i in ii if truth[i]==c and pred[i]==c)}/{sum(1 for i in ii if truth[i]==c)}" for c in NAMES)
        print(f"  {name:16s} [{label}] n={len(ii):3d} acc {acc:.3f} (95% {lo:.2f}-{hi:.2f}) | side acc {side:.3f} (n={len(fb)}) | precision {pr} | recall {rc}")
    for label, subset in (("representative", "rep"), ("diagnostic", "diag"), ("all", None)):
        print(f"\n{label}:")
        for nm, pred in rec.items(): report(nm, pred, subset, label[:4])
    if "skeleton" in rec:
        print("\nconfusion, skeleton (rows = your tag, cols = skeleton):", NAMES)
        for c in NAMES: print(f"  {c:10s}", [sum(1 for i in rec['skeleton'] if truth.get(i) == c and rec['skeleton'][i] == d) for d in NAMES])
        print("\nhybrid gate (skeleton confident -> skeleton; else a confident cloud answer; else silent):")
        for nm, L in clouds.items():
            for th in (0.6, 0.7, 0.8):
                got = {}
                for i in ids:
                    if i not in sk or i not in L: continue
                    lab, src = gate(sk[i], L[i], skel_accept=th)
                    if lab is not None and lab != "other": got[i] = lab
                if got:
                    acc = np.mean([truth[i] == got[i] for i in got]); lo, hi = ci(list(got), got)
                    fb = [i for i in got if truth[i] in ("forehand", "backhand") and got[i] in ("forehand", "backhand")]
                    print(f"  skeleton>={th} + {nm}: answers {len(got)/len(ids):.0%} of windows, acc {acc:.3f} (95% {lo:.2f}-{hi:.2f}), side acc {np.mean([truth[i]==got[i] for i in fb]):.3f}")


if __name__ == "__main__":
    main()
