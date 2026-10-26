# Factory report: tennis_backhand

Clips found: 40 (usable for attempts: 37). Attempts: 411.
Confidence tier: **low**. Checks: 8 pass, 1 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.42 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [n/a ] 6. discrimination: no objective has enough labelled good and faulty examples (3 of each), so no target range is validated; 6 of 6 come from good-form demonstrations, 0 from everyday footage (what is typical, not what is good)
- [PASS] 7. outcome links: 4 links, 4 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.61 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 4 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept; left out for lack of agreement: poor_recovery.

- 1. **insufficient_turn** (medium, agreed by 5 of 5 runs): Turn the shoulders relative to the hips to load the trunk and then unwind through the shot.. Target: angle.shoulder_hip_twist between -33.0647 and 38.319 at L1. Wrong if below: Shoulders and hips move as one block, or the player pokes at the ball with the arms. (medium); above: Over-rotated shoulders relative to hips. (low). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.
- 2. **pulling_across_body** (medium, agreed by 4 of 5 runs): Extend the hitting arm out through the ball instead of pulling the racket across the body.. Target: reach.wrist.dom between 0.5312 and 1.0974 at L1. Wrong if below: Wrist stays close to the shoulder; racket is dragged across the chest rather than extended. (medium); above: Arm overly stretched out away from body at the finish. (low). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.
- 3. **elbows_tucked_in** (low, agreed by 5 of 5 runs): Keep the hitting elbow and arm out from the body, with room to swing, rather than jammed against the body.. Target: angle.shoulder.dom at most 132.6362 at L1. Wrong if above: Arm lifted very far from body at the finish. (low). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.
- 4. **short_follow_through** (medium, agreed by 3 of 5 runs): Swing through the ball and finish with the hands and racket rising to a high finish rather than stopping early.. Target: height.wrist_mid between -0.7915 and 0.4543 at L1. Wrong if below: Swing checks or stops after contact; hands finish low and the racket does not finish up. (medium); above: Hands finish very high, over the shoulder; usually harmless. (low). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.
- 5. **upright_not_low** (medium, agreed by 5 of 5 runs): Stay low through the shot, bending the legs and transferring weight into the front leg rather than standing tall.. Target: height.hip at most 1.6305 at L1. Wrong if above: Standing tall on a straight front leg with little weight transfer; body pops up. (medium). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.
- 6. **non_dominant_arm_inactive** (low, agreed by 5 of 5 runs): Use the non-dominant arm actively: let it lead the extension or move away as the hitting arm comes forward.. Target: angle.shoulder.non between 0.3792 and 108.1913 at L1. Wrong if below: Non-hitting arm hangs or stays in place by the body. (low); above: Non-hitting arm flung out to the side. (low). Range from good-form demonstrations (132 attempts in 12 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **tight_grip_or_wrists** (form; 5 of 12, strong): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **faulty_takeback** (form; 4 of 12, some): a body feature can show it but no objective tests it (no agreed target): height.wrist.dom, angle.elbow.dom and reach.wrist.dom show takeback height, length and arm straightness, but no objective tests them. Coaches disagree: Source 0 wants the racket head above the hands at the start of the loop, source 2 wants a low takeback, and source 10 wants the racket head up; a down-and-back takeback is a fault for source 0 but acceptable on returns.
- **pulling_across_body** (form; 4 of 12, some): measured by the camera (pulling_across_body).
- **arm_only_hitting** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (insufficient_turn).
- **elbows_tucked_in** (form; 3 of 12, some): measured by the camera (elbows_tucked_in).
- **excess_wrist_action** (safety; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks or racket detection to track wrist break and racket-face roll.
- **late_preparation** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection to time the ball's bounce and net crossing against the start of the turn.
- **non_dominant_arm_inactive** (form; 3 of 12, some): measured by the camera (non_dominant_arm_inactive).
- **wrong_grip_position** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to show hand position on the racket handle and bevels. Coaches disagree: The sources recommend different grips: left bevel 7 and right bevel 2 (3); bottom Continental or Eastern, top Eastern (4); dominant Eastern or semi-western, non-dominant Continental (5); dominant Continental, non-dominant mild Eastern or semi-western (11).
- **insufficient_turn** (form; 2 of 12, some): measured by the camera (insufficient_turn).
- **poor_recovery** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): dist.stance_width, lat.com_shift and fwd.trunk_shift over time could show stepping out or stopping, but no objective tests them.
- **short_follow_through** (form; 2 of 12, some): measured by the camera (short_follow_through).
- **upright_not_low** (form; 2 of 12, some): measured by the camera (upright_not_low).
- **eye_dominance_footwork_mismatch** (form; 1 of 12, single): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **flat_low_clearance_ball** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection to track the ball's trajectory and net clearance.
- **high_balls_over_shoulder** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection to track the ball's height and contact point.
- **lifting_arm_for_spin** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection to show racket head path around the hand versus arm lift.
- **rushing_or_reaching** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (pulling_across_body).
- **stepping_across_stuck** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): dist.stance_width, lat.com_shift and rot.foot_turnout.dom could show stepping across, but no objective tests them.

Good form, as coaches give it:

- Follow through fully, finishing high over the opposite shoulder with the racket tip up, then release and recover. (6 of 12)
- Turn the shoulders (and hips less than shoulders) fully, until the front shoulder is under the chin, so the body powers the shot. (5 of 12)
- Keep the grip and wrists relaxed, so the racket can drop under the ball and accelerate. (5 of 12)
- Let the racket drop below the ball, then swing low to high to a contact point out in front. (5 of 12)
- Use the non-dominant hand as the leading, swinging hand, with the bottom hand only stabilizing. (5 of 12)
- Stay low and athletic with bent legs, and transfer weight forward through the ball. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **load_and_unwind_the_trunk** (biomechanics, 3 of 3 runs; explains insufficient_turn, arm_only_hitting, non_dominant_arm_inactive): Power comes from the big muscles of the legs, hips and trunk, not the arms. Turning the shoulders against the hips stores energy in the trunk, and unwinding it passes that energy up the chain into the racket. Cue handle: .
- **ground_up_weight_transfer** (biomechanics, 3 of 3 runs; explains upright_not_low, arm_only_hitting, poor_recovery): Bending the legs and moving weight into the front leg lets the body push against the ground and carry that force forward into the shot. Standing tall breaks that link and leaves the arm to do the work. Cue handle: Stay low and let your weight travel through the ball toward the target..
- **extend_through_the_ball** (coaching_consensus, 3 of 3 runs; explains pulling_across_body, elbows_tucked_in, short_follow_through, stepping_across_stuck, non_dominant_arm_inactive): Space for the arm to swing and a path that extends out through the ball keep the racket on the line of the shot for longer. Pulling across the body or stopping early cuts the swing short and wastes the speed you built. Cue handle: Send the racket out toward the target and keep it travelling up to a high finish..
- **loose_hands_let_racket_accelerate** (coaching_consensus, 3 of 3 runs; explains tight_grip_or_wrists, excess_wrist_action, lifting_arm_for_spin): A relaxed grip and loose wrists let the racket head lag and then speed up freely as the body unwinds. Squeezing or tensing stops it dropping and swinging, and breaking the wrist makes it roll over instead of guiding through. Cue handle: Let the racket feel heavy and free so it whips through by itself..

## Check against labelled mistake videos (23 videos, 269 attempts, 98 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| faulty_takeback | 8 / 4 | 1 / 1 |
| short_follow_through | 2 / 2 | 52 / 12 |
| elbows_tucked_in | 1 / 1 | 9 / 2 |
| excess_wrist_action | 0 / 0 | 1 / 1 |
| insufficient_turn | 0 / 0 | 3 / 2 |
| non_dominant_arm_inactive | 0 / 0 | 2 / 2 |
| poor_recovery | 0 / 0 | 13 / 1 |
| pulling_across_body | 0 / 0 | 1 / 1 |
| upright_not_low | 0 / 0 | 3 / 2 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| insufficient_turn | 3 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| pulling_across_body | 1 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| elbows_tucked_in | 9 / 1 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| short_follow_through | 52 / 2 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| upright_not_low | 3 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| non_dominant_arm_inactive | 2 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.wrist_mid, height.wrist.dom, height.wrist.non, angle.shoulder.dom, angle.shoulder.non, reach.wrist.dom
Attempts found as: height.wrist_mid rises (to at least 0.0). Typical size of the last event 1.285, lasting 1.77 s; smaller ones (below 0.514) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 380 clear attempts in 18 of 19 clips after 1 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 22 | 246 | mixed 246 |
| pro_footage | 10 | 115 | good_form 115 |
| coach_demo | 4 | 33 | good_form 18, mixed 15 |
| practice_session | 3 | 19 | good_form 2, unknown 17 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| insufficient_turn | 12% (12 clips) | 9% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| pulling_across_body | 6% (12 clips) | 7% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| elbows_tucked_in | 2% (12 clips) | 3% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| short_follow_through | 3% (12 clips) | 7% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| upright_not_low | 0% (12 clips) | 0% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| non_dominant_arm_inactive | 5% (12 clips) | 7% (25 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- prepare_and_swing: L0 to L1
- finish_and_recover: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip 2h6r6upGt8I: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 411 of 411 attempts (tolerance 2.04). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (2h6r6upGt8I, 8d-wKLOUa7c, DA8sM2ilEsc, OfT3Qu9WFDc, UEhEvPrTjwc, Us8NR4iFovs, WWLo4_FAnkk, c6kda39TIr0, iXBBCqS_mVA, jVkUJII5Cn4, k6oFVTj3RWg, mO6XiArAjPI, q6q9t6kbrdY, w4xG2fkHfJA, xlzY0ZBdFmM, y-RLOCf5yFQ, yWhXMYo4prc, zZ2zmsPIMXI).

| clip | attempts found | kept | note |
|---|---|---|---|
| 0WjRNWc4OkA | 15 | 15 |  |
| 2h6r6upGt8I | 15 | 15 | seed |
| 40ZjU6Hp9dQ | 15 | 15 |  |
| 8d-wKLOUa7c | 11 | 11 | seed |
| C6lGp3xVxq8 | 12 | 12 |  |
| DA8sM2ilEsc | 15 | 15 | seed |
| ELI4ojmMXJk | 15 | 15 |  |
| H4KAAHoLhQo | 15 | 15 |  |
| LcB7We4VK-Q | 10 | 10 |  |
| N4D9HNumgQo | 13 | 13 |  |
| NG-uJLenLoE | 7 | 7 |  |
| OfT3Qu9WFDc | 15 | 15 | seed |
| UEhEvPrTjwc | 7 | 7 | seed |
| UUYZwAquhe8 | 15 | 15 |  |
| Us8NR4iFovs | 15 | 15 | seed |
| VjiyNLuFDlo | 13 | 13 |  |
| WWLo4_FAnkk | 15 | 15 | seed |
| WtzF3LfsjSA | 4 | 4 |  |
| YmIvcCAGpKM | 15 | 15 |  |
| aSoXddB7rPg | 15 | 15 |  |
| b6nD-NdKhPU | 2 | 2 |  |
| c6kda39TIr0 | 2 | 2 | seed |
| iXBBCqS_mVA | 15 | 15 | seed |
| jVkUJII5Cn4 | 3 | 3 | seed |
| jf2vpi4GG3A | 5 | 5 |  |
| k1i21RvVCaQ | 12 | 12 |  |
| k6oFVTj3RWg | 15 | 15 | seed |
| mO6XiArAjPI | 15 | 15 | seed |
| nuRh27czEy8 | 3 | 3 |  |
| q6q9t6kbrdY | 2 | 2 | seed |
| qdvd0jB2NBU | 2 | 2 |  |
| r1KRhB4QeCg | 15 | 15 |  |
| w4xG2fkHfJA | 15 | 15 | seed |
| xlzY0ZBdFmM | 15 | 15 | seed |
| y-RLOCf5yFQ | 15 | 15 | seed |
| yWhXMYo4prc | 15 | 15 | seed |
| zZ2zmsPIMXI | 3 | 3 | seed |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist_mid=-0.696, height.wrist.dom=-0.715, height.wrist.non=-0.714, angle.shoulder.dom=31.263, angle.shoulder.non=32.259, reach.wrist.non=0.884, angle.trunk_lean=13.946, angle.elbow.non=136.515, reach.wrist.dom=0.873, angle.elbow.dom=136.474
- L1 (t=0.449): height.wrist_mid=-0.106, height.wrist.dom=-0.091, height.wrist.non=-0.138, angle.shoulder.dom=65.012, angle.shoulder.non=57.759, reach.wrist.non=0.764, angle.trunk_lean=7.897, angle.elbow.non=118.685, reach.wrist.dom=0.794, angle.elbow.dom=126.802
- L2 (t=1.0): height.wrist_mid=-0.688, height.wrist.dom=-0.681, height.wrist.non=-0.693, angle.shoulder.dom=29.749, angle.shoulder.non=30.93, reach.wrist.non=0.856, angle.trunk_lean=9.483, angle.elbow.non=130.97, reach.wrist.dom=0.856, angle.elbow.dom=130.206

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist_mid at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| 0WjRNWc4OkA | 15 | 100% | 17 | -0.76 | -0.74 / -0.19 / 0.08 |
| 2h6r6upGt8I | 15 | 100% | 48 | -0.67 | -0.46 / 0.09 / 0.24 |
| 40ZjU6Hp9dQ | 15 | 90% | 35 | -0.72 | -0.44 / -0.23 / -0.0 |
| 8d-wKLOUa7c | 11 | 98% | 11 | -0.74 | -0.11 / 0.1 / 0.33 |
| C6lGp3xVxq8 | 12 | 87% | 22 | -0.67 | -0.3 / -0.12 / 0.06 |
| CWGpyv89lcc | 0 | 93% | 52 |  |  |
| DA8sM2ilEsc | 15 | 97% | 35 | -0.67 | -0.51 / -0.29 / 0.05 |
| ELI4ojmMXJk | 15 | 98% | 53 | -0.61 | -0.4 / 0.05 / 0.33 |
| H4KAAHoLhQo | 15 | 98% | 24 | -0.86 | -0.38 / 0.3 / 0.59 |
| LcB7We4VK-Q | 10 | 96% | 11 | -0.7 | -0.4 / 0.12 / 0.36 |
| N4D9HNumgQo | 13 | 99% | 26 | -0.68 | 0.03 / 0.23 / 0.52 |
| NG-uJLenLoE | 7 | 98% | 7 | -0.71 | -0.67 / -0.11 / 0.06 |
| OfT3Qu9WFDc | 15 | 80% | 30 | -0.7 | -0.77 / -0.13 / 0.12 |
| UEhEvPrTjwc | 7 | 99% | 38 | -0.53 | -0.7 / -0.66 / -0.28 |
| UUYZwAquhe8 | 15 | 98% | 15 | -0.66 | -0.57 / -0.2 / 0.1 |
| Ulk_gXK9GrI | 1 | 93% | 59 | -0.35 | 0.2 / 0.2 / 0.2 |
| Us8NR4iFovs | 15 | 99% | 27 | -0.74 | -0.49 / 0.17 / 0.51 |
| VjiyNLuFDlo | 13 | 86% | 40 | -0.67 | -0.53 / -0.2 / 0.03 |
| WWLo4_FAnkk | 15 | 91% | 13 | -0.9 | -0.64 / -0.16 / 0.08 |
| WtzF3LfsjSA | 4 | 93% | 9 | -0.71 | -0.24 / -0.03 / 0.01 |
| YmIvcCAGpKM | 15 | 96% | 28 | -0.77 | -0.62 / -0.25 / 0.02 |
| aSoXddB7rPg | 15 | 99% | 14 | -0.83 | -0.71 / -0.07 / 0.23 |
| b6nD-NdKhPU | 2 | 84% | 23 | -0.77 | -0.57 / -0.31 / -0.04 |
| c6kda39TIr0 | 2 | 85% | 54 | -0.61 | -0.45 / -0.24 / -0.03 |
| iXBBCqS_mVA | 15 | 93% | 41 | -0.64 | -0.46 / 0.11 / 0.34 |
| jVkUJII5Cn4 | 3 | 100% | 8 | -0.6 | -0.44 / -0.14 / 0.03 |
| jf2vpi4GG3A | 5 | 95% | 15 | -0.37 | -0.02 / -0.0 / 0.04 |
| k1i21RvVCaQ | 12 | 100% | 14 | -0.56 | -0.69 / -0.34 / 0.2 |
| k6oFVTj3RWg | 15 | 97% | 50 | -0.77 | -0.49 / -0.27 / -0.03 |
| mO6XiArAjPI | 15 | 99% | 55 | -0.62 | -0.33 / -0.08 / 0.01 |
| nuRh27czEy8 | 3 | 94% | 17 | -0.87 | -0.26 / 0.05 / 0.18 |
| q6q9t6kbrdY | 2 | 100% | 42 | -0.65 | -0.21 / -0.21 / -0.21 |
| qdvd0jB2NBU | 2 | 92% | 56 | -0.61 | -0.74 / -0.42 / -0.09 |
| r1KRhB4QeCg | 15 | 99% | 55 | -0.7 | -0.69 / -0.1 / 0.2 |
| tlysHumoDug | 1 | 98% | 19 | -1.02 | -0.07 / -0.07 / -0.07 |
| w4xG2fkHfJA | 15 | 94% | 39 | -0.64 | -0.61 / -0.46 / -0.09 |
| xlzY0ZBdFmM | 15 | 87% | 18 | -0.79 | -0.59 / 0.03 / 0.35 |
| y-RLOCf5yFQ | 15 | 86% | 45 | -0.71 | -0.57 / -0.08 / 0.13 |
| yWhXMYo4prc | 15 | 99% | 18 | -0.7 | -0.71 / -0.28 / 0.07 |
| zZ2zmsPIMXI | 3 | 85% | 28 | -0.32 | -0.2 / 0.03 / 0.12 |

## Vocabulary proposals

- trackable: racket (Needed to judge racket-head position in the takeback, drop and finish (faulty_takeback, pulling across the body).)
- trackable: ball (Needed to judge late preparation (turn relative to the ball's bounce/crossing the net) and outcomes such as depth and landing area.)
- feature: angle.wrist_flexion.dom (Needed to test excess wrist action (breaking, scooping, casting the wrist) which no current feature shows.)
- feature: grip_bevel (Needed to test wrong grip position; hand posture is not visible in registered body features.)
- feature: forearm_tension (Tight grip or tense wrists cannot be observed with registered features.)
- measurement: time_from_bounce_to_turn_start (Needed to judge late preparation relative to ball events.)
- feature: eye_dominance_alignment (Needed to test mismatch between eye dominance and footwork (head/eye facing relative to the shoulders).)
- feature: racket_head_height_above_hands (Needed to adjudicate the takeback disagreement (racket head up versus low).)
