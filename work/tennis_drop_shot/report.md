# Factory report: tennis_drop_shot

Clips found: 23 (usable for attempts: 20). Attempts: 202.
Confidence tier: **low**. Checks: 7 pass, 2 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [FAIL] 4. recognition: false-accept rate 0.73 against other activities is above 0.15
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [n/a ] 6. discrimination: no objective has enough labelled good and faulty examples (3 of each), so no target range is validated; 5 of 5 come from good-form demonstrations, 0 from everyday footage (what is typical, not what is good)
- [PASS] 7. outcome links: 2 links, 2 prior-only (no data to test them yet)
- [FAIL] 8. agreement: agreement 0.45 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent
- [PASS] 10. principles: 4 principles; sound

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **waiting_on_ball** (medium, agreed by 5 of 5 runs): Move forward into the ball and take it early, with the body travelling toward the net instead of waiting for it to drop or reaching for it.. Target: fwd.trunk_shift at least -0.1128 at L1. Wrong if below: The body stays upright or leans back on the baseline and the player reaches for the ball as it drops. (medium). Range from good-form demonstrations (72 attempts in 6 clips); reliability C.
- 2. **telegraphing_shot** (low, agreed by 3 of 5 runs): Make the preparation look like the normal slice or groundstroke preparation until late, so the opponent cannot read the drop shot.. Target: angle.shoulder.dom at most 104.6909 at L1. Wrong if above: The racket arm is raised or opened wider than in the player's usual preparation. (low). Range from good-form demonstrations (72 attempts in 6 clips); reliability C.
- 3. **swinging_too_hard** (medium, agreed by 3 of 5 runs): Keep the take-back and swing short and compact. Touch the ball softly instead of swinging through it with pace.. Target: height.wrist.dom between -1.0007 and 0.3201 at L1. Wrong if above: A big, high take-back and a full swing with the racket arm lifted well away from the body, as for a normal groundstroke. The ball flies deep with pace. (medium); below: The racket hand hardly lifts, so the player pokes or pushes at the ball with no controlled slicing motion. (low). Range from good-form demonstrations (72 attempts in 6 clips); reliability C.
- 4. **no_footwork_through_shot** (low, agreed by 3 of 5 runs): Keep the feet moving through the shot, with a step into the ball and a continuing step afterward. Do not stop before contact.. Target: dist.stance_width between 0.0437 and 2.9193 at L1. Wrong if below: Feet planted close together and static at contact, so the arm does all the work. (low); above: A very wide, braced stance that stops the player moving on after the shot. (low). Range from good-form demonstrations (72 attempts in 6 clips); reliability C.
- 5. **poor_recovery_after_shot** (medium, agreed by 5 of 5 runs): After the shot, keep moving forward and recover toward the net or a good covering position. Do not stay on the baseline.. Target: fwd.trunk_shift at least -0.1321 at L2. Wrong if below: The player stays back and upright, and is out of position for a lob or a reply. (medium). Range from good-form demonstrations (72 attempts in 6 clips); reliability C.

## What coaches say (12 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **wrong_tactical_moment** (form; 5 of 12, strong): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor. Coaches disagree: Source 0 allows a safer, longer version when the opponent is stretched wide, while 9 prefers a neutralising slice when defending.
- **hit_from_deep_or_unprepared** (form; 4 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (waiting_on_ball). Coaches disagree: Source 0 says the drop shot can be played from around the baseline, while 7 says hitting it from the baseline is harder.
- **swinging_too_hard** (form; 4 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (swinging_too_hard).
- **telegraphing_shot** (form; 4 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (telegraphing_shot). Coaches disagree: Source 1 suggests running in with a topspin grip and changing late, while 8 says to use the normal forehand or backhand grip until the last moment.
- **ball_flight_too_high** (form; 3 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection to track the trajectory over the net. Coaches disagree: Source 9 says to aim higher for more backspin, and 6 and 8 say to keep the ball low.
- **waiting_on_ball** (form; 3 of 12, some): measured by the camera (waiting_on_ball).
- **aim_too_short** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection for landing spot relative to net.
- **gripping_too_tight** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **nervous_or_rushed** (form; 2 of 12, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor.
- **no_footwork_through_shot** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (no_footwork_through_shot).
- **poor_direction_placement** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection for landing spot and racket tracking for direction.
- **poor_recovery_after_shot** (form; 2 of 12, some): only a proxy is measured (a test that goes with it, not the thing itself) (poor_recovery_after_shot). Coaches disagree: Source 7 allows staying back at three-quarter court, while 8 says to follow the shot to the net.
- **too_little_backspin** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket and ball detection for racket path and ball spin. Coaches disagree: Source 0 prefers the ball to spin forward after the bounce, and 5 says only a little backspin is needed.
- **too_much_backspin_open_face** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket detection for face angle. Coaches disagree: Source 6 says to add more backspin even if the ball goes too high, and 9 says to aim higher for more backspin.
- **unsuitable_incoming_ball** (form; 2 of 12, some): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection for type, height and spin of the incoming ball. Coaches disagree: Source 0 says slice, dead and high balls are poor choices and 9 says contact should be around chest height, while 8 says to hit off a soft or slightly high ball and 10 builds the shot off a backhand slice.
- **counter_drop_when_stretched** (form; 1 of 12, single): a body feature can show it but no objective tests it (no agreed target): reach.wrist.dom and dist.stance_width show stretch, no test uses them.
- **cross_court_reply_to_drop_shot** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: ball detection for the direction of the reply.
- **poor_absorption_control** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: racket and ball detection for ball rebound off the strings and racket movement.
- **racket_back_while_running** (form; 1 of 12, single): would need a new body feature: dominant wrist fore-aft offset relative to the shoulder/trunk (wrist behind body).
- **same_grip_through_shot** (form; 1 of 12, single): the camera can see it, but it needs a hand or racket/ball tracker that does not exist yet: hand landmarks to see the grip. Coaches disagree: Sources 4 and 8 say to keep the normal forehand or backhand grip until the last moment.

Good form, as coaches give it:

- Play it from an attacking position, stepping into the court, when the opponent is pushed back or has hit short. (6 of 12)
- Go under or behind the ball with a slightly open face and a little backspin so it dies after landing. (6 of 12)
- Prepare like a normal forehand or backhand, or like the slice, and disguise the shot until the last moment. (5 of 12)
- Change grip late to a continental or neutral grip, which helps you get under the ball. (4 of 12)
- Use a short, soft, simple swing with little or no backswing, like a volley. (4 of 12)
- Keep the ball low and have its peak on your side of the net, so it lands short. (4 of 12)

## Principles (why good form works; offered rarely, never during an attempt)

- **travel_into_the_ball** (coaching_consensus, 3 of 3 runs; explains waiting_on_ball, no_footwork_through_shot, poor_recovery_after_shot, hit_from_deep_or_unprepared, racket_back_while_running): Moving toward the net as you meet the ball lets your body's momentum do the work, so the shot needs very little arm effort. Taking the ball early, while still moving, also shortens the opponent's reaction time and keeps you from reaching or waiting. Cue handle: Keep travelling forward so the ball is met early and you keep moving afterward..
- **small_swing_soft_touch** (coaching_consensus, 3 of 3 runs; explains swinging_too_hard, gripping_too_tight, poor_absorption_control, nervous_or_rushed): A drop shot needs very little ball speed, so a short take-back and a short slicing motion give control. A big swing adds pace that you then have to cancel out. A soft, absorbing contact with a relaxed grip lets the ball lose its speed on the strings. Cue handle: Let the ball lose its pace on contact, so it feels cushioned and soft..
- **disguise_with_matching_preparation** (contested, 3 of 3 runs; explains telegraphing_shot, same_grip_through_shot): The shot works best when the opponent cannot read it. If the preparation looks like your normal slice or groundstroke until late, the opponent stays back and the ball has time to land short. How to handle the grip while doing this is something coaches disagree on. Cue handle: Make the preparation look like your usual stroke until the last moment.. Competing views: Run in with a topspin-style grip and change late (Source 1).; Keep the normal forehand or backhand grip until the last moment (Sources 4 and 8)..
- **low_flight_with_light_backspin** (contested, 3 of 3 runs; explains ball_flight_too_high, too_little_backspin, too_much_backspin_open_face, aim_too_short): A gentle slicing contact gives the ball backspin, which helps it stop after it lands. The ball should clear the net with a low, short arc. The amount of backspin and the height of the flight are matters of debate among coaches. Cue handle: Make the ball just clear the net and die softly after it bounces.. Competing views: Aim higher to get more backspin (Source 9; Source 6 adds more backspin even if the ball goes too high).; Keep the ball low, with only a little backspin (Sources 5, 6 and 8)..

## Check against labelled mistake videos (8 videos, 112 attempts, 94 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| swinging_too_hard | 3 / 1 | 0 / 0 |
| poor_recovery_after_shot | 1 / 1 | 0 / 0 |
| racket_back_while_running | 0 / 0 | 1 / 1 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| waiting_on_ball | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| telegraphing_shot | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| swinging_too_hard | 0 / 3 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| no_footwork_through_shot | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| poor_recovery_after_shot | 0 / 1 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.wrist.dom, angle.shoulder.dom, height.wrist_mid, dist.wrist_width, reach.wrist.dom
Attempts found as: height.wrist.dom rises (to at least -0.3). Typical size of the last event 1.37, lasting 2.18 s; smaller ones (below 0.548) or much longer or shorter ones are not attempts.

Footage when it was last grown (before any later downloads; the numbers at the top are current): 386 clear attempts in 16 of 16 clips after 1 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| mistake_analysis | 7 | 84 | mistakes 19, mixed 65 |
| coach_demo | 6 | 68 | good_form 57, mixed 11 |
| instruction_talk | 3 | 18 | unknown 18 |
| practice_session | 3 | 17 | good_form 8, unknown 9 |
| pro_footage | 2 | 16 | good_form 16 |
| other | 0 | 0 |  |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| waiting_on_ball | 2% (6 clips) | 12% (14 clips) | everyday footage departs more: the objective picks up a difference from good form |
| telegraphing_shot | 11% (6 clips) | 4% (14 clips) | demos depart more: doubtful |
| swinging_too_hard | 5% (6 clips) | 5% (14 clips) | no difference: everyone is inside, or this measure does not separate them |
| no_footwork_through_shot | 5% (6 clips) | 8% (14 clips) | no difference: everyone is inside, or this measure does not separate them |
| poor_recovery_after_shot | 2% (6 clips) | 13% (14 clips) | everyday footage departs more: the objective picks up a difference from good form |

## Phases

- prepare_and_contact: L0 to L1
- soft_follow_and_recover: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip JXMXLy82_Ng: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 202 of 231 attempts (tolerance 2.092). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (13G2saUuzsc, 5wdrcvQQJMg, 7QsGRqgADsA, Cx7UAObRReM, FNvMbMrjs6s, HDQosGUWAdM, ObJQ7R9Koi8, TmH-ZT_PgeA, bWzBO613Pb8, eu3tJ5e9UBw, kpVuLzQghiM, piiCNvvcQLg, wQX8B7wYip4).

| clip | attempts found | kept | note |
|---|---|---|---|
| 13G2saUuzsc | 15 | 15 | seed |
| 5wdrcvQQJMg | 15 | 15 | seed |
| 7QsGRqgADsA | 15 | 12 | seed |
| AaZGB8VTt2A | 8 | 8 |  |
| BljEo-vSpPI | 4 | 4 |  |
| Cx7UAObRReM | 3 | 3 | seed |
| FNvMbMrjs6s | 15 | 15 | seed |
| FqCoCN8xQvg | 13 | 0 | clip does not show the movement |
| HDQosGUWAdM | 8 | 8 | seed |
| JXMXLy82_Ng | 15 | 9 |  |
| ObJQ7R9Koi8 | 4 | 4 | seed |
| TVdBFrYW-es | 15 | 11 |  |
| TmH-ZT_PgeA | 5 | 5 | seed |
| avJgdX-feEw | 15 | 13 |  |
| bWzBO613Pb8 | 5 | 5 | seed |
| eu3tJ5e9UBw | 15 | 15 | seed |
| gh_GAi0F2nM | 15 | 15 |  |
| kpVuLzQghiM | 6 | 6 | seed |
| mO6XiArAjPI | 15 | 15 |  |
| piiCNvvcQLg | 10 | 10 | seed |
| wQX8B7wYip4 | 15 | 14 | seed |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): height.wrist.dom=-0.697, height.wrist_mid=-0.688, angle.shoulder.dom=26.404, dist.wrist_width=1.136, reach.wrist.dom=0.853, height.wrist.non=-0.697, angle.shoulder.non=27.535, angle.elbow.dom=126.448, angle.shoulder_hip_twist=0.549, angle.knee.non=156.079
- L1 (t=0.388): height.wrist.dom=-0.285, height.wrist_mid=-0.424, angle.shoulder.dom=46.428, dist.wrist_width=1.34, reach.wrist.dom=0.802, height.wrist.non=-0.549, angle.shoulder.non=33.874, angle.elbow.dom=121.281, angle.shoulder_hip_twist=0.299, angle.knee.non=152.823
- L2 (t=1.0): height.wrist.dom=-0.707, height.wrist_mid=-0.694, angle.shoulder.dom=26.916, dist.wrist_width=1.228, reach.wrist.dom=0.861, height.wrist.non=-0.715, angle.shoulder.non=28.954, angle.elbow.dom=128.508, angle.shoulder_hip_twist=0.235, angle.knee.non=158.37

## Per clip

| clip | attempts used | believable frames | view yaw | height.wrist.dom at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| 13G2saUuzsc | 15 | 93% | 7 | -0.7 | -0.61 / -0.26 / 0.12 |
| 5wdrcvQQJMg | 15 | 97% | 32 | -0.72 | -0.48 / -0.13 / 0.17 |
| 7QsGRqgADsA | 12 | 93% | 22 | -0.74 | -0.54 / -0.35 / -0.04 |
| 9mRn18OxcNs | 1 | 100% | 50 | -0.3 | -0.23 / -0.23 / -0.23 |
| AaZGB8VTt2A | 8 | 80% | 41 | -0.71 | -0.57 / -0.32 / 0.03 |
| BljEo-vSpPI | 4 | 77% | 14 | -0.58 | -0.44 / -0.21 / 0.29 |
| Cx7UAObRReM | 3 | 76% | 36 | -0.8 | -0.6 / -0.59 / -0.52 |
| FNvMbMrjs6s | 15 | 99% | 51 | -0.64 | -0.68 / -0.28 / -0.02 |
| FqCoCN8xQvg | 0 | 69% | 33 |  |  |
| HDQosGUWAdM | 8 | 92% | 6 | -0.81 | -0.73 / -0.62 / -0.21 |
| JXMXLy82_Ng | 9 | 100% | 27 | -0.97 | -0.63 / -0.16 / 0.88 |
| ObJQ7R9Koi8 | 4 | 97% | 7 | -0.64 | -0.59 / -0.24 / 0.28 |
| QAcBgVZheDo | 0 | 100% | 22 |  |  |
| TVdBFrYW-es | 11 | 99% | 15 | -0.73 | -0.71 / -0.3 / -0.18 |
| TmH-ZT_PgeA | 5 | 93% | 25 | -0.67 | -0.72 / -0.26 / -0.26 |
| avJgdX-feEw | 13 | 98% | 7 | -0.71 | -0.68 / -0.5 / 0.19 |
| bWzBO613Pb8 | 5 | 91% | 62 | -0.86 | -0.73 / -0.49 / -0.0 |
| eu3tJ5e9UBw | 15 | 88% | 7 | -0.7 | -0.55 / -0.29 / 0.0 |
| gh_GAi0F2nM | 15 | 98% | 28 | -0.61 | -0.53 / -0.13 / 0.3 |
| kpVuLzQghiM | 6 | 80% | 42 | -0.73 | -0.67 / -0.55 / -0.16 |
| mO6XiArAjPI | 15 | 99% | 55 | -0.55 | -0.42 / -0.14 / 0.04 |
| piiCNvvcQLg | 10 | 89% | 5 | -0.67 | -0.73 / -0.49 / -0.26 |
| wQX8B7wYip4 | 14 | 96% | 8 | -0.78 | -0.49 / -0.08 / 0.25 |

## Vocabulary proposals

- trackable: racket and ball position (Ball height over the net, bounce spot and spin cannot be seen from body features. They are needed to judge ball_flight_too_high, aim_too_short, poor_direction_placement and too_little_backspin.)
- measurement: racket face angle at contact (Needed to judge whether the face is opened too wide (too_much_backspin_open_face) or too closed.)
- measurement: grip tension or wrist stiffness (gripping_too_tight cannot be seen with the registered features.)
- feature: opponent court position (wrong_tactical_moment and hit_from_deep_or_unprepared depend on where the opponent and the player are on the court.)
- feature: racket-head path (high to low) relative to the ball (Needed to judge slice or backspin and the length of the swing directly.)
