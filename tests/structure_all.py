"""Adds the structure of every labelled video (talking / wrong demo / right demo / play) to the labels of an activity, WITHOUT re-judging the swings.
  python tests/structure_all.py [--activity tennis_forehand]
Saves after every video (stop and rerun any time); a backup of labels.json is kept as labels.before_structure.json. Adds lab["structure"][clip] and a "segment" to every attempt."""
import argparse, json, os, sys, shutil, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import labelling as L, knowledge as K
ap = argparse.ArgumentParser(); ap.add_argument("--activity", default="tennis_forehand"); ap.add_argument("--comments", action="store_true"); ap.add_argument("--threads", type=int, default=4); a = ap.parse_args()
W, ACT = "work", a.activity; P = L.path(W, ACT)
bak = P.replace("labels.json", "labels.before_structure.json")
if not os.path.exists(bak): shutil.copy(P, bak)
lab = json.load(open(P)); lab.setdefault("structure", {})
src = {x["id"]: x for x in json.load(open(f"{W}/{ACT}/sources.json"))}
done = lambda c: c in lab["structure"] and all("faults" in g for g in lab["structure"][c])      # an older structure without the faults is redone
todo = [c for c, v in lab["clips"].items() if v["attempts"] and not done(c) and c in src]
kmap = K.load(W, ACT)
print(len(todo), "videos to do of", len(lab["clips"]), flush=True)
lock, fetch_lock = threading.Lock(), threading.Lock()
count = [0]


def one(c):
    x = src[c]; vid = L.video_file(f"{W}/{ACT}/videos", c)
    if not vid: return c, None, "video not on disk"
    try:
        with fetch_lock:                       # captions are fetched one at a time, spaced out (YouTube blocks quick repeats)
            raw = K.parse_vtt_timed(K.fetch_vtt(x["url"]) or "")
    except Exception: raw = []
    wins = [tuple(t["window"]) for t in lab["clips"][c]["attempts"]]
    dur = float(x.get("duration") or max(b for _, b in wins) + 5)
    segs = L.ask_structure(ACT, dur, L.transcript_text(raw, max_chars=24000) if raw else "", L.grab_frames(vid, 0, max(1.0, dur - 1), k=12, width=448), faults=kmap["faults"])
    return c, segs, None


with ThreadPoolExecutor(a.threads) as ex:
    for f in as_completed([ex.submit(one, c) for c in todo]):
        c, segs, why = f.result(); count[0] += 1; title = (src[c].get("title") or "")[:50]
        if not segs: print(f"{count[0]}/{len(todo)} {title}: {why or 'no usable answer'}", flush=True); continue
        with lock:
            lab["structure"][c] = segs
            for t in lab["clips"][c]["attempts"]:
                g = L.segment_at(segs, t["window"]) or {}; t["segment"] = g.get("kind"); t["segment_faults"] = g.get("faults", [])
            json.dump(lab, open(P, "w"), indent=1)
        print(f"{count[0]}/{len(todo)} {title}: {len(segs)} segments", flush=True)
print("done")
