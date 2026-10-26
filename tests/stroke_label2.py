"""Stroke labels v2: windows that contain the whole stroke, 8 frames, and observable yes/no questions answered first,
so the stroke call rests on what is visible. Frames only: no title, no activity name, no captions.
Swing windows come from two skeleton detectors (not from any activity entry):
  overhead events: a wrist reaches well above the head (serve, smash)      window -2.2 s .. +0.8 s
  swing events:    peaks of wrist speed away from the overhead events       window -1.3 s .. +0.9 s
  python tests/stroke_label2.py --estimate | --dry | (real run, needs ANTHROPIC_API_KEY; safe to stop and restart)
Writes work/stroke_labels2.json."""
import argparse, glob, json, os, random, sys, time, collections
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
sys.path.insert(0, ".")
from sphere.skeleton import J
from sphere import labelling

OUT = "work/stroke_labels2.json"
K = 8
STROKES = ["serve", "smash", "forehand", "backhand", "volley", "slice", "drop_shot", "lob", "other"]
YNU = {"type": "string", "enum": ["yes", "no", "unclear"]}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["swings"], "properties": {"swings": {"type": "array", "items": {
    "type": "object", "additionalProperties": False,
    "required": ["n", "ball_toss_seen", "hit_above_head", "ball_bounced_before_hit", "two_hands_on_racket", "contact_in_frames", "shown", "stroke", "grip", "view_clean", "confidence", "evidence"],
    "properties": {
        "n": {"type": "integer"},
        "ball_toss_seen": dict(YNU, description="the player throws the ball up with the free hand to hit it"),
        "hit_above_head": dict(YNU, description="the racket meets the ball with the arm stretched up, above the head"),
        "ball_bounced_before_hit": dict(YNU, description="the ball bounces on the court before the player hits it"),
        "two_hands_on_racket": dict(YNU, description="both hands are on the racket handle during the swing"),
        "contact_in_frames": dict(YNU, description="the moment of contact (or the complete swing for a shadow swing) is inside these frames"),
        "shown": {"type": "string", "enum": ["real_stroke", "shadow_swing", "not_a_stroke"],
                  "description": "real_stroke: the player hits a ball; shadow_swing: a swing without a ball; not_a_stroke: anything else (walking, talking, picking up or bouncing a ball, set-up, another sport)"},
        "stroke": {"type": "string", "enum": STROKES + ["none"]},
        "grip": {"type": "string", "enum": ["one_handed", "two_handed", "not_applicable"]},
        "view_clean": {"type": "boolean", "description": "one player, whole body followable, not cut off or tiny"},
        "confidence": {"type": "integer", "enum": [1, 2, 3], "description": "3 = certain, 2 = fairly sure, 1 = a guess"},
        "evidence": {"type": "string", "description": "at most 15 words: what in the frames decides the stroke"}}}}}}
PROMPT = """Below are {n} windows from one tennis video, each shown as {k} frames in time order (about 3 seconds). Each window is meant to contain one stroke, but it may instead show a pause, a ball bounce, a rally shot of another player, or a different movement.

For each window first answer the yes/no questions from the frames, then name the stroke. Judge only what you see. If the contact is not visible, say so (contact_in_frames: no) and name the stroke only if the preparation makes it certain.

Stroke definitions:
- serve: starts a point; the ball is tossed up and hit overhead.
- smash: an overhead hit on a ball coming down from a lob or high ball, no toss by the hitter.
- forehand: a full groundstroke on the dominant side of the body, after the ball has bounced.
- backhand: a full groundstroke on the non-dominant side, with one or two hands on the racket, after the bounce.
- volley: a short punch at the ball before it bounces, usually near the net, little backswing.
- slice: a groundstroke or approach shot with a high-to-low cutting swing and open racket face.
- drop_shot: a soft touch shot meant to land just over the net.
- lob: a stroke that lifts the ball high over an opponent.
- other: a tennis stroke that is none of these (half-volley, tweener, a return you cannot class).
Use 'none' when no stroke is shown. For shadow swings (no ball) name the stroke being imitated. Answer by calling the submit_swings tool exactly once."""


def events(npz, n_over, n_swing, rng):
    d = np.load(npz, allow_pickle=True)
    P, fps = gaussian_filter1d(d["pose"], 1.5, axis=0, mode="nearest"), float(d["fps"])
    if len(P) < 4 * fps:
        return []
    ms = (P[:, J["l_shoulder"]] + P[:, J["r_shoulder"]]) / 2; mh = (P[:, J["l_hip"]] + P[:, J["r_hip"]]) / 2
    torso = float(np.median(np.linalg.norm(ms - mh, axis=1))) or 0.5
    nose = P[:, J["nose"]]
    up = np.stack([(P[:, J[f"{s}_wrist"], 1] - nose[:, 1]) / torso for s in "lr"]).max(0)
    sp = np.stack([gaussian_filter1d(np.linalg.norm(np.gradient(P[:, J[f"{s}_wrist"]], axis=0), axis=1) * fps / torso, 2) for s in "lr"]).max(0)
    ov, _ = find_peaks(gaussian_filter1d(up, 2), height=0.45, distance=int(3.0 * fps))
    ov = list(ov); rng.shuffle(ov); ov = sorted(ov[:n_over])
    top = np.percentile(sp, 99)
    pk, _ = find_peaks(sp, height=max(3.0, 0.35 * top), distance=int(1.5 * fps))
    pk = [p for p in pk if all(abs(p - o) > 1.5 * fps for o in ov) and up[p] < 0.45]
    rng.shuffle(pk); pk = sorted(pk[:n_swing])
    return [("over", max(0, o / fps - 2.2), o / fps + 0.8, o / fps) for o in ov] + [("swing", max(0, p / fps - 1.3), p / fps + 0.9, p / fps) for p in pk]


def jobs(args):
    rng = random.Random(0)
    byact = {}
    for adir in sorted(glob.glob("work/tennis_*")):
        act = os.path.basename(adir)
        if act == "tennis_live" or not os.path.isdir(adir + "/clips") or (args.acts and act not in args.acts.split(",")):
            continue
        L = []
        for f in sorted(glob.glob(adir + "/clips/*.npz")):
            vid = os.path.basename(f)[:-4]
            v = labelling.video_file(adir + "/videos", vid)
            if not v or (args.new_hours and time.time() - os.path.getmtime(v) > args.new_hours * 3600):
                continue
            for kind, a, b, p in events(f, args.over_per_clip, args.swing_per_clip, random.Random(vid)):   # same windows every run, whatever else is selected
                L.append((act, vid, v, a, b, p, kind))
        rng.shuffle(L)
        byact[act] = L[: args.cap]
    return byact


def key(act, vid, p, kind):
    return f"{act}/{vid}/{kind}/{p:.2f}"


def ask(batch, client, model):
    content = [{"type": "text", "text": PROMPT.format(n=len(batch), k=K)}]
    for n, b in enumerate(batch, 1):
        content.append({"type": "text", "text": f"Window {n}"})
        for im in b[-1]:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    for _ in range(3):
        try:
            r = client.messages.create(model=model, max_tokens=3000, tools=[{"name": "submit_swings", "description": "Submit.", "input_schema": SCHEMA}],
                                       messages=[{"role": "user", "content": content}])
        except Exception:
            time.sleep(5); continue
        for blk in r.content:
            if blk.type == "tool_use":
                return {s["n"]: s for s in blk.input.get("swings", []) if 1 <= s.get("n", 0) <= len(batch)}
    return {}


class Fake:
    class messages:
        @staticmethod
        def create(**kw):
            class B:
                type = "tool_use"
                input = {"swings": [dict(n=i + 1, ball_toss_seen="no", hit_above_head="no", ball_bounced_before_hit="yes", two_hands_on_racket="no", contact_in_frames="yes",
                                          shown="real_stroke", stroke="forehand", grip="one_handed", view_clean=True, confidence=2, evidence="fake") for i in range(6)]}
            class R: content = [B]
            return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--over-per-clip", type=int, default=2); ap.add_argument("--swing-per-clip", type=int, default=3)
    ap.add_argument("--cap", type=int, default=420); ap.add_argument("--batch", type=int, default=4); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--acts", default="", help="comma list of activity folders to mine (default all), e.g. tennis_backhand,tennis_volley")
    ap.add_argument("--new-hours", type=float, default=0, help="only videos downloaded in the last N hours (e.g. 14 for today's new footage)")
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--dry", action="store_true")
    ap.add_argument("--model", default=labelling.DEFAULT_MODEL)
    args = ap.parse_args()
    byact = jobs(args)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [j for L in byact.values() for j in L if key(j[0], j[1], j[5], j[6]) not in res]
    print({a: len(L) for a, L in byact.items()}, "| windows", sum(len(L) for L in byact.values()), "| still to label", len(todo),
          "| overhead events", sum(1 for j in todo if j[6] == "over"))
    tok = len(todo) * (K * labelling.TOKENS_PER_IMAGE + 40) + (len(todo) // args.batch + 1) * 700 + len(todo) * 120
    print(f"estimate: about {tok/1e6:.1f} M input tokens in {len(todo)//args.batch+1} calls (roughly ${tok/1e6*3:.0f} at $3 per million input tokens, approximate); output about {len(todo)*110/1e6:.2f} M tokens")
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
        for act, vid, v, a, bb, p, kind in b:
            imgs, _ = labelling.grab_frames(v, a, bb, k=K)
            if len(imgs) >= 6:
                full.append((act, vid, v, a, bb, p, kind, imgs))
        if not full:
            return []
        r = ask(full, client, args.model)
        return [(key(f[0], f[1], f[5], f[6]), dict(window=[round(f[3], 2), round(f[4], 2)], peak=round(f[5], 2), kind=f[6], **r[n])) for n, f in enumerate(full, 1) if n in r]

    done = 0
    with ThreadPoolExecutor(args.threads) as ex:
        futs = [ex.submit(one, b) for b in batches]
        for f in as_completed(futs):
            for k, v in f.result():
                res[k] = v
            done += 1
            if done % 10 == 0 or done == len(futs):
                json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
                print(f"  {done}/{len(futs)} batches, {len(res)} windows labelled", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
    print(collections.Counter(v["stroke"] for v in res.values()))


main()
