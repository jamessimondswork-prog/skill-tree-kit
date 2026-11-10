# /learn playbook

How to turn a request into a topic the learner can start straight away. Everything here comes from corrected runs (see `lessons.md`). The worked example is `skill-tree/example/` (`gen_pack.py`, `README.md`, `trials/example-formulas.json`): spreadsheet formulas in the learner's own Excel or Google Sheets, on a made-up expenses sheet, with `do` and `input` steps and no sandbox. It's reference only: never load it onto the page. For SQL topics, see "SQL sandbox shape" below.

Teaching method credit: mission, resources, learning records, glossary, quiz balance and interleaving are adapted from [mattpocock/skills `teach`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach) (MIT).

## The quality bar

A topic is ready when all of this is true. `build_pack.py` checks the parts marked (checked).

- **Beginner first.** Every step teaches one idea in plain words, example first, every term defined. Max 170 words per teach (checked). Never assume they know a term you haven't taught.
- **Label every value.** Say which column each number or value is in examples and starters (e.g. "each row is (item, category, qty)"). A beginner can't guess what 245 means.
- **Teach the skill, not the project.** The project is the practice ground. One new concept per session, layered: every later session reuses all earlier concepts, so the final sessions use the whole toolkit.
- **They write it, never copy it.** No half-written starters and no full formulas in teach text. Loop per concept: what it does and why, look at the data, tiny example on different data, blank-editor task in plain English. 3 tries per new concept (guided, own, twist), hints on all 3 (keyword, then shape with blanks, then answer), then one explain-it-back question.
- **Real-world why** (all topics). Every concept has a work example from the learner's own field (their job from setup; made-up numbers, never company data) and the logic of why it's used.
- **Show the data first.** Before using a table, they look at it themselves, with a plain-English meaning for every column code.
- **Not too easy.** Benchmark: a good full online course. By the end they solve unlabelled problems with no hints and apply it to their own ideas.
- **Everything in the page.** No pasting into chat. Hands-on skills use a sandbox. Off-page actions (installing a tool, GitHub) are `do` steps with a check question.
- **Guided, not stuck.** 2 hints per step (checked): name the keyword, then the shape with blanks. Show answer after 2 wrong tries. Feedback says what's wrong ("38 rows expected, you got 760: check your brackets").
- **Their interests.** Projects use the `interests` from setup (`skill-tree/setup.json`), or something from their own field they'd actually use. Languages use real situations (ordering, travel, chatting). Public or made-up data only.
- **Data topics start with the data.** Quest 1 teaches collect, load and clean: where it comes from (site + exact URLs), downloading it, loading it, fixing types and dates. Say the source everywhere (checked: `dataSource`).
- **Boss fight builds the project** (checked: one `boss` quest). Rounds reuse earlier quests with lighter hints.
- **Ship it.** Projects end with a "ship it" quest: repo-ready zip, run it in a real desktop tool, publish to GitHub. The learner makes accounts and pushes themselves. Data stays out of the repo; a fetch script and credit go in.
- **Tools get their own skill.** A quest that teaches a separate tool (Git, Power Query, DB Browser) sets its own `stat` + `statName`.
- **Quizzes test doing** (3 per quest, checked): "which query returns...", "what's wrong with this", never trivia.
- **Harder questions** (checked): most quiz and check questions set a short scene (15-45 words) they have to apply the idea to: "you built X and Y happens, what's the fix?". Every wrong option is a believable mistake learners really make, same form and similar length as the right one. No joke options. `why` says why the right answer wins and why the most tempting wrong one fails. Checker: under a third of questions under 12 words; shortest option at least 35% of the longest.
- **Go deeper** (checked): teach stays short. Every step with 40+ words of teach also gets `deeper` (80-350 words, from the source only): **Why it works**, **Worked example**, **Common mistakes**, optional **In the source**. The page shows it as a fold under the lesson, plus an "Ask Claude about this step" box (page `sample` capability) for live follow-ups. The box gets the step's teach, deeper, goal and source, and won't give the mission answer unless they ask.
- **Review cards** 2-3 per quest (checked), short, testable.
- **Trophies tell a story.** One per quest (noted if fewer), RPG-style name, one-line lore in a career-story voice, unique 12x12 sprite (checked).
- **Every answer works.** SQL answers run against the real data and pass their own check (checked). Typed answers list every accepted variant.
- **Real mastery, not effort.** Every skill has a 1-7 ladder (`skill-tree/trial-data/ladders.py`) with honest benchmarks and Rank Trials for each level the topic teaches (checked by `build_pack.py --trials`). Each level says what you can **do** (knowledge, not a job title), `proof` (how it's proven), `benchmark` (real-world comparison) and `quest` (the level-up quest name). Master means top-level knowledge in the area. From level 3 up, at least half of each attempt is on data or scenarios they haven't practised on (`unseen: true`, checked; e.g. a made-up sheet or table the quests never touch, like `trip-expenses.csv` in the worked example). Levels 5-7 need outside `evidence` too (public platform, real cert, reviewed work), checked by Claude before mastery is given (checked). Trial problems are new (never copied from quests), unaided and timed. Say the topic's ceiling plainly (e.g. "this gets you to Proficient, 4/7").
- **Mission first** (checked). Every topic has a concrete Why and 2+ observable "success looks like" abilities. Role skills: derive it from the gap's `why` in `role-gaps.json`, no questions. Personal topics: ask the learner one question on why. Write `MISSION.md` in the topic folder too.
- **Never trust memory.** Teach from the source and a curated `RESOURCES.md` (Knowledge with "Use for:" notes, Wisdom = 1-3 well-run communities, Gaps). Each quest names one primary source (checked: `source`) and one tangible `win` (checked).
- **Knowledge easy, skills hard.** Teach text is clear with no tricks. Practice gets harder through the topic: fade the scaffolding (shorter starters, vaguer hints) toward the boss.
- **Interleave** (checked): topics with 5+ quests have a `mixed` quest before the boss: earlier techniques, new problems, no labels.
- **Balanced quizzes** (checked): the right answer is not usually the longest option, positions spread across A-D, no "all/none of the above". Same for do-step checks and trial choice questions.
- **Field Guide**: `reference` sections (syntax, "which tool when", recipes) and a `glossary` (term, tight definition, `avoid` aliases, `quest` that unlocks it). Use glossary terms in teach text, not the aliases (noted by the checker).
- **Placement**: map Rank Trial levels to the quests they cover in `placement`. Passing places them out of those quests. Required on role topics (see "Placement for role topics"), optional on their own requests.
- **Public or made-up data only.** Never anything from the work project. No company names, figures, clients or internal terms in any text.
- **Honest credit.** The project is the learner's work. The Skill Tree is Claude's build, never theirs.

- **One topic per subject.** Links on the same subject merge into one topic (`category`, `sources[]`, SKILL Mode 5). Research beyond their links to fill gaps, from high-trust sources only, and list them in `sources` too.

## Sizing

- 6-9 quests, 3-8 steps each (checked), 15-20 min per quest. A 30-min session = review cards + 1-2 quests.
- Fit the pace to `timePerWeek` in setup: fewer, shorter quests for 1 hour a week.
- Source of N hours: aim for under half that in quests. Cut intros, repeats, platform-specific bits (say what you cut and why).

## Step kinds

| kind | Use for | Clears when |
|---|---|---|
| `sql` (default) | Writing queries in the page sandbox | Result matches (see checks) |
| `input` | Languages, definitions, short answers, numbers, formulas in a real spreadsheet (they type the value their formula returns, as in the worked example) | Typed answer matches any of `accept` (case, accents, punctuation ignored) |
| `input` + `answerSql` | SQL written in a real tool (e.g. pgAdmin). They type what their query returned | Same as `input`. Show answer also shows `answerSql`. Work `accept` out by running `answerSql` on the same data in a script (e.g. SQLite from the CSVs in `gen_pack.py`), never by hand, and check for ties before asking "which one" |
| `do` | Things done outside the page: install, sign up, GitHub, a desktop tool | Check question answered right |

SQL checks (pick one): `answer` only (page runs the answer and compares; any column names or order, extras OK; set `ordered` only when there are no ties on the sort key), `contains` (text in result, e.g. "USING INDEX"), `verify` (SQL on their db returning 1), `matchSql` (compare with SQL run on their own tables). `keepDb: true` on a quest keeps their tables between its steps. `upload: true` shows a CSV upload that loads `raw_results`.

### SQL sandbox shape

SQL topics get an in-page SQLite sandbox. The topic has `sandbox: {"type": "sql", "dataset": "data/<name>.json", "table": "<table>", "setup": "<optional SQL run after loading, e.g. extra tables for unseen trial problems>", "rawSample": "<optional data/<file>.csv for upload steps>"}` plus `dataSource`. The dataset file is `{"table", "columns", "rows"}`. Steps default to `kind: "sql"` with `starter`, `answer` and one check from the list above, and `build_pack.py` runs every answer against the real data. Quest 1 is the data quest (`keepDb: true`). Trials can use SQL problems (`goal` + `answer`) when the trials file names the topic in `sandbox`.

## Pack format (`skill-tree/<topic-id>/pack.json`)

```json
{
  "topic": {
    "title": "SQL on shop sales", "stat": "sql", "statName": "SQL", "area": "job", "category": "sql",
    "sources": [ { "title": "Video or course", "url": "https://...", "addedOn": "YYYY-MM-DD", "notes": "sources/v1.md" } ],
    "project": "One line: what they build",
    "sourceUrl": "https://...", "sourceTitle": "Course or video name", "sourceLength": "7 hours of course, about 2 hours of quests",
    "dataSource": "Where the data comes from (sandbox topics)",
    "sandbox": { "type": "sql", "dataset": "data/<name>.json", "table": "sales", "setup": "CREATE VIEW ...", "rawSample": "data/raw.csv" },
    "status": "active", "createdOn": "YYYY-MM-DD",
    "fromRole": true, "gapId": "<gap id>", "placementStart": 1,
    "quests": [
      { "id": "q1", "title": "...", "minutes": 15, "keepDb": false, "boss": false, "stat": null, "statName": null,
        "steps": [ { "id": "s1", "kind": "sql", "title": "...", "teach": "...", "deeper": "...", "example": null, "goal": "...",
                     "starter": "SELECT ", "answer": "SELECT ...;", "hints": ["...", "..."], "ordered": false,
                     "contains": null, "verify": null, "matchSql": null, "upload": false } ],
        "quiz": [ { "q": "...", "options": ["...", "...", "...", "..."], "answer": 1, "why": "..." } ] }
    ],
    "trophies": [ { "id": "unique-id", "ch": 2, "name": "Lens of WHERE", "need": "Clear \"Your first queries\".",
                    "lore": "One line of story.", "sprite": ["12 rows of 12 chars"], "when": { "quest": "q1" } } ]
  },
  "cards": [ { "id": "<topic>-q1-1", "quest": "q1", "front": "...", "back": "..." } ]
}
```

- `fromRole`, `gapId` and `placementStart` only on topics built from a role gap.
- `input` steps: `"accept": ["dónde está el baño", "donde esta el baño"]`, optional `"why"`.
- `do` steps: `"check": {"q": "...", "options": [...], "answer": 2, "why": "..."}`, optional `"action": "download" | "repoUrl"` (SQL ship quest only today).
- Trophy `when`: `{"quest": "q1"}` (quest cleared), `{"quest": "q0", "step": 5}` (that many steps done), `{}` (topic finished). Chapters: 1 The Newcomer (first steps, setup), 2 The Specialist (core quests), 3 The Legend (boss, ship).
- Sprite colours: `k` outline, `g/G` gold, `s/S` silver, `w` white, `r/R` red, `b/B` brown, `o` orange, `y` yellow, `c` cyan, `p` purple, `u` blue, `n` green, `.` empty. Built-in `art` names: whistle, satchel, rake, key, lens, stones, tablet, banners, hourglass, boot, cup, orb, torch, tome, sword, diamond, scroll.
- Sandbox datasets: `skill-tree/data/<name>.json` = `{"table", "columns", "rows"}`, built from public or made-up data by a script in the topic folder. `dataset` and `rawSample` are paths relative to `skill-tree/` (e.g. `"rawSample": "data/raw.csv"` means the file `raw.csv` in `skill-tree/data/`). The page fetches them at the same path relative to itself, so publish each one with the page at that path (`files`, SKILL Setup step 8).

## Page limits (what the Skill Tree can and can't do)

- SQL sandbox only (SQLite in the browser). No Python, R or Excel runtime: teach those with `input` + `do` steps and a desktop tool, or ask the learner before building a new sandbox.
- The page can't reach other websites (no fetching, no GitHub API). Links open in a new tab.
- Downloads: zip only for project files (built-in for the SQL ship quest).

## Mastery ladder and trials (`skill-tree/trials/<stat>.json`)

```json
{ "stat": "sql", "statName": "SQL", "sandbox": "<topic-id whose sandbox the trials use, or omit>",
  "ladder": [ { "level": 1, "name": "Novice", "can": "What you can do", "benchmark": "Real-world comparison" } ... 7 levels ],
  "trials": [ { "level": 1, "pick": 6, "passMark": 5, "minutes": 15, "placementPick": 4, "placementPass": 3,
                "problems": [ { "id": "n1", "goal": "...", "answer": "SELECT ...;" },
                              { "id": "g1", "kind": "choice", "q": "...", "options": ["..."], "answer": 1 } ] } ] }
```

- Pool at least pick + 3 (checked). Levels 1, 2, 3... with no gaps (checked). Only build trials up to the level the topics teach, except role topics, which need levels 1-3 for placement.
- `placementPick` (3 to `pick`) and `placementPass` (at least 75% of `placementPick`) on every trial (checked).
- Optional on a trial: `dataFiles` (`[{"name": "orders.csv", "path": "data/<file>"}]`, published with the page) and `tool` (e.g. "a spreadsheet"). The page then shows a "Get the trial data" card before the clock starts, zipping those files for download.
- Role topics keep their trials in `skill-tree/trials/<stat>.json` like every other topic. Only the worked example keeps its trials in its own folder (the checker looks in the topic folder first, then `skill-tree/trials/`).
- A new skill gets its ladder written once, from real job and interview benchmarks, in `skill-tree/trial-data/ladders.py` (`L()` helper). Later topics add trials for higher levels.
- A new skill also gets its gear set once: 7 items, one per mastery level, in `skill-tree/gear/<stat>.json` (template in `skill-tree/gear/README.md`, checked by `gear_check.py` and again by `build_pack.py`; steps in SKILL.md, "Gear set for a new skill"). Skills that match a preset (SQL, Power BI, Git & GitHub, AI agents) need no file. Optional `crown` on the topic, or on a quest with its own `stat`: a preset id to pick that preset, or `own` to opt out. Pass the learner's privacy terms to every pack build with `--terms`.
- Push, always in this order: `newStats` set (a new stat's entry already carries `ladder` and `mastery: 0` when its trials file exists: `build_pack.py` puts them there), then a `ladder` update for stats that already exist (pinned), then the `trials/<stat>-L<n>` docs, then the topic, then the cards, then the gear set when the build made one (`gear/<stat>`, the last entry in `writes.json`). On a fresh page there is no stat to update, so a ladder sent before or without the `newStats` set gets lost or wiped.

## Placement for role topics

Topics built from a role gap find the learner's real starting level, using the real Rank Trials.

- **Self-rating** (terminal, when the topic gets built): 1-2 short questions per gap, e.g. "Which of these have you done: a VLOOKUP, a pivot table, a Power Query merge?" Save `selfRating: {question, answer, startLevel}` on the gap in `role-gaps.json` and set the topic's `placementStart` to `startLevel` (1-4). No reply (the learner isn't there): `placementStart: 1`. It never sets mastery on its own.
- **Trials up front** (in `skill-tree/trials/<stat>.json`): levels 1-3 (1-4 when `placementStart` is 4), even levels the topic doesn't teach, each with `placementPick` and `placementPass`. `build_pack.py --trials` must pass for every one.
- **`placement` map**: each level to the quests it covers, so passing a level places them out of those quests.
- **On the page**: the first open of the topic offers the placement test. It starts at `placementStart`, uses `placementPick` problems per level (aim for 10-15 minutes in all) and climbs until they score under `placementPass`. Every level passed gives real mastery and places out its quests. The page stores `placementDone` or `placementSkipped` on the topic; they can skip to quest 1 or retake later.
- **Past the topic already?** If they pass every level the topic teaches, `/learn` builds a level-up quest next (SKILL Mode 6).
- The worked example shows the fields: `skill-tree/example/pack.json` and `skill-tree/example/trials/example-formulas.json`.

## Quest Board offer (`offers/<gap-id>` on the Skill Tree)

```json
{ "rank": 1, "npc": "mentor | professor", "skill": "Power BI", "gapId": "power-bi", "alsoGaps": [],
  "priority": "High", "title": "RPG quest name",
  "pitch": "2-3 sentences in the NPC's voice, facts from role-gaps.json only.",
  "reward": ["New skill: X, with Rank Trials up to <ceiling>", "Project: ...", "..."],
  "effort": "About 8 quests, roughly 3 hours", "ceiling": "Competent (3/7)", "note": "Tool it needs",
  "sourceUrl": "https://...", "status": "offered | accepted | snoozed | built", "offeredOn": "YYYY-MM-DD",
  "snoozeUntil": "set by the page on Not now (+14 days)", "topicId": "set when built" }
```

- The page shows live offers (offered, or snoozed past `snoozeUntil`) with the NPC, typed-out pitch, reward, Accept and Not now.
- Accept sets `status: "accepted"`. The next `/learn` builds it (Mode 2) as a role topic with placement. The page can't build topics by itself.
- Pitches describe general skills only: never company names, figures, clients or internal terms.

## Guide NPC (`topic.guide`) and side quests

Every topic has a guide. It offers the topic on the Quest Board (when `status: "offered"`), then shows up on the topic page and every step, reacting to passes, fails and combos.

```json
{ "npc": "mentor | professor",            // built-in, OR give name/role/col/rows for a new character
  "name": "Sparks", "role": "Crew Chief",
  "col": { "a": "#ff7a1a", "m": "#b9c4d6" }, // one char per colour
  "rows": ["14 chars x 20 rows, '.' = empty"],
  "offer": { "title": "RPG quest name", "pitch": "Under 70 words, in voice", "reward": ["..."], "effort": "~15 min a quest", "ceiling": "Competent (3/7)", "note": "Tool it needs" },
  "lines": { "accept": "", "hello": "", "back": [3+], "step": [3+], "pass": [3+], "fail": [3+], "quiz": "", "boss": "", "done": "", "combo": [3+] } }
```

- Pick the character to fit the topic: **The Mentor** (warm, direct) for tools and job skills, **The Professor** (curious, a bit dry) for theory, a new one when neither fits (e.g. Sparks the robot for agents). Give each a clear voice. Lines max 30 words, warm, never sarcastic about mistakes.
- `offer` is needed only when `status: "offered"`. Gap offers already accepted load as `"active"` with the NPC who offered them.
- Side quests: any number of topics can be active. `player/me.activeTopic` is the main quest; the learner switches it on the page with "Make main". `/learn` never changes it.
- Combos (steps cleared first time in a row) are bragging rights only: no XP. The "Lightning in a Bottle" trophy is for 5.
- `build_pack.py` checks the guide: sprite size and colours, every line, 3+ variants, offer fields when offered.

## Learner memory and adapting (zone of proximal development)

- Preferences: `skill-tree/learner/NOTES.md` (written by setup from `skill-tree/setup.json`). Read it before every build.
- Records: `skill-tree/learner/records/<NNNN-slug>.md`. Title + 1-3 sentences, optional Evidence / Implications / `Status: superseded by NNNN`. Write one only for proven understanding, disclosed prior knowledge, a corrected misconception, or a mission change. Not a journal.
- Evidence comes from the page: per-step `evidence` (fails, hints, revealed) on each quest, and `log` entries `quizmiss` and `trialresult`. `.claude/skills/learn/scripts/evidence_report.py` on `skill-tree/state/` lists proven, struggles and misses.
- Adapt: a struggle becomes a record plus 2 review cards (and a short remedial quest if it repeats). New topics compress what records prove and offer placement. The NPC board prefers gaps whose prerequisites they have.
