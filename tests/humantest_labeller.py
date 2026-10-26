"""Test labeller variants against Basile's human tags (work/humantest/tags.json), on the same 12-frame sheets he saw.
  python tests/humantest_labeller.py --estimate
  python tests/humantest_labeller.py --run v1a            (12 frames, 4 windows per call)
  python tests/humantest_labeller.py --run v1b            (same again: agreement test)
  python tests/humantest_labeller.py --run v2 --batch 1   (one window per call)
  python tests/humantest_labeller.py --eval               (no API: accuracy table of every run so far + old labels)"""
import argparse, base64, collections, glob, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2, numpy as np
sys.path.insert(0, ".")
D = os.environ.get("HT_DIR") or "work/humantest"; K = 12; COLS = 4
H2C = {"forehand": "forehand", "backhand": "backhand", "serve": "serve", "none": "none", "other": "other"}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["windows"], "properties": {"windows": {"type": "array", "items": {
    "type": "object", "additionalProperties": False,
    "required": ["n", "player_faces", "racket_hand", "side_in_takeback", "side_at_contact", "stroke", "confidence", "evidence"],
    "properties": {
        "n": {"type": "integer"},
        "player_faces": {"type": "string", "enum": ["toward_camera", "away_from_camera", "side_on", "unclear"]},
        "racket_hand": {"type": "string", "enum": ["player_right", "player_left", "unclear"], "description": "the hand holding the racket, the PLAYER's own"},
        "side_in_takeback": {"type": "string", "enum": ["player_right_side", "player_left_side", "centre", "no_swing", "unclear"], "description": "where the racket is when drawn back before the forward swing, on the PLAYER's own right or left side"},
        "side_at_contact": {"type": "string", "enum": ["player_right_side", "player_left_side", "centre", "no_swing", "unclear"]},
        "stroke": {"type": "string", "enum": ["forehand", "backhand", "serve", "volley_or_smash", "none", "unclear"]},
        "confidence": {"type": "integer", "enum": [1, 2, 3]},
        "evidence": {"type": "string", "description": "at most 12 words"}}}}}}
PROMPT = """Each window below is {k} frames of one video in time order (numbered 1-{k}, a fraction of a second apart), about 2-3 seconds in all. Judge the main player only. For each window:
1. player_faces: toward the camera, away from it, or side-on. Decide this first.
2. racket_hand, side_in_takeback, side_at_contact: always the PLAYER's own right and left, never the viewer's. The take-back is where the racket is when drawn back before the forward swing.
3. stroke:
   - forehand: the racket hand swings on its own side of the body (take-back and contact on the same side as the racket hand).
   - backhand: the racket crosses to the opposite side (a two-handed backhand included; a one-handed backhand has the racket arm across the body). Slice shots count as forehand or backhand by the same side rule.
   - serve: ball toss and overhead swing.
   - volley_or_smash: a short punch at the net, or an overhead hit in a rally.
   - none: no tennis stroke is being played (coach talking or walking, gesture or set-up, a swing in another sport, no real swing). A practice or shadow swing of a tennis stroke still counts as that stroke.
   - unclear: you cannot tell which stroke it is.
Answer by calling the submit tool exactly once."""


import copy
SCHEMA_R = copy.deepcopy(SCHEMA)
_it = SCHEMA_R["properties"]["windows"]["items"]
_it["required"] = ["n", "frame_notes"] + _it["required"][1:]
_it["properties"] = {"n": _it["properties"]["n"], "frame_notes": {"type": "string", "description": "one short phrase per frame, frames 1 to 12 in order, separated by ' | ': where the racket is relative to the PLAYER's own body (own right, own left, across the body, overhead, low, not visible) and what the player is doing"}, **{k: v for k, v in _it["properties"].items() if k != "n"}}
REASON = False


def frames(iid):
    im = cv2.imread(f"{D}/img/{iid}.jpg"); H, W = im.shape[:2]; h, w = H // (K // COLS), W // COLS
    out = []
    for i in range(K):
        r, c = divmod(i, COLS); f = im[r * h:(r + 1) * h, c * w:(c + 1) * w]
        out.append(base64.b64encode(cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 75])[1].tobytes()).decode())
    return out


def ask(batch, client, model):
    content = [{"type": "text", "text": PROMPT.format(k=K)}]
    for n, (iid, imgs) in enumerate(batch, 1):
        content.append({"type": "text", "text": f"Window {n}"})
        for i, im in enumerate(imgs, 1):
            content.append({"type": "text", "text": f"frame {i}"}); content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    for _ in range(3):
        try:
            r = client.messages.create(model=model, max_tokens=6000, tools=[{"name": "submit", "description": "Submit.", "input_schema": SCHEMA_R if REASON else SCHEMA}], messages=[{"role": "user", "content": content}])
        except Exception as e:
            print("  API error:", str(e)[:300], flush=True)
            if "authentication_error" in str(e):
                print("The key in this Terminal window is invalid: export the current one, then run again.", flush=True); os._exit(1)
            time.sleep(5); continue
        for blk in r.content:
            if blk.type == "tool_use":
                ws = blk.input.get("windows", [])
                if isinstance(ws, str):
                    try: ws = json.loads(ws)
                    except Exception: print("  unreadable answer, retrying", flush=True); continue
                return {w["n"]: w for w in ws if isinstance(w, dict) and 1 <= w.get("n", 0) <= len(batch)}
    return {}


LIMIT = 0


def todo_ids():
    t = json.load(open(f"{D}/tags.json"))
    ids = sorted(i for i, h in t.items() if h in H2C)  # unsure excluded
    return ids[:LIMIT] if LIMIT else ids


def run(args):
    from sphere import labelling
    ids = todo_ids(); out = f"{D}/lab_{args.run}.json"
    res = json.load(open(out)) if os.path.exists(out) else {}
    todo = [i for i in ids if i not in res]
    per = K * labelling.TOKENS_PER_IMAGE + 80
    tok = len(todo) * per + (len(todo) // args.batch + 1) * 900
    print(f"{len(todo)} windows to do, about {tok/1e6:.2f} M input tokens, roughly ${tok/1e6*3:.1f} per run (approximate)")
    if args.estimate or not todo: return
    if not os.environ.get("ANTHROPIC_API_KEY"): sys.exit("ANTHROPIC_API_KEY is not set in this Terminal window")
    client = __import__("anthropic").Anthropic(timeout=120.0, max_retries=2)
    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    def one(b):
        full = [(i, frames(i)) for i in b]; r = ask(full, client, args.model or labelling.DEFAULT_MODEL)
        return [(i, r[n]) for n, (i, _) in enumerate(full, 1) if n in r]
    done = 0
    with ThreadPoolExecutor(args.threads) as ex:
        for f in as_completed([ex.submit(one, b) for b in batches]):
            for i, v in f.result(): res[i] = v
            done += 1
            if done % 5 == 0 or done == len(batches):
                json.dump(res, open(out + ".tmp", "w")); os.replace(out + ".tmp", out); print(f"  {done}/{len(batches)}", flush=True)
    json.dump(res, open(out + ".tmp", "w")); os.replace(out + ".tmp", out); print("done", len(res))


def norm_pred(s):
    return {"forehand": "forehand", "backhand": "backhand", "serve": "serve", "none": "none", "no_stroke": "none"}.get(s, "other" if s in ("volley_or_smash", "volley", "smash", "slice", "lob", "drop_shot", "other") else s)


def ev():
    t = json.load(open(f"{D}/tags.json")); K_ = json.load(open(f"{D}/key_DO_NOT_OPEN.json"))
    ids = todo_ids(); H = {i: H2C[t[i]] for i in ids}
    sets = {"old labels (baseline)": {i: K_[i]["claude"] for i in ids}}
    for f in sorted(glob.glob(f"{D}/lab_*.json")):
        sets[os.path.basename(f)[4:-5]] = {i: v["stroke"] for i, v in json.load(open(f)).items()}
    def report(name, P, ids_):
        rows = [(H[i], norm_pred(P[i])) for i in ids_ if i in P]
        committed = [(h, p) for h, p in rows if p != "unclear"]
        acc = np.mean([h == p for h, p in committed]) if committed else 0
        fh = [(h, p) for h, p in committed if p in ("forehand", "backhand")]
        side = np.mean([h == p for h, p in fh]) if fh else 0
        pr = {c: (sum(1 for h, p in committed if p == c and h == c), sum(1 for h, p in committed if p == c)) for c in ("forehand", "backhand", "serve", "none")}
        rec = {c: (sum(1 for h, p in rows if h == c and p == c), sum(1 for h, p in rows if h == c)) for c in ("forehand", "backhand", "serve", "none")}
        f = lambda a: f"{a[0]}/{a[1]}"
        print(f"{name:26s} n={len(rows):3d} committed {len(committed):3d} acc {acc:.3f} | precision fh {f(pr['forehand'])} bh {f(pr['backhand'])} serve {f(pr['serve'])} none {f(pr['none'])} | recall fh {f(rec['forehand'])} bh {f(rec['backhand'])} serve {f(rec['serve'])} none {f(rec['none'])}")
    common = [i for i in ids if all(i in P for P in sets.values())]
    print(f"(all rows scored on the {len(common)} windows every run covers)")
    for n, P in sets.items(): report(n, P, common)
    runs = [n for n in sets if n != "old labels (baseline)"]
    if len(runs) >= 2:
        a, b = sets[runs[0]], sets[runs[1]]
        agree = {i: a[i] for i in ids if i in a and i in b and norm_pred(a[i]) == norm_pred(b[i])}
        print(f"\nagreement of {runs[0]} and {runs[1]}: {len(agree)}/{len(ids)} windows agree"); report("  agreed windows only", agree, ids)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--run"); ap.add_argument("--batch", type=int, default=4); ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--eval", action="store_true"); ap.add_argument("--model"); ap.add_argument("--limit", type=int, default=0, help="only the first N tagged windows (for a cheaper test)"); ap.add_argument("--reason", action="store_true", help="first write one note per frame, then decide")
    a = ap.parse_args()
    REASON = a.reason; LIMIT = a.limit
    if a.eval: ev()
    elif a.run: run(a)
    else: ap.print_help()
