# Skill Tree index (for Claude)

Home for `/learn`. Everything in `skill-tree/` stays on this computer except the page and its public data files. The learner's own guide is `skill-tree/README.md`; this file is the index Claude reads and keeps up to date.

- **Skill Tree page:** (not set up yet: the first `/learn` publishes it and writes the link here and in `setup.json`). Private, owner-only db rules. Source: `skill-tree/skill-tree.html`. Republish from that file with the page's `url` to keep the link.
- **Setup answers:** `skill-tree/setup.json` (`done`, `prebuilt`, `lastUpdate` (last kit version applied), name, job, `workProject` and `workProjectRead`, interests, time, learning style, `firstLinks`, `pageUrl`, which extras installed).
- **Role gaps:** `skill-tree/learner/role-gaps.json`, the skills the learner's role needs. The Quest Board's source. Checked with `.claude/skills/learn/scripts/role_gaps.py`.
- **Packs:** `skill-tree/<topic-id>/pack.json`, the master copy of each topic, built and checked by that folder's `gen_pack.py`.
- **Sandbox data:** `skill-tree/data/*.json`, published next to the page (`files` on publish). Public or made-up data only.
- **State copy:** `skill-tree/state/`, pulled from the page at the start of each run. A prebuilt kit also holds `pending-writes.json` here: the page writes `/learn prebuild` saved for the learner's first `/learn` to load, replayed with `.claude/skills/learn/scripts/pending_writes.py`.
- **Learner memory:** `skill-tree/learner/NOTES.md` (preferences) and `skill-tree/learner/records/` (proven skills, prior knowledge, misconceptions).
- **Per topic:** `MISSION.md`, `RESOURCES.md`, `pack.json` (+ generator).
- **Worked example:** `skill-tree/example/`, spreadsheet formulas on a made-up expenses sheet (reference only, never loaded onto the page).
- **Version and updates:** `skill-tree/VERSION` (the kit version) and `skill-tree/UPDATE-NOTES.md` (what each update changed, newest first). `/learn update` applies an update.
- **Rules:** `.claude/skills/learn/references/game-rules.md`. **Quality bar and pack format:** `.claude/skills/learn/references/playbook.md`. **Checker:** `.claude/skills/learn/scripts/build_pack.py`.

## Mastery

- Ladders: `skill-tree/trial-data/ladders.py` (empty until the first topic). Trials: `skill-tree/trials/<stat>.json` (role topics too; only the worked example keeps its own `trials/` folder).
- None yet.

## Topics

- None yet. `/learn` adds one line per topic: id, title, quests, stat, trials, ceiling, guide, status.

## Page data model (ArtifactData collections)

| Path | Fields |
|---|---|
| `player/me` | `name`, `look` (character from the creator), `xp`, `streak`, `bestStreak`, `lastActiveOn`, `restUsedOn`, `cardsOn`, `cardsToday`, `activeTopic` (main quest; others active = side quests), `bestCombo`, `trophies`, `flawless`, `cardsGot`, `gear` (equipped items: `head`, `face`, `body`, `hands`, `back`, `pet`, each an item id or null; set by the page only), `gearSeen` (item ids whose unlock screen has shown) |
| `stats/<id>` | `name`, `area` (`job` / `ai` / `personal`), `xp` (practice), `mastery` (0-7, trials and placement only), `masteryOn`, `ladder[7]`, `trialFails.<level>`, `trainingId` (role gap id, optional), `crown` (optional preset crown id, e.g. `ai-agents`: pins the Master crown; `own` opts out of presets and keeps the stat's own crown; without it the page matches a preset by id or name, else makes one from the stat id) |
| `requests/r<timestamp>` | The learner's own asks from the page's "Request training" box: `text`, `url` (if a link), `files` (uploads: `id`, `name`, `type`, `size`; big files and .mov have `parts` (base64 text asset ids, in order) + `enc: base64` instead of `id`, rebuilt with `join_parts.py`; deleted after the build; download with Artifact `read` + `path` = id), `addTo` (auto / new / a topic id), `kind` (`levelup` for level-up quests), `status` (queued / built), `askedOn`, `topicId` |
| `offers/<gap-id>` | Quest Board offers from `role-gaps.json`: `rank` (1-5), `npc` (mentor / professor), `skill`, `gapId`, `alsoGaps[]`, `title`, `pitch`, `reward[]`, `effort`, `ceiling`, `priority`, `note`, `sourceUrl`, `status` (offered / accepted / snoozed / built), `offeredOn`, `snoozeUntil`, `topicId` |
| `trials/<stat>-L<n>` | `stat`, `level`, `pick`, `passMark`, `placementPick`, `placementPass`, `minutes`, `sandboxTopic`, `problems[]` (from the trials file) |
| `topics/<id>` | `title`, `stat`, `project`, `sourceUrl`, `sourceTitle`, `sourceLength`, `status` (offered / active / paused / done), `guide` (NPC: sprite, offer, lines), `acceptedOn`, `snoozeUntil`, `createdOn`, `mission`, `communities[]`, `placement`, `fromRole`, `gapId`, `placementStart`, `placementDone`, `placementSkipped`, `reference[]`, `glossary[]`, `trophies[]`, `quests[]` (each with `source`, `win`, `mixed?`, `evidence`, `placed?`) |
| `cards/<id>` | `topic`, `quest`, `stat`, `front`, `back`, `due` (null until the quest clears), `gapIdx`, `lapses` (times forgotten), `remind` (true = refresher lesson waiting in the Quest Log) |
| `log/<YYYY-MM>` | `entries[]`: `on`, `type`, `topic`, `xp`, `note` |

Sandbox topics add `sandbox: { type: "sql", dataset: "data/<name>.json", table, setup, rawSample? }` and `dataSource`. `dataset` and `rawSample` are relative to `skill-tree/` and published at the same path next to the page.

Guided quest shape: `{ id, title, minutes, keepDb?, boss?, steps: [{ id, title, teach, goal, starter, hints[], answer, rows, ordered, contains | verify | matchSql, upload? }], quiz[], stepsDone, taskDone, quizBest, completedOn }`.

`pack.json` = `{ "topic": {...topics doc...}, "cards": [{ "id": "...", ...card doc... }] }`. Ids: kebab-case, cards `<topic>-<quest>-<n>`.

## Stats so far

- None yet. A stat is created only when a topic that uses it starts (no placeholder skills). A quest's own `stat` overrides the topic's.
