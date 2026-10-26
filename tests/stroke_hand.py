"""Which hand holds the racket? One small call per video: 3 frames taken at labelled strokes, the model says which of the
player's own hands (left or right) holds the racket. Gives each clip a handedness to train with, and a test of the
skeleton-only guess. Frames only. Writes work/stroke_hands.json.
  python tests/stroke_hand.py --estimate | (real run, needs ANTHROPIC_API_KEY; safe to stop and restart)"""
import argparse, json, os, sys, time, collections, random
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, ".")
from sphere import labelling

OUT = "work/stroke_hands.json"
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["frames"], "properties": {"frames": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["n", "racket_hand", "one_player"],
    "properties": {"n": {"type": "integer"},
                   "racket_hand": {"type": "string", "enum": ["player_right", "player_left", "unclear"],
                                   "description": "which of the PLAYER'S OWN hands holds the racket handle (their right hand or their left hand, not the side of the picture). When the player faces the camera, their right hand is on the left of the picture. If both hands hold it, say which hand is lower on the handle (the hand at the bottom of the grip is the dominant hand)"},
                   "one_player": {"type": "boolean", "description": "exactly one player is clearly the person hitting"}}}}}}
PROMPT = "Below are {n} frames from one tennis video, each showing a player who is playing or about to play a stroke. For each frame say which of the player's own hands (their right or their left) holds the racket, as described in the tool. Answer by calling submit_hands exactly once."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--model", default=labelling.DEFAULT_MODEL)
    args = ap.parse_args()
    lab = json.load(open("work/stroke_labels2.json"))
    by = collections.defaultdict(list)
    for k, v in lab.items():
        a, vid = k.split("/")[:2]
        if v.get("stroke") in ("forehand", "backhand", "serve") and v.get("confidence", 0) >= 2 and v.get("view_clean"):
            by[(a, vid)].append(v["peak"])
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = []
    for (a, vid), ps in by.items():
        if f"{a}/{vid}" in res:
            continue
        v = labelling.video_file(f"work/{a}/videos", vid)
        if v:
            random.Random(vid).shuffle(ps)
            todo.append((a, vid, v, sorted(ps[:3])))
    tok = len(todo) * (3 * labelling.TOKENS_PER_IMAGE + 250)
    print(f"{len(todo)} videos still to check | about {tok/1e6:.2f} M input tokens (roughly ${tok/1e6*3:.1f}, approximate)")
    if args.estimate or not todo:
        return
    import anthropic
    client = anthropic.Anthropic(timeout=90.0, max_retries=2)

    def one(j):
        a, vid, v, ps = j
        imgs = []
        for p in ps:
            im, _ = labelling.grab_frames(v, p, p, k=1, width=640)
            imgs += im
        if not imgs:
            return None
        content = [{"type": "text", "text": PROMPT.format(n=len(imgs))}] + [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": i}} for i in imgs]
        for _ in range(3):
            try:
                r = client.messages.create(model=args.model, max_tokens=500, tools=[{"name": "submit_hands", "description": "Submit.", "input_schema": SCHEMA}],
                                           messages=[{"role": "user", "content": content}])
            except Exception:
                time.sleep(5); continue
            for b in r.content:
                if b.type == "tool_use":
                    return f"{a}/{vid}", b.input.get("frames", [])
        return None

    done = 0
    with ThreadPoolExecutor(args.threads) as ex:
        futs = [ex.submit(one, j) for j in todo]
        for f in as_completed(futs):
            r = f.result()
            if r:
                res[r[0]] = r[1]
            done += 1
            if done % 20 == 0 or done == len(futs):
                json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
                print(f"  {done}/{len(futs)} videos", flush=True)
    json.dump(res, open(OUT + ".tmp", "w")); os.replace(OUT + ".tmp", OUT)
    c = collections.Counter()
    for fr in res.values():
        v = collections.Counter(x["racket_hand"] for x in fr if x["racket_hand"] != "unclear")
        c[v.most_common(1)[0][0] if v else "unclear"] += 1
    print(dict(c))


main()
