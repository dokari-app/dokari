# Factory report: tennis_overhead_smash

Clips found: 50 (usable for attempts: 33). Attempts: 196.
Confidence tier: **low**. Checks: 9 pass, 0 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [PASS] 4. recognition: recall 0.98 (leave-one-clip-out), false accepts 0.05 (shape alone 0.81), by view {'front/back (<30)': 0.9896907216494846, 'oblique (30-60)': 0.9659090909090909, 'side (>60)': 1.0}
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [n/a ] 6. discrimination: no objective has enough labelled good and faulty examples (3 of each), so no target range is validated; 7 of 7 come from good-form demonstrations, 0 from everyday footage (what is typical, not what is good)
- [PASS] 7. outcome links: 4 links, 4 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.69 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 4 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **non_hitting_arm_down_or_unused** (medium, agreed by 4 of 5 runs): Raise the non-hitting arm up toward the ball to track it and balance the swing, rather than letting it hang or stay bent against the body.. Target: angle.shoulder.non between 15.2009 and 156.9191 at L1. Wrong if below: Non-hitting arm stays low by the side or collapses against the body, so the ball is tracked poorly and the body is less balanced. (medium); above: Non-hitting arm flung very high or wide, pulling the shoulders off line. (low). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 2. **facing_net_not_sideways** (medium, agreed by 5 of 5 runs): Turn the shoulders and hips sideways to the net while preparing, coiling the trunk, so the swing can uncoil into the ball.. Target: angle.shoulder_hip_twist between -22.0992 and 21.242 at L1. Wrong if below: Chest and shoulders stay open to the net with little coil, giving an arm-only swing with less power and control. (medium); above: Over-rotated, shoulders twisted far beyond the hips. (low). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 3. **wrong_contact_point** (medium, agreed by 5 of 5 runs): Meet the ball at full reach above and slightly in front of the hitting shoulder.. Target: height.wrist.dom between -0.4076 and 1.366 at L1. Wrong if below: Contact is low, with the ball dropping on the player or hit before the arm is fully up. (medium); above: Wrist is extended as high as possible with the body stretching; this is mostly a good sign. (low). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 4. **contact_position_fore_aft** (medium, agreed by 3 of 5 runs): Position the body so the ball is met in front of the body, neither behind the head nor too far ahead.. Target: fwd.trunk_shift between -0.3128 and 0.6327 at L1. Wrong if below: Body leaning back under the ball, contact behind the head, so the ball tends to fly long. (medium); above: Body lunging forward, contact too far in front, so the ball tends to go into the net. (medium). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 5. **arming_without_extension** (medium, agreed by 4 of 5 runs): Extend the hitting arm up fully to the ball at contact, instead of an arm-only swing with a bent elbow.. Target: angle.elbow.dom at least 98.6191 at L1. Wrong if below: Bent elbow at contact, with a short, arm-only push and lost height and power. (medium). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 6. **dropping_head_and_chest** (medium, agreed by 5 of 5 runs): Keep the trunk tall and stable through contact, with the head up on the ball, instead of letting the chest drop early.. Target: angle.trunk_lean between 0.4119 and 21.6426 at L1. Wrong if above: Head and chest fall forward before the racket meets the ball, to see the result. (medium); below: Trunk leaning back and falling away from the ball. (medium). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.
- 7. **loss_of_balance** (medium, agreed by 4 of 5 runs): Finish the smash balanced over the feet, without drifting sideways, and ready to recover.. Target: lat.com_shift between -1.233 and 1.0295 at L2. Wrong if below: Body falls away to one side after contact. (medium); above: Body falls away to the other side after contact. (medium). Range from good-form demonstrations (103 attempts in 22 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **facing_net_not_sideways** (form; 5 of 12, strong): measured by the camera (facing_net_not_sideways).
- **non_hitting_arm_down_or_unused** (form; 5 of 12, strong): measured by the camera (non_hitting_arm_down_or_unused).
- **slow_footwork_or_backpedaling** (form; 5 of 12, strong): would need a new body feature: timing of foot movement / foot displacement over time (ankle travel and direction relative to the body); not a static pose feature.
- **wrong_contact_point** (form; 4 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (wrong_contact_point). Coaches disagree: Sources 6 and 11 say contact behind the body sends the ball long. Source 0 warns that contact too far in front sends it into the net.
- **smashing_too_hard_or_wrong_moment** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball tracking and court position/racket speed to judge power and shot selection. Coaches disagree: Source 4 says hit about half speed. Source 7 says go full on and aim for a winner, except when deep.
- **wrong_grip_or_no_spin** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks for grip and racket/ball detection for spin.
- **dropping_head_and_chest** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (dropping_head_and_chest).
- **loss_of_balance** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (loss_of_balance).
- **misjudging_ball_for_overhead** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection (height, bounce, trajectory).
- **netting_when_deep_or_moving_back** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball and racket detection plus court position to see aim and net clearance.
- **planting_feet_too_early** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball tracking to know when the ball is in position relative to foot planting.
- **pointing_without_turning** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (facing_net_not_sideways). Coaches disagree: Sources 0, 3, 5 and 7 teach pointing at the ball with the non-hitting arm. Source 8 calls pointing an older beginner approach, and source 9 says pointing alone fails without the turn.
- **poor_placement_choice** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball tracking and court position to see placement.
- **arming_without_extension** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (arming_without_extension).
- **decelerating_the_hand** (form; 1 of 12, single): would need a new body feature: dominant wrist speed/acceleration through contact over frames (velocity of wrist).
- **disguising_overhead_too_early** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball and racket direction/shot placement detection to see faked direction.
- **going_up_into_trophy_position** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): angle.shoulder.dom, height.wrist.dom, and elbow angle show racket-arm raise in the prep phase, but no objective tests it. Coaches disagree: Source 7 starts the swing from the trophy position.
- **not_recovering_after_smash** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (loss_of_balance).
- **oversized_swing_or_overusing_body** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): angle.shoulder.dom, angle.elbow.dom and reach.wrist.dom show swing size, but no objective tests it.
- **standing_straight_up_at_contact** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (dropping_head_and_chest).

Tested in this entry but named by no coach: contact_position_fore_aft.

Good form, as coaches give it:

- Turn sideways early, with shoulders and hips (unit turn or quarterback-style turn), as soon as the ball goes up. (7 of 12)
- Keep the non-hitting arm up, pointing at or tracking the ball, for balance and positioning. (6 of 12)
- Shuffle, crossover or scissor-kick back instead of backpedaling. (5 of 12)
- Aim deep toward the baseline, especially when moving back or hitting from deep. (5 of 12)
- Get the racket up quickly and use an abbreviated, serve-like swing, not a full swing. (4 of 12)
- Make contact high and out in front of the shoulder so the ball goes down. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **coil_sideways_then_uncoil** (biomechanics, 3 of 3 runs; explains facing_net_not_sideways, arming_without_extension, standing_straight_up_at_contact): Turning the shoulders and hips sideways to the net stores rotation in the trunk. The swing then unwinds from the body up through the arm into the ball, so the arm isn't swinging on its own. Cue handle: Coil to store power, then unwind it into the ball..
- **reach_tall_to_contact** (contested, 3 of 3 runs; explains wrong_contact_point, contact_position_fore_aft, arming_without_extension): Meeting the ball at full reach lets the racket arm work as one long lever, and the ball leaves from the highest point with the most room to clear the net. A bent arm shortens the lever, and a ball behind or too far in front changes the ball's angle off the strings. Cue handle: Meet the ball at the very top of your reach, a touch in front.. Competing views: Sources 6 and 11: contact behind the body sends the ball long.; Source 0: contact too far in front sends the ball into the net..
- **free_arm_tracks_and_balances** (contested, 3 of 3 runs; explains non_hitting_arm_down_or_unused, dropping_head_and_chest, loss_of_balance): Lifting the non-hitting arm toward the ball helps the eyes and body track its flight and offsets the racket arm's motion, which keeps the body steady. Coaches differ on whether pointing alone is enough, because the turn is what gives it value. Cue handle: Use the free side to track the ball and keep the body steady.. Competing views: Sources 0, 3, 5 and 7: point at the ball with the non-hitting arm.; Source 8: pointing is an older beginner approach.; Source 9: pointing alone fails without the turn..
- **stay_tall_and_balanced_over_base** (coaching_consensus, 2 of 3 runs; explains dropping_head_and_chest, loss_of_balance): A stable trunk with the head up keeps the centre of mass over a base of support through contact. The body then holds a steady platform for the swing, and the player can finish balanced and recover. Cue handle: Stay tall and steady until the ball has gone..

## Check against labelled mistake videos (15 videos, 102 attempts, 28 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| oversized_swing_or_overusing_body | 4 / 2 | 0 / 0 |
| going_up_into_trophy_position | 3 / 3 | 0 / 0 |
| facing_net_not_sideways | 2 / 2 | 4 / 2 |
| non_hitting_arm_down_or_unused | 2 / 2 | 41 / 9 |
| standing_straight_up_at_contact | 2 / 2 | 0 / 0 |
| dropping_head_and_chest | 0 / 0 | 10 / 4 |
| not_recovering_after_smash | 0 / 0 | 1 / 1 |
| pointing_without_turning | 0 / 0 | 1 / 1 |
| smashing_too_hard_or_wrong_moment | 0 / 0 | 11 / 1 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| non_hitting_arm_down_or_unused | 41 / 2 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| facing_net_not_sideways | 4 / 2 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| wrong_contact_point | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| contact_position_fore_aft | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| arming_without_extension | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| dropping_head_and_chest | 0 / 2 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| loss_of_balance | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.wrist.dom, angle.shoulder.dom, angle.shoulder.non, dist.wrist_width, height.wrist_mid
Attempts found as: height.wrist.dom rises (to at least 0.8). Typical size of the last event 1.822, lasting 3.22 s; smaller ones (below 0.729) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 133 clear attempts in 30 of 34 clips after 2 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 13 | 81 | mixed 81 |
| coach_demo | 12 | 60 | good_form 59, mixed 1 |
| pro_footage | 17 | 50 | good_form 50 |
| practice_session | 2 | 16 | mixed 15, unknown 1 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| non_hitting_arm_down_or_unused | 8% (22 clips) | 8% (11 clips) | no difference: everyone is inside, or this measure does not separate them |
| facing_net_not_sideways | 9% (22 clips) | 7% (11 clips) | no difference: everyone is inside, or this measure does not separate them |
| wrong_contact_point | 6% (22 clips) | 15% (11 clips) | everyday footage departs more: the objective picks up a difference from good form |
| contact_position_fore_aft | 7% (22 clips) | 3% (11 clips) | no difference: everyone is inside, or this measure does not separate them |
| arming_without_extension | 3% (22 clips) | 8% (11 clips) | no difference: everyone is inside, or this measure does not separate them |
| dropping_head_and_chest | 4% (22 clips) | 2% (11 clips) | no difference: everyone is inside, or this measure does not separate them |
| loss_of_balance | 7% (22 clips) | 5% (11 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- prepare_and_swing_to_contact: L0 to L1
- follow_through_and_recovery: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip TXSlHCVfXj0: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 197 of 203 attempts (tolerance 2.133). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (0_Xa6KG4qbE, ASPvxu5R0Bs, En56zLkbIPs, G67va1Qj4Nw, K_EexG6l7E8, NzoLPWvWcbs, S7k_-CJDq9I, T2S6v1jEJeE, TXSlHCVfXj0, TwtUPDMY468, U0TEJqnCoX4, WOjPM9GZsCs, YhcYQXrguLc, feCB0-CYqrI, m8NpygZi44Q, r9bcy937WoY, ssDipBYDZFo, w9ZIs2dgiJk).

| clip | attempts found | kept | note |
|---|---|---|---|
| 0_Xa6KG4qbE | 2 | 2 | seed |
| ASPvxu5R0Bs | 4 | 4 | seed |
| BaATu8_FCRY | 8 | 8 |  |
| En56zLkbIPs | 2 | 2 | seed |
| Ev3L_V1bQv8 | 8 | 7 |  |
| G67va1Qj4Nw | 2 | 2 | seed |
| I-peo1nbxhQ | 3 | 3 |  |
| IYitGxUK8MM | 4 | 3 |  |
| K_EexG6l7E8 | 2 | 2 | seed |
| LV9Yp4fpWa8 | 2 | 2 |  |
| MCjWyI2M_Ew | 15 | 15 |  |
| NOMh7eK5HY4 | 4 | 4 |  |
| NzoLPWvWcbs | 13 | 13 | seed |
| S7k_-CJDq9I | 6 | 6 | seed |
| T2S6v1jEJeE | 7 | 7 | seed |
| TXSlHCVfXj0 | 15 | 15 | seed |
| TwtUPDMY468 | 8 | 8 | seed |
| U0TEJqnCoX4 | 2 | 2 | seed |
| VWBkh_SMyf8 | 4 | 4 |  |
| WOjPM9GZsCs | 9 | 9 | seed |
| YhcYQXrguLc | 6 | 6 | seed |
| ebjjbl_yafg | 3 | 1 |  |
| feCB0-CYqrI | 13 | 13 | seed |
| m8NpygZi44Q | 5 | 5 | seed |
| qENjaMTnCmc | 7 | 7 |  |
| r9bcy937WoY | 3 | 3 | seed |
| ssDipBYDZFo | 6 | 5 | seed |
| swwe2Un2zfM | 5 | 4 |  |
| um4KDC3P6IQ | 2 | 2 |  |
| vlemE5TZJng | 12 | 12 |  |
| w9ZIs2dgiJk | 5 | 5 | seed |
| wD3kwZwpHSQ | 2 | 2 |  |
| xFCwXFHKmhI | 2 | 2 |  |
| xfi2hg11eS0 | 12 | 12 |  |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist.dom=-0.522, angle.shoulder.dom=37.214, height.wrist_mid=-0.531, angle.shoulder.non=36.678, height.wrist.non=-0.538, dist.wrist_width=1.15, angle.elbow.dom=122.511, angle.trunk_lean=8.311, reach.wrist.dom=0.823, lat.com_shift=0.024
- L1 (t=0.469): height.wrist.dom=0.707, angle.shoulder.dom=132.21, height.wrist_mid=0.339, angle.shoulder.non=79.538, height.wrist.non=0.036, dist.wrist_width=2.197, angle.elbow.dom=149.709, angle.trunk_lean=9.844, reach.wrist.dom=0.895, lat.com_shift=0.178
- L2 (t=1.0): height.wrist.dom=-0.535, angle.shoulder.dom=43.968, height.wrist_mid=-0.444, angle.shoulder.non=42.191, height.wrist.non=-0.442, dist.wrist_width=1.594, angle.elbow.dom=135.658, angle.trunk_lean=10.779, reach.wrist.dom=0.83, lat.com_shift=-0.091

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| 0_Xa6KG4qbE | 2 | 98% | 24 | 0.07 | 0.63 / 0.69 / 0.74 |
| 6bdl1zs2Owk | 1 | 90% | 45 | -0.46 | 0.89 / 0.89 / 0.89 |
| 6kgcJY-AGXg | 1 | 98% | 31 | -0.46 | -0.02 / -0.02 / -0.02 |
| 6lQguSBY1GY | 0 | 99% | 12 |  |  |
| ASPvxu5R0Bs | 4 | 91% | 14 | -0.33 | 0.6 / 0.85 / 0.87 |
| BaATu8_FCRY | 8 | 91% | 55 | -0.47 | -0.44 / 0.64 / 0.9 |
| En56zLkbIPs | 2 | 96% | 14 | -0.73 | -0.46 / 0.1 / 0.67 |
| Ev3L_V1bQv8 | 7 | 93% | 7 | -0.13 | -0.1 / 0.29 / 0.75 |
| G67va1Qj4Nw | 2 | 97% | 28 | -0.52 | 0.25 / 0.26 / 0.27 |
| I-peo1nbxhQ | 3 | 91% | 38 | 0.81 | 0.81 / 0.91 / 0.93 |
| IYitGxUK8MM | 3 | 95% | 7 | -0.77 | -0.44 / -0.17 / 0.2 |
| K_EexG6l7E8 | 2 | 97% | 5 | -0.61 | -0.1 / 0.37 / 0.84 |
| KcSdmb98pJI | 1 | 71% | 36 | -0.85 | 0.59 / 0.59 / 0.59 |
| Kps89b_fa5Y | 1 | 99% | 54 | -0.87 | -0.86 / -0.86 / -0.86 |
| LCKk0N4p2_A | 0 | 98% | 8 |  |  |
| LV9Yp4fpWa8 | 2 | 99% | 30 | -0.25 | -0.18 / 0.08 / 0.34 |
| MCjWyI2M_Ew | 15 | 99% | 39 | -0.15 | -0.07 / 0.74 / 0.9 |
| Mlx0eGTbD2U | 1 | 87% | 7 | -0.67 | 0.84 / 0.84 / 0.84 |
| NOMh7eK5HY4 | 4 | 92% | 17 | -0.42 | -0.15 / -0.01 / 0.57 |
| NzoLPWvWcbs | 13 | 96% | 46 | -0.58 | -0.08 / 0.39 / 0.88 |
| S7k_-CJDq9I | 6 | 99% | 34 | -0.4 | -0.01 / 0.39 / 0.8 |
| T2S6v1jEJeE | 7 | 81% | 45 | -0.66 | 0.65 / 0.99 / 1.07 |
| TXSlHCVfXj0 | 15 | 98% | 29 | -0.78 | -0.49 / 0.75 / 0.88 |
| TwtUPDMY468 | 8 | 98% | 47 | -0.39 | 0.16 / 0.64 / 0.82 |
| U0TEJqnCoX4 | 2 | 98% | 41 | -0.74 | 0.28 / 0.35 / 0.41 |
| UlU4UCuFgms | 1 | 94% | 29 | -0.58 | 0.44 / 0.44 / 0.44 |
| VQRyu0qGY_k | 1 | 92% | 66 | -0.66 | -0.57 / -0.57 / -0.57 |
| VWBkh_SMyf8 | 4 | 93% | 12 | -0.7 | 0.29 / 0.73 / 0.82 |
| WOjPM9GZsCs | 9 | 91% | 12 | -0.15 | 0.05 / 0.75 / 0.84 |
| YhcYQXrguLc | 6 | 95% | 46 | -0.61 | 0.24 / 0.65 / 0.96 |
| YlxUtWxFif8 | 0 | 100% | 14 |  |  |
| aPw7WmZApKU | 0 | 72% | 23 |  |  |
| beAkcxGGKsA | 1 | 82% | 6 | -0.67 | 0.95 / 0.95 / 0.95 |
| ebjjbl_yafg | 1 | 98% | 47 | 0.02 | 0.23 / 0.23 / 0.23 |
| feCB0-CYqrI | 13 | 99% | 41 | -0.54 | -0.35 / 0.66 / 0.79 |
| m8NpygZi44Q | 5 | 92% | 8 | -0.83 | 0.02 / 0.26 / 0.95 |
| mMOK8MPTXAQ | 0 | 96% | 56 |  |  |
| o05HRLcPigQ | 1 | 96% | 11 | -0.87 | -0.56 / -0.56 / -0.56 |
| qENjaMTnCmc | 7 | 99% | 79 | 0.41 | 0.69 / 0.85 / 0.87 |
| r9bcy937WoY | 3 | 100% | 34 | 0.3 | 0.22 / 0.68 / 0.81 |
| sExiSpKimNQ | 1 | 98% | 55 | 0.27 | 0.7 / 0.7 / 0.7 |
| ssDipBYDZFo | 5 | 98% | 8 | -0.79 | -0.25 / -0.19 / 0.71 |
| swwe2Un2zfM | 4 | 93% | 67 | -0.61 | -0.39 / 0.13 / 0.44 |
| um4KDC3P6IQ | 2 | 99% | 16 | 0.13 | 0.79 / 0.87 / 0.95 |
| vlemE5TZJng | 12 | 95% | 27 | -0.71 | 0.71 / 0.8 / 0.87 |
| w9ZIs2dgiJk | 5 | 80% | 6 | -0.63 | -0.03 / 0.79 / 0.82 |
| wD3kwZwpHSQ | 2 | 90% | 56 | -0.17 | -0.66 / -0.36 / -0.05 |
| xFCwXFHKmhI | 2 | 95% | 33 | -0.07 | -0.08 / 0.39 / 0.86 |
| xfi2hg11eS0 | 12 | 89% | 10 | -0.52 | -0.53 / 0.68 / 0.92 |
| yf_bT-CjCcQ | 0 | 96% | 47 |  |  |

## Vocabulary proposals

- trackable: ball (Contact point, the ball's flight and the landing zone, and judging whether the ball is a true overhead, all need ball tracking.)
- trackable: racket_head (Contact in front or behind the head and the swing path cannot be seen from the wrists alone.)
- feature: fwd.contact_offset_from_head (Coaches disagree about contact too far behind or ahead; the horizontal offset of the wrist from the head or shoulder at contact would test it directly.)
- feature: steps_per_second / foot_travel_before_contact (Slow footwork, backpedaling and planting the feet too early can't be tested with posture features.)
- feature: angle.head_tilt (Dropping the head to see the result cannot be separated from trunk lean with the current features.)
- feature: grip_type (Using a frying-pan or forehand grip is a named fault, and wrist and hand orientation are not registered.)
