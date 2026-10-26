# Skill Sphere factory (v0)

Takes the name of an activity and produces an *entry*: the knowledge the iPhone app needs to
coach it (phases, key poses, objectives with target ranges and causes, what coaches say, outcome links).
Nothing in the code is specific to one activity.

    activity name -> model proposes structure -> find reference videos -> download -> extract skeletons
                  -> key poses and target ranges from the real movement (best footage first) -> 9 automated checks
                  -> work/<activity>/entry.json  +  work/<activity>/report.md

**Status: first version.** The movement analysis, calibration, schema and checks are tested on synthetic
data (`python factory.py selftest`, `python -m tests.test_pipeline`). The download, pose extraction and
model-proposal steps could not be run where this was written (no internet), so **the first real run is the real test**.
Expect to fix things. Send the report and any error messages back and they get fixed.

## One-time setup on your Mac (about 10 minutes)

1. **Open Terminal** (press Cmd+Space, type Terminal, press Enter).
2. **Check Python.** Type `python3 --version`. You want 3.10 or newer. If it is missing or older,
   download the installer from python.org/downloads and run it, then open a new Terminal window.
3. **Go to the folder.** Unzip the file you downloaded, then in Terminal type `cd ` (with a space),
   drag the unzipped `factory` folder onto the Terminal window, and press Enter.
4. **Create a private environment and install the tools** (copy these lines one at a time):

       python3 -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt

   Whenever you open a new Terminal window later, run `cd` into the folder again and `source .venv/bin/activate`.
5. **Test the machinery** (no internet or key needed): `python factory.py selftest`. You should see a report
   ending with "selftest finished". Then `python -m tests.test_pipeline` should end with "passed" and no error.
6. **Add your Anthropic API key** (create one at console.anthropic.com, under API keys; keep it private):

       export ANTHROPIC_API_KEY="paste-your-key-here"

   This only lasts for the current Terminal window.

## Running it

    python factory.py run --activity "tennis forehand"

This does everything in order: finds footage until there are enough clear attempts (`grow`), reads what coaches say (`learn`),
finds and extracts videos that show mistakes (`mistakes`), labels their attempts (`label`), and builds the entry and
`work/<activity>/report.md` (`build`). When it finishes, or stops at a step, a banner appears on the screen
(macOS: allow Terminal in System Settings > Notifications; choose "Alerts" to keep the banner until dismissed).
Work already done is reused, so running it again continues where it stopped.

The steps can also be run separately: `grow`, `learn`, `mistakes`, `label`, `build` (same `--activity`).
Each attempt event of an activity says how long it takes (`seconds`); this is what cuts a rally or a set into single attempts.
Labels are made again for a video whose attempts are cut differently from when it was labelled.
If YouTube refuses captions ("429 too many requests"), requests are spaced out and retried after longer waits;
`export SPHERE_COOKIES=chrome` (or `safari`, `firefox`) uses the browser's sign-in, which is limited less.

Useful options:
- `--videos FOLDER` with `extract`: use your own videos instead of downloaded ones.
- `--delete-videos`: delete each video once its skeleton has been extracted (keeps only derived data).
- `mistakes`, `label`: download videos that show mistakes, then for each attempt in them the model looks at four frames and the coach's words at that time
  and records which coach faults are visibly present or absent (`work/<activity>/labels.json`: time windows and fault ids only). `build` uses them automatically:
  an objective linked to a coach fault with enough labelled attempts gets a validated range, checked on videos it was not fitted on.
- `--labels labels.csv`: a file with lines like `clipid,good` or `clipid,knee_cave` (an objective id). Labelled clips let the
  factory validate target ranges (AUC). Without labels, each range is taken from footage of coaches and professionals
  demonstrating good form (or, when there is not enough of that, from everyday footage, which is marked as such);
  none of those ranges is validated and the entry stays at confidence tier "low".
- `--runs N`: number of independent model proposals (default 3); their agreement is measured.

Run it on more than one activity (for example a squat, a tennis serve and a dance move). The other activities in
`work/` serve as negatives when the factory tests whether one activity is mistaken for another.

## Known limits of this version

- Pose comes from MediaPipe; axes are assumed roughly camera-aligned, and camera tilt is not corrected
  (the phone's inclinometer does this in the app, not here).
- Videos from search are unlabelled: they show the movement, not whether it was good or faulty. `mistakes` then `label` add labels from videos that show mistakes.
  Validated target ranges need labelled examples (public datasets, labelling, or coach videos that show a mistake and its fix).
- Only body outcomes are measured. Ball flight (M19) is registered as planned, not implemented.
- Downloaded videos have licence and terms-of-service implications that have not been looked at yet.


## Coaching (coach.py)

An entry plus a recorded video or a camera gives spoken cues. Nothing in `sphere/engine.py` knows the activity.

    python coach.py video --activity tennis_serve --video my_serve.mp4     # timeline, a .coach.json log, and a copy of the video with cues on it
    python coach.py live  --activity tennis_serve                          # webcam; speaks with the Mac voice

Each finished attempt is judged on every objective (met / missed / unknown when the camera angle is outside what the entry was built from). An objective
missed often enough by the entry's own rule (e.g. 3 of the last 5) is said, one cue per attempt, the most important first, not repeated for three attempts.
With ANTHROPIC_API_KEY set the sentence is worded for the moment from the objective's goal and intent; without it the entry's cue intent is used.

## Principles

`build` also asks the model, three independent times, for the few ideas that explain why good form works (`principles` in the entry). Only ideas that
at least two runs reach again are kept. Each says which objectives and coach-named faults it explains, gives the intent of a short cue that names the
effect to achieve (never a body part), and when it may be offered. Check 10 fails on: references to nothing, a contested idea with no competing views,
a cue handle that names a body part, or a safety/medical statement. In `coach.py` the spoken cue points at the principle; `Session.why()` explains it
on request, and after a rest of 20 s the principle behind the latest cue is offered once.
