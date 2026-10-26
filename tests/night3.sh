#!/bin/bash
# Overnight, offline: neural stroke classifier sweep. No internet, no API key, no cost. ~2-5 min per run.
#   nohup caffeinate -i bash tests/night3.sh > work/night3.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
log() { echo "[$(date +%H:%M)] $*"; }
python -c "import torch" 2>/dev/null || { log "torch is not installed: run  pip install torch  while online"; exit 1; }
log "started"
mkdir -p work/night3
n=0
for seed in 0 1 2; do
 for hand in none oracle; do
  for pre in 1.0 1.6 2.4; do
   for ep in 40 80; do
    tag="h${hand}_pre${pre}_ep${ep}_s${seed}"
    PRE=$pre python -u tests/stroke_net.py --hand "$hand" --epochs "$ep" --seed "$seed" --tag "_$tag" > "work/night3/$tag.txt" 2>&1
    n=$((n+1)); log "run $n/36 done: $tag (exit $?)"
   done
  done
 done
done
log "all 36 runs finished: results in work/night3/*.txt"
