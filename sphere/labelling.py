"""Step 2: real ground truth from mistake videos.

A mistake video shows someone doing the movement wrongly (and often rightly) while a coach says what is going on. For every
attempt we found in such a video, the model looks at a few frames of that attempt together with what the coach says at that
moment and states which of the coaches' faults are visibly present and which are visibly absent. The frames decide; the words
tell the model which fault the coach is pointing at. Whatever cannot be judged from the frames (the wrong camera angle, the
body part out of view) is left unlabelled, never guessed.

Only derived data is kept: labels.json holds, per attempt, the time window and the fault ids. Captions are read once, used for the
labelling call and discarded; no frames are kept."""
import base64
import glob
import json
import os
import time
import jsonschema

DEFAULT_MODEL = os.environ.get("SPHERE_MODEL", "claude-sonnet-5-5")
FRAMES = 6                      # frames shown per attempt
WIDTH = 576                     # pixels; posture is visible at this size and the cost stays low
TRANSCRIPT_CHARS = 9000
TOKENS_PER_IMAGE = 330          # estimate used for the cost preview only
LABEL_TIERS = ("mistake_analysis", "coach_demo", "practice_session", "pro_footage")


# ---------------------------------------------------------------- finding the footage
def mistake_queries(activity, kmap, n_faults=12):
    """Searches for videos that show and name mistakes: general ones, and for each fault the coaches name most, a few ways people title such a video."""
    a = activity.replace("_", " ")
    qs = [f"{a} common mistakes", f"{a} form check what is wrong", f"{a} bad form vs good form", f"{a} mistakes and corrections",
          f"{a} beginner mistakes", f"{a} why do I keep getting it wrong", f"{a} bad habits to fix", f"{a} lesson with student correcting form",
          f"{a} wrong vs right", f"{a} before and after fix", f"{a} biggest mistakes players make"]
    faults = sorted(kmap["faults"], key=lambda f: -f["n_sources"])[:n_faults] if kmap else []
    for f in faults:
        name = f["id"].replace("_", " ")
        qs += [f"{a} {name} fix", f"{a} {name} mistake", f"{a} {name} drill"]
    return [{"query": q, "kind": "mistakes"} for q in qs]


def rank_for_labelling(items, n, per_channel=3):
    """Videos that show mistakes with a person in view. 'mixed' (the mistake and then the fix, often by the same person) comes first:
    it holds both sides of a comparison. A channel is limited, so one coach's habits are not taken for the movement's."""
    ok = [it for it in items if it.get("shows") in ("mistakes", "mixed") and it.get("tier") in LABEL_TIERS]
    ok.sort(key=lambda it: (it["shows"] != "mixed", LABEL_TIERS.index(it["tier"])))
    seen, out = {}, []
    for it in ok:
        ch = it.get("channel") or it["id"]
        if seen.get(ch, 0) >= per_channel:
            continue
        seen[ch] = seen.get(ch, 0) + 1
        out.append(it)
        if len(out) >= n:
            break
    return out


def find_mistake_videos(activity, work_dir, kmap, n=25, model=None, acquire_fn=None):
    """Search for, rate and download up to n videos that show mistakes. Returns the newly downloaded items."""
    from . import acquire
    fn = acquire_fn or acquire.acquire
    return fn(mistake_queries(activity, kmap), work_dir, activity, max_videos=n, per_query=12, model=model,
              chooser=rank_for_labelling, search_kw={"min_s": 30, "max_s": 600})


# ---------------------------------------------------------------- what the video shows at a time
def _mmss(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def transcript_text(cues, max_chars=TRANSCRIPT_CHARS, span=10.0):
    """Captions as lines of about `span` seconds, each starting with its time. Long videos are cut at max_chars."""
    lines, cur, t0 = [], [], None
    for a, b, txt in cues:
        if t0 is None:
            t0 = a
        cur.append(txt)
        if b - t0 >= span:
            lines.append(f"[{_mmss(t0)}] {' '.join(cur)}"); cur, t0 = [], None
    if cur:
        lines.append(f"[{_mmss(t0)}] {' '.join(cur)}")
    text = "\n".join(lines)
    return text[:max_chars]


def grab_frames(video_path, t0, t1, k=FRAMES, width=WIDTH):
    """k JPEG frames (base64) evenly spread over [t0, t1] of the video, and the times they were taken at."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    out, times = [], []
    try:
        for i in range(k):
            t = t0 + (t1 - t0) * (i / max(1, k - 1))
            cap.set(cv2.CAP_PROP_POS_MSEC, 1000 * t)
            ok, fr = cap.read()
            if not ok:
                continue
            h, w = fr.shape[:2]
            fr = cv2.resize(fr, (width, max(1, int(h * width / w))), interpolation=cv2.INTER_AREA)
            ok, buf = cv2.imencode(".jpg", fr, [cv2.IMWRITE_JPEG_QUALITY, 72])
            if ok:
                out.append(base64.b64encode(buf.tobytes()).decode()); times.append(round(t, 1))
    finally:
        cap.release()
    return out, times


def video_file(videos_dir, vid):
    for f in sorted(glob.glob(os.path.join(videos_dir, vid + ".*"))):
        if not f.endswith((".part", ".ytdl", ".vtt")):
            from .localfile import is_local
            return f if is_local(f) else None
    return None


# ---------------------------------------------------------------- the model's judgement
LABEL_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["attempts"], "properties": {
    "attempts": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["n", "not_an_attempt", "stroke", "view_clean", "present", "absent"],
        "properties": {
            "n": {"type": "integer", "description": "the attempt number as given"},
            "not_an_attempt": {"type": "boolean", "description": "true if these frames do not show one repetition of the activity (talking, walking, set-up, another exercise)"},
            "stroke": {"type": "string", "description": "which movement these frames show, in one or two lowercase words (for tennis: serve, forehand, backhand, volley, smash, slice, drop shot); 'none' when not an attempt"},
            "view_clean": {"type": "boolean", "description": "true when exactly one player is in the attempt and the whole body can be followed (not cut off, hidden or tiny, no cut to another camera)"},
            "present": {"type": "array", "items": {"type": "string"}, "description": "ids of faults that are visibly present in these frames"},
            "absent": {"type": "array", "items": {"type": "string"}, "description": "ids of faults that are visibly absent: the relevant body part is clearly in view and the fault is not there"}}}}}}

PROMPT = """Activity: {activity}

Coaches name these faults (id: what it looks like):
{faults}

Below are {n} attempts from one video, each as {k} frames in time order. {words}

For every attempt say which of the faults are visibly PRESENT and which are visibly ABSENT.
- The frames decide. What the coach says tells you which fault is being pointed at; it does not show that the fault happens in these frames. A coach describing a mistake and then performing it correctly is common: the same words can go with a wrong and a right attempt.
- present: you can see the fault in the frames.
- absent: the body part or aspect needed to judge the fault is in view, you would have seen the fault if it were there, and you see none of it. A person doing the movement well is an attempt where the faults are absent: say so, do not leave everything unjudged.
- Anything you cannot judge from the frames (wrong camera angle, body part hidden or too small, fault not about posture) is left out of both lists. Do not guess. Most faults will be left out of most attempts.
- not_an_attempt is true when the frames do not show one repetition of the activity.
- stroke: name the movement you see in the frames (what the player does, not what the video title says); view_clean: one player, whole body followable.
- Use only the ids above. Answer by calling the submit_labels tool exactly once."""


def _content(activity, faults, attempts, frames, cues_text):
    words = (f"The coach's words with their times in the video:\n{cues_text}\n" if cues_text else "There are no captions for this video; judge from the frames alone.")
    blocks = [{"type": "text", "text": PROMPT.format(
        activity=activity.replace("_", " "), n=len(attempts), k=FRAMES, words=words,
        faults="\n".join(f"- {f['id']}: {f.get('looks_like') or f['description']}" for f in faults))}]
    for n, ((a, b), (imgs, times)) in enumerate(zip(attempts, frames), 1):
        blocks.append({"type": "text", "text": f"Attempt {n}: video time {_mmss(a)}-{_mmss(b)} ({a:.1f}-{b:.1f} s); frames at {', '.join(str(t) for t in times)} s"})
        for im in imgs:
            blocks.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    return blocks


def ask_labels(activity, faults, attempts, frames, cues_text, model=None, client=None, retries=2):
    """-> {n (1-based): {not_an_attempt, present, absent}} for the attempts, or {} if the model gave no usable answer."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic(timeout=120.0, max_retries=2)
    ids = {f["id"] for f in faults}
    content = _content(activity, faults, attempts, frames, cues_text)
    for i in range(retries + 1):
        try:
            resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=4000,
                                          tools=[{"name": "submit_labels", "description": "Submit the labels.", "input_schema": LABEL_SCHEMA}],
                                          messages=[{"role": "user", "content": content}])
        except Exception:
            time.sleep(5); continue
        for b in resp.content:
            if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(LABEL_SCHEMA).iter_errors(b.input)):
                out = {}
                for r in b.input["attempts"]:
                    if 1 <= r["n"] <= len(attempts):
                        pres = [x for x in dict.fromkeys(r["present"]) if x in ids]
                        out[r["n"]] = {"not_an_attempt": bool(r["not_an_attempt"]), "stroke": str(r["stroke"]).strip().lower(), "view_clean": bool(r["view_clean"]), "present": pres,
                                       "absent": [x for x in dict.fromkeys(r["absent"]) if x in ids and x not in pres]}
                if out:
                    return out
    return {}


# ---------------------------------------------------------------- the structure of a video (what the coach is doing when)
STRUCTURE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["segments"], "properties": {
    "segments": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["start", "end", "kind", "note"],
        "properties": {
            "start": {"type": "number", "description": "seconds from the start of the video"},
            "end": {"type": "number", "description": "seconds from the start of the video"},
            "kind": {"type": "string", "enum": ["talking", "wrong_demo", "right_demo", "mixed_demo", "match_play", "other"],
                     "description": "talking = coach speaks with no swings; wrong_demo = swings shown as the mistake; right_demo = swings shown as the correct way; mixed_demo = both or cannot tell; match_play = real play or practice with no teaching; other"},
            "note": {"type": "string", "description": "one short line: what the coach says or shows here, naming the fault or correction if there is one"},
            "faults": {"type": "array", "items": {"type": "string"}, "description": "ids (from the list given) of the faults this segment is about: for a wrong_demo the faults being shown, for a right_demo the faults being corrected; empty when none of the listed faults is addressed"}}}}}}

STRUCTURE_PROMPT = """Activity: {activity}

This is a coaching video of {dur:.0f} seconds. Below are its captions with times, then {k} frames spread over the whole video with their times.

Split the whole video into consecutive segments and say what is going on in each, so that later every single swing can be placed in the right part of the video.
- wrong_demo: the coach (or someone) performs the movement the way it should NOT be done, usually while naming the mistake
- right_demo: the movement is performed the correct way, usually right after a wrong_demo
- mixed_demo: swings are shown but you cannot tell whether they are the mistake or the correction
- talking: speech with no swings; match_play: real play or plain practice with no teaching; other: titles, ads, anything else
- Use the words AND the frames: the same words ("keep your elbow in") often come with a wrong swing first and a right swing after. Put the boundary where the swing changes, not where the sentence ends.
- faults: for wrong_demo and right_demo segments, give the ids of the listed coach faults the segment is about (the mistake being shown, or the mistake being corrected). Use only ids from the list; leave empty when none fits.
- Segments must cover the video without gaps, in time order, 3 to 15 segments. Answer by calling the submit_structure tool exactly once."""


def ask_structure(activity, duration, cues_text, frames, model=None, client=None, retries=2, faults=None):
    """-> [{start, end, kind, note}] covering the video, or [] when the model gave no usable answer. frames = (base64 images, times)."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic(timeout=120.0, max_retries=2)
    imgs, times = frames
    blocks = [{"type": "text", "text": STRUCTURE_PROMPT.format(activity=activity.replace("_", " "), dur=duration, k=len(imgs)) +
               ("\n\nCoach faults (id: what it looks like):\n" + "\n".join(f"- {f['id']}: {f.get('looks_like') or f.get('description', '')}" for f in faults) if faults else "") +
               "\n\nCaptions:\n" + (cues_text or "(no captions)")}]
    ids = {f["id"] for f in faults or []}
    for im, t in zip(imgs, times):
        blocks.append({"type": "text", "text": f"Frame at {t:.0f} s ({_mmss(t)})"})
        blocks.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": im}})
    for _ in range(retries + 1):
        try:
            resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=3000,
                                          tools=[{"name": "submit_structure", "description": "Submit the segments.", "input_schema": STRUCTURE_SCHEMA}],
                                          messages=[{"role": "user", "content": blocks}])
        except Exception:
            time.sleep(5); continue
        for b in resp.content:
            if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(STRUCTURE_SCHEMA).iter_errors(b.input)):
                segs = sorted((dict(start=float(x["start"]), end=float(x["end"]), kind=x["kind"], note=str(x["note"])[:200],
                                    faults=[i for i in dict.fromkeys(x.get("faults") or []) if i in ids]) for x in b.input["segments"]),
                              key=lambda x: x["start"])
                if segs:
                    return segs
    return []


def segment_at(segments, window):
    """The segment holding the middle of the window (or None)."""
    m = (window[0] + window[1]) / 2
    for s in segments or []:
        if s["start"] <= m <= s["end"]:
            return s
    return None


def structure_text(segments):
    return "Structure of this video (worked out from the whole video; use it to tell a mistake being shown from the correction):\n" + \
        "\n".join(f"- {_mmss(s['start'])}-{_mmss(s['end'])} {s['kind']}: {s['note']}" for s in segments)


# ---------------------------------------------------------------- the labelling run
def path(work_dir, activity):
    return os.path.join(work_dir, activity, "labels.json")


def load(work_dir, activity):
    p = path(work_dir, activity)
    return json.load(open(p)) if os.path.exists(p) else None


def candidates(cols, min_s=0.8, max_s=20.0, min_prom=0.15, cap=15):
    """Every attempt the movement detector found, before the size, shape and cap filters: those filters were made to drop things that are not
    attempts, but they also drop the odd, shallow or slow ones, which is exactly what a mistake video shows. The model says whether a window is an attempt.
    Only windows of a plausible length and size are shown (at most `cap` per video, evenly spread)."""
    import numpy as np
    out = []
    for c in cols:
        keep = [i for i, (p, d) in enumerate(zip(c["prominence"], c["duration"])) if p >= min_prom and min_s <= d <= max_s]
        if len(keep) > cap:
            keep = [keep[int(j)] for j in np.round(np.linspace(0, len(keep) - 1, cap)).astype(int)]
        out.append(dict(c, windows=[c["windows"][i] for i in keep], attempts=[c["attempts"][i] for i in keep], usable=bool(keep)))
    return out


def trusted(lab):
    """trusted(clip id, window): the attempt has been looked at and is a real attempt of the activity (or None when nothing is labelled)."""
    if not lab:
        return None
    return lambda cid, window: (lambda r: r is not None and not r["not_an_attempt"])(find(lab, cid, window))


def clips_to_label(sources, cols, videos_dir):
    """Clips from videos that are about mistakes, that have attempts, and whose video file is still here."""
    by = {x["id"]: x for x in sources}
    out = []
    for c in cols:
        x = by.get(c["clip_id"])
        if not x or not c["usable"] or not c["attempts"] or not video_file(videos_dir, x["id"]):
            continue
        if x.get("tier") == "mistake_analysis" or x.get("shows") in ("mistakes", "mixed"):
            out.append((c, x))
    return out


def estimate(todo):
    n_att = sum(len(c["windows"]) for c, _ in todo)
    return {"clips": len(todo), "attempts": n_att, "images": n_att * FRAMES,
            "input_tokens": n_att * FRAMES * TOKENS_PER_IMAGE + len(todo) * (TRANSCRIPT_CHARS // 4 + 1500)}


def needs_labels(lab, c):
    """True when a video has not been labelled, or its attempts are cut differently now (an earlier cut of the same video leaves no label for them)."""
    if c["clip_id"] not in lab["clips"]:
        return True
    found = sum(find(lab, c["clip_id"], w) is not None for w in c["windows"])
    return found < 0.5 * len(c["windows"])                      # most of today's attempts have no label: the video was cut differently when it was labelled


ALIAS_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["matches"], "properties": {"matches": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["old", "current"],
    "properties": {"old": {"type": "string"}, "current": {"type": ["string", "null"], "description": "id of the current fault that is the same fault, or null if none is"}}}}}}


def reconcile(lab, faults, model=None, client=None):
    """Labels made under earlier names of the coaches' faults keep their meaning: each old id is matched to the current fault that is
    the same thing (or dropped), once, and the matches are saved. Returns the number of old ids found."""
    ids = {f["id"] for f in faults}
    seen = {x for rec in lab["clips"].values() for a in rec["attempts"] for x in a["present"] + a["absent"]}
    alias = lab.setdefault("aliases", {})
    todo = sorted(x for x in seen if x not in ids and x not in alias)
    if todo:
        if client is None:
            import anthropic
            client = anthropic.Anthropic(timeout=120.0, max_retries=2)
        cur = "\n".join(f"- {f['id']}: {f.get('looks_like') or f['description']}" for f in faults)
        prompt = ("These are the coaches' faults now:\n" + cur + "\n\nEarlier labels used these names for faults. For each, give the current fault id that is the SAME fault "
                  "(same thing going wrong, not merely related), or null if no current fault is the same:\n" + "\n".join(f"- {x.replace('_', ' ')} ({x})" for x in todo)
                  + "\n\nAnswer by calling the submit_matches tool exactly once.")
        got = {}
        for _ in range(3):
            try:
                resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=2000,
                                              tools=[{"name": "submit_matches", "description": "Submit the matches.", "input_schema": ALIAS_SCHEMA}],
                                              messages=[{"role": "user", "content": prompt}])
            except Exception:
                time.sleep(5); continue
            for b in resp.content:
                if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(ALIAS_SCHEMA).iter_errors(b.input)):
                    got = {m["old"]: (m["current"] if m["current"] in ids else None) for m in b.input["matches"] if m["old"] in todo}
            if got:
                break
        if not got:
            return 0                                           # nothing learned: try again next time rather than treat the old names as unmatched for good
        for x in todo:
            alias[x] = got.get(x)
    if alias:
        for rec in lab["clips"].values():
            for a in rec["attempts"]:
                for k in ("present", "absent"):
                    a[k] = list(dict.fromkeys(alias.get(x, x) if x not in ids else x for x in a[k] if (x in ids or alias.get(x))))
                a["absent"] = [x for x in a["absent"] if x not in a["present"]]
    return len(todo)


def label_activity(activity, work_dir, model=None, client=None, refresh=False, estimate_only=False, log=print,
                   frames=grab_frames, cues=None, use_comments=False, use_structure=False):
    """Label the attempts of every mistake video that has not been labelled yet. Saves after every video, so a stopped run resumes."""
    from . import pipeline, knowledge as K
    cues = cues or (lambda url: K.parse_vtt_timed(K.fetch_vtt(url) or ""))
    d = os.path.join(work_dir, activity)
    kmap = K.load(work_dir, activity)
    if not kmap:
        raise RuntimeError("no coaching knowledge yet: run learn first (the labels are about the faults coaches name)")
    prior = pipeline.load_prior(work_dir, activity, model)
    clips_dir = os.path.join(d, "clips")
    events, _ = pipeline.supported_events(clips_dir, prior["attempt_events"], prior["primary_features"])
    cols = candidates(pipeline.load_collections(clips_dir, events, None, prior["primary_features"]))
    sources = json.load(open(os.path.join(d, "sources.json")))
    lab = load(work_dir, activity) or {"model": model or DEFAULT_MODEL, "faults": [], "clips": {}}
    if refresh:
        lab["clips"] = {}
    lab["faults"] = [f["id"] for f in kmap["faults"]]
    if reconcile(lab, kmap["faults"], model, client):
        json.dump(lab, open(path(work_dir, activity), "w"), indent=1)
    todo = [(c, x) for c, x in clips_to_label(sources, cols, os.path.join(d, "videos")) if needs_labels(lab, c)]
    est = estimate(todo)
    log(f"     {est['clips']} videos to label: {est['attempts']} attempts, {est['images']} frames, about {est['input_tokens'] // 1000}k input tokens "
        f"({est['clips']} model calls)")
    if estimate_only or not todo:
        return lab, est
    for i, (c, x) in enumerate(todo, 1):
        wins = [tuple(w) for w in c["windows"]]
        vid = video_file(os.path.join(d, "videos"), x["id"])
        fr = [frames(vid, a, b) for a, b in wins]
        try:
            raw = cues(x["url"])
        except Exception:
            raw = []
        txt = transcript_text(raw) if raw else ""
        if use_comments:
            from . import comments as CM
            ct = CM.text_for(CM.cached(d, x["id"], x["url"]), wins)
            txt = (txt + "\n\n" + ct).strip() if ct else txt
        segs = []
        if use_structure:
            segs = (lab.setdefault("structure", {})).get(c["clip_id"]) or []
            if not segs and vid:
                dur = float(x.get("duration") or max(b for _, b in wins) + 5)
                sf = grab_frames(vid, 0, max(1.0, dur - 1), k=12, width=448)
                full = transcript_text(raw, max_chars=24000) if raw else ""
                segs = ask_structure(activity, dur, full, sf, model, client, faults=kmap["faults"])
                if segs:
                    lab["structure"][c["clip_id"]] = segs
            if segs:
                txt = (structure_text(segs) + "\n\n" + txt).strip()
        got = ask_labels(activity, kmap["faults"], wins, fr, txt, model, client)
        if not got:
            log(f"     {i}/{len(todo)}  {x['id']}: no usable answer, left unlabelled")
            continue
        lab["clips"][c["clip_id"]] = {"attempts": [dict(window=list(w), **got[n], **({"segment": (segment_at(segs, w) or {}).get("kind"), "segment_faults": (segment_at(segs, w) or {}).get("faults", [])} if segs else {})) for n, w in enumerate(wins, 1) if n in got]}
        json.dump(lab, open(path(work_dir, activity), "w"), indent=1)
        n_p = sum(len(a["present"]) for a in lab["clips"][c["clip_id"]]["attempts"])
        log(f"     {i}/{len(todo)}  {(x.get('title') or '')[:50]}: {len(wins)} attempts, {n_p} faults seen")
    return lab, est


# ---------------------------------------------------------------- using the labels
def find(lab, clip_id, window, min_iou=0.4):
    """The label record of the attempt at this window of this clip (windows are matched by overlap, so a later run that cuts the attempts a little differently still finds them)."""
    if not lab or window is None:
        return None
    best, bi = None, min_iou
    for r in lab["clips"].get(clip_id, {}).get("attempts", []):
        a, b = r["window"]
        inter = max(0.0, min(b, window[1]) - max(a, window[0]))
        iou = inter / max(1e-9, (b - a) + (window[1] - window[0]) - inter)
        if iou >= bi:
            best, bi = r, iou
    return best


def tags_for(lab, faults_of):
    """tags_for(objective id, meta) -> 'good' / 'bad' / 'unlabelled' per attempt, or None when no coach fault is linked to the objective.
    bad: a linked fault is visibly present. good: every linked fault is visibly absent. Anything else is unlabelled."""
    def f(oid, meta):
        F = set(faults_of.get(oid, ()))
        if not F or not lab:
            return None
        out = []
        for m in meta:
            r = find(lab, m["clip_id"], m.get("window"))
            if r is None or r["not_an_attempt"]:
                out.append("unlabelled")
            elif F & set(r["present"]):
                out.append("bad")
            elif F <= set(r["absent"]):
                out.append("good")
            elif F & set(r.get("segment_faults") or ()) and r.get("segment") == "wrong_demo":
                out.append("bad")          # the coach shows this very fault here (same video, same player, same camera as the right demo)
            elif F & set(r.get("segment_faults") or ()) and r.get("segment") == "right_demo":
                out.append("good")         # ... and the correction of it here
            else:
                out.append("unlabelled")
        return out
    return f


def summary(lab):
    """What the labels hold: per fault, the attempts where it is present or absent and in how many videos."""
    per = {}
    n_att = n_not = 0
    for cid, rec in lab["clips"].items():
        for a in rec["attempts"]:
            n_att += 1
            n_not += a["not_an_attempt"]
            if a["not_an_attempt"]:
                continue
            for k in ("present", "absent"):
                for fid in a[k]:
                    r = per.setdefault(fid, {"present": 0, "absent": 0, "clips_present": set(), "clips_absent": set()})
                    r[k] += 1; r["clips_" + k].add(cid)
    return {"videos": len(lab["clips"]), "attempts": n_att, "not_attempts": n_not,
            "per_fault": {fid: {"present": r["present"], "absent": r["absent"], "videos_present": len(r["clips_present"]), "videos_absent": len(r["clips_absent"])}
                          for fid, r in sorted(per.items())}}
