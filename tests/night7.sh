#!/bin/bash
# Waits for the racket test to finish, then 3 variants x 3 seeds (free, about 45 min). Start (can be started right now):
#   nohup caffeinate -i bash tests/night7.sh > work/night7.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
echo "[$(date +%H:%M)] waiting for racket test"
for i in $(seq 1 480); do grep -q "all finished" work/racket2.log 2>/dev/null && break; sleep 30; done
for s in 0 1 2; do for v in tta mix mixtta; do
  PRE=2.4 python -u tests/humantest_night7.py --variant $v --seed $s > work/humantest/n7_${v}_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done $v seed $s"
done; done
python tests/humantest_night7.py --eval | tee work/humantest/night7_summary.txt; echo "all finished"
