#!/bin/bash
# The night run: more footage for the five shots other than serve and forehand (keeping the ball pictures around each shot), then the ball loop over all seven shots.
# Run it with the environment and the API key set:   caffeinate -i bash night.sh
cd "$(dirname "$0")"
for a in tennis_backhand tennis_slice tennis_volley tennis_overhead_smash tennis_drop_shot; do
  free=$(df -k . | awk 'NR==2{print int($4/1048576)}')
  if [ "$free" -lt 5 ]; then echo "stopped before $a: only $free GB free (the limit is 5 GB)"; break; fi
  echo "=== grow $a $(date +%H:%M), $free GB free"
  python factory.py grow --activity $a --target-attempts 300 --target-clips 80 --max-rounds 2 --per-round 20 --ball-windows --delete-videos
done
echo "=== ball loop $(date +%H:%M)"
python tests/ball_night.py --act work/tennis_serve,work/tennis_forehand,work/tennis_backhand,work/tennis_slice,work/tennis_volley,work/tennis_overhead_smash,work/tennis_drop_shot --hours 3
echo "=== finished $(date +%H:%M)"
