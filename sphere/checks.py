"""Automated checks (spec section 9). Each returns pass | fail | not_testable with a reason."""
import jsonschema
from .schema import ENTRY_SCHEMA
from .vocab import MEASURES, DEFERRED, PLANNED, SLOW_ONLY, TIME_BUDGETS, plausible_range
from .features import FEATURES


def _r(cid, name, status, detail):
    return {"id": cid, "name": name, "status": status, "detail": detail}


def run_checks(entry):
    out = []
    # 1 format
    errs = sorted(jsonschema.Draft202012Validator(ENTRY_SCHEMA).iter_errors(entry), key=lambda e: list(e.path))
    out.append(_r(1, "format", "pass" if not errs else "fail",
                  "valid against the v0.7 schema" if not errs else "; ".join(f"{list(e.path)}: {e.message[:120]}" for e in errs[:5])))
    if errs:
        return out                      # later checks assume a well-formed entry

    tests = [(f["id"], t) for f in entry["objectives"] for t in f["tests"]]
    # 2 vocabulary
    bad = [t["feature"] for _, t in tests if t["feature"] not in FEATURES]
    dfr = [t["measure"] for _, t in tests if t["measure"] in DEFERRED]
    planned = [t["measure"] for _, t in tests if t["measure"] in PLANNED]
    ok = not bad and not dfr
    detail = "all features and measurements are registered and active"
    if not ok:
        detail = f"unknown features {bad}; deferred measurements {dfr}"
    elif planned:
        detail = f"registered; planned measurements used: {sorted(set(planned))}"
    out.append(_r(2, "vocabulary", "pass" if ok else "fail", detail))
    # 3 time budget
    viol = [fid for fid, t in tests if t["time_budget"] not in TIME_BUDGETS or
            (t["measure"] in SLOW_ONLY and t["time_budget"] in ("per_frame", "per_attempt"))]
    out.append(_r(3, "time budget", "pass" if not viol else "fail",
                  "every test's time budget can be met by its path" if not viol else f"violations in {viol}"))
    # 4 recognition
    acc = entry["recognition"]["accuracy"]
    far = acc.get("false_accept_rate_vs_other_activities")
    if acc["recall"] < 0.85:
        out.append(_r(4, "recognition", "fail", f"recall {acc['recall']:.2f} ({acc['recall_mode']}) is below 0.85"))
    elif far is None:
        out.append(_r(4, "recognition", "not_testable",
                      f"recall {acc['recall']:.2f} ({acc['recall_mode']}); no other activities in the library to test false accepts"))
    elif far > 0.15:
        out.append(_r(4, "recognition", "fail", f"false-accept rate {far:.2f} against other activities is above 0.15"))
    else:
        v = {k: x for k, x in acc["recall_by_view"].items() if x is not None}
        out.append(_r(4, "recognition", "pass", f"recall {acc['recall']:.2f} ({acc['recall_mode']}), false accepts {far:.2f}" + (f" (shape alone {acc['false_accept_rate_shape_only']:.2f})" if acc.get("false_accept_rate_shape_only") is not None else "") + f", by view {v}"))
    # 5 plausibility
    implausible = []
    for fid, t in tests:
        lo, hi = plausible_range(t["feature"])
        vals = [t["compare"][k] for k in ("value", "low", "high") if k in t["compare"]]
        implausible += [(fid, v) for v in vals if v is not None and not (lo <= v <= hi)]
    for lid, feats in entry["movement_model"]["key_poses"].items():
        for fn, st in feats.items():
            lo, hi = plausible_range(fn)
            if not (lo <= st["median"] <= hi):
                implausible.append((lid, fn))
    out.append(_r(5, "plausibility", "pass" if not implausible else "fail",
                  "all thresholds and key poses are inside plausible ranges" if not implausible else f"implausible: {implausible[:5]}"))
    # 6 discrimination
    cal = [(f["id"], f["calibration"]) for f in entry["objectives"]]
    lab = [(i, c["labelled"]) for i, c in cal if c.get("labelled")]
    ok = [i for i, l in lab if l["validated"]]
    failed = [i for i, l in lab if not l["validated"] and l["held_out_accuracy"] is not None]
    untested = [i for i, l in lab if not l["validated"] and l["held_out_accuracy"] is None]
    if not lab:
        n_demo = sum(1 for _, c in cal if c["basis"] == "good_form_demonstrations")
        out.append(_r(6, "discrimination", "not_testable",
                      f"no objective has enough labelled good and faulty examples (3 of each), so no target range is validated; {n_demo} of {len(cal)} come from good-form demonstrations, "
                      f"{len(cal) - n_demo} from everyday footage (what is typical, not what is good)"))
    else:
        status = "fail" if failed else "pass" if ok else "not_testable"
        out.append(_r(6, "discrimination", status,
                      f"{len(ok)}/{len(lab)} objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75)"
                      + (f"; do not: {failed}" if failed else "") + (f"; too few wrong examples in different videos to test: {untested}" if untested else "")
                      + f"; {len(cal) - len(lab)} without enough labels"))
    # 7 outcome links
    oids = {o["id"] for o in entry["outcomes"]}
    broken = [l["outcome"] for l in entry["links"] if l["outcome"] not in oids] + \
             [o for f in entry["objectives"] for o in f["outcome_links"] if o not in oids]
    prior = sum(1 for l in entry["links"] if l["evidence"] == "prior_only")
    out.append(_r(7, "outcome links", "pass" if not broken else "fail",
                  (f"{len(entry['links'])} links, {prior} prior-only (no data to test them yet)") if not broken else f"unknown outcomes {broken}"))
    # 8 agreement
    ag = entry["metadata"]["provenance"]["agreement"]
    runs = entry["metadata"]["provenance"]["runs"]
    if runs < 2 or ag is None:
        out.append(_r(8, "agreement", "not_testable", "only one generation run"))
    else:
        out.append(_r(8, "agreement", "pass" if ag >= 0.5 else "fail", f"agreement {ag:.2f} across {runs} runs"))
    # 9 cross-references
    probs = []
    ids = {f["id"] for f in entry["objectives"]}
    pr = {f["id"]: f["priority"] for f in entry["objectives"]}
    lms = {l["id"] for l in entry["movement_model"]["landmarks"]}
    for f in entry["objectives"]:
        for c in f["caused_by"]:
            if c not in ids:
                probs.append(f"{f['id']}: unknown cause {c}")
            elif pr[c] >= pr[f["id"]]:
                probs.append(f"{f['id']}: cause {c} is not ahead of it in priority")
        for t in f["tests"]:
            if t["at"] not in lms:
                probs.append(f"{f['id']}: unknown landmark {t['at']}")
    for p in entry["movement_model"]["phases"]:
        if p["start"] not in lms or p["end"] not in lms:
            probs.append(f"phase {p['id']}: unknown landmark")
    used = {t["feature"] for f in entry["objectives"] for t in f["tests"]} | {l["feature"] for l in entry["links"]}
    missing = used - set(entry["metadata"]["requires"]["features"])
    if missing:
        probs.append(f"requires is missing {sorted(missing)}")
    out.append(_r(9, "cross-references", "pass" if not probs else "fail",
                  "ids, landmarks, priorities and requires are consistent" if not probs else "; ".join(probs[:5])))
    # 10 principles
    ps = entry.get("principles")
    if not ps:
        out.append(_r(10, "principles", "not_testable", "no principles generated"))
    else:
        from .principles import problems, uncovered
        pr = problems(entry)
        gap = uncovered(entry)
        out.append(_r(10, "principles", "pass" if not pr else "fail",
                      f"{len(ps)} principles; " + ("sound" if not pr else "; ".join(pr[:4])) + ("; high-priority not explained: " + ", ".join(gap) if gap else "")))
    return out


def summarise(checks):
    return {s: sum(1 for c in checks if c["status"] == s) for s in ("pass", "fail", "not_testable")}
