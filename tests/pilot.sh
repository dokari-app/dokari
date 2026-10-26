#!/bin/bash
# After the labelling is done: 2 label sets x 3 seeds, free. nohup caffeinate -i bash tests/pilot.sh > work/pilot.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
for s in 0 1 2; do for w in old new; do
  PRE=2.4 python -u tests/humantest_pilot.py --train $w --seed $s > work/humantest/pilot_${w}_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done $w seed $s"
done; done
python tests/humantest_pilot.py --eval | tee work/humantest/pilot_summary.txt; echo "all finished"
