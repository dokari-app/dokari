#!/bin/bash
# Overnight: label the new footage, retrain, collect a second round, label it, retrain, write the morning report.
cd "$(dirname "$0")/.." || exit 1
LOG=work/night2.log; REP=work/night2_report.txt
ACTS=tennis_volley,tennis_overhead_smash,tennis_slice,tennis_drop_shot,tennis_lob,tennis_backhand
if [ -z "$ANTHROPIC_API_KEY" ]; then echo "ANTHROPIC_API_KEY is not set in this window"; exit 1; fi
: > "$REP"
step() { echo "[$(date '+%H:%M')] $*" | tee -a "$LOG"; }
report() {  # $1 = label, $2 = model output file, $3 = replay output file
  { echo "== $1"; grep -E "labelled windows|classes:|accuracy|recall" "$2"; echo "-- replay of your clips:"; grep -E "^IMG|strokes|correct" "$3"; echo; } >> "$REP"
}
step "1/5 label today's new footage"
python tests/stroke_label2.py --new-hours 16 --acts $ACTS --swing-per-clip 10 --over-per-clip 3 --cap 1500 >> "$LOG" 2>&1
step "2/5 train and replay"
python tests/stroke_model.py work/stroke_labels2.json > work/night2_model1.txt 2>&1
python tests/stroke_live.py > work/night2_live1.txt 2>&1
report "after labelling today's footage" work/night2_model1.txt work/night2_live1.txt
step "3/5 collect a second round of footage"
python tests/shot_footage.py --per-stroke 12 --per-query 15 >> "$LOG" 2>&1
step "4/5 label the second round"
python tests/stroke_label2.py --new-hours 30 --acts $ACTS --swing-per-clip 10 --over-per-clip 3 --cap 1500 >> "$LOG" 2>&1
step "5/5 train and replay again"
python tests/stroke_model.py work/stroke_labels2.json > work/night2_model2.txt 2>&1
python tests/stroke_live.py > work/night2_live2.txt 2>&1
report "after the second round" work/night2_model2.txt work/night2_live2.txt
step "finished"
