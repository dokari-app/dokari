# Factory report: tennis_forehand

Clips found: 231 (usable for attempts: 220). Attempts: 2785.
Confidence tier: **low**. Checks: 7 pass, 3 fail, 0 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.64 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [FAIL] 6. discrimination: 0/4 objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75); do not: ['rotation_late_or_blocked', 'short_or_stopped_follow_through', 'poor_spacing_to_ball', 'non_hitting_hand_misuse']; 1 without enough labels
- [PASS] 7. outcome links: 3 links, 3 prior-only (no data to test them yet)
- [FAIL] 8. agreement: agreement 0.45 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 5 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **rotation_late_or_blocked** (medium, agreed by 5 of 5 runs): Rotate the hips and shoulders through the shot so the shoulder line has turned with the swing at contact.. Target: angle.shoulder_hip_twist between -33.946 and 31.8166 at L1. Wrong if below: Torso stays square or blocked, the arm swings alone and the shoulders are behind at contact. (medium); above: Over-rotation, with the shoulders spun far ahead of the hips and the body pulling around too early. (low). Range from good-form demonstrations (489 attempts in 44 clips); reliability C.
- 2. **arm_pulling_in_on_acceleration** (medium, agreed by 5 of 5 runs): Let the hitting arm extend away from the body and up through contact, not bend and pull in toward the body.. Target: reach.wrist.dom between 0.5721 and 1.0726 at L1. Wrong if below: The elbow collapses and the hand cuts down and in toward the body, so contact is cramped. (medium); above: Arm fully stretched out, reaching for a ball that is too far away. (low). Range from good-form demonstrations (489 attempts in 44 clips); reliability C.
- 3. **short_or_stopped_follow_through** (medium, agreed by 3 of 5 runs): Swing through the ball into a complete, unhurried finish instead of stopping the arm early.. Target: height.wrist.dom at least -0.8083 at L1. Wrong if below: The arm stops or bends low and the finish is short or rushed. Coaches disagree whether the finish should be over the shoulder or across the body, so only a stopped finish counts as the fault. (medium). Range from good-form demonstrations (489 attempts in 44 clips); reliability C.
- 4. **poor_spacing_to_ball** (medium, agreed by 4 of 5 runs): Set up with the body at a comfortable distance from the ball, with weight moving neutrally or forward through contact.. Target: fwd.trunk_shift between -0.3205 and 0.7454 at L1. Wrong if below: Weight stays back or travels backward and the ball ends up behind the body. (medium); above: Crowding the ball, or leaning forward and jamming the arm. (low). Range from good-form demonstrations (489 attempts in 44 clips); reliability C.
- 5. **non_hitting_hand_misuse** (medium, agreed by 3 of 5 runs): Use the non-hitting arm to help balance and turn, extended in the preparation and then drawn in smoothly, not left dangling or flung away.. Target: angle.shoulder.non between 12.1206 and 115.1748 at L1. Wrong if below: The free arm hangs or hugs the body, so balance and rotation are poor. (medium); above: The free arm splits away early or flails outward, which pulls the shoulders off line. (medium). Range from good-form demonstrations (489 attempts in 44 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **late_or_mistimed_preparation** (form; 4 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **short_or_stopped_follow_through** (form; 4 of 12, some): measured by the camera (short_or_stopped_follow_through). Coaches disagree: Source 11 finishes over the shoulder. Source 8 finishes across the body, and source 1 says follow-throughs vary on tour.
- **arm_only_takeback** (safety; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (rotation_late_or_blocked).
- **arm_style_in_unit_turn** (form; 3 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.elbow.dom shows arm straightness; no test because the right value depends on player style.. Coaches disagree: Sources 0 and 1 want a bent or in-line elbow in the unit turn. Source 8 says bent or straight doesn't matter, so don't force a straight arm.
- **contact_face_angle_wrong** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection (racket face orientation) or hand landmarks for forearm rotation. Coaches disagree: Source 4 says tilt the face forward, and source 9 says beginners should use an open angle.
- **non_hitting_hand_misuse** (safety; 3 of 12, some): measured by the camera (non_hitting_hand_misuse).
- **poor_spacing_to_ball** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (poor_spacing_to_ball). Coaches disagree: Source 9 says stay open and don't step into every ball. Sources 7 and 10 say step in for neutral stance and step into the ball.
- **rotation_late_or_blocked** (form; 3 of 12, some): measured by the camera (rotation_late_or_blocked).
- **take_back_too_big** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (short_or_stopped_follow_through). Coaches disagree: Source 11 says to take the racquet all the way back behind you while staying compact. Sources 2 and 3 push a smaller take-back.
- **takeback_arm_path** (form; 3 of 12, some): would need a new body feature: wrist trajectory path during backswing (wrist position over time relative to shoulder/trunk, loop detection). Coaches disagree: Source 9 says don't loop the arm. Sources 5 and 6 recommend a loop or circle path for the racket.
- **arm_pulling_in_on_acceleration** (form; 2 of 12, some): measured by the camera (arm_pulling_in_on_acceleration).
- **arm_started_swing_no_leg_drive** (form; 2 of 12, some): would need a new body feature: sequencing of leg extension (knee/hip angle change) before arm movement; timing/order of joint velocities. Coaches disagree: Source 9 disagrees: legs are complementary and the arm leads.
- **ball_behind_body_when_pushed_back** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (poor_spacing_to_ball). Coaches disagree: Source 3 says weight should go forward or stay neutral. Source 5 says keep the body behind the ball and hit off the back foot.
- **poor_shot_choice_and_target** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **racket_face_not_closed_backswing** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection or hand landmarks for racket face orientation.
- **tension_in_grip_and_contact** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **wrist_flexed_arm_cramped_at_contact** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (arm_pulling_in_on_acceleration).
- **conscious_wrist_action** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks or racket tracking for wrist flick; intent is not visible. Coaches disagree: Source 1 wants an active windshield-wiper wrist, and source 0 wants a flip. Source 8 wants the wrist passive at contact.
- **over_relying_on_legs** (form; 1 of 12, single): would need a new body feature: coordination of leg drive versus arm movement over time (knee/hip extension timing relative to arm swing). Coaches disagree: Sources 0, 1 and 3 teach leg drive first as the power source.
- **wrong_grip** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks for grip rotation in the hand; racket detection for grip size.

Good form, as coaches give it:

- Accelerate as a kinetic chain from the ground up: legs, hips, trunk, then arm. (5 of 12)
- Stay balanced with weight moving forward or neutral, and keep enough space from the ball. (5 of 12)
- Take the racket back by turning the whole body, with the racket going along. (4 of 12)
- Start the take-back early, as soon as you read the ball, without waiting for the bounce. (4 of 12)
- Use the non-hitting hand to help the racket back, stay coiled, and catch the racket at the finish. (4 of 12)
- Make contact out in front of the body with the arm in front and the wrist extended. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **power_flows_from_ground_through_trunk** (contested, 3 of 3 runs; explains rotation_late_or_blocked, arm_only_takeback, arm_started_swing_no_leg_drive, over_relying_on_legs): Power builds from the ground up: legs and hips turn first, then the trunk, then the arm and racket. The arm adds speed at the end of the chain instead of creating it, so the shoulder line has turned with the swing by contact. Cue handle: . Competing views: Sources 0, 1 and 3 teach leg drive first as the main power source.; Source 9 says the legs are complementary and the arm leads the swing..
- **space_to_extend_through_contact** (contested, 3 of 3 runs; explains poor_spacing_to_ball, arm_pulling_in_on_acceleration, wrist_flexed_arm_cramped_at_contact, ball_behind_body_when_pushed_back): A comfortable distance from the ball leaves room for the arm to extend away from the body and up through contact. If the ball is too close or the arm bends in, the lever is cramped and the swing loses reach and speed. Cue handle: Keep room to reach out and up through the ball.. Competing views: Sources 7 and 10 say to step in with a neutral stance and step into the ball.; Source 9 says to stay open and not step into every ball.; Source 3 says weight should go forward or stay neutral when pushed back; Source 5 says to hit off the back foot, body behind the ball..
- **early_preparation_creates_time** (contested, 2 of 3 runs; explains late_or_mistimed_preparation, take_back_too_big, takeback_arm_path, arm_style_in_unit_turn): Getting the turn and racket ready early gives time to set up and swing at an even pace. Late preparation forces a rushed or mistimed swing. A compact preparation keeps contact on time. Cue handle: Be set and ready before the ball arrives so the swing flows at an even rhythm.. Competing views: Source 11 says to take the racquet all the way back while staying compact; Sources 2 and 3 push a smaller take-back.; Sources 5 and 6 recommend a looped racket path; Source 9 says not to loop the arm.; Sources 0 and 1 want a bent or in-line elbow in the unit turn; Source 8 says bent or straight does not matter..
- **swing_through_to_finish** (contested, 2 of 3 runs; explains short_or_stopped_follow_through, arm_pulling_in_on_acceleration): Keep the racket moving through the ball into a full, unhurried finish. The arm then keeps accelerating through contact instead of braking early, and the speed bleeds off smoothly on the way to recovery. Cue handle: Keep accelerating through the ball and let the swing finish on its own.. Competing views: Source 11 finishes over the shoulder.; Source 8 finishes across the body.; Source 1 says follow-throughs vary on tour..
- **free_arm_balances_the_turn** (coaching_consensus, 2 of 3 runs; explains non_hitting_hand_misuse, rotation_late_or_blocked): The non-hitting arm acts as a counterweight. Extended during preparation, it helps balance and turn the trunk, then it draws in smoothly so the body stays stable and the turn is controlled. Dangling or flinging it away upsets balance. Cue handle: Stay balanced and turn smoothly, with both sides working together..

## Check against labelled mistake videos (173 videos, 2353 attempts, 1115 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| non_hitting_hand_misuse | 22 / 10 | 31 / 15 |
| poor_spacing_to_ball | 20 / 5 | 4 / 3 |
| takeback_arm_path | 18 / 10 | 3 / 3 |
| late_or_mistimed_preparation | 14 / 8 | 51 / 16 |
| short_or_stopped_follow_through | 9 / 8 | 126 / 49 |
| take_back_too_big | 8 / 5 | 13 / 4 |
| arm_started_swing_no_leg_drive | 5 / 3 | 1 / 1 |
| rotation_late_or_blocked | 5 / 3 | 0 / 0 |
| arm_style_in_unit_turn | 4 / 4 | 1 / 1 |
| arm_only_takeback | 2 / 2 | 336 / 81 |
| conscious_wrist_action | 1 / 1 | 1 / 1 |
| over_relying_on_legs | 0 / 0 | 1 / 1 |
| racket_face_not_closed_backswing | 0 / 0 | 1 / 1 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| rotation_late_or_blocked | 36 / 19 | 13 / 10 | 0.56 | 49% | does not tell right from wrong well enough; range kept from good form demonstrations |
| arm_pulling_in_on_acceleration | 2 / 4 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| short_or_stopped_follow_through | 132 / 16 | 52 / 12 | 0.57 | 58% | does not tell right from wrong well enough; range kept from good form demonstrations |
| poor_spacing_to_ball | 54 / 38 | 14 / 14 | 0.49 | 38% | does not tell right from wrong well enough; range kept from good form demonstrations |
| non_hitting_hand_misuse | 90 / 34 | 24 / 12 | 0.5 | 41% | does not tell right from wrong well enough; range kept from good form demonstrations |

Movement characterised by: height.wrist.dom, angle.shoulder.dom, reach.wrist.dom, angle.shoulder.non, dist.wrist_width, angle.shoulder_hip_twist
Attempts found as: angle.shoulder.dom rises (to at least 55). Typical size of the last event 115.659, lasting 3.33 s; smaller ones (below 46.263) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 6521 clear attempts in 223 of 230 clips after 0 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 139 | 1812 | mistakes 60, mixed 1752 |
| coach_demo | 51 | 614 | good_form 264, mixed 350 |
| pro_footage | 23 | 221 | good_form 221 |
| practice_session | 9 | 126 | good_form 43, mixed 23, unknown 60 |
| instruction_talk | 2 | 16 | good_form 9, mixed 7 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| rotation_late_or_blocked | 7% (44 clips) | 4% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| arm_pulling_in_on_acceleration | 8% (44 clips) | 4% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| short_or_stopped_follow_through | 4% (44 clips) | 5% (176 clips) | no difference: everyone is inside, or this measure does not separate them |
| poor_spacing_to_ball | 10% (44 clips) | 4% (176 clips) | demos depart more: doubtful |
| non_hitting_hand_misuse | 5% (44 clips) | 4% (176 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- swing_to_peak_reach: L0 to L1
- follow_through_and_recovery: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip FssCtZEWBH4: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 2785 of 2827 attempts (tolerance 2.025). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (-V9fRDexnPM, -XEk39hZzzo, -pfEfb63tZ4, 0-yol2xtr_E, 0t4qsd6LeJg, 1AY-2Cc3LJU, 1meRp15WlKQ, 2J8q7sn4JLc, 2uuk8nZ8W_8, 33ffZPw9y-c, 4PnKAIKuypI, 56Tzj_Ie7l0, 5_vJU8XJOTs, 5mtw69jSZAY, 5wdrcvQQJMg, 7HvlDrYpWEQ, 8VAT46jqJA0, 8r6F0MgBbz0, 96i30WAkwUM, 9L9narLQj9M, 9v3NfhfJD5Q, A9e-LtL7IaI, Aifm8Ssxibw, BnmVSa9dWz0, Bun_Ouz5-bs, BwYS96dRFM0, CxLVAuZLAMs, D6C0g7zPaGk, DiXCMYwvw-8, EEHaZ4PrUFI, F-yNBm8loyk, FssCtZEWBH4, FuinI7uw8hQ, IWj5qhSHnL0, Ib7DmMuqPiE, JQXdqMXUfJM, LCtYngOwfsw, Le0dgmeL-LE, M5mhUjZd22s, NaP7RiVXz2E, OBZaRtH7OQY, OaBuo8jBgJU, PeEkclg6SKE, PkiZmPZBdw8, PsPQWDKw7Zo, Pv5kymKGQEA, QQTpd0z9C1k, RXsu2NlL2kE, S5N0ASybB7g, SHB7xsIPv5E, T1FuyfTHsmQ, TeYKveJ1NS4, TgCZr6aRa1Q, U2dKyI_2lWQ, V26ifGuICIE, VLNuqgjf4-4, W-v8U7K0_m0, WlQLN5mJ7Xg, XA34mJgU0ks, XVs_p57iNLE, YpPCRn5czWM, ZBJfWvONORw, ZDPAINbsTI4, ZI-r1-3-6X4, _yJNVtqOvHw, bDl4mWTJrg0, bpUwrIMGh7A, cK8Rb-clu6o, cu_h1trboKk, dPOmMMObcn4, dieLbZ9XLlA, dxr99mLfUXE, dzAIDEiFBv4, e_nKX3QcU04, f3yz0WZ8NOs, fDiJW1OYxac, fRjwYp_t0OE, fn7ty-cPv4U, gA4mDtJlPF0, gC26cC9N1VU, gbXgoKc2NIc, gky0Lktyt_0, ht_vOk4Idcs, jBjuY3eZ8mg, lhumU9wqWls, ljqBTn1jZbU, lpFI1yxeok8, lqB5CjbU2-k, nn3-xPK-fzw, nuqjhrjqcd0, o_ZZFk-pB3A, pbuUnesx7Ls, pgJ2nT4_pU0, qfMVnQ07pcI, scD84O4afpk, tTkRZz3P4WM, tdnrLAzyriA, uXF4jhDcX2A, uzPSqM3nj0A, v9Oe1avJf2o, vI4mperPhj0, vX_xBFeAIcg, v_Z-f5KHcNY, wQX8B7wYip4, x7VPW17Rew0, xwFVcyt8P_M, yPCY1PNAYqE, yYLrp-15Ao0, zTxLiZaSDbQ, ziWEgWm4FkQ).

| clip | attempts found | kept | note |
|---|---|---|---|
| -Eu80hGbgVA | 15 | 15 |  |
| -V9fRDexnPM | 15 | 15 | seed |
| -XEk39hZzzo | 15 | 15 | seed |
| -pfEfb63tZ4 | 15 | 15 | seed |
| 0-yol2xtr_E | 15 | 15 | seed |
| 0GN5BTx-ups | 15 | 15 |  |
| 0O391AzKX6Q | 15 | 15 |  |
| 0t4qsd6LeJg | 15 | 15 | seed |
| 1AY-2Cc3LJU | 15 | 15 | seed |
| 1l4ZC4047is | 7 | 7 |  |
| 1meRp15WlKQ | 2 | 2 | seed |
| 2GYxGHFKD5E | 15 | 12 |  |
| 2J8q7sn4JLc | 15 | 15 | seed |
| 2UlY27kxSa4 | 9 | 9 |  |
| 2pr4Xb-_B38 | 8 | 8 |  |
| 2uuk8nZ8W_8 | 9 | 9 | seed |
| 33ffZPw9y-c | 6 | 6 | seed |
| 3ja7tvQFbQQ | 15 | 15 |  |
| 4PnKAIKuypI | 15 | 15 | seed |
| 4ak0XepJYA0 | 5 | 5 |  |
| 4myNhYHhJFY | 4 | 4 |  |
| 4sr1wD_-r1s | 15 | 14 |  |
| 56Tzj_Ie7l0 | 13 | 13 | seed |
| 5_vJU8XJOTs | 15 | 15 | seed |
| 5arVdubK9Pg | 5 | 5 |  |
| 5mtw69jSZAY | 15 | 15 | seed |
| 5t_zAmaON_g | 9 | 7 |  |
| 5wdrcvQQJMg | 15 | 15 | seed |
| 6_CAfr0mQ-A | 15 | 15 |  |
| 6pe6DfGtOAM | 15 | 11 |  |
| 75SDa52tY1c | 15 | 15 |  |
| 7HvlDrYpWEQ | 15 | 15 | seed |
| 7xdQDqILnSI | 15 | 15 |  |
| 8VAT46jqJA0 | 15 | 15 | seed |
| 8r6F0MgBbz0 | 15 | 15 | seed |
| 96i30WAkwUM | 9 | 8 | seed |
| 9L9narLQj9M | 15 | 15 | seed |
| 9NKtOSzeIIM | 15 | 15 |  |
| 9O_3QibgbRE | 15 | 15 |  |
| 9v3NfhfJD5Q | 12 | 12 | seed |
| A2CdXZ-Ct-c | 15 | 15 |  |
| A9e-LtL7IaI | 15 | 15 | seed |
| AAIc7Li2WbA | 15 | 15 |  |
| AWs09rEo_v0 | 7 | 7 |  |
| Ai1wvW13HOc | 15 | 13 |  |
| Aifm8Ssxibw | 14 | 14 | seed |
| Ap0qSdyx9H4 | 8 | 7 |  |
| Aq0fU8nnSOs | 7 | 7 |  |
| BPLFRhnkziY | 15 | 15 |  |
| BnmVSa9dWz0 | 15 | 15 | seed |
| Bun_Ouz5-bs | 15 | 15 | seed |
| BwYS96dRFM0 | 15 | 15 | seed |
| CxLVAuZLAMs | 5 | 5 | seed |
| D0IQYtGQHKE | 15 | 15 |  |
| D6C0g7zPaGk | 15 | 15 | seed |
| DA8sM2ilEsc | 15 | 15 |  |
| DiXCMYwvw-8 | 15 | 15 | seed |
| DivLvT5R_JA | 15 | 15 |  |
| E0g3LNBhJeU | 15 | 15 |  |
| E5F6qmT2XCk | 14 | 11 |  |
| EEHaZ4PrUFI | 15 | 15 | seed |
| EZuZTjn8I08 | 15 | 13 |  |
| F-yNBm8loyk | 7 | 7 | seed |
| F3qUPNxUGgo | 15 | 15 |  |
| FssCtZEWBH4 | 15 | 15 | seed |
| FuinI7uw8hQ | 9 | 9 | seed |
| GgvWLeest9I | 3 | 3 |  |
| GztttGCA1pY | 15 | 14 |  |
| IWj5qhSHnL0 | 10 | 10 | seed |
| Ib7DmMuqPiE | 15 | 15 | seed |
| IpoTbr5XINI | 15 | 14 |  |
| J929_RFF32E | 15 | 15 |  |
| JQXdqMXUfJM | 15 | 15 | seed |
| KAK5a9Qs12w | 15 | 15 |  |
| KAyZ1uH5plI | 15 | 15 |  |
| K_bqRpOU6rA | 4 | 4 |  |
| KcHbjatv8yU | 15 | 14 |  |
| LCKk0N4p2_A | 15 | 14 |  |
| LCtYngOwfsw | 15 | 15 | seed |
| LSqVp9QHERQ | 9 | 9 |  |
| Le0dgmeL-LE | 15 | 15 | seed |
| M5mhUjZd22s | 11 | 11 | seed |
| NaP7RiVXz2E | 10 | 10 | seed |
| NfyrO92yMTc | 9 | 9 |  |
| NlGP2PaZ5HA | 15 | 10 |  |
| NuepcSzH44o | 12 | 12 |  |
| O21f-6kaIwk | 15 | 15 |  |
| OBZaRtH7OQY | 15 | 15 | seed |
| OMvRlIlLa_8 | 15 | 15 |  |
| OSkioIwXEYM | 15 | 15 |  |
| OaBuo8jBgJU | 6 | 6 | seed |
| Paw1e6sIJkM | 6 | 6 |  |
| PeEkclg6SKE | 15 | 15 | seed |
| PkiZmPZBdw8 | 14 | 14 | seed |
| PsPQWDKw7Zo | 11 | 11 | seed |
| Pv5kymKGQEA | 15 | 15 | seed |
| QAcBgVZheDo | 2 | 2 |  |
| QQTpd0z9C1k | 15 | 15 | seed |
| QrDWirGkue8 | 6 | 6 |  |
| RVnHEcORqqI | 15 | 15 |  |
| RXsu2NlL2kE | 9 | 9 | seed |
| RwEF_Mty7Ps | 15 | 15 |  |
| S5N0ASybB7g | 6 | 6 | seed |
| SHB7xsIPv5E | 15 | 15 | seed |
| Sb2Cm_KmwPU | 15 | 15 |  |
| T1FuyfTHsmQ | 15 | 15 | seed |
| TeYKveJ1NS4 | 15 | 15 | seed |
| TgCZr6aRa1Q | 15 | 15 | seed |
| U2dKyI_2lWQ | 9 | 9 | seed |
| UaPuZ5HIU1U | 15 | 15 |  |
| UdLFwBicq8E | 8 | 8 |  |
| UnEUw4jVrEY | 15 | 15 |  |
| V26ifGuICIE | 15 | 15 | seed |
| V9QMvLauAls | 8 | 8 |  |
| VC4_qolv6mk | 9 | 9 |  |
| VLNuqgjf4-4 | 2 | 2 | seed |
| W-v8U7K0_m0 | 15 | 15 | seed |
| We-nHWaJ2Ig | 15 | 15 |  |
| WlQLN5mJ7Xg | 15 | 15 | seed |
| XA34mJgU0ks | 15 | 15 | seed |
| XVs_p57iNLE | 15 | 15 | seed |
| X_eg2H8Fa3Q | 15 | 15 |  |
| XeJyEfMVp5E | 15 | 15 |  |
| YGZrgFsQCjg | 15 | 15 |  |
| YpPCRn5czWM | 15 | 15 | seed |
| ZBJfWvONORw | 15 | 15 | seed |
| ZDPAINbsTI4 | 15 | 15 | seed |
| ZI-r1-3-6X4 | 15 | 15 | seed |
| _nIDNlOp7yo | 15 | 15 |  |
| _yJNVtqOvHw | 5 | 5 | seed |
| _z_60MokjvI | 7 | 7 |  |
| a3tPNl7BsFw | 5 | 5 |  |
| aMMtit2VFTc | 15 | 15 |  |
| anl7snB3TAI | 15 | 14 |  |
| bDl4mWTJrg0 | 8 | 8 | seed |
| b_kWKaTz_aQ | 15 | 15 |  |
| bpUwrIMGh7A | 10 | 10 | seed |
| cIqEpKRczJ4 | 15 | 12 |  |
| cK8Rb-clu6o | 15 | 15 | seed |
| cu_h1trboKk | 11 | 11 | seed |
| dCWA2Gr98ZY | 6 | 6 |  |
| dPOmMMObcn4 | 15 | 15 | seed |
| dQLfd9ogDQ0 | 15 | 15 |  |
| dieLbZ9XLlA | 4 | 4 | seed |
| dnxe6t97xzo | 15 | 14 |  |
| dxr99mLfUXE | 13 | 13 | seed |
| dzAIDEiFBv4 | 12 | 12 | seed |
| e_nKX3QcU04 | 15 | 15 | seed |
| eu0Kym_vs1E | 15 | 15 |  |
| f3yz0WZ8NOs | 12 | 12 | seed |
| fDiJW1OYxac | 12 | 12 | seed |
| fRjwYp_t0OE | 15 | 15 | seed |
| fn7ty-cPv4U | 15 | 15 | seed |
| g4_PTWXDY_I | 5 | 5 |  |
| gA4mDtJlPF0 | 10 | 10 | seed |
| gC26cC9N1VU | 15 | 15 | seed |
| gWTvbXyg2HM | 15 | 15 |  |
| gbXgoKc2NIc | 15 | 15 | seed |
| gky0Lktyt_0 | 10 | 10 | seed |
| hdVnB1t6ZUM | 15 | 15 |  |
| hsnd8zfiROs | 15 | 15 |  |
| ht_vOk4Idcs | 15 | 15 | seed |
| iXvWh-xMSd0 | 15 | 15 |  |
| jBjuY3eZ8mg | 15 | 14 | seed |
| jf2vpi4GG3A | 15 | 15 |  |
| kB3aP3vMEeU | 15 | 15 |  |
| kFRYXXm8ZM0 | 15 | 14 |  |
| lCKDP2gKR_Y | 4 | 4 |  |
| lQxFiUhgj8k | 15 | 15 |  |
| lhumU9wqWls | 15 | 15 | seed |
| ljqBTn1jZbU | 15 | 15 | seed |
| lpFI1yxeok8 | 15 | 15 | seed |
| lqB5CjbU2-k | 15 | 15 | seed |
| lrNPyAyprTk | 5 | 5 |  |
| mO6XiArAjPI | 15 | 15 |  |
| mbx0ZebdPAQ | 15 | 15 |  |
| nh8NLQwcqZU | 15 | 15 |  |
| nn3-xPK-fzw | 15 | 15 | seed |
| nuqjhrjqcd0 | 12 | 11 | seed |
| nxht8qbaWu8 | 13 | 13 |  |
| o_ZZFk-pB3A | 15 | 15 | seed |
| ohupLT98G4c | 15 | 15 |  |
| p9ggFteqtpY | 9 | 9 |  |
| pZIBqmv4By8 | 15 | 15 |  |
| pbuUnesx7Ls | 15 | 15 | seed |
| pfvYK7xbSIQ | 15 | 15 |  |
| pgJ2nT4_pU0 | 15 | 15 | seed |
| q4A9i-RFTvY | 15 | 15 |  |
| qU5OxAgpE1A | 15 | 15 |  |
| qfMVnQ07pcI | 15 | 15 | seed |
| r1KRhB4QeCg | 15 | 15 |  |
| scD84O4afpk | 15 | 15 | seed |
| sw2_HmjgqpI | 3 | 3 |  |
| tTkRZz3P4WM | 15 | 15 | seed |
| tdnrLAzyriA | 15 | 15 | seed |
| u0NvVbKVG4I | 9 | 8 |  |
| uDwKji3EC6M | 6 | 6 |  |
| uXF4jhDcX2A | 15 | 15 | seed |
| uXGwWhOj6P4 | 15 | 15 |  |
| ubFJi2M3AMM | 15 | 15 |  |
| ucEw3C6Zpc8 | 15 | 15 |  |
| ukNZF2Q9ki0 | 14 | 14 |  |
| uzPSqM3nj0A | 15 | 15 | seed |
| v4oUVVlM1JA | 15 | 13 |  |
| v9Oe1avJf2o | 15 | 15 | seed |
| v9n_EbpIWNI | 6 | 6 |  |
| vI4mperPhj0 | 15 | 15 | seed |
| vX_xBFeAIcg | 15 | 15 | seed |
| v_Z-f5KHcNY | 15 | 15 | seed |
| wQX8B7wYip4 | 15 | 15 | seed |
| x7VPW17Rew0 | 3 | 3 | seed |
| xeGZAHe4BAE | 15 | 15 |  |
| xwFVcyt8P_M | 15 | 15 | seed |
| yEly5ZJw5ng | 15 | 14 |  |
| yPCY1PNAYqE | 15 | 15 | seed |
| yYLrp-15Ao0 | 15 | 14 | seed |
| yZ0-We5d0jQ | 15 | 15 |  |
| zPbtp0WtHA4 | 15 | 14 |  |
| zTxLiZaSDbQ | 15 | 15 | seed |
| ziWEgWm4FkQ | 15 | 15 | seed |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): angle.shoulder.dom=28.797, height.wrist.dom=-0.636, height.wrist_mid=-0.608, angle.shoulder.non=32.119, height.wrist.non=-0.595, dist.wrist_width=1.125, angle.elbow.non=121.15, angle.elbow.dom=121.747, angle.ankle.non=112.842, angle.ankle.dom=112.509
- L1 (t=0.469): angle.shoulder.dom=64.109, height.wrist.dom=-0.209, height.wrist_mid=-0.307, angle.shoulder.non=50.943, height.wrist.non=-0.382, dist.wrist_width=1.427, angle.elbow.non=129.072, angle.elbow.dom=128.245, angle.ankle.non=115.632, angle.ankle.dom=114.57
- L2 (t=1.0): angle.shoulder.dom=28.729, height.wrist.dom=-0.627, height.wrist_mid=-0.601, angle.shoulder.non=31.381, height.wrist.non=-0.594, dist.wrist_width=1.135, angle.elbow.non=120.642, angle.elbow.dom=120.426, angle.ankle.non=112.73, angle.ankle.dom=112.896

## Per clip

| clip | attempts used | believable frames | view yaw | angle.shoulder.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -Eu80hGbgVA | 15 | 97% | 42 | 30 | 43 / 64 / 109 |
| -V9fRDexnPM | 15 | 88% | 35 | 34 | 38 / 70 / 85 |
| -XEk39hZzzo | 15 | 97% | 36 | 29 | 41 / 65 / 95 |
| -pfEfb63tZ4 | 15 | 100% | 58 | 26 | 40 / 64 / 94 |
| 0-yol2xtr_E | 15 | 100% | 39 | 17 | 29 / 44 / 89 |
| 0GN5BTx-ups | 15 | 98% | 8 | 25 | 47 / 82 / 102 |
| 0O391AzKX6Q | 15 | 97% | 57 | 35 | 42 / 75 / 96 |
| 0t4qsd6LeJg | 15 | 99% | 8 | 32 | 33 / 66 / 90 |
| 1AY-2Cc3LJU | 15 | 98% | 45 | 16 | 26 / 71 / 95 |
| 1ZVaP90Wxcg | 0 | 93% | 65 |  |  |
| 1l4ZC4047is | 7 | 94% | 3 | 30 | 28 / 57 / 94 |
| 1meRp15WlKQ | 2 | 88% | 5 | 9 | 38 / 60 / 83 |
| 2GYxGHFKD5E | 12 | 100% | 44 | 41 | 42 / 70 / 133 |
| 2J8q7sn4JLc | 15 | 93% | 45 | 29 | 29 / 46 / 62 |
| 2UlY27kxSa4 | 9 | 79% | 27 | 32 | 56 / 76 / 115 |
| 2pr4Xb-_B38 | 8 | 100% | 36 | 35 | 71 / 85 / 123 |
| 2uuk8nZ8W_8 | 9 | 99% | 6 | 33 | 32 / 75 / 91 |
| 33ffZPw9y-c | 6 | 87% | 36 | 17 | 72 / 85 / 100 |
| 3ja7tvQFbQQ | 15 | 82% | 10 | 28 | 29 / 65 / 90 |
| 4PnKAIKuypI | 15 | 100% | 11 | 33 | 41 / 79 / 97 |
| 4ak0XepJYA0 | 5 | 95% | 66 | 42 | 39 / 69 / 94 |
| 4myNhYHhJFY | 4 | 97% | 21 | 22 | 67 / 80 / 90 |
| 4sr1wD_-r1s | 14 | 91% | 15 | 25 | 44 / 94 / 126 |
| 56Tzj_Ie7l0 | 13 | 92% | 11 | 21 | 40 / 62 / 81 |
| 5_vJU8XJOTs | 15 | 100% | 18 | 34 | 32 / 62 / 82 |
| 5arVdubK9Pg | 5 | 97% | 53 | 31 | 52 / 67 / 102 |
| 5mtw69jSZAY | 15 | 99% | 9 | 28 | 30 / 67 / 94 |
| 5t_zAmaON_g | 7 | 90% | 5 | 25 | 27 / 42 / 89 |
| 5wdrcvQQJMg | 15 | 97% | 32 | 27 | 29 / 57 / 89 |
| 6_CAfr0mQ-A | 15 | 100% | 12 | 27 | 38 / 60 / 88 |
| 6pe6DfGtOAM | 11 | 97% | 54 | 30 | 63 / 72 / 106 |
| 75SDa52tY1c | 15 | 99% | 13 | 32 | 30 / 44 / 86 |
| 784lVNd-apU | 1 | 100% | 3 | 20 | 60 / 60 / 60 |
| 7HvlDrYpWEQ | 15 | 100% | 4 | 31 | 36 / 72 / 101 |
| 7xdQDqILnSI | 15 | 99% | 39 | 26 | 19 / 49 / 86 |
| 8VAT46jqJA0 | 15 | 89% | 27 | 20 | 27 / 64 / 87 |
| 8r6F0MgBbz0 | 15 | 99% | 63 | 24 | 33 / 97 / 159 |
| 96i30WAkwUM | 8 | 93% | 11 | 24 | 24 / 37 / 58 |
| 9L9narLQj9M | 15 | 98% | 39 | 31 | 34 / 60 / 84 |
| 9NKtOSzeIIM | 15 | 98% | 46 | 26 | 28 / 43 / 100 |
| 9O_3QibgbRE | 15 | 99% | 10 | 36 | 64 / 78 / 97 |
| 9v3NfhfJD5Q | 12 | 99% | 37 | 23 | 21 / 46 / 85 |
| A2CdXZ-Ct-c | 15 | 90% | 64 | 33 | 46 / 91 / 100 |
| A9e-LtL7IaI | 15 | 100% | 38 | 22 | 35 / 51 / 104 |
| AAIc7Li2WbA | 15 | 100% | 22 | 45 | 23 / 32 / 106 |
| AEn2acwAQ7Y | 1 | 100% | 40 | 18 | 23 / 23 / 23 |
| AWs09rEo_v0 | 7 | 100% | 32 | 19 | 23 / 55 / 76 |
| Ai1wvW13HOc | 13 | 79% | 20 | 20 | 30 / 63 / 107 |
| Aifm8Ssxibw | 14 | 99% | 18 | 24 | 26 / 64 / 94 |
| Ap0qSdyx9H4 | 7 | 75% | 5 | 30 | 34 / 72 / 101 |
| Aq0fU8nnSOs | 7 | 81% | 7 | 25 | 29 / 46 / 74 |
| BPLFRhnkziY | 15 | 97% | 30 | 29 | 34 / 54 / 87 |
| Bm8QljKE9MM | 1 | 100% | 56 | 22 | 54 / 54 / 54 |
| BnmVSa9dWz0 | 15 | 100% | 9 | 20 | 26 / 63 / 74 |
| Bun_Ouz5-bs | 15 | 100% | 50 | 27 | 32 / 49 / 62 |
| BwYS96dRFM0 | 15 | 100% | 10 | 26 | 30 / 43 / 78 |
| CxLVAuZLAMs | 5 | 100% | 11 | 24 | 29 / 37 / 56 |
| D0IQYtGQHKE | 15 | 98% | 53 | 33 | 42 / 67 / 107 |
| D6C0g7zPaGk | 15 | 99% | 28 | 28 | 67 / 78 / 103 |
| DA8sM2ilEsc | 15 | 97% | 35 | 34 | 41 / 74 / 100 |
| DiXCMYwvw-8 | 15 | 100% | 6 | 31 | 30 / 73 / 93 |
| DivLvT5R_JA | 15 | 98% | 11 | 19 | 57 / 79 / 103 |
| E0g3LNBhJeU | 15 | 100% | 48 | 35 | 29 / 90 / 104 |
| E5F6qmT2XCk | 11 | 89% | 15 | 35 | 27 / 39 / 105 |
| EEHaZ4PrUFI | 15 | 94% | 9 | 23 | 44 / 68 / 88 |
| EZuZTjn8I08 | 13 | 96% | 46 | 27 | 56 / 80 / 114 |
| F-yNBm8loyk | 7 | 98% | 28 | 21 | 26 / 50 / 87 |
| F3qUPNxUGgo | 15 | 98% | 16 | 20 | 43 / 73 / 117 |
| FKRYw1VU9Qk | 0 | 82% | 25 |  |  |
| FssCtZEWBH4 | 15 | 99% | 12 | 29 | 33 / 56 / 90 |
| FuinI7uw8hQ | 9 | 100% | 28 | 25 | 23 / 60 / 85 |
| GgvWLeest9I | 3 | 100% | 37 | 17 | 43 / 52 / 75 |
| GztttGCA1pY | 14 | 99% | 22 | 41 | 27 / 61 / 92 |
| Hn_xHDmR2zM | 0 | 89% | 56 |  |  |
| IWj5qhSHnL0 | 10 | 93% | 11 | 37 | 44 / 65 / 89 |
| Ib7DmMuqPiE | 15 | 99% | 48 | 25 | 29 / 41 / 115 |
| IpoTbr5XINI | 14 | 98% | 8 | 39 | 46 / 84 / 126 |
| J929_RFF32E | 15 | 98% | 41 | 37 | 39 / 79 / 106 |
| JQXdqMXUfJM | 15 | 99% | 32 | 28 | 34 / 70 / 90 |
| KAK5a9Qs12w | 15 | 100% | 6 | 28 | 40 / 53 / 103 |
| KAyZ1uH5plI | 15 | 98% | 7 | 39 | 26 / 70 / 92 |
| K_bqRpOU6rA | 4 | 99% | 57 | 69 | 29 / 59 / 95 |
| KcHbjatv8yU | 14 | 100% | 40 | 40 | 43 / 77 / 102 |
| LCKk0N4p2_A | 14 | 98% | 8 | 36 | 26 / 54 / 76 |
| LCtYngOwfsw | 15 | 100% | 6 | 28 | 19 / 60 / 93 |
| LSqVp9QHERQ | 9 | 98% | 28 | 29 | 32 / 87 / 111 |
| Le0dgmeL-LE | 15 | 97% | 10 | 30 | 43 / 72 / 84 |
| M5mhUjZd22s | 11 | 99% | 42 | 28 | 38 / 58 / 98 |
| NaP7RiVXz2E | 10 | 98% | 8 | 26 | 28 / 47 / 53 |
| NfyrO92yMTc | 9 | 100% | 46 | 42 | 36 / 83 / 94 |
| NlGP2PaZ5HA | 10 | 92% | 44 | 32 | 44 / 68 / 126 |
| NuepcSzH44o | 12 | 100% | 8 | 26 | 34 / 61 / 105 |
| O21f-6kaIwk | 15 | 92% | 37 | 34 | 28 / 67 / 112 |
| OBZaRtH7OQY | 15 | 94% | 11 | 19 | 28 / 66 / 87 |
| OMvRlIlLa_8 | 15 | 100% | 44 | 21 | 33 / 59 / 86 |
| OSkioIwXEYM | 15 | 97% | 51 | 23 | 41 / 82 / 111 |
| OaBuo8jBgJU | 6 | 97% | 17 | 27 | 21 / 33 / 55 |
| Paw1e6sIJkM | 6 | 92% | 25 | 46 | 59 / 79 / 86 |
| PeEkclg6SKE | 15 | 96% | 11 | 34 | 47 / 63 / 97 |
| PkiZmPZBdw8 | 14 | 100% | 7 | 29 | 36 / 55 / 67 |
| PsPQWDKw7Zo | 11 | 100% | 6 | 29 | 37 / 63 / 88 |
| Pv5kymKGQEA | 15 | 99% | 16 | 31 | 24 / 53 / 79 |
| QAcBgVZheDo | 2 | 100% | 22 | 41 | 84 / 90 / 95 |
| QQTpd0z9C1k | 15 | 99% | 15 | 19 | 24 / 55 / 83 |
| QrDWirGkue8 | 6 | 86% | 49 | 39 | 21 / 35 / 68 |
| RVnHEcORqqI | 15 | 96% | 32 | 43 | 37 / 71 / 92 |
| RXsu2NlL2kE | 9 | 93% | 24 | 27 | 25 / 39 / 80 |
| RwEF_Mty7Ps | 15 | 99% | 50 | 18 | 35 / 49 / 73 |
| S5N0ASybB7g | 6 | 97% | 19 | 40 | 48 / 70 / 92 |
| SHB7xsIPv5E | 15 | 95% | 52 | 17 | 29 / 46 / 99 |
| Sb2Cm_KmwPU | 15 | 100% | 15 | 22 | 32 / 99 / 122 |
| T1FuyfTHsmQ | 15 | 94% | 20 | 39 | 35 / 70 / 100 |
| TeYKveJ1NS4 | 15 | 97% | 14 | 30 | 40 / 54 / 101 |
| TgCZr6aRa1Q | 15 | 94% | 32 | 35 | 59 / 99 / 107 |
| U2dKyI_2lWQ | 9 | 100% | 4 | 27 | 51 / 73 / 108 |
| UaPuZ5HIU1U | 15 | 95% | 10 | 30 | 28 / 52 / 86 |
| UdLFwBicq8E | 8 | 97% | 12 | 29 | 30 / 49 / 100 |
| UnEUw4jVrEY | 15 | 100% | 8 | 41 | 49 / 105 / 114 |
| V26ifGuICIE | 15 | 95% | 14 | 40 | 50 / 78 / 92 |
| V9QMvLauAls | 8 | 89% | 37 | 42 | 46 / 83 / 100 |
| VC4_qolv6mk | 9 | 100% | 44 | 42 | 88 / 105 / 108 |
| VLNuqgjf4-4 | 2 | 100% | 6 | 38 | 35 / 36 / 37 |
| W-v8U7K0_m0 | 15 | 100% | 5 | 29 | 27 / 49 / 70 |
| We-nHWaJ2Ig | 15 | 99% | 11 | 36 | 34 / 54 / 77 |
| WlQLN5mJ7Xg | 15 | 91% | 9 | 29 | 52 / 68 / 87 |
| XA34mJgU0ks | 15 | 100% | 10 | 25 | 21 / 59 / 76 |
| XVs_p57iNLE | 15 | 99% | 59 | 32 | 26 / 53 / 64 |
| X_eg2H8Fa3Q | 15 | 93% | 6 | 34 | 44 / 81 / 102 |
| XeJyEfMVp5E | 15 | 98% | 13 | 33 | 42 / 77 / 97 |
| YGZrgFsQCjg | 15 | 91% | 39 | 28 | 33 / 54 / 84 |
| YpPCRn5czWM | 15 | 100% | 5 | 26 | 36 / 60 / 83 |
| ZBJfWvONORw | 15 | 94% | 14 | 24 | 21 / 41 / 81 |
| ZDPAINbsTI4 | 15 | 98% | 9 | 23 | 12 / 40 / 73 |
| ZI-r1-3-6X4 | 15 | 96% | 9 | 25 | 21 / 40 / 69 |
| Z_ykU7AKpiI | 0 | 79% | 8 |  |  |
| _nIDNlOp7yo | 15 | 94% | 52 | 28 | 22 / 67 / 103 |
| _yJNVtqOvHw | 5 | 90% | 61 | 28 | 47 / 69 / 86 |
| _z_60MokjvI | 7 | 75% | 11 | 24 | 47 / 102 / 123 |
| a3tPNl7BsFw | 5 | 97% | 51 | 30 | 40 / 49 / 109 |
| aMMtit2VFTc | 15 | 93% | 55 | 33 | 38 / 67 / 101 |
| anl7snB3TAI | 14 | 96% | 55 | 18 | 34 / 68 / 105 |
| bDl4mWTJrg0 | 8 | 99% | 55 | 33 | 28 / 50 / 57 |
| b_kWKaTz_aQ | 15 | 98% | 9 | 30 | 31 / 59 / 100 |
| bpUwrIMGh7A | 10 | 97% | 10 | 27 | 23 / 28 / 67 |
| cIqEpKRczJ4 | 12 | 98% | 54 | 41 | 59 / 73 / 86 |
| cK8Rb-clu6o | 15 | 98% | 8 | 21 | 27 / 84 / 114 |
| cu_h1trboKk | 11 | 100% | 8 | 18 | 35 / 58 / 73 |
| dCWA2Gr98ZY | 6 | 100% | 62 | 18 | 51 / 73 / 97 |
| dPOmMMObcn4 | 15 | 100% | 19 | 23 | 25 / 52 / 90 |
| dQLfd9ogDQ0 | 15 | 88% | 13 | 15 | 18 / 35 / 98 |
| dieLbZ9XLlA | 4 | 99% | 29 | 41 | 46 / 54 / 85 |
| dnxe6t97xzo | 14 | 100% | 45 | 28 | 45 / 78 / 87 |
| dxr99mLfUXE | 13 | 100% | 8 | 25 | 27 / 50 / 62 |
| dzAIDEiFBv4 | 12 | 98% | 5 | 22 | 27 / 37 / 68 |
| e_nKX3QcU04 | 15 | 91% | 10 | 36 | 43 / 64 / 101 |
| eu0Kym_vs1E | 15 | 84% | 49 | 33 | 42 / 53 / 83 |
| f3yz0WZ8NOs | 12 | 100% | 6 | 23 | 25 / 36 / 79 |
| fDiJW1OYxac | 12 | 98% | 13 | 32 | 34 / 53 / 70 |
| fRjwYp_t0OE | 15 | 98% | 10 | 45 | 38 / 79 / 91 |
| fgFocZOAxog | 0 | 99% | 7 |  |  |
| fn7ty-cPv4U | 15 | 98% | 8 | 23 | 24 / 57 / 74 |
| g4_PTWXDY_I | 5 | 99% | 35 | 42 | 65 / 68 / 108 |
| gA4mDtJlPF0 | 10 | 100% | 10 | 16 | 22 / 56 / 120 |
| gC26cC9N1VU | 15 | 98% | 13 | 30 | 26 / 51 / 91 |
| gWTvbXyg2HM | 15 | 97% | 51 | 22 | 64 / 82 / 109 |
| gbXgoKc2NIc | 15 | 100% | 14 | 36 | 47 / 70 / 92 |
| gky0Lktyt_0 | 10 | 95% | 15 | 25 | 52 / 58 / 72 |
| hdVnB1t6ZUM | 15 | 97% | 12 | 24 | 27 / 62 / 83 |
| hsnd8zfiROs | 15 | 91% | 32 | 34 | 36 / 64 / 74 |
| ht_vOk4Idcs | 15 | 100% | 9 | 32 | 23 / 43 / 88 |
| iXvWh-xMSd0 | 15 | 97% | 16 | 36 | 32 / 58 / 94 |
| jBjuY3eZ8mg | 14 | 98% | 43 | 16 | 21 / 52 / 81 |
| jf2vpi4GG3A | 15 | 95% | 15 | 26 | 54 / 90 / 101 |
| kB3aP3vMEeU | 15 | 78% | 12 | 24 | 19 / 57 / 85 |
| kFRYXXm8ZM0 | 14 | 100% | 35 | 53 | 35 / 97 / 110 |
| lCKDP2gKR_Y | 4 | 93% | 24 | 55 | 48 / 56 / 65 |
| lDKV9j6VX4Y | 0 | 89% | 35 |  |  |
| lQxFiUhgj8k | 15 | 91% | 25 | 49 | 80 / 96 / 115 |
| lhumU9wqWls | 15 | 92% | 35 | 38 | 46 / 62 / 96 |
| ljqBTn1jZbU | 15 | 85% | 8 | 32 | 38 / 67 / 95 |
| lpFI1yxeok8 | 15 | 99% | 9 | 27 | 27 / 59 / 85 |
| lqB5CjbU2-k | 15 | 94% | 34 | 26 | 15 / 46 / 59 |
| lrNPyAyprTk | 5 | 99% | 40 | 28 | 45 / 86 / 100 |
| mO6XiArAjPI | 15 | 99% | 55 | 34 | 64 / 92 / 101 |
| mbx0ZebdPAQ | 15 | 100% | 28 | 42 | 28 / 65 / 122 |
| mfyu-kW4OvQ | 1 | 97% | 4 | 30 | 71 / 71 / 71 |
| nh8NLQwcqZU | 15 | 100% | 44 | 31 | 35 / 65 / 106 |
| nn3-xPK-fzw | 15 | 96% | 18 | 19 | 43 / 56 / 100 |
| nuqjhrjqcd0 | 11 | 94% | 54 | 40 | 43 / 57 / 68 |
| nxht8qbaWu8 | 13 | 98% | 55 | 22 | 25 / 39 / 87 |
| o_ZZFk-pB3A | 15 | 100% | 34 | 28 | 45 / 82 / 93 |
| ohupLT98G4c | 15 | 97% | 40 | 37 | 37 / 66 / 91 |
| p9ggFteqtpY | 9 | 96% | 8 | 24 | 19 / 56 / 86 |
| pZIBqmv4By8 | 15 | 78% | 6 | 25 | 36 / 65 / 82 |
| pbuUnesx7Ls | 15 | 100% | 10 | 32 | 30 / 70 / 91 |
| peG7SSmzgvE | 0 | 100% | 13 |  |  |
| pfvYK7xbSIQ | 15 | 99% | 23 | 36 | 50 / 67 / 88 |
| pgJ2nT4_pU0 | 15 | 99% | 14 | 30 | 39 / 69 / 87 |
| q4A9i-RFTvY | 15 | 94% | 17 | 26 | 35 / 82 / 105 |
| qU5OxAgpE1A | 15 | 99% | 35 | 33 | 32 / 59 / 94 |
| qfMVnQ07pcI | 15 | 95% | 13 | 32 | 27 / 48 / 82 |
| r1KRhB4QeCg | 15 | 99% | 55 | 26 | 28 / 55 / 92 |
| scD84O4afpk | 15 | 100% | 12 | 31 | 23 / 51 / 95 |
| sw2_HmjgqpI | 3 | 96% | 5 | 32 | 74 / 83 / 93 |
| tTkRZz3P4WM | 15 | 99% | 13 | 27 | 23 / 57 / 101 |
| tdnrLAzyriA | 15 | 99% | 35 | 20 | 39 / 66 / 90 |
| u0NvVbKVG4I | 8 | 100% | 55 | 21 | 66 / 101 / 112 |
| uDwKji3EC6M | 6 | 99% | 53 | 40 | 20 / 60 / 96 |
| uXF4jhDcX2A | 15 | 93% | 5 | 21 | 27 / 66 / 111 |
| uXGwWhOj6P4 | 15 | 78% | 48 | 31 | 42 / 97 / 112 |
| ubFJi2M3AMM | 15 | 91% | 48 | 30 | 46 / 71 / 98 |
| ucEw3C6Zpc8 | 15 | 85% | 7 | 46 | 26 / 79 / 109 |
| ukNZF2Q9ki0 | 14 | 97% | 37 | 28 | 45 / 73 / 121 |
| uzPSqM3nj0A | 15 | 98% | 13 | 32 | 28 / 60 / 87 |
| v4oUVVlM1JA | 13 | 100% | 22 | 51 | 54 / 82 / 98 |
| v9Oe1avJf2o | 15 | 93% | 11 | 29 | 33 / 60 / 76 |
| v9n_EbpIWNI | 6 | 99% | 38 | 42 | 74 / 83 / 95 |
| vI4mperPhj0 | 15 | 92% | 11 | 21 | 30 / 56 / 87 |
| vX_xBFeAIcg | 15 | 97% | 28 | 22 | 25 / 50 / 99 |
| v_Z-f5KHcNY | 15 | 100% | 6 | 21 | 38 / 69 / 103 |
| wQX8B7wYip4 | 15 | 96% | 8 | 24 | 33 / 86 / 108 |
| x7VPW17Rew0 | 3 | 92% | 4 | 28 | 45 / 52 / 53 |
| xeGZAHe4BAE | 15 | 95% | 31 | 33 | 64 / 99 / 112 |
| xwFVcyt8P_M | 15 | 99% | 12 | 21 | 27 / 42 / 79 |
| yEly5ZJw5ng | 14 | 97% | 49 | 31 | 74 / 85 / 100 |
| yPCY1PNAYqE | 15 | 94% | 40 | 38 | 42 / 70 / 84 |
| yYLrp-15Ao0 | 14 | 93% | 24 | 22 | 23 / 41 / 83 |
| yZ0-We5d0jQ | 15 | 99% | 7 | 31 | 34 / 75 / 94 |
| zPbtp0WtHA4 | 14 | 97% | 13 | 35 | 26 / 54 / 86 |
| zTxLiZaSDbQ | 15 | 95% | 41 | 16 | 21 / 39 / 72 |
| ziWEgWm4FkQ | 15 | 88% | 6 | 29 | 27 / 64 / 74 |

## Vocabulary proposals

- measurement: racket_face_angle_at_contact (Coaches name a wrong racket face angle (too closed or too open) but no registered feature shows the racket.)
- trackable: ball (Needed to judge late preparation, spacing to the ball, contact point and where the ball lands.)
- feature: takeback_peak_marker (The take-back (arm-only take-back, size of the take-back, loop or straight path) happens inside the first phase, with no landmark at its peak, so a test at a phase boundary cannot show it.)
- feature: racket_or_wrist_path_shape (Looped versus straight take-back and the arm bending or dropping twice cannot be seen with the current features.)
- measurement: time_from_ready_to_contact (Would let late or mistimed preparation be tested directly, with no ball tracking.)
