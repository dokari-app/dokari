#!/bin/bash
# Free: 4 variants x 3 seeds (about 12 runs of 3-4 min). Start:  nohup caffeinate -i bash tests/night6.sh > work/night6.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
for seed in 0 1 2; do for v in base A B C; do
  PRE=2.4 python -u tests/humantest_clean.py --variant $v --seed $seed > work/humantest/clean_${v}_s${seed}.txt 2>&1
  echo "[$(date +%H:%M)] done $v seed $seed"
done; done
python tests/humantest_clean.py --eval | tee work/humantest/clean_summary.txt
echo "all finished"
