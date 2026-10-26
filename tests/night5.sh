#!/bin/bash
# Learning curve, offline, free: does more labelled data help? depth-pose-only network, 25/50/75/100% of the training videos, 3 seeds.
#   nohup caffeinate -i bash tests/night5.sh > work/night5.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
mkdir -p work/night5
for seed in 0 1 2; do for frac in 0.25 0.5 0.75 1.0; do
  tag="f${frac}_s${seed}"; PRE=2.4 python -u tests/stroke_net.py --chan 3d --hand none --epochs 60 --seed $seed --frac $frac --tag "_lc_$tag" > "work/night5/$tag.txt" 2>&1
  echo "[$(date +%H:%M)] done $tag"
done; done
python - <<'PY'
import glob,re,collections,numpy as np
d=collections.defaultdict(list)
for f in glob.glob("work/night5/*.txt"):
    t=open(f).read();fr=re.search(r"f([0-9.]+)_s",f).group(1);m=re.search(r"forehand-vs-backhand AUC[^:]*: ([0-9.]+)",t);a=re.search(r"accuracy ([0-9.]+)",t);r=re.search(r"recall (\{.*\})",t)
    if m and a and r: d[fr].append((float(m.group(1)),float(a.group(1)),eval(r.group(1))["backhand"]))
out=["share of training videos | fh-vs-bh AUC | accuracy | backhand recall"]
for fr in sorted(d,key=float): v=np.array([x for x in d[fr]]);out.append(f"{float(fr):>5.2f}                   | {v[:,0].mean():.3f}        | {v[:,1].mean():.3f}    | {v[:,2].mean():.2f}")
open("work/night5_curve.txt","w").write("\n".join(out)+"\n");print("\n".join(out))
PY
