# Update notes

Newest first. `/learn update` reads this file after you unzip an update into your work project folder. Each entry says what changed and what `/learn update` has to do.

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
