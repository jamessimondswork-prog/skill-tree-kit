"""Check a Skill Tree gear set (the 7 items a skill gives, one per mastery level).

  python -I -X utf8 gear_check.py <set.json> [--id <stat id>] [--terms "a,b"] [--used-colours "#aabbcc,#ddeeff"]

Exit 0 on pass, 1 with one plain line per problem, 2 on a usage error.
  --id             the skill (stat) id this set is for. The set's own id must equal it
  --terms          words that must never appear in a name (the learner's privacy terms), comma-separated.
                   A term matches as a whole word or phrase, any case ("Sam" does not match "Sample")
  --used-colours   glow colours already on this learner's page, comma-separated hex

The format, the slot limits and the anchors are written down in skill-tree/gear/README.md.
build_pack.py runs the same checks through check(). compare() tells you whether two sets that
should share a preset really have the same art.
"""
import json
import math
import re
import sys

USAGE = 'usage: gear_check.py <set.json> [--id <stat id>] [--terms "a,b"] [--used-colours "#aabbcc,#ddeeff"]'

SLOTS = ("badge", "tool", "face", "book", "back", "pet", "crown")
LABEL = {"badge": "badge", "tool": "tool", "face": "face piece", "book": "book",
         "back": "back item", "pet": "companion", "crown": "crown"}

# The item grid is 28 x 40 and covers the character. x and y can run past it: the whole canvas is
# 60 x 60 item pixels with the character's top left corner at (0, 0).
CANVAS = (-16, -18, 43, 41)                       # x0, y0, x1, y1, inclusive

# Per slot: the biggest sprite allowed (w, h) and the box every pixel must stay inside (x0, y0, x1, y1).
MAX_SIZE = {"badge": (8, 8), "tool": (16, 16), "face": (18, 7), "book": (14, 16),
            "back": (40, 30), "pet": (14, 15), "crown": (22, 16)}
ZONE = {"badge": (8, 21, 19, 29), "tool": (-12, 20, 11, 40), "face": (5, 10, 22, 17), "book": (30, 0, 43, 22),
        "back": (-6, 2, 33, 30), "pet": (28, 22, 43, 40), "crown": (2, -14, 25, 7)}
FRONT_MAX = (20, 12)                              # the back item's strap layer, drawn over the shirt
FRONT_ZONE = (4, 19, 23, 31)
HAIRLINE = 10                                     # the face piece's top row can't be above this
HAND = (5, 26, 7, 29)                             # the tool's hand anchor must land in this box
CROWN_BASE = (2, 6)                               # the crown's bottom row must sit on the hair, between these rows
BACK_VISIBLE = 40                                 # this many back item pixels must show past the body
CROWN_DROP = 4                                    # the page lowers the crown this many rows on the lowest hair style (Buzz)
STAGE_X = (-7, 43)                                # the inventory stage shows these columns. Anything drawn outside is cut off
NAME_MAX = 24
SET_NAME_MAX = 40                                 # the set's name is the skill's name, which runs longer than an item's
PALETTE_MAX = 16
GEMS_MAX = 64                                     # the page ignores a set with more gems than this
COLOUR_GAP = 60                                   # two glow colours closer than this look the same

PRESETS = ("sql", "power-bi", "git-github", "ai-agents")
AGENT_IDS = ("agents", "agentic-os", "ai-agents")
# The one source of truth for which skill ids get which preset. Matching is by id only, never by name.
# The order of each list matters: when two skills on one page want the same preset, the earlier id keeps it.
# `powerbi` and `git` are ids already in use on a live page, so they stay matched. The page holds the same lists (GEAR_PRESET_IDS).
PRESET_IDS = {"sql": ("sql",), "power-bi": ("power-bi", "powerbi"), "git-github": ("git-github", "git"), "ai-agents": AGENT_IDS}

# The default character, 21 x 30. Only the outline matters here: any letter is body, '.' is empty.
# One character pixel is 4 screen units and one item pixel is 3, so the character fills the 28 x 40 item grid.
BODY = [
    ".....................", "......hhhhhhhhh......", "....hhHHhhhhhhhhh....", "...hhHhhhhhhhhhhhh...", "..hhhhhhhhhhhhhhhhh..",
    "..hhhhhhhhhhhhhhhhh..", "..hhhhhhhhhhhhhhhhh..", "..hhhssssssssssshhh..", "..hhhssssssssssshhh..", "..hhhsswesssewsshhh..",
    "...hhsswesssewsshh...", "...hhssssssssssshh...", "......sssmmmsss......", ".......sssssss.......", "........nnnnn........",
    ".....oowwssswwoo.....", "...ooooooowooooood...", "...ooooooooooooood...", "...wwwooooooooowww...", "....ssoooooooodss....",
    "....ssoooooooodss....", "....ssoooooooodss....", "......ddddddddd......", "......dddd.dddd......", ".......sss.sss.......",
    ".......www.www.......", ".......ooo.ooo.......", ".......bbb.bbb.......", "......bbbb.bbbb......", ".....................",
]

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def body_at(x, y):
    """Is the item-grid pixel (x, y) covered by the default character? Tested at the pixel's centre."""
    col, row = int((x * 3 + 1.5) // 4), int((y * 3 + 1.5) // 4)
    return 0 <= row < len(BODY) and 0 <= col < len(BODY[0]) and BODY[row][col] != "."


def colour_distance(a, b):
    """Straight-line distance between two #rrggbb colours (0 = same, 441 = black to white)."""
    pa, pb = (int(a[i:i + 2], 16) for i in (1, 3, 5)), (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(pa, pb)))


def preset_for(stat_id, name="", crown=None):
    """Which hand-made preset a skill asks for, or None. Same rule as the page: the stat's `crown` field first
    (`own` opts out, a preset id forces that preset), then the id. By id only: `name` is not used (it stays in the
    signature for older callers)."""
    if crown == "own":
        return None
    if isinstance(crown, str) and crown in PRESETS:
        return crown
    for preset, ids in PRESET_IDS.items():
        if stat_id in ids:
            return preset
    return None


def resolve_presets(stats):
    """One preset can dress only one skill on a page. `stats` is an iterable of (stat id, crown).
    Returns {stat id: preset id or None}. When several skills ask for the same preset, the first one keeps it:
    in the order of that preset's id list (PRESET_IDS), then by stat id. The others get None and need their own set."""
    out, asks = {}, {}
    for stat_id, crown in stats:
        preset = preset_for(stat_id, "", crown)
        out[stat_id] = None
        if preset:
            asks.setdefault(preset, []).append(stat_id)
    for preset, ids in asks.items():
        order = PRESET_IDS[preset]
        winner = sorted(set(ids), key=lambda i: (order.index(i) if i in order else len(order), i))[0]
        out[winner] = preset
    return out


def term_hit(term, text):
    """Does a privacy term appear in text as a whole word or phrase? Any case. "Sam" hits "Sam's Pin", not "Sample Pin"."""
    term = (term or "").strip()
    if not term or not isinstance(text, str):
        return False
    pre = r"(?<![A-Za-z0-9])" if term[0].isalnum() else ""
    post = r"(?![A-Za-z0-9])" if term[-1].isalnum() else ""
    return re.search(pre + re.escape(term) + post, text, re.I) is not None


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _rows_problems(tag, what, rows, palette):
    """Shape problems for one block of rows. Returns (problems, usable)."""
    if not isinstance(rows, list) or not rows or not all(isinstance(r, str) and r for r in rows):
        return ["%s: %s must be a list of text rows, one per pixel row" % (tag, what)], False
    p = []
    widths = sorted(set(len(r) for r in rows))
    if len(widths) > 1:
        p.append("%s: %s are uneven (%s wide). Every row must be the same width, with '.' for empty"
                 % (tag, what, " and ".join(str(w) for w in widths)))
    missing = sorted(set("".join(rows)) - set(palette) - {"."})
    if missing:
        p.append("%s: %s use %s, which %s not in the palette"
                 % (tag, what, ", ".join("'%s'" % m for m in missing), "is" if len(missing) == 1 else "are"))
    if not p and not any(ch != "." for r in rows for ch in r):
        p.append("%s: %s are empty. Draw something" % (tag, what))
    return p, len(widths) == 1


def _box_problems(tag, what, rows, x, y, max_size, zone, zone_name):
    """Size, canvas and zone problems for rows placed at x, y."""
    p = []
    w, h = len(rows[0]), len(rows)
    if w > max_size[0] or h > max_size[1]:
        p.append("%s: %s is %d x %d, bigger than the %d x %d this slot allows" % (tag, what, w, h, max_size[0], max_size[1]))
    x1, y1 = x + w - 1, y + h - 1
    if x < CANVAS[0] or y < CANVAS[1] or x1 > CANVAS[2] or y1 > CANVAS[3]:
        p.append("%s: %s sits off the canvas (it covers x %d to %d, y %d to %d; the canvas is x %d to %d, y %d to %d)"
                 % (tag, what, x, x1, y, y1, CANVAS[0], CANVAS[2], CANVAS[1], CANVAS[3]))
    elif x < zone[0] or y < zone[1] or x1 > zone[2] or y1 > zone[3]:
        p.append("%s: %s is outside %s (it covers x %d to %d, y %d to %d; it must stay inside x %d to %d, y %d to %d)"
                 % (tag, what, zone_name, x, x1, y, y1, zone[0], zone[2], zone[1], zone[3]))
    return p


def _stage_problems(tag, what, rows, x):
    """Drawn pixels left or right of the inventory stage would be cut off there."""
    cols = [x + i for r in rows for i, ch in enumerate(r) if ch != "."]
    if cols and (min(cols) < STAGE_X[0] or max(cols) > STAGE_X[1]):
        return ["%s: %s is drawn from x %d to %d, past the edge of the inventory picture. Keep every drawn pixel inside x %d to %d"
                % (tag, what, min(cols), max(cols), STAGE_X[0], STAGE_X[1])]
    return []


def check(data, terms=(), used_colours=(), expected_id=None):
    """Every problem with a set, as plain lines. An empty list means it passes.
    expected_id is the skill (stat) id the set is for: the set's own id must equal it."""
    if not isinstance(data, dict):
        return ["The set file is not a JSON object"]
    p = []
    sid = data.get("id")
    if not (isinstance(sid, str) and KEBAB.match(sid)):
        p.append("id must be the skill id in kebab-case, e.g. power-bi")
    if expected_id is not None and sid != expected_id:
        p.append("The set's id is %r. It must be %r, the id of the skill it is for" % (sid, expected_id))
    name = data.get("name")
    if not (isinstance(name, str) and name.strip()):
        p.append("The set needs a name (the skill's name)")
        name = ""
    elif len(name.strip()) > SET_NAME_MAX:
        p.append("Set name '%s': the name is %d characters. The most is %d" % (name.strip(), len(name.strip()), SET_NAME_MAX))
    colour = data.get("colour")
    if not (isinstance(colour, str) and HEX.match(colour)):
        p.append("colour (the glow colour) must be a hex colour like #1fb6ff, got %r" % (colour,))
        colour = None
    palette = data.get("palette")
    if not isinstance(palette, dict) or not palette:
        p.append("palette must map single letters to hex colours")
        palette = {}
    if len(palette) > PALETTE_MAX:
        p.append("The palette has %d colours. The most a set can have is %d" % (len(palette), PALETTE_MAX))
    for k, v in palette.items():
        if not (isinstance(k, str) and len(k) == 1 and k.isalnum() and k.isascii()):
            p.append("Palette key '%s' must be a single letter or digit" % k)
        if not (isinstance(v, str) and HEX.match(v)):
            p.append("Palette colour '%s' is %r, which is not a valid hex colour like #1fb6ff" % (k, v))

    def name_problems(tag, value):
        out = []
        for term in terms:
            if term_hit(term, value):
                out.append("%s: the name contains the private term '%s'" % (tag, term.strip()))
        return out

    p += name_problems("Set name '%s'" % name, name)

    for used in used_colours:
        if colour and isinstance(used, str) and HEX.match(used) and colour_distance(colour, used) < COLOUR_GAP:
            p.append("Glow colour %s is too close to %s, which another skill on this page already uses "
                     "(distance %d, needs %d or more). Pick a colour that looks different"
                     % (colour, used, colour_distance(colour, used), COLOUR_GAP))

    items = data.get("items")
    if not isinstance(items, list) or len(items) != 7:
        return p + ["A set needs exactly 7 items, one per level. This one has %s"
                    % (len(items) if isinstance(items, list) else "no items list")]

    placed = {}                                   # slot -> (x, y, w, h) for the cross-item rules
    for n, it in enumerate(items):
        level, slot = n + 1, SLOTS[n]
        if not isinstance(it, dict):
            p.append("Item %d is not an object" % level)
            continue
        iname = it.get("name")
        shown = iname.strip() if isinstance(iname, str) else ""
        tag = "Level %d %s '%s'" % (level, LABEL[slot], shown) if shown else "Level %d %s" % (level, LABEL[slot])
        if it.get("level") != level or it.get("slot") != slot:
            p.append("Item %d must be level %d in the %s slot (the order is %s). Found level %r, slot %r"
                     % (level, level, slot, ", ".join(SLOTS), it.get("level"), it.get("slot")))
            continue
        if not shown:
            p.append("%s: the name is empty. Every item needs a short name" % tag)
        elif len(shown) > NAME_MAX:
            p.append("%s: the name is %d characters. The most is %d" % (tag, len(shown), NAME_MAX))
        p += name_problems(tag, shown)

        x, y = it.get("x"), it.get("y")
        if not (_is_int(x) and _is_int(y)):
            p.append("%s: x and y must be whole numbers on the item grid" % tag)
            continue
        rp, usable = _rows_problems(tag, "rows", it.get("rows"), palette)
        p += rp
        if not usable:
            continue
        rows = it["rows"]
        w, h = len(rows[0]), len(rows)
        zone = ZONE[slot]
        if slot == "face" and y < HAIRLINE:           # the hairline has its own, clearer line below
            zone = (zone[0], CANVAS[1], zone[2], zone[3])
        p += _box_problems(tag, "it", rows, x, y, MAX_SIZE[slot], zone, "the %s area" % LABEL[slot])
        p += _stage_problems(tag, "it", rows, x)
        placed[slot] = (x, y, w, h)

        if slot == "tool":
            hand = it.get("hand")
            if not (isinstance(hand, list) and len(hand) == 2 and all(_is_int(v) for v in hand)):
                p.append("%s: needs hand [x, y], the pixel of the handle that sits in the character's hand" % tag)
            elif not (0 <= hand[0] < w and 0 <= hand[1] < h) or rows[hand[1]][hand[0]] == ".":
                p.append("%s: hand %s is not on a drawn pixel of the tool" % (tag, hand))
            else:
                hx, hy = x + hand[0], y + hand[1]
                if not (HAND[0] <= hx <= HAND[2] and HAND[1] <= hy <= HAND[3]):
                    p.append("%s: the handle is not in the hand. Its hand point lands at (%d, %d); the hand is x %d to %d, y %d to %d"
                             % (tag, hx, hy, HAND[0], HAND[2], HAND[1], HAND[3]))
        elif slot == "face":
            if y < HAIRLINE:
                p.append("%s: it covers the hairline. Its top row is %d; the face piece must start at row %d or lower so a crown still fits"
                         % (tag, y, HAIRLINE))
        elif slot == "back":
            front = it.get("front")
            if not isinstance(front, dict) or not (_is_int(front.get("x")) and _is_int(front.get("y"))):
                p.append("%s: needs a front layer (the straps drawn over the shirt): front {x, y, rows}" % tag)
            else:
                fp, fusable = _rows_problems(tag, "front rows", front.get("rows"), palette)
                p += fp
                if fusable:
                    p += _box_problems(tag, "the front layer", front["rows"], front["x"], front["y"], FRONT_MAX, FRONT_ZONE, "the strap area")
                    p += _stage_problems(tag, "the front layer", front["rows"], front["x"])
            seen = sum(1 for j, r in enumerate(rows) for i, ch in enumerate(r) if ch != "." and not body_at(x + i, y + j))
            if seen < BACK_VISIBLE:
                p.append("%s: it is mostly hidden behind the body. Only %d pixels show; at least %d must show past the character"
                         % (tag, seen, BACK_VISIBLE))
        elif slot == "pet":
            blink = it.get("blink")
            if blink is None:
                p.append("%s: needs a blink frame: blink [rows], the same size as rows with the eyes shut" % tag)
            else:
                bp, busable = _rows_problems(tag, "blink rows", blink, palette)
                p += bp
                if busable and (len(blink) != h or len(blink[0]) != w):
                    p.append("%s: the blink frame is %d x %d but the companion is %d x %d. They must be the same size"
                             % (tag, len(blink[0]), len(blink), w, h))
                elif busable and blink == rows:
                    p.append("%s: the blink frame is the same as the open-eyed frame. Draw the eyes shut" % tag)
        elif slot == "crown":
            gems = it.get("gems")
            if not isinstance(gems, list) or not gems:
                p.append("%s: a crown needs gems: gems [[x, y], ...], the pixels that sparkle" % tag)
            elif len(gems) > GEMS_MAX:
                p.append("%s: it lists %d gems. The most is %d" % (tag, len(gems), GEMS_MAX))
            else:
                for g in gems:
                    if not (isinstance(g, list) and len(g) == 2 and all(_is_int(v) for v in g)
                            and 0 <= g[0] < w and 0 <= g[1] < h and rows[g[1]][g[0]] != "."):
                        p.append("%s: gem %s is not on a drawn pixel of the crown" % (tag, g))
            base = y + h - 1
            if not CROWN_BASE[0] <= base <= CROWN_BASE[1]:
                p.append("%s: it does not sit on the head. Its bottom row is %d; it must be between %d and %d"
                         % (tag, base, CROWN_BASE[0], CROWN_BASE[1]))

    if "crown" in placed:
        cx, cy, cw, ch = placed["crown"]
        if "face" in placed and cy + ch - 1 + CROWN_DROP >= placed["face"][1] and placed["face"][1] >= HAIRLINE:
            p.append("The crown would overlap the face piece on short hair. The page lowers the crown by up to %d rows, so its bottom row (%d) "
                     "plus %d must stay above the face piece's top row (%d)" % (CROWN_DROP, cy + ch - 1, CROWN_DROP, placed["face"][1]))
        if "face" in placed and ch <= placed["face"][3]:
            p.append("The crown must be the tallest head item. It is %d rows tall and the face piece is %d"
                     % (ch, placed["face"][3]))
        for slot in SLOTS[:-1]:
            if slot in placed and placed[slot][1] <= cy:
                p.append("The crown must be the tallest head item. Its top row is %d but the %s starts at row %d, level with it or above it"
                         % (cy, LABEL[slot], placed[slot][1]))
    return p


def compare(a, b):
    """Two sets that should share a preset must have the same art. Returns the differences as plain lines.
    The id and the set name can differ (they belong to each learner's skill). Everything else can't."""
    if not (isinstance(a, dict) and isinstance(b, dict)):
        return ["Both sets must be JSON objects"]
    who = "%s and %s" % (a.get("id"), b.get("id"))
    p = []
    if a.get("colour") != b.get("colour"):
        p.append("%s should share a preset but have different glow colours (%s and %s)" % (who, a.get("colour"), b.get("colour")))
    if a.get("palette") != b.get("palette"):
        p.append("%s should share a preset but have different palettes" % who)
    ia, ib = a.get("items") or [], b.get("items") or []
    if len(ia) != len(ib):
        p.append("%s should share a preset but have %d and %d items" % (who, len(ia), len(ib)))
    for n, (x, y) in enumerate(zip(ia, ib)):
        if x != y:
            keys = sorted(k for k in set(x) | set(y) if x.get(k) != y.get(k)) if isinstance(x, dict) and isinstance(y, dict) else ["item"]
            p.append("%s should share a preset but level %d differs (%s)" % (who, n + 1, ", ".join(keys)))
    return p


def _option(argv, flag):
    """The comma-separated value after a flag, as a list. None when the flag isn't given."""
    if flag not in argv:
        return None
    i = argv.index(flag)
    value = argv[i + 1] if i + 1 < len(argv) else ""
    if value.startswith("--"):
        value = ""
    out = [v.strip() for v in value.split(",") if v.strip()]
    if not out:
        raise ValueError("%s needs a value" % flag)
    return out


def main(argv):
    args, i = [], 1
    while i < len(argv):
        if argv[i] in ("--terms", "--used-colours", "--id"):
            i += 2
            continue
        if argv[i].startswith("--"):
            print("unknown option %s. %s" % (argv[i], USAGE))
            return 2
        args.append(argv[i])
        i += 1
    if len(args) != 1:
        print(USAGE)
        return 2
    try:
        terms = _option(argv, "--terms") or []
        used = _option(argv, "--used-colours") or []
        want = _option(argv, "--id")
        if want is not None and (len(want) != 1 or not KEBAB.match(want[0])):
            raise ValueError("--id needs one skill id in kebab-case")
    except ValueError as e:
        print("%s. %s" % (e, USAGE))
        return 2
    for c in used:
        if not HEX.match(c):
            print("--used-colours: %s is not a hex colour like #1fb6ff. %s" % (c, USAGE))
            return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print("cannot read %s: %s" % (args[0], e))
        return 1
    problems = check(data, terms, used, want[0] if want else None)
    for line in problems:
        print(line)
    if problems:
        return 1
    print("OK %s: 7 items, glow %s" % (data["id"], data["colour"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
