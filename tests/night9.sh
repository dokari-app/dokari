#!/bin/bash
# Two free tests, about 45 min. Start:  nohup caffeinate -i bash tests/night9.sh > work/night9.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
python -u tests/vid_probe.py > work/humantest/vidprobe_summary.txt 2>&1; echo "[$(date +%H:%M)] video probe done"
for s in 0 1 2; do for v in bf yaw bfyaw; do
  PRE=2.4 python -u tests/humantest_view.py --variant $v --seed $s > work/humantest/view_${v}_s${s}.txt 2>&1; echo "[$(date +%H:%M)] done $v seed $s"
done; done
python tests/humantest_view.py --eval | tee work/humantest/view_summary.txt; echo "all finished"
