"""Rate candidate videos before anything is downloaded, from what the search already tells us (title, channel, length,
views). Two things are judged: what kind of video it is (tier) and what it shows (good form, mistakes, mixed).

The rating only orders the candidates; it never decides what is true about the
movement. Footage is chosen for being easy to measure (a person doing the movement, whole body, many repetitions) and for
coming from people who know the movement; the knowledge stage uses the talking videos."""
import os
import jsonschema

DEFAULT_MODEL = os.environ.get("SPHERE_MODEL", "claude-sonnet-5-5")
BATCH = 40

TIERS = ["coach_demo", "pro_footage", "practice_session", "mistake_analysis", "instruction_talk", "other"]
SHOWS = ["good_form", "mistakes", "mixed", "unknown"]

# Lower is better. 'other' (unrelated, compilations, vlogs) is the last choice but not excluded: rated from the title alone, it still
# held real repetitions in about a third of the squat footage, so it is only taken when better sources run out.
FOOTAGE_ORDER = {"coach_demo": 0, "pro_footage": 0, "practice_session": 1, "mistake_analysis": 2, "instruction_talk": 3, "other": 4}
KNOWLEDGE_ORDER = {"mistake_analysis": 0, "instruction_talk": 0, "coach_demo": 1}

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["ratings"], "properties": {
    "ratings": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["id", "tier", "shows"],
        "properties": {"id": {"type": "string"}, "tier": {"enum": TIERS}, "shows": {"enum": SHOWS}}}}}}

PROMPT = """Activity: {activity}

Below are search results (id | title | channel | seconds | views). Rate each one from what the listing tells you.

tier:
- coach_demo: a coach or instructor demonstrating or explaining how to do the activity correctly, with the body in view
- pro_footage: a skilled or professional performer doing the activity (match, competition, training footage), little or no talking
- practice_session: someone training, drilling or practising the activity, repeated attempts
- mistake_analysis: a video about errors, faults or corrections in this activity
- instruction_talk: mostly talking about the activity (tips, explanation, lessons), little of the movement shown
- other: probably not about performing this activity, or a compilation, gear review, vlog, reaction, news, highlights reel, or a different activity

shows (what the movement in it is likely to be):
- good_form: correct or skilled performance
- mistakes: errors or poor technique are the point of the video
- mixed: both (a coach shows the mistake and then the fix)
- unknown: the listing does not say

Titles can mislead. Use 'other' only when the listing clearly is not what the tiers describe. Rate every id.

{items}

Answer by calling the submit_ratings tool exactly once."""


def _line(it):
    return " | ".join(str(x) for x in (it["id"], (it.get("title") or "")[:110], it.get("channel") or "", it.get("duration") or "", it.get("views") or ""))


def rate(activity, items, model=None, client=None, retries=2):
    """Add 'tier' and 'shows' to each item (in place) and return the items. A video the model did not rate gets tier
    'unrated' and is kept: missing information is not a reason to throw footage away."""
    if not items:
        return items
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    todo = [it for it in items if not it.get("tier")]
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        ids = {it["id"] for it in chunk}
        got = {}
        for _ in range(retries + 1):
            resp = client.messages.create(
                model=model or DEFAULT_MODEL, max_tokens=3000,
                tools=[{"name": "submit_ratings", "description": "Submit the ratings.", "input_schema": SCHEMA}],
                messages=[{"role": "user", "content": PROMPT.format(activity=activity.replace("_", " "), items="\n".join(_line(it) for it in chunk))}])
            for b in resp.content:
                if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(b.input)):
                    got = {r["id"]: r for r in b.input["ratings"] if r["id"] in ids}
            if len(got) >= 0.9 * len(chunk):
                break
        for it in chunk:
            r = got.get(it["id"])
            it["tier"], it["shows"] = (r["tier"], r["shows"]) if r else ("unrated", "unknown")
    return items


def rank_for_footage(items, max_videos):
    """Best tiers first, search order inside a tier; 'other' only after everything else. A quarter of the places (at least two)
    are kept for videos that show mistakes, so the footage also holds faulty form to test the fault thresholds against."""
    keep = list(items)
    order = lambda it: FOOTAGE_ORDER.get(it.get("tier"), 2)             # unrated sits in the middle
    ranked = sorted(keep, key=order)                                     # sorted() is stable: search order is kept inside a tier
    wrong = [it for it in ranked if it.get("shows") in ("mistakes", "mixed")]
    reserve = wrong[:max(2, max_videos // 4)]
    chosen = list(reserve)
    for it in ranked:
        if len(chosen) >= max_videos:
            break
        if it not in chosen:
            chosen.append(it)
    return sorted(chosen[:max_videos], key=lambda it: ranked.index(it))


def rank_for_knowledge(items, n, per_channel=2):
    """Videos where someone explains the technique, from different channels (a single coach repeated is one opinion)."""
    keep = [it for it in items if it.get("tier") in KNOWLEDGE_ORDER]
    keep.sort(key=lambda it: KNOWLEDGE_ORDER[it["tier"]])
    seen, out = {}, []
    for it in keep:
        ch = it.get("channel") or it["id"]
        if seen.get(ch, 0) >= per_channel:
            continue
        seen[ch] = seen.get(ch, 0) + 1
        out.append(it)
        if len(out) >= n:
            break
    return out


def tier_counts(items):
    out = {}
    for it in items:
        k = it.get("tier") or "unrated"
        out[k] = out.get(k, 0) + 1
    return out
