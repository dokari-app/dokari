"""Average the held-out results of the overnight runs over seeds. Reads work/night3/*.txt and work/night4/*.txt. Writes work/night4_summary.txt and work/night4_best3d.json"""
import glob, re, json, collections, os
import numpy as np
runs = collections.defaultdict(list)
for f in sorted(glob.glob("work/night3/*.txt") + glob.glob("work/night4/*.txt")):
    txt = open(f).read(); name = os.path.basename(f)[:-4]
    m = re.search(r"forehand-vs-backhand AUC[^:]*: ([0-9.]+)", txt); r = re.search(r"recall (\{.*\})", txt); a = re.search(r"accuracy ([0-9.]+)", txt)
    c = re.search(r"confidence>=2 labels: ([0-9.]+)", txt)
    if not (m and r and a): continue
    mm = re.match(r"(?:c(?P<chan>\w+?)_a(?P<arch>\w+?)_)?h(?P<hand>\w+?)_pre(?P<pre>[0-9.]+)_ep(?P<ep>\d+)_s(?P<seed>\d+)", name)
    if not mm: continue
    d = mm.groupdict(); cfg = (d["chan"] or "both", d["arch"] or "conv", d["hand"], d["pre"], d["ep"])
    runs[cfg].append(dict(auc=float(m.group(1)), auc2=float(c.group(1)) if c else np.nan, acc=float(a.group(1)), rec=eval(r.group(1))))
rows = []
for cfg, L in runs.items():
    rec = {k: np.mean([x["rec"][k] for x in L]) for k in L[0]["rec"]}
    rows.append((cfg, len(L), np.mean([x["auc"] for x in L]), np.std([x["auc"] for x in L]), np.nanmean([x["auc2"] for x in L]), np.mean([x["acc"] for x in L]), rec))
rows.sort(key=lambda r: -r[2]); out = ["channels arch   hand   pre  epochs | seeds | fh-vs-bh AUC (std) | AUC conf>=2 | accuracy | recall forehand/backhand/serve/no_stroke"]
for cfg, n, auc, sd, auc2, acc, rec in rows:
    out.append(f"{cfg[0]:8s} {cfg[1]:5s} {cfg[2]:7s} {cfg[3]:4s} {cfg[4]:5s} | {n:3d}   | {auc:.3f} ({sd:.3f})       | {auc2:.3f}        | {acc:.3f}    | " + " / ".join(f"{rec[k]:.2f}" for k in ("forehand", "backhand", "serve", "no_stroke")))
open("work/night4_summary.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
best = [r for r in rows if r[0][0] == "3d" and r[0][2] == "none" and r[1] >= 2]
if best:
    b = best[0][0]; json.dump(dict(chan=b[0], arch=b[1], hand=b[2], pre=b[3], epochs=b[4]), open("work/night4_best3d.json", "w")); print("\nbest depth-pose-only configuration:", b)
else:
    json.dump(dict(chan="3d", arch="conv", hand="none", pre="1.6", epochs="60"), open("work/night4_best3d.json", "w")); print("no 3d runs finished: default configuration")
