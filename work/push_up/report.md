# Factory report: push_up

Clips found: 45 (usable for attempts: 23). Attempts: 249.
Confidence tier: **low**. Checks: 7 pass, 1 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [PASS] 4. recognition: recall 0.98 (leave-one-clip-out), false accepts 0.00 (shape alone 0.00), by view {'front/back (<30)': 0.9803921568627451, 'oblique (30-60)': 0.9719626168224299, 'side (>60)': 0.978021978021978}
- [FAIL] 5. plausibility: implausible: [('wrong_hand_placement', -0.0023), ('elbow_flare', -16.3131)]
- [n/a ] 6. discrimination: no labelled good/faulty examples, so no target range is validated; 5 of 5 come from good-form demonstrations, 0 from everyday footage (what is typical, not what is good)
- [PASS] 7. outcome links: 5 links, 5 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.83 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **hips_sagging** (high, agreed by 5 of 5 runs): Keep the body in a straight line from shoulders to ankles at the bottom, with the hips and lower back not dropping toward the floor.. Target: angle.hip.dom at least 109.5438 at L1. Wrong if below: The hips and lower back sag toward the floor, or the hips pike, so the trunk and thigh are no longer in line at the bottom. (high). Range from good-form demonstrations (36 attempts in 4 clips); reliability C.
- 2. **hips_too_high** (medium, agreed by 4 of 5 runs): Start each rep with the hips level with the shoulders and feet, not piked up like a downward dog.. Target: height.hip between 0.1066 and 1.004 at L0. Wrong if above: Hips pike above the shoulder-to-feet line, so the chest moves toward the floor but the hips stay high, which turns the push-up into a pike press. (medium); below: Hips are already sagging low in the starting plank. (medium). Range from good-form demonstrations (36 attempts in 4 clips); reliability C.
- 3. **not_going_low_enough** (medium, agreed by 5 of 5 runs): Lower until the elbows reach about 90 degrees or the chest is close to the floor, then press back up.. Target: angle.elbow.dom at most 114.4466 at L1. Wrong if above: The elbows bend only a little and the chest stops well short of the floor, giving a partial range of motion. (medium). Range from good-form demonstrations (36 attempts in 4 clips); reliability C.
- 4. **wrong_hand_placement** (medium, agreed by 5 of 5 runs): Place the hands on the floor about shoulder width apart, under or just outside the shoulders and not ahead of them.. Target: dist.wrist_width between -0.0023 and 2.4271 at L0. Wrong if above: The hands are set much wider than the shoulders, which pushes the elbows out. (medium); below: The hands are set close together, narrower than the shoulders, which shifts the work toward the triceps and away from the chest. (low). Range from good-form demonstrations (36 attempts in 4 clips); reliability C.
- 5. **elbow_flare** (high, agreed by 5 of 5 runs): Keep the elbows angled back at a moderate angle from the body (not flared out to a T shape) as the chest lowers.. Target: angle.shoulder.dom between -16.3131 and 94.9847 at L1. Wrong if above: Elbows flare out to the sides, forming a T shape with the upper arms nearly perpendicular to the trunk at the bottom. (high); below: Elbows are pinned tight against the ribs, with the upper arms almost along the trunk. This is a different push-up variation and a smaller error. (low). Range from good-form demonstrations (36 attempts in 4 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **elbow_flare** (safety; 9 of 12, strong): measured by the camera (elbow_flare).
- **hips_sagging** (safety; 9 of 12, strong): measured by the camera (hips_sagging).
- **fast_bouncy_reps** (safety; 5 of 12, strong): would need a new body feature: rep tempo / angular velocity of the elbow angle (time per descent and ascent, bounce at the bottom).
- **head_neck_out_of_line** (form; 5 of 12, strong): would need a new body feature: head-to-trunk alignment angle (ear-shoulder-hip line). Coaches disagree: Source 4 says look down at a spot ahead of the hands, while source 6 says look straight ahead rather than down.
- **wrong_hand_placement** (form; 5 of 12, strong): only a proxy is measured (a test that goes with it, not the thing itself) (wrong_hand_placement). Coaches disagree: Source 3 says hands too narrow reduce chest work, while source 7 recommends just outside shoulder width or narrower.
- **hips_too_high** (form; 4 of 12, some): measured by the camera (hips_too_high).
- **not_going_low_enough** (form; 4 of 12, some): measured by the camera (not_going_low_enough).
- **scapular_control_wrong** (form; 4 of 12, some): would need a new body feature: scapular protraction/retraction: change in shoulder-blade/shoulder-width spacing across the rep. Coaches disagree: Sources 1, 2 and 3 want the blades to retract at the bottom and protract at the top. Source 0 says to keep them set and not retract and protract.
- **shoulders_collapsing_forward** (safety; 4 of 12, some): a body feature can show it but no objective tests it (no agreed target): fwd.trunk_shift (shoulder centre forward of ankles/wrists at the bottom).
- **body_not_moving_as_one_unit** (form; 3 of 12, some): would need a new body feature: relative timing of shoulder and hip vertical movement (chest-hip lag) across the rep. Coaches disagree: Source 0 wants the chest zone to touch the floor first, not the hips, while source 11 wants chest and hips to touch together, not chest first.
- **shoulder_shrugging** (form; 3 of 12, some): would need a new body feature: shoulder elevation: ear-to-shoulder distance / torso length.
- **arching_lower_back** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (hips_sagging).
- **hands_turned_in** (form; 2 of 12, some): would need a new body feature: hand direction relative to the body (hand turnout angle, from finger/hand landmarks). Coaches disagree: Source 0 allows fingers turned out to about 2:00, while source 7 wants the hands neutral.
- **no_lockout** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.elbow.dom at the top of the rep (max elbow angle). Coaches disagree: Source 9 says not to worry about locking out at the top, and has trainees push past it for scapular strength.
- **passive_hands_no_lats** (safety; 2 of 12, some): cannot be seen by the camera: ask the learner or use another sensor.
- **straight_up_down_path** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): fwd.trunk_shift (forward/back shoulder travel over the rep).
- **wrist_strain** (safety; 2 of 12, some): would need a new body feature: wrist extension angle (forearm to hand), from hand landmarks.
- **arms_tense_on_way_up** (form; 1 of 12, single): cannot be seen by the camera: ask the learner or use another sensor.
- **feet_too_wide** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): dist.stance_width.
- **poor_programming** (form; 1 of 12, single): cannot be seen by the camera: ask the learner or use another sensor.

Good form, as coaches give it:

- Keep elbows tucked at about 45° (an arrow shape from above, not a T), but not squeezed to the sides. (8 of 12)
- Keep the whole body tight in one straight line: glutes squeezed, core braced, quads locked, pelvis slightly tucked. (8 of 12)
- Set hands about shoulder width or just outside, directly under the shoulders, with fingers spread. (5 of 12)
- Keep the head and neck in line with the spine. (5 of 12)
- Move with control, lowering slowly, with no bouncing and no rushing. (5 of 12)
- Keep the shoulder blades back and chest open at the bottom, and keep the shoulders from rolling forward. (5 of 12)

Movement characterised by: angle.elbow.dom, angle.elbow.non, height.hip, angle.shoulder.dom, height.wrist_mid, reach.wrist.dom
Attempts found as: angle.elbow.dom falls. Typical size of the last event 94.691, lasting 2.79 s; smaller ones (below 37.876) or much longer or shorter ones are not attempts.

Footage: 860 clear attempts in 41 of 45 clips after 2 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| practice_session | 6 | 83 | unknown 83 |
| mistake_analysis | 6 | 49 | mixed 49 |
| instruction_talk | 5 | 45 | unknown 45 |
| other | 7 | 41 | unknown 41 |
| coach_demo | 6 | 38 | good_form 38 |
| pro_footage | 0 | 0 |  |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| hips_sagging | 6% (4 clips) | 1% (19 clips) | demos depart more: doubtful |
| hips_too_high | 4% (4 clips) | 8% (19 clips) | no difference: everyone is inside, or this measure does not separate them |
| not_going_low_enough | 5% (4 clips) | 5% (19 clips) | no difference: everyone is inside, or this measure does not separate them |
| wrong_hand_placement | 0% (4 clips) | 2% (19 clips) | no difference: everyone is inside, or this measure does not separate them |
| elbow_flare | 0% (4 clips) | 0% (19 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- lowering: L0 to L1
- pushing_up: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip IODxDxX7oi4: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 249 of 329 attempts (tolerance 2.321). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (-w6r23P-fy8, 4wS2kxDNPRA, 7ODJboTuANY, IODxDxX7oi4, KpjTZemHB1U, MO10KOoQx5E, PS4wjX-5AtU, QBM2qG5o4Es, TYSCQRmJAYk, UoQWEgKu8ww, WkRyOOQCVbo, Z88Rl5bpnmI, _q_-adYzkh0, f6wZv1n4sSw, qqyquVlh03Y, w-fQXFSysVw).

| clip | attempts found | kept | note |
|---|---|---|---|
| -0eYiItN2D8 | 15 | 13 |  |
| -w6r23P-fy8 | 7 | 7 | seed |
| 4JOSJDBlpQY | 8 | 0 | clip does not show the movement |
| 4wS2kxDNPRA | 6 | 6 | seed |
| 5WHdim80e7o | 10 | 0 | clip does not show the movement |
| 7ODJboTuANY | 15 | 14 | seed |
| 7xVMkYjVpiA | 10 | 10 |  |
| Ajna6AxQdtw | 15 | 0 | clip does not show the movement |
| I9fsqKE5XHo | 5 | 4 |  |
| IODxDxX7oi4 | 15 | 15 | seed |
| Kh50UfMS_Qc | 2 | 0 |  |
| KpjTZemHB1U | 6 | 6 | seed |
| L4bz6Gj7QX0 | 6 | 0 | clip does not show the movement |
| MO10KOoQx5E | 15 | 15 | seed |
| OPoF9zrDqUE | 15 | 0 | clip does not show the movement |
| PS4wjX-5AtU | 5 | 5 | seed |
| QBM2qG5o4Es | 15 | 15 | seed |
| SwDe1e7Pz60 | 9 | 9 |  |
| TYSCQRmJAYk | 10 | 10 | seed |
| UoQWEgKu8ww | 15 | 14 | seed |
| WkRyOOQCVbo | 15 | 15 | seed |
| YU-q60aJDv0 | 3 | 0 |  |
| Z88Rl5bpnmI | 13 | 9 | seed |
| _eQ2gw_Gg5Y | 5 | 0 | clip does not show the movement |
| _q_-adYzkh0 | 15 | 15 | seed |
| e8RJSXyN9MM | 13 | 13 |  |
| f6wZv1n4sSw | 7 | 5 | seed |
| hwnsLAFDuHA | 15 | 15 |  |
| qqyquVlh03Y | 15 | 15 | seed |
| w-fQXFSysVw | 15 | 15 | seed |
| xeb5ZuCtnPI | 7 | 4 |  |
| yS4zvJ_30dU | 2 | 0 |  |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist_mid=-0.932, height.wrist.non=-0.945, angle.elbow.non=154.099, height.wrist.dom=-0.921, angle.elbow.dom=148.757, reach.wrist.non=0.969, reach.wrist.dom=0.94, angle.shoulder.non=67.487, height.hip=0.405, angle.shoulder.dom=63.344
- L1 (t=0.531): height.wrist_mid=-0.341, height.wrist.non=-0.372, angle.elbow.non=86.574, height.wrist.dom=-0.313, angle.elbow.dom=92.539, reach.wrist.non=0.611, reach.wrist.dom=0.646, angle.shoulder.non=27.654, height.hip=-0.041, angle.shoulder.dom=38.778
- L2 (t=1.0): height.wrist_mid=-0.93, height.wrist.non=-0.942, angle.elbow.non=153.791, height.wrist.dom=-0.918, angle.elbow.dom=148.992, reach.wrist.non=0.972, reach.wrist.dom=0.946, angle.shoulder.non=66.661, height.hip=0.397, angle.shoulder.dom=62.632

## Per clip

| clip | attempts used | believable frames | view yaw | angle.elbow.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -0eYiItN2D8 | 13 | 87% | 38 | 144 | 74 / 85 / 107 |
| -w6r23P-fy8 | 7 | 84% | 8 | 167 | 90 / 94 / 102 |
| 09ZRt-f28cc | 1 | 57% | 19 | 145 | 96 / 96 / 96 |
| 4JOSJDBlpQY | 0 | 92% | 40 |  |  |
| 4wS2kxDNPRA | 6 | 75% | 68 | 142 | 83 / 88 / 99 |
| 5WHdim80e7o | 0 | 73% | 68 |  |  |
| 7ODJboTuANY | 14 | 99% | 77 | 141 | 89 / 92 / 110 |
| 7xVMkYjVpiA | 10 | 85% | 24 | 157 | 83 / 89 / 119 |
| Ajna6AxQdtw | 0 | 90% | 74 |  |  |
| BVqbzaI5nU4 | 1 | 72% | 8 | 138 | 115 / 115 / 115 |
| HcIoFm8dl3U | 0 | 59% | 11 |  |  |
| I9fsqKE5XHo | 4 | 84% | 71 | 158 | 83 / 87 / 96 |
| IODxDxX7oi4 | 15 | 88% | 59 | 161 | 90 / 93 / 113 |
| Kh50UfMS_Qc | 0 | 93% | 34 |  |  |
| KpjTZemHB1U | 6 | 51% | 59 | 155 | 85 / 88 / 92 |
| L4bz6Gj7QX0 | 0 | 92% | 39 |  |  |
| MO10KOoQx5E | 15 | 82% | 12 | 144 | 54 / 72 / 83 |
| OPoF9zrDqUE | 0 | 92% | 41 |  |  |
| PS4wjX-5AtU | 5 | 60% | 37 | 145 | 80 / 84 / 96 |
| QBM2qG5o4Es | 15 | 92% | 70 | 145 | 74 / 86 / 105 |
| QNoQ1CbSC_M | 0 | 38% | 25 |  |  |
| SwDe1e7Pz60 | 9 | 75% | 67 | 144 | 69 / 81 / 103 |
| TK95u_mohmY | 0 | 86% | 76 |  |  |
| TYSCQRmJAYk | 10 | 90% | 56 | 147 | 104 / 108 / 110 |
| TgQInnM4F30 | 1 | 95% | 84 | 158 | 79 / 79 / 79 |
| UoQWEgKu8ww | 14 | 90% | 35 | 153 | 103 / 111 / 131 |
| WkRyOOQCVbo | 15 | 93% | 68 | 153 | 92 / 98 / 112 |
| XYZ46bGfZ08 | 0 | 69% | 42 |  |  |
| YU-q60aJDv0 | 0 | 47% | 9 |  |  |
| Z88Rl5bpnmI | 9 | 78% | 55 | 152 | 61 / 75 / 87 |
| Zn_aYiEXymg | 1 | 67% | 50 | 167 | 113 / 113 / 113 |
| _eQ2gw_Gg5Y | 0 | 73% | 8 |  |  |
| _q_-adYzkh0 | 15 | 94% | 49 | 140 | 89 / 93 / 101 |
| bHUwyaAh_Mk | 1 | 69% | 12 | 160 | 100 / 100 / 100 |
| bQolznsOqTk | 1 | 95% | 50 | 147 | 80 / 80 / 80 |
| e8RJSXyN9MM | 13 | 79% | 65 | 149 | 68 / 81 / 94 |
| f6wZv1n4sSw | 5 | 84% | 45 | 145 | 88 / 95 / 128 |
| hwnsLAFDuHA | 15 | 73% | 62 | 151 | 71 / 92 / 106 |
| mECzqUIDWfU | 1 | 86% | 84 | 151 | 107 / 107 / 107 |
| pvIjsG5Svck | 0 | 86% | 87 |  |  |
| qqyquVlh03Y | 15 | 73% | 29 | 152 | 90 / 101 / 112 |
| w-fQXFSysVw | 15 | 96% | 56 | 148 | 103 / 104 / 107 |
| wIPJvBQs7RA | 0 | 98% | 72 |  |  |
| xeb5ZuCtnPI | 4 | 78% | 8 | 142 | 61 / 81 / 88 |
| yS4zvJ_30dU | 0 | 65% | 20 |  |  |

## Vocabulary proposals

- measurement: rep_tempo (descent and ascent duration, velocity) (Fast, bouncy reps that use momentum can't be shown by a posture feature. This needs the duration of each phase and the speed of change of the elbow angle.)
- feature: angle.head_neck_alignment (Head craning, poking forward or dropping needs a head-to-trunk angle (ear, shoulder, hip). No registered feature covers it.)
- feature: scapular_protraction / shoulder_blade_position (Scapular control and shoulders collapsing forward can't be seen from the registered joint angles. This needs a shoulder-blade or back-view feature.)
- feature: angle.lumbar_extension (spine curvature) (Arching of the lower back needs a spine curve measure, because the hip angle can't tell an arch from a pike.)
- feature: shoulder_height_difference (shoulder shrug) (Shrugging toward the ears needs the distance between ear and shoulder.)
- feature: shoulder_vs_hip_descent_lag (Chest and hips moving as one unit needs a comparison of the timing of shoulder-height and hip-height change.)
- feature: rot.hand_turnout (Hands turned in or out on the floor need a hand-direction feature. Only foot turnout is registered.)
