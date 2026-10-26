#!/bin/bash
# Overnight part 2, offline, no key, no cost. Waits for night3.sh to finish, then:
#  1. sweep: channels (both / depth-only) x network (conv / gru) x seeds (+ window length for depth-only conv)
#  2. average over seeds -> work/night4_summary.txt
#  3. final depth-pose-only models (5 seeds) on ALL windows with the best configuration
#  4. replay of the three recorded clips and the live sessions with those models -> work/night4_replay.txt
#   nohup caffeinate -i bash tests/night4.sh > work/night4.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
log() { echo "[$(date +%H:%M)] $*"; }
log "waiting for night3"
for i in $(seq 1 720); do grep -q "all 36 runs finished" work/night3.log 2>/dev/null && break; sleep 30; done
mkdir -p work/night4; log "sweep starts"
run() { # chan arch pre ep seed
  tag="c$1_a$2_hnone_pre$3_ep$4_s$5"
  PRE=$3 python -u tests/stroke_net.py --chan "$1" --arch "$2" --hand none --epochs "$4" --seed "$5" --tag "_$tag" > "work/night4/$tag.txt" 2>&1
  log "done $tag"
}
for seed in 0 1 2; do
  for chan in both 3d; do for arch in conv gru; do run $chan $arch 1.6 60 $seed; done; done
  for pre in 1.0 2.4; do run 3d conv $pre 60 $seed; done
done
log "summary"; python tests/select_best.py > work/night4_select.txt 2>&1
read ARCH PRE EP < <(python -c "import json;b=json.load(open('work/night4_best3d.json'));print(b['arch'],b['pre'],b['epochs'])")
log "final models: depth-pose only, arch=$ARCH pre=$PRE epochs=$EP"
PRE=$PRE python -u tests/stroke_net.py --chan 3d --arch "$ARCH" --hand none --epochs "$EP" --final 5 --tag _final3d > work/night4_final.txt 2>&1
log "replay"; python -u tests/stroke_replay_net.py work/net_final/final3d_config.json > work/night4_replay.txt 2>&1
log "night4 finished"
