# Update notes

Newest first. `/learn update` reads this file after an update is installed (fetched by `/learn update` itself, or unzipped into your work project folder). Each entry says what changed and what `/learn update` has to do.

## 1.2.0 (item sets, inventory and auto-update)

- New on your page: every skill now has its own set of 7 items for your character. You earn one per level you prove in that skill: chest badge (1), tool (2), face piece (3), book (4), back item (5), companion (6) and crown (7). The last four have effects in the skill's own colour.
- New: an inventory. Press the backpack button next to the cog to see every item across your skills. Tap to wear, tap again to take off. You can mix items from different skills. Locked items show what to pass. "Wear full set" puts on everything you've earned in one skill, and pressing it again takes that set off.
- New: a share card. The Share card button in the inventory saves a picture of your character. If your browser can't download it, the picture shows on the page so you can save it from there.
- Your character is redrawn in a sharper style. Your look, trophies, XP, ranks, streaks and quests don't change.
- Gone: the 1.1.0 gear (Champion belt, Victory scarf, Shades, Golden gloves, Flame aura, Wings, Pixel pet), the rank crown and the Master crowns. The rank headband and cape stay. A crown now only comes from level 7 in a skill.
- What you see on first open: one screen that lists the items you've already earned, with a button to the inventory. Nothing is put on for you, and the old gear is off. After that, each new item gets its own screen (or one list when more than three arrive together).
- New: `/learn update` now checks the kit's public home for a newer version by itself, shows you what changed and asks before installing. It installs exactly the version you agreed to and replaces kit files only. Unzipping an update by hand still works.
- **Before the republish (do this first):** give every existing skill with no preset its item set, and load it. Do all of this before Update mode step 2. A `gear/<stat id>` document does nothing on the old page, so loading early is safe. If the page goes up first, the learner's first open misses those skills and the one "already earned" screen never shows them.
  1. ArtifactData `list` on `stats` and on `gear`.
  2. Skip a skill that matches a preset, unless its `crown` is `own`. Presets match by stat id only: SQL `sql`; Power BI `power-bi` and `powerbi`; Git & GitHub `git-github` and `git`; AI agents `agents`, `agentic-os` and `ai-agents`, and any stat whose `crown` names a preset. A skill that only has "agent" in its name is not a preset any more: it gets its own set. Presets are built into the page and need no load.
     - One preset dresses one skill on a page. If two skills on the same page would get the same preset, the one whose id comes first in that preset's id list keeps it (for Power BI: `power-bi` before `powerbi`; for Git & GitHub: `git-github` before `git`; for AI agents: `agents`, then `agentic-os`, then `ai-agents`; then the lower stat id). The other one needs its own set from step 4.
  3. Skip a skill that already has a `gear/<stat id>` document.
  4. For every other skill: make its set as SKILL.md "Gear set for a new skill" steps 2 and 3 say. Save it as `skill-tree/gear/<stat id>.json` and run `gear_check.py` on it with `--id <stat id>`, `--terms` (the learner's privacy terms) and `--used-colours` (the `colour` of every other set in `skill-tree/gear/`) until it prints OK.
  5. Load each one with ArtifactData `set`: collection `gear`, doc id `<stat id>`, `file_path` = `skill-tree/gear/<stat id>.json`. It is a new document, so there is no version to pin. The doc id must be the stat id exactly: the page matches on it. Only load a set the checker passed. The page ignores a set whose shape is wrong and shows that skill as "set not made yet".
  6. Tell the learner each new set's name and colour, one line each.
  7. Leave `player/me` alone. On first open the page saves the new `gear` shape (`v: 2`, nothing worn), which is what marks the player as updated, and sets `gearSeen` to what is already earned. Leave `stats/<id>.crown` as it is: a preset id or `own` still works, and now picks the whole set.
- Page: republish (Update mode step 2), only once every set above is loaded and checked with ArtifactData `list` on `gear`. The new items only show once the page is republished.
- Capabilities: no change. The share card uses the downloads capability the page already has.
- Data steps: none after the republish.
- Index: in `skill-tree/INDEX.md`, edit these rows only; never replace the file (it lists the learner's own topics).
  - `player/me` row: `gear` is now `{ v: 2, worn: { badge, tool, face, book, back, pet, crown } }`, all seven always written, each the skill id worn in that slot or `null`, set by the page only. `gearSeen` is now a list of `<skill id>:<level>` strings.
  - `stats/<id>` row: `crown` (a preset id, or `own`) now picks the skill's whole item set.
  - Add a row `gear/<skill id>`: the skill's own item set (`id`, `name`, `colour`, `palette`, `items[7]`), written by `/learn` from `skill-tree/gear/<skill id>.json`.
  - Add a "Gear sets" line to the list at the top: `skill-tree/gear/`, one file per skill, template in `skill-tree/gear/README.md`, checked with `.claude/skills/learn/scripts/gear_check.py`.
  - In "Stats so far", note each skill's set: the preset, or its own set's name and colour.
- Checker (`build_pack.py`): changed. A skill with no preset now needs a set file, and the build takes `--terms`. After the data steps, re-run it on every active topic and its trials file (Update mode step 4). Load nothing from these runs.
- New scripts: `gear_check.py` (checks a set) and `fetch_update.py` (fetches an update). `pending_writes.py` now accepts a `gear` write after the cards.
- `lastUpdate`: Update mode step 5 sets it to `1.2.0` in `setup.json`, only after every step above worked. If a step failed it stays as it was, so the next `/learn update` tries again.

## 1.1.0 (gear and Master crowns)

- New on your page: gear for your character. Reach Champion rank to unlock a Champion belt, Victory scarf, Shades and Golden gloves. Reach Legend for a Flame aura, Wings and a Pixel pet. Wear them from the ⚙ button, one item per slot.
- Master a skill (level 7) and you earn that skill's own crown. It replaces the rank crown while you wear it.
- Page: republish (Update mode step 2).
- Capabilities: no change.
- Data steps: none. Gear is saved by the page itself.
- Index: in `skill-tree/INDEX.md`, add `gear`, `gearSeen` to the `player/me` row and `crown` (optional preset id, or `own`) to the `stats/<id>` row. Edit those rows only; never replace the file (it lists the learner's own topics).
- Checker (`build_pack.py`): no change.
- Update mode now records the version it applied in `setup.json` (`lastUpdate`).

## 1.0.0 (first release)

- First release.
- Page: no change to republish.
- Capabilities: no change.
- Data steps: none.
- Checker (`build_pack.py`): no change.
