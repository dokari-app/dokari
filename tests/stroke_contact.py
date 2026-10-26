"""Pilot: for forehand/backhand windows already labelled, ask which frame shows contact, which hand swings, and re-judge the stroke.
  python tests/stroke_contact.py --estimate | (real run, needs ANTHROPIC_API_KEY; safe to stop and restart)
Writes work/stroke_contact_pilot.json (key = same key as stroke_labels2.json)."""
import argparse, json, os, random, sys, time, collections
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, ".")
from sphere import labelling

OUT = "work/stroke_contact_pilot.json"
K = 8
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["windows"], "properties": {"windows": {"type": "array", "items": {
    "type": "object", "additionalProperties": False,
    "required": ["n", "contact_frame", "swinging_hand", "other_hand_on_racket", "racket_side_at_contact", "stroke", "confidence", "evidence"],
    "properties": {
        "n": {"type": "integer"},
        "contact_frame": {"type": "integer", "enum": list(range(0, K + 1)), "description": "number (1-8) of the frame closest to the moment the racket meets the ball; 0 if the contact is not visible in any frame"},
        "swinging_hand": {"type": "string", "enum": ["player_right", "player_left", "unclear"], "description": "the hand that holds the racket at contact, as the PLAYER's own right or left hand (not the viewer's)"},
        "other_hand_on_racket": {"type": "string", "enum": ["yes", "no", "unclear"]},
        "racket_side_at_contact": {"type": "string", "enum": ["player_right_side", "player_left_side", "centre", "unclear"], "description": "at contact the racket is on the player's own right side or left side of the body (the player's, not the viewer's)"},
        "stroke": {"type": "string", "enum": ["forehand", "backhand", "serve", "volley", "other", "none"]},
        "confidence": {"type": "integer", "enum": [1, 2, 3]},
        "evidence": {"type": "string", "description": "at most 12 words"}}}}}}
PROMPT = """Below are {n} windows from one tennis video, each shown as {k} frames in time order (numbered from 1, about 0.3 s apart, {k} frames). For each window answer from the frames only:
- contact_frame: which frame is closest to the instant the racket meets the ball (0 if no frame shows it);
- swinging_hand and racket_side_at_contact: use the PLAYER's own right and left, not the viewer's. Think about which way the player faces (toward or away from the camera) before deciding;
- other_hand_on_racket: is the second hand on the handle at contact;
- stroke: forehand (racket on the hitting hand's own side), backhand (racket across on the opposite side), serve, volley, other, or none.
Answer by calling the submit tool exactly once."""


def ask(batch, client, model):
    content = [{"type": "text", "text": PROMPT.format(n=len(batch), k="up to 8")}]
    for n, b in enumerate(batch, 1):
        content.append({"type": "text", "text": f"Window {n}"})
        for i, im in enumerate(b["imgs"], 1):
            content.append({"type": "text", "text": f"frame {i}"})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    for _ in range(3):
        try:
            r = client.messages.create(model=model, max_tokens=2500, tools=[{"name": "submit", "description": "Submit.", "input_schema": SCHEMA}], messages=[{"role": "user", "content": content}])
        except Exception as e:
            print('  API error:', str(e)[:300], flush=True)
            if 'authentication_error' in str(e):
                print('The key in this Terminal window is invalid or revoked: set the current one with the export line, then run again.', flush=True); os._exit(1)
            time.sleep(5); continue
        for blk in r.content:
            if blk.type == "tool_use":
                return {w["n"]: w for w in blk.input.get("windows", []) if 1 <= w.get("n", 0) <= len(batch)}
        print('  no tool answer; stop reason:', r.stop_reason, flush=True)
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=75); ap.add_argument("--batch", type=int, default=4); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--all", action="store_true", help="every window labelled forehand/backhand/volley/slice/smash/lob/other (not serve, not none) -> work/stroke_contact_all.json")
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--model", default=labelling.DEFAULT_MODEL)
    args = ap.parse_args()
    global OUT
    lab = json.load(open("work/stroke_labels2.json"))
    if args.all:
        pilot = json.load(open(OUT)) if os.path.exists(OUT) else {}
        OUT = "work/stroke_contact_all.json"
        res = json.load(open(OUT)) if os.path.exists(OUT) else {}
        for k, v in pilot.items():
            res.setdefault(k, v)
    else:
        res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    pool = {"forehand": [], "backhand": []}
    if args.all:
        pool = {c: [] for c in ("forehand", "backhand", "volley", "slice", "smash", "lob", "other")}
    for k, v in lab.items():
        ok = v.get("stroke") in pool and (args.all or (v.get("contact_in_frames") == "yes" and v.get("confidence", 0) >= 2 and v.get("view_clean") and v.get("hit_above_head") != "yes"))
        if ok:
            act, vid = k.split("/")[:2]
            vf = labelling.video_file(f"work/{act}/videos", vid)
            if vf:
                pool[v["stroke"]].append((k, vf, v["window"]))
    rng = random.Random(5)
    sel = []
    for c, L in pool.items():
        rng.shuffle(L); sel += L if args.all else L[:args.per_class]
    todo = [s for s in sel if s[0] not in res]
    tok = len(todo) * (K * labelling.TOKENS_PER_IMAGE + 60) + (len(todo) // args.batch + 1) * 600
    print(f"pool {({c: len(L) for c, L in pool.items()})} | selected {len(sel)} | to do {len(todo)} | about {tok/1e6:.2f} M input tokens, roughly ${tok/1e6*3:.1f} (approximate)")
    if args.estimate or not todo:
        return
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set in this Terminal window: run the export line first")
    client = __import__("anthropic").Anthropic(timeout=120.0, max_retries=2)
    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]

    def one(b):
        full = []
        for k, vf, w in b:
            imgs, times = labelling.grab_frames(vf, w[0], w[1], k=K)
            if len(imgs) >= 6:
                full.append(dict(k=k, imgs=imgs, times=times, window=w))
        if len(full) < len(b):
            print('  frames missing for', len(b) - len(full), 'of', len(b), 'windows (video not readable?)', flush=True)
        if not full:
            return []
        r = ask(full, client, args.model)
        return [(f["k"], dict(times=f["times"], **r[n])) for n, f in enumerate(full, 1) if n in r]

    done = 0
    with ThreadPoolExecutor(args.threads) as ex:
        for f in as_completed([ex.submit(one, b) for b in batches]):
            for k, v in f.result():
                res[k] = v
            done += 1
            if done % 5 == 0 or done == len(batches):
                json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
                print(f"  {done}/{len(batches)} batches, {len(res)} windows", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
    print("done", len(res))


if __name__ == "__main__":
    main()
