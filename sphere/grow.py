"""Grow an activity's footage until there are enough clear attempts, not just enough videos.

How many videos it takes depends on the activity and on the footage: a squat appears many times in almost every clip, a
serve in a few. So the stop condition is attempts found (with the events that identify the action), spread over several
clips. Each round asks the model for new, more targeted searches, downloads only videos not seen before, extracts their
skeletons and counts again. If the target is not reached it stops after a few rounds and says so."""
import json
import os
from . import acquire, extract, pipeline
from . import propose as P

TARGET_ATTEMPTS = 60
TARGET_CLIPS = 15


def core_events(events):
    """The events that identify the action: those the proposal defines by a level to reach, otherwise all of them."""
    lead = [e for e in events if e.get("peak_at_least") is not None]
    return lead if len(lead) >= 2 else events


def count(activity, work_dir, prior, labels=None):
    cols = pipeline.load_collections(os.path.join(work_dir, activity, "clips"), core_events(prior["attempt_events"]),
                                     labels, prior["primary_features"])
    return sum(len(c["attempts"]) for c in cols), sum(1 for c in cols if c["attempts"]), len(cols)


def grow(activity, work_dir, model=None, variant="full", target_attempts=TARGET_ATTEMPTS, target_clips=TARGET_CLIPS,
         max_rounds=4, per_round=20, per_query=15, delete_videos=False, workers=3, ball_windows=False):
    prior = pipeline.load_prior(work_dir, activity, model)
    d = os.path.join(work_dir, activity)
    used = [q["query"] for q in prior["search_queries"]]
    src = os.path.join(d, "sources.json")
    sources = lambda: json.load(open(src)) if os.path.exists(src) else []
    a, c, n = count(activity, work_dir, prior)
    print(f"     now: {a} clear attempts in {c} of {n} clips (aim: {target_attempts} attempts in {target_clips} clips)", flush=True)
    rounds = 0
    while (a < target_attempts or c < target_clips) and rounds < max_rounds:
        rounds += 1
        print(f"     round {rounds}: looking for more footage ...", flush=True)
        queries = P.propose_queries(activity.replace("_", " "), prior["attempt_events"], used, model)
        used += [q["query"] for q in queries]
        got = acquire.acquire(queries, work_dir, activity, max_videos=per_round, per_query=per_query, model=model)
        if not got:
            print("     no new videos found; stopping.", flush=True)
            break
        extract.extract_folder(os.path.join(d, "videos"), os.path.join(d, "clips"), sources(), delete_video=delete_videos, variant=variant, workers=workers, ball_windows=ball_windows)
        a, c, n = count(activity, work_dir, prior)
        print(f"     now: {a} clear attempts in {c} of {n} clips", flush=True)
    done = a >= target_attempts and c >= target_clips
    if not done:
        print(f"     target not reached ({a} attempts in {c} clips); building from what there is. The entry will say so.", flush=True)
    prior["footage"] = {"attempts": a, "clips_with_attempts": c, "clips": n, "target_reached": done, "rounds": rounds}
    json.dump(prior, open(os.path.join(d, "prior.json"), "w"), indent=2)
    return prior["footage"]
