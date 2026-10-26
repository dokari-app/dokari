"""Principles layer: the few ideas that explain WHY good form works, so the coach can point at a principle instead of correcting one swing at a time.

A principle is generated (never hand-written) from the activity's objectives, phases and coaching knowledge, several times independently; only
principles that independent runs reach again are kept. Each says which faults and objectives it accounts for, gives the intent of a very short
effect-focused cue (what the movement should achieve, not which body part to move), and says when it may be offered. Delivery rules (never during
an attempt, offered rarely, on request) belong to the engine, not to the entry."""
import re
import jsonschema
from .schema import ID

WORLDVIEW = ["kinetic_chain", "balance_and_centre_of_mass", "lever_and_torque", "rotation", "stretch_shortening",
             "timing_and_rhythm", "projectile_motion", "grip_and_friction", "base_of_support", "force_transfer"]
OFFER_WHEN = ["warm_up", "rest", "wrap_up", "on_request"]
BASES = ["biomechanics", "motor_learning", "coaching_consensus", "contested"]
MAX_STATEMENT = 320

PRINCIPLE = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "statement", "mechanism", "applies_to", "explains", "handle_intent", "offer_when", "basis"],
    "properties": {
        "id": ID,
        "statement": {"type": "string", "maxLength": MAX_STATEMENT,
                      "description": "The key point in plain language, 1-3 sentences: why this works. The point, not a spoken script."},
        "mechanism": {"type": "array", "minItems": 1, "items": {"enum": WORLDVIEW}, "description": "Which body or physics ideas make it work."},
        "applies_to": {"type": "array", "items": ID, "description": "Phase ids where it matters."},
        "explains": {"type": "array", "minItems": 1, "items": ID, "description": "Objective ids and coach-fault ids this principle accounts for."},
        "handle_intent": {"type": "string", "description": "The intent of a very short cue that points at the principle during practice. It names the EFFECT "
                                                          "to achieve (what the movement should do), never a body part or a joint."},
        "offer_when": {"type": "array", "minItems": 1, "items": {"enum": OFFER_WHEN}},
        "basis": {"enum": BASES, "description": "biomechanics: follows from mechanics; motor_learning: from learning research; coaching_consensus: what "
                                                "the coaches given agree on; contested: coaches disagree."},
        "alternatives": {"type": "array", "items": {"type": "string"}, "description": "Required when basis is contested: the competing views."},
        "transfer_group": {"type": "string", "description": "Optional id shared with the same idea in other activities."}}}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["principles"],
          "properties": {"principles": {"type": "array", "minItems": 2, "maxItems": 6, "items": PRINCIPLE}}}

SYSTEM = ("You write the principles layer of a coaching knowledge entry. A principle is an idea that explains WHY good form works and that a learner "
          "can carry to the next problem, not a correction of one movement. Give 3 to 5 principles that together account for the most important "
          "objectives and faults you are given. Rules: each principle must explain at least one objective or fault id from the lists given (use those ids "
          "exactly); mechanisms use only the listed concepts; the handle_intent names the effect to achieve and never a body part, joint or limb; "
          "make no statement that a movement is safe, unsafe, dangerous or harmful and no medical claim; where the coaching knowledge shows coaches disagree, "
          "set basis to contested and give the competing views in alternatives; do not invent facts. Answer by calling the tool exactly once.")

BODY_WORDS = re.compile(r"\b(arm|arms|elbow|elbows|wrist|wrists|shoulder|shoulders|hand|hands|finger|fingers|hip|hips|knee|knees|leg|legs|foot|feet|ankle|ankles|"
                        r"back|spine|trunk|chest|neck|head|forearm|thigh|thighs|torso|core|glute|glutes|heel|heels|toe|toes)\b", re.I)
SAFETY_WORDS = re.compile(r"\b(safe|unsafe|safely|dangerous|danger|injur\w*|harm\w*|pain\w*|strain\w*|risk\w*|medical)\b", re.I)


def prompt(activity, entry, knowledge=""):
    phases = "\n".join(f"- {p['id']}: {p['description']}" for p in entry["movement_model"]["phases"])
    objs = "\n".join(f"- {o['id']} ({o['severity']}): {o['goal']}" for o in entry["objectives"])
    faults = "\n".join(f"- {f['id']}: {f['description']}" + (f" (coaches disagree: {f['disagreement']})" if f.get("disagreement") else "")
                       for f in entry.get("coaching", {}).get("faults", []))
    return (f"Activity: {activity.replace('_', ' ')}\n\nPhases:\n{phases}\n\nObjectives:\n{objs}\n\nCoach-named faults:\n{faults or '(none)'}\n\n"
            f"Allowed mechanism concepts: {', '.join(WORLDVIEW)}\nAllowed offer_when moments: {', '.join(OFFER_WHEN)}\n"
            + (f"\n{knowledge}\n" if knowledge else "") + "\nCall the tool now.")


def generate_once(activity, entry, knowledge="", model=None, client=None, retries=2):
    import anthropic
    from .propose import DEFAULT_MODEL
    client = client or anthropic.Anthropic()
    last = None
    for _ in range(retries + 1):
        resp = client.messages.create(model=model or DEFAULT_MODEL, max_tokens=4000, system=SYSTEM,
                                      tools=[{"name": "submit_principles", "description": "Submit the principles.", "input_schema": SCHEMA}],
                                      messages=[{"role": "user", "content": prompt(activity, entry, knowledge)}])
        for b in resp.content:
            if b.type == "tool_use":
                errs = list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(b.input))
                if not errs:
                    return b.input["principles"]
                last = "; ".join(e.message[:100] for e in errs[:3])
    raise RuntimeError(f"model did not return valid principles: {last or 'no tool call'}")


def _jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(1, len(a | b))


def merge(runs, min_runs=None):
    """Principles that independent runs reach again. Two principles are the same idea when what they explain overlaps by at least a third.
    Returns [principle + 'support': number of runs]; the wording is taken from the first run that had it."""
    need = min_runs or max(1, (len(runs) + 1) // 2)
    groups = []
    for r in runs:
        used = set()
        for p in r:
            for g in groups:
                if g["run"] != id(r) and id(g) not in used and _jaccard(g["p"]["explains"], p["explains"]) >= 1 / 3:
                    g["n"] += 1; g["run"] = id(r); used.add(id(g)); break
            else:
                g = {"p": p, "n": 1, "run": id(r)}; groups.append(g); used.add(id(g))
    out = [dict(g["p"], support=g["n"]) for g in groups if g["n"] >= need]
    return sorted(out, key=lambda p: -p["support"])


def clean(principles, entry):
    """Drop what the entry cannot stand behind: references to nothing, and the same idea twice. Returns (kept, dropped [{id, why}])."""
    phases = {p["id"] for p in entry["movement_model"]["phases"]}
    known = {o["id"] for o in entry["objectives"]} | {f["id"] for f in entry.get("coaching", {}).get("faults", [])}
    kept, dropped, seen = [], [], set()
    for p in principles:
        explains = [e for e in p["explains"] if e in known]
        if not explains:
            dropped.append({"id": p["id"], "why": "explains nothing in this entry"}); continue
        if p["basis"] == "contested" and not p.get("alternatives"):
            dropped.append({"id": p["id"], "why": "called contested but names no competing view"}); continue
        if p["id"] in seen:
            dropped.append({"id": p["id"], "why": "duplicate id"}); continue
        seen.add(p["id"])
        q = dict(p, explains=explains, applies_to=[a for a in p["applies_to"] if a in phases])
        if BODY_WORDS.search(q["handle_intent"]):                  # a cue handle must name the effect, not a body part: without a usable handle the cue uses the objective's own intent
            q["handle_intent"] = ""
            dropped.append({"id": p["id"], "why": "its cue handle named a body part (handle removed, principle kept)"})
        kept.append(q)
    return kept, dropped


def build(activity, entry, knowledge="", runs=3, model=None, generator=None):
    """-> (principles, dropped). `generator(activity, entry, knowledge, model)` stands in for the language model in tests."""
    gen = generator or (lambda a, e, k, m: generate_once(a, e, k, m))
    got = [gen(activity, entry, knowledge, model) for _ in range(runs)]
    kept, dropped = clean(merge(got), entry)
    return kept, dropped


def problems(entry):
    """Checks on the principles of an entry -> list of strings (empty when sound)."""
    out = []
    ps = entry.get("principles") or []
    phases = {p["id"] for p in entry["movement_model"]["phases"]}
    known = {o["id"] for o in entry["objectives"]} | {f["id"] for f in entry.get("coaching", {}).get("faults", [])}
    for p in ps:
        for e in p["explains"]:
            if e not in known:
                out.append(f"{p['id']}: explains unknown {e}")
        for a in p.get("applies_to", []):
            if a not in phases:
                out.append(f"{p['id']}: unknown phase {a}")
        if p["basis"] == "contested" and not p.get("alternatives"):
            out.append(f"{p['id']}: contested but gives no alternatives")
        if BODY_WORDS.search(p["handle_intent"]):
            out.append(f"{p['id']}: the cue handle names a body part")
        if SAFETY_WORDS.search(p["statement"]) or SAFETY_WORDS.search(p["handle_intent"]):
            out.append(f"{p['id']}: makes a safety or medical statement")
        if len(p["statement"]) > MAX_STATEMENT:
            out.append(f"{p['id']}: statement too long")
    return out


def uncovered(entry):
    """High-severity objectives that no principle explains."""
    covered = {e for p in entry.get("principles") or [] for e in p["explains"]}
    return [o["id"] for o in entry["objectives"] if o["severity"] == "high" and o["id"] not in covered]


def has_handle(p):
    """True when the principle has a cue handle that may be used."""
    return bool(p and p.get("handle_intent", "").strip() and not BODY_WORDS.search(p["handle_intent"]))


def for_objective(entry, oid):
    """The principle that best explains an objective: the one that explains the fewest other things (the most specific), or None."""
    ps = [p for p in entry.get("principles") or [] if oid in p["explains"]]
    return min(ps, key=lambda p: len(p["explains"])) if ps else None
