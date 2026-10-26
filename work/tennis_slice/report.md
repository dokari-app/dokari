# Factory report: tennis_slice

Clips found: 58 (usable for attempts: 48). Attempts: 524.
Confidence tier: **low**. Checks: 8 pass, 2 fail, 0 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.57 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [FAIL] 6. discrimination: 0/1 objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75); do not: ['left_arm_not_counterbalancing']; 4 without enough labels
- [PASS] 7. outcome links: 3 links, 3 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.88 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 5 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **late_turn_low_takeback** (medium, agreed by 5 of 5 runs): Turn early and take the racket back high, with the hitting wrist up near shoulder height, so there is room to swing down on the ball.. Target: height.wrist.dom between -0.7019 and 0.6475 at L1. Wrong if below: Racket stays low and flat beside the hip with a late turn, so there is no height to swing down from. (medium); above: Racket lifted well above the shoulder, a long loose takeback that is hard to control. (low). Range from good-form demonstrations (225 attempts in 22 clips); reliability C.
- 2. **undercutting_ball** (medium, agreed by 3 of 5 runs): Keep the hitting elbow and upper arm lifted at the top of the takeback so the racket can come down on the ball from above.. Target: angle.shoulder.dom between 6.9936 and 127.2391 at L1. Wrong if below: Dropped elbow and level shoulders, the racket goes under the ball rather than down on it. (medium); above: Elbow lifted very high away from the body, an overly big takeback. (low). Range from good-form demonstrations (225 attempts in 22 clips); reliability C.
- 3. **opening_up_early** (medium, agreed by 5 of 5 runs): Keep the shoulders turned (coiled) against the hips at the top of the takeback and stay sideways into contact instead of opening the chest early.. Target: angle.shoulder_hip_twist at least -34.0417 at L1. Wrong if below: Shoulders barely turned relative to the hips, chest already facing the net before contact. (medium). Range from good-form demonstrations (225 attempts in 22 clips); reliability C.
- 4. **elbow_swing_changes_angle** (medium, agreed by 5 of 5 runs): Keep the hitting-arm angle steady through the swing, moving the arm from the shoulder rather than straightening it from the elbow.. Target: angle.elbow.dom between 102.0393 and 165.8019 at L2. Wrong if above: Arm straightens from the elbow on the way through, losing the L-shape and racket control. (medium); below: Arm collapses and folds tightly at the finish. (low). Range from good-form demonstrations (225 attempts in 22 clips); reliability C.
- 5. **left_arm_not_counterbalancing** (low, agreed by 5 of 5 runs): Keep the non-hitting arm out and back through and after contact to counterbalance the swing.. Target: angle.shoulder.non at least 5.3649 at L2. Wrong if below: Non-hitting arm drops to the side or is pulled in as the body turns with the ball. (low). Range from good-form demonstrations (225 attempts in 22 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **wrist_flicking** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to measure wrist angle (hand vs forearm).
- **wrong_grip** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection for grip. Coaches disagree: Sources differ on the result: 1 says heavy side spin, 7 says an open face and floating ball, and 11 says an awkward defensive slice and a flat face when closed.
- **late_turn_low_takeback** (form; 2 of 12, some): measured by the camera (late_turn_low_takeback).
- **opening_up_early** (form; 2 of 12, some): measured by the camera (opening_up_early).
- **undercutting_ball** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (undercutting_ball).
- **arm_powering_the_shot** (form; 1 of 12, single): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **contact_too_far_forward** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): reach.wrist.dom (wrist distance from shoulder) at contact; ideal contact point is coach-dependent.
- **dropping_l_shape** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (elbow_swing_changes_angle).
- **elbow_swing_changes_angle** (form; 1 of 12, single): measured by the camera (elbow_swing_changes_angle).
- **face_control_lost_on_way_down** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection for racket face angle.
- **face_too_open** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection for racket face angle.
- **left_arm_not_counterbalancing** (form; 1 of 12, single): measured by the camera (left_arm_not_counterbalancing).
- **over_supinating** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection for forearm rotation and racket head position.
- **racket_tip_comes_through** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection to track racket tip.
- **reverse_pivot** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): fwd.trunk_shift (and lat.com_shift) over the swing show stepping/leaning back.
- **slicing_across_body** (form; 1 of 12, single): would need a new body feature: hitting wrist lateral position relative to the body midline / shoulder line.
- **too_flat_on_top** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket and ball detection for swing path and contact.
- **too_little_arm_action** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): range of motion of reach.wrist.dom or angle.shoulder.dom through the swing.
- **weak_coil_setup** (form; 1 of 12, single): measured by the camera (opening_up_early).
- **wrist_neutral_too_early** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to measure wrist angle at contact. Coaches disagree: Source 6 wants a cocked, tensioned wrist, while sources 0, 5 and 7 stress a firm, fixed wrist angle. The sources do not clearly contradict each other.

Good form, as coaches give it:

- Swing down through the ball from high to low, keeping the racket face square, then let the racket rise after contact. (5 of 12)
- Turn early and take the racket back high, above the shoulder or head, to create leverage. (4 of 12)
- Keep the racket face angle fixed through the downward swing, because the face sets direction and height and the path adds spin. (4 of 12)
- Keep the wrist firm and steady with no change in angle, and let the forearm and big muscles control the face. (4 of 12)
- Use a Continental (hammer) grip so racket and forearm line up and the face is square to the net at contact. (3 of 12)
- Play the stroke from the shoulder and back, with little elbow, and relax the arm once the forward swing starts. (3 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **early_turn_builds_height_to_swing_down** (coaching_consensus, 3 of 3 runs; explains late_turn_low_takeback, undercutting_ball, weak_coil_setup): Turning early and lifting the racket to a high L-shape gives the racket height and room to travel down through the ball. A low, late takeback leaves nowhere to swing but under or across it. Cue handle: Get the racket set high early so it has room to fall down onto the ball..
- **coil_then_stay_sideways** (coaching_consensus, 3 of 3 runs; explains opening_up_early, arm_powering_the_shot, reverse_pivot): Shoulders turned against the hips store rotational tension. Staying sideways into contact lets the swing be driven by the shoulder and back, not by the chest opening early or by the arm tensing. Cue handle: Stay coiled and let the swing unwind late, as the racket arrives at the ball..
- **steady_arm_shape_swings_from_shoulder** (contested, 3 of 3 runs; explains elbow_swing_changes_angle, wrist_flicking, dropping_l_shape, face_control_lost_on_way_down, wrist_neutral_too_early): A steady arm angle and a firm wrist keep the racket-face angle the same swing after swing. Moving the arm as one unit from the shoulder, rather than flicking the wrist or straightening the elbow, keeps the L-shape and the contact repeatable. Cue handle: Keep the racket's shape unchanged so the face stays the same through the ball.. Competing views: Source 6 wants a cocked, tensioned wrist through the swing.; Sources 0, 5 and 7 stress a firm, fixed wrist angle..
- **counterbalance_with_free_arm** (coaching_consensus, 3 of 3 runs; explains left_arm_not_counterbalancing, opening_up_early): The free arm held out and back balances the swinging arm and helps the body stay turned through contact. It slows the chest from rotating with the ball. Cue handle: Keep the body balanced and quiet while the racket moves through..
- **grip_sets_face_angle** (contested, 2 of 3 runs; explains wrong_grip, face_too_open): The grip sets the racket-face angle the hand brings to the ball. Coaches here favour Continental for the slice, but they disagree on what other grips produce. Cue handle: . Competing views: One source says a non-Continental grip still gives heavy side spin.; Another source says it gives an open face and a floating ball.; A third source says it gives an awkward, defensive slice and a flat face when closed..

## Check against labelled mistake videos (29 videos, 311 attempts, 147 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| contact_too_far_forward | 5 / 1 | 2 / 1 |
| left_arm_not_counterbalancing | 5 / 4 | 9 / 3 |
| opening_up_early | 3 / 2 | 2 / 2 |
| slicing_across_body | 3 / 1 | 3 / 1 |
| undercutting_ball | 3 / 3 | 0 / 0 |
| wrist_flicking | 2 / 1 | 1 / 1 |
| dropping_l_shape | 1 / 1 | 0 / 0 |
| late_turn_low_takeback | 1 / 1 | 15 / 4 |
| racket_tip_comes_through | 0 / 0 | 2 / 1 |
| reverse_pivot | 0 / 0 | 4 / 3 |
| wrong_grip | 0 / 0 | 1 / 1 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| late_turn_low_takeback | 15 / 1 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| undercutting_ball | 0 / 3 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| opening_up_early | 0 / 3 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| elbow_swing_changes_angle | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| left_arm_not_counterbalancing | 9 / 5 | 3 / 4 | 0.38 | 52% | does not tell right from wrong well enough; range kept from good form demonstrations |

Movement characterised by: height.wrist.dom, angle.shoulder.dom, height.wrist_mid, angle.elbow.dom
Attempts found as: height.wrist.dom rises (to at least 0.0). Typical size of the last event 1.438, lasting 2.41 s; smaller ones (below 0.575) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 466 clear attempts in 30 of 34 clips after 2 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 27 | 300 | mixed 300 |
| coach_demo | 12 | 145 | good_form 145 |
| pro_footage | 12 | 82 | good_form 82 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| late_turn_low_takeback | 6% (22 clips) | 6% (26 clips) | no difference: everyone is inside, or this measure does not separate them |
| undercutting_ball | 4% (22 clips) | 4% (26 clips) | no difference: everyone is inside, or this measure does not separate them |
| opening_up_early | 7% (22 clips) | 1% (26 clips) | demos depart more: doubtful |
| elbow_swing_changes_angle | 8% (22 clips) | 13% (26 clips) | everyday footage departs more: the objective picks up a difference from good form |
| left_arm_not_counterbalancing | 0% (22 clips) | 1% (26 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- turn_and_takeback: L0 to L1
- downward_swing_and_finish: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip 3Ex_I5A3xRY: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 524 of 527 attempts (tolerance 2.019). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (0WjRNWc4OkA, 0Zr-iNkH4mw, 12Km_yWVppw, 1WruwNr8CJo, 3Ex_I5A3xRY, 5wdrcvQQJMg, 8J3BpWJUdmM, 9-I3bpN0ZsU, A6rXAdnieeM, EEHaZ4PrUFI, GW463x8rhw0, H-mGGf9D3kE, JPLgQVP5yQo, L3ZzViOphWc, Op-AV2OVt6Q, RKH7U9fT98c, Wtrvw88_-kk, bGKXJZcwSEc, dBrNLTahdaY, dY3sTyUxTCk, eKpsVdBi7Ww, gwZt6tExL0E, j3s-3XW2sck, j7TGZzsocgg, jmGqii5G3E0, kddPZBiGsLM, lBjDpj4qcJE, t6lmLmDL51E, y0fyVtkT0Os).

| clip | attempts found | kept | note |
|---|---|---|---|
| -56d6PVdSXg | 15 | 15 |  |
| 0WjRNWc4OkA | 15 | 15 | seed |
| 0Zr-iNkH4mw | 15 | 15 | seed |
| 12Km_yWVppw | 15 | 15 | seed |
| 1WruwNr8CJo | 15 | 15 | seed |
| 3Ex_I5A3xRY | 15 | 15 | seed |
| 4WUUdz9McfE | 15 | 15 |  |
| 5wdrcvQQJMg | 15 | 15 | seed |
| 7njJvDaNXyc | 15 | 15 |  |
| 8J3BpWJUdmM | 9 | 9 | seed |
| 9-I3bpN0ZsU | 2 | 2 | seed |
| 9F3UYGMsqA0 | 6 | 6 |  |
| A6rXAdnieeM | 8 | 8 | seed |
| A9XC-kop1zM | 5 | 5 |  |
| BG9xU9Ikjtk | 15 | 15 |  |
| EEHaZ4PrUFI | 15 | 15 | seed |
| EWJGWcVx-nM | 15 | 15 |  |
| GW463x8rhw0 | 4 | 4 | seed |
| H-mGGf9D3kE | 12 | 12 | seed |
| JPLgQVP5yQo | 10 | 10 | seed |
| JXMXLy82_Ng | 14 | 13 |  |
| L3ZzViOphWc | 12 | 12 | seed |
| Op-AV2OVt6Q | 5 | 5 | seed |
| QblBVxDSv0I | 15 | 15 |  |
| RKH7U9fT98c | 10 | 10 | seed |
| UUYZwAquhe8 | 15 | 15 |  |
| Wtrvw88_-kk | 15 | 15 | seed |
| Zd_rWYHScAo | 4 | 4 |  |
| aSFlQU3-F1o | 15 | 15 |  |
| b6nD-NdKhPU | 5 | 5 |  |
| bGKXJZcwSEc | 15 | 15 | seed |
| dBrNLTahdaY | 15 | 15 | seed |
| dY3sTyUxTCk | 12 | 11 | seed |
| eKpsVdBi7Ww | 7 | 7 | seed |
| gwZt6tExL0E | 10 | 10 | seed |
| iIw-6hWgAmQ | 5 | 5 |  |
| j3s-3XW2sck | 5 | 5 | seed |
| j7TGZzsocgg | 6 | 6 | seed |
| jmGqii5G3E0 | 15 | 15 | seed |
| kddPZBiGsLM | 15 | 15 | seed |
| lBjDpj4qcJE | 2 | 2 | seed |
| n-2cN7V4amY | 12 | 11 |  |
| rarWfNSPDHw | 12 | 12 |  |
| sqwfUGFzlr8 | 6 | 6 |  |
| t6lmLmDL51E | 15 | 15 | seed |
| w4xG2fkHfJA | 15 | 15 |  |
| y0fyVtkT0Os | 5 | 5 | seed |
| zZ2zmsPIMXI | 9 | 9 |  |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist.dom=-0.717, height.wrist_mid=-0.681, angle.shoulder.dom=29.82, height.wrist.non=-0.655, reach.wrist.dom=0.878, angle.shoulder.non=32.558, angle.elbow.dom=132.84, reach.wrist.non=0.854, fwd.trunk_shift=0.34, angle.ankle.non=112.377
- L1 (t=0.429): height.wrist.dom=-0.03, height.wrist_mid=-0.21, angle.shoulder.dom=64.947, height.wrist.non=-0.351, reach.wrist.dom=0.788, angle.shoulder.non=46.043, angle.elbow.dom=124.14, reach.wrist.non=0.803, fwd.trunk_shift=0.248, angle.ankle.non=115.637
- L2 (t=1.0): height.wrist.dom=-0.737, height.wrist_mid=-0.684, angle.shoulder.dom=29.035, height.wrist.non=-0.65, reach.wrist.dom=0.867, angle.shoulder.non=32.492, angle.elbow.dom=133.524, reach.wrist.non=0.855, fwd.trunk_shift=0.305, angle.ankle.non=112.709

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -56d6PVdSXg | 15 | 97% | 38 | -0.92 | -0.27 / 0.04 / 0.42 |
| -Wa9L1sK0to | 1 | 95% | 8 | -0.72 | -0.22 / -0.22 / -0.22 |
| 0WjRNWc4OkA | 15 | 100% | 17 | -0.78 | -0.36 / -0.0 / 0.16 |
| 0Zr-iNkH4mw | 15 | 98% | 20 | -0.73 | -0.52 / -0.08 / 0.06 |
| 12Km_yWVppw | 15 | 94% | 19 | -0.62 | -0.57 / -0.12 / 0.09 |
| 1WruwNr8CJo | 15 | 93% | 52 | -0.61 | -0.71 / -0.28 / 0.18 |
| 3Ex_I5A3xRY | 15 | 95% | 5 | -0.92 | -0.64 / -0.18 / 0.22 |
| 4WUUdz9McfE | 15 | 92% | 48 | -0.82 | -0.48 / 0.1 / 0.38 |
| 5wdrcvQQJMg | 15 | 97% | 32 | -0.65 | -0.37 / -0.09 / 0.08 |
| 7njJvDaNXyc | 15 | 97% | 13 | -0.8 | -0.33 / 0.01 / 0.18 |
| 8FbdM5OlR6k | 0 | 98% | 62 |  |  |
| 8J3BpWJUdmM | 9 | 85% | 27 | -0.56 | -0.39 / -0.04 / 0.25 |
| 9-I3bpN0ZsU | 2 | 99% | 18 | -0.65 | -0.55 / -0.48 / -0.41 |
| 9F3UYGMsqA0 | 6 | 93% | 43 | -0.78 | -0.38 / 0.13 / 0.43 |
| A6rXAdnieeM | 8 | 100% | 8 | -0.6 | -0.22 / -0.08 / 0.0 |
| A9XC-kop1zM | 5 | 78% | 5 | -0.53 | -0.53 / 0.27 / 0.5 |
| BG9xU9Ikjtk | 15 | 100% | 33 | -0.65 | -0.16 / 0.12 / 0.39 |
| CIr1f34AIvs | 0 | 100% | 19 |  |  |
| EEHaZ4PrUFI | 15 | 94% | 9 | -0.89 | -0.5 / -0.02 / 0.24 |
| EWJGWcVx-nM | 15 | 88% | 52 | -0.66 | -0.5 / 0.06 / 0.35 |
| GW463x8rhw0 | 4 | 99% | 57 | -0.93 | -0.43 / -0.12 / -0.02 |
| H-mGGf9D3kE | 12 | 99% | 33 | -0.62 | -0.71 / -0.19 / 0.22 |
| HxJxBl8Obhs | 0 | 100% | 17 |  |  |
| JPLgQVP5yQo | 10 | 84% | 12 | -0.79 | -0.63 / 0.04 / 0.12 |
| JXMXLy82_Ng | 13 | 100% | 27 | -0.95 | -0.18 / 0.65 / 0.95 |
| L3ZzViOphWc | 12 | 82% | 44 | -0.63 | -0.65 / -0.37 / 0.06 |
| Op-AV2OVt6Q | 5 | 91% | 23 | -0.72 | -0.68 / -0.4 / 0.09 |
| QAcBgVZheDo | 1 | 100% | 22 | -0.68 | -0.25 / -0.25 / -0.25 |
| QblBVxDSv0I | 15 | 99% | 30 | -0.71 | 0.02 / 0.18 / 0.44 |
| RKH7U9fT98c | 10 | 88% | 15 | -0.71 | -0.16 / 0.11 / 0.15 |
| UUYZwAquhe8 | 15 | 97% | 15 | -0.65 | -0.6 / -0.09 / 0.37 |
| Wtrvw88_-kk | 15 | 96% | 17 | -0.8 | -0.43 / -0.04 / 0.28 |
| Wy_oniVmLYI | 0 | 86% | 40 |  |  |
| Zd_rWYHScAo | 4 | 96% | 13 | -0.78 | -0.3 / -0.09 / 0.03 |
| aSFlQU3-F1o | 15 | 99% | 20 | -0.86 | -0.12 / 0.36 / 0.64 |
| ab3CVOj6V8Q | 1 | 100% | 39 | -0.45 | 0.43 / 0.43 / 0.43 |
| b6nD-NdKhPU | 5 | 82% | 23 | -0.72 | -0.65 / 0.24 / 0.41 |
| bGKXJZcwSEc | 15 | 95% | 9 | -0.69 | -0.65 / -0.2 / 0.03 |
| brYjAfTazt8 | 0 | 99% | 20 |  |  |
| dBrNLTahdaY | 15 | 99% | 33 | -0.72 | -0.21 / 0.08 / 0.52 |
| dY3sTyUxTCk | 11 | 97% | 11 | -0.6 | -0.27 / -0.11 / 0.48 |
| eKpsVdBi7Ww | 7 | 87% | 24 | -0.77 | -0.52 / -0.05 / 0.14 |
| gwZt6tExL0E | 10 | 95% | 29 | -0.73 | -0.78 / -0.3 / 0.03 |
| iIw-6hWgAmQ | 5 | 90% | 49 | -0.62 | -0.31 / -0.23 / 0.4 |
| iWCnmhCXLSE | 0 | 100% | 68 |  |  |
| j3s-3XW2sck | 5 | 90% | 10 | -0.62 | -0.67 / -0.61 / -0.2 |
| j7TGZzsocgg | 6 | 96% | 24 | -0.58 | -0.39 / -0.15 / 0.09 |
| jmGqii5G3E0 | 15 | 93% | 10 | -0.79 | -0.47 / -0.11 / 0.22 |
| kddPZBiGsLM | 15 | 98% | 37 | -0.63 | -0.65 / -0.17 / 0.31 |
| lBjDpj4qcJE | 2 | 84% | 2 | -0.82 | 0.18 / 0.26 / 0.35 |
| ly6FDnEompU | 0 | 88% | 69 |  |  |
| n-2cN7V4amY | 11 | 100% | 58 | -0.72 | -0.36 / -0.06 / 0.07 |
| rarWfNSPDHw | 12 | 93% | 15 | -0.45 | -0.45 / 0.01 / 0.31 |
| sqwfUGFzlr8 | 6 | 83% | 24 | -0.72 | -0.14 / 0.05 / 0.1 |
| t6lmLmDL51E | 15 | 81% | 12 | -0.85 | -0.65 / -0.02 / 0.31 |
| w4xG2fkHfJA | 15 | 94% | 39 | -0.76 | -0.67 / -0.44 / 0.1 |
| y0fyVtkT0Os | 5 | 96% | 38 | -0.71 | -0.73 / -0.64 / 0.15 |
| zZ2zmsPIMXI | 9 | 84% | 28 | -0.63 | 0.03 / 0.4 / 0.56 |

## Vocabulary proposals

- feature: angle.wrist_cock (racket-hand wrist angle) (Wrist flicking and over-supinating are the most-cited faults but no registered feature shows the wrist angle.)
- feature: racket face angle / racket tip position (Face too open, face control lost and racket tip whipping through cannot be seen from body landmarks.)
- measurement: grip type (Continental vs Eastern) (Wrong grip is a top fault but is not visible in the registered features.)
- feature: contact point distance in front of the body (Contact too far forward needs a feature relating wrist position to the hips at contact.)
- trackable: racket (Racket path and angle needed to judge undercutting and face control.)
- trackable: ball (Needed to observe contact point and ball landing for the outcome.)
