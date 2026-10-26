"""Glue: clips on disk -> attempts -> entry -> checks. Activity-agnostic."""
import glob
import json
import os
import numpy as np
from .skeleton import load_clip
from .calibrate import collect_attempts, stack, curate, align_cycles, align_attempts, cap_per_clip, size_gate
from .builder import build_entry, observed_structure
from .checks import run_checks, summarise
from . import propose as P
from . import knowledge as K
from . import principles as PR
from . import sources as S
from . import labelling as LB
from .vocab import feature_catalogue


EVENTS_RULE = 6


def load_collections(clips_dir, events, labels=None, primary=None):
    cols = []
    for p in sorted(glob.glob(os.path.join(clips_dir, "*.npz"))):
        clip = load_clip(p)
        if labels and clip["meta"].get("id") in labels:
            clip["meta"]["tag"] = labels[clip["meta"]["id"]]
        cols.append(collect_attempts(clip, events, primary=primary))
    return cols


def load_prior(work_dir, activity, model=None):
    """The activity proposal made before any video was seen (it chose the search queries, the primary features and the
    attempt events). A prior made before attempt events existed gets them: from its single defining signal if it has one,
    otherwise from one small model call."""
    path = os.path.join(work_dir, activity, "prior.json")
    if os.path.exists(path):
        prior = json.load(open(path))
        if prior.get("events_rule") != EVENTS_RULE:         # events are asked again under the current rules (simultaneous movement is one event; events present in every performance, poor ones too; big and characteristic, each with the level it must reach)
            prior["attempt_events"] = P.propose_events(activity.replace("_", " "), prior["primary_features"], model)
            prior.pop("defining_signal", None)
            prior["events_rule"] = EVENTS_RULE
            json.dump(prior, open(path, "w"), indent=2)
            print("  attempt events for %s: %s" % (activity, ", then ".join(
                "%s %s%s" % (e["feature"], e["direction"], " (at least %s)" % e["peak_at_least"] if e.get("peak_at_least") is not None else "")
                for e in prior["attempt_events"])))
        if any(not e.get("seconds") for e in prior["attempt_events"]):         # durations are asked for events proposed without them; the events stay
            for e, sec in zip(prior["attempt_events"], P.propose_seconds(activity.replace("_", " "), prior["attempt_events"], model)):
                e["seconds"] = sec
            json.dump(prior, open(path, "w"), indent=2)
            print("  how long each event takes: " + ", ".join(f"{e['feature']} {e['seconds']} s" for e in prior["attempt_events"]))
        return prior
    prior = P.propose_once(activity.replace("_", " "), model)
    prior["events_rule"] = EVENTS_RULE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(prior, open(path, "w"), indent=2)
    return prior


def library_negatives(work_dir, activity, model=None):
    """Attempts from every OTHER activity in the library, used as negatives for recognition."""
    out = []
    for d in sorted(glob.glob(os.path.join(work_dir, "*", "clips"))):
        other = os.path.basename(os.path.dirname(d))
        if other == activity:
            continue
        prior = load_prior(work_dir, other, model)
        cols, _ = size_gate(load_collections(d, prior["attempt_events"], primary=prior["primary_features"]))
        A, _ = stack(cols)
        out.extend(list(A))
    return np.stack(out) if out else None


MIN_ATTEMPTS = 30         # fewer attempts than this cannot characterise a movement


def supported_events(clips_dir, events, primary, labels=None):
    """The proposal may name an event that real footage rarely shows clearly (a shallow knee bend in a serve). While the
    events together find too few attempts, drop the one whose removal finds the most, but never go below two events:
    one event alone no longer tells the action apart. Events the proposal defines by a level they must reach (a wrist
    overhead) are its identifying events and are never dropped. Returns (events kept, events dropped)."""
    def count(ev):
        return sum(len(c["attempts"]) for c in load_collections(clips_dir, ev, labels, primary))
    kept, dropped = list(events), []
    while len(kept) > 2 and count(kept) < MIN_ATTEMPTS:
        free = [i for i, e in enumerate(kept) if e.get("peak_at_least") is None]
        if not free:
            break
        best = max(free, key=lambda i: count(kept[:i] + kept[i + 1:]))
        dropped.append(kept.pop(best))
    return kept, dropped


def footage_sources(work_dir, activity, cols, model=None, client=None, rate_missing=True):
    """How the footage splits by kind of source: for every tier, the clips and the attempts that ended up in the entry. Videos
    downloaded before sources were rated are rated now (one cheap call per 40 videos) so the numbers are complete."""
    path = os.path.join(work_dir, activity, "sources.json")
    if not os.path.exists(path):
        return None
    src = json.load(open(path))
    if rate_missing and any(not x.get("tier") for x in src):
        try:
            print("  rating the sources of the footage ...", flush=True)
            S.rate(activity, src, model, client)
            json.dump(src, open(path, "w"), indent=2)
        except Exception as e:
            print(f"  could not rate the sources ({str(e)[:80]})", flush=True)
    by = {x["id"]: x for x in src}
    out = {}
    for c in cols:
        x = by.get(c["clip_id"], {})
        row = out.setdefault(x.get("tier") or "unrated", {"clips": 0, "attempts": 0, "shows": {}})
        n = len(c["attempts"])
        if n:
            row["clips"] += 1
            row["attempts"] += n
            sh = x.get("shows") or "unknown"
            row["shows"][sh] = row["shows"].get(sh, 0) + n
    return out, by


GOOD_TIERS = ("coach_demo", "pro_footage")


def reference_clips(by, cols):
    """The clips that show what good looks like: coaches and professionals demonstrating, in videos that are not about mistakes."""
    ok = lambda cid: by.get(cid, {}).get("tier") in GOOD_TIERS and by.get(cid, {}).get("shows") not in ("mistakes", "mixed")
    return {c["clip_id"] for c in cols if c["usable"] and ok(c["clip_id"])}


def _met(v, cmp):
    """Whether values meet an objective's condition (the compare of its test)."""
    if cmp["op"] == "WITHIN_RANGE":
        return (v >= cmp["low"]) & (v <= cmp["high"])
    if cmp["op"] == "LESS_OR_EQUAL":
        return v <= cmp["value"]
    if cmp["op"] == "GREATER_OR_EQUAL":
        return v >= cmp["value"]
    raise ValueError(f"unexpected comparison {cmp['op']}")


def weak_check(entry, cols, ref, min_clips=3, margin=0.05):
    """A check of the target ranges that needs no human labels. The range comes from demonstrations of good form, so everyday
    footage should depart from it more often than the demonstrations do. Each demonstration clip is judged against a range
    made from the OTHER demonstration clips, so the demonstrations cannot pass by construction. This shows whether an
    objective picks up any difference between good form and everyday footage; it does not show that a departure is a mistake
    (everyday footage also differs in camera, lighting and distance). Objectives whose range had to come from everyday footage
    cannot be checked. Returns {objective id: {...}} or None when no clip is a reference."""
    from .calibrate import stack, N_T, target_range, REF_MIN_CLIPS
    from .features import FEATURES
    A, meta = stack([c for c in cols if c["usable"]])
    if not len(A) or not ref:
        return None
    cid = np.array([m["clip_id"] for m in meta])
    isref = np.isin(cid, list(ref))
    lm = {l["id"]: int(round(l["t"] * (N_T - 1))) for l in entry["movement_model"]["landmarks"]}
    out = {}
    for o in entry["objectives"]:
        t = o["tests"][0]
        li = lm[t["at"]]
        v = np.nanmedian(A[:, max(0, li - 1):li + 2, FEATURES.index(t["feature"])], axis=1)
        ok = np.isfinite(v)
        if o["calibration"]["basis"] != "good_form_demonstrations":
            out[o["id"]] = {"verdict": "no_reference"}
            continue
        flag = np.zeros(len(v), bool)
        flag[~isref] = ~_met(v[~isref], t["compare"])
        for c in sorted(set(cid[isref])):
            rest = isref & ok & (cid != c)
            if len(set(cid[rest])) >= REF_MIN_CLIPS:
                lo, hi = target_range(v[rest], set(o["sides"]), 5, cid[rest])
                cmp_ = {"op": "WITHIN_RANGE", "low": lo, "high": hi} if lo is not None and hi is not None else \
                       {"op": "LESS_OR_EQUAL", "value": hi} if hi is not None else {"op": "GREATER_OR_EQUAL", "value": lo}
            else:
                cmp_ = t["compare"]
            sel = cid == c
            flag[sel] = ~_met(v[sel], cmp_)
        row = {}
        for g, mask in (("good", isref), ("other", ~isref)):
            sel = ok & mask
            clips = sorted(set(cid[sel]))
            per_clip = [float(flag[sel & (cid == c)].mean()) for c in clips]
            row[g] = {"attempts": int(sel.sum()), "clips": len(clips), "flagged": round(float(flag[sel].mean()), 3) if sel.any() else None,
                      "flagged_per_clip": round(float(np.mean(per_clip)), 3) if per_clip else None}
        if row["good"]["clips"] < min_clips or row["other"]["clips"] < min_clips:
            verdict = "too_little_data"
        else:
            d = row["other"]["flagged_per_clip"] - row["good"]["flagged_per_clip"]
            verdict = "supports" if d >= margin else "opposite" if d <= -margin else "no_difference"
        out[o["id"]] = dict(row, verdict=verdict)
    return out


def prepare(clips_dir, events, primary, labels=None, trusted=None):
    """Clips -> the attempts the entry is built from (and each attempt's time window in its video). `trusted(clip id, window)` tells which
    attempts have been confirmed as real attempts by looking at them: the size, shape and loop filters never drop those."""
    cols, amp = size_gate(load_collections(clips_dir, events, labels, primary), trusted=trusted)
    cols, al = align_cycles(cols)
    cols = align_attempts(cols, trusted=trusted)
    cols = cap_per_clip(cols, trusted=trusted)
    cols, cur = curate(cols, primary=primary, trusted=trusted)
    return cols, amp, al, cur


def deciding_faults(links):
    """objective id -> the coaching faults whose labels say whether its attempts are right or wrong: the faults it measures itself;
    faults it only stands in for (a proxy) say nothing about its feature. An objective with only proxies is judged by those."""
    by = {}
    for fid, l in links.items():
        if l["objective"]:
            by.setdefault(l["objective"], []).append(fid)
    return {oid: [f for f in fids if links[f]["measurable"] == "measured"] or fids for oid, fids in by.items()}


def build(activity, work_dir, runs=1, labels=None, proposer=None, model=None, linker=None, principler=None):
    clips_dir = os.path.join(work_dir, activity, "clips")
    if proposer:
        first = proposer(activity, 1)[0]
    else:
        first = load_prior(work_dir, activity, model)
    primary, events = first["primary_features"], first["attempt_events"]
    events, dropped = supported_events(clips_dir, events, primary, labels)
    lab = LB.load(work_dir, activity)
    cols, amp, al, cur = prepare(clips_dir, events, primary, labels)
    cols_lab = prepare(clips_dir, events, primary, labels, trusted=LB.trusted(lab))[0] if lab else None
    usable = [c for c in cols if c["usable"]]
    obs = observed_structure(cols)
    kmap = K.load(work_dir, activity)
    props = proposer(activity, runs) if proposer else P.propose(activity, runs, model=model, observed=obs, knowledge=K.for_prompt(kmap))
    props = P.most_central_first(props)
    ag = P.agreement(props)
    support, dropped_objectives = None, []
    if len(props) >= 3:
        props[0], support, dropped_objectives = P.consensus(props)
    others = library_negatives(work_dir, activity, model)
    fs, by = footage_sources(work_dir, activity, cols, model, rate_missing=not proposer) or (None, None)
    ref = reference_clips(by, cols) if by else set()
    links = unsupported = None
    faults_of = {}
    if kmap:               # the coaches' faults are linked to the objectives first: labels about faults then say which attempts meet which objective
        obs0 = [{"id": o["id"], "goal": o["goal"], "feature": o["test"]["feature"]} for o in props[0]["objectives"]]
        links, _ = (linker or (lambda k, e: K.link(k, e, feature_catalogue(), activity, model)))(kmap, obs0)
        faults_of = deciding_faults(links)
    entry = build_entry(props[0], cols, other_attempts=others, runs=runs, agreement=ag, events=events, reference_clips=ref,
                        tags_for=LB.tags_for(lab, faults_of) if lab else None, cal_collections=cols_lab)
    entry["metadata"]["provenance"]["attempt_events"] = events
    if first.get("footage"):
        entry["metadata"]["provenance"]["footage"] = first["footage"]
    if dropped:
        entry["metadata"]["provenance"]["attempt_events_dropped"] = dropped
    if support:
        entry["metadata"]["provenance"]["objective_support"] = {"runs": len(props), "per_objective": support, "dropped": dropped_objectives}
    if lab:
        entry["metadata"]["provenance"]["labels"] = LB.summary(lab)
    if fs:
        entry["metadata"]["provenance"]["footage_sources"] = fs
        entry["metadata"]["provenance"]["reference_clips"] = sorted(ref)
        wc = weak_check(entry, cols, ref)
        if wc:
            entry["metadata"]["weak_check"] = wc
    if kmap:
        kept = {o["id"] for o in entry["objectives"]}
        for l in links.values():                        # an objective that ended without a usable range tests nothing
            if l["objective"] and l["objective"] not in kept:
                l.update(objective=None, measurable="feature_available", note="no usable target range")
        named = {l["objective"] for l in links.values() if l["objective"]}
        unsupported = [i for i in kept if i not in named]
        entry["coaching"] = K.coaching_section(kmap, links, unsupported)
        kind = {l["objective"]: f["kind"] for f in entry["coaching"]["faults"] for l in [links[f["id"]]] if l["objective"]}
        for o in entry["objectives"]:                   # an objective is a safety matter only when the coaches that name it say so
            o["kind"] = "safety" if kind.get(o["id"]) == "safety" else "form"
        entry["metadata"]["provenance"]["coaching_sources"] = kmap["sources"]
        if principler or not proposer:                  # the ideas that explain why good form works (a model call, so not in offline tests unless given)
            ps, pdrop = PR.build(activity, entry, K.for_prompt(kmap), runs=3, model=model, generator=principler)
            if ps:
                entry["principles"] = ps
            if pdrop:
                entry["metadata"]["provenance"]["principles_dropped"] = pdrop
    checks = run_checks(entry)
    entry["metadata"]["checks"] = checks
    out = os.path.join(work_dir, activity)
    with open(os.path.join(out, "entry.json"), "w") as fh:
        json.dump(entry, fh, indent=2)
    with open(os.path.join(out, "report.md"), "w") as fh:
        fh.write(report(activity, entry, checks, len(cols), len(usable), cols, obs, cur, al, amp))
    return entry, checks


def report(activity, entry, checks, n_clips, n_usable, cols=None, obs=None, cur=None, al_=None, amp=None):
    s = summarise(checks)
    L = [f"# Factory report: {activity}", "",
         f"Clips found: {n_clips} (usable for attempts: {n_usable}). Attempts: {entry['metadata']['provenance']['n_attempts']}.",
         f"Confidence tier: **{entry['metadata']['confidence_tier']}**. Checks: {s['pass']} pass, {s['fail']} fail, {s['not_testable']} not testable.", "",
         "## Checks", ""]
    for c in checks:
        mark = {"pass": "PASS", "fail": "FAIL", "not_testable": "n/a "}[c["status"]]
        L.append(f"- [{mark}] {c['id']}. {c['name']}: {c['detail']}")
    fs = entry["metadata"]["provenance"].get("objective_support")
    L += ["", "## Objectives (in priority order)", ""]
    if fs:
        L += [f"Only objectives whose feature at least {(fs['runs'] + 1) // 2} of {fs['runs']} independent model runs also test are kept"
              + (f"; left out for lack of agreement: {', '.join(fs['dropped'])}." if fs["dropped"] else "."), ""]
    for f in entry["objectives"]:
        t = f["tests"][0]; c = f["calibration"]; cm = t["compare"]
        n = (fs or {}).get("per_objective", {}).get(f["id"])
        rng = f"between {cm['low']} and {cm['high']}" if cm["op"] == "WITHIN_RANGE" else f"at most {cm['value']}" if cm["op"] == "LESS_OR_EQUAL" else f"at least {cm['value']}"
        basis = {"labelled": f"labelled examples ({c['n_good']} right, {c['n_bad']} wrong, in {c.get('n_good_clips')} and {c.get('n_bad_clips')} videos; AUC {None if c['auc'] is None else round(c['auc'], 2)}"
                             f"{'' if c.get('held_out_accuracy') is None else ', right on %d%% of attempts from videos left out' % round(100 * c['held_out_accuracy'])})",
                 "good_form_demonstrations": f"good-form demonstrations ({c['n_reference_attempts']} attempts in {c['n_reference_clips']} clips)",
                 "everyday_footage": "everyday footage only (what is typical, not shown to be good)"}[c["basis"]]
        wrong = "; ".join(f"{k}: {v['looks_like']} ({v['severity']})" for k, v in f["sides"].items())
        L.append(f"- {f['priority']}. **{f['id']}** ({f['severity']}{', agreed by %d of %d runs' % (n, fs['runs']) if n else ''}): {f['goal']}. "
                 f"Target: {t['feature']} {rng} at {t['at']}. Wrong if {wrong}. Range from {basis}; reliability {f['detection']['reliability']}.")
    co = entry.get("coaching")
    if co:
        word = {"measured": "measured by the camera", "proxy": "only a proxy is measured (a test that goes with it, not the thing itself)", "feature_available": "a body feature can show it but no objective tests it (no agreed target)", "needs_new_feature": "would need a new body feature", "needs_new_tracker": "the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet", "not_visible": "not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor"}
        L += ["", f"## What coaches say ({co['n_sources']} coaching videos)", "", "Faults they name, most-cited first (kind; how many sources; what the camera can do about it):", ""]
        for f in co["faults"]:
            how = word[f["measurable"]] + (f" ({f['objective']})" if f["objective"] else "") + (f": {f['note']}" if f["note"] else "")
            L.append(f"- **{f['id']}** ({f['kind']}; {f['n_sources']} of {co['n_sources']}, {f['support']}): {how}." + (f" Coaches disagree: {f['disagreement']}" if f["disagreement"] else ""))
        if co["objectives_no_coach_names"]:
            L += ["", "Tested in this entry but named by no coach: " + ", ".join(co["objectives_no_coach_names"]) + "."]
        L += ["", "Good form, as coaches give it:", ""] + [f"- {g['point']} ({g['n_sources']} of {co['n_sources']})" for g in co["good_form"][:6]]
    if entry.get("principles"):
        L += ["", "## Principles (why good form works; offered rarely, never during an attempt)", ""]
        for p in entry["principles"]:
            L.append(f"- **{p['id']}** ({p['basis']}, {p['support']} of 3 runs; explains {', '.join(p['explains'])}): {p['statement']} "
                     f"Cue handle: {p['handle_intent']}." + (f" Competing views: {'; '.join(p['alternatives'])}." if p.get("alternatives") else ""))
        gap = PR.uncovered(entry)
        if gap:
            L += ["", "High-priority objectives no principle explains: " + ", ".join(gap) + "."]
    lb = entry["metadata"]["provenance"].get("labels")
    if lb:
        L += ["", f"## Check against labelled mistake videos ({lb['videos']} videos, {lb['attempts']} attempts, {lb['not_attempts']} judged not to be attempts)", "",
              "What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):", "",
              "| coach fault | present (attempts / videos) | absent (attempts / videos) |", "|---|---|---|"]
        for fid, r in sorted(lb["per_fault"].items(), key=lambda kv: -kv[1]["present"]):
            L.append(f"| {fid} | {r['present']} / {r['videos_present']} | {r['absent']} / {r['videos_absent']} |")
        L += ["", "| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |", "|---|---|---|---|---|---|"]
        for f in entry["objectives"]:
            c = f["calibration"]; lb_ = c.get("labelled")
            src = c["basis"].replace("_", " ")
            if not lb_:
                L.append(f"| {f['id']} | {c['n_good']} / {c['n_bad']} | | | | not enough labelled examples (needs 3 of each); range from {src} |")
                continue
            held = "" if lb_["held_out_accuracy"] is None else f"{round(100 * lb_['held_out_accuracy'])}%"
            verdict = ("separates right from wrong on videos left out: the range comes from the labelled examples" if lb_["validated"] else
                       f"separates on these attempts but the wrong ones come from too few videos to test on others; range kept from {src}" if lb_["held_out_accuracy"] is None and lb_["auc"] >= 0.75 else
                       f"does not tell right from wrong well enough; range kept from {src}")
            L.append(f"| {f['id']} | {lb_['n_good']} / {lb_['n_bad']} | {lb_['n_good_clips']} / {lb_['n_bad_clips']} | {round(lb_['auc'], 2)} | {held} | {verdict} |")
    ev = entry["metadata"]["provenance"].get("attempt_events")
    L += ["", f"Movement characterised by: {', '.join(entry['metadata']['provenance'].get('primary_features', []))}"]
    if ev:
        L += ["Attempts found as: " + ", then ".join(f"{e['feature']} {e['direction']}" + (f" (to at least {e['peak_at_least']})" if e.get("peak_at_least") is not None else "") for e in ev) + "."
              + (f" Typical size of the last event {amp['typical_excursion']}, lasting {amp['typical_seconds']} s; smaller ones (below {amp['minimum']}) or much longer or shorter ones are not attempts." if amp and amp.get("applied") else "")]
    fo = entry["metadata"]["provenance"].get("footage")
    if fo:
        L += ["", f"Footage when it was last grown (before any later downloads; the numbers at the top are current): {fo['attempts']} clear attempts in {fo['clips_with_attempts']} of {fo['clips']} clips after {fo['rounds']} round(s) of searching; "
              + ("target reached." if fo["target_reached"] else "TARGET NOT REACHED: this entry rests on little footage.")]
    fsrc = entry["metadata"]["provenance"].get("footage_sources")
    if fsrc:
        L += ["", "Footage by kind of source (clips and attempts that ended up in the entry):", "", "| kind | clips | attempts | shows |", "|---|---|---|---|"]
        for k, v in sorted(fsrc.items(), key=lambda kv: -kv[1]["attempts"]):
            L.append(f"| {k} | {v['clips']} | {v['attempts']} | " + ", ".join(f"{a} {b}" for a, b in sorted(v["shows"].items())) + " |")
    wc = entry["metadata"].get("weak_check")
    if wc:
        L += ["", "Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:", "",
              "| objective | good-form demos | everyday footage | reading |", "|---|---|---|---|"]
        read = {"supports": "everyday footage departs more: the objective picks up a difference from good form", "no_difference": "no difference: everyone is inside, or this measure does not separate them",
                "opposite": "demos depart more: doubtful", "too_little_data": "too few clips in a group to say", "no_reference": "range from everyday footage: nothing to compare against"}
        for fid, r in wc.items():
            if r["verdict"] == "no_reference":
                L.append(f"| {fid} | | | {read[r['verdict']]} |")
                continue
            g, o = r["good"], r["other"]
            fmt = lambda x: f"{round(100 * x['flagged_per_clip'])}% ({x['clips']} clips)" if x["flagged_per_clip"] is not None else "none"
            L.append(f"| {fid} | {fmt(g)} | {fmt(o)} | {read[r['verdict']]} |")
    dr = entry["metadata"]["provenance"].get("attempt_events_dropped")
    if dr:
        L += ["Not used (too rarely clear in this footage): " + ", ".join(f"{e['feature']} {e['direction']}" for e in dr) + "."]
    L += ["", "## Phases", ""] + [f"- {p['id']}: {p['start']} to {p['end']}" for p in entry["movement_model"]["phases"]]
    if al_ and al_.get("applied"):
        L += ["", "## Alignment", "", f"Clips whose repetitions start at different points of the cycle were rotated to match "
              f"reference clip {al_['reference']}: " + ", ".join(f"{k} by {v}/50" for k, v in al_["shifts"].items() if v) + "."]
    if cur and cur.get("applied"):
        L += ["", "## Curation (only attempts that look like the repeated movement are kept)", "",
              f"Kept {cur['kept']} of {cur['total']} attempts (tolerance {cur['tolerance']}). Seed: {cur['seed_basis']} ({', '.join(cur['seed_clips'])}).", "",
              "| clip | attempts found | kept | note |", "|---|---|---|---|"]
        L += [f"| {r['clip']} | {r['before']} | {r['kept']} | {'clip does not show the movement' if r.get('foreign') else 'seed' if r['seed'] else ''} |" for r in cur["clips"]]
    if obs:
        L += ["", "## What the clips show (landmarks of one attempt, median values)", ""]
        for lm in obs["landmarks"]:
            L.append(f"- {lm['id']} (t={lm['t']}): " + ", ".join(f"{k}={v}" for k, v in lm["values"].items()))
    if cols:
        from .features import FEATURES
        kn = FEATURES.index(ev[-1]["feature"] if ev else "angle.knee.dom")
        i1 = int(round(obs["landmarks"][1]["t"] * 49)) if obs else 24
        L += ["", "## Per clip", "", f"| clip | attempts used | believable frames | view yaw | {FEATURES[kn]} at start (median) | at L1 (p10 / median / p90) |", "|---|---|---|---|---|---|"]
        for c in cols:
            if c["attempts"]:
                X = np.stack(c["attempts"])
                rd = (lambda v: round(float(v))) if FEATURES[kn].startswith("angle.") else (lambda v: round(float(v), 2))
                top = rd(np.nanmedian(X[:, 0, kn]))
                b = X[:, i1, kn]
                bot = f"{rd(np.nanpercentile(b, 10))} / {rd(np.nanmedian(b))} / {rd(np.nanpercentile(b, 90))}"
            else:
                top, bot = "", ""
            L.append(f"| {c['clip_id']} | {len(c['attempts'])} | {round(100 * c['valid_share'])}% | {round(c['view_yaw_deg'])} | {top} | {bot} |")
    if entry["proposals"]:
        L += ["", "## Vocabulary proposals", ""] + [f"- {p['kind']}: {p['name']} ({p['why']})" for p in entry["proposals"]]
    return "\n".join(L) + "\n"
