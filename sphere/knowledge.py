"""Coaching knowledge: what the people who teach an activity say about it.

For one activity the factory finds videos in which coaches explain technique and correct mistakes, reads what they say
(the transcript is read once and thrown away), and keeps only short structured notes: the faults they name, whether they
call them a safety matter or a matter of form, what causes them (from the most direct cause to the most fundamental), how
they fix them, and what the result looks like when it goes wrong. Many sources are then merged by meaning, and each point
records how many different sources made it. Disagreement is kept and marked, never averaged away.

Nothing here decides a threshold. It tells the proposal stage what is worth testing and tells the app what to say and
in what order to look for causes."""
import json
import math
import os
import re
import tempfile
import time
import jsonschema
from . import sources as S

DEFAULT_MODEL = os.environ.get("SPHERE_MODEL", "claude-sonnet-5-5")
MAX_CHARS = 24000                     # transcript characters read per video (about 20 minutes of speech)

QUERY_TEMPLATES = ["{a} common mistakes and how to fix them", "{a} technique explained by a coach", "{a} biggest mistakes",
                   "how to improve your {a}", "{a} form check tips", "{a} drills to fix technique"]


# ---------------------------------------------------------------- transcripts
def parse_vtt(text):
    """Plain speech from a WebVTT caption file. Automatic captions repeat each line as it scrolls; repeats are dropped."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in line or re.fullmatch(r"\d+", line):
            continue
        line = re.sub(r"<[^>]+>", "", line).replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").strip()
        if line and not (out and line in out[-1]):               # a caption line is repeated in the next caption
            out.append(line)
    return " ".join(out)


CAPTION_STATS = {"fetched": 0, "none": 0, "rate_limited": 0}
_LAST_REQUEST = [0.0]
MIN_GAP_S = 6.0           # captions are asked for no faster than this, whoever asks (YouTube refuses quick successions)


class _Quiet:
    """Collects what yt-dlp says instead of printing it, so a rate limit can be told from a video that simply has no captions."""
    def __init__(self):
        self.msgs = []
    def debug(self, m): pass
    def info(self, m): pass
    def warning(self, m): self.msgs.append(str(m))
    def error(self, m): self.msgs.append(str(m))


def fetch_vtt(url, wait=20, tries=5):
    """The raw English caption file (WebVTT) of one video, or None. Only the captions are fetched, never the video.
    Requests are spaced out; on "too many requests" it waits longer each time (20, 40, 80, 120 s); a video with no captions is not retried.
    If SPHERE_COOKIES is set to a browser name (chrome, safari, firefox), that browser's YouTube sign-in is used, which is limited much less."""
    import random
    import time
    import yt_dlp
    for attempt in range(tries):
        gap = MIN_GAP_S + random.uniform(0, 3) - (time.time() - _LAST_REQUEST[0])
        if gap > 0:
            time.sleep(gap)
        _LAST_REQUEST[0] = time.time()
        log = _Quiet()
        with tempfile.TemporaryDirectory() as tmp:
            opts = {"quiet": True, "no_warnings": True, "skip_download": True, "writesubtitles": True, "writeautomaticsub": True, "logger": log,
                    "subtitleslangs": ["en", "en-US", "en-GB", "en-orig"], "subtitlesformat": "vtt", "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
                    "sleep_interval_subtitles": 2, "retries": 2, "extractor_retries": 2}
            if os.environ.get("SPHERE_COOKIES"):
                opts["cookiesfrombrowser"] = (os.environ["SPHERE_COOKIES"],)
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                log.msgs.append(str(e))
            for f in sorted(os.listdir(tmp)):
                if f.endswith(".vtt"):
                    CAPTION_STATS["fetched"] += 1
                    return open(os.path.join(tmp, f), encoding="utf-8", errors="ignore").read()
        limited = any("429" in m or "Too Many Requests" in m for m in log.msgs)
        if not limited:
            CAPTION_STATS["none"] += 1              # no captions, or the video is unavailable: asking again changes nothing
            return None
        if attempt < tries - 1:
            time.sleep(min(120, wait * 2 ** attempt))
    CAPTION_STATS["rate_limited"] += 1
    return None


def caption_summary():
    c = CAPTION_STATS
    n = c["fetched"] + c["none"] + c["rate_limited"]
    if not n:
        return ""
    return (f"captions: {c['fetched']} of {n} videos fetched" + (f", {c['none']} have none" if c["none"] else "")
            + (f", {c['rate_limited']} refused by YouTube (too many requests)" if c["rate_limited"] else ""))


def fetch_transcript(url, wait=15):
    """English captions of one video as plain text, or None."""
    raw = fetch_vtt(url, wait)
    return parse_vtt(raw) if raw else None


def parse_vtt_timed(text):
    """Captions with their times: [(start seconds, end seconds, text)]. Automatic captions show each line twice as it scrolls; only the new line of each caption is kept."""
    def secs(h):
        parts = [float(x) for x in h.replace(",", ".").split(":")]
        return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
    out, prev = [], set()
    for block in re.split(r"\n\s*\n", text):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        for i, l in enumerate(lines):
            m = re.match(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", l)
            if m:
                body = [re.sub(r"<[^>]+>", "", x).replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").strip() for x in lines[i + 1:]]
                body = [x for x in body if x]
                new = [x for x in body if x not in prev]
                prev = set(body)
                if new:
                    out.append((secs(m.group(1)), secs(m.group(2)), " ".join(new)))
                break
    return out


# ---------------------------------------------------------------- notes from one video
NOTES_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["about_this_activity", "good_form", "faults"], "properties": {
    "about_this_activity": {"type": "boolean", "description": "true only if the speaker teaches technique for this activity in this video"},
    "good_form": {"type": "array", "items": {"type": "string"}, "description": "key points of correct technique the speaker gives, one short sentence each"},
    "faults": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["name", "kind", "looks_like", "why_it_matters", "causes", "fixes", "outcome_effects"],
        "properties": {
            "name": {"type": "string", "description": "a short plain name for the mistake"},
            "kind": {"enum": ["safety", "form"], "description": "safety only if the speaker says it risks injury or strain; otherwise form"},
            "looks_like": {"type": "string", "description": "what the body does, in the speaker's terms"},
            "why_it_matters": {"type": "string"},
            "causes": {"type": "array", "items": {"type": "string"}, "description": "what the speaker says leads to it, the most direct cause first, deeper causes after"},
            "fixes": {"type": "array", "items": {"type": "string"}, "description": "the corrections, cues or drills the speaker gives, paraphrased"},
            "outcome_effects": {"type": "array", "items": {"type": "string"}, "description": "what goes wrong in the result when it happens (ball goes long, balance lost, ...)"}}}}}}

NOTES_PROMPT = """Activity: {activity}

Below is the transcript of one video. Report only what the speaker says about technique for this activity. Do not add anything \
from your own knowledge, do not judge whether the speaker is right, and do not invent mistakes the speaker does not name. \
If the video is not teaching this activity, set about_this_activity to false and leave the lists empty. Paraphrase; do not copy sentences. \
Mark a fault 'safety' only when the speaker says it risks injury or strain.

TRANSCRIPT:
{text}

Answer by calling the submit_notes tool exactly once."""


def read_video(activity, text, model=None, client=None, retries=2):
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    for _ in range(retries + 1):
        resp = client.messages.create(
            model=model or DEFAULT_MODEL, max_tokens=4000,
            tools=[{"name": "submit_notes", "description": "Submit the notes.", "input_schema": NOTES_SCHEMA}],
            messages=[{"role": "user", "content": NOTES_PROMPT.format(activity=activity.replace("_", " "), text=text[:MAX_CHARS])}])
        for b in resp.content:
            if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(NOTES_SCHEMA).iter_errors(b.input)):
                return b.input
    return None


# ---------------------------------------------------------------- merge many sources
MAP_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["good_form", "faults"], "properties": {
    "good_form": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["point", "sources"],
        "properties": {"point": {"type": "string"}, "sources": {"type": "array", "items": {"type": "integer"}}}}},
    "faults": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "description", "kind", "sources", "causes", "fixes", "outcome_effects", "disagreement"],
        "properties": {
            "id": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
            "description": {"type": "string"},
            "kind": {"enum": ["safety", "form"]},
            "sources": {"type": "array", "items": {"type": "integer"}, "description": "numbers of the sources that name this fault"},
            "causes": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["cause", "proximity"],
                "properties": {"cause": {"type": "string"},
                               "proximity": {"enum": ["direct", "upstream", "fundamental"],
                                             "description": "direct: the movement itself; upstream: an earlier part of the movement; fundamental: balance, gaze, timing, setup, strength or mobility"}}}},
            "fixes": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["idea", "type"],
                "properties": {"idea": {"type": "string"}, "type": {"enum": ["cue", "drill", "setup"]}}}},
            "outcome_effects": {"type": "array", "items": {"type": "string"}},
            "disagreement": {"type": "string", "description": "empty unless sources disagree about this fault; then say how"}}}}}}

MAP_PROMPT = """Activity: {activity}

Below are notes from {n} different videos in which coaches teach this activity, numbered 0 to {last}. Merge them into one map of \
what coaches say. Rules:
- Merge faults that are the same mistake in different words. Give each merged fault a short snake_case id.
- For every fault and good-form point list the numbers of the sources that made it (only numbers that really appear below).
- Keep a fault named by a single source: it stays in the map and the count shows it is single.
- Order causes from direct to upstream to fundamental. Do not add causes, fixes or faults that no source gave.
- If sources disagree (for example one coach says a thing is a fault and another says it is fine, or they give opposite fixes), say so in 'disagreement'.
- kind is 'safety' only if at least one source says the pattern risks injury or strain.
- The activity may name a variant (for example bodyweight squat). Leave out advice that only applies to a different variant, such as barbell or heavy-load advice for a bodyweight activity, even if a source gave it.
- Keep it compact: at most 20 faults, at most 5 causes and 5 fixes per fault, every text one short sentence.

NOTES:
{notes}

Answer by calling the submit_map tool exactly once."""


def _complete(client, **kw):
    """One model call. A long answer is streamed, because a long silent wait can make the connection drop."""
    m = client.messages
    if hasattr(m, "stream"):
        with m.stream(**kw) as s:
            return s.get_final_message()
    return m.create(**kw)


def merge(activity, notes, model=None, client=None, retries=2):
    """notes: list of per-video notes (about_this_activity true). Returns the merged map with source counts computed here.
    If the model's answer is cut off, does not fit the format, or the connection drops, it is asked again (with the reason when
    the answer was rejected); if it still fails the merge is done in smaller steps."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    text = "\n\n".join(f"SOURCE {i}:\n" + json.dumps({k: v for k, v in n.items() if k != "about_this_activity"}) for i, n in enumerate(notes))
    prompt = MAP_PROMPT.format(activity=activity.replace("_", " "), n=len(notes), last=len(notes) - 1, notes=text)
    last, rejected = "no tool call in the reply", None
    for _ in range(retries + 1):
        extra = f"\n\nYour previous answer was rejected: {rejected}. Fix that, and keep every text short." if rejected else ""
        try:
            resp = _complete(client, model=model or DEFAULT_MODEL, max_tokens=16000,
                             tools=[{"name": "submit_map", "description": "Submit the merged map.", "input_schema": MAP_SCHEMA}],
                             messages=[{"role": "user", "content": prompt + extra}])
        except Exception as e:                      # the connection dropped or the service answered with an error
            last = f"the connection to the model failed ({type(e).__name__})"
            time.sleep(5)
            continue
        if getattr(resp, "stop_reason", None) == "max_tokens":
            last = rejected = "the answer was cut off for length; use fewer, shorter entries"
            continue
        for b in resp.content:
            if b.type == "tool_use":
                errs = list(jsonschema.Draft202012Validator(MAP_SCHEMA).iter_errors(b.input))
                if not errs:
                    return _count(b.input, len(notes))
                last = rejected = "; ".join(f"{list(e.path)}: {e.message[:90]}" for e in errs[:3])
    print(f"     one-step merge failed ({last}); merging in smaller steps ...", flush=True)
    return merge_in_parts(activity, notes, model, client)


CLUSTER_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["clusters"], "properties": {
    "clusters": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "members"],
        "properties": {"id": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
                       "members": {"type": "array", "items": {
                           "type": "object", "additionalProperties": False, "required": ["source", "fault"],
                           "properties": {"source": {"type": "integer"}, "fault": {"type": "integer"}}}}}}}}}

DETAIL_SCHEMA = MAP_SCHEMA["properties"]["faults"]["items"]
_DETAIL_PROPS = {k: v for k, v in DETAIL_SCHEMA["properties"].items() if k not in ("id", "sources")}
DETAIL_SCHEMA = {"type": "object", "additionalProperties": False, "required": [k for k in DETAIL_SCHEMA["required"] if k not in ("id", "sources")],
                 "properties": _DETAIL_PROPS}
GOOD_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["good_form"], "properties": {"good_form": MAP_SCHEMA["properties"]["good_form"]}}


def _ask(client, model, tool, schema, prompt, retries=2, max_tokens=4000):
    last = "no tool call in the reply"
    for _ in range(retries + 1):
        try:
            resp = _complete(client, model=model or DEFAULT_MODEL, max_tokens=max_tokens,
                             tools=[{"name": tool, "description": "Submit the answer.", "input_schema": schema}],
                             messages=[{"role": "user", "content": prompt + (f"\n\nYour previous answer was rejected: {last}." if last != "no tool call in the reply" else "")}])
        except Exception:                           # a dropped connection: wait and ask again
            time.sleep(5)
            continue
        for b in resp.content:
            if b.type == "tool_use":
                errs = list(jsonschema.Draft202012Validator(schema).iter_errors(b.input))
                if not errs:
                    return b.input
                last = "; ".join(f"{list(e.path)}: {e.message[:80]}" for e in errs[:3])
    return None


def merge_in_parts(activity, notes, model=None, client=None, max_faults=24):
    """The same merge in small steps, for when a single answer is too long or does not fit the format: (1) group the faults that
    are the same mistake, from a short list; (2) write each group from the notes of its members; (3) merge the good-form
    points. Which sources made a point is taken from the group members, not from anything the model states."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    name = activity.replace("_", " ")
    lines = [f"S{i}.{j} | {f['name']} | {f['kind']} | {f['looks_like'][:110]}" for i, n in enumerate(notes) for j, f in enumerate(n["faults"])]
    got = _ask(client, model, "submit_clusters", CLUSTER_SCHEMA,
               f"Activity: {name}\n\nFaults named by coaches in {len(notes)} videos (S<video>.<fault> | name | kind | what it looks like). Group the ones that are the same "
               "mistake in different words. Give each group a short snake_case id and list its members as source (video number) and fault (fault number within that video). "
               "A fault that matches nothing else is its own group. Leave out advice that only applies to a different variant of the activity (barbell or heavy-load advice for a bodyweight activity).\n\n"
               + "\n".join(lines) + "\n\nAnswer by calling the submit_clusters tool exactly once.", max_tokens=8000)
    if not got:
        raise RuntimeError("the model could not group the coaching faults")
    faults, used = [], set()
    for c in got["clusters"]:
        mem = sorted({(m["source"], m["fault"]) for m in c["members"] if 0 <= m["source"] < len(notes) and 0 <= m["fault"] < len(notes[m["source"]]["faults"])})
        if not mem:
            continue
        cid, k = c["id"], 2
        while cid in used:
            cid, k = f"{c['id']}_{k}", k + 1
        used.add(cid)
        recs = "\n".join(f"SOURCE {i}: " + json.dumps(notes[i]["faults"][j]) for i, j in mem)
        d = _ask(client, model, "submit_fault", DETAIL_SCHEMA,
                 f"Activity: {name}\n\nCoaches' notes on one mistake. Write it once. Order causes from direct to upstream to fundamental. "
                 "Do not add causes, fixes or effects that no note gave. If the notes disagree, say how in 'disagreement', otherwise leave it empty. "
                 "kind is 'safety' only if a note says it risks injury or strain. Keep every text one short sentence.\n\n" + recs
                 + "\n\nAnswer by calling the submit_fault tool exactly once.")
        if d:
            faults.append(dict(d, id=cid, sources=sorted({i for i, _ in mem})))
    pts = "\n".join(f"SOURCE {i}: {g}" for i, n in enumerate(notes) for g in n["good_form"])
    g = _ask(client, model, "submit_good_form", GOOD_SCHEMA,
             f"Activity: {name}\n\nKey points of correct technique from {len(notes)} coaching videos. Merge points that say the same, and list the numbers of the sources that made each. "
             "Leave out advice for a different variant of the activity. At most 20 points, one short sentence each.\n\n" + pts + "\n\nAnswer by calling the submit_good_form tool exactly once.", max_tokens=6000)
    if not faults:
        raise RuntimeError("no coaching fault could be written from the grouped notes")
    return _count({"good_form": (g or {"good_form": []})["good_form"], "faults": faults[:max_faults * 2]}, len(notes))


def _count(m, n):
    """Source counts come from the numbers the model cited, checked against the sources that exist; never from a number it states."""
    def srcs(x):
        return sorted({i for i in x["sources"] if isinstance(i, int) and 0 <= i < n})
    faults = []
    for f in m["faults"]:
        s = srcs(f)
        if not s:                                   # cites nothing real: not supported
            continue
        support = "strong" if len(s) >= max(3, math.ceil(0.4 * n)) else "some" if len(s) >= 2 else "single"
        faults.append(dict(f, sources=s, n_sources=len(s), support=support))
    faults.sort(key=lambda f: (-f["n_sources"], f["id"]))
    good = [dict(g, sources=srcs(g), n_sources=len(srcs(g))) for g in m["good_form"] if srcs(g)]
    good.sort(key=lambda g: -g["n_sources"])
    return {"n_sources": n, "good_form": good, "faults": faults}


# ---------------------------------------------------------------- the stage
def learn(activity, work_dir, n_videos=12, model=None, client=None, search=None, transcripts=None, log=print, refresh=False):
    """Find coaching videos, read them, merge. Writes work/<activity>/knowledge.json and returns it.
    The notes read from each video are saved first (coaching_notes.json), so if a later step fails, running again does not
    read the videos again; refresh=True reads them afresh. search/transcripts can be replaced for testing."""
    from . import acquire
    search = search or acquire.search
    transcripts = transcripts or fetch_transcript
    d = os.path.join(work_dir, activity)
    os.makedirs(d, exist_ok=True)
    npath = os.path.join(d, "coaching_notes.json")
    if os.path.exists(npath) and not refresh:
        saved = json.load(open(npath))
        notes, used = saved["notes"], saved["sources"]
        log(f"     using the {len(notes)} videos already read (--refresh reads them again)")
    else:
        name = activity.replace("_", " ")
        found, seen = [], set()
        for t in QUERY_TEMPLATES:
            q = t.format(a=name)
            log(f"     searching: {q}")
            try:
                res = search(q, 10, min_s=90, max_s=1500)
            except Exception as e:
                log(f"     search failed: {str(e)[:80]}")
                continue
            for it in res:
                if it["id"] not in seen:
                    seen.add(it["id"]); found.append(it)
        S.rate(activity, found, model, client)
        log("     videos by kind: " + ", ".join(f"{k} {v}" for k, v in sorted(S.tier_counts(found).items())))
        chosen = S.rank_for_knowledge(found, int(n_videos * 1.6))          # a few spare: some have no captions or are off topic
        notes, used = [], []
        for it in chosen:
            if len(notes) >= n_videos:
                break
            text = transcripts(it["url"])
            if not text or len(text) < 400:
                log(f"     no usable captions: {it['id']}")
                continue
            n = read_video(activity, text, model, client)
            if not n or not n["about_this_activity"] or not n["faults"]:
                log(f"     nothing on technique: {it['id']}")
                continue
            notes.append(n)
            used.append({"id": it["id"], "title": it.get("title"), "channel": it.get("channel"), "tier": it.get("tier")})
            log(f"     read {len(notes)}/{n_videos}: {(it.get('title') or '')[:60]}  [{it.get('channel')}]")
        if len(notes) < 2:
            raise RuntimeError(f"only {len(notes)} coaching video(s) with usable captions were found; need at least 2")
        json.dump({"sources": used, "notes": notes}, open(npath, "w"), indent=2)
    old = load(work_dir, activity)
    if old and not refresh and [u["id"] for u in old.get("sources", [])] == [u["id"] for u in used]:
        log("     the notes are already merged (the fault names stay as they are, so earlier labels keep their meaning)")
        return old
    log("     merging the notes of different coaches ...")
    kmap = merge(activity, notes, model, client)
    kmap["sources"] = used
    json.dump(kmap, open(os.path.join(d, "knowledge.json"), "w"), indent=2)
    return kmap


def load(work_dir, activity):
    p = os.path.join(work_dir, activity, "knowledge.json")
    return json.load(open(p)) if os.path.exists(p) else None


def effective_kind(f):
    """'safety' is claimed by the coaches' words, but a single source, or a point other coaches dispute, is not enough to call
    something a safety matter in an app that coaches people: it counts as form until two or more sources back it uncontested."""
    if f["kind"] == "safety" and f["n_sources"] >= 2 and not f.get("disagreement"):
        return "safety"
    return "form"


def for_prompt(kmap, max_faults=14):
    """The coaches' map as text for the proposal stage."""
    if not kmap:
        return ""
    L = [f"WHAT COACHES SAY ({kmap['n_sources']} different coaching videos). Faults they name, most-cited first:"]
    for f in kmap["faults"][:max_faults]:
        extra = f" DISAGREEMENT: {f['disagreement']}" if f.get("disagreement") else ""
        L.append(f"- {f['id']} [{effective_kind(f)}, named by {f['n_sources']} of {kmap['n_sources']}]: {f['description']}.{extra}")
    return "\n".join(L)


# ---------------------------------------------------------------- link the coaches' faults to what the camera measures
LINK_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["links"], "properties": {
    "links": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["fault", "objective", "measurable", "note"],
        "properties": {
            "fault": {"type": "string", "description": "id of a coaching fault"},
            "objective": {"type": ["string", "null"], "description": "id of the entry objective whose test covers this same thing, or null"},
            "measurable": {"enum": ["measured", "proxy", "feature_available", "needs_new_feature", "needs_new_tracker", "not_visible"],
                           "description": "measured: an objective's test shows this very thing; proxy: an objective's test shows something that goes with it but is not the thing itself; feature_available: a registered feature shows it but no objective tests it (for example because coaches disagree about the right value), name the feature in note; needs_new_feature: pose could show it but no registered feature does, name the feature that would be needed in note; needs_new_tracker: the camera can see it but not with the body skeleton, it needs hand landmarks or racket / ball / object detection (grip, forearm rotation, racket face, ball), name the tracker in note; not_visible: no camera can see it (feel, tension, breathing, sound, intention)"},
            "note": {"type": "string", "description": "for needs_new_feature or needs_new_tracker, what would be needed; otherwise empty"}}}}}}

LINK_PROMPT = """Coaches name these faults for {activity} (id: description):
{coach}

The entry already tests these objectives with the camera's body features (id: goal, feature):
{entry}

Registered features:
{feats}

For every coaching fault say which entry objective's test covers the same thing (objective, or null), and whether it is measured, measured only by a proxy, would need a new body feature, would need another tracker (hands, racket, ball), or cannot be seen at all and needs a question to the learner or another sensor. \
Be strict: 'measured' only when the objective's test shows the very thing the coach describes (knee position shows knees caving; it does not show heels lifting, which would be a proxy at best). Check the registered features before saying a new feature is needed or that the camera cannot see something: a coach point about stance width, foot direction or heel height can be matched to a feature that exists. \
Set objective whenever a test is a measure or a proxy of the coaching fault. When coaches say the right value depends on the person or disagree about it (stance width, toe angle), a target range can only be a proxy, and a registered feature with no test is feature_available. Answer by calling the submit_links tool exactly once."""


def link(kmap, objectives, feature_catalogue, activity, model=None, client=None, retries=2):
    """Returns (links by coaching fault id, entry objectives no coach names). objectives: [{id, goal, feature}]."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    ids = {f["id"] for f in kmap["faults"]}
    oids = {o["id"] for o in objectives}
    prompt = LINK_PROMPT.format(
        activity=activity.replace("_", " "),
        coach="\n".join(f"- {f['id']}: {f['description']}" for f in kmap["faults"]),
        entry="\n".join(f"- {o['id']}: {o['goal']} ({o['feature']})" for o in objectives),
        feats="\n".join(f"- {k}: {v}" for k, v in feature_catalogue.items()))
    got = {}
    for _ in range(retries + 1):
        resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=4000,
                                      tools=[{"name": "submit_links", "description": "Submit the links.", "input_schema": LINK_SCHEMA}],
                                      messages=[{"role": "user", "content": prompt}])
        for b in resp.content:
            if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(LINK_SCHEMA).iter_errors(b.input)):
                got = {l["fault"]: l for l in b.input["links"] if l["fault"] in ids}
        if got:
            break
    out = {}
    for f in kmap["faults"]:
        l = got.get(f["id"])
        ob = l["objective"] if l and l["objective"] in oids else None
        m = l["measurable"] if l else "not_visible"
        if ob and m not in ("measured", "proxy"):
            m = "proxy"                                              # names a test but did not say it is the thing itself: the weaker claim
        elif not ob and m in ("measured", "proxy"):
            m = "not_visible"                           # claims a measure but names no test: not measured
        out[f["id"]] = {"objective": ob, "measurable": m, "note": (l or {}).get("note", "") if m in ("needs_new_feature", "needs_new_tracker", "feature_available") else ""}
    named = {l["objective"] for l in out.values() if l["objective"]}
    return out, [o["id"] for o in objectives if o["id"] not in named]


def coaching_section(kmap, links, unsupported):
    """The part of the entry the app reads: what coaches say, how often, and what the camera can check."""
    faults = []
    for f in kmap["faults"]:
        l = links.get(f["id"], {})
        faults.append({"id": f["id"], "description": f["description"], "kind": effective_kind(f), "n_sources": f["n_sources"], "support": f["support"],
                       "causes": f["causes"], "fixes": f["fixes"], "outcome_effects": f["outcome_effects"], "disagreement": f.get("disagreement", ""),
                       "objective": l.get("objective"), "measurable": l.get("measurable", "not_visible"), "note": l.get("note", "")})
    return {"n_sources": kmap["n_sources"], "good_form": [{"point": g["point"], "n_sources": g["n_sources"]} for g in kmap["good_form"]],
            "faults": faults, "objectives_no_coach_names": unsupported}
