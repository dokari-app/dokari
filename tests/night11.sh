#!/bin/bash
# Locked-set scoring: final skeleton networks WITHOUT the held-out videos (3 seeds, free, ~10 min), then Sonnet v2 on the locked sheets (paid, about $4.5), then the report.
#   nohup caffeinate -i bash tests/night11.sh > work/night11.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
PRE=2.4 python -u tests/stroke_net.py --chan 3d --arch conv --hand none --epochs 60 --final 3 --tag _locked || exit 1
python -u tests/locked_skeleton.py || exit 1
HT_DIR=work/locked python -u tests/humantest_labeller.py --run v2 --batch 1
python tests/lockedtest_eval.py | tee work/locked/summary.txt; echo "all finished"
