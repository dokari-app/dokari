#!/bin/bash
# 1) crops (about 20-30 min if not done) 2) one image-model run (5 folds). Start: nohup caffeinate -i bash tests/img_run.sh > work/img_run.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
python -u tests/crops_extract.py
python -u tests/img_net.py --seed 0 --epochs 8 --tag a
python tests/img_net.py --eval --tag a | tee work/humantest/img_summary_a.txt
echo "all finished"
