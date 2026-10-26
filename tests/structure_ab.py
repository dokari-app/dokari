"""Does the structure pass (what the coach does when: talking / wrong demo / right demo / play) improve the labelling?
  python tests/structure_ab.py [--videos 20]
Re-labels the forehand videos that had the most faults marked present, with and without the structure pass, into SEPARATE files (today's labels.json is not touched):
  work/tennis_forehand/labels_structure.json   and the comparison in work/structure_ab.md
Cost: about 20 structure calls and 20 labelling calls (about 1M input tokens)."""
import argparse, json, os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from sphere import labelling as L
ap = argparse.ArgumentParser(); ap.add_argument("--videos", type=int, default=20); a = ap.parse_args()
ACT, W = "tennis_forehand", "work"
old = json.load(open(f"{W}/{ACT}/labels.json"))
score = lambda v: sum(len(x["present"]) for x in v["attempts"])
pick = [c for c, v in sorted(old["clips"].items(), key=lambda kv: -score(kv[1])) if len(v["attempts"]) >= 4][: a.videos]
print(len(pick), "videos chosen")
L.path = lambda w, act: f"{w}/{act}/labels_structure.json"
orig = L.clips_to_label
L.clips_to_label = lambda sources, cols, vd: [t for t in orig(sources, cols, vd) if t[0]["clip_id"] in pick]
lab, est = L.label_activity(ACT, W, use_structure=True)
new = json.load(open(f"{W}/{ACT}/labels_structure.json"))
rows = collections.Counter(); seg = collections.Counter(); kinds = collections.Counter(); agree = tot = 0
for c in pick:
    if c not in new["clips"]: rows["videos not relabelled"] += 1; continue
    o = {tuple(round(t, 1) for t in x["window"]): x for x in old["clips"][c]["attempts"]}
    for x in new["clips"][c]["attempts"]:
        k = tuple(round(t, 1) for t in x["window"]); y = o.get(k)
        if not y: continue
        rows["attempts compared"] += 1
        rows["present: before"] += len(y["present"]); rows["present: with structure"] += len(x["present"])
        rows["absent: before"] += len(y["absent"]); rows["absent: with structure"] += len(x["absent"])
        rows["not-an-attempt: before"] += y["not_an_attempt"]; rows["not-an-attempt: with structure"] += x["not_an_attempt"]
        kinds[x.get("segment")] += 1
        if not x["not_an_attempt"] and not y["not_an_attempt"]:
            tot += 1; agree += (set(x["present"]) == set(y["present"]))
        # the point of the pass: a mistake shown as a wrong demo should carry present faults, a right demo should not
        seg[(x.get("segment"), "has present fault" if x["present"] else "no present fault")] += 1
md = ["# Structure pass A/B", "", f"{len(pick)} videos", ""] + [f"- {k}: {v}" for k, v in rows.items()]
md += ["", f"same set of present faults on {agree} of {tot} attempts judged real in both", "", "segment kinds of the attempts:"] + [f"- {k}: {v}" for k, v in kinds.most_common()]
md += ["", "segment x fault present (with structure):"] + [f"- {k[0]} / {k[1]}: {v}" for k, v in sorted(seg.items(), key=lambda kv: str(kv[0]))]
open(f"{W}/structure_ab.md", "w").write("\n".join(md)); print("\n".join(md))
