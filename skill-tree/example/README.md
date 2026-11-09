# Worked example: spreadsheet formulas on team expenses

**Reference only. Never load this pack onto the Skill Tree.** It's here so Claude can see what a finished `/learn` pack looks like before building a real one. Its `status` stays `offered` and nothing in it is pushed to the page.

The skill is practised in the learner's own Excel or Google Sheets, not on the page. So there's no sandbox and no SQL: `do` steps cover things done in the spreadsheet, and `input` steps ask for the value their formula returns.

## What it shows

- A data quest first: where the data comes from, open the CSV, count the rows, spot the mess with a filter, fix it with Find and Replace.
- Guided `input` steps with `teach`, `deeper` (Why it works / Worked example / Common mistakes), 2 hints and every accepted answer form (e.g. `1,038.60`, `£1038.60`, `1038.6`).
- `do` steps with a check question, including "Explain it back".
- Scene-setting quizzes, 3 per quest, with right answers spread across A-D.
- Review cards (2-3 per quest), a mixed practice quest, a boss fight that builds a summary tab, and a "use it at work" quest (`ship: true`): a template, notes, one real task done with formulas, and sharing it safely.
- A guide NPC (the built-in Mentor) with a Quest Board offer, trophies (built-in art and one custom sprite), mission, Field Guide (`reference`, `glossary`) and communities.
- The role-topic fields: `fromRole`, `gapId`, `placementStart`, `placement`, and Rank Trials for levels 1-3 with `placementPick` and `placementPass`.
- Hands-on trials: 7 `input` problems and 3 choice questions per level, with `tool` and `dataFiles` so the page offers "Get the trial data".
- Level 3 trial problems on a second sheet the quests never use (`trip-expenses.csv`), marked `unseen: true`.

## Files

| File | What it is |
|---|---|
| `gen_pack.py` | Builds everything below from a fixed seed. Every input answer is worked out from the CSV text. |
| `team-expenses.csv` | The sheet the quests use: 60 **made-up** claims, one quarter. |
| `trip-expenses.csv` | A second **made-up** sheet, only for the level 3 Rank Trial. |
| `pack.json` | The topic and review cards. |
| `trials/example-formulas.json` | The 1-7 ladder and Rank Trials for levels 1-3. |
| `topic.json`, `writes.json`, `trials/example-formulas.writes.json` | Written by `build_pack.py` when it passes. Delete them after checking: `writes.json` holds a full path from your computer. |

In a real topic, data files go in `skill-tree/data/`, and the steps tell the learner to open them from there. Trial `dataFiles` paths are relative to `skill-tree/` and get published with the page (the data files rule in SKILL.md). The example keeps its CSVs in its own folder so `skill-tree/data/` stays empty.

## The data

Made up, not real. One row per expense claim, January to March 2026, in date order (rows 2-21 January, 22-41 February, 42-61 March).

- `id` claim number, `date` YYYY-MM-DD, `month` Jan, Feb or Mar, `person`
- `category` Travel, Meals, Software, Office or Training. 3 rows say `Softwear` on purpose: quest 1 finds and fixes them, and a level 2 trial problem checks you remember on the file as downloaded.
- `amount` pounds, `receipt` Yes or No, `status` Approved, Pending or Rejected

`trip-expenses.csv`: `id`, `trip` (Leeds, Bristol, Glasgow), `traveller`, `type` (Train, Hotel, Taxi, Food), `cost` (pounds), `booked_early` (Yes or No).

## Rebuild and check

From the work project folder (the one holding `skill-tree/`):

```
python -I -X utf8 skill-tree/example/gen_pack.py
python -I -X utf8 .claude/skills/learn/scripts/build_pack.py skill-tree/example
python -I -X utf8 .claude/skills/learn/scripts/build_pack.py --trials skill-tree/example/trials/example-formulas.json
```

All three should end with OK. Re-running `gen_pack.py` gives the same files every time.
