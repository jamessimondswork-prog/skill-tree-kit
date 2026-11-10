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
| Champion | 5,000 | cape (no new item: crowns only come from level 7 in a skill) |
| Legend | 10,000 | big cape |

The character is the learner's own, from the creator on first open (name, hair, hair colour, skin tone, outfit, outfit colour, extra), stored in `player/me.name` and `player/me.look`. They can change it from the settings button. Rank gear is never picked: it's earned. Headband and cape take the rank's tier colour. Everything else the character wears comes from skill item sets (next section).

## Gear: item sets (page 1.2.0)

Every skill has its own set of 7 items. The learner earns one item per mastery level in that skill, and wears them from the inventory (the backpack button next to the cog). The cog keeps name and look only.

| Level | Slot | Id in the data | Effect |
|---|---|---|---|
| 1 | Chest badge | `badge` | None |
| 2 | Right-hand tool | `tool` | None |
| 3 | Face piece | `face` | None |
| 4 | Book | `book` | Floats by the shoulder, bobs, glows |
| 5 | Back item | `back` | Moving parts and a pulse of energy |
| 6 | Companion | `pet` | Blinks, hops, leaves a spark trail |
| 7 | Crown | `crown` | Gems sparkle in turn, glow, slow light rays, faint aura on the whole character |

- Same slot at the same level for every skill. Only the art is themed.
- **Effects** belong to the page, not the set. Each effect takes the glow colour of the set its item came from, so a mixed outfit can glow in several colours. The aura and light rays follow the crown's set. A set can't add its own animation. Reduced motion: no movement, a still glow only. Small character icons (leaderboard rows, mini avatars) show the worn items with no effects and no companion. The creator preview shows the look with no items, so hair, glasses and caps are never hidden while choosing.
- **Earned = the skill's confirmed mastery level.** The page reads one thing: `stats/<id>.mastery`, rounded down and held to 0 to 7. Level n earns slot n, so mastery 3 means the level 1, 2 and 3 items are earned. Levels 1 to 4 count as soon as the Rank Trial is passed on the page (the page sets `mastery` then). Levels 5 to 7 count once Claude has confirmed the level and set `mastery` (the outside evidence, as in "Skill mastery"). What is earned is always worked out from the level. It is never stored. If a level drops, an item from above the new level comes off and the page saves that straight away, so it stays off when the level comes back. The learner puts it on again from the inventory.
- **The crown** only comes at level 7 of 7 in a skill. Nothing else gives a crown: the rank crown is gone.
- **Wearing:** one item per slot at a time. Items from different skills can be mixed (the SQL book with the Power BI crown). The face piece sits below the hairline, so it always fits under a crown. Creator extras: a worn face piece hides Glasses, a worn crown hides a Cap, Headphones stay on under a crown. The crown sits at the right height on every hair style. Layer order, back to front: rank cape, back item, body, straps, badge, face piece, tool, crown, book, companion.
- **Inventory:** opened with the backpack button, which sits before the cog. The button is hidden mid-trial, when signed out and before the character exists. A big live character at the top with "Wearing X of Y earned". One row per skill, highest level first, seven slots in level order (four per line on a phone). Earned items are in colour: tap to wear, tap again to remove, tap a filled slot to swap. Locked items are dark outlines with the rule under them ("Pass SQL level 5"). "Wear full set" per row puts on every earned item of that skill; pressed again (it then reads "Full set on") it takes that set off. "Take everything off" at the top. It saves on every tap. A skill with no set yet shows numbered placeholders 1 to 7 and "set not made yet".
- **Day-one screen:** the first open after the 1.2.0 update shows one screen, "N items already earned", listing them by skill, with "Open inventory" and "Later". Nothing is put on automatically. The 1.1.0 gear comes off, because those items no longer exist. "After the update" means `player/me.gear.v === 2`: until the page has saved that shape, it treats the player as not yet updated. A player with nothing earned gets no screen; the empty new shape is saved quietly.
- **Unlock screens:** after that, newly earned items are announced once. One to three new items get a screen each. More than three at once (a set added to a skill that is already at a high level) show as one list screen. None mid-trial, before the character exists, when signed out, or before the skills and sets have loaded. A level that drops and is earned again shows no second screen.
- **Share card:** a button in the inventory downloads a PNG of the character with the worn items (still, with glows), the name, the XP rank and one line per skill with its level (ten skills, then "+N more skills"). It is made in the browser with the downloads capability. Nothing is uploaded. If downloads aren't available, or the save fails, the picture is shown in the inventory instead with a line saying to press and hold it (or right-click) to save it.
- **Gone from 1.1.0:** Champion belt, Victory scarf, Shades, Golden gloves, Flame aura, Wings, Pixel pet, the automatic rank crown and the Master crowns. The rank headband and cape stay.

### Which set a skill gets

1. `crown: "own"` on the stat opts out of presets: the skill uses its own set from `gear/<skill id>`.
2. `crown: "<preset id>"` on the stat picks that preset.
3. Otherwise a preset match, by stat id only (never by name). Presets are built into the page, so they need no load. Each preset has a list of ids: SQL `sql`; Power BI `power-bi` and `powerbi`; Git & GitHub `git-github` and `git`; AI agents `agents`, `agentic-os` and `ai-agents`. Same skill, same set for everyone.
   - One preset dresses one skill on a page. If two skills on the same page would get the same preset, the one whose id comes first in that preset's id list keeps it (for Power BI: `power-bi` before `powerbi`; for Git & GitHub: `git-github` before `git`; for AI agents: `agents`, then `agentic-os`, then `ai-agents`; then the lower stat id). The other one needs its own set (step 4), or shows placeholders until it has one. `build_pack.py` stops a pack that would cause this.
4. Otherwise the stat's own set, made by `/learn` when the skill is first built and loaded as `gear/<skill id>`.
5. No set at all: the inventory shows numbered placeholders until `/learn` loads one.

The `crown` field keeps its 1.1.0 name. It now chooses the whole set, not only the crown.

### Set format

One JSON file per skill in `skill-tree/gear/<skill id>.json`. The full template (grid, slot limits, anchors) is `skill-tree/gear/README.md`.

- `id`, `name`, `colour` (the skill's glow colour), `palette` (letter to colour, 16 colours at most). Colours are free per skill. Two skills on one page can't have glow colours too close to tell apart.
- `items`: exactly 7, one per level, each with `level`, `slot`, `name`, `rows` (the pixel art as text rows), `x`, `y` (where it sits on the 28 x 40 item grid).
- Slot extras: the tool has a hand anchor (`hand`), the back item has a strap layer (`front`), the companion has a blink frame (`blink`), the crown lists its gem pixels (`gems`).
- Checked by `.claude/skills/learn/scripts/gear_check.py`, and by `build_pack.py` for every skill a pack names. A set that fails never loads.

### Data

- `player/me.gear = { v: 2, worn: { badge, tool, face, book, back, pet, crown } }`. All seven slots are always written. Each value is the skill id whose item is worn in that slot, or `null` when the slot is empty. Written by the page only: on every inventory tap, and once on the first open after the update. **Never write `gear` from `/learn`.**
- `player/me.gearSeen`: a list of `"<skill id>:<level>"` strings (e.g. `"sql:3"`), one per item already announced. Written by the page only. A level that drops stays in the list. Old 1.1.0 strings are ignored and dropped on the next write.
- Anything in `gear` that isn't the `v: 2` shape (the 1.1.0 `head`, `face`, `body`, `hands`, `back`, `pet` included) counts as nothing worn. On the first open the page saves the empty `v: 2` shape and sets `gearSeen` to everything already earned. That is the day-one screen.
- The page drops anything worn that isn't earned any more (the level fell, the skill was removed, or the skill has no usable set). It checks on every read and before every write.
- `gear/<skill id>`: one document per skill with its own set, in the set format above. Written by `/learn` with the topic (a plain `set`). Presets have no document. **The document id must be the stat id**: the page matches a set to a skill by the document id, not by the `id` inside it.
- **The page's own shape check.** The page uses a `gear/<skill id>` document only if it is safe to draw: 7 items in slot order, `colour` and every palette value a `#rrggbb` hex, every `rows` block non-empty with equal-width rows (60 at most each way), whole-number `x` and `y` on the canvas (x -16 to 43, y -18 to 41), a `front` layer on the back item, a `blink` frame the same size as `rows` on the companion, at least one gem on the crown (64 at most), and a palette of 32 colours at most. A document that fails is treated as no set: the skill shows placeholders and "set not made yet", nothing it had is worn, and the page carries on. `gear_check.py` is stricter on every one of these points, so a set that passed the checker always passes the page. Never load a set that hasn't passed the checker.
- `stats/<id>.crown`: optional. A preset id, or `own`.

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
