# Factory report: bodyweight_squat

Clips found: 67 (usable for attempts: 34). Attempts: 241.
Confidence tier: **low**. Checks: 8 pass, 0 fail, 1 not testable.

## Checks

- [PASS] 1. format: valid against the v0.7 schema
- [PASS] 2. vocabulary: all features and measurements are registered and active
- [PASS] 3. time budget: every test's time budget can be met by its path
- [PASS] 4. recognition: recall 0.96 (leave-one-clip-out), false accepts 0.02 (shape alone 0.02), by view {'front/back (<30)': 0.9736842105263158, 'oblique (30-60)': 0.9306930693069307, 'side (>60)': 1.0}
- [PASS] 5. plausibility: all thresholds and key poses are inside plausible ranges
- [n/a ] 6. discrimination: 0/1 objectives with enough labelled examples separate good from faulty on videos left out (AUC>=0.75); too few wrong examples in different videos to test: ['knees_caving_in']; 6 without enough labels
- [PASS] 7. outcome links: 5 links, 5 prior-only (no data to test them yet)
- [PASS] 8. agreement: agreement 0.72 across 5 runs
- [PASS] 9. cross-references: ids, landmarks, priorities and requires are consistent

## Objectives (in priority order)

Only objectives whose feature at least 3 of 5 independent model runs also test are kept.

- 1. **knees_caving_in** (high, agreed by 5 of 5 runs): Keep the knees tracking out over the toes, in line with the hip and ankle, all the way down.. Target: dev.knee_inward.dom at most -0.0313 at L1. Wrong if above: The knee drifts inward past the line from hip to ankle at the bottom. (high). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 2. **heels_lift_ankle_limit** (medium, agreed by 5 of 5 runs): Keep the whole foot flat on the floor throughout the squat.. Target: height.heel.dom at most 0.2196 at L1. Wrong if above: The heel rises off the floor at the bottom, with the weight pushed onto the toes. (medium). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 3. **forward_chest_lean** (medium, agreed by 5 of 5 runs): Keep the chest up and the trunk steady as you go down, with only the natural lean needed to balance over the feet.. Target: angle.trunk_lean between 5.3709 and 59.6542 at L1. Wrong if above: The chest drops and the torso folds or rocks forward over the thighs at the bottom. (medium); below: Torso held very upright; usually acceptable, though some coaches want a more inclined torso. (low). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 4. **incomplete_range** (low, agreed by 3 of 5 runs): Lower the hips to a full, consistent depth at the bottom of every rep.. Target: height.hip at most 1.1485 at L1. Wrong if above: The person stops high, with the hips well above knee level, short of the usual depth. (low). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 5. **full_lockout** (low, agreed by 4 of 5 runs): Stand fully tall at the top of each rep with the hips and knees extended.. Target: angle.hip.dom at least 153.4874 at L2. Wrong if below: The person stays partly bent at the hips and does not stand fully upright at the top. (low). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 6. **stance_not_matched_to_hips** (low, agreed by 5 of 5 runs): Set the feet at a width that suits your own hips, about hip to shoulder width or a little wider.. Target: dist.stance_width between 1.1515 and 2.3089 at L0. Wrong if below: The feet are very close together, which limits depth and balance. (low); above: A very wide or sumo stance for a standard squat. (low). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.
- 7. **toe_angle_wrong** (low, agreed by 3 of 5 runs): Set the toes at a consistent, comfortable angle (straight ahead to slightly turned out) and keep them there during the rep.. Target: rot.foot_turnout.dom between -6.7974 and 38.6789 at L0. Wrong if below: The toes point straight ahead or inward, which can limit depth for some people. (low); above: The toes are turned out a lot, or screw outward during the rep. (low). Range from good-form demonstrations (47 attempts in 9 clips); reliability C.

## What coaches say (11 coaching videos)

Faults they name, most-cited first (kind; how many sources; what the camera can do about it):

- **forward_chest_lean** (form; 5 of 11, strong): measured by the camera (forward_chest_lean).
- **knees_caving_in** (safety; 5 of 11, strong): measured by the camera (knees_caving_in).
- **lumbar_rounding_butt_wink** (safety; 4 of 11, some): would need a new body feature: lumbar spine / pelvic tilt angle (pelvis tuck relative to spine) at the bottom; the skeleton has only a trunk line, not a lumbar curve.
- **heels_lift_ankle_limit** (form; 3 of 11, some): measured by the camera (heels_lift_ankle_limit).
- **stance_not_matched_to_hips** (form; 3 of 11, some): only a proxy is measured (a test that goes with it, not the thing itself) (stance_not_matched_to_hips). Coaches disagree: Source 5 rejects wide sumo stances, while source 6 recommends a wider stance for long femurs; all agree the width should suit the individual.
- **arm_counterbalance** (form; 2 of 11, some): a body feature can show it but no objective tests it (no agreed target): reach.wrist.dom / height.wrist_mid / angle.shoulder.dom show arms reaching forward; no objective tests it. Coaches disagree: Sources 8 and 10 put the arms out in front as part of normal technique.
- **falling_backward_weight_on_heels** (safety; 2 of 11, some): a body feature can show it but no objective tests it (no agreed target): fwd.trunk_shift (shoulder centre vs ankle) and height.heel show balance shift; no objective tests it.
- **hips_rise_first_good_morning** (safety; 2 of 11, some): only a proxy is measured (a test that goes with it, not the thing itself) (forward_chest_lean).
- **incomplete_range** (form; 2 of 11, some): measured by the camera (incomplete_range).
- **poor_bracing_and_breathing** (form; 2 of 11, some): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor. Coaches disagree: Source 3 says to brace on the way down and breathe out as you finish coming up.
- **toe_angle_wrong** (form; 2 of 11, some): only a proxy is measured (a test that goes with it, not the thing itself) (toe_angle_wrong). Coaches disagree: Source 8 treats toes turning out as a compensation and wants them forward. Source 9 says toes straight ahead is the fault and wants about 30 degrees out.
- **arching_lower_back** (form; 1 of 11, single): would need a new body feature: lumbar extension / spine curvature angle at the bottom; trunk lean alone does not show lower back arch.
- **back_too_vertical** (form; 1 of 11, single): only a proxy is measured (a test that goes with it, not the thing itself) (forward_chest_lean). Coaches disagree: Source 9 wants a torso inclined about 45 degrees, but sources 3, 6, 8 and 10 want an upright torso and chest.
- **feet_out_knees_straight** (form; 1 of 11, single): only a proxy is measured (a test that goes with it, not the thing itself) (toe_angle_wrong).
- **forcing_depth_passively** (form; 1 of 11, single): only a proxy is measured (a test that goes with it, not the thing itself) (incomplete_range).
- **hip_shift_leg_imbalance** (form; 1 of 11, single): a body feature can show it but no objective tests it (no agreed target): lat.com_shift shows lateral shift; no objective tests it.
- **knees_held_back** (form; 1 of 11, single): a body feature can show it but no objective tests it (no agreed target): fwd.knee_over_toe.dom/non and angle.shin_lean show knee travel; no objective tests it. Coaches disagree: Source 3 calls knees shooting far past the toes bad for the knees, though it accepts this at low depth. Sources 0, 1, 5 and 7 want the knees to travel forward.
- **knees_too_far_forward** (form; 1 of 11, single): a body feature can show it but no objective tests it (no agreed target): fwd.knee_over_toe.dom/non and angle.shin_lean show it; no objective tests it. Coaches disagree: Source 0 says holding the knees back is the fault, and sources 1, 5 and 7 want the knees travelling forward.
- **no_hip_hinge** (form; 1 of 11, single): a body feature can show it but no objective tests it (no agreed target): angle.hip.dom vs angle.knee.dom timing shows hinge order; no objective tests it.
- **pinchy_tight_hips** (form; 1 of 11, single): not visible to any camera (feel, tension, breathing, sound): ask the learner or use another sensor. Coaches disagree: Source 7 says constant hip stretching is not the answer for most people.

Tested in this entry but named by no coach: full_lockout.

Good form, as coaches give it:

- Set feet about shoulder width, or just outside hip width, and tune the width to your own hips and limb proportions. (8 of 11)
- Turn the toes out slightly to open the hips, with knees tracking the same way (one coach prefers toes straight ahead). (6 of 11)
- Push the knees out so they track in line with the toes and do not cave in. (6 of 11)
- Hold a light weight at the chest or raise the arms to aid balance and chest position, and build depth gradually, e.g. with heel elevation or support. (6 of 11)
- Keep the whole foot grounded, with weight balanced over the midfoot and not on the heels or toes. (5 of 11)
- Let the knees travel forward over the toes as needed for depth and balance. (5 of 11)

## Check against labelled mistake videos (28 videos, 259 attempts, 134 judged not to be attempts)

What the model saw in the frames of each attempt (visibly present or absent; the rest could not be judged):

| coach fault | present (attempts / videos) | absent (attempts / videos) |
|---|---|---|
| arm_counterbalance | 42 / 14 | 12 / 4 |
| forward_chest_lean | 18 / 11 | 6 / 4 |
| hips_rise_first_good_morning | 4 / 3 | 0 / 0 |
| knees_caving_in | 3 / 3 | 32 / 9 |
| incomplete_range | 2 / 2 | 31 / 14 |
| lumbar_rounding_butt_wink | 2 / 1 | 5 / 2 |
| arching_lower_back | 0 / 0 | 4 / 1 |
| falling_backward_weight_on_heels | 0 / 0 | 5 / 4 |
| heels_lift_ankle_limit | 0 / 0 | 22 / 10 |

| objective | right / wrong attempts | videos | AUC | right on videos left out | verdict |
|---|---|---|---|---|---|
| knees_caving_in | 32 / 3 | 9 / 3 | 0.88 |  | separates on these attempts but the wrong ones come from too few videos to test on others; range kept from good form demonstrations |
| heels_lift_ankle_limit | 22 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| forward_chest_lean | 0 / 18 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| incomplete_range | 0 / 2 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| full_lockout | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| stance_not_matched_to_hips | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |
| toe_angle_wrong | 0 / 0 | | | | not enough labelled examples (needs 3 of each); range from good form demonstrations |

Movement characterised by: height.hip, angle.knee.dom, angle.hip.dom, angle.trunk_lean
Attempts found as: height.hip falls. Typical size of the last event 1.039, lasting 3.9 s; smaller ones (below 0.415) or much longer or shorter ones are not attempts.

Footage: 872 clear attempts in 40 of 43 clips after 2 round(s) of searching; target reached.

Footage by kind of source (clips and attempts that ended up in the entry):

| kind | clips | attempts | shows |
|---|---|---|---|
| other | 11 | 67 | unknown 67 |
| mistake_analysis | 20 | 66 | mixed 66 |
| coach_demo | 11 | 49 | good_form 49 |
| practice_session | 3 | 39 | unknown 39 |
| instruction_talk | 5 | 36 | unknown 36 |

Sanity check of the target ranges without labels. Each range comes from demonstrations of good form (each demonstration clip is judged against a range made from the other demonstration clips); the table shows the share of attempts outside the range, averaged over clips:

| objective | good-form demos | everyday footage | reading |
|---|---|---|---|
| knees_caving_in | 6% (9 clips) | 5% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| heels_lift_ankle_limit | 0% (9 clips) | 5% (25 clips) | everyday footage departs more: the objective picks up a difference from good form |
| forward_chest_lean | 11% (9 clips) | 9% (25 clips) | no difference: everyone is inside, or this measure does not separate them |
| incomplete_range | 0% (9 clips) | 6% (25 clips) | everyday footage departs more: the objective picks up a difference from good form |
| full_lockout | 2% (9 clips) | 24% (25 clips) | everyday footage departs more: the objective picks up a difference from good form |
| stance_not_matched_to_hips | 15% (9 clips) | 39% (25 clips) | everyday footage departs more: the objective picks up a difference from good form |
| toe_angle_wrong | 7% (9 clips) | 11% (25 clips) | no difference: everyone is inside, or this measure does not separate them |

## Phases

- descent: L0 to L1
- ascent: L1 to L2

## Alignment

Clips whose repetitions start at different points of the cycle were rotated to match reference clip JTMFAYNoAxM: .

## Curation (only attempts that look like the repeated movement are kept)

Kept 245 of 277 attempts (tolerance 2.226). Seed: typical attempt found by repeatedly keeping the closest half of all attempts (3GTp-HYp4MY, 4pI_6Wi6okE, AhfgIM8YWBY, Dua9h7wsFVI, E2z5zK5V-MM, GK84GSUGUW4, HFnSsLIB7a4, JTMFAYNoAxM, MnboqiN-4ng, P-yaD24bUE8, QKKXd6celO0, ckvHymGK3s0, m0GcZ24pK6k, niWFDg6wyD0, ovxI_waWQcI, p5nE_Yahbto, tfqMxAhSfE8, vW99IkimKDI).

| clip | attempts found | kept | note |
|---|---|---|---|
| 0euDDJu6GnQ | 15 | 15 |  |
| 21ksLeoHL_4 | 2 | 0 |  |
| 3GTp-HYp4MY | 2 | 2 | seed |
| 45n9jUSY0Sg | 2 | 0 |  |
| 4pI_6Wi6okE | 10 | 10 | seed |
| 6BoGcuIkakE | 2 | 1 |  |
| 965Fwq2aVIo | 14 | 10 |  |
| AhfgIM8YWBY | 2 | 2 | seed |
| Dua9h7wsFVI | 15 | 15 | seed |
| E2z5zK5V-MM | 5 | 5 | seed |
| GK84GSUGUW4 | 2 | 1 | seed |
| HFnSsLIB7a4 | 15 | 15 | seed |
| JTMFAYNoAxM | 7 | 7 | seed |
| M6_dNPSP2dQ | 6 | 5 |  |
| MODXeW-a_uc | 13 | 8 |  |
| MnPuHBh48bA | 4 | 2 |  |
| MnboqiN-4ng | 15 | 14 | seed |
| P-yaD24bUE8 | 2 | 2 | seed |
| QKKXd6celO0 | 2 | 1 | seed |
| U3HlEF_E9fo | 8 | 8 |  |
| YN_XnIhEjQw | 2 | 2 |  |
| YaXPRqUwItQ | 5 | 5 |  |
| YjfXBCJtKAQ | 2 | 0 |  |
| aOVC5wOPih0 | 2 | 1 |  |
| ckvHymGK3s0 | 4 | 4 | seed |
| ektFAcztVLc | 3 | 2 |  |
| jmqbh-i2SGQ | 15 | 15 |  |
| m0GcZ24pK6k | 2 | 2 | seed |
| ndhOueWuCB0 | 15 | 10 |  |
| niWFDg6wyD0 | 12 | 11 | seed |
| nmUof3vszxM | 2 | 2 |  |
| o4D4LqdpYfQ | 15 | 14 |  |
| ovxI_waWQcI | 4 | 4 | seed |
| p5nE_Yahbto | 4 | 4 | seed |
| plvV-xAQZRo | 2 | 2 |  |
| rMvwVtlqjTE | 9 | 9 |  |
| tfqMxAhSfE8 | 15 | 15 | seed |
| u0r0b6NK7HY | 3 | 2 |  |
| vW99IkimKDI | 12 | 12 | seed |
| xqvCmoLULNY | 2 | 2 |  |
| zdrYdfrWn1c | 4 | 4 |  |

## What the clips show (landmarks of one attempt, median values)

- L0 (t=0.0): angle.hip.dom=163.337, angle.hip.non=160.655, angle.knee.non=162.338, angle.knee.dom=164.78, height.hip=1.599, dev.knee_inward.dom=0.06, angle.trunk_lean=11.267, angle.shoulder.non=31.263, dev.knee_inward.non=0.039, angle.shoulder.dom=26.803
- L1 (t=0.469): angle.hip.dom=67.413, angle.hip.non=71.906, angle.knee.non=72.495, angle.knee.dom=74.721, height.hip=0.745, dev.knee_inward.dom=-0.579, angle.trunk_lean=31.701, angle.shoulder.non=70.343, dev.knee_inward.non=-0.316, angle.shoulder.dom=66.821
- L2 (t=1.0): angle.hip.dom=163.957, angle.hip.non=161.936, angle.knee.non=162.571, angle.knee.dom=165.453, height.hip=1.601, dev.knee_inward.dom=0.071, angle.trunk_lean=12.242, angle.shoulder.non=30.441, dev.knee_inward.non=0.032, angle.shoulder.dom=26.796

## Per clip

| clip | attempts used | believable frames | view yaw | height.hip at start (median) | at L1 (p10 / median / p90) |
|---|---|---|---|---|---|
| -CiWQ2IvY34 | 1 | 79% | 25 | 0.63 | 0.23 / 0.23 / 0.23 |
| 0KtrNQre5rQ | 0 | 84% | 17 |  |  |
| 0euDDJu6GnQ | 15 | 94% | 44 | 1.62 | 0.47 / 0.53 / 0.55 |
| 1DY6gAVqLC0 | 1 | 98% | 33 | 1.52 | 1.07 / 1.07 / 1.07 |
| 21ksLeoHL_4 | 0 | 88% | 22 |  |  |
| 3GTp-HYp4MY | 2 | 100% | 5 | 1.41 | 0.81 / 0.84 / 0.87 |
| 45n9jUSY0Sg | 0 | 59% | 28 |  |  |
| 4pI_6Wi6okE | 10 | 93% | 3 | 1.62 | 0.94 / 1.01 / 1.05 |
| 6BoGcuIkakE | 1 | 87% | 4 | 1.58 | 1.05 / 1.05 / 1.05 |
| 965Fwq2aVIo | 10 | 61% | 33 | 1.71 | 0.51 / 0.6 / 0.65 |
| AhfgIM8YWBY | 2 | 98% | 50 | 1.52 | 0.62 / 0.67 / 0.73 |
| Dua9h7wsFVI | 15 | 96% | 34 | 1.58 | 0.93 / 0.94 / 0.95 |
| E2z5zK5V-MM | 5 | 98% | 8 | 1.56 | 0.85 / 0.88 / 0.91 |
| EG4YKX3-Ygk | 0 | 68% | 32 |  |  |
| FvvuN7wZFlA | 0 | 95% | 25 |  |  |
| GK84GSUGUW4 | 1 | 85% | 5 | 1.72 | 0.87 / 0.87 / 0.87 |
| H1H1WKSm5CU | 1 | 91% | 45 | 0.63 | 1.46 / 1.46 / 1.46 |
| HFnSsLIB7a4 | 15 | 68% | 37 | 1.69 | 0.42 / 0.51 / 0.65 |
| HQfN0ddIpzg | 1 | 86% | 14 | 1.46 | 0.56 / 0.56 / 0.56 |
| Ihc9Gg5MrAk | 0 | 88% | 13 |  |  |
| JTMFAYNoAxM | 7 | 87% | 5 | 1.56 | 0.59 / 0.79 / 1.15 |
| LG0801vRVek | 0 | 77% | 6 |  |  |
| M6_dNPSP2dQ | 5 | 86% | 4 | 1.66 | 0.68 / 1.19 / 1.46 |
| MODXeW-a_uc | 8 | 70% | 48 | 1.65 | 0.58 / 0.64 / 0.66 |
| MnPuHBh48bA | 2 | 95% | 14 | 1.66 | 0.99 / 1.05 / 1.12 |
| MnboqiN-4ng | 14 | 96% | 4 | 1.62 | 0.84 / 0.9 / 0.97 |
| NU7ajbIFH58 | 0 | 81% | 30 |  |  |
| P-yaD24bUE8 | 2 | 95% | 31 | 1.57 | 0.9 / 0.91 / 0.92 |
| QKKXd6celO0 | 1 | 53% | 12 | 1.35 | 0.85 / 0.85 / 0.85 |
| S9XUYbQmEQo | 0 | 100% | 8 |  |  |
| SZXOPRVP1Oc | 1 | 100% | 76 | 1.56 | 1.37 / 1.37 / 1.37 |
| U3HlEF_E9fo | 8 | 73% | 26 | 1.58 | 0.61 / 0.65 / 0.67 |
| XQeAXoD-Tdc | 0 | 99% | 66 |  |  |
| Y7QEmD5MgDQ | 1 | 93% | 37 | 0.38 | 0.52 / 0.52 / 0.52 |
| YN_XnIhEjQw | 2 | 73% | 17 | 1.64 | 0.42 / 0.44 / 0.46 |
| YaXPRqUwItQ | 5 | 70% | 15 | 1.55 | 0.67 / 0.75 / 0.77 |
| YjfXBCJtKAQ | 0 | 93% | 7 |  |  |
| aOVC5wOPih0 | 1 | 91% | 43 | 1.51 | 0.93 / 0.93 / 0.93 |
| ckUsHNZjZrQ | 1 | 75% | 30 | 1.63 | 0.99 / 0.99 / 0.99 |
| ckvHymGK3s0 | 4 | 85% | 22 | 1.48 | 0.78 / 0.81 / 0.84 |
| dYY28h8OMSg | 0 | 100% | 11 |  |  |
| ektFAcztVLc | 2 | 66% | 33 | 1.69 | 0.5 / 0.5 / 0.51 |
| fLaNf82-6ik | 0 | 55% | 31 |  |  |
| gCOKozKJpEY | 0 | 87% | 27 |  |  |
| gsNoPYwWXeM | 1 | 85% | 57 | 1.07 | 0.81 / 0.81 / 0.81 |
| jmqbh-i2SGQ | 15 | 92% | 15 | 1.68 | 0.52 / 0.56 / 0.58 |
| kMsfO-EOjWY | 1 | 79% | 46 | 0.5 | 0.36 / 0.36 / 0.36 |
| l2cHd2dLSzY | 0 | 99% | 10 |  |  |
| m0GcZ24pK6k | 2 | 78% | 78 | 1.59 | 0.91 / 0.97 / 1.02 |
| mmb618X9Ieg | 1 | 67% | 68 | 1.57 | 0.9 / 0.9 / 0.9 |
| ndhOueWuCB0 | 10 | 71% | 75 | 1.59 | 0.69 / 0.77 / 0.87 |
| niWFDg6wyD0 | 11 | 78% | 16 | 1.54 | 0.7 / 0.94 / 0.99 |
| nmUof3vszxM | 2 | 90% | 4 | 1.56 | 0.66 / 0.93 / 1.2 |
| o4D4LqdpYfQ | 14 | 78% | 62 | 1.46 | 0.59 / 0.75 / 0.96 |
| ovxI_waWQcI | 4 | 87% | 8 | 1.55 | 0.87 / 0.9 / 0.91 |
| p5nE_Yahbto | 4 | 90% | 52 | 1.64 | 0.41 / 0.66 / 0.79 |
| plvV-xAQZRo | 2 | 97% | 6 | 1.39 | 0.55 / 0.55 / 0.55 |
| rMvwVtlqjTE | 9 | 88% | 48 | 1.53 | 0.43 / 0.5 / 0.65 |
| tfqMxAhSfE8 | 15 | 99% | 33 | 1.7 | 0.95 / 0.95 / 0.96 |
| u0r0b6NK7HY | 2 | 94% | 46 | 1.39 | 0.62 / 0.63 / 0.63 |
| vW99IkimKDI | 12 | 85% | 24 | 1.55 | 0.47 / 0.48 / 0.52 |
| wUcbA9TKtmk | 1 | 89% | 9 | 1.02 | 0.96 / 0.96 / 0.96 |
| x1FCpVZYrUs | 0 | 99% | 33 |  |  |
| x5tcKrm092A | 0 | 99% | 10 |  |  |
| x921teWPTfM | 1 | 99% | 32 | 1.47 | 0.89 / 0.89 / 0.89 |
| xqvCmoLULNY | 2 | 86% | 33 | 1.58 | 0.79 / 0.88 / 0.97 |
| zdrYdfrWn1c | 4 | 100% | 4 | 1.55 | 1.08 / 1.11 / 1.16 |

## Vocabulary proposals

- feature: angle.lumbar_flexion (pelvic tilt / spine curvature) (Lumbar rounding or butt wink at the bottom, and arching of the lower back, cannot be seen with the current features, which have no spine curvature or pelvis tilt.)
- feature: timing.hip_vs_shoulder_rise (The 'hips rise first' fault (good-morning squat) needs the relative timing of hip and shoulder rise during the ascent.)
- measurement: centre_of_pressure_front_back (Weight too far on the heels or toes, and tipping backward, need foot pressure or a balance estimate that the body-frame features cannot give.)
- feature: knee_toe_direction_alignment (A fault where the feet turn out but the knees stay pointing forward needs the knee direction compared with the foot direction.)
- measurement: breathing_and_bracing (Bracing and breathing cannot be observed from body landmarks on a phone camera.)
