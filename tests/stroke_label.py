"""Stroke labels for swings found in ALL tennis footage, by looking at the frames only (no title, no activity name,
no captions), so every stroke type gets labelled the same way. Swings come from the skeleton (peaks of hitting-wrist
speed), not from any activity entry.
  python tests/stroke_label.py --estimate            size of the job, calls nothing
  python tests/stroke_label.py --dry                 whole pipeline with a fake model, calls nothing
  python tests/stroke_label.py                       the real run (needs ANTHROPIC_API_KEY); safe to stop and restart
Writes work/stroke_labels.json."""
import argparse, glob, json, os, random, sys, time, base64
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, ".")
from sphere.skeleton import J
from sphere import labelling

OUT = "work/stroke_labels.json"
STROKES = ["serve", "smash", "forehand", "backhand", "volley", "slice", "drop_shot", "lob", "other"]
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["swings"], "properties": {"swings": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["n", "shown", "stroke", "grip", "view_clean", "confidence"],
    "properties": {
        "n": {"type": "integer"},
        "shown": {"type": "string", "enum": ["real_stroke", "shadow_swing", "not_a_stroke"],
                  "description": "real_stroke: the player hits (or is clearly about to hit) a ball; shadow_swing: a swing without a ball, for demonstration; not_a_stroke: anything else (walking, talking, picking up a ball, set-up, a different sport)"},
        "stroke": {"type": "string", "enum": STROKES + ["none"]},
        "grip": {"type": "string", "enum": ["one_handed", "two_handed", "not_applicable"], "description": "how the racket is held on this stroke: one or two hands on the handle (n/a for serve, smash, none)"},
        "view_clean": {"type": "boolean", "description": "one player, whole body followable, not cut off or tiny"},
        "confidence": {"type": "integer", "enum": [1, 2, 3], "description": "3 = certain, 2 = fairly sure, 1 = a guess"}}}}}}
PROMPT = """Below are {n} swings from one tennis video, each shown as {k} frames in time order (about 1.5 seconds). Name the stroke the player performs in each. Judge only what you see in the frames.

Stroke definitions:
- serve: the stroke that starts a point, the ball is tossed up and hit overhead.
- smash: an overhead hit on a ball that comes down from a lob or high ball, with no toss by the hitter.
- forehand: a full groundstroke on the dominant side of the body.
- backhand: a full groundstroke on the non-dominant side, one or two hands on the racket.
- volley: a short punch at the ball before it bounces, usually near the net, little backswing.
- slice: a groundstroke or approach shot with a high-to-low cutting swing and an open racket face (not a volley, not a drop shot).
- drop_shot: a slice or touch shot played softly to land just over the net.
- lob: a stroke that lifts the ball high over an opponent.
- other: a tennis stroke that is none of these (for example a return of serve you cannot class, a half-volley, a tweener).
Use stroke 'none' when the frames show no stroke. For shadow swings (no ball) name the stroke being imitated. Answer by calling the submit_swings tool exactly once."""


def swings(npz, per_clip, rng):
    d = np.load(npz, allow_pickle=True)
    P, fps = gaussian_filter1d(d["pose"], 1.5, axis=0, mode="nearest"), float(d["fps"])
    if len(P) < 3 * fps:
        return []
    ms = (P[:, J["l_shoulder"]] + P[:, J["r_shoulder"]]) / 2; mh = (P[:, J["l_hip"]] + P[:, J["r_hip"]]) / 2
    torso = float(np.median(np.linalg.norm(ms - mh, axis=1))) or 0.5
    sp = np.stack([gaussian_filter1d(np.linalg.norm(np.gradient(P[:, J[f"{s}_wrist"]], axis=0), axis=1) * fps / torso, 2) for s in "lr"]).max(0)
    top = np.percentile(sp, 99)
    pk, _ = find_peaks(sp, height=max(3.0, 0.35 * top), distance=int(1.5 * fps))
    pk = list(pk)
    rng.shuffle(pk)
    out = [(max(0, p / fps - 0.9), p / fps + 0.6, p / fps) for p in sorted(pk[:per_clip])]
    return out


def jobs(args):
    rng = random.Random(0)
    byact = {}
    for adir in sorted(glob.glob("work/tennis_*")):
        act = os.path.basename(adir)
        if act == "tennis_live" or not os.path.isdir(adir + "/clips"):
            continue
        L = []
        for f in sorted(glob.glob(adir + "/clips/*.npz")):
            vid = os.path.basename(f)[:-4]
            v = labelling.video_file(adir + "/videos", vid)
            if not v:
                continue
            for a, b, p in swings(f, args.per_clip, rng):
                L.append((act, vid, v, a, b, p))
        rng.shuffle(L)
        byact[act] = L[: args.cap]
    return byact


def key(act, vid, p):
    return f"{act}/{vid}/{p:.2f}"


def ask(batch, client, model):
    content = [{"type": "text", "text": PROMPT.format(n=len(batch), k=labelling.FRAMES)}]
    for n, (act, vid, v, a, b, p, imgs) in enumerate(batch, 1):
        content.append({"type": "text", "text": f"Swing {n}"})
        for im in imgs:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    for _ in range(3):
        try:
            r = client.messages.create(model=model, max_tokens=2000, tools=[{"name": "submit_swings", "description": "Submit.", "input_schema": SCHEMA}],
                                       messages=[{"role": "user", "content": content}])
        except Exception as e:
            time.sleep(5); continue
        for blk in r.content:
            if blk.type == "tool_use":
                return {s["n"]: s for s in blk.input.get("swings", []) if 1 <= s.get("n", 0) <= len(batch)}
    return {}


class Fake:
    class messages:
        @staticmethod
        def create(**kw):
            class B: type = "tool_use"; input = {"swings": [{"n": i + 1, "shown": "real_stroke", "stroke": "forehand", "grip": "one_handed", "view_clean": True, "confidence": 2} for i in range(6)]}
            class R: content = [B]
            return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-clip", type=int, default=5); ap.add_argument("--cap", type=int, default=450)
    ap.add_argument("--batch", type=int, default=5); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--dry", action="store_true")
    ap.add_argument("--model", default=labelling.DEFAULT_MODEL)
    args = ap.parse_args()
    byact = jobs(args)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [j for act, L in byact.items() for j in L if key(j[0], j[1], j[5]) not in res]
    tot = sum(len(L) for L in byact.values())
    print({a: len(L) for a, L in byact.items()}, "| swings", tot, "| still to label", len(todo))
    tok = len(todo) * (labelling.FRAMES * labelling.TOKENS_PER_IMAGE + 30) + (len(todo) // args.batch + 1) * 600
    print(f"estimate: about {tok/1e6:.1f} M input tokens, {len(todo)//args.batch+1} calls "
          f"(roughly ${tok/1e6*3:.0f} at $3 per million input tokens, approximate; output is small)")
    if args.estimate or not todo:
        return
    client = Fake() if args.dry else __import__("anthropic").Anthropic(timeout=120.0, max_retries=2)
    if args.dry:
        todo = todo[:12]
    groups = {}
    for j in todo:
        groups.setdefault((j[0], j[1]), []).append(j)
    batches = [g[i:i + args.batch] for g in groups.values() for i in range(0, len(g), args.batch)]

    def one(b):
        full = []
        for act, vid, v, a, bb, p in b:
            imgs, _ = labelling.grab_frames(v, a, bb)
            if len(imgs) >= 4:
                full.append((act, vid, v, a, bb, p, imgs))
        if not full:
            return []
        r = ask(full, client, args.model)
        return [(key(f[0], f[1], f[5]), dict(window=[round(f[3], 2), round(f[4], 2)], peak=round(f[5], 2), **r[n])) for n, f in enumerate(full, 1) if n in r]

    done = 0
    with ThreadPoolExecutor(args.threads) as ex:
        futs = [ex.submit(one, b) for b in batches]
        for f in as_completed(futs):
            for k, v in f.result():
                res[k] = v
            done += 1
            if done % 10 == 0 or done == len(futs):
                json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
                print(f"  {done}/{len(futs)} batches, {len(res)} swings labelled", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
    import collections
    print(collections.Counter(v["stroke"] for v in res.values()))


main()
