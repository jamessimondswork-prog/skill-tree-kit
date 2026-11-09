# Skill Tree game rules

The page and `/learn` both follow these. Change them here first, then in the page script (`skill-tree/skill-tree.html`).

## XP

| Event | XP | Who awards it |
|---|---|---|
| Step cleared (answer checked by the page, answer not revealed) | +5 | Page |
| Quiz passed (2 of 3 or better) | +25 | Page, on submit |
| Flawless quiz (3 of 3, first time) | +10 bonus | Page |
| Quest cleared (all steps or task done AND quiz passed) | +50 | Page |
| Review card answered "Got it" | +5 | Page |
| Project shipped (boss quest cleared, every round auto-checked) | +200 | Page |
| Topic finished (every quest cleared) | +100 | Page |
| Rank Trial passed | +100 | Page |
| Project shipped outside the page (the learner shows it, Claude checks) | +200 | Claude, via ArtifactData |

- XP goes to the skill's practice total and to the player total. It never changes mastery.
- No XP for reading. No XP for a failed quiz. Retries are fine and score when passed.
- XP never goes down.

## Skill mastery (the real measure)

- Every skill has a fixed 1-7 ladder: Novice, Beginner, Competent, Proficient, Advanced, Expert, Master. Each level says what you can do and a real-world benchmark. Master = top few percent.
- Mastery only goes up by passing a **Rank Trial** for the next level: 6 problems picked at random from a pool of 9+ (not from quests), no hints, no show answer, a time limit, pass mark 5 of 6 (80%+). Leaving mid-trial or running out of time counts unanswered as wrong.
- Trials are hands-on: at least two thirds of each pool is real work, either SQL in the page or an `input` problem done in the real tool (a spreadsheet, Power BI Desktop, a terminal on a pinned public repo) where they type the result. Choice-only is allowed only with `handsOn: false` and a reason (agent design judgement).
- Fail = that level locks for 3 days (`stats.trialFails.<level>`, `TRIAL_WAIT` in the page). Missed problems are listed, answers stay hidden.
- Pass = `stats.mastery`, `masteryOn`, +100 XP and a Rank up screen.
- Quests and XP never change mastery. XP is practice: it drives the player rank and character.
- Card tier colour by mastery: Bronze 1-2, Silver 3-4, Gold 5, Platinum 6, Diamond 7.
- Be honest about ceilings: a topic only gets trials for levels it really teaches (a topic with trials up to level 4 reaches Proficient, 4/7). Role topics also get trials for levels 1-3 so placement can run.
- Placement (role topics): a short test on the first open, starting at the self-rated level and climbing through the real trial problems (`placementPick` per level, pass with `placementPass`) until a miss. Each level passed sets real mastery and places out the quests it covers. It can be skipped or retaken.
- Ladders and trials live in `skill-tree/trials/<stat>.json`, checked with `build_pack.py --trials`.
- Trial answers sit in the page's data so the page can mark them. It's an honour system: don't look.

## Ranks (total XP) and the character

| Rank | XP | Character gear |
|---|---|---|
| Rookie | 0 | plain |
| Contender | 500 | headband |
| Challenger | 2,000 | cape |
| Champion | 5,000 | crown |
| Legend | 10,000 | big cape |

The character is the learner's own, from the creator on first open (name, hair, hair colour, skin tone, outfit, outfit colour, extra), stored in `player/me.name` and `player/me.look`. They can change it from the settings button. Rank gear is never picked: it's earned. Headband and cape take the rank's tier colour.

## Gear and Master crowns (page 1.1.0)

Gear is picked, but only once it's earned. The learner wears it from the Gear section of the settings button. One item per slot: head, face, body, hands, back, pet.

| Item | Slot | Unlocks |
|---|---|---|
| Champion belt | body | Champion rank |
| Victory scarf | body | Champion rank |
| Shades | face | Champion rank |
| Golden gloves | hands | Champion rank |
| Flame aura | back | Legend rank |
| Wings | back | Legend rank |
| Pixel pet | pet | Legend rank (drawn beside the character) |
| Master crown | head | mastery 7 in that skill |

- **Master crowns:** every skill at mastery 7 unlocks its own crown. It's bigger than the Champion rank crown, with gems, and replaces it on the character while worn. Crowns show as locked teasers once a skill reaches level 5.
- **Which crown a skill gets:** the stat's optional `crown` field (a preset id, or `own`) first, then a preset match, then a crown made from the stat id (shape and colours fixed per id).
- **Presets** give everyone who masters the same subject the same crown, whatever the stat id. The `PRESET_CROWNS` table in the page lists them. First preset: `ai-agents` ("AI Agents crown"), matching stat ids `agents`, `agentic-os`, `ai-agents` or a stat name with a word starting "agent". To pin a crown, set `crown: "<preset id>"` on the stat. `crown: "own"` opts a stat out of presets so it keeps its own crown.
- Saved on `player/me.gear` (`head`, `face`, `body`, `hands`, `back`, `pet`: item ids or null). The page ignores any item the learner no longer qualifies for, e.g. a crown after a mastery reset. Never write `gear` from `/learn`.
- First unlock of each item shows a "New gear unlocked" screen once. Shown items are kept in `player/me.gearSeen`.

## Streak fire

Pixel fire under the character grows with the streak: Spark 1-2 days, Flame 3-6, Blaze 7-13, Inferno 14-29, Supernova 30+ (teal-white core). No streak, no fire.

## Quest order

- Quests unlock in order. Quest n opens when quest n-1 is cleared.

## Rusty (the decay)

- A skill goes rusty when its review cards are overdue: minus 10% per overdue card, floor 50%.
- Shows on the skill card only while overdue. Clearing the cards restores it. Only rust changes, never XP.

## Review cards (spaced)

- Every quest makes 2-3 cards. First due 1 day after the quest clears.
- "Got it" pushes the gap along: 1, 3, 7, 14, 30, 60 days.
- "Again" resets the gap to 1 day.

## Streak and Today's run

- A day banks if the learner clears a quest or 3+ review cards. The page shows this as Today's run.
- Streak = consecutive banked days. One free miss per 7 days (a "rest day") so a busy day doesn't wipe it.

## Session shape (30 min)

- 3-5 review cards (5 min).
- Quest 1: explain (3 min), do (8-10 min), quiz (2 min).
- Quest 2: same.
- Builds can take one 30-min quest instead of two.

## Trophy Hall

- 16 unique pixel trophies in 3 chapters of a career story: The Newcomer, The Specialist, The Legend. Each has a name, a requirement and a line of lore.
- Locked trophies show as silhouettes with the requirement and a progress bar. The lore stays hidden until earned.
- Earned date saved on `player/me.trophies.<id>`. New ones get a "Trophy earned" screen with the lore.
- Shelf next to the character: earned trophies (last 8), plus the closest locked ones while fewer than 3 are earned.
- Counters on `player/me`: `flawless` (3/3 quizzes), `cardsGot` (review cards right).
- Topic trophies live in the page script (`ACH`). A new topic gets its own set of chapter 1-2 trophies tied to its quests, with new sprites.

## Step checks (sandbox quests)

- Shown answer: the step still clears but earns no step XP.
- "Show answer" unlocks after 2 wrong runs or both hints used.
