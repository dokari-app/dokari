"""Skill Sphere coach: an entry built by the factory + a video or a camera -> spoken cues.

  python coach.py video --video my_session.mp4                              (no --activity: every entry in the library is tried and each swing goes to the
                                                                             activity it fits best, or to none; then each is coached by its own entry)
  python coach.py video --activity tennis_serve --video my_serve.mp4        (recorded video: prints the coaching timeline, writes a log
                                                                             and a copy of the video with the cues on it)
  python coach.py live  --activity tennis_serve                             (webcam: speaks through the speakers or earbuds)

Cues are worded at the moment they are needed by a language model when ANTHROPIC_API_KEY is set; otherwise the entry's own cue intent is used."""
import argparse, json, os, queue, subprocess, sys, threading, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")


def slug(s):
    return "_".join(s.lower().split())


def load_entry(activity):
    path = os.path.join(WORK, slug(activity), "entry.json")
    if not os.path.exists(path):
        sys.exit(f"No entry at {path}. Build it first:  python factory.py build --activity {activity}")
    return json.load(open(path))


def make_wording(entry, language, offline):
    from sphere.engine import Wording
    client = None
    if not offline and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
        except ImportError:
            print("(anthropic package missing: using the entry's own wording)")
    elif not offline:
        print("(no ANTHROPIC_API_KEY: using the entry's own wording)")
    return Wording(entry, client=client, language=language)


def say_text(text, voice):
    cmd = ["say"] + (["-v", voice] if voice else []) + [text] if sys.platform == "darwin" else None
    if cmd:
        subprocess.run(cmd, check=False)


def objective_goal(entry, oid):
    return next((o["goal"] for o in entry["objectives"] if o["id"] == oid), oid)


def debug_swings(entry, clip):
    """What the swing finder sees in this video: how much of the body was followed, every excursion of each event's signal, and the
    tests each candidate then has to pass to count as an attempt."""
    import numpy as np
    from sphere.features import compute_features
    from sphere import segment as SG
    names, F, _ = compute_features(clip)
    fps = clip["fps"]
    prov = entry["metadata"]["provenance"]
    primary = list(prov.get("primary_features") or [])
    events = prov.get("attempt_events", [])
    for e in events:
        if e["feature"] not in primary:
            primary.append(e["feature"])
    cols = [names.index(n) for n in primary]
    valid = SG.valid_mask(F, fps, names, watch=primary)
    thr = np.array([SG.MIN_SWING_DEG if names[c].startswith("angle.") else SG.MIN_SWING_REL for c in cols])
    need = max(1, int(np.ceil(len(cols) / 2)))
    ang_cols = [c for c in cols if names[c].startswith("angle.")]
    print(f"\nbody followed in {100 * float((clip['vis'].mean(1) > 0.4).mean()):.0f}% of frames; {len(F) / fps:.1f} s at {fps:.0f} fps")
    for e in events:
        sign = 1.0 if e["direction"] == "rises" else -1.0
        sig = SG._fill_nan(F[:, [names.index(e["feature"])]])[:, 0] * sign
        t = SG.MIN_SWING_DEG if e["feature"].startswith("angle.") else SG.MIN_SWING_REL
        lvl = e.get("peak_at_least")
        print(f"event: {e['feature']} {e['direction']}" + (f", must reach {lvl}" if lvl is not None else "") + f"; the signal ranges {np.min(sig * sign):.2f} to {np.max(sig * sign):.2f}")
        for st, pk, en, pr in SG.excursions(sig, fps, t):
            ok = lvl is None or sig[max(0, pk - 2):pk + 3].max() >= sign * float(lvl)
            line = f"   {st / fps:5.1f}-{en / fps:5.1f} s  peak {sig[pk] * sign:6.2f}  size {pr:5.2f}  " + ("reaches the level" if ok else "DROPPED: does not reach the level")
            if ok:
                a, b = max(0, int(st)), min(len(F) - 1, int(en))
                v = float(valid[a:b + 1].mean())
                u = SG.swing_units(F, a, b, cols, thr, need)
                r = SG.roughness(F, a, b, ang_cols, fps)
                bad = [x for x, c in (("believable frames %.2f < %.2f" % (v, SG.MIN_VALID), v < SG.MIN_VALID), ("body moves as a group %.1f < 1" % u, u < 1.0),
                                      ("roughness %.1f > %.1f" % (r, SG.MAX_ROUGH_DEG), r > SG.MAX_ROUGH_DEG), ("length %.1f s outside 0.4-20" % ((b - a) / fps), not 0.4 * fps <= b - a <= 20 * fps)) if c]
                line += "  | believable %.2f, moves as a group %.1f, roughness %.1f" % (v, u, r) + (("  -> DROPPED: " + "; ".join(bad)) if bad else "  -> passes")
            print(line)
    out = os.path.join(WORK, slug(entry.get("activity_id", "clip")), "coaching")
    os.makedirs(out, exist_ok=True)
    from sphere.skeleton import save_clip
    save_clip(os.path.join(out, "last_debug_clip.npz"), clip)
    print(f"\nskeleton of this video saved to {out}/last_debug_clip.npz")
    print()


def load_all_entries(only=None):
    """Every activity the library knows: the entries the factory has built (an entry from an older format that cannot be used is left out).
    `only` keeps the activities whose name starts with it (a tennis video: only="tennis"); several, comma-separated, keep each of them
    (only="tennis_serve,tennis_forehand")."""
    out = {}
    starts = tuple(slug(x) for x in only.split(",") if x.strip()) if only else ()
    named = set(starts)                     # an activity named in full is used whatever its quality; a family (a prefix) only brings in the entries that are ready
    from sphere.identify import ready
    held = []
    for d in sorted(os.listdir(WORK)):
        p = os.path.join(WORK, d, "entry.json")
        if d.startswith("_") or not os.path.exists(p) or (starts and not d.startswith(starts)):
            continue
        e = json.load(open(p))
        if e.get("recognition") and e["metadata"]["provenance"].get("attempt_events"):
            ok, why = ready(e)
            if not ok and d not in named:
                held.append((d, why))
                continue
            out[d] = e
    for d, why in held:
        print(f"  held back as a draft: {d}: {why}")
    if not out:
        sys.exit("No entries in the library" + (f" for '{only}'" if only else "") + " yet. Build one first:  python factory.py run --activity <name>")
    return out


def coach_all(entries, clip, a):
    """Several activities in one video: each swing goes to the activity it fits best (or to none), and is coached by that activity's entry."""
    from sphere import engine
    from sphere.identify import identify, accepts
    owned, found = identify(entries, clip)
    print(f"\nactivities in the library: {', '.join(entries)}\n")
    shown = set()
    for f in found:
        key = (round(f["start"], 1), f["activity"])
        if key in shown:
            continue
        shown.add(key)
        print(f"  {f['start']:6.1f}-{f['end']:5.1f}s  looks like {f['activity']:<16} fit {f['fit']:6.2f}  " + ("(taken)" if f["owner"] == f["activity"] else "(fits no better than another, or not at all)" if f["fit"] <= 1.0 else "(too far from a typical attempt)"))
    nothing = [f for f in found if f["owner"] is None]
    events, log = [], []
    for act, entry in entries.items():
        if not owned[act]:
            continue
        ev, lg = engine.run_clip(entry, clip, wording=make_wording(entry, a.language, a.offline), accept=lambda s, e, w=owned[act]: accepts(w, s, e))
        for r in lg:
            r["activity"] = act
        for x in ev:
            x["activity"] = act
        events += ev; log += lg
    if not any(owned.values()):
        print("\nNo known activity fits what was found in this video.")
    log.sort(key=lambda r: r["start"])
    for i, r in enumerate(log, 1):
        r["attempt"] = i
    return sorted(events, key=lambda e: e["t"]), log


def cmd_video(a):
    import cv2
    from sphere import engine
    from sphere.extract import extract_video
    auto = not a.activity
    entries = load_all_entries(a.only) if auto else {a.activity: load_entry(a.activity)}
    entry = entries[a.activity] if not auto else None
    print("reading the video ...")
    clip = extract_video(a.video, {"source": "coach"}, variant=a.model)
    if clip is None:
        sys.exit("The person could not be followed in this video (too little of the body found).")
    from sphere.skeleton import save_clip                # the skeleton (not the picture) is kept, so a video can be analysed again without reading it again
    keep = os.path.join(WORK, slug(a.activity or "auto"), "coaching")
    os.makedirs(keep, exist_ok=True)
    save_clip(os.path.join(keep, os.path.splitext(os.path.basename(a.video))[0] + ".skeleton.npz"), clip)
    if a.debug and not auto:
        debug_swings(entry, clip)
    if auto:
        events, log = coach_all(entries, clip, a)
        a.activity = "auto"
    else:
        events, log = engine.run_clip(entry, clip, wording=make_wording(entry, a.language, a.offline))
    print(f"\n{len(log)} attempts found in {len(clip['pose']) / clip['fps']:.0f} s\n")
    for r in log:
        mark = {"met": "ok", "missed": "MISS", "unknown": "?"}
        marks = "  ".join(f"{i} {mark[v['status']]}" for i, v in r["objectives"].items())
        said = f'   -> "{r["said"]["text"]}"' if "said" in r else ""
        print(f"  attempt {r['attempt']:>2}  {r['start']:6.1f}-{r['end']:5.1f}s   {r.get('activity', '') + '  ' if r.get('activity') else ''}{marks}{said}")
    print("\nWhat was said:")
    for e in events:
        print(f"  {e['t']:6.1f}s  [{e['kind']}] {e['text']}")
    if not events:
        print("  nothing: no objective was missed often enough to be worth interrupting")
    outdir = os.path.join(WORK, slug(a.activity), "coaching")
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.join(outdir, os.path.splitext(os.path.basename(a.video))[0] + ".coach")
    json.dump({"activity": a.activity, "events": events, "attempts": log}, open(stem + ".json", "w"), indent=1)
    print(f"\nlog: {stem}.json")
    if not a.no_video:
        cap = cv2.VideoCapture(a.video)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        W, H = int(cap.get(3)), int(cap.get(4))
        out = cv2.VideoWriter(stem + ".mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
        i, shown = 0, ""
        pending = sorted(events, key=lambda e: e["t"])
        until = 0.0
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            t = i / fps
            while pending and pending[0]["t"] <= t:
                shown, until = pending.pop(0)["text"], t + 3.5
            if shown and t < until:
                cv2.rectangle(fr, (0, H - 70), (W, H), (0, 0, 0), -1)
                cv2.putText(fr, shown, (20, H - 25), cv2.FONT_HERSHEY_SIMPLEX, max(0.6, W / 1400), (255, 255, 255), 2, cv2.LINE_AA)
            out.write(fr); i += 1
        cap.release(); out.release()
        print(f"video with the cues on it: {stem}.mp4")


def cmd_live(a):
    import cv2
    from sphere import engine
    from sphere.extract import Tracker
    entry = load_entry(a.activity)
    wording = make_wording(entry, a.language, a.offline)
    cam = cv2.VideoCapture(a.camera)
    if not cam.isOpened():
        sys.exit("Could not open the camera. On a Mac, allow Terminal under System Settings > Privacy & Security > Camera.")
    fps = a.fps
    session = engine.Session(entry, wording=wording, fps=fps)
    track = Tracker(a.model)
    frames, speech, stop = queue.Queue(maxsize=int(3 * fps)), queue.Queue(), threading.Event()

    def think():                      # judging and wording happen off the camera loop so no frame is ever waited for
        while not stop.is_set():
            try:
                P, V, t = frames.get(timeout=0.2)
            except queue.Empty:
                continue
            for e in session.push(P, V, t):
                print(f"  {e['t']:6.1f}s  [{e['kind']}] {e['text']}", flush=True)
                speech.put(e["text"])

    def talk():                       # one sentence at a time, never over itself
        while not stop.is_set():
            try:
                txt = speech.get(timeout=0.2)
            except queue.Empty:
                continue
            say_text(txt, a.voice)

    for fn in (think, talk):
        threading.Thread(target=fn, daemon=True).start()
    print("Coaching. Stand so your whole body is in view. Press q in the video window (or Ctrl-C) to stop.")
    t0, last = time.time(), -1.0
    try:
        while True:
            ok, fr = cam.read()
            if not ok:
                break
            t = time.time() - t0
            if t - last >= 1.0 / fps:                  # feed the engine at its own steady rate whatever the camera delivers
                last = t
                P, V = track(fr, t)
                try:
                    frames.put_nowait((P, V, last))
                except queue.Full:
                    pass
            cv2.imshow("Skill Sphere coach", cv2.flip(fr, 1) if a.mirror else fr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    stop.set(); cam.release(); cv2.destroyAllWindows(); track.close()
    stem = os.path.join(WORK, slug(a.activity), time.strftime("session_%Y%m%d_%H%M%S"))
    json.dump({"activity": a.activity, "attempts": session.log}, open(stem + ".json", "w"), indent=1)
    print(f"session log: {stem}.json")


def main():
    ap = argparse.ArgumentParser(description="Skill Sphere coach")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("video", cmd_video), ("live", cmd_live)):
        p = sub.add_parser(name)
        p.add_argument("--activity", required=(name == "live"), default=None, help="video: leave out to let the coach recognise the activity from the library")
        p.add_argument("--model", default="full", help="pose model: lite | full | heavy")
        p.add_argument("--language", default="English")
        p.add_argument("--offline", action="store_true", help="do not call a language model for the wording")
        if name == "video":
            p.add_argument("--video", required=True)
            p.add_argument("--only", default=None, help="with no --activity: only try the activities whose name starts with this (for example: tennis)")
            p.add_argument("--debug", action="store_true", help="print what the swing finder sees (body followed, each swing candidate and why it is kept or dropped)")
            p.add_argument("--no-video", action="store_true", help="do not write a copy of the video with the cues on it")
        else:
            p.add_argument("--camera", type=int, default=0)
            p.add_argument("--fps", type=float, default=30.0)
            p.add_argument("--voice", default=None, help="macOS voice name for 'say' (see: say -v '?')")
            p.add_argument("--mirror", action="store_true", help="show the preview mirrored")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
