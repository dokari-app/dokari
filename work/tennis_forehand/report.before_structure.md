# Factory report: tennis_forehand

Clips found: 231 (usable for attempts: 216). Attempts: 2511.
Confidence tier: **low**. Checks: 8 pass, 2 fail, 0 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.17 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [FAIL] 6. discrimination: 0/4 objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75); do not: ['rotation_late_or_blocked', 'short_or_stopped_follow_through', 'non_hitting_hand_misuse']; too few wrong examples in different videos to test: ['poor_spacing_to_ball']; 2 without enough labels
- [PASS] 7. outcome links: 3 links, 3 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.62 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 4 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **rotation_late_or_blocked** (medium, agreed by 5 of 5 runs): Rotate the hips and shoulders through the shot so the shoulder line has turned fully toward the target by the finish.. Target: angle.shoulder_hip_twist between -24.0181 and 26.3318 at L1. Wrong if below: The trunk is blocked or turns late and the swing comes from the arm alone, so the shoulders are still behind at the finish. (medium); above: The shoulders over-rotate relative to the hips and the body spins off balance. (low). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.
- 2. **poor_spacing_to_ball** (medium, agreed by 5 of 5 runs): Stand at a distance from the ball that lets the hitting arm extend comfortably out and up through contact.. Target: reach.wrist.dom between 0.5491 and 1.0146 at L1. Wrong if below: The player is crowded or jammed by the ball, and the arm stays folded close to the body. (medium); above: The player overreaches and the arm is stretched far from the body. (medium). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.
- 3. **arm_pulling_in_on_acceleration** (medium, agreed by 4 of 5 runs): Let the hitting arm travel up and out away from the body through the swing, not bend and pull in toward the body.. Target: angle.elbow.dom between 78.9943 and 157.6997 at L1. Wrong if below: The elbow collapses and the arm folds in toward the body instead of extending out and up. (medium); above: The arm is locked straight and stiff at the finish. (low). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.
- 4. **short_or_stopped_follow_through** (medium, agreed by 4 of 5 runs): Swing all the way through contact and finish with the hitting arm lifted and extended up and across, with the wrist near shoulder height.. Target: height.wrist.dom between -0.7743 and 0.3723 at L1. Wrong if below: The swing stops early or finishes low, with the racket arm cut off at the waist or chest. (medium); above: The racket finishes very high over the shoulder or head. This is a style difference and a smaller error. (low). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.
- 5. **non_hitting_hand_misuse** (medium, agreed by 4 of 5 runs): Use the non-hitting arm for balance. Extend it forward in the preparation, then fold it in toward the chest in the finish, instead of letting it dangle or split away.. Target: angle.shoulder.non between 0.6781 and 98.7687 at L1. Wrong if below: The arm hugs the body or dangles at the side with no counterbalance. (medium); above: The arm flies out to the side early, which pulls the shoulders open and unbalances the body. (medium). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.
- 6. **ball_behind_body_when_pushed_back** (medium, agreed by 3 of 5 runs): Keep the body weight moving forward or staying neutral through the shot, not falling backward, even when the ball is deep.. Target: fwd.trunk_shift between -0.3674 and 0.7179 at L1. Wrong if below: The trunk and weight lean back over the rear foot, with the ball behind the body at contact. (medium); above: The trunk lunges too far forward over the front foot. (low). Range from good-form demonstrations (364 attempts in 40 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **late_or_mistimed_preparation** (form; 4 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Timing relative to ball bounce needs ball detection (and racket tracking); pose alone cannot show ball position or bounce..
- **short_or_stopped_follow_through** (form; 4 of 12, some): measured by the camera (short_or_stopped_follow_through). Coaches disagree: Source 11 finishes over the shoulder. Source 8 finishes across the body, and source 1 says follow-throughs vary on tour.
- **arm_only_takeback** (safety; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (rotation_late_or_blocked).
- **arm_style_in_unit_turn** (form; 3 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.elbow.dom shows arm straightness in the unit turn, but no objective tests it because the right value depends on player style.. Coaches disagree: Sources 0 and 1 want a bent or in-line elbow in the unit turn. Source 8 says bent or straight doesn't matter, so don't force a straight arm.
- **contact_face_angle_wrong** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Racket detection (racket face orientation) and hand/forearm landmarks needed.. Coaches disagree: Source 4 says tilt the face forward, and source 9 says beginners should use an open angle.
- **non_hitting_hand_misuse** (safety; 3 of 12, some): measured by the camera (non_hitting_hand_misuse).
- **poor_spacing_to_ball** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (poor_spacing_to_ball). Coaches disagree: Source 9 says stay open and don't step into every ball. Sources 7 and 10 say step in for neutral stance and step into the ball.
- **rotation_late_or_blocked** (form; 3 of 12, some): measured by the camera (rotation_late_or_blocked).
- **take_back_too_big** (form; 3 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.shoulder.dom, reach.wrist.dom or height.wrist.dom in the backswing show take-back size, but no objective tests it.. Coaches disagree: Source 11 says to take the racquet all the way back behind you while staying compact. Sources 2 and 3 push a smaller take-back.
- **takeback_arm_path** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Racket path/loop and racket drop need racket detection; wrist trajectory from pose is only coarse.. Coaches disagree: Source 9 says don't loop the arm. Sources 5 and 6 recommend a loop or circle path for the racket.
- **arm_pulling_in_on_acceleration** (form; 2 of 12, some): measured by the camera (arm_pulling_in_on_acceleration).
- **arm_started_swing_no_leg_drive** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.knee.dom and height.hip show leg drive, and sequencing from the time series, but no objective tests it.. Coaches disagree: Source 9 disagrees: legs are complementary and the arm leads.
- **ball_behind_body_when_pushed_back** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (ball_behind_body_when_pushed_back). Coaches disagree: Source 3 says weight should go forward or stay neutral. Source 5 says keep the body behind the ball and hit off the back foot.
- **poor_shot_choice_and_target** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **racket_face_not_closed_backswing** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Racket detection for face orientation in the backswing, plus hand landmarks for wrist/forearm position..
- **tension_in_grip_and_contact** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **wrist_flexed_arm_cramped_at_contact** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (arm_pulling_in_on_acceleration).
- **conscious_wrist_action** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Wrist flick and lag need hand landmarks and racket tracking; the body skeleton wrist point is too coarse.. Coaches disagree: Source 1 wants an active windshield-wiper wrist, and source 0 wants a flip. Source 8 wants the wrist passive at contact.
- **over_relying_on_legs** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): angle.knee.dom and height.hip show leg drive, and angle.elbow.dom/height.wrist.dom show arm activity, but no objective tests it.. Coaches disagree: Sources 0, 1 and 3 teach leg drive first as the power source.
- **wrong_grip** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: Hand landmarks (and racket detection) needed to see grip rotation and size..

Good form, as coaches give it:

- Accelerate as a kinetic chain from the ground up: legs, hips, trunk, then arm. (5 of 12)
- Stay balanced with weight moving forward or neutral, and keep enough space from the ball. (5 of 12)
- Take the racket back by turning the whole body, with the racket going along. (4 of 12)
- Start the take-back early, as soon as you read the ball, without waiting for the bounce. (4 of 12)
- Use the non-hitting hand to help the racket back, stay coiled, and catch the racket at the finish. (4 of 12)
- Make contact out in front of the body with the arm in front and the wrist extended. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **turn_the_body_to_drive_the_arm** (contested, 3 of 3 runs; explains rotation_late_or_blocked, arm_only_takeback, arm_started_swing_no_leg_drive, over_relying_on_legs): Power builds from the ground and trunk and passes out to the arm and racket. When the hips and shoulders turn early and keep turning through the shot, the arm is carried along by that turn instead of generating the swing alone. Cue handle: Let the turn of the body whip the racket through the ball, so the swing feels pulled rather than pushed.. Competing views: Sources 0, 1 and 3 teach leg drive and rotation first as the main power source.; Source 9 says the legs are complementary and the arm leads the swing..
- **room_to_extend_through_contact** (contested, 3 of 3 runs; explains poor_spacing_to_ball, arm_pulling_in_on_acceleration, wrist_flexed_arm_cramped_at_contact, contact_face_angle_wrong): Contact is strongest when the arm has room to travel up and out away from the body. Good spacing and an arm that keeps extending stop it from bending and pulling in. That keeps the racket moving along the line of the shot for longer. Cue handle: Create space so the racket keeps travelling out and up through the ball.. Competing views: Sources 7 and 10 say step in toward a neutral stance and step into the ball to set the distance.; Source 9 says stay open and don't step into every ball..
- **finish_what_the_swing_started** (contested, 3 of 3 runs; explains short_or_stopped_follow_through, take_back_too_big, late_or_mistimed_preparation): A swing that keeps accelerating to a full finish keeps the racket speed through the ball instead of slowing before contact. The finish also shows whether the body kept turning. Its exact shape varies between players. Cue handle: Keep the racket speeding up all the way through the ball and out into the finish.. Competing views: Source 11 finishes over the shoulder.; Source 8 finishes across the body.; Source 1 says follow-throughs vary on tour..
- **free_arm_steadies_the_turn** (coaching_consensus, 2 of 3 runs; explains non_hitting_hand_misuse, rotation_late_or_blocked): The non-hitting arm acts as a counterweight. Reaching it forward in the preparation and folding it in at the finish helps keep the body balanced and the turn controlled. It also helps the body rotate as one unit. Cue handle: Use the free side to steady the turn and keep the body balanced from start to finish..

## Check against labelled mistake videos (173 videos, 2328 attempts, 1262 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| non_hitting_hand_misuse | 27 / 10 | 33 / 15 |
| short_or_stopped_follow_through | 16 / 11 | 69 / 38 |
| poor_spacing_to_ball | 15 / 4 | 3 / 2 |
| takeback_arm_path | 15 / 7 | 3 / 3 |
| arm_only_takeback | 13 / 3 | 238 / 66 |
| late_or_mistimed_preparation | 12 / 8 | 39 / 13 |
| arm_started_swing_no_leg_drive | 9 / 3 | 4 / 2 |
| take_back_too_big | 7 / 3 | 26 / 7 |
| rotation_late_or_blocked | 5 / 4 | 5 / 2 |
| conscious_wrist_action | 4 / 3 | 1 / 1 |
| ball_behind_body_when_pushed_back | 3 / 1 | 0 / 0 |
| arm_style_in_unit_turn | 2 / 2 | 2 / 2 |
| over_relying_on_legs | 1 / 1 | 1 / 1 |
| poor_shot_choice_and_target | 1 / 1 | 0 / 0 |
| racket_face_not_closed_backswing | 1 / 1 | 2 / 2 |
| wrist_flexed_arm_cramped_at_contact | 1 / 1 | 0 / 0 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| rotation_late_or_blocked | 5 / 4 | 2 / 3 | 0.65 | 50% | does not tell right from wrong well enough; range kept from good form demonstrations |
| poor_spacing_to_ball | 3 / 15 | 2 / 4 | 0.93 |  | separates on these attempts but the wrong ones come from too few videos to test on others; range kept from good form demonstrations |
| arm_pulling_in_on_acceleration | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| short_or_stopped_follow_through | 66 / 16 | 37 / 11 | 0.58 | 65% | does not tell right from wrong well enough; range kept from good form demonstrations |
| non_hitting_hand_misuse | 33 / 27 | 15 / 10 | 0.47 | 43% | does not tell right from wrong well enough; range kept from good form demonstrations |
| ball_behind_body_when_pushed_back | 0 / 3 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.wrist.dom, angle.shoulder.dom, reach.wrist.dom, angle.shoulder_hip_twist, height.wrist_mid
Attempts found as: height.wrist.dom rises (to at least -0.3). Typical size of the last event 1.326, lasting 2.18 s; smaller ones (below 0.53) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 6521 clear attempts in 223 of 230 clips after 0 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 137 | 1690 | mistakes 59, mixed 1631 |
| coach_demo | 51 | 541 | good_form 200, mixed 341 |
| pro_footage | 22 | 168 | good_form 168 |
| practice_session | 9 | 105 | good_form 31, mixed 23, unknown 51 |
| instruction_talk | 2 | 12 | good_form 4, mixed 8 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| rotation_late_or_blocked | 9% (40 clips) | 7% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| poor_spacing_to_ball | 8% (40 clips) | 4% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| arm_pulling_in_on_acceleration | 5% (40 clips) | 3% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| short_or_stopped_follow_through | 8% (40 clips) | 5% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| non_hitting_hand_misuse | 6% (40 clips) | 3% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| ball_behind_body_when_pushed_back | 8% (40 clips) | 3% (176 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- swing_to_finish: L0 to L1
- recovery: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip LCtYngOwfsw: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 2511 of 2566 attempts (tolerance 2.038). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (1meRp15WlKQ, 2J8q7sn4JLc, 2uuk8nZ8W_8, 3ja7tvQFbQQ, 4sr1wD_-r1s, 5_vJU8XJOTs, 5mtw69jSZAY, 5t_zAmaON_g, 5wdrcvQQJMg, 6_CAfr0mQ-A, 75SDa52tY1c, 7HvlDrYpWEQ, 7xdQDqILnSI, 96i30WAkwUM, 9L9narLQj9M, 9v3NfhfJD5Q, AEn2acwAQ7Y, Ap0qSdyx9H4, BPLFRhnkziY, Bm8QljKE9MM, BnmVSa9dWz0, Bun_Ouz5-bs, BwYS96dRFM0, CxLVAuZLAMs, D0IQYtGQHKE, D6C0g7zPaGk, DiXCMYwvw-8, EEHaZ4PrUFI, F-yNBm8loyk, F3qUPNxUGgo, FssCtZEWBH4, FuinI7uw8hQ, GztttGCA1pY, IWj5qhSHnL0, KAK5a9Qs12w, KAyZ1uH5plI, LCKk0N4p2_A, LCtYngOwfsw, M5mhUjZd22s, NaP7RiVXz2E, NfyrO92yMTc, OBZaRtH7OQY, OMvRlIlLa_8, OaBuo8jBgJU, PeEkclg6SKE, PkiZmPZBdw8, PsPQWDKw7Zo, Pv5kymKGQEA, Sb2Cm_KmwPU, TeYKveJ1NS4, U2dKyI_2lWQ, UaPuZ5HIU1U, UdLFwBicq8E, V26ifGuICIE, VLNuqgjf4-4, W-v8U7K0_m0, We-nHWaJ2Ig, WlQLN5mJ7Xg, XA34mJgU0ks, XeJyEfMVp5E, YpPCRn5czWM, ZBJfWvONORw, ZDPAINbsTI4, ZI-r1-3-6X4, _yJNVtqOvHw, bDl4mWTJrg0, bpUwrIMGh7A, cu_h1trboKk, dPOmMMObcn4, dQLfd9ogDQ0, dxr99mLfUXE, dzAIDEiFBv4, e_nKX3QcU04, eu0Kym_vs1E, f3yz0WZ8NOs, fDiJW1OYxac, fRjwYp_t0OE, fn7ty-cPv4U, gA4mDtJlPF0, gC26cC9N1VU, gky0Lktyt_0, hsnd8zfiROs, ht_vOk4Idcs, iXvWh-xMSd0, kB3aP3vMEeU, ljqBTn1jZbU, lpFI1yxeok8, mO6XiArAjPI, p9ggFteqtpY, pbuUnesx7Ls, pgJ2nT4_pU0, qfMVnQ07pcI, r1KRhB4QeCg, scD84O4afpk, sw2_HmjgqpI, tTkRZz3P4WM, uXF4jhDcX2A, v9Oe1avJf2o, vI4mperPhj0, vX_xBFeAIcg, v_Z-f5KHcNY, wQX8B7wYip4, x7VPW17Rew0, xwFVcyt8P_M, yPCY1PNAYqE, yYLrp-15Ao0, yZ0-We5d0jQ, zPbtp0WtHA4, zTxLiZaSDbQ, ziWEgWm4FkQ).

| clip | attempts found | kept | note |
|---|---|---|---|
| -Eu80hGbgVA | 15 | 15 |  |
| -V9fRDexnPM | 4 | 4 |  |
| -XEk39hZzzo | 15 | 15 |  |
| -pfEfb63tZ4 | 6 | 6 |  |
| 0-yol2xtr_E | 15 | 15 |  |
| 0GN5BTx-ups | 13 | 13 |  |
| 0O391AzKX6Q | 11 | 10 |  |
| 0t4qsd6LeJg | 15 | 14 |  |
| 1AY-2Cc3LJU | 15 | 15 |  |
| 1l4ZC4047is | 3 | 3 |  |
| 1meRp15WlKQ | 3 | 3 | seed |
| 2GYxGHFKD5E | 15 | 14 |  |
| 2J8q7sn4JLc | 15 | 15 | seed |
| 2pr4Xb-_B38 | 7 | 7 |  |
| 2uuk8nZ8W_8 | 8 | 8 | seed |
| 33ffZPw9y-c | 6 | 6 |  |
| 3ja7tvQFbQQ | 15 | 15 | seed |
| 4PnKAIKuypI | 15 | 14 |  |
| 4ak0XepJYA0 | 2 | 2 |  |
| 4myNhYHhJFY | 5 | 5 |  |
| 4sr1wD_-r1s | 15 | 15 | seed |
| 56Tzj_Ie7l0 | 9 | 8 |  |
| 5_vJU8XJOTs | 15 | 15 | seed |
| 5arVdubK9Pg | 2 | 2 |  |
| 5mtw69jSZAY | 15 | 15 | seed |
| 5t_zAmaON_g | 5 | 4 | seed |
| 5wdrcvQQJMg | 15 | 15 | seed |
| 6_CAfr0mQ-A | 15 | 15 | seed |
| 6pe6DfGtOAM | 15 | 10 |  |
| 75SDa52tY1c | 15 | 15 | seed |
| 784lVNd-apU | 10 | 10 |  |
| 7HvlDrYpWEQ | 15 | 15 | seed |
| 7xdQDqILnSI | 15 | 15 | seed |
| 8VAT46jqJA0 | 15 | 15 |  |
| 8r6F0MgBbz0 | 15 | 13 |  |
| 96i30WAkwUM | 9 | 9 | seed |
| 9L9narLQj9M | 15 | 15 | seed |
| 9NKtOSzeIIM | 15 | 15 |  |
| 9O_3QibgbRE | 15 | 15 |  |
| 9v3NfhfJD5Q | 15 | 15 | seed |
| A2CdXZ-Ct-c | 8 | 8 |  |
| A9e-LtL7IaI | 15 | 15 |  |
| AAIc7Li2WbA | 15 | 15 |  |
| AEn2acwAQ7Y | 2 | 2 | seed |
| AWs09rEo_v0 | 8 | 8 |  |
| Ai1wvW13HOc | 8 | 7 |  |
| Aifm8Ssxibw | 8 | 8 |  |
| Ap0qSdyx9H4 | 7 | 7 | seed |
| BPLFRhnkziY | 15 | 15 | seed |
| Bm8QljKE9MM | 2 | 2 | seed |
| BnmVSa9dWz0 | 15 | 15 | seed |
| Bun_Ouz5-bs | 15 | 15 | seed |
| BwYS96dRFM0 | 15 | 15 | seed |
| CxLVAuZLAMs | 9 | 9 | seed |
| D0IQYtGQHKE | 15 | 15 | seed |
| D6C0g7zPaGk | 15 | 15 | seed |
| DA8sM2ilEsc | 14 | 14 |  |
| DiXCMYwvw-8 | 15 | 15 | seed |
| DivLvT5R_JA | 13 | 12 |  |
| E0g3LNBhJeU | 15 | 15 |  |
| E5F6qmT2XCk | 7 | 6 |  |
| EEHaZ4PrUFI | 15 | 15 | seed |
| EZuZTjn8I08 | 15 | 14 |  |
| F-yNBm8loyk | 15 | 15 | seed |
| F3qUPNxUGgo | 15 | 15 | seed |
| FssCtZEWBH4 | 15 | 15 | seed |
| FuinI7uw8hQ | 9 | 9 | seed |
| GgvWLeest9I | 3 | 3 |  |
| GztttGCA1pY | 15 | 15 | seed |
| IWj5qhSHnL0 | 8 | 8 | seed |
| Ib7DmMuqPiE | 15 | 15 |  |
| IpoTbr5XINI | 15 | 15 |  |
| J929_RFF32E | 3 | 3 |  |
| JQXdqMXUfJM | 15 | 15 |  |
| KAK5a9Qs12w | 15 | 15 | seed |
| KAyZ1uH5plI | 15 | 15 | seed |
| K_bqRpOU6rA | 5 | 5 |  |
| KcHbjatv8yU | 15 | 13 |  |
| LCKk0N4p2_A | 11 | 10 | seed |
| LCtYngOwfsw | 15 | 15 | seed |
| LSqVp9QHERQ | 4 | 4 |  |
| Le0dgmeL-LE | 15 | 15 |  |
| M5mhUjZd22s | 3 | 3 | seed |
| NaP7RiVXz2E | 11 | 11 | seed |
| NfyrO92yMTc | 7 | 7 | seed |
| NlGP2PaZ5HA | 9 | 6 |  |
| NuepcSzH44o | 15 | 14 |  |
| O21f-6kaIwk | 15 | 15 |  |
| OBZaRtH7OQY | 15 | 15 | seed |
| OMvRlIlLa_8 | 15 | 15 | seed |
| OSkioIwXEYM | 12 | 12 |  |
| OaBuo8jBgJU | 8 | 8 | seed |
| PeEkclg6SKE | 15 | 15 | seed |
| PkiZmPZBdw8 | 8 | 8 | seed |
| PsPQWDKw7Zo | 10 | 10 | seed |
| Pv5kymKGQEA | 15 | 15 | seed |
| QQTpd0z9C1k | 15 | 13 |  |
| QrDWirGkue8 | 7 | 7 |  |
| RVnHEcORqqI | 15 | 15 |  |
| RXsu2NlL2kE | 14 | 14 |  |
| RwEF_Mty7Ps | 15 | 15 |  |
| S5N0ASybB7g | 7 | 7 |  |
| SHB7xsIPv5E | 15 | 15 |  |
| Sb2Cm_KmwPU | 15 | 15 | seed |
| T1FuyfTHsmQ | 11 | 11 |  |
| TeYKveJ1NS4 | 15 | 15 | seed |
| TgCZr6aRa1Q | 15 | 13 |  |
| U2dKyI_2lWQ | 4 | 4 | seed |
| UaPuZ5HIU1U | 15 | 15 | seed |
| UdLFwBicq8E | 9 | 9 | seed |
| UnEUw4jVrEY | 15 | 14 |  |
| V26ifGuICIE | 6 | 6 | seed |
| V9QMvLauAls | 3 | 3 |  |
| VC4_qolv6mk | 9 | 9 |  |
| VLNuqgjf4-4 | 6 | 6 | seed |
| W-v8U7K0_m0 | 15 | 15 | seed |
| We-nHWaJ2Ig | 15 | 15 | seed |
| WlQLN5mJ7Xg | 15 | 15 | seed |
| XA34mJgU0ks | 15 | 15 | seed |
| XVs_p57iNLE | 8 | 8 |  |
| X_eg2H8Fa3Q | 13 | 13 |  |
| XeJyEfMVp5E | 15 | 15 | seed |
| YGZrgFsQCjg | 15 | 14 |  |
| YpPCRn5czWM | 15 | 15 | seed |
| ZBJfWvONORw | 15 | 15 | seed |
| ZDPAINbsTI4 | 15 | 15 | seed |
| ZI-r1-3-6X4 | 14 | 14 | seed |
| _nIDNlOp7yo | 9 | 9 |  |
| _yJNVtqOvHw | 5 | 5 | seed |
| _z_60MokjvI | 4 | 4 |  |
| aMMtit2VFTc | 15 | 15 |  |
| anl7snB3TAI | 15 | 14 |  |
| bDl4mWTJrg0 | 3 | 3 | seed |
| b_kWKaTz_aQ | 15 | 15 |  |
| bpUwrIMGh7A | 15 | 15 | seed |
| cIqEpKRczJ4 | 15 | 11 |  |
| cK8Rb-clu6o | 15 | 14 |  |
| cu_h1trboKk | 7 | 7 | seed |
| dCWA2Gr98ZY | 2 | 2 |  |
| dPOmMMObcn4 | 15 | 15 | seed |
| dQLfd9ogDQ0 | 15 | 15 | seed |
| dnxe6t97xzo | 15 | 14 |  |
| dxr99mLfUXE | 14 | 14 | seed |
| dzAIDEiFBv4 | 15 | 15 | seed |
| e_nKX3QcU04 | 15 | 15 | seed |
| eu0Kym_vs1E | 14 | 14 | seed |
| f3yz0WZ8NOs | 11 | 11 | seed |
| fDiJW1OYxac | 10 | 10 | seed |
| fRjwYp_t0OE | 15 | 15 | seed |
| fn7ty-cPv4U | 13 | 13 | seed |
| g4_PTWXDY_I | 2 | 2 |  |
| gA4mDtJlPF0 | 11 | 11 | seed |
| gC26cC9N1VU | 13 | 12 | seed |
| gWTvbXyg2HM | 15 | 13 |  |
| gbXgoKc2NIc | 15 | 15 |  |
| gky0Lktyt_0 | 2 | 2 | seed |
| hdVnB1t6ZUM | 15 | 15 |  |
| hsnd8zfiROs | 4 | 4 | seed |
| ht_vOk4Idcs | 8 | 8 | seed |
| iXvWh-xMSd0 | 13 | 13 | seed |
| jBjuY3eZ8mg | 15 | 15 |  |
| jf2vpi4GG3A | 15 | 15 |  |
| kB3aP3vMEeU | 12 | 12 | seed |
| kFRYXXm8ZM0 | 15 | 14 |  |
| lQxFiUhgj8k | 15 | 15 |  |
| lhumU9wqWls | 15 | 15 |  |
| ljqBTn1jZbU | 15 | 15 | seed |
| lpFI1yxeok8 | 15 | 15 | seed |
| lqB5CjbU2-k | 15 | 15 |  |
| lrNPyAyprTk | 3 | 3 |  |
| mO6XiArAjPI | 15 | 15 | seed |
| mbx0ZebdPAQ | 15 | 12 |  |
| nh8NLQwcqZU | 15 | 15 |  |
| nn3-xPK-fzw | 15 | 15 |  |
| nuqjhrjqcd0 | 4 | 4 |  |
| nxht8qbaWu8 | 5 | 5 |  |
| o_ZZFk-pB3A | 15 | 15 |  |
| ohupLT98G4c | 15 | 15 |  |
| p9ggFteqtpY | 7 | 7 | seed |
| pZIBqmv4By8 | 15 | 15 |  |
| pbuUnesx7Ls | 15 | 15 | seed |
| pfvYK7xbSIQ | 15 | 15 |  |
| pgJ2nT4_pU0 | 15 | 14 | seed |
| q4A9i-RFTvY | 15 | 15 |  |
| qU5OxAgpE1A | 15 | 15 |  |
| qfMVnQ07pcI | 15 | 15 | seed |
| r1KRhB4QeCg | 13 | 12 | seed |
| scD84O4afpk | 15 | 15 | seed |
| sw2_HmjgqpI | 2 | 2 | seed |
| tTkRZz3P4WM | 15 | 15 | seed |
| tdnrLAzyriA | 9 | 9 |  |
| u0NvVbKVG4I | 6 | 3 |  |
| uDwKji3EC6M | 4 | 4 |  |
| uXF4jhDcX2A | 12 | 12 | seed |
| uXGwWhOj6P4 | 13 | 12 |  |
| ubFJi2M3AMM | 15 | 15 |  |
| ucEw3C6Zpc8 | 15 | 15 |  |
| ukNZF2Q9ki0 | 15 | 12 |  |
| uzPSqM3nj0A | 15 | 15 |  |
| v4oUVVlM1JA | 15 | 15 |  |
| v9Oe1avJf2o | 15 | 15 | seed |
| v9n_EbpIWNI | 3 | 3 |  |
| vI4mperPhj0 | 15 | 14 | seed |
| vX_xBFeAIcg | 15 | 15 | seed |
| v_Z-f5KHcNY | 15 | 15 | seed |
| wQX8B7wYip4 | 15 | 15 | seed |
| x7VPW17Rew0 | 2 | 2 | seed |
| xeGZAHe4BAE | 11 | 11 |  |
| xwFVcyt8P_M | 15 | 15 | seed |
| yEly5ZJw5ng | 9 | 8 |  |
| yPCY1PNAYqE | 13 | 13 | seed |
| yYLrp-15Ao0 | 13 | 13 | seed |
| yZ0-We5d0jQ | 15 | 15 | seed |
| zPbtp0WtHA4 | 9 | 9 | seed |
| zTxLiZaSDbQ | 15 | 15 | seed |
| ziWEgWm4FkQ | 15 | 15 | seed |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist.dom=-0.688, height.wrist_mid=-0.639, angle.shoulder.dom=28.789, height.wrist.non=-0.626, reach.wrist.dom=0.843, angle.shoulder.non=32.312, angle.elbow.dom=126.557, angle.trunk_lean=9.137, reach.wrist.non=0.837, angle.ankle.non=112.335
- L1 (t=0.49): height.wrist.dom=-0.201, height.wrist_mid=-0.311, angle.shoulder.dom=54.687, height.wrist.non=-0.41, reach.wrist.dom=0.781, angle.shoulder.non=41.82, angle.elbow.dom=117.966, angle.trunk_lean=7.549, reach.wrist.non=0.813, angle.ankle.non=114.218
- L2 (t=1.0): height.wrist.dom=-0.66, height.wrist_mid=-0.62, angle.shoulder.dom=30.92, height.wrist.non=-0.608, reach.wrist.dom=0.846, angle.shoulder.non=31.784, angle.elbow.dom=125.972, angle.trunk_lean=8.654, reach.wrist.non=0.838, angle.ankle.non=112.375

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -Eu80hGbgVA | 15 | 88% | 42 | -0.79 | -0.69 / -0.01 / 0.37 |
| -V9fRDexnPM | 4 | 74% | 35 | -0.73 | -0.35 / -0.32 / -0.14 |
| -XEk39hZzzo | 15 | 88% | 36 | -0.72 | -0.63 / -0.36 / 0.04 |
| -pfEfb63tZ4 | 6 | 92% | 58 | -0.53 | -0.55 / -0.47 / -0.2 |
| 0-yol2xtr_E | 15 | 97% | 39 | -0.59 | -0.61 / -0.2 / 0.24 |
| 0GN5BTx-ups | 13 | 94% | 8 | -0.85 | -0.36 / 0.21 / 0.36 |
| 0O391AzKX6Q | 10 | 79% | 57 | -0.55 | -0.44 / -0.19 / 0.01 |
| 0t4qsd6LeJg | 14 | 97% | 8 | -0.6 | -0.68 / -0.13 / 0.08 |
| 1AY-2Cc3LJU | 15 | 87% | 45 | -0.69 | -0.55 / -0.38 / -0.12 |
| 1ZVaP90Wxcg | 0 | 93% | 65 |  |  |
| 1l4ZC4047is | 3 | 91% | 3 | -0.41 | -0.24 / -0.12 / 0.25 |
| 1meRp15WlKQ | 3 | 87% | 5 | -0.74 | -0.35 / -0.31 / -0.22 |
| 2GYxGHFKD5E | 14 | 97% | 44 | -0.59 | -0.63 / -0.34 / 0.1 |
| 2J8q7sn4JLc | 15 | 83% | 45 | -0.75 | -0.42 / -0.24 / -0.06 |
| 2UlY27kxSa4 | 1 | 76% | 27 | -0.78 | -0.81 / -0.81 / -0.81 |
| 2pr4Xb-_B38 | 7 | 99% | 36 | -0.85 | -0.17 / -0.03 / 0.6 |
| 2uuk8nZ8W_8 | 8 | 98% | 6 | -0.56 | -0.34 / 0.05 / 0.34 |
| 33ffZPw9y-c | 6 | 84% | 36 | -0.61 | -0.32 / -0.16 / 0.12 |
| 3ja7tvQFbQQ | 15 | 79% | 10 | -0.62 | -0.57 / -0.07 / 0.12 |
| 4PnKAIKuypI | 14 | 95% | 11 | -0.79 | -0.35 / -0.08 / 0.17 |
| 4ak0XepJYA0 | 2 | 93% | 66 | -0.71 | 0.22 / 0.27 / 0.33 |
| 4myNhYHhJFY | 5 | 96% | 21 | -0.72 | -0.32 / -0.08 / 0.02 |
| 4sr1wD_-r1s | 15 | 87% | 15 | -0.79 | -0.53 / -0.22 / 0.3 |
| 56Tzj_Ie7l0 | 8 | 90% | 11 | -0.78 | -0.68 / -0.27 / 0.01 |
| 5_vJU8XJOTs | 15 | 97% | 18 | -0.75 | -0.59 / -0.39 / -0.21 |
| 5arVdubK9Pg | 2 | 95% | 53 | -0.48 | -0.03 / 0.04 / 0.12 |
| 5mtw69jSZAY | 15 | 96% | 9 | -0.67 | -0.69 / -0.34 / 0.13 |
| 5t_zAmaON_g | 4 | 80% | 5 | -0.6 | -0.44 / -0.24 / -0.16 |
| 5wdrcvQQJMg | 15 | 96% | 32 | -0.72 | -0.58 / -0.18 / 0.12 |
| 6_CAfr0mQ-A | 15 | 95% | 12 | -0.84 | -0.67 / -0.38 / -0.13 |
| 6pe6DfGtOAM | 10 | 94% | 54 | -0.78 | -0.4 / 0.05 / 0.3 |
| 75SDa52tY1c | 15 | 95% | 13 | -0.77 | -0.65 / -0.3 / -0.04 |
| 784lVNd-apU | 10 | 98% | 3 | -0.89 | -0.6 / -0.22 / -0.05 |
| 7HvlDrYpWEQ | 15 | 97% | 4 | -0.64 | -0.76 / -0.49 / 0.14 |
| 7xdQDqILnSI | 15 | 91% | 39 | -0.68 | -0.57 / -0.15 / 0.1 |
| 8VAT46jqJA0 | 15 | 84% | 27 | -0.59 | -0.59 / -0.24 / 0.15 |
| 8r6F0MgBbz0 | 13 | 83% | 63 | -0.69 | -0.4 / -0.27 / 0.02 |
| 96i30WAkwUM | 9 | 90% | 11 | -0.6 | -0.34 / -0.2 / 0.02 |
| 9L9narLQj9M | 15 | 95% | 39 | -0.71 | -0.6 / -0.16 / 0.17 |
| 9NKtOSzeIIM | 15 | 93% | 46 | -1.01 | -0.53 / -0.43 / -0.08 |
| 9O_3QibgbRE | 15 | 99% | 10 | -0.74 | -0.46 / -0.23 / 0.12 |
| 9v3NfhfJD5Q | 15 | 98% | 37 | -0.82 | -0.67 / -0.44 / -0.09 |
| A2CdXZ-Ct-c | 8 | 84% | 64 | -0.34 | -0.63 / -0.05 / 0.08 |
| A9e-LtL7IaI | 15 | 96% | 38 | -0.62 | -0.63 / -0.15 / -0.0 |
| AAIc7Li2WbA | 15 | 98% | 22 | -0.48 | -0.42 / -0.12 / 0.27 |
| AEn2acwAQ7Y | 2 | 99% | 40 | -0.74 | -0.26 / -0.22 / -0.18 |
| AWs09rEo_v0 | 8 | 96% | 32 | -0.6 | -0.42 / -0.17 / 0.11 |
| Ai1wvW13HOc | 7 | 65% | 20 | -0.63 | -0.37 / 0.1 / 0.21 |
| Aifm8Ssxibw | 8 | 94% | 18 | -0.63 | -0.62 / -0.28 / 0.14 |
| Ap0qSdyx9H4 | 7 | 70% | 5 | -0.76 | -0.23 / -0.15 / -0.0 |
| Aq0fU8nnSOs | 1 | 73% | 7 | -0.64 | -0.24 / -0.24 / -0.24 |
| BPLFRhnkziY | 15 | 93% | 30 | -0.59 | -0.61 / -0.38 / -0.05 |
| Bm8QljKE9MM | 2 | 100% | 56 | -0.59 | -0.52 / -0.3 / -0.08 |
| BnmVSa9dWz0 | 15 | 98% | 9 | -0.8 | -0.43 / -0.19 / -0.01 |
| Bun_Ouz5-bs | 15 | 93% | 50 | -0.46 | -0.49 / -0.09 / 0.21 |
| BwYS96dRFM0 | 15 | 99% | 10 | -0.76 | -0.62 / -0.39 / -0.0 |
| CxLVAuZLAMs | 9 | 100% | 11 | -0.66 | -0.89 / -0.43 / -0.14 |
| D0IQYtGQHKE | 15 | 88% | 53 | -0.59 | -0.52 / -0.25 / 0.06 |
| D6C0g7zPaGk | 15 | 94% | 28 | -0.79 | -0.68 / -0.26 / -0.01 |
| DA8sM2ilEsc | 14 | 79% | 35 | -0.88 | -0.66 / -0.35 / 0.06 |
| DiXCMYwvw-8 | 15 | 100% | 6 | -0.71 | -0.7 / -0.25 / 0.12 |
| DivLvT5R_JA | 12 | 94% | 11 | -0.62 | -0.54 / -0.2 / -0.0 |
| E0g3LNBhJeU | 15 | 99% | 48 | -0.63 | -0.44 / -0.13 / 0.4 |
| E5F6qmT2XCk | 6 | 71% | 15 | -0.76 | -0.77 / -0.74 / -0.62 |
| EEHaZ4PrUFI | 15 | 94% | 9 | -0.84 | -0.62 / -0.11 / 0.21 |
| EZuZTjn8I08 | 14 | 88% | 46 | -0.73 | -0.2 / -0.06 / 0.51 |
| F-yNBm8loyk | 15 | 95% | 28 | -0.68 | -0.53 / -0.33 / 0.12 |
| F3qUPNxUGgo | 15 | 92% | 16 | -0.67 | -0.47 / -0.07 / 0.04 |
| FKRYw1VU9Qk | 0 | 79% | 25 |  |  |
| FssCtZEWBH4 | 15 | 96% | 12 | -0.6 | -0.42 / -0.1 / 0.02 |
| FuinI7uw8hQ | 9 | 98% | 28 | -0.83 | -0.74 / -0.13 / 0.12 |
| GgvWLeest9I | 3 | 99% | 37 | -0.59 | -0.43 / -0.22 / -0.16 |
| GztttGCA1pY | 15 | 96% | 22 | -0.48 | -0.5 / -0.05 / 0.34 |
| Hn_xHDmR2zM | 0 | 72% | 56 |  |  |
| IWj5qhSHnL0 | 8 | 91% | 11 | -0.41 | -0.49 / -0.21 / 0.12 |
| Ib7DmMuqPiE | 15 | 90% | 48 | -0.79 | -0.7 / -0.33 / 0.11 |
| IpoTbr5XINI | 15 | 91% | 8 | -0.8 | -0.62 / 0.14 / 0.48 |
| J929_RFF32E | 3 | 79% | 41 | -0.53 | -0.45 / 0.05 / 0.12 |
| JQXdqMXUfJM | 15 | 96% | 32 | -0.78 | -0.52 / -0.26 / -0.06 |
| KAK5a9Qs12w | 15 | 97% | 6 | -0.77 | -0.63 / -0.18 / 0.14 |
| KAyZ1uH5plI | 15 | 95% | 7 | -0.86 | -0.55 / -0.1 / 0.2 |
| K_bqRpOU6rA | 5 | 78% | 57 | -0.51 | -0.41 / -0.27 / -0.03 |
| KcHbjatv8yU | 13 | 92% | 40 | -0.66 | -0.61 / -0.24 / -0.04 |
| LCKk0N4p2_A | 10 | 95% | 8 | -0.57 | -0.43 / -0.08 / 0.32 |
| LCtYngOwfsw | 15 | 100% | 6 | -0.81 | -0.7 / -0.08 / 0.1 |
| LSqVp9QHERQ | 4 | 93% | 28 | -0.89 | -0.17 / 0.22 / 0.33 |
| Le0dgmeL-LE | 15 | 94% | 10 | -0.73 | -0.4 / -0.17 / 0.11 |
| M5mhUjZd22s | 3 | 87% | 42 | -0.79 | -0.56 / -0.43 / -0.03 |
| NaP7RiVXz2E | 11 | 98% | 8 | -0.64 | -0.4 / -0.25 / 0.21 |
| NfyrO92yMTc | 7 | 98% | 46 | -0.69 | -0.64 / 0.08 / 0.19 |
| NlGP2PaZ5HA | 6 | 82% | 44 | -0.73 | -0.3 / -0.06 / 0.29 |
| NuepcSzH44o | 14 | 100% | 8 | -0.59 | -0.58 / -0.16 / 0.18 |
| O21f-6kaIwk | 15 | 87% | 37 | -0.56 | -0.34 / -0.1 / 0.04 |
| OBZaRtH7OQY | 15 | 92% | 11 | -0.74 | -0.69 / -0.18 / 0.08 |
| OMvRlIlLa_8 | 15 | 93% | 44 | -0.65 | -0.57 / -0.34 / -0.09 |
| OSkioIwXEYM | 12 | 93% | 51 | -0.61 | -0.49 / -0.27 / -0.19 |
| OaBuo8jBgJU | 8 | 97% | 17 | -0.63 | -0.74 / -0.46 / -0.29 |
| Paw1e6sIJkM | 1 | 91% | 25 | -0.13 | -0.15 / -0.15 / -0.15 |
| PeEkclg6SKE | 15 | 92% | 11 | -0.52 | -0.65 / -0.08 / 0.06 |
| PkiZmPZBdw8 | 8 | 99% | 7 | -0.75 | -0.68 / -0.24 / -0.2 |
| PsPQWDKw7Zo | 10 | 100% | 6 | -0.73 | -0.8 / -0.44 / -0.22 |
| Pv5kymKGQEA | 15 | 99% | 16 | -0.71 | -0.69 / -0.3 / -0.09 |
| QAcBgVZheDo | 0 | 99% | 22 |  |  |
| QQTpd0z9C1k | 13 | 96% | 15 | -0.82 | -0.64 / -0.29 / 0.05 |
| QrDWirGkue8 | 7 | 82% | 49 | -0.83 | -0.7 / -0.65 / -0.38 |
| RVnHEcORqqI | 15 | 86% | 32 | -0.32 | -0.25 / 0.03 / 0.24 |
| RXsu2NlL2kE | 14 | 92% | 24 | -0.74 | -0.54 / -0.08 / 0.2 |
| RwEF_Mty7Ps | 15 | 85% | 50 | -0.73 | -0.63 / -0.26 / -0.07 |
| S5N0ASybB7g | 7 | 92% | 19 | -0.57 | -0.43 / -0.08 / 0.2 |
| SHB7xsIPv5E | 15 | 94% | 52 | -0.6 | -0.58 / -0.3 / 0.29 |
| Sb2Cm_KmwPU | 15 | 96% | 15 | -0.85 | -0.46 / -0.05 / 0.27 |
| T1FuyfTHsmQ | 11 | 91% | 20 | -0.77 | -0.34 / -0.11 / 0.18 |
| TeYKveJ1NS4 | 15 | 95% | 14 | -0.6 | -0.35 / -0.09 / 0.14 |
| TgCZr6aRa1Q | 13 | 90% | 32 | -0.69 | -0.42 / -0.06 / 0.05 |
| U2dKyI_2lWQ | 4 | 100% | 4 | -0.52 | -0.31 / -0.09 / 0.24 |
| UaPuZ5HIU1U | 15 | 89% | 10 | -0.69 | -0.52 / -0.17 / 0.03 |
| UdLFwBicq8E | 9 | 95% | 12 | -0.63 | -0.66 / -0.45 / -0.28 |
| UnEUw4jVrEY | 14 | 97% | 8 | -0.5 | -0.26 / 0.11 / 0.45 |
| V26ifGuICIE | 6 | 94% | 14 | -0.79 | -0.78 / -0.35 / -0.1 |
| V9QMvLauAls | 3 | 88% | 37 | -0.45 | -0.1 / 0.07 / 0.41 |
| VC4_qolv6mk | 9 | 100% | 44 | -0.41 | 0.02 / 0.17 / 0.19 |
| VLNuqgjf4-4 | 6 | 100% | 6 | -0.57 | -0.7 / -0.4 / -0.16 |
| W-v8U7K0_m0 | 15 | 98% | 5 | -0.56 | -0.5 / -0.11 / 0.39 |
| We-nHWaJ2Ig | 15 | 95% | 11 | -0.7 | -0.31 / -0.2 / -0.01 |
| WlQLN5mJ7Xg | 15 | 88% | 9 | -0.72 | -0.59 / -0.24 / 0.16 |
| XA34mJgU0ks | 15 | 99% | 10 | -0.77 | -0.75 / -0.35 / -0.07 |
| XVs_p57iNLE | 8 | 84% | 59 | -0.59 | -0.61 / -0.49 / -0.35 |
| X_eg2H8Fa3Q | 13 | 90% | 6 | -0.7 | -0.46 / -0.18 / 0.1 |
| XeJyEfMVp5E | 15 | 93% | 13 | -0.78 | -0.47 / -0.22 / 0.07 |
| YGZrgFsQCjg | 14 | 84% | 39 | -0.79 | -0.38 / 0.07 / 0.19 |
| YpPCRn5czWM | 15 | 100% | 5 | -0.48 | -0.29 / -0.02 / 0.18 |
| ZBJfWvONORw | 15 | 89% | 14 | -0.75 | -0.36 / -0.08 / 0.17 |
| ZDPAINbsTI4 | 15 | 92% | 9 | -0.75 | -0.66 / -0.32 / -0.09 |
| ZI-r1-3-6X4 | 14 | 93% | 9 | -0.73 | -0.41 / -0.23 / -0.13 |
| Z_ykU7AKpiI | 0 | 37% | 8 |  |  |
| _nIDNlOp7yo | 9 | 88% | 52 | -0.87 | -0.71 / -0.48 / -0.04 |
| _yJNVtqOvHw | 5 | 88% | 61 | -0.54 | -0.17 / -0.03 / 0.07 |
| _z_60MokjvI | 4 | 70% | 11 | -0.61 | -0.43 / -0.09 / 0.04 |
| a3tPNl7BsFw | 1 | 70% | 51 | -0.72 | -0.45 / -0.45 / -0.45 |
| aMMtit2VFTc | 15 | 80% | 55 | -0.48 | -0.62 / -0.25 / 0.07 |
| anl7snB3TAI | 14 | 89% | 55 | -0.85 | -0.48 / -0.15 / 0.32 |
| bDl4mWTJrg0 | 3 | 97% | 55 | -0.78 | -0.35 / -0.18 / -0.18 |
| b_kWKaTz_aQ | 15 | 94% | 9 | -0.69 | -0.71 / -0.37 / 0.0 |
| bpUwrIMGh7A | 15 | 96% | 10 | -0.75 | -0.57 / -0.22 / 0.14 |
| cIqEpKRczJ4 | 11 | 94% | 54 | -0.71 | -0.25 / 0.03 / 0.48 |
| cK8Rb-clu6o | 14 | 97% | 8 | -0.7 | -0.58 / -0.21 / 0.43 |
| cu_h1trboKk | 7 | 100% | 8 | -0.73 | -0.54 / -0.33 / -0.03 |
| dCWA2Gr98ZY | 2 | 93% | 62 | -0.62 | -0.32 / -0.07 / 0.17 |
| dPOmMMObcn4 | 15 | 99% | 19 | -0.52 | -0.51 / -0.21 / 0.16 |
| dQLfd9ogDQ0 | 15 | 84% | 13 | -0.67 | -0.9 / -0.48 / -0.2 |
| dieLbZ9XLlA | 1 | 89% | 29 | -0.73 | 0.27 / 0.27 / 0.27 |
| dnxe6t97xzo | 14 | 91% | 45 | -0.49 | -0.41 / 0.0 / 0.05 |
| dxr99mLfUXE | 14 | 97% | 8 | -0.72 | -0.39 / -0.13 / 0.06 |
| dzAIDEiFBv4 | 15 | 95% | 5 | -0.71 | -0.58 / -0.16 / 0.16 |
| e_nKX3QcU04 | 15 | 88% | 10 | -0.69 | -0.49 / -0.11 / 0.12 |
| eu0Kym_vs1E | 14 | 71% | 49 | -0.75 | -0.79 / -0.58 / -0.12 |
| f3yz0WZ8NOs | 11 | 100% | 6 | -0.65 | -0.58 / -0.41 / -0.02 |
| fDiJW1OYxac | 10 | 97% | 13 | -0.74 | -0.58 / -0.39 / -0.12 |
| fRjwYp_t0OE | 15 | 96% | 10 | -0.66 | -0.4 / -0.23 / 0.06 |
| fgFocZOAxog | 0 | 99% | 7 |  |  |
| fn7ty-cPv4U | 13 | 95% | 8 | -0.71 | -0.75 / -0.48 / -0.25 |
| g4_PTWXDY_I | 2 | 92% | 35 | -0.57 | -0.44 / -0.35 / -0.26 |
| gA4mDtJlPF0 | 11 | 99% | 10 | -0.77 | -0.57 / -0.18 / 0.51 |
| gC26cC9N1VU | 12 | 96% | 13 | -0.73 | -0.74 / -0.25 / 0.09 |
| gWTvbXyg2HM | 13 | 93% | 51 | -0.81 | -0.46 / -0.33 / 0.34 |
| gbXgoKc2NIc | 15 | 98% | 14 | -0.64 | -0.56 / 0.03 / 0.35 |
| gky0Lktyt_0 | 2 | 94% | 15 | -0.49 | -0.0 / 0.11 / 0.23 |
| hdVnB1t6ZUM | 15 | 94% | 12 | -0.73 | -0.52 / 0.01 / 0.19 |
| hsnd8zfiROs | 4 | 73% | 32 | -0.77 | -0.7 / -0.56 / -0.23 |
| ht_vOk4Idcs | 8 | 95% | 9 | -0.72 | -0.47 / -0.18 / -0.02 |
| iXvWh-xMSd0 | 13 | 97% | 16 | -0.61 | -0.51 / -0.23 / -0.12 |
| jBjuY3eZ8mg | 15 | 95% | 43 | -0.55 | -0.65 / -0.26 / 0.21 |
| jf2vpi4GG3A | 15 | 94% | 15 | -0.43 | -0.54 / -0.1 / 0.32 |
| kB3aP3vMEeU | 12 | 65% | 12 | -0.7 | -0.63 / -0.17 / 0.17 |
| kFRYXXm8ZM0 | 14 | 96% | 35 | -0.59 | -0.21 / 0.24 / 0.47 |
| lCKDP2gKR_Y | 0 | 61% | 24 |  |  |
| lDKV9j6VX4Y | 0 | 50% | 35 |  |  |
| lQxFiUhgj8k | 15 | 79% | 25 | -0.56 | -0.58 / -0.12 / 0.18 |
| lhumU9wqWls | 15 | 87% | 35 | -0.6 | -0.58 / -0.18 / 0.42 |
| ljqBTn1jZbU | 15 | 80% | 8 | -0.76 | -0.62 / -0.26 / -0.03 |
| lpFI1yxeok8 | 15 | 98% | 9 | -0.74 | -0.42 / -0.11 / 0.21 |
| lqB5CjbU2-k | 15 | 86% | 34 | -0.7 | -0.57 / -0.15 / -0.02 |
| lrNPyAyprTk | 3 | 83% | 40 | -0.46 | -0.1 / -0.09 / 0.02 |
| mO6XiArAjPI | 15 | 92% | 55 | -0.51 | -0.31 / -0.2 / -0.07 |
| mbx0ZebdPAQ | 12 | 98% | 28 | -0.59 | -0.54 / -0.07 / 0.43 |
| mfyu-kW4OvQ | 0 | 85% | 4 |  |  |
| nh8NLQwcqZU | 15 | 93% | 44 | -0.77 | -0.48 / -0.17 / 0.01 |
| nn3-xPK-fzw | 15 | 88% | 18 | -0.55 | -0.47 / -0.23 / 0.05 |
| nuqjhrjqcd0 | 4 | 86% | 54 | -0.35 | -0.06 / -0.05 / 0.33 |
| nxht8qbaWu8 | 5 | 90% | 55 | -0.78 | -0.27 / -0.22 / -0.07 |
| o_ZZFk-pB3A | 15 | 98% | 34 | -0.55 | -0.42 / 0.05 / 0.23 |
| ohupLT98G4c | 15 | 85% | 40 | -0.63 | -0.42 / -0.07 / 0.13 |
| p9ggFteqtpY | 7 | 95% | 8 | -0.65 | -0.71 / -0.53 / 0.14 |
| pZIBqmv4By8 | 15 | 74% | 6 | -0.69 | -0.49 / -0.17 / 0.08 |
| pbuUnesx7Ls | 15 | 98% | 10 | -0.47 | -0.46 / -0.06 / 0.15 |
| peG7SSmzgvE | 0 | 99% | 13 |  |  |
| pfvYK7xbSIQ | 15 | 94% | 23 | -0.65 | -0.51 / -0.42 / 0.14 |
| pgJ2nT4_pU0 | 14 | 93% | 14 | -0.73 | -0.52 / -0.29 / -0.1 |
| q4A9i-RFTvY | 15 | 85% | 17 | -0.76 | -0.19 / 0.2 / 0.38 |
| qU5OxAgpE1A | 15 | 95% | 35 | -0.71 | -0.69 / -0.27 / -0.09 |
| qfMVnQ07pcI | 15 | 91% | 13 | -0.84 | -0.75 / -0.28 / -0.01 |
| r1KRhB4QeCg | 12 | 78% | 55 | -0.9 | -0.6 / -0.32 / 0.51 |
| scD84O4afpk | 15 | 97% | 12 | -0.74 | -0.71 / -0.34 / 0.1 |
| sw2_HmjgqpI | 2 | 94% | 5 | -0.55 | -0.27 / -0.19 / -0.11 |
| tTkRZz3P4WM | 15 | 96% | 13 | -0.66 | -0.68 / -0.31 / -0.0 |
| tdnrLAzyriA | 9 | 95% | 35 | -0.65 | -0.72 / -0.55 / -0.35 |
| u0NvVbKVG4I | 3 | 92% | 55 | -0.55 | -0.35 / 0.07 / 0.22 |
| uDwKji3EC6M | 4 | 97% | 53 | -0.35 | -0.71 / -0.43 / 0.03 |
| uXF4jhDcX2A | 12 | 91% | 5 | -0.79 | -0.49 / -0.15 / 0.31 |
| uXGwWhOj6P4 | 12 | 73% | 48 | -0.85 | -0.71 / -0.05 / 0.07 |
| ubFJi2M3AMM | 15 | 86% | 48 | -0.68 | -0.5 / -0.19 / 0.02 |
| ucEw3C6Zpc8 | 15 | 81% | 7 | -0.59 | -0.41 / 0.11 / 0.29 |
| ukNZF2Q9ki0 | 12 | 95% | 37 | -0.74 | -0.41 / -0.29 / 0.31 |
| uzPSqM3nj0A | 15 | 94% | 13 | -0.71 | -0.43 / -0.14 / 0.12 |
| v4oUVVlM1JA | 15 | 97% | 22 | -0.49 | -0.23 / 0.02 / 0.24 |
| v9Oe1avJf2o | 15 | 88% | 11 | -0.72 | -0.67 / -0.33 / -0.03 |
| v9n_EbpIWNI | 3 | 86% | 38 | -0.63 | -0.14 / 0.39 / 0.4 |
| vI4mperPhj0 | 14 | 88% | 11 | -0.74 | -0.39 / -0.12 / 0.07 |
| vX_xBFeAIcg | 15 | 92% | 28 | -0.76 | -0.51 / -0.24 / 0.15 |
| v_Z-f5KHcNY | 15 | 99% | 6 | -0.76 | -0.73 / -0.13 / 0.19 |
| wQX8B7wYip4 | 15 | 94% | 8 | -0.79 | -0.62 / -0.27 / 0.1 |
| x7VPW17Rew0 | 2 | 82% | 4 | -0.6 | -0.37 / -0.35 / -0.33 |
| xeGZAHe4BAE | 11 | 88% | 31 | -0.69 | -0.36 / -0.1 / 0.07 |
| xwFVcyt8P_M | 15 | 95% | 12 | -0.7 | -0.55 / -0.16 / 0.32 |
| yEly5ZJw5ng | 8 | 74% | 49 | -0.6 | -0.21 / -0.07 / 0.1 |
| yPCY1PNAYqE | 13 | 89% | 40 | -0.71 | -0.68 / -0.32 / -0.24 |
| yYLrp-15Ao0 | 13 | 89% | 24 | -0.56 | -0.48 / -0.32 / 0.3 |
| yZ0-We5d0jQ | 15 | 97% | 7 | -0.54 | -0.7 / -0.31 / 0.09 |
| zPbtp0WtHA4 | 9 | 93% | 13 | -0.52 | -0.41 / -0.21 / 0.04 |
| zTxLiZaSDbQ | 15 | 93% | 41 | -0.57 | -0.47 / -0.17 / -0.02 |
| ziWEgWm4FkQ | 15 | 87% | 6 | -0.7 | -0.68 / -0.29 / 0.06 |

## Vocabulary proposals

- measurement: phase boundary at end of takeback (Late preparation, arm-only takeback, take-back size and arm path all show at the end of the unit turn, which falls inside the 'swing_to_finish' phase. A separate landmark there would let tests be placed on it.)
- measurement: phase boundary at ball contact (Contact is the key moment for spacing, shoulder rotation and elbow angle. The two landmarks in this data do not mark it.)
- feature: racket face angle at contact (Coaches cite a wrong face angle as a fault, but no registered feature shows the racket or the angle of the hand or wrist.)
- trackable: racket head / racket path (Needed to see loops in the takeback and the racket drop. It would also show the timing of the swing.)
- trackable: ball position (Timing, spacing, waiting for the bounce, shot choice and target outcomes need the ball and its landing point.)
- feature: racket-arm elbow angle relative to the trunk in the unit turn (Used to judge a bent or straight arm in the takeback, which coaches disagree on.)
