#!/bin/bash
# Free, about 15 min. Start (wait until night9 is finished):  nohup caffeinate -i bash tests/night10.sh > work/night10.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
for s in 0 1 2; do for v in bone wd bonewd; do
  PRE=2.4 python -u tests/humantest_bone.py --variant $v --seed $s > work/humantest/bone_${v}_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done $v seed $s"
done; done
python tests/humantest_bone.py --eval | tee work/humantest/bone_summary.txt; echo "all finished"
