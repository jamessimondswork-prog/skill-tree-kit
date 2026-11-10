# Gear sets

Every skill has a set of 7 items. The learner earns one per mastery level in that skill.
One JSON file per skill lives here: `skill-tree/gear/<skill-id>.json`. It loads to the page database as the document `gear/<skill-id>`.

Four sets are hand-made presets and are built into the page as well, so they work with no load:

| File | Skill | Glow colour |
|---|---|---|
| `sql.json` | SQL | `#1fb6ff` |
| `power-bi.json` | Power BI | `#ffb000` |
| `git-github.json` | Git & GitHub | `#f05033` |
| `ai-agents.json` | AI agents | `#9b6bff` |

Any other skill gets its own set, drawn when the skill is first built and saved here (or in the topic folder, see "Where build_pack looks"). `skill-tree/example/gear/example-formulas.json` is a worked example at the simpler level a new set is drawn at.

Don't edit the four preset files. They are the same for everyone.

## The format

```json
{
  "id": "sql",
  "name": "SQL",
  "colour": "#1fb6ff",
  "palette": { "k": "#071428", "4": "#1fb6ff", "c": "#f2c14e" },
  "items": [
    { "level": 1, "slot": "badge", "name": "Table Pin", "x": 11, "y": 23, "rows": [".bcccb.", "c44444c"] },
    { "level": 2, "slot": "tool",  "name": "...", "x": -5, "y": 25, "rows": ["..."], "hand": [11, 3] },
    { "level": 3, "slot": "face",  "name": "...", "x": 6,  "y": 11, "rows": ["..."] },
    { "level": 4, "slot": "book",  "name": "...", "x": 31, "y": 3,  "rows": ["..."] },
    { "level": 5, "slot": "back",  "name": "...", "x": -2, "y": 7,  "rows": ["..."], "front": { "x": 9, "y": 21, "rows": ["..."] } },
    { "level": 6, "slot": "pet",   "name": "...", "x": 30, "y": 24, "rows": ["..."], "blink": ["..."] },
    { "level": 7, "slot": "crown", "name": "...", "x": 4,  "y": -10, "rows": ["..."], "gems": [[10, 2], [3, 5]] }
  ]
}
```

| Field | Rule |
|---|---|
| `id` | The skill (stat) id, kebab-case. Same as the file name. |
| `name` | The skill's name. |
| `colour` | The skill's glow colour, `#rrggbb`. The page tints all four effects with it. |
| `palette` | Single letter or digit to `#rrggbb`. 16 colours at most. `.` is never a key: it means empty. |
| `items` | Exactly 7, in level order. Level 1 to 7 is always `badge`, `tool`, `face`, `book`, `back`, `pet`, `crown`. |
| `level`, `slot` | Must match the item's place in the list. |
| `name` | 1 to 24 characters. Never a company, client, product or person from the learner's work. |
| `rows` | The pixel art, top row first. One string per row, one character per pixel, all rows the same width. `.` is empty. Every other character must be in the palette. |
| `x`, `y` | Where the top left pixel of `rows` sits on the item grid. Whole numbers. Can be negative. |

Slot extras:

| Slot | Extra | Rule |
|---|---|---|
| `tool` | `hand: [x, y]` | The pixel of the handle that sits in the hand, counted inside `rows` (0, 0 is its top left). It must be a drawn pixel, and `x + hand[0]`, `y + hand[1]` must land in the hand box. |
| `back` | `front: { x, y, rows }` | `rows` is the layer behind the character. `front` is the strap layer drawn over the shirt. Both are needed. |
| `pet` | `blink: [rows]` | A second frame with the eyes shut. Same size as `rows`, and not identical to it. |
| `crown` | `gems: [[x, y], ...]` | At least one. Each is a drawn pixel inside `rows`. These are the pixels that sparkle in turn. |

Effects are not in the file. The page owns the four effects (book, back item, companion, crown) and tints them with `colour`. A set can't add its own animation.

## The item grid

- The character is 21 x 30 pixels. Items are drawn on a finer 28 x 40 grid that covers the same space. One character pixel is 4 screen units, one item pixel is 3.
- Item pixel (0, 0) is the top left of the character. x runs right, y runs down.
- Items can sit outside the character. The whole canvas is 60 x 60 item pixels: x from -16 to 43, y from -18 to 41.
- The character faces you, so its right hand is on the left of the picture.

Where things are on the default character, in item pixels:

| Part | x | y |
|---|---|---|
| Hair | 3 to 25 | 1 to 15 |
| Face | 7 to 21 | 9 to 18 |
| Eyes | 9 to 11 and 16 to 18 | 12 to 14 |
| Mouth | 12 to 15 | 16 to 17 |
| Shirt | 4 to 23 (8 to 19 between the arms) | 20 to 29 |
| Tool hand | 5 to 7 | 25 to 29 |
| Legs and boots | 8 to 19 | 29 to 38 |
| Ground | | 39 |

## Slot limits

Biggest size (width x height) and the area every pixel of the item must stay inside:

| Slot | Biggest size | x | y |
|---|---|---|---|
| `badge` | 8 x 8 | 8 to 19 | 21 to 29 |
| `tool` | 16 x 16 | -12 to 11 | 20 to 40 |
| `face` | 18 x 7 | 5 to 22 | 10 to 17 |
| `book` | 14 x 16 | 30 to 43 | 0 to 22 |
| `back` | 40 x 30 | -6 to 33 | 2 to 30 |
| `pet` | 14 x 15 | 28 to 43 | 22 to 40 |
| `crown` | 22 x 16 | 2 to 25 | -14 to 7 |

The back item's `front` layer: 20 x 12 at most, inside x 4 to 23, y 19 to 31.

Anchors and the rules that go with them:

- **Hand.** The tool's hand point must land inside x 5 to 7, y 26 to 29. Tools hang down or point down and out from the hand (the tool area starts at y 20), which keeps them clear of back items.
- **Hairline.** The face piece's top row is 10 or lower, so it always fits under a crown.
- **Crown base.** The crown's bottom row is between 2 and 6, so it sits on the hair.
- **Tallest head item.** The crown is taller than the face piece, and its top row is above the top row of every other item in the set.
- **Back item shows.** At least 40 pixels of the back layer must show past the default character. The body hides x 4 to 23 from the shoulders down, so draw the main shapes at x 3 or less and x 24 or more. Keep the right side at x 29 or less so it doesn't run into the book.
- **Book.** Floats by the shoulder at about x 31, y 3, one pixel clear of the back item. The page bobs it up and down by a pixel or two.
- **Companion.** Stands on the ground: bottom row at about y 38.

## What the page does with a set

Back to front: back layer, character, front straps, badge, face piece, tool, crown, book, companion. Small icons (leaderboard rows, mini avatars) show the worn items with no effects and no companion. Locked items show as a dark outline of the same `rows`.

## The checker

```
python -I -X utf8 .claude/skills/learn/scripts/gear_check.py skill-tree/gear/<skill-id>.json --id <skill-id> --terms "<term>,<term>" --used-colours "#1fb6ff,#ffb000"
```

It prints `OK` and exits 0, or prints one line per problem and exits 1. It fails a set when:

- there aren't exactly 7 items, or a level has the wrong slot
- rows are uneven or empty, a letter isn't in the palette, a colour isn't a valid hex, or the palette has over 16 colours
- an item is bigger than its slot allows, sits off the canvas or sits outside its area
- the face piece covers the hairline, or the crown isn't the tallest head item or doesn't sit on the head
- the crown would sit on the face piece on short hair: the page lowers the crown by up to 4 rows (Buzz hair), so the crown's bottom row plus 4 must stay above the face piece's top row
- any drawn pixel is left of x -7 or right of x 43: the inventory picture shows x -7 to 43, and anything past it is cut off
- a crown has no gems, over 64 gems, or a gem that isn't on the crown, or a companion has no blink frame
- the tool has no hand point or the handle isn't in the hand
- the back item has no front layer, or is mostly hidden behind the body
- an item name is empty, over 24 characters, or contains one of the `--terms`. The set's own name can be 40 characters and gets the same terms check
- the set's `id` is not the `--id` given
- the glow colour is too close to one in `--used-colours`

**Glow colour rule.** The distance between two colours is the straight-line distance between their red, green and blue values (0 to 255 each): `sqrt(dr*dr + dg*dg + db*db)`. Two glow colours must be 60 or more apart. The four presets are at least 100 apart from each other.

`--id` is the skill (stat) id the set is for. `--terms` is the learner's privacy terms (company, client, product and people names). A term matches as a whole word or phrase, any case: "Sam" matches "Sam Pin" but not "Sample Pin". `--used-colours` is every glow colour already on that learner's page: the four presets plus any other set in `skill-tree/gear/`.

A set file kept for a skill that uses a preset must have that preset's art. `gear_check.compare(a, b)` lists the differences between two sets (the `id` and set `name` may differ, nothing else), and `build_pack.py` runs it.

## Where build_pack looks

`build_pack.py` checks every skill a pack names:

1. A skill that matches a preset needs no file. Presets match by stat id only, never by name. Each preset has a list of ids: SQL `sql`; Power BI `power-bi` and `powerbi`; Git & GitHub `git-github` and `git`; AI agents `agents`, `agentic-os` and `ai-agents`. A pack can set `crown` on the topic (or on a quest that has its own `stat`) to a preset id to pick that preset, or to `own` to opt out and use its own set.
   - One preset dresses one skill on a page. If two skills on the same page would get the same preset, the one whose id comes first in that preset's id list keeps it (for Power BI: `power-bi` before `powerbi`; for Git & GitHub: `git-github` before `git`; for AI agents: `agents`, then `agentic-os`, then `ai-agents`; then the lower stat id). The other one needs its own set. The build stops with a line naming that skill. It reads the skills already on the page from `skill-tree/state/stats/`, and a skill already on the page always keeps its set.
   - If a file for that skill is in a `gear/` folder anyway, it must be the preset's art exactly, or the build stops.
2. Any other skill needs `<topic folder>/gear/<skill-id>.json` or `skill-tree/gear/<skill-id>.json`. The build stops if the file is missing or the checker finds a problem.
3. The set goes into the pack's `writes.json` as the document `gear/<skill-id>`.

Pass the privacy terms to the build as well: `build_pack.py <topic folder> --terms "<term>,<term>"`.
