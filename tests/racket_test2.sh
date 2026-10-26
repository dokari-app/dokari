#!/bin/bash
# After racket_seq_extract.py is done: 2 variants x 3 seeds, free.  nohup caffeinate -i bash tests/racket_test.sh > work/racket_test.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
for s in 0 1 2; do for w in base racket; do
  PRE=2.4 python -u tests/humantest_racket2.py --train $w --seed $s > work/humantest/racket2_${w}_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done $w seed $s"
done; done
python tests/humantest_racket2.py --eval | tee work/humantest/racket2_summary.txt; echo "all finished"
