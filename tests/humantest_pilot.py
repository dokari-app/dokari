"""Pilot: do better labels help the network?  Relabel ~600 training windows with the v2 labeller (12 frames, one window per call),
then train two networks of the same size on the same windows, one with the old labels and one with the v2 labels, and score both on Basile's human tags.
  python tests/humantest_pilot.py --estimate
  python tests/humantest_pilot.py --label        (needs ANTHROPIC_API_KEY; safe to stop and restart)
  python tests/humantest_pilot.py --train old --seed 0 | --train new --seed 0
  python tests/humantest_pilot.py --eval"""
import argparse, base64, glob, json, os, sys, types, random
os.environ.setdefault("PRE", "2.4")
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, ".")
import numpy as np
D = "work/humantest"; OUT = "work/pilot_v2.json"; N = int(os.environ.get("PILOT_N", "600")); K = 12; W = 480
import humantest_labeller as hl


def pilot_rows():
    import stroke_net as sn
    key = json.load(open(f"{D}/key_DO_NOT_OPEN.json")); test_keys = {v["key"] for v in key.values()}
    rows = [r for r in sn.build() if r["k"] not in test_keys]
    random.Random(11).shuffle(rows)
    return sn, rows[:N]


def grab(vf, w):
    import cv2
    cap = cv2.VideoCapture(vf); out = []
    for i in range(K):
        t = w[0] + (w[1] - w[0]) * i / (K - 1); cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * t); ok, f = cap.read()
        if not ok: cap.release(); return None
        h, ww = f.shape[:2]; f = cv2.resize(f, (W, int(h * W / ww)), interpolation=cv2.INTER_AREA)
        out.append(base64.b64encode(cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 75])[1].tobytes()).decode())
    cap.release(); return out


def label(args):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from sphere import labelling
    sn, rows = pilot_rows(); res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [r for r in rows if r["k"] not in res]
    tok = len(todo) * (K * labelling.TOKENS_PER_IMAGE + 80) + len(todo) * 900
    print(f"{len(todo)} windows to do, about {tok/1e6:.2f} M input tokens, roughly ${tok/1e6*3:.1f} (approximate)")
    if args.estimate or not todo: return
    if not os.environ.get("ANTHROPIC_API_KEY"): sys.exit("ANTHROPIC_API_KEY is not set in this Terminal window")
    client = __import__("anthropic").Anthropic(timeout=120.0, max_retries=2)
    def one(r):
        act, vid = r["k"].split("/")[:2]; vf = labelling.video_file(f"work/{act}/videos", vid)
        if not vf: return None
        im = grab(vf, sn.LAB[r["k"]]["window"])
        if im is None: return None
        a = hl.ask([(r["k"], im)], client, labelling.DEFAULT_MODEL)
        return (r["k"], a[1]) if 1 in a else None
    done = 0
    with ThreadPoolExecutor(4) as ex:
        for f in as_completed([ex.submit(one, r) for r in todo]):
            v = f.result(); done += 1
            if v: res[v[0]] = v[1]
            if done % 10 == 0 or done == len(todo):
                json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT); print(f"  {done}/{len(todo)}", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT); print("done", len(res))


NEW = {"forehand": "forehand", "backhand": "backhand", "serve": "serve", "none": "no_stroke"}


def train(which, seed):
    import torch
    sn, rows = pilot_rows(); sn.CHAN, sn.ARCH = "3d", "conv"; torch.manual_seed(seed); np.random.seed(seed)
    lab = json.load(open(OUT)); args = types.SimpleNamespace(hand="none", epochs=60)
    pr = []
    for r in rows:
        v = lab.get(r["k"])
        if not v or v["stroke"] not in NEW: continue          # same windows for both label sets
        r2 = dict(r)
        if which == "new": r2["y"] = sn.CLASSES.index(NEW[v["stroke"]])
        pr.append(r2)
    allrows = sn.build(); vids = sorted({r["vid"] for r in allrows}); rng = np.random.RandomState(0); rng.shuffle(vids); fold = {v: i % 5 for i, v in enumerate(vids)}
    key = json.load(open(f"{D}/key_DO_NOT_OPEN.json")); tags = json.load(open(f"{D}/tags.json")); hk = {key[i]["key"] for i, h in tags.items() if h in ("forehand", "backhand", "serve", "none")}
    P = {}
    for f in range(5):
        tr = [r for r in pr if fold[r["vid"]] != f]; te = [r for r in allrows if fold[r["vid"]] == f and r["k"] in hk]
        if te: p = sn.fit_predict(tr, te, args); P.update({r["k"]: p[i].tolist() for i, r in enumerate(te)})
        print(f"  fold {f + 1}/5 trained on {len(tr)}", flush=True)
    json.dump(dict(P=P, n=len(pr)), open(f"{D}/pilot_{which}_s{seed}.json", "w"))


def ev():
    tags = json.load(open(f"{D}/tags.json")); key = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    H = {"forehand": 0, "backhand": 1, "serve": 2, "none": 3}; hum = {key[i]["key"]: H[h] for i, h in tags.items() if h in H}
    pred = {}
    for w in ("old", "new"):
        R = [json.load(open(f)) for f in sorted(glob.glob(f"{D}/pilot_{w}_s*.json"))]
        if not R: continue
        ks = set.intersection(*[set(r["P"]) for r in R]); pred[w] = {k: int(np.argmax(np.mean([r["P"][k] for r in R], 0))) for k in ks}
        ks = [k for k in pred[w] if k in hum]; acc = np.mean([hum[k] == pred[w][k] for k in ks])
        fb = [k for k in ks if hum[k] in (0, 1) and pred[w][k] in (0, 1)]; side = np.mean([hum[k] == pred[w][k] for k in fb])
        rec = {c: f"{sum(1 for k in ks if hum[k]==i and pred[w][k]==i)}/{sum(1 for k in ks if hum[k]==i)}" for i, c in enumerate(["fh", "bh", "serve", "none"])}
        print(f"{w:4s} labels | seeds {len(R)} | trained on ~{R[0]['n']*4//5} windows | scored {len(ks)} human windows | acc {acc:.3f} | side acc {side:.3f} (n={len(fb)}) | recall {rec}")
    if len(pred) == 2:
        both = [k for k in pred["old"] if k in pred["new"] and k in hum]
        d = np.mean([hum[k] == pred["new"][k] for k in both]) - np.mean([hum[k] == pred["old"][k] for k in both])
        print(f"new minus old on the same {len(both)} windows: {d:+.3f} accuracy (decision rule: continue to the full relabel only if this is at least +0.07)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--label", action="store_true"); ap.add_argument("--estimate", action="store_true"); ap.add_argument("--train"); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--eval", action="store_true"); a = ap.parse_args()
    if a.label or a.estimate: label(a)
    elif a.train: train(a.train, a.seed)
    elif a.eval: ev()
