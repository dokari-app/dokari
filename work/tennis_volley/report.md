# Factory report: tennis_volley

Clips found: 40 (usable for attempts: 38). Attempts: 449.
Confidence tier: **low**. Checks: 8 pass, 2 fail, 0 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.71 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [FAIL] 6. discrimination: 0/1 objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75); do not: ['big_swing']; 6 without enough labels
- [PASS] 7. outcome links: 3 links, 3 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.76 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 4 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **excessive_body_turn** (medium, agreed by 5 of 5 runs): Turn the shoulders only modestly toward the volley side, and do not rotate the whole body as on a groundstroke.. Target: angle.shoulder_hip_twist between -17.5184 and 23.1085 at L1. Wrong if below: Completely square to the net with no shoulder turn, so the arm has to reach across. (low); above: Large groundstroke-like turn that leaves the hand and elbow behind the body. (medium). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 2. **big_swing** (medium, agreed by 3 of 5 runs): Use a short punch or block with a compact motion instead of a long backswing or groundstroke-style swing.. Target: angle.elbow.dom between 98.3863 and 171.315 at L1. Wrong if below: Elbow still tightly bent or collapsed at contact, with the arm jammed or the racket pulled around the body. (low); above: Arm swings through and extends almost straight at contact, as in a groundstroke or reaching swing. (medium). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 3. **elbows_not_in_front** (low, agreed by 5 of 5 runs): Keep the hitting elbow in front of the body and away from the ribs, so the racket hand stays in front.. Target: angle.shoulder.dom at most 89.2487 at L1. Wrong if above: Elbow lifted or pulled out and behind the body line. (low). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 4. **wrong_footwork** (low, agreed by 5 of 5 runs): Step into the ball, with a split step and a balanced step toward it, so the body is involved and the contact is stable.. Target: dist.stance_width at most 3.4804 at L1. Wrong if above: Over-wide lunge that leaves the player unbalanced and slow to recover. (low). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 5. **distance_from_ball** (medium, agreed by 5 of 5 runs): Meet the ball comfortably in front of the body, with the arm extended only moderately, without overreaching or crowding the ball.. Target: reach.wrist.dom between 0.7054 and 1.0977 at L1. Wrong if below: Crowded on the ball, with the hand pulled in close to the body and no room to punch. (medium); above: Arm overextended while reaching or lunging at a ball that is too far away. (medium). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 6. **leaning_over_ball** (medium, agreed by 4 of 5 runs): Keep the trunk stable and slightly forward, without hunching or leaning over the ball too early.. Target: angle.trunk_lean at most 33.7925 at L1. Wrong if above: Upper body folded over the ball, or leaning too early. (medium). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.
- 7. **chopping_down** (low, agreed by 4 of 5 runs): Punch forward through the ball with a firm hand in front of the body, instead of chopping high to low.. Target: height.wrist.dom between -1.2317 and 0.0594 at L1. Wrong if below: Hand finishes well below the shoulder, as in a downward karate chop. (low); above: Hand raised high above the shoulder, with the racket dropped on the ball from above. (low). Range from good-form demonstrations (96 attempts in 9 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **big_swing** (form; 7 of 12, strong): only a proxy is measured (a test that goes with it, not the thing itself) (big_swing). Coaches disagree: Source 6 says a bit of swing is fine on higher, slower balls. Source 0 says a slight racket lag gives power.
- **wrong_footwork** (form; 6 of 12, strong): only a proxy is measured (a test that goes with it, not the thing itself) (wrong_footwork). Coaches disagree: Source 2 says not to split step when under a foot from the net. Sources 1, 6 and 11 say to split step. Source 11 makes contact and then steps, while source 7 wants contact before the foot lands.
- **elbows_not_in_front** (form; 4 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (elbows_not_in_front). Coaches disagree: Source 1 wants elbows aired out, not down. Sources 0 and 11 want elbows in front, as if on a table.
- **wrist_unstable** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks / racket detection to see wrist bend and racket head relative to hand. Coaches disagree: Sources 3 and 8 want a locked wrist. Source 11 wants a loose grip so the wrist absorbs the ball.
- **wrong_grip** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to detect grip (Continental vs Eastern/Western). Coaches disagree: Source 1 uses a composite grip at bevel 2.5. Source 11 adjusts slightly toward the weaker side. Others say to keep a pure continental grip.
- **chopping_down** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (chopping_down).
- **distance_from_ball** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (distance_from_ball). Coaches disagree: Source 4 wants good extension toward the net at the finish.
- **excessive_body_turn** (form; 2 of 12, some): measured by the camera (excessive_body_turn). Coaches disagree: Source 0 says the backhand turn can be slightly larger than the forehand turn. Source 9 says to turn sideways like a groundstroke, but modestly.
- **grip_too_tight** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **leaning_over_ball** (form; 2 of 12, some): measured by the camera (leaning_over_ball). Coaches disagree: Source 8 says to lean forward and finish low and in front.
- **not_watching_ball** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: head/gaze direction relative to the ball needs ball detection and face/head orientation tracking.
- **racket_tip_up_open_body** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection to see racket tip direction.
- **approach_positioning** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball and opponent detection plus court position tracking to judge path of approach ball and opponent cues.
- **chest_high_forehand** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection to know the ball is at chest height, plus shot type (forehand vs backhand) classification.
- **dumping_short** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): angle.elbow.dom shows the bent arm; abrupt finish not tested; ball outcome needs ball tracking.
- **low_volley_cross_court** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection for ball height and direction of shot; lat.com_shift shows momentum but no test.
- **not_closing_forward** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): fwd.trunk_shift shows forward movement; no objective tests it.
- **racket_low_late_set** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection to see racket head position and set timing; height.wrist.dom shows hand height but no test for preparation.
- **slicing_too_much** (form; 1 of 12, single): only a proxy is measured (a test that goes with it, not the thing itself) (chopping_down).
- **splitting_hands_early** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): dist.wrist_width shows hand separation; no objective tests it. Coaches disagree: Source 2 says a two-handed backhand volley is fine for high or fast balls.

Good form, as coaches give it:

- Keep the volley compact and short, like a punch, push or block, not a groundstroke swing. (6 of 12)
- Use a continental grip for all volleys, forehand and backhand, with no grip change. (5 of 12)
- Keep the preparation small, with only a modest shoulder or upper-body turn so you meet the ball outside the body. (5 of 12)
- Keep the hand and elbow in front of the body. (4 of 12)
- Let the racket lag slightly behind the hand, with the hands close together, as if catching the ball on the strings. (4 of 12)
- Use a ready position with a knee bend, on the toes, racket in front, and the upper body tilted slightly down. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **use_the_ball_pace** (contested, 3 of 3 runs; explains big_swing, chopping_down): At the net the ball arrives fast and already carries energy, so the racket only has to redirect it. A short, compact punch gives a steady contact and leaves time to be on balance, while a long backswing adds timing demands and variation. Cue handle: Let the ball's pace do the work with a short, firm redirect forward through it.. Competing views: Most coaches want a short punch, block or catch with almost no backswing.; Source 6 says a bit of swing is fine on higher, slower balls.; Source 0 says a slight racket lag gives power..
- **step_into_balanced_base** (contested, 3 of 3 runs; explains wrong_footwork, leaning_over_ball): A split step and a balanced step toward the ball let the legs and body move forward together with the hand. That gives a stable base to hit from and a firm contact, rather than an arm-only hit with footwork as a separate action. Cue handle: Move the body into the ball as one balanced action, with step and hit flowing together.. Competing views: Sources 1, 6 and 11 say to split step.; Source 2 says not to split step when within about a foot of the net.; Source 11 makes contact and then steps, while source 7 wants contact before the foot lands..
- **small_turn_hand_in_front** (contested, 3 of 3 runs; explains excessive_body_turn, elbows_not_in_front, big_swing): A small shoulder turn is enough to set the racket, and it keeps the hand and elbow in front where they can be seen and controlled. A full groundstroke-style turn carries them behind the body and makes the contact harder to time. Cue handle: . Competing views: Source 0 says the backhand turn can be slightly larger than the forehand turn.; Source 9 says to turn sideways like a groundstroke, but modestly.; Source 1 wants elbows aired out, not down; sources 0 and 11 want elbows in front, as if on a table..
- **reset_for_next_ball** (coaching_consensus, 3 of 3 runs; explains wrong_footwork, big_swing): Bringing the hands back toward the body and bending the elbow again after contact restores the ready position and the balance. It prepares the player to react to the next ball, which can come back quickly at the net. Cue handle: Return to a ready, balanced shape right away so the next ball finds you set..

## Check against labelled mistake videos (25 videos, 338 attempts, 224 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| big_swing | 34 / 9 | 27 / 11 |
| excessive_body_turn | 8 / 4 | 0 / 0 |
| distance_from_ball | 6 / 2 | 0 / 0 |
| wrong_footwork | 4 / 2 | 2 / 1 |
| elbows_not_in_front | 1 / 1 | 2 / 1 |
| leaning_over_ball | 1 / 1 | 2 / 2 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| excessive_body_turn | 0 / 8 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| big_swing | 27 / 34 | 11 / 9 | 0.55 | 43% | does not tell right from wrong well enough; range kept from good form demonstrations |
| elbows_not_in_front | 2 / 1 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| wrong_footwork | 2 / 4 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| distance_from_ball | 0 / 6 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| leaning_over_ball | 2 / 1 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| chopping_down | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: reach.wrist.dom, angle.elbow.dom, dist.wrist_width, height.wrist.dom, angle.shoulder.dom
Attempts found as: reach.wrist.dom rises (to at least 0.7). Typical size of the last event 0.548, lasting 4.8 s; smaller ones (below 0.219) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 386 clear attempts in 17 of 17 clips after 1 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 24 | 307 | mixed 307 |
| coach_demo | 8 | 88 | good_form 88 |
| practice_session | 5 | 32 | good_form 16, unknown 16 |
| pro_footage | 2 | 15 | good_form 15 |
| other | 1 | 9 | mixed 9 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| excessive_body_turn | 8% (9 clips) | 4% (29 clips) | no difference: everyone is inside, or this measure does not separate them |
| big_swing | 4% (9 clips) | 5% (29 clips) | no difference: everyone is inside, or this measure does not separate them |
| elbows_not_in_front | 9% (9 clips) | 2% (29 clips) | demos depart more: doubtful |
| wrong_footwork | 6% (9 clips) | 5% (29 clips) | no difference: everyone is inside, or this measure does not separate them |
| distance_from_ball | 4% (9 clips) | 5% (29 clips) | no difference: everyone is inside, or this measure does not separate them |
| leaning_over_ball | 8% (9 clips) | 6% (29 clips) | no difference: everyone is inside, or this measure does not separate them |
| chopping_down | 6% (9 clips) | 2% (29 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- step_and_punch: L0 to L1
- recover: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip 6IoRXheRq-M: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 449 of 463 attempts (tolerance 2.041). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (-11kpMTXv2g, 1bhTL0cMMRk, 3Or7isgKeIc, 5c8I4lL_jjo, 8kTPsQ0NHlM, Fm48pbfyl-4, Gif7Y1p67hA, Jf8hbFah-o0, KcJvg_aSU-E, L5iL2k7FUZE, LtPhf1L3TSE, QczXKX1lHSk, S51OCVdnXQ0, UIDDv6PXNdY, Xvfn10AY2Gw, cHBZ8U2Rtak, ebSB47mHNuQ, huY2zpkDFKA, q1sRADw_VrI, qJTL8N20CxE, qWnBzauZp_Y, sUJK93Py4m8, tMQW0-ueh2s).

| clip | attempts found | kept | note |
|---|---|---|---|
| -11kpMTXv2g | 15 | 15 | seed |
| 1bhTL0cMMRk | 8 | 8 | seed |
| 3Or7isgKeIc | 15 | 15 | seed |
| 5c8I4lL_jjo | 15 | 15 | seed |
| 5vvm5c1Z2mg | 15 | 15 |  |
| 6IoRXheRq-M | 2 | 2 |  |
| 6fAtunAkRX4 | 15 | 13 |  |
| 8kTPsQ0NHlM | 15 | 15 | seed |
| A5zj-BpFJPg | 15 | 15 |  |
| BOqx_u8jP6s | 9 | 9 |  |
| DF4VbA5-Dks | 15 | 14 |  |
| ESZzCjrtC8I | 15 | 8 |  |
| Fm48pbfyl-4 | 8 | 8 | seed |
| Gif7Y1p67hA | 4 | 4 | seed |
| Jf8hbFah-o0 | 5 | 5 | seed |
| KcJvg_aSU-E | 15 | 15 | seed |
| L5iL2k7FUZE | 15 | 15 | seed |
| LtPhf1L3TSE | 15 | 15 | seed |
| QczXKX1lHSk | 12 | 12 | seed |
| QyVQiqo-ZkA | 15 | 15 |  |
| S51OCVdnXQ0 | 15 | 15 | seed |
| UIDDv6PXNdY | 11 | 11 | seed |
| UVIaWRNJ42Y | 12 | 12 |  |
| XMcCo2MVhjU | 15 | 15 |  |
| Xvfn10AY2Gw | 15 | 15 | seed |
| b-wlSIOMnO8 | 15 | 15 |  |
| b4uFvVbfsBw | 15 | 15 |  |
| cHBZ8U2Rtak | 15 | 15 | seed |
| ebSB47mHNuQ | 15 | 15 | seed |
| gnS8exFXS0g | 3 | 3 |  |
| huY2zpkDFKA | 13 | 13 | seed |
| k0nshf_Pdk4 | 12 | 9 |  |
| q1sRADw_VrI | 8 | 8 | seed |
| qJTL8N20CxE | 15 | 15 | seed |
| qWnBzauZp_Y | 6 | 6 | seed |
| sUJK93Py4m8 | 15 | 15 | seed |
| tMQW0-ueh2s | 5 | 5 | seed |
| tdSNnrjsDAQ | 15 | 14 |  |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): reach.wrist.dom=0.806, angle.elbow.dom=119.002, height.wrist.dom=-0.569, reach.wrist.non=0.849, angle.elbow.non=122.728, dist.wrist_width=1.062, height.wrist_mid=-0.596, angle.shoulder.non=30.818, angle.knee.non=151.495, angle.trunk_lean=9.013
- L1 (t=0.551): reach.wrist.dom=0.896, angle.elbow.dom=133.707, height.wrist.dom=-0.641, reach.wrist.non=0.875, angle.elbow.non=128.39, dist.wrist_width=1.249, height.wrist_mid=-0.626, angle.shoulder.non=34.0, angle.knee.non=149.126, angle.trunk_lean=9.749
- L2 (t=1.0): reach.wrist.dom=0.808, angle.elbow.dom=117.947, height.wrist.dom=-0.589, reach.wrist.non=0.842, angle.elbow.non=122.348, dist.wrist_width=1.098, height.wrist_mid=-0.615, angle.shoulder.non=29.117, angle.knee.non=150.979, angle.trunk_lean=8.644

## Per clip

| clip | attempts used | believable frames | view yaw | reach.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -11kpMTXv2g | 15 | 91% | 14 | 0.79 | 0.77 / 0.9 / 1.0 |
| 1bhTL0cMMRk | 8 | 94% | 9 | 0.77 | 0.78 / 0.85 / 0.89 |
| 3Or7isgKeIc | 15 | 100% | 7 | 0.77 | 0.78 / 0.86 / 0.98 |
| 5c8I4lL_jjo | 15 | 99% | 10 | 0.85 | 0.79 / 0.86 / 0.96 |
| 5vvm5c1Z2mg | 15 | 98% | 28 | 0.79 | 0.84 / 0.94 / 1.02 |
| 6IoRXheRq-M | 2 | 92% | 13 | 0.79 | 0.75 / 0.81 / 0.86 |
| 6fAtunAkRX4 | 13 | 98% | 51 | 0.83 | 0.78 / 0.9 / 1.05 |
| 8kTPsQ0NHlM | 15 | 99% | 12 | 0.76 | 0.77 / 0.86 / 0.96 |
| A5zj-BpFJPg | 15 | 94% | 53 | 0.81 | 0.81 / 0.92 / 1.05 |
| BOqx_u8jP6s | 9 | 93% | 12 | 0.92 | 0.92 / 0.98 / 1.06 |
| DF4VbA5-Dks | 14 | 99% | 8 | 0.75 | 0.76 / 0.92 / 0.98 |
| ESZzCjrtC8I | 8 | 92% | 22 | 0.79 | 0.92 / 1.01 / 1.13 |
| Fm48pbfyl-4 | 8 | 100% | 42 | 0.67 | 0.66 / 0.8 / 0.84 |
| Gif7Y1p67hA | 4 | 89% | 15 | 0.73 | 0.8 / 0.81 / 1.02 |
| Jf8hbFah-o0 | 5 | 87% | 6 | 0.85 | 0.83 / 0.91 / 0.95 |
| KcJvg_aSU-E | 15 | 100% | 5 | 0.8 | 0.83 / 0.89 / 0.97 |
| L5iL2k7FUZE | 15 | 99% | 18 | 0.83 | 0.74 / 0.86 / 1.01 |
| LtPhf1L3TSE | 15 | 90% | 6 | 0.83 | 0.84 / 0.98 / 1.05 |
| QczXKX1lHSk | 12 | 87% | 4 | 0.85 | 0.84 / 0.89 / 0.97 |
| QyVQiqo-ZkA | 15 | 99% | 47 | 0.74 | 0.72 / 0.94 / 1.03 |
| S51OCVdnXQ0 | 15 | 100% | 17 | 0.86 | 0.84 / 0.95 / 1.05 |
| UIDDv6PXNdY | 11 | 93% | 8 | 0.86 | 0.81 / 0.9 / 0.97 |
| UVIaWRNJ42Y | 12 | 86% | 10 | 0.83 | 0.83 / 0.9 / 1.03 |
| XMcCo2MVhjU | 15 | 99% | 13 | 0.85 | 0.85 / 0.92 / 1.07 |
| Xvfn10AY2Gw | 15 | 96% | 13 | 0.83 | 0.76 / 0.85 / 0.94 |
| b-wlSIOMnO8 | 15 | 95% | 25 | 0.89 | 0.82 / 0.93 / 1.03 |
| b4uFvVbfsBw | 15 | 97% | 3 | 0.71 | 0.79 / 0.83 / 0.87 |
| cHBZ8U2Rtak | 15 | 100% | 13 | 0.82 | 0.81 / 0.93 / 1.02 |
| ebSB47mHNuQ | 15 | 95% | 54 | 0.76 | 0.72 / 0.9 / 1.0 |
| gnS8exFXS0g | 3 | 97% | 13 | 0.92 | 0.79 / 0.85 / 0.93 |
| huY2zpkDFKA | 13 | 100% | 4 | 0.84 | 0.8 / 0.9 / 1.01 |
| k0nshf_Pdk4 | 9 | 96% | 31 | 0.91 | 0.88 / 1.02 / 1.11 |
| q1sRADw_VrI | 8 | 92% | 17 | 0.73 | 0.74 / 0.81 / 0.91 |
| qJTL8N20CxE | 15 | 97% | 21 | 0.76 | 0.71 / 0.86 / 0.96 |
| qWnBzauZp_Y | 6 | 95% | 5 | 0.82 | 0.74 / 0.83 / 0.95 |
| sUJK93Py4m8 | 15 | 97% | 8 | 0.82 | 0.78 / 0.89 / 0.95 |
| tMQW0-ueh2s | 5 | 100% | 22 | 0.79 | 0.78 / 0.81 / 0.94 |
| tdSNnrjsDAQ | 14 | 93% | 26 | 0.79 | 0.74 / 0.92 / 1.02 |
| v5rj1UA1YCI | 1 | 65% | 29 | 0.91 | 0.97 / 0.97 / 0.97 |
| wQJjXPrGqpE | 1 | 74% | 28 | 0.87 | 0.83 / 0.83 / 0.83 |

## Vocabulary proposals

- feature: angle.wrist_extension.dom (Needed to test wrist_unstable: the wrist collapsing or the racket overtaking the hand at contact.)
- trackable: racket_head (Needed to test racket_tip_up_open_body, and the racket lag and grip-related faults.)
- feature: racket_tip_direction (Needed to test whether the racket tip points up or to the side, and the facing of the body.)
- feature: head_orientation_to_ball (Needed to test not_watching_ball, which means the head turned to the opponent or the target instead of facing the ball.)
- measurement: grip_type_and_tension (Needed to show wrong_grip (continental) and grip_too_tight; neither is visible through body-frame landmarks.)
- feature: step_timing_vs_contact (Needed to judge whether the split step and step-in line up with ball contact, which one point of a single feature cannot show.)
