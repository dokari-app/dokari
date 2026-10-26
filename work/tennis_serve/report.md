# Factory report: tennis_serve

Clips found: 281 (usable for attempts: 82). Attempts: 402.
Confidence tier: **low**. Checks: 9 pass, 0 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [PASS] 4. recognition: recall 0.98 (leave-one-clip-out), false accepts 0.01 (shape alone 0.24), by view {'front/back (<30)': 0.9722222222222222, 'oblique (30-60)': 0.9793103448275862, 'side (>60)': 0.975609756097561}
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [n/a ] 6. discrimination: no objective has enough labelled good and faulty examples (3 of each), so no target range is validated; 6 of 6 come from good-form demonstrations, 0 from everyday footage (what is typical, not what is good)
- [PASS] 7. outcome links: 4 links, 4 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.78 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 5 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **low_elbow** (high, agreed by 5 of 5 runs): Reach the trophy position with the hitting upper arm raised out to about shoulder level and the elbow bent, not tucked down.. Target: angle.shoulder.dom between 6.3027 and 141.0068 at L1. Wrong if below: The hitting elbow stays tucked low and the arm hangs near the body, with no trophy position or 90-degree set. (high); above: The hitting arm is lifted unusually high or straightened early at the trophy position. (low). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.
- 2. **toss_arm_misused** (medium, agreed by 5 of 5 runs): Lift the tossing arm smoothly up, extended along the line of the toss, and keep it up until the hit.. Target: angle.shoulder.non at least 38.8922 at L1. Wrong if below: The tossing arm drops early or does not rise far, which loses balance and a consistent toss. (medium). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.
- 3. **toss_height_wrong** (medium, agreed by 5 of 5 runs): Toss the ball high enough to reach full height on contact without waiting, with the tossing hand released high.. Target: height.wrist.non between -0.5963 and 1.7085 at L1. Wrong if below: The toss is released low and the ball is too low, so contact is cramped or rushed. (medium); above: The toss goes too high and the player waits and hitches. (low). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.
- 4. **leg_timing_rhythm** (low, agreed by 5 of 5 runs): Bend the knees smoothly in the loading phase so the legs can drive up into the hit.. Target: angle.knee.dom at least 95.1462 at L1. Wrong if below: The knees bend very deep or too early, so the player sinks and loses rhythm. (low). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.
- 5. **open_up_too_early** (medium, agreed by 5 of 5 runs): Stay sideways, with the shoulders turned away from the net, through the loading phase and then rotate into the ball.. Target: angle.shoulder_hip_twist between -15.8265 and 30.1738 at L1. Wrong if below: The shoulders and stance face the net early, which loses the coil. (medium); above: The shoulders are over-rotated relative to the hips. (low). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.
- 6. **poor_finish_and_recovery** (low, agreed by 5 of 5 runs): Finish with the tossing arm folded in toward the body and recover in balance after the swing.. Target: angle.shoulder.non at most 134.4716 at L2. Wrong if above: The tossing arm is still flung out or back and the player is off balance at the end, not recovered. (low). Range from good-form demonstrations (134 attempts in 29 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **wrong_grip** (form; 4 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection to see grip. Coaches disagree: Sources 3, 5 and 6 say continental; source 10 recommends an eastern grip, and source 9 allows eastern for beginners.
- **fist_grip** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to see finger spacing on handle.
- **flawed_toss_release** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (toss_height_wrong).
- **leg_timing_rhythm** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (leg_timing_rhythm). Coaches disagree: Source 3 says toss then bend; source 6 says bend as the ball leaves the hand; source 9 says bend as the ball rises.
- **open_up_too_early** (form; 3 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (open_up_too_early).
- **toss_height_wrong** (form; 3 of 12, some): measured by the camera (toss_height_wrong). Coaches disagree: Source 10 says hit at the apex; source 6 says contact just as the ball begins to drop.
- **chopping_low_contact** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket and ball detection to see which part of strings hits the ball.
- **contact_posture** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.trunk_lean, angle.shoulder.dom, height.wrist.dom at contact.
- **forearm_pronation_not_used** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket orientation to see forearm rotation. Coaches disagree: Sources 0 and 2 call shoulder internal rotation the main power source; source 4 says the forearm is the last link that hits the ball.
- **low_elbow** (safety; 2 of 12, some): measured by the camera (low_elbow).
- **poor_finish_and_recovery** (form; 2 of 12, some): measured by the camera (poor_finish_and_recovery). Coaches disagree: Source 3 says serves with the arm held back can still be good, just not your best.
- **tight_stiff_arm** (form; 2 of 12, some): a body feature can show it but no objective tests it (no agreed target): angle.elbow.dom through the swing; stiffness itself is partly feel.
- **toss_arm_misused** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (toss_arm_misused).
- **waiters_tray** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection to see palm and strings orientation.
- **wrist_powered** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection to see racket face and wrist action. Coaches disagree: Source 10 teaches a wrist snap to bring the ball down; source 2 says wrist power is small.
- **wrong_sequence** (form; 2 of 12, some): would need a new body feature: timing of peak velocity across hip, trunk, shoulder, arm segments, plus spine arch measure. Coaches disagree: Source 2 says drive the legs first; source 11 says lead with the hand and let the legs follow.
- **abbreviated_serve_shoulder** (form; 1 of 12, single): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor. Coaches disagree: Source 9 also praises the abbreviated serve as compact, with lots of snap and power.
- **dropping_body_on_snap** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): angle.trunk_lean and height.hip at contact.
- **power_position_too_early** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (low_elbow).
- **slice_contact_wrong** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball and racket detection to see contact point on ball.

Good form, as coaches give it:

- Use a continental-style grip with a small gap between index finger and hand, not a fist. (4 of 12)
- Stand sideways with the front shoulder toward the target and keep shoulders closed as long as possible. (4 of 12)
- Tilt the shoulders with the tossing shoulder higher (trophy position), then swap shoulders like a seesaw. (4 of 12)
- Time the leg bend with the toss, then drive up into contact. (4 of 12)
- Make contact high, in front and slightly to the side so the arm is extended and the forearm can pronate. (4 of 12)
- Place the toss rather than throw it: ball in the fingers, straight loose arm, still wrist, release near eye level. (3 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **loaded_arm_long_lever** (coaching_consensus, 3 of 3 runs; explains low_elbow, power_position_too_early, tight_stiff_arm): Raising the hitting elbow out to about shoulder height with the arm bent sets the racket up so it can drop behind and then be swung up and out. A tucked-down elbow skips this set position and leaves less room to build racket speed. Cue handle: .
- **toss_sets_the_timing** (contested, 3 of 3 runs; explains toss_arm_misused, toss_height_wrong, flawed_toss_release): A smooth, extended tossing arm that releases the ball high gives a repeatable ball path. The ball then arrives at the contact point at the moment the body is ready to hit, so you do not wait or hitch. How high exactly to hit (at the apex or as it starts to drop) is a matter of preference among coaches. Cue handle: Send the ball up smoothly on a steady line so it peaks where you want to meet it.. Competing views: Source 10: hit the ball at the apex of the toss.; Source 6: make contact just as the ball begins to drop..
- **legs_load_then_drive** (contested, 3 of 3 runs; explains leg_timing_rhythm, wrong_sequence): A smooth knee bend stores energy that the legs release upward into the swing, and it works best when it is timed with the toss. Coaches disagree on exactly when to start the bend, and a rhythm forced on a player can disrupt it. Cue handle: Sink smoothly and spring up in one flowing rhythm.. Competing views: Source 3: toss first, then bend the knees.; Source 6: bend as the ball leaves the hand.; Source 9: bend as the ball rises..
- **turn_then_unwind** (coaching_consensus, 3 of 3 runs; explains open_up_too_early, wrong_sequence, contact_posture): Staying sideways while loading stores rotation in the trunk. Turning into the ball afterwards passes force from the ground through the legs and trunk to the arm. Opening early uses up that stored turn before contact. Cue handle: Hold the coil, then release it all together at the ball..
- **balanced_finish** (contested, 2 of 3 runs; explains poor_finish_and_recovery): Folding the tossing arm in and finishing across the body keeps the centre of mass under control as the swing slows. This leaves you balanced and ready for the next shot. Cue handle: Finish tucked and steady so you are ready to move straight away.. Competing views: Source 3: serves with the tossing arm held back can still be good, just not your best..

## Check against labelled mistake videos (15 videos, 32 attempts, 11 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| tight_stiff_arm | 3 / 1 | 0 / 0 |
| flawed_toss_release | 0 / 0 | 2 / 1 |
| low_elbow | 0 / 0 | 6 / 2 |
| open_up_too_early | 0 / 0 | 1 / 1 |
| poor_finish_and_recovery | 0 / 0 | 2 / 1 |
| toss_arm_misused | 0 / 0 | 3 / 2 |
| wrong_grip | 0 / 0 | 5 / 2 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| low_elbow | 6 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| toss_arm_misused | 3 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| toss_height_wrong | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| leg_timing_rhythm | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| open_up_too_early | 1 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| poor_finish_and_recovery | 2 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.wrist.non, height.wrist.dom, angle.shoulder.non, angle.shoulder.dom, angle.elbow.dom, dist.wrist_width
Attempts found as: height.wrist.non rises (to at least 0.6), then height.wrist.dom rises (to at least 0.7). Typical size of the last event 1.796, lasting 3.56 s; smaller ones (below 0.718) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 68 clear attempts in 37 of 240 clips after 4 round(s) of searching; TARGET NOT REACHED: this entry rests on little footage.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 38 | 153 | mistakes 1, mixed 152 |
| coach_demo | 38 | 124 | good_form 112, mixed 12 |
| pro_footage | 16 | 57 | good_form 43, mixed 14 |
| instruction_talk | 12 | 55 | good_form 12, unknown 43 |
| other | 10 | 20 | good_form 3, unknown 17 |
| unrated | 3 | 20 | unknown 20 |
| practice_session | 4 | 12 | unknown 12 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| low_elbow | 13% (29 clips) | 10% (53 clips) | no difference: everyone is inside, or this measure does not separate them |
| toss_arm_misused | 10% (29 clips) | 5% (53 clips) | no difference: everyone is inside, or this measure does not separate them |
| toss_height_wrong | 12% (29 clips) | 6% (53 clips) | demos depart more: doubtful |
| leg_timing_rhythm | 6% (29 clips) | 1% (53 clips) | demos depart more: doubtful |
| open_up_too_early | 6% (29 clips) | 4% (53 clips) | no difference: everyone is inside, or this measure does not separate them |
| poor_finish_and_recovery | 10% (29 clips) | 7% (53 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- toss_and_load: L0 to L1
- swing_and_finish: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip JEsU4nTozSA: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 403 of 408 attempts (tolerance 2.497). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (-7qtgLZ95VU, -_Q1aI1Em_M, 16KptrgtdDM, 1ugRPNu765Q, 3wirS8eqVYI, 5aJtdopjCyg, 6PR-QQdUa0g, 6arnqtt0eT8, 72YkMkLdkFo, 9SXaq_cwvAI, BOaF8rDF3gU, BUn0J2SeHwM, Bcqi_M9aPmg, CgEDaaV-Ba8, FQGEUsAqEgs, GumlybS_rBo, IXgxVgFDyxY, Kkj6K29A8-s, L7hxyUCHo-g, MUg4UjW_JL4, Np3ex7Uo08M, Pmu29Uet23A, S10nJN2Y1og, UJ3xNfw7G3Y, Um5q7Lx107k, VIFLw3w1XJs, Va9uJMa_QtQ, XQYtS5u3V6Y, azpOGkeEgE0, dRV_CBoj1gg, fJ_a2RLdFCM, jVANF0nbCUA, jtmJ1d0fTbA, lVOB4diuOHA, mOlf4pcvUxM, oDs8zNGc1no, pS8KuAM9G8k, qwlkRHQiUnM, tH2fowVHLUQ, vD0wO3tq6BM, xnTPbWmk8eI).

| clip | attempts found | kept | note |
|---|---|---|---|
| -7qtgLZ95VU | 2 | 2 | seed |
| -V9EovSX8OI | 10 | 10 |  |
| -_Q1aI1Em_M | 2 | 2 | seed |
| 0tP2pmXd9Gk | 14 | 14 |  |
| 16KptrgtdDM | 4 | 4 | seed |
| 1ugRPNu765Q | 4 | 4 | seed |
| 3wirS8eqVYI | 2 | 2 | seed |
| 4JWK1h7NMdA | 4 | 4 |  |
| 4osbfneXwXI | 3 | 3 |  |
| 5VaZ9AXBKjM | 5 | 5 |  |
| 5aJtdopjCyg | 2 | 2 | seed |
| 6PR-QQdUa0g | 3 | 3 | seed |
| 6arnqtt0eT8 | 10 | 10 | seed |
| 72YkMkLdkFo | 6 | 6 | seed |
| 7kEZTgkmqfg | 3 | 3 |  |
| 85brcxUjxAI | 3 | 3 |  |
| 8N5O1t3UZkE | 3 | 3 |  |
| 9SXaq_cwvAI | 12 | 12 | seed |
| 9imKaY0myyI | 4 | 4 |  |
| AKnXtyVrcz4 | 2 | 2 |  |
| B2uDfNd9QSo | 11 | 11 |  |
| BOaF8rDF3gU | 10 | 10 | seed |
| BUn0J2SeHwM | 8 | 7 | seed |
| Bcqi_M9aPmg | 3 | 3 | seed |
| CgEDaaV-Ba8 | 15 | 15 | seed |
| DLLz7uPta_g | 2 | 2 |  |
| Da5zIBPzU8Q | 7 | 7 |  |
| EbhB3HpmMmA | 2 | 2 |  |
| FKtqaKjZVPs | 4 | 4 |  |
| FMxUuvb9d1Q | 4 | 4 |  |
| FQGEUsAqEgs | 5 | 5 | seed |
| FlZ1yNj1T3A | 5 | 4 |  |
| GumlybS_rBo | 3 | 3 | seed |
| IXgxVgFDyxY | 5 | 5 | seed |
| JB9PsFq5oe8 | 3 | 3 |  |
| JEsU4nTozSA | 4 | 4 |  |
| JXXH3bvKjA4 | 3 | 3 |  |
| KJY-qILhlWk | 3 | 3 |  |
| Kkj6K29A8-s | 7 | 7 | seed |
| L7hxyUCHo-g | 9 | 9 | seed |
| Lq5ZF2VfEGk | 8 | 8 |  |
| MUg4UjW_JL4 | 7 | 7 | seed |
| Np3ex7Uo08M | 5 | 5 | seed |
| Pmu29Uet23A | 8 | 7 | seed |
| RWP2a7QmtHw | 3 | 3 |  |
| S10nJN2Y1og | 6 | 6 | seed |
| U39OzzOxaMM | 2 | 2 |  |
| UJ3xNfw7G3Y | 9 | 9 | seed |
| UOf0sV68-O4 | 3 | 3 |  |
| Um5q7Lx107k | 6 | 6 | seed |
| VIFLw3w1XJs | 11 | 11 | seed |
| Va9uJMa_QtQ | 4 | 4 | seed |
| XQYtS5u3V6Y | 3 | 3 | seed |
| Y3j0idcVtDs | 3 | 3 |  |
| azpOGkeEgE0 | 2 | 2 | seed |
| c-F_OhLGPMQ | 2 | 2 |  |
| cdS8QlI7qF4 | 3 | 3 |  |
| d0Hg3t_43tI | 3 | 3 |  |
| dRV_CBoj1gg | 2 | 2 | seed |
| eYaIOC8KMlk | 2 | 2 |  |
| fJ_a2RLdFCM | 10 | 10 | seed |
| fhn2ANDE4kA | 8 | 8 |  |
| jVANF0nbCUA | 5 | 5 | seed |
| jjra4H3WO6Y | 2 | 2 |  |
| jtmJ1d0fTbA | 4 | 4 | seed |
| lVOB4diuOHA | 3 | 3 | seed |
| mOlf4pcvUxM | 5 | 5 | seed |
| nbPFqP-kIuc | 7 | 7 |  |
| oDs8zNGc1no | 3 | 3 | seed |
| pS8KuAM9G8k | 4 | 4 | seed |
| quUydRpf96Q | 4 | 4 |  |
| qwlkRHQiUnM | 15 | 14 | seed |
| rTXgMbyjMuU | 2 | 2 |  |
| rcCymL9uzs8 | 4 | 4 |  |
| s-rOCECttUo | 2 | 2 |  |
| tH2fowVHLUQ | 2 | 2 | seed |
| uH1894jAvIA | 2 | 2 |  |
| vD0wO3tq6BM | 3 | 3 | seed |
| w7n5p2Dt4J4 | 3 | 3 |  |
| xDqrsO42uAQ | 2 | 2 |  |
| xJDBaSJuums | 9 | 9 |  |
| xLj6KEqkWJs | 2 | 1 |  |
| xnTPbWmk8eI | 4 | 4 | seed |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist.non=-0.54, angle.shoulder.non=46.902, height.wrist.dom=-0.622, angle.shoulder.dom=39.341, height.wrist_mid=-0.466, reach.wrist.non=0.911, angle.elbow.non=144.622, reach.wrist.dom=0.896, angle.elbow.dom=142.642, dist.wrist_width=1.71
- L1 (t=0.388): height.wrist.non=0.832, angle.shoulder.non=139.54, height.wrist.dom=0.024, angle.shoulder.dom=84.938, height.wrist_mid=0.449, reach.wrist.non=0.954, angle.elbow.non=155.606, reach.wrist.dom=0.75, angle.elbow.dom=128.412, dist.wrist_width=2.473
- L2 (t=1.0): height.wrist.non=-0.592, angle.shoulder.non=38.416, height.wrist.dom=-0.632, angle.shoulder.dom=40.414, height.wrist_mid=-0.582, reach.wrist.non=0.823, angle.elbow.non=135.09, reach.wrist.dom=0.857, angle.elbow.dom=140.002, dist.wrist_width=1.559

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -7qtgLZ95VU | 2 | 97% | 5 | -0.87 | 0.06 / 0.1 / 0.14 |
| -94f-Hf5xOQ | 0 | 96% | 8 |  |  |
| -Eu80hGbgVA | 0 | 97% | 42 |  |  |
| -V9EovSX8OI | 10 | 78% | 18 | -0.24 | -0.78 / -0.68 / -0.64 |
| -_Q1aI1Em_M | 2 | 96% | 27 | 0.06 | -0.77 / -0.07 / 0.62 |
| -u2ZZhnEG1Y | 0 | 98% | 27 |  |  |
| 0tP2pmXd9Gk | 14 | 98% | 43 | -0.26 | -0.45 / 0.15 / 0.35 |
| 16KptrgtdDM | 4 | 77% | 6 | -0.64 | -0.2 / -0.06 / -0.02 |
| 1Aja20oCGQo | 0 | 98% | 28 |  |  |
| 1Vkb2_3nFVU | 0 | 95% | 38 |  |  |
| 1Xs1kshVDno | 0 | 97% | 48 |  |  |
| 1ZHj5OmzyN8 | 0 | 87% | 63 |  |  |
| 1sUK8cY1gbk | 0 | 100% | 16 |  |  |
| 1ugRPNu765Q | 4 | 97% | 18 | -0.83 | 0.18 / 0.22 / 0.39 |
| 2LIZ7Y9AxHc | 0 | 99% | 21 |  |  |
| 2sIwBgG--mA | 0 | 89% | 34 |  |  |
| 3GxcUdWTqv4 | 0 | 79% | 48 |  |  |
| 3RluM0LMFKU | 0 | 94% | 4 |  |  |
| 3Ygxi5B-7cI | 0 | 94% | 13 |  |  |
| 3wirS8eqVYI | 2 | 95% | 13 | -0.98 | -0.08 / -0.08 / -0.08 |
| 448jPxkSr6s | 1 | 89% | 14 | -0.95 | -0.5 / -0.5 / -0.5 |
| 45v4zssxrQY | 0 | 78% | 33 |  |  |
| 4JWK1h7NMdA | 4 | 95% | 46 | -0.37 | -0.33 / -0.23 / 0.12 |
| 4cq8Cf1JVjY | 0 | 71% | 44 |  |  |
| 4osbfneXwXI | 3 | 98% | 12 | -0.79 | -0.8 / -0.78 / -0.29 |
| 53DI6ZSwUt4 | 0 | 97% | 49 |  |  |
| 5B14UNrfwuM | 0 | 96% | 7 |  |  |
| 5LKDOj8wvEs | 0 | 87% | 30 |  |  |
| 5VaZ9AXBKjM | 5 | 99% | 19 | 0.47 | -0.68 / -0.46 / 0.71 |
| 5aJtdopjCyg | 2 | 100% | 68 | -0.65 | -0.42 / -0.32 / -0.22 |
| 5eLNW1LgkB8 | 0 | 79% | 6 |  |  |
| 5t0S1btK2Ag | 0 | 72% | 30 |  |  |
| 5wdrcvQQJMg | 0 | 97% | 32 |  |  |
| 6PR-QQdUa0g | 3 | 97% | 12 | -0.16 | -0.16 / -0.1 / 0.22 |
| 6arnqtt0eT8 | 10 | 98% | 34 | -0.83 | -0.09 / 0.19 / 0.46 |
| 6dLODqhPAQM | 0 | 91% | 7 |  |  |
| 72YkMkLdkFo | 6 | 71% | 44 | -0.76 | 0.85 / 0.93 / 0.96 |
| 7FzPoKoKiC0 | 0 | 91% | 9 |  |  |
| 7kEZTgkmqfg | 3 | 71% | 11 | -0.59 | -0.25 / 0.59 / 0.59 |
| 7lAFD7V87jk | 0 | 92% | 40 |  |  |
| 7nGY_2ev9bE | 0 | 99% | 61 |  |  |
| 7xdQDqILnSI | 0 | 98% | 39 |  |  |
| 7xpQTZi7FdI | 1 | 99% | 43 | -0.76 | -0.63 / -0.63 / -0.63 |
| 85brcxUjxAI | 3 | 92% | 10 | -0.16 | -0.02 / -0.01 / -0.01 |
| 8N5O1t3UZkE | 3 | 90% | 71 | -0.54 | 0.09 / 0.66 / 0.69 |
| 8ZuHbuHi5WE | 1 | 100% | 6 | -0.99 | -0.69 / -0.69 / -0.69 |
| 8dXIU_QmdLs | 1 | 98% | 71 | -0.42 | -0.18 / -0.18 / -0.18 |
| 8lIWvG3RhWs | 0 | 100% | 5 |  |  |
| 95zbfLDcB2I | 0 | 72% | 11 |  |  |
| 9K3YrEEc-IE | 1 | 100% | 22 | 0.71 | -0.01 / -0.01 / -0.01 |
| 9SXaq_cwvAI | 12 | 99% | 11 | -0.73 | 0.35 / 0.43 / 0.73 |
| 9UxKCr3HytI | 0 | 95% | 21 |  |  |
| 9Yw37BL4uHA | 0 | 85% | 15 |  |  |
| 9imKaY0myyI | 4 | 96% | 17 | -0.82 | -0.61 / -0.5 / 0.01 |
| A271FsbDhDA | 1 | 100% | 5 | -0.97 | 0.62 / 0.62 / 0.62 |
| ACYaEOtuQWE | 0 | 65% | 23 |  |  |
| AKnXtyVrcz4 | 2 | 97% | 54 | -0.83 | -0.46 / 0.1 / 0.65 |
| ASskVkjHsAU | 0 | 78% | 20 |  |  |
| AVx7qLZQaRQ | 0 | 99% | 16 |  |  |
| AWgTZBADqoo | 0 | 99% | 9 |  |  |
| AqgvVxzTFzQ | 0 | 89% | 36 |  |  |
| B2uDfNd9QSo | 11 | 95% | 48 | -0.28 | 0.41 / 0.91 / 0.96 |
| BCe6rK5qoyY | 0 | 99% | 5 |  |  |
| BOaF8rDF3gU | 10 | 95% | 12 | -0.87 | -0.23 / -0.03 / 0.26 |
| BUn0J2SeHwM | 7 | 99% | 4 | 0.21 | 0.35 / 0.56 / 0.76 |
| BYbrT2Xadb8 | 0 | 99% | 39 |  |  |
| Bcqi_M9aPmg | 3 | 86% | 12 | -0.9 | -0.0 / 0.02 / 0.03 |
| Bh7rbePs4SM | 1 | 83% | 44 | -1.05 | -0.9 / -0.9 / -0.9 |
| BjgZxNbYqtU | 0 | 95% | 24 |  |  |
| Ce7D2nr5nGY | 0 | 95% | 56 |  |  |
| CgEDaaV-Ba8 | 15 | 99% | 68 | -0.87 | -0.12 / -0.07 / 0.41 |
| CiO3FrE8Z7s | 0 | 95% | 46 |  |  |
| CwkBIJfrVqY | 0 | 100% | 4 |  |  |
| DA8sM2ilEsc | 0 | 97% | 35 |  |  |
| DLLz7uPta_g | 2 | 99% | 9 | -0.24 | -0.34 / 0.2 / 0.75 |
| DWE4apy3L4w | 0 | 96% | 46 |  |  |
| DWsHRZFTqtk | 0 | 68% | 20 |  |  |
| D_qpSb5OQcQ | 0 | 97% | 56 |  |  |
| Da5zIBPzU8Q | 7 | 90% | 15 | -0.48 | -0.62 / -0.02 / 0.21 |
| DvPSQkrvLLg | 0 | 81% | 42 |  |  |
| E9-AKhBPnJ0 | 0 | 100% | 45 |  |  |
| EHt6ybfkYTs | 1 | 77% | 53 | -0.84 | 0.15 / 0.15 / 0.15 |
| EbhB3HpmMmA | 2 | 91% | 35 | -0.5 | -0.68 / -0.65 / -0.61 |
| EkbDqZa4Do4 | 0 | 92% | 7 |  |  |
| EowqCcoCL5k | 0 | 98% | 6 |  |  |
| F2XZjDDwjxQ | 0 | 80% | 6 |  |  |
| FKtqaKjZVPs | 4 | 88% | 9 | -0.67 | -0.61 / -0.48 / -0.32 |
| FMxUuvb9d1Q | 4 | 95% | 11 | -0.72 | -0.77 / -0.69 / -0.53 |
| FQGEUsAqEgs | 5 | 91% | 3 | -0.04 | 0.17 / 0.55 / 0.64 |
| FlZ1yNj1T3A | 4 | 97% | 14 | 0.09 | -0.72 / 0.16 / 0.84 |
| G5S6lMBwzXU | 0 | 93% | 10 |  |  |
| GBnzzBQu-2E | 0 | 99% | 7 |  |  |
| GVL2PSny6A4 | 0 | 100% | 42 |  |  |
| G_U5BCTfgRg | 0 | 91% | 63 |  |  |
| GumlybS_rBo | 3 | 97% | 40 | -0.97 | 0.19 / 0.42 / 0.51 |
| HfUZZ2gWvC0 | 0 | 94% | 67 |  |  |
| HopxMlCOnJs | 1 | 88% | 29 | 0.83 | -0.74 / -0.74 / -0.74 |
| I7dm6K6-PPI | 0 | 96% | 29 |  |  |
| IHcHQQzDKLU | 1 | 100% | 45 | -0.87 | -0.23 / -0.23 / -0.23 |
| IXgxVgFDyxY | 5 | 86% | 41 | -0.83 | -0.2 / -0.03 / 0.2 |
| IuV-OISSWDc | 0 | 100% | 52 |  |  |
| JB9PsFq5oe8 | 3 | 99% | 44 | -0.49 | -0.47 / -0.45 / -0.45 |
| JEsU4nTozSA | 4 | 99% | 37 | 0.19 | -0.87 / -0.76 / 0.39 |
| JXMXLy82_Ng | 0 | 100% | 27 |  |  |
| JXXH3bvKjA4 | 3 | 97% | 21 | -0.06 | -0.07 / -0.06 / 0.21 |
| JZhOx-a4Idg | 0 | 93% | 33 |  |  |
| K9X18xUHVq8 | 1 | 97% | 32 | 0.93 | 0.15 / 0.15 / 0.15 |
| KJY-qILhlWk | 3 | 100% | 46 | -0.91 | -0.04 / 0.03 / 0.27 |
| KW7nygNYRKs | 0 | 79% | 45 |  |  |
| KhN7481B7Fc | 0 | 73% | 44 |  |  |
| Kkj6K29A8-s | 7 | 98% | 51 | -0.93 | -0.62 / -0.52 / 0.34 |
| L-SEIHP59qU | 0 | 90% | 43 |  |  |
| L7hxyUCHo-g | 9 | 88% | 68 | -0.84 | 0.13 / 0.21 / 0.24 |
| LL4w-3yAspE | 1 | 100% | 40 | -0.57 | -0.21 / -0.21 / -0.21 |
| LUY1yxBVVz4 | 0 | 100% | 45 |  |  |
| LVuGNkrGBR0 | 0 | 88% | 28 |  |  |
| LlJqwwsrREM | 0 | 99% | 37 |  |  |
| Lo0pf_TmN44 | 0 | 96% | 9 |  |  |
| Lomfb5AcsK0 | 0 | 100% | 8 |  |  |
| LopyXe_2QKE | 0 | 96% | 8 |  |  |
| Lq5ZF2VfEGk | 8 | 95% | 12 | -0.9 | -0.96 / -0.8 / 0.22 |
| LzeTSaODzww | 0 | 100% | 6 |  |  |
| MCEaqcCHRyw | 0 | 90% | 19 |  |  |
| MHdDiWfeZw8 | 1 | 73% | 5 | -0.75 | 0.53 / 0.53 / 0.53 |
| MUg4UjW_JL4 | 7 | 97% | 10 | -0.83 | -0.16 / -0.03 / 0.18 |
| M_3Rd8NL4fA | 0 | 97% | 61 |  |  |
| Mmo_IQ11OK4 | 1 | 87% | 48 | 0.17 | -0.03 / -0.03 / -0.03 |
| MxWDtKFq1HA | 1 | 73% | 45 | -0.9 | -0.63 / -0.63 / -0.63 |
| N4TTxjp9NYQ | 0 | 98% | 30 |  |  |
| NOJ14cfla9E | 0 | 89% | 9 |  |  |
| Np3ex7Uo08M | 5 | 71% | 8 | -0.45 | 0.21 / 0.27 / 0.64 |
| OF1Lqo5uh6g | 0 | 53% | 22 |  |  |
| Pmu29Uet23A | 7 | 93% | 39 | -0.71 | 0.09 / 0.38 / 0.73 |
| QAcBgVZheDo | 0 | 100% | 22 |  |  |
| RWP2a7QmtHw | 3 | 92% | 32 | 0.46 | -0.23 / -0.12 / 0.63 |
| S10nJN2Y1og | 6 | 90% | 13 | -0.39 | -0.39 / 0.07 / 0.64 |
| SdaMb96OhNA | 0 | 92% | 34 |  |  |
| TDu6ipJkQUo | 0 | 98% | 58 |  |  |
| T_5osrG-fGI | 1 | 74% | 17 | -0.62 | -0.51 / -0.51 / -0.51 |
| TjH37PpeX7k | 0 | 91% | 9 |  |  |
| TkUydJGtlyM | 0 | 100% | 24 |  |  |
| TrAZBJxLfTo | 0 | 99% | 8 |  |  |
| U39OzzOxaMM | 2 | 97% | 24 | -0.7 | -0.69 / -0.12 / 0.45 |
| UJ3xNfw7G3Y | 9 | 95% | 31 | -0.7 | -0.52 / 0.18 / 0.7 |
| ULIxMsGg-c4 | 0 | 97% | 47 |  |  |
| UOf0sV68-O4 | 3 | 87% | 44 | -0.83 | -0.64 / 0.0 / 0.77 |
| Ulk_gXK9GrI | 0 | 92% | 59 |  |  |
| Um5q7Lx107k | 6 | 85% | 29 | -0.47 | -0.32 / -0.22 / -0.04 |
| UyFOOBD4tks | 0 | 94% | 5 |  |  |
| VIFLw3w1XJs | 11 | 80% | 6 | -0.72 | 0.11 / 0.21 / 0.28 |
| Va9uJMa_QtQ | 4 | 98% | 24 | -0.73 | -0.4 / 0.22 / 0.5 |
| Vr-PDc6beYI | 1 | 98% | 32 | -1.0 | 0.72 / 0.72 / 0.72 |
| WCV7RcBKUxc | 0 | 78% | 35 |  |  |
| WNnW9Dd2vMY | 0 | 97% | 36 |  |  |
| WTAmRGCeCYk | 0 | 96% | 7 |  |  |
| WsQ0ghZg5FE | 0 | 100% | 29 |  |  |
| X7fZRpsBCeM | 0 | 99% | 26 |  |  |
| XAGlVI9aqn8 | 0 | 99% | 16 |  |  |
| XCcRm-7UaIc | 0 | 72% | 5 |  |  |
| XFcUTZGev3w | 1 | 100% | 13 | -0.43 | -0.61 / -0.61 / -0.61 |
| XO5W7vCf3hc | 0 | 95% | 12 |  |  |
| XQYtS5u3V6Y | 3 | 89% | 58 | -1.14 | 0.11 / 0.17 / 0.28 |
| XcAbgXgi76c | 0 | 95% | 24 |  |  |
| XoNhZtPO5S4 | 0 | 97% | 22 |  |  |
| XsZHCDPU86E | 0 | 86% | 37 |  |  |
| XuwlOfbFyOY | 0 | 99% | 37 |  |  |
| Y3j0idcVtDs | 3 | 70% | 15 | -0.85 | -0.9 / -0.43 / -0.4 |
| YGrjinmNBoM | 0 | 100% | 11 |  |  |
| YjjfSspZq0k | 0 | 97% | 11 |  |  |
| Z6zavTr7zWY | 0 | 74% | 35 |  |  |
| Zam8nGoJA8o | 0 | 94% | 34 |  |  |
| Zi509W8wgno | 0 | 83% | 13 |  |  |
| aY2BjFuwxB0 | 0 | 85% | 43 |  |  |
| ac7BTGvT84M | 1 | 98% | 9 | -0.21 | -0.47 / -0.47 / -0.47 |
| arnQYv-L6Qk | 0 | 87% | 31 |  |  |
| arq9Jl8rjq0 | 0 | 93% | 29 |  |  |
| avs8uD8F-Cc | 0 | 95% | 6 |  |  |
| azpOGkeEgE0 | 2 | 100% | 23 | -0.78 | -0.29 / -0.28 / -0.26 |
| b-HII85xJRs | 0 | 97% | 47 |  |  |
| bSJAbDdTqUg | 0 | 100% | 10 |  |  |
| bqhJwjIe9Co | 0 | 99% | 19 |  |  |
| brYjAfTazt8 | 0 | 99% | 20 |  |  |
| c-F_OhLGPMQ | 2 | 100% | 34 | -0.69 | -0.41 / -0.23 / -0.05 |
| c1ajJjLN2ng | 1 | 80% | 46 | 0.24 | 0.82 / 0.82 / 0.82 |
| cIIEYn42o4g | 1 | 98% | 48 | -0.42 | 0.54 / 0.54 / 0.54 |
| cPurQuEOUjo | 1 | 95% | 41 | -0.79 | -0.4 / -0.4 / -0.4 |
| cdS8QlI7qF4 | 3 | 95% | 25 | -0.64 | -0.5 / -0.47 / -0.44 |
| cu8WH2JvjJ0 | 1 | 99% | 70 | 0.09 | -0.7 / -0.7 / -0.7 |
| d0Hg3t_43tI | 3 | 99% | 16 | 0.33 | -0.1 / -0.01 / 0.03 |
| d0f74mzQ1ew | 0 | 93% | 6 |  |  |
| dQXRQqngsy0 | 0 | 95% | 60 |  |  |
| dRV_CBoj1gg | 2 | 94% | 10 | -0.78 | 0.25 / 0.27 / 0.3 |
| dw1nSzUpiE0 | 0 | 89% | 27 |  |  |
| dwD8HKCzWrQ | 1 | 97% | 42 | -0.94 | -0.67 / -0.67 / -0.67 |
| eBa-sy2Mt1s | 0 | 96% | 17 |  |  |
| eYaIOC8KMlk | 2 | 100% | 27 | -0.18 | 0.1 / 0.19 / 0.28 |
| f4RP_bDXUsc | 0 | 96% | 5 |  |  |
| fJ_a2RLdFCM | 10 | 97% | 6 | -0.41 | -0.27 / -0.01 / 0.11 |
| fhn2ANDE4kA | 8 | 94% | 62 | -0.27 | -0.64 / -0.47 / 0.91 |
| fxwUwZGaZNg | 0 | 99% | 9 |  |  |
| fyeo4Vb9GPk | 1 | 82% | 26 | 0.34 | 0.51 / 0.51 / 0.51 |
| gnISwtmtEFY | 0 | 95% | 21 |  |  |
| gtVMOCXjpPo | 0 | 100% | 21 |  |  |
| gvttMVTks24 | 0 | 100% | 41 |  |  |
| h8_sVbLhOAo | 1 | 79% | 28 | -0.22 | 0.4 / 0.4 / 0.4 |
| hYUl6NC6MLw | 0 | 93% | 2 |  |  |
| i9vzSZ2ckc0 | 0 | 90% | 25 |  |  |
| jM4e75z13yA | 0 | 100% | 20 |  |  |
| jVANF0nbCUA | 5 | 99% | 5 | -0.61 | 0.3 / 0.34 / 0.38 |
| jjra4H3WO6Y | 2 | 95% | 8 | -0.45 | -0.47 / -0.46 / -0.46 |
| jmcEyigkSd8 | 0 | 99% | 71 |  |  |
| jtmJ1d0fTbA | 4 | 90% | 21 | -0.84 | -0.5 / -0.15 / -0.04 |
| k4DCZL1T6-0 | 0 | 94% | 17 |  |  |
| kCoOyt4c9SQ | 0 | 100% | 3 |  |  |
| kJUuzlk6d8M | 0 | 84% | 38 |  |  |
| knhkXMTLL68 | 1 | 92% | 32 | -0.64 | 0.8 / 0.8 / 0.8 |
| lANolilLOho | 0 | 76% | 13 |  |  |
| lVOB4diuOHA | 3 | 88% | 50 | -0.86 | 0.0 / 0.03 / 0.75 |
| lxqUJr64itc | 0 | 97% | 3 |  |  |
| ly4SOGeZmcU | 0 | 84% | 44 |  |  |
| m4wt5jmpk3U | 0 | 93% | 27 |  |  |
| mKXtVQnqhB4 | 1 | 96% | 52 | -0.25 | -0.57 / -0.57 / -0.57 |
| mOlf4pcvUxM | 5 | 94% | 26 | -0.63 | -0.51 / -0.28 / 0.43 |
| mY0j4CgxgIQ | 0 | 97% | 40 |  |  |
| mebvb2nYO7o | 1 | 100% | 40 | -0.07 | -0.7 / -0.7 / -0.7 |
| mhFMCKL6xak | 0 | 90% | 26 |  |  |
| nbPFqP-kIuc | 7 | 97% | 17 | -0.7 | -0.77 / -0.72 / -0.49 |
| nbRUa-IgdDA | 0 | 88% | 14 |  |  |
| nc1mMleFihg | 0 | 100% | 8 |  |  |
| nrPywbL1plk | 1 | 88% | 11 | -0.21 | -0.13 / -0.13 / -0.13 |
| oDs8zNGc1no | 3 | 95% | 18 | -0.57 | 0.01 / 0.09 / 0.2 |
| oTFLbD77unY | 0 | 82% | 45 |  |  |
| oTLFPLV1C4o | 1 | 89% | 51 | -0.67 | -0.24 / -0.24 / -0.24 |
| o_u9Nu-MPME | 0 | 74% | 7 |  |  |
| ogYGv0g3VFA | 1 | 72% | 6 | 0.03 | 0.59 / 0.59 / 0.59 |
| oyBL4tw4CSg | 0 | 89% | 34 |  |  |
| pS8KuAM9G8k | 4 | 83% | 24 | -0.88 | -0.27 / -0.03 / 0.08 |
| pg_dxIvJRZo | 1 | 94% | 30 | -0.87 | -0.7 / -0.7 / -0.7 |
| ph3DXfeyzc8 | 0 | 99% | 40 |  |  |
| qJoYbak-or0 | 0 | 99% | 3 |  |  |
| qKNFoObQN48 | 0 | 85% | 21 |  |  |
| qKrTAnq58sk | 0 | 92% | 52 |  |  |
| qNX6VVbHY2A | 0 | 89% | 8 |  |  |
| qkQmT4fXKD8 | 0 | 97% | 46 |  |  |
| qm8qoMnaFTY | 0 | 93% | 8 |  |  |
| qmbFPM7y3-M | 0 | 83% | 22 |  |  |
| quUydRpf96Q | 4 | 98% | 38 | -0.13 | -0.75 / -0.47 / 0.04 |
| qvJ7gbH2zrY | 1 | 81% | 28 | -0.52 | -0.52 / -0.52 / -0.52 |
| qwlkRHQiUnM | 14 | 89% | 50 | -0.9 | -0.24 / 0.1 / 0.63 |
| rGgXKbDB4hQ | 0 | 90% | 20 |  |  |
| rTXgMbyjMuU | 2 | 98% | 15 | -0.15 | -0.27 / -0.26 / -0.24 |
| rWgw9qCqqUA | 0 | 87% | 69 |  |  |
| rcCymL9uzs8 | 4 | 95% | 72 | 0.94 | -0.73 / -0.51 / 0.5 |
| rtPri1J_5Q8 | 0 | 100% | 5 |  |  |
| rwNfOc4H7P4 | 1 | 97% | 50 | -0.89 | -0.56 / -0.56 / -0.56 |
| rzSAGU5R4qk | 1 | 99% | 31 | 0.15 | 0.12 / 0.12 / 0.12 |
| s-rOCECttUo | 2 | 92% | 9 | -0.27 | -0.02 / 0.17 / 0.36 |
| sMTXr1JFDnA | 0 | 97% | 11 |  |  |
| sw2_HmjgqpI | 0 | 96% | 5 |  |  |
| tH2fowVHLUQ | 2 | 93% | 45 | -0.3 | 0.34 / 0.46 / 0.57 |
| u88U3jjzg3M | 0 | 100% | 16 |  |  |
| uH1894jAvIA | 2 | 100% | 34 | -0.19 | -0.39 / 0.14 / 0.67 |
| um9GK-QTefM | 1 | 95% | 8 | -0.09 | -0.11 / -0.11 / -0.11 |
| uzeFWAwj1hY | 0 | 79% | 37 |  |  |
| v54FZ_gi5KI | 0 | 99% | 5 |  |  |
| vD0wO3tq6BM | 3 | 91% | 40 | -0.77 | 0.33 / 0.38 / 0.54 |
| vaTDBxZ2UoA | 0 | 98% | 39 |  |  |
| w-T12UV981c | 0 | 86% | 25 |  |  |
| w7n5p2Dt4J4 | 3 | 99% | 44 | -0.58 | -0.71 / -0.51 / 0.44 |
| wT9QgWvLpUE | 0 | 100% | 30 |  |  |
| wzzvN23gDnU | 0 | 85% | 27 |  |  |
| xDqrsO42uAQ | 2 | 99% | 3 | -0.56 | -0.18 / -0.12 / -0.05 |
| xJDBaSJuums | 9 | 97% | 53 | -0.26 | -0.01 / 0.41 / 0.55 |
| xLj6KEqkWJs | 1 | 98% | 65 | 0.15 | 0.44 / 0.44 / 0.44 |
| xnTPbWmk8eI | 4 | 85% | 59 | 0.32 | -0.25 / 0.29 / 0.59 |
| xwFVcyt8P_M | 0 | 99% | 12 |  |  |
| y77bYHCpWoE | 0 | 85% | 31 |  |  |
| yIUp9Ox9v2c | 0 | 98% | 46 |  |  |
| z9yBm2-Q-QE | 1 | 85% | 45 | 0.02 | 0.24 / 0.24 / 0.24 |
| zdNWH66tr5M | 0 | 98% | 36 |  |  |
| zqXN1hfEdzI | 0 | 89% | 43 |  |  |

## Vocabulary proposals

- measurement: contact_point_landmark (Contact and the racket-drop low point are not landmarks in the two-phase data, so the contact posture, chopping at a low contact point and trunk lean at contact cannot be tested.)
- feature: trunk_lean_at_contact_sideways (Coaches fault an upright or backward-leaning chest, or a sideways and backward trunk, at contact; the trunk lean needs a forward-versus-sideways split.)
- feature: forearm_pronation_angle (The forearm supination to pronation snap cannot be seen with the registered elbow and shoulder angles.)
- feature: grip_type (A continental, eastern or western grip, or a fist grip, is a hand and racket detail that no body-frame feature shows.)
- trackable: racket_head (The racket's path, waiter's tray position and racket-drop depth need the racket tracked.)
- trackable: ball (Toss height, toss placement and where the ball lands need the ball tracked.)
