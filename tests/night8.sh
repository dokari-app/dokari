#!/bin/bash
# PAID step first (about $9, needs the key exported in this Terminal), then free retraining.
#   export ANTHROPIC_API_KEY=<your key>; nohup caffeinate -i bash tests/night8.sh > work/night8.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
export PILOT_N=1200
python -u tests/humantest_pilot.py --estimate || exit 1
python -u tests/humantest_pilot.py --label || { echo "labelling failed"; exit 1; }
for s in 0 1 2; do
  PRE=2.4 python -u tests/humantest_night7.py --variant mix2 --seed $s > work/humantest/n7_mix2_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done mix2 seed $s"
done
python tests/humantest_night7.py --eval | tee work/humantest/night8_summary.txt; echo "all finished"
