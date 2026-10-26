"""Factory stage 1: the language model proposes an activity's structure, objectives, outcomes and
links, using only the registered vocabulary. It never chooses target ranges: those are taken from
real movement. Output is schema-constrained, validated and retried."""
import itertools
import os
import jsonschema
from .schema import PROPOSAL_SCHEMA
from .vocab import feature_catalogue

DEFAULT_MODEL = os.environ.get("SPHERE_MODEL", "claude-sonnet-5-5")

SYSTEM = """You are the knowledge-generation stage of a factory that builds coaching knowledge for ANY physical activity, \
for an app that watches a person practise through a phone camera and coaches them. You are given one activity name.

Rules:
- Describe the movement the way a good coach and the instructional literature would, but express every test ONLY with the \
registered body-frame features you are given (angles, heights, deviations, widths, all normalised to the person). \
Each objective's test says: which feature, at which phase boundary (start or end of a named phase). The objective is met \
when that feature is inside a target range. You do NOT choose the range; it is taken from footage of good performances.
- primary_features: the 2 to 6 registered features that change most during ONE attempt (the body parts that do the movement, not \nthe ones that merely accompany it). They are used to find repetitions in video, so choose features whose swing is large in a real attempt.
- attempt_events: what the body does, IN ORDER, in ONE attempt, as 1 to 4 events: each is a large excursion of one registered feature (from its rest value it rises, \
or falls, to an extreme and comes back). Choose events that are present in EVERY performance of the action, including poor ones. Never use a movement that is itself a coaching point, or that a common mistake shrinks or removes (for a forehand, the shoulder-hip twist: an arm-only swing lacks it, so such swings would never be found, and mistakes are exactly what must be found). Use as few events as will do, often one: the main swing or the main displacement. But the event must be big and characteristic of the action, so that a person talking, gesturing or walking does not trigger it: when it is defined by reaching a level, give peak_at_least. IMPORTANT: events must follow one another in time. Joints that move in the same moment are ONE event (a squat: the knees, hips and hip height all move together, so it is one event, named by the feature that shows it best); the other joints are checked through primary_features. They are used to find attempts in video, whether a clip holds one attempt or many, and must tell this action apart from \
every other movement a person makes: a squat is one event (height.hip falls); a serve is two (the tossing wrist rises overhead, then the hitting wrist rises overhead). Every feature \
used must be one of primary_features. Give each event's seconds: how long it takes in a typical attempt, from the feature leaving its rest value to being back (a tennis forehand swing about 1; a serve's toss about 1.5; a squat about 3). They are used to cut a rally or a set into single attempts. When an event is defined by reaching a level (a wrist overhead), give peak_at_least in the feature's units \
so that everyday gestures are not mistaken for it, yet small or hurried performances still reach it. Choose only events that are large and unmistakable even in distant, imperfect footage (a wrist overhead, the hips dropping); leave out subtle ones such as a shallow knee bend.
- Phases are the natural segments of ONE attempt (one rep, one shot, one cycle), in order.
- Objectives: what the person should achieve in the movement, each stated as the right thing to do ("keep the knees tracking over the toes"), \
not as a mistake. Include only things that change how well the person achieves the activity's purpose or that are plainly unconventional. \
For each objective say in 'sides' which way the feature can be wrong: 'below' (under the target range) and/or 'above' (over it). Describe \
BOTH sides when both are mistakes, each with how it looks and how serious it is (a mallet swing parallel to the horse: angled in risks \
the horse's head, angled out is a smaller error); describe only one when the other side is harmless or cannot happen (a squat deeper than \
the target). Give causes (objective ids that cause this one), an intent for the coaching cue, an intent for a clarifying question, \
and an intent for the fix. These are intents, not scripted sentences. Make no safety or medical claims of your own: \
set an objective's kind to 'safety' only when the coaching knowledge you are given calls a mistake against it a risk of injury or strain; otherwise 'form'.
- If you are given WHAT COACHES SAY, build the objective list from it: prefer the points many coaches make and that a registered feature \
can test, and when an objective you test answers a fault they name, use the coaches' id for it. A coach-named fault that no registered feature \
can show is not tested: list the feature it would need under vocabulary_proposals. Add an objective the coaches do not name only when the movement data \
points to it. Where coaches disagree, keep the objective only if the disagreement is about its fix, not about whether it matters.
- Outcomes: what the activity is trying to achieve and what must be observable to judge it (use short words such as \
"body", "ball", "landing_area", "net", "target"). If the form itself is the point, say so as an outcome that needs only "body".
- Links: technique features that influence an outcome, including adjustments within the normal range (levers), with the \
mechanism in one sentence.
- If a needed feature, trackable or measurement is missing from the registry, add it under vocabulary_proposals instead of \
stretching a feature.
- search_queries: queries that would find reference videos with one person, whole body in view, a mostly fixed camera: \
demonstrations, good-form instruction, and common-mistakes videos.
- confusable_with: activities easily mistaken for this one (used as negatives to test recognition).
- Be specific and conservative. Do not invent facts. Prefer fewer, well-grounded objectives to many speculative ones."""


def observed_text(obs):
    lines = [f"REAL MOVEMENT DATA. {obs['n_attempts']} attempts from {obs['n_clips']} real clips were segmented and time-normalised. "
             f"One attempt has {len(obs['landmarks'])} landmarks, so exactly {obs['n_phase']} phases (phase i runs from landmark i to landmark i+1). "
             "Median feature values at each landmark:"]
    for lm in obs["landmarks"]:
        vals = ", ".join(f"{k}={v}" for k, v in lm["values"].items())
        lines.append(f"- {lm['id']} (t={lm['t']}): {vals}")
    lines.append(f"Use this data to work out what each landmark physically is. Return EXACTLY {obs['n_phase']} phases, in order, "
                 "named and described for what really happens between consecutive landmarks. Place each objective's test and each link at the "
                 "phase boundary where it would actually show in this data (at_point 'start' = the landmark opening that phase, "
                 "'end' = the landmark closing it). If the data looks inconsistent with the activity, still follow the structure above.")
    return "\n".join(lines)


def build_prompt(activity, observed=None, knowledge=""):
    feats = "\n".join(f"- {k}: {v}" for k, v in feature_catalogue().items())
    extra = ("\n\n" + observed_text(observed)) if observed else ""
    extra += ("\n\n" + knowledge) if knowledge else ""
    return (f"Activity: {activity}\n\nRegistered features (the only things a test may use):\n{feats}{extra}\n\n"
            "You must answer by calling the submit_proposal tool exactly once. Do not reply with plain text.")


def propose_once(activity, model=None, client=None, retries=2, observed=None, knowledge=""):
    import anthropic
    client = client or anthropic.Anthropic()
    last = None
    for _ in range(retries + 1):
        resp = client.messages.create(
            model=model or DEFAULT_MODEL, max_tokens=8000, system=SYSTEM,
            tools=[{"name": "submit_proposal", "description": "Submit the activity proposal.", "input_schema": PROPOSAL_SCHEMA}],
            messages=[{"role": "user", "content": build_prompt(activity, observed, knowledge)}])
        for b in resp.content:
            if b.type == "tool_use":
                errs = list(jsonschema.Draft202012Validator(PROPOSAL_SCHEMA).iter_errors(b.input))
                if not errs and any(e["feature"] not in b.input["primary_features"] for e in b.input["attempt_events"]):
                    last = "every attempt_events feature must be one of primary_features"
                    continue
                if not errs and observed and len(b.input["phases"]) != observed["n_phase"]:
                    last = f"expected exactly {observed['n_phase']} phases, got {len(b.input['phases'])}"
                    continue
                if not errs:
                    return b.input
                last = "; ".join(e.message[:100] for e in errs[:3])
    raise RuntimeError(f"model did not return a valid proposal: {last or 'no tool call in the reply'}")


EVENTS_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["attempt_events"], "properties": {
    "attempt_events": {"type": "array", "minItems": 1, "maxItems": 4, "items": {
        "type": "object", "additionalProperties": False, "required": ["feature", "direction", "peak_at_least", "seconds"],
        "properties": {"feature": {"type": "string"}, "direction": {"enum": ["rises", "falls"]}, "peak_at_least": {"type": "number"}, "seconds": {"type": "number", "minimum": 0.2, "maximum": 30}}}}}}


def propose_events(activity, primary_features, model=None, client=None, retries=2):
    """The attempt events for an activity whose proposal was made before they existed."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic()
    from .features import FEATURE_DOC
    prompt = (f"Activity: {activity}\nPrimary features (with their units):\n" + "\n".join(f"- {f}: {FEATURE_DOC.get(f, '')}" for f in primary_features) + "\n\nWhat does the body do, IN ORDER, in ONE attempt, as 1 to 4 "
              "events? Each event is a large excursion of one of the primary features: from its rest value it rises (or falls) to an extreme and comes back. "
              "Choose events that are present in EVERY performance of the action, including poor ones. Never use a movement that is itself a coaching point, or that a common mistake shrinks or removes (for a forehand, the shoulder-hip twist: an arm-only swing lacks it, so such swings would never be found, and mistakes are exactly what must be found). Use as few events as will do, often one: the main swing or the main displacement. But the event must be big and characteristic of the action, so that a person talking, gesturing or walking does not trigger it: when it is defined by reaching a level, give peak_at_least. Events must follow one another in time. Joints that move in the same moment are ONE event (a squat: the knees, hips and hip height all move together, so it is one event, named by the feature that shows it best); the other joints are checked through primary_features. "
              "The events together must tell this action apart from every other movement a person makes (a squat: height.hip falls; a serve: the tossing "
              "wrist rises overhead, then the hitting wrist rises overhead). Give every event its peak_at_least, in the feature's units: the level the feature must reach for the event to count (for a feature that rises, at least this value; for one that falls, at most this value). Set it above what everyday gestures and other movements reach, so that this action is not confused with them, yet low enough that a poor, small or hurried performance of the action still reaches it. Give each event's seconds: how long it takes in a typical attempt, from the feature leaving its rest value to being back (a tennis forehand swing about 1; a serve's toss about 1.5; a squat about 3). Answer by calling the submit_attempt_events tool exactly once.")
    for _ in range(retries + 1):
        resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=600,
                                      tools=[{"name": "submit_attempt_events", "description": "Submit the attempt events.", "input_schema": EVENTS_SCHEMA}],
                                      messages=[{"role": "user", "content": prompt}])
        for b in resp.content:
            if b.type == "tool_use" and all(e.get("feature") in primary_features and e.get("peak_at_least") is not None for e in b.input.get("attempt_events", [])):
                return b.input["attempt_events"]
    raise RuntimeError("model did not name attempt events among the primary features")


SECONDS_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["seconds"], "properties": {
    "seconds": {"type": "array", "items": {"type": "number", "minimum": 0.2, "maximum": 30}}}}


def propose_seconds(activity, events, model=None, client=None, retries=2):
    """How long each attempt event takes, for an activity whose events were proposed before durations existed (the events stay as they are)."""
    import anthropic
    client = client or anthropic.Anthropic()
    listing = "\n".join(f"{i + 1}. {e['feature']} {e['direction']}" for i, e in enumerate(events))
    prompt = (f"Activity: {activity}\nIn one attempt the body does these events, in order:\n{listing}\n\nFor each event, how many seconds does it take in a typical "
              "attempt, from the feature leaving its rest value to being back at it (a tennis forehand swing about 1; a serve's ball toss about 1.5; a squat about 3)? "
              "One number per event, in the same order. Answer by calling the submit_seconds tool exactly once.")
    for _ in range(retries + 1):
        resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=300,
                                      tools=[{"name": "submit_seconds", "description": "Submit the durations.", "input_schema": SECONDS_SCHEMA}],
                                      messages=[{"role": "user", "content": prompt}])
        for b in resp.content:
            if b.type == "tool_use" and len(b.input.get("seconds", [])) == len(events):
                return [float(x) for x in b.input["seconds"]]
    raise RuntimeError("model did not give one duration per attempt event")


QUERIES_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["search_queries"], "properties": {
    "search_queries": {"type": "array", "minItems": 3, "maxItems": 8, "items": {
        "type": "object", "additionalProperties": False, "required": ["query", "kind"],
        "properties": {"query": {"type": "string"},
                       "kind": {"enum": ["demonstration", "good_form", "common_mistakes", "instruction"]}}}}}}


def propose_queries(activity, events, used, model=None, client=None, retries=2):
    """New video searches when earlier ones did not find enough clear attempts. The aim is footage in which the movement
    is repeated many times and is easy to see: one person, whole body in view, a steady camera, little talking."""
    import anthropic
    client = client or anthropic.Anthropic()
    ev = ", then ".join(f"{e['feature']} {e['direction']}" for e in events)
    prompt = (f"Activity: {activity}\nOne attempt is recognised in video as: {ev}.\n\nSearches already used:\n"
              + "\n".join(f"- {u}" for u in used)
              + "\n\nPropose 6 NEW YouTube searches likely to find videos that show this activity performed many times by one person, "
                "whole body in view, steady camera, little cutting or talking (practice sessions, drills, slow motion, training reps, "
                "different camera angles, different skill levels, left- and right-handed players). Do not repeat the searches above. "
                "Answer by calling the submit_queries tool exactly once.")
    for _ in range(retries + 1):
        resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=800,
                                      tools=[{"name": "submit_queries", "description": "Submit the searches.", "input_schema": QUERIES_SCHEMA}],
                                      messages=[{"role": "user", "content": prompt}])
        for b in resp.content:
            if b.type == "tool_use" and not list(jsonschema.Draft202012Validator(QUERIES_SCHEMA).iter_errors(b.input)):
                return b.input["search_queries"]
    raise RuntimeError("model did not return new search queries")


def propose(activity, runs=1, model=None, client=None, observed=None, knowledge=""):
    return [propose_once(activity, model, client, observed=observed, knowledge=knowledge) for _ in range(runs)]


def agreement(proposals):
    """Mean pairwise Jaccard overlap of the features the runs chose to test."""
    if len(proposals) < 2:
        return None
    sets = [{o["test"]["feature"] for o in p["objectives"]} for p in proposals]
    js = [len(a & b) / max(1, len(a | b)) for a, b in itertools.combinations(sets, 2)]
    return round(sum(js) / len(js), 3)


def most_central_first(proposals):
    """Put the proposal that agrees most with the others first (the medoid), so one odd run does not decide the entry."""
    if len(proposals) < 3:
        return proposals
    sets = [{o["test"]["feature"] for o in p["objectives"]} for p in proposals]
    score = [sum(len(a & b) / max(1, len(a | b)) for j, b in enumerate(sets) if j != i) for i, a in enumerate(sets)]
    best = max(range(len(proposals)), key=lambda i: score[i])
    return [proposals[best]] + [p for i, p in enumerate(proposals) if i != best]


def consensus(proposals, min_keep=3):
    """Keep, from the most central proposal, only the objectives whose feature a majority of the independent runs also test. An
    objective only one run thought of is a guess; one that most runs reach separately is the model's stable knowledge of the
    movement. Returns (proposal, support, dropped): support = {objective id: number of runs}."""
    base = proposals[0]
    sets = [{o["test"]["feature"] for o in p["objectives"]} for p in proposals]
    support = {o["id"]: sum(1 for st in sets if o["test"]["feature"] in st) for o in base["objectives"]}
    need = (len(proposals) + 1) // 2
    keep = [o for o in base["objectives"] if support[o["id"]] >= need]
    if len(keep) < min_keep:                                    # runs hardly agree: keep the best supported
        keep = sorted(base["objectives"], key=lambda o: -support[o["id"]])[:min_keep]
    kept = {o["id"] for o in keep}
    out = dict(base)
    out["objectives"] = [dict(o, caused_by=[c for c in o["caused_by"] if c in kept]) for o in base["objectives"] if o["id"] in kept]
    return out, support, [o["id"] for o in base["objectives"] if o["id"] not in kept]


def stub_squat_proposal():
    """A fixed proposal used ONLY for offline tests of the pipeline."""
    return {
        "activity_id": "squat", "primary_features": ["angle.knee.dom", "angle.hip.dom", "height.hip"], "attempt_events": [{"feature": "height.hip", "direction": "falls", "seconds": 3.0}], "purpose": "Lower the hips under control and stand back up with the knees tracking over the feet.",
        "search_queries": [{"query": "bodyweight squat form", "kind": "good_form"},
                           {"query": "squat common mistakes", "kind": "common_mistakes"},
                           {"query": "air squat tutorial", "kind": "instruction"}],
        "phases": [{"id": "descent", "description": "from standing to the lowest point"},
                   {"id": "ascent", "description": "from the lowest point back to standing"}],
        "objectives": [
            {"id": "knee_cave", "goal": "knees track out over the toes", "caused_by": [],
             "test": {"feature": "dev.knee_inward.dom", "at_phase": "descent", "at_point": "end"},
             "sides": {"above": {"looks_like": "knees collapse toward the midline", "severity": "high"}},
             "outcome_links": ["depth_reached"], "cue_intent": "knees drifting inward; push them out over the toes",
             "ask_if_unsure_intent": "ask whether the knees feel like they fall inward", "fix_intent": "slow the descent, press knees outward"},
            {"id": "shallow_depth", "goal": "hips reach a low position", "caused_by": [],
             "test": {"feature": "height.hip", "at_phase": "descent", "at_point": "end"},
             "sides": {"above": {"looks_like": "hips stay high", "severity": "medium"}},
             "outcome_links": ["depth_reached"], "cue_intent": "go a little lower", "ask_if_unsure_intent": "ask what limits the depth",
             "fix_intent": "work to a box at the target height"},
            {"id": "excess_forward_lean", "goal": "chest stays at the trunk angle good squats show", "caused_by": ["shallow_depth"],
             "test": {"feature": "angle.trunk_lean", "at_phase": "descent", "at_point": "end"},
             "sides": {"above": {"looks_like": "trunk leans far forward", "severity": "low"},
                       "below": {"looks_like": "trunk stays bolt upright", "severity": "low"}},
             "outcome_links": [], "cue_intent": "bring the chest to the usual angle", "ask_if_unsure_intent": "ask whether the lean feels forced",
             "fix_intent": "cue the chest up, check ankle mobility"}],
        "outcomes": [{"id": "depth_reached", "description": "hips reach a controlled low position", "requires_observable": ["body"]}],
        "links": [{"feature": "height.hip", "at_phase": "descent", "at_point": "end", "outcome": "depth_reached",
                   "effect": "lower_is_better", "mechanism": "a lower hip position at the bottom is the depth achieved"}],
        "confusable_with": ["lunge", "arm_raise"], "session_ideas": ["3 sets of 8 slow reps", "tempo squats: two seconds down"],
        "vocabulary_proposals": []}


def stub_squat_principles():
    """Fixed principles used ONLY for offline tests of the pipeline."""
    return [{"id": "stable_base", "statement": "The lower body works as a stable base: when the knees follow the line of the feet the load goes through the strong joints.",
             "mechanism": ["balance_and_centre_of_mass", "force_transfer"], "applies_to": ["descent"], "explains": ["knee_cave", "knees_cave"],
             "handle_intent": "keep the base wide and steady", "offer_when": ["rest", "on_request"], "basis": "coaching_consensus"},
            {"id": "depth_gives_range", "statement": "Working through a full range gives the strongest, most controlled drive out of the bottom.",
             "mechanism": ["lever_and_torque", "stretch_shortening"], "applies_to": ["descent", "ascent"], "explains": ["shallow_depth"],
             "handle_intent": "sink into the bottom of the movement", "offer_when": ["warm_up", "rest", "on_request"], "basis": "biomechanics"}]
