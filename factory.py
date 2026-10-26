#!/usr/bin/env python3
"""Skill Sphere factory.   python factory.py --help

  run      --activity "squat"     the whole thing: footage, coaching notes, mistake videos, labels, entry, checks;
                                  shows a banner on your screen when it finishes or stops (any step can be repeated; finished work is reused)
  queue    --activities a b c      several sports one after another (for the night); one failing does not stop the others;
                                  keeps the Mac awake while it runs; a summary is written to work/queue.log and shown as a banner
  acquire  --activity "squat"     only search and download reference videos
  extract  --activity "squat"     only turn downloaded (or your own) videos into skeleton clips
  grow     --activity "squat"     look for more footage until there are enough clear attempts
  learn    --activity "squat"     read what coaches say (captions of coaching videos) and keep structured notes
  mistakes --activity "squat"     find and download videos that show mistakes (needs: learn), then extract their skeletons
  label    --activity "squat"     say, for every attempt in those videos, which coach faults are visibly present or absent
                                  (--estimate shows the size of the job first and calls nothing)
  build    --activity "squat"     only propose + calibrate + check from existing clips
  check                           score the tennis entries on your three videos with known content (as filmed, half size, quarter size); table in work/check.log
  selftest                        run the whole pipeline on synthetic data (no internet, no API key)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

WORK = os.environ.get("SPHERE_WORK", "work")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def cmd_acquire(a):
    from sphere import acquire, pipeline
    act = slug(a.activity)
    print("1/5  asking the model what to search for (or reusing the earlier proposal) ...", flush=True)
    prop = pipeline.load_prior(WORK, act, a.llm)
    print(f"     {len(prop['search_queries'])} search queries ready", flush=True)
    got = acquire.acquire(prop["search_queries"], WORK, act, max_videos=a.max_videos, per_query=a.per_query, model=a.llm)
    print(f"{len(got)} videos in {WORK}/{act}/videos")


def cmd_extract(a):
    from sphere import extract
    act = slug(a.activity)
    d = os.path.join(WORK, act)
    src = []
    if os.path.exists(os.path.join(d, "sources.json")):
        src = json.load(open(os.path.join(d, "sources.json")))
    vdir = a.videos or os.path.join(d, "videos")
    n = extract.extract_folder(vdir, os.path.join(d, "clips"), src, delete_video=a.delete_videos, variant=a.model, workers=a.workers, ball_windows=getattr(a, "ball_windows", False))
    print(f"{n} clips written to {d}/clips")


def load_labels(path):
    if not path:
        return None
    out = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "," in line:
            cid, tag = [x.strip() for x in line.split(",", 1)]
            out[cid] = tag
    return out


def cmd_build(a):
    from sphere import pipeline
    act = slug(a.activity)
    entry, checks = pipeline.build(act, WORK, runs=a.runs, labels=load_labels(a.labels), model=a.llm)
    print(open(os.path.join(WORK, act, "report.md")).read())
    print(f"\n>>> {act}: {verdict(act)[1]}")


STEPS = ("grow", "learn", "mistakes", "label", "build")


def verdict(act):
    """Is the finished entry good enough to be used beside others? -> (ready, text). Written to work/<activity>/status.json as well, so that a build that
    finished is not mistaken for a build that is good."""
    from sphere.identify import ready
    p = os.path.join(WORK, slug(act), "entry.json")
    if not os.path.exists(p):
        return False, "no entry was built"
    ok, why = ready(json.load(open(p)))
    json.dump({"ready": ok, "why": why, "checked": time.strftime("%Y-%m-%d %H:%M")}, open(os.path.join(WORK, slug(act), "status.json"), "w"))
    return ok, "READY" if ok else f"DRAFT, not used beside other activities: {why}"


def banner(title, message, good=True):
    """A notification banner on the Mac screen (nothing happens on other systems)."""
    if sys.platform != "darwin":
        return
    script = f"display notification {json.dumps(message, ensure_ascii=False)} with title {json.dumps(title, ensure_ascii=False)} sound name \"{'Glass' if good else 'Basso'}\""
    try:
        subprocess.run(["osascript", "-e", script], check=False, timeout=10)
    except Exception:
        pass


def cmd_run(a):
    started, step = time.time(), None
    try:
        for i, step in enumerate(STEPS, 1):
            print(f"\n=== step {i}/{len(STEPS)}: {step} ===", flush=True)
            globals()["cmd_" + step](a)
    except KeyboardInterrupt:
        raise                                                          # you stopped it yourself: no banner
    except BaseException:
        banner("SPHERE factory stopped", f"{a.activity}: stopped at '{step}'. Look at the Terminal.", good=False)
        raise
    ok, text = verdict(a.activity)
    banner("SPHERE factory finished" if ok else "SPHERE factory finished, but the entry is a draft", f"{a.activity}: built in {round((time.time() - started) / 60)} min. {text}", good=ok)


def audit(prefix):
    """Quality check of the entries of one family of activities (say 'tennis') on every video of yours whose skeleton is saved:
    what each entry finds. An entry that finds nothing in footage that should hold its shot, or that takes over another entry's
    swings, shows here. Returns the lines of the report."""
    import glob
    from sphere.identify import identify
    from sphere.skeleton import load_clip
    entries = {}
    for d in sorted(os.listdir(WORK)):
        p = os.path.join(WORK, d, "entry.json")
        if d.startswith(prefix) and os.path.exists(p):
            e = json.load(open(p))
            if e.get("recognition") and e["metadata"]["provenance"].get("attempt_events"):
                entries[d] = e
    lines = ["entries: " + ", ".join(entries)]
    for sk in sorted(glob.glob(os.path.join(WORK, "*", "coaching", "*.skeleton.npz"))):
        owned, found = identify(entries, load_clip(sk))
        lines.append(f"{os.path.basename(sk)[:-13]}: " + ", ".join(f"{k} {len(v)}" for k, v in owned.items()))
    return lines


def cmd_queue(a):
    """Runs `run` for each activity in turn, each in its own process, so one that fails is reported and the next still runs.
    A failed sport is tried once more (finished steps are reused). The Mac is kept awake, the free disk is watched, and the
    entries are audited on your own saved videos at the end. Everything is written to work/queue.log."""
    import shutil
    started, results = time.time(), []
    log = os.path.join(WORK, "queue.log")
    os.makedirs(WORK, exist_ok=True)
    def note(msg):
        print(msg, flush=True)
        with open(log, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M')}  {msg}\n")
    prefix = ["caffeinate", "-i"] if sys.platform == "darwin" else []      # keeps the Mac from going to sleep while it works
    for i, act in enumerate(a.activities, 1):
        free = shutil.disk_usage(WORK).free / 1e9
        if free < a.min_free_gb:
            note(f"stopped before {act}: only {free:.0f} GB free (the limit is {a.min_free_gb} GB)")
            results.append((act, False, 0)); break
        print(f"\n######## {i}/{len(a.activities)}: {act} ########", flush=True)
        t0 = time.time()
        cmd = prefix + [sys.executable, os.path.abspath(__file__), "run", "--activity", act] + (["--delete-videos"] if a.delete_videos else []) + (["--ball-windows"] if getattr(a, "ball_windows", False) else [])
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            note(f"{act}: failed (exit {rc}), trying once more")
            rc = subprocess.run(cmd).returncode
        results.append((act, rc == 0, round((time.time() - t0) / 60)))
        note(f"{act}: {'built' if rc == 0 else 'FAILED (exit %d)' % rc} in {results[-1][2]} min" + (f" - {verdict(act)[1]}" if rc == 0 else ""))
    ok = sum(1 for r in results if r[1])
    usable = sum(1 for r in results if r[1] and verdict(r[0])[0])
    summary = ", ".join(f"{act} {('ready' if verdict(act)[0] else 'draft') if good else 'FAILED'}" for act, good, _ in results)
    try:
        for line in audit(a.audit):
            note("audit  " + line)
    except Exception as e:
        note(f"audit not possible: {str(e)[:100]}")
    note(f"queue finished in {round((time.time() - started) / 60)} min: {summary}")
    banner("SPHERE queue finished", f"{usable} of {len(results)} usable ({ok} built): {summary}", good=usable == len(results))


def cmd_check(a):
    """The check that needs nobody: your three videos (5 serves, 5 forehands, 5 serves then forehands) are read again with the code as it is, once as
    they are and once as a half-size copy (what a phone may send), and the entries are scored on what they find. Everything is written to work/check.log."""
    import cv2
    from sphere.extract import extract_video
    from sphere.skeleton import save_clip
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))
    import bench
    folder = os.path.expanduser(a.videos)
    log = os.path.join(WORK, "check.log")
    os.makedirs(os.path.join(WORK, "check"), exist_ok=True)
    def note(msg):
        print(msg, flush=True)
        with open(log, "a") as f:
            f.write(msg + "\n")
    note(f"\n=== check {time.strftime('%Y-%m-%d %H:%M')} ===")
    files = {os.path.splitext(fn)[0]: os.path.join(folder, fn) for fn in os.listdir(folder) if fn.lower().endswith((".mov", ".mp4"))}
    for variant in ("as filmed", "half size", "quarter size"):
        out = os.path.join(WORK, "check", variant.replace(" ", "_"))
        os.makedirs(out, exist_ok=True)
        for stem in bench.CLIPS:
            if stem not in files:
                note(f"{variant}: {stem}: video not found in {folder}"); continue
            src = files[stem]
            if variant != "as filmed":
                k = 2 if variant == "half size" else 4
                cap = cv2.VideoCapture(src)
                w, h, fps = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) // k), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // k), cap.get(cv2.CAP_PROP_FPS) or 30.0
                src = os.path.join(out, stem + ".half.mp4")
                vw = cv2.VideoWriter(src, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
                while True:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    vw.write(cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA))
                vw.release(); cap.release()
            t0 = time.time()
            clip = extract_video(src, {"source": "check", "variant": variant}, variant=a.model)
            if variant != "as filmed":
                os.remove(src)
            if clip is None:
                note(f"{variant}: {stem}: the person could not be followed"); continue
            save_clip(os.path.join(out, stem + ".skeleton.npz"), clip)
            note(f"{variant}: {stem}: read in {round(time.time() - t0)} s")
        note(f"\n--- {variant} ---")
        for line in bench.report(WORK, out):
            note(line)
    banner("SPHERE check finished", f"the table is in {log}", good=True)


def cmd_grow(a):
    from sphere import grow
    act = slug(a.activity)
    r = grow.grow(act, WORK, model=a.llm, variant=a.model, target_attempts=a.target_attempts, target_clips=a.target_clips,
                  max_rounds=a.max_rounds, per_round=a.per_round, delete_videos=a.delete_videos, workers=a.workers, ball_windows=getattr(a, "ball_windows", False))
    print(f"footage: {r['attempts']} clear attempts in {r['clips_with_attempts']} of {r['clips']} clips; "
          f"target {'reached' if r['target_reached'] else 'NOT reached'} after {r['rounds']} round(s)")


def cmd_learn(a):
    from sphere import knowledge
    act = slug(a.activity)
    k = knowledge.learn(act, WORK, n_videos=a.sources, model=a.llm, refresh=a.refresh)
    strong = sum(1 for f in k["faults"] if f["support"] != "single")
    from sphere import knowledge as _K
    if _K.caption_summary():
        print("     " + _K.caption_summary())
    print(f"coaching knowledge: {k['n_sources']} videos read, {len(k['faults'])} faults named ({strong} by at least two); saved to {WORK}/{act}/knowledge.json")


def cmd_mistakes(a):
    from sphere import labelling, knowledge
    act = slug(a.activity)
    kmap = knowledge.load(WORK, act)
    if not kmap:
        sys.exit("run learn first: the searches are made from the faults coaches name")
    print("1/2  looking for videos that show mistakes ...", flush=True)
    got = labelling.find_mistake_videos(act, WORK, kmap, n=a.n_mistakes, model=a.llm)
    print(f"     {len(got)} new videos downloaded", flush=True)
    print("2/2  extracting skeletons ...", flush=True)
    cmd_extract(argparse.Namespace(activity=a.activity, videos=None, delete_videos=False, model=a.model, workers=a.workers))


def cmd_label(a):
    from sphere import labelling
    act = slug(a.activity)
    lab, est = labelling.label_activity(act, WORK, model=a.llm, refresh=a.refresh, estimate_only=a.estimate, use_comments=a.comments, use_structure=a.structure)
    if not a.estimate:
        s = labelling.summary(lab)
        from sphere import knowledge as _K
        if _K.caption_summary():
            print("     " + _K.caption_summary())
        print(f"labels: {s['attempts']} attempts in {s['videos']} videos ({s['not_attempts']} not attempts); saved to {WORK}/{act}/labels.json")


def cmd_inspect(a):
    from sphere import inspect_clips
    act = slug(a.activity)
    from sphere import pipeline
    prior = pipeline.load_prior(WORK, act)
    out = inspect_clips.inspect(os.path.join(WORK, act, "clips"), os.path.join(WORK, act, "inspect.png"),
                                prior["attempt_events"], primary=prior["primary_features"])
    print(f"picture written to {out}")


def cmd_selftest(a):
    import shutil
    from sphere import synth, skeleton, pipeline, propose
    w = os.path.join(WORK, "_selftest")
    shutil.rmtree(w, ignore_errors=True)
    for act in ("squat", "arm_raise"):
        os.makedirs(os.path.join(w, act, "clips"))
    for s, y in enumerate([0, 40, 80, 20, 60, 10]):
        skeleton.save_clip(f"{w}/squat/clips/g{s}.npz", synth.squat_clip(yaw=y, seed=s, tag="good"))
    for i in range(4):
        skeleton.save_clip(f"{w}/squat/clips/c{i}.npz", synth.squat_clip(yaw=40, seed=10 + i, tag="knee_cave", valgus=0.05))
    for i in range(3):
        skeleton.save_clip(f"{w}/squat/clips/s{i}.npz", synth.squat_clip(yaw=30, seed=20 + i, tag="shallow_depth", depth=0.5))
    for s, y in enumerate([0, 40, 70]):
        skeleton.save_clip(f"{w}/arm_raise/clips/a{s}.npz", synth.arm_raise_clip(seed=s, yaw=y))
    json.dump({"primary_features": ["angle.shoulder.dom", "angle.shoulder.non"], "attempt_events": [{"feature": "angle.shoulder.dom", "direction": "rises", "seconds": 2.0}],
               "events_rule": 6}, open(f"{w}/arm_raise/prior.json", "w"))             # the other activity's prior, so no model call is needed
    pipeline.build("squat", w, runs=2, proposer=lambda act, r: [propose.stub_squat_proposal() for _ in range(r)])
    print(open(os.path.join(w, "squat", "report.md")).read())
    print("selftest finished (synthetic data: this checks the machinery, not real-world accuracy)")


def main():
    ap = argparse.ArgumentParser(description="Skill Sphere factory")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("run", cmd_run), ("acquire", cmd_acquire), ("extract", cmd_extract), ("grow", cmd_grow), ("learn", cmd_learn), ("build", cmd_build), ("inspect", cmd_inspect), ("mistakes", cmd_mistakes), ("label", cmd_label)):
        p = sub.add_parser(name); p.add_argument("--activity", required=True)
        p.add_argument("--max-videos", type=int, default=20)
        p.add_argument("--per-query", type=int, default=8, help="search results taken per query (queries x this = most videos found)")
        p.add_argument("--target-attempts", type=int, default=60, help="grow: stop when this many clear attempts are found")
        p.add_argument("--target-clips", type=int, default=15, help="grow: ... in at least this many different clips")
        p.add_argument("--max-rounds", type=int, default=4, help="grow: most rounds of new searches")
        p.add_argument("--per-round", type=int, default=20, help="grow: most new videos downloaded per round")
        p.add_argument("--sources", type=int, default=12, help="learn: coaching videos to read")
        p.add_argument("--refresh", action="store_true", help="learn / label: do it again instead of reusing what is already saved")
        p.add_argument("--n-mistakes", type=int, default=25, help="mistakes: most mistake videos to download")
        p.add_argument("--estimate", action="store_true", help="label: only show how big the job is, call no model")
        p.add_argument("--structure", action="store_true", help="label: first work out each video's structure (talking, wrong demo, right demo, play) and give it to the labelling of every swing")
        p.add_argument("--comments", action="store_true", help="label: also show the model the viewers' comments of each video (fetched once, cached)")
        p.add_argument("--workers", type=int, default=3, help="videos analysed at the same time (1 = one at a time)")
        p.add_argument("--runs", type=int, default=5, help="independent model proposals, to measure agreement")
        p.add_argument("--labels", help="csv of clip_id,tag (tag 'good' or an objective id) for validated target ranges")
        p.add_argument("--videos", help="folder of your own videos to extract instead of the downloaded ones")
        p.add_argument("--delete-videos", action="store_true", help="delete each video after its skeleton is extracted")
        p.add_argument("--ball-windows", action="store_true", help="before a video is deleted, keep the pictures around each tennis shot (about 5 MB a window) for the ball tracker")
        p.add_argument("--model", default="full", help="pose model: lite | full | heavy")
        p.add_argument("--llm", default=None, help="language model id for proposals")
        p.set_defaults(fn=fn)
    p = sub.add_parser("queue"); p.add_argument("--activities", nargs="+", required=True)
    p.add_argument("--delete-videos", action="store_true", help="delete each video after its skeleton is extracted")
    p.add_argument("--ball-windows", action="store_true", help="keep the pictures around each tennis shot for the ball tracker")
    p.add_argument("--min-free-gb", type=int, default=15, help="stop when less disk than this is free")
    p.add_argument("--audit", default="tennis", help="activities whose names start with this are compared on your saved videos at the end"); p.set_defaults(fn=cmd_queue)
    p = sub.add_parser("check"); p.add_argument("--videos", default="~/Desktop/SPHERE", help="folder with IMG_2935.mov, IMG_2935 2.MOV and IMG_2935 3.mov")
    p.add_argument("--model", default="full", help="pose model: lite | full | heavy"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
