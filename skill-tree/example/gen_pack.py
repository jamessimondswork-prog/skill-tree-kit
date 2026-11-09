"""Build the worked example pack: spreadsheet formulas on a made-up team expenses sheet.

Usage (from the work project folder that holds skill-tree/):
  python -I -X utf8 skill-tree/example/gen_pack.py
  python -I -X utf8 .claude/skills/learn/scripts/build_pack.py skill-tree/example
  python -I -X utf8 .claude/skills/learn/scripts/build_pack.py --trials skill-tree/example/trials/example-formulas.json

REFERENCE ONLY. This pack is never loaded onto the Skill Tree. It shows the learner's Claude what a
finished pack looks like for a skill practised in a desktop tool (Excel or Google Sheets): a data quest
first, `do` steps for things done in the tool, `input` steps where the learner types the value their
formula returns, teach + deeper, quizzes that set a scene, review cards, mixed practice, a boss, a
"use it at work" quest, a guide NPC, trophies, a Field Guide, and the role-topic fields (fromRole,
gapId, placementStart) with Rank Trials for levels 1-3. There is no sandbox and no SQL.

It writes four files, all from a fixed seed, so every answer is the same on every run:
  team-expenses.csv                the sheet the quests use (60 claims, one quarter)
  trip-expenses.csv                a second sheet only the level 3 Rank Trial uses (unseen data)
  pack.json                        the topic + review cards
  trials/example-formulas.json     the 1-7 ladder and Rank Trials for levels 1-3
Every input answer is worked out here from the CSV text itself (parsed back with the csv module),
never typed by hand. Money is added up in whole pence, and rounding is half away from zero, like a
spreadsheet's ROUND. Questions that need "the one with the most" are checked for ties.
"""
import csv
import io
import json
import os
import random
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
TID = os.path.basename(HERE)  # "example": the topic id is the folder name
STAT = "example-formulas"
STAT_NAME = "Spreadsheet formulas (example)"
SEED = 20260106
TOOL = "Excel or Google Sheets"

# ---------------------------------------------------------------- the made-up data

PEOPLE = ["Asha", "Ben", "Chloe", "Dev", "Ella", "Femi"]
# (category, smallest claim in pence, biggest claim in pence, weight)
CATEGORIES = [("Travel", 1500, 18000, 5), ("Meals", 600, 4500, 5), ("Software", 800, 6000, 2),
              ("Office", 300, 4000, 3), ("Training", 5000, 30000, 1)]
MONTHS = [("Jan", 1), ("Feb", 2), ("Mar", 3)]
PER_MONTH = 20
COLUMNS = ["id", "date", "month", "person", "category", "amount", "receipt", "status"]
TYPO, FIXED, N_TYPO = "Softwear", "Software", 3  # quest 1 finds and fixes these

TRIP_COLUMNS = ["id", "trip", "traveller", "type", "cost", "booked_early"]
TRIPS = ["Leeds", "Bristol", "Glasgow"]
TRAVELLERS = ["Gwen", "Hari", "Isla", "Kofi"]
# (type, smallest, biggest cost in pence)
TRIP_TYPES = [("Train", 2500, 16000), ("Hotel", 6000, 15000), ("Taxi", 800, 4500), ("Food", 500, 3500)]


def pounds(p):
    return f"{p // 100}.{p % 100:02d}"


def to_csv(columns, rows):
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(columns)
    w.writerows(rows)
    return buf.getvalue()


def make_team(rng):
    rows = []
    for month, mnum in MONTHS:
        for _ in range(PER_MONTH):
            cat, lo, hi, _ = rng.choices(CATEGORIES, weights=[c[3] for c in CATEGORIES])[0]
            day = rng.randint(1, 28)
            receipt = "Yes" if cat == "Training" else rng.choices(["Yes", "No"], weights=[4, 1])[0]
            status = rng.choices(["Approved", "Pending", "Rejected"], weights=[7, 2, 1])[0]
            rows.append([f"2026-{mnum:02d}-{day:02d}", month, rng.choice(PEOPLE), cat, rng.randint(lo, hi), receipt, status])
    rows.sort(key=lambda r: (r[0], r[2], r[3], r[4]))
    soft = [i for i, r in enumerate(rows) if r[3] == FIXED]
    assert len(soft) >= N_TYPO + 2, "need some correct Software rows left after the typos"
    for i in rng.sample(soft, N_TYPO):
        rows[i][3] = TYPO
    return [[n + 1, r[0], r[1], r[2], r[3], pounds(r[4]), r[5], r[6]] for n, r in enumerate(rows)]


def make_trips(rng):
    rows = []
    for trip in TRIPS:
        for _ in range(11):
            kind, lo, hi = rng.choice(TRIP_TYPES)
            rows.append([trip, rng.choice(TRAVELLERS), kind, rng.randint(lo, hi), rng.choices(["Yes", "No"], weights=[3, 2])[0]])
    return [[n + 1, r[0], r[1], r[2], pounds(r[3]), r[4]] for n, r in enumerate(rows)]


def parse(text):
    """Read a CSV the way a spreadsheet opens it: header row, then one dict per row, money in pence."""
    rows = list(csv.reader(io.StringIO(text, newline="")))
    head = rows[0]
    out = []
    for r in rows[1:]:
        d = dict(zip(head, r))
        for money in ("amount", "cost"):
            if money in d:
                whole, pence = d[money].split(".")
                d[money] = int(whole) * 100 + int(pence)
        out.append(d)
    return out


RNG = random.Random(SEED)
TEAM_CSV = to_csv(COLUMNS, make_team(RNG))
TRIP_CSV = to_csv(TRIP_COLUMNS, make_trips(RNG))
RAW = parse(TEAM_CSV)    # the file as downloaded (with the Softwear typo)
TEAM = [dict(r, category=FIXED if r["category"] == TYPO else r["category"]) for r in RAW]  # after quest 1's fix
TRIP = parse(TRIP_CSV)

# ---------------------------------------------------------------- answers, worked out from the CSV


def money(p):
    """Every way a learner might type a pence amount. The page ignores case, spaces and punctuation,
    so 1,234.50 and £1234.50 match 1234.50 already; 1234.5 needs its own entry."""
    forms = [f"{p / 100:.2f}", f"{p / 100:,.2f}", f"£{p / 100:,.2f}"]
    if p % 10 == 0:
        forms.append(f"{p / 100:.1f}")
    if p % 100 == 0:
        forms.append(str(p // 100))
    return list(dict.fromkeys(forms))


def count(n):
    return [str(n)]


def rnd(x, places):
    """Spreadsheet ROUND (half away from zero) on an exact value. Refuses values sitting on a .5 edge,
    where float rounding in a real spreadsheet could land either way."""
    scaled = Fraction(x) * 10 ** places
    assert scaled.denominator != 2, f"{x} sits on a rounding edge"
    return int(scaled + Fraction(1, 2)) if scaled >= 0 else -int(-scaled + Fraction(1, 2))


def where(rows, **tests):
    return [r for r in rows if all(r[k] == v for k, v in tests.items())]


def total(rows, col="amount"):
    return sum(r[col] for r in rows)


def avg_money(rows, col="amount"):
    """Average of a pence column, rounded to 2 decimal places of pounds, returned in pence."""
    assert rows
    return rnd(Fraction(total(rows, col), len(rows)), 0)


def top(groups):
    """The key with the biggest value. Asserts there's no tie at the top."""
    ranked = sorted(groups.items(), key=lambda kv: -kv[1])
    assert len(ranked) == 1 or ranked[0][1] != ranked[1][1], f"tie at the top: {ranked[:2]}"
    return ranked[0][0]


def percent(part, whole):
    return rnd(Fraction(part * 100, whole), 0)


N = len(TEAM)
assert N == 60
SPELLINGS = len({r["category"] for r in RAW})
assert SPELLINGS == len(CATEGORIES) + 1
FLAG = [r for r in TEAM if r["amount"] > 5000 and r["receipt"] == "No"]  # quest 3's Check rows
assert FLAG, "need some Check rows"
ELLA_OK = total(where(TEAM, person="Ella", status="Approved"))
assert ELLA_OK > 0
TRAINING = where(TEAM, category="Training")
assert len(TRAINING) >= 3
REJECTED_BY = {p: total(where(TEAM, person=p, status="Rejected")) for p in PEOPLE}
assert sum(REJECTED_BY.values()) > 0
TEAM_MONTHS = [r["month"] for r in TEAM]
assert all(TEAM_MONTHS[i] == m for i, m in enumerate([m for m, _ in MONTHS for _ in range(PER_MONTH)])), \
    "rows must stay in month blocks (rows 2-21 Jan, 22-41 Feb, 42-61 Mar) for the level 1 trial"
TRAVEL_MAR = total(where(TEAM, category="Travel", month="Mar"))
assert TRAVEL_MAR > 0

A = {
    "rows": count(N),
    "spellings": count(SPELLINGS) + ["six"],
    "typos": count(N_TYPO) + ["three"],
    "total": money(total(TEAM)),
    "average": money(avg_money(TEAM)),
    "max": money(max(r["amount"] for r in TEAM)),
    "min": money(min(r["amount"] for r in TEAM)),
    "pending_n": count(len(where(TEAM, status="Pending"))),
    "travel": money(total(where(TEAM, category="Travel"))),
    "ella_ok": money(ELLA_OK),
    "flag_n": count(len(FLAG)),
    "meals_feb": count(len(where(TEAM, category="Meals", month="Feb"))),
    "training_avg": money(avg_money(TRAINING)),
    "rejected_top": [top(REJECTED_BY)],
    "no_receipt_pct": count(percent(len(where(TEAM, receipt="No")), N)),
    "travel_mar": money(TRAVEL_MAR),
    "feb_total": money(total(where(TEAM, month="Feb"))),
    "pending_money": money(total(where(TEAM, status="Pending"))),
    "flag_money": money(total(FLAG)),
}
A["no_receipt_pct"].append(A["no_receipt_pct"][0] + "%")

# ---------------------------------------------------------------- step and quiz helpers


def words(text):
    return len((text or "").split())


def do(sid, title, teach, goal, check, deeper=None):
    s = {"id": sid, "kind": "do", "title": title, "teach": teach, "goal": goal, "check": check}
    if deeper:
        s["deeper"] = deeper
    return s


def inp(sid, title, teach, goal, accept, hints, why, deeper=None):
    assert accept and len(hints) == 2, sid
    s = {"id": sid, "kind": "input", "title": title, "teach": teach, "goal": goal, "accept": accept, "hints": hints, "why": why}
    if deeper:
        s["deeper"] = deeper
    return s


def ask(qn, options, answer, why):
    return {"q": qn, "options": options, "answer": answer, "why": why}


def explain(sid, check):
    return do(sid, "Explain it back", "Quick check that the **why** stuck, not just the typing. No formula needed.",
              "Think it through, then pick.", check)


def spread(items):
    """Rotate each right answer into a different slot so positions spread across A-D (checked).
    Write every question with the right answer first, then let this move it."""
    order = [1, 3, 0, 2, 2, 0, 3, 1]
    for i, it in enumerate(items):
        want = order[i % len(order)] % len(it["options"])
        right = it["options"].pop(it["answer"])
        it["options"].insert(want, right)
        it["answer"] = want


# ---------------------------------------------------------------- quest 1: the data

Q1 = {"id": "q1", "title": "Open the expenses sheet", "minutes": 20,
      "source": {"title": "Microsoft Support: Import or export text (.txt or .csv) files",
                 "url": "https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba"},
      "win": "You can open a CSV in your own spreadsheet, size it up and fix a messy column before you trust it.",
      "steps": [
    do("s1", "Where this data comes from",
       "Most teams claim expenses through a form or an app. Once a quarter, someone exports the claims as a **CSV** file: plain text, one claim per line, commas between the values.\n\n"
       "This sheet is **made up** (a script wrote it with a fixed seed). The file is **team-expenses.csv** in the `skill-tree` folder of your work project.\n\n"
       "The **columns**: `id` (claim number), `date`, `month` (Jan, Feb or Mar), `person`, `category` (Travel, Meals, Software, Office, Training), "
       "`amount` (pounds), `receipt` (Yes or No) and `status` (Approved, Pending or Rejected).",
       "Find team-expenses.csv on your computer, read the column list, then answer the check question.",
       ask("A row says person Ben, category Meals, amount 18.40, receipt No, status Pending. His manager asks what this row tells her. Which reading is right?",
           ["Ben claimed 18.40 pounds for a meal, with no receipt, not yet signed off",
            "Ben was paid 18.40 pounds for a meal, and his receipt was turned down",
            "Ben spent 18.40 pounds on meals in total across the whole quarter",
            "Ben's team claimed 18.40 pounds for meals, waiting for a receipt upload"], 0,
           "Each row is one claim by one person. Pending means nobody has approved it yet, so it hasn't been paid. Reading one row as a quarterly total is the most common slip."),
       deeper="**Why it works**\nAlmost every system can export a CSV, and every spreadsheet can open one. That's why so much everyday number work starts here: "
              "export from the system that records things, open it in a spreadsheet, then answer questions with formulas.\n\n"
              "**Worked example**\nA small shop exports its refunds: `id, date, item, amount, reason`. One refund of a 12.50 pound mug is one row. "
              "The shop's total refunds aren't stored anywhere. You work them out with a formula when you need them.\n\n"
              "**Common mistakes**\n- Reading one row as a total. Each row is one claim.\n- Treating `month` as a number. Here it's text: Jan, Feb, Mar.\n"
              "- Trusting a column before looking at it. Exports often have typos, which is exactly what you'll find in step 4."),
    do("s2", "Open it in your spreadsheet",
       "**Excel:** double-click the file, or open Excel and use File, Open. **Google Sheets:** open a blank sheet, then File, Import, Upload, pick the file and choose Replace spreadsheet.\n\n"
       "Then look. Row 1 holds the column names. Every row under it is one claim. Click a few cells in `amount`: numbers sit on the right of the cell, text sits on the left.",
       "Open team-expenses.csv in Excel or Google Sheets and scroll through it once. Then answer the check question.",
       ask("You open the file and every amount sits on the left of its cell, and a quick total shows 0. What's the most likely cause?",
           ["The amounts came in as text, often because the computer uses commas for decimals",
            "The file is too large for the spreadsheet, so it skipped the amount column",
            "The amounts are stored as dates, so they need a date format before adding up",
            "The receipt column is blank for some rows, which stops the amounts from adding"], 0,
           "Left-aligned numbers are usually text. A spreadsheet set up for a comma decimal reads 18.40 as words. Blank cells elsewhere don't stop a total."),
       deeper="**Why it works**\nA spreadsheet guesses each value's type as it opens a CSV. Numbers it recognises line up on the right and can be added. "
              "Values it can't read as numbers stay text, line up on the left and count as zero in a total.\n\n"
              "**Worked example**\nA laptop set to a European region expects 18,40. It opens 18.40 as text. In Excel, Data, From Text/CSV lets you pick the file's format before loading. "
              "In Google Sheets, File, Settings, Locale changes how numbers are read.\n\n"
              "**Common mistakes**\n- Typing over values by hand to fix them. Fix how the file is read instead.\n"
              "- Saving over the original CSV in a different format. Keep the download as it is and save your work as a new file.\n"
              "- Assuming the first screen is the whole file. Press Ctrl+End to jump to the last row."),
    inp("s3", "How big is it?",
        "`COUNTA` counts the cells in a **range** that aren't empty. A range is a block of cells, written as first cell, colon, last cell. "
        "Example on a different sheet: `=COUNTA(B2:B30)` counts the names in B2 to B30. Row 1 holds the header, so start at row 2.",
        "How many claims are in the sheet? Count the filled cells in the `id` column, without the header.",
        A["rows"],
        ["Function: COUNTA, on column A.", "Shape: `=COUNTA(A2:A___)`. Scroll to the last row to find the number."],
        "One row per claim, so the filled id cells are the claims.",
        deeper="**Why it works**\nCOUNTA counts any cell that isn't empty: numbers, text or dates. The id column has a value on every claim row, so counting it counts the claims. "
               "Starting at row 2 leaves the header out.\n\n"
               "**Worked example**\nA sign-up list has names in B2 to B48. `=COUNTA(B2:B48)` gives 47 people. "
               "If you're not sure where the list ends, press Ctrl+Down in the column to jump to the last filled cell and read its row number.\n\n"
               "**Common mistakes**\n- Starting at row 1, so the header counts as a claim.\n"
               "- Using COUNT instead. COUNT only counts numbers, so it would miss a text column.\n"
               "- Counting a column with gaps, like `receipt` if some cells were blank. Pick a column that's filled on every row."),
    inp("s4", "Spot the mess",
        "A **filter** puts a small arrow on each header. Click the arrow on a column and it lists every different value in it, once each. "
        "It's the quickest way to spot typos. **Excel:** Data, Filter. **Google Sheets:** Data, Create a filter.\n\n"
        "Example: a `colour` column might list Red, red and Redd. A spreadsheet treats Redd as a different value, even though a person reads all three as red.",
        "Turn on a filter and open the arrow on `category`. How many different values does it list?",
        A["spellings"],
        ["Data, Filter (Excel) or Data, Create a filter (Google Sheets), then the arrow on category.", "Count the ticked values in the list. Look closely at the spellings."],
        "There are five real categories, plus one misspelling of Software.",
        deeper="**Why it works**\nFormulas match text exactly, letter by letter (they ignore upper and lower case, but not spelling). "
               "If Softwear sits in the column, a formula that adds up Software misses those rows, and the total comes out wrong with no error.\n\n"
               "**Worked example**\nA shop's `channel` column lists Online, Onlin and In store under the filter. A total for Online would miss the Onlin rows. "
               "Spotting it takes ten seconds; missing it can put a wrong number in a report.\n\n"
               "**Common mistakes**\n- Only scanning the first screen of rows. The filter list shows every value in the whole column.\n"
               "- Leaving a filter on and forgetting it. Rows it hides still count in most formulas, but you can't see them.\n"
               "- Fixing the spelling in your head instead of in the data."),
    inp("s5", "Fix it with Find and Replace",
        "**Find and Replace** swaps one piece of text for another across the sheet. Press **Ctrl+H** in either tool. Type what to find, what to put instead, then **Replace all**. "
        "Excel says how many replacements it made. Google Sheets says how many instances it replaced.\n\n"
        "Example: find `Redd`, replace with `Red`, and every Redd in the sheet becomes Red at once.",
        "Replace the misspelled category with the right spelling, Software. How many cells did it change?",
        A["typos"],
        ["Ctrl+H. Find the misspelling you saw in the filter list.", "Find `Soft____`, replace with `Software`, then Replace all. Read the message."],
        "Three claims had the typo. Your sheet now has five clean categories.",
        deeper="**Why it works**\nFixing the data once, at the start, means every formula you write later is right without extra work. "
               "Replace all also tells you how many cells changed, which is a useful check that you fixed what you meant to.\n\n"
               "**Worked example**\nA sign-up sheet has `Londn` in 4 rows. Ctrl+H, find Londn, replace with London, Replace all: \"4 replacements\". "
               "Re-open the filter on the column and Londn has gone.\n\n"
               "**Common mistakes**\n- Replacing a short piece of text that also sits inside other words. Finding `Soft` would change Software too. Find the whole misspelling.\n"
               "- Running it on the wrong sheet or column. Select the column first if you want to limit it.\n"
               "- Not checking afterwards. Open the filter again: you should see five categories."),
    explain("s6", ask("A teammate says: why fix the spelling first, when you could just remember Softwear when you add things up later? What's the strongest answer?",
                      ["Every later formula then works on clean data, so no total quietly misses rows",
                       "Find and Replace makes the file smaller, so formulas run much faster after",
                       "Spreadsheets refuse to add up a column that holds more than one spelling",
                       "The filter arrow stops working until every value in the column matches"], 0,
                      "Fix once and every formula after is right. Spreadsheets don't refuse mixed spellings: they just leave rows out, with no warning.")),
], "quiz": [
    ask("You open a new CSV of sales and want to know how many rows it has, without the header. Which formula fits a sheet with ids in A2 to A120?",
        ["=COUNTA(A2:A120)", "=COUNTA(A1:A120)", "=SUM(A2:A120)", "=COUNTA(A2:H2)"], 0,
        "Start at row 2 to skip the header. SUM would add the id numbers together, which is the tempting mix-up."),
    ask("A filter on the region column lists North, north and Nrth. A formula that adds up North claims will miss which rows?",
        ["The Nrth rows, because the spelling is different", "The north rows, because the case is different", "Both north and Nrth rows, for different reasons", "None of them, since filters fix spelling for you"], 0,
        "Formulas ignore upper and lower case, so north still counts. A different spelling is a different value."),
    ask("Replace all says it made 40 replacements, but you only expected 3 typos in the city column. What most likely went wrong?",
        ["The text you searched for also sits inside other values", "Replace all always counts every cell in the whole sheet", "The filter was on, so hidden rows were counted twice", "Google Sheets counts each letter it changes, not cells"], 0,
        "A short search term matches inside longer words. Search for the whole misspelling, then check with the filter."),
]}

# ---------------------------------------------------------------- quest 2: totals and averages

Q2 = {"id": "q2", "title": "Totals and averages", "minutes": 20,
      "source": {"title": "Microsoft Support: SUM function", "url": "https://support.microsoft.com/en-us/office/sum-function-043e1c7d-7726-4e80-8f32-07b23e057f89"},
      "win": "You can total a column, find its average to the penny, and pick out the biggest and smallest values.",
      "steps": [
    inp("s1", "Add it all up",
        "A **formula** starts with `=` and works something out. `SUM` adds every number in a range. "
        "Example on a different sheet: `=SUM(C2:C13)` adds twelve monthly bills in C2 to C13. Click an empty cell, type the formula, press Enter.",
        "What's the total of every claim in the `amount` column? Type it in pounds and pence.",
        A["total"],
        ["Function: SUM, on the amount column (F).", "Shape: `=SUM(F2:F___)`."],
        "That's the whole quarter's claims, approved or not."),
    inp("s2", "The typical claim",
        "`AVERAGE` adds up a range and divides by how many numbers are in it. Money looks odd with lots of decimals, so wrap it in `ROUND`, which takes the value and how many decimal places to keep.\n\n"
        "Example on a different sheet: `=ROUND(AVERAGE(D2:D9), 1)` gives the average test score to 1 decimal place.",
        "What's the average claim, rounded to 2 decimal places?",
        A["average"],
        ["Functions: AVERAGE inside ROUND.", "Shape: `=ROUND(AVERAGE(F2:F___), _)`."],
        "ROUND keeps it to the penny.",
        deeper="**Why it works**\nThe average gives you one number for a typical claim, which is easier to compare month to month than a long list. "
               "ROUND changes the value itself, not just how it looks, so later formulas use the rounded number.\n\n"
               "**Worked example**\nFive taxi fares: 8.20, 12.50, 9.90, 30.00 and 11.40. `=AVERAGE(...)` gives 14.4. Notice the 30.00 fare pulls the average up: "
               "most fares are nearer 10. That's worth knowing before you call 14.40 typical.\n\n"
               "**Common mistakes**\n- Putting ROUND inside AVERAGE. Round once, on the outside.\n"
               "- Using the decimal buttons on the toolbar and thinking the value changed. They only change how it looks.\n"
               "- Including the header row. Text is skipped by AVERAGE, but a total row at the bottom would be counted."),
    inp("s3", "The biggest claim",
        "`MAX` returns the biggest number in a range. Example on a different sheet: `=MAX(E2:E50)` finds the highest score in E2 to E50.",
        "What's the biggest single claim in the sheet?",
        A["max"],
        ["Function: MAX.", "Shape: `=MAX(F2:F___)`."],
        "Big one-off claims are usually worth a second look."),
    inp("s4", "The smallest claim",
        "`MIN` is the opposite of MAX: the smallest number in a range. It's a quick way to spot a claim that looks too small, like a typo.",
        "What's the smallest single claim in the sheet?",
        A["min"],
        ["Function: MIN.", "Shape: `=MIN(F2:F___)`."],
        "MIN and MAX together show the spread of the claims."),
    explain("s5", ask("Your average claim is far above what most rows look like when you scroll. What's the most likely reason, and what would show it?",
                      ["A few very big claims pull it up, which MAX would show you",
                       "AVERAGE skipped the small claims, which MIN would show you",
                       "ROUND moved the average up, which a wider ROUND would fix",
                       "SUM counted the header row, which COUNTA would show you"], 0,
                      "One or two big values drag an average up. MAX shows how big the biggest is. ROUND only trims decimals.")),
], "quiz": [
    ask("A team lead wants the average training cost to the penny, from costs in D2 to D25. Which formula gives exactly that?",
        ["=ROUND(AVERAGE(D2:D25), 2)", "=AVERAGE(ROUND(D2:D25, 2))", "=ROUND(SUM(D2:D25), 2)", "=AVERAGE(D2:D25, 2)"], 0,
        "Average first, then round the result. ROUND(SUM()) gives a total, not an average."),
    ask("You typed =SUM(F2:F61) and got a number much bigger than every claim added in your head. You notice a total row at F62. Is that the problem?",
        ["No, F62 is outside the range, so it isn't counted", "Yes, SUM always adds every number in the column", "Yes, SUM counts F62 because it follows the range", "No, SUM skips any row that has a formula in it"], 0,
        "A range stops at its last cell. If the total is too big, look for a wrong range, or amounts that were typed twice."),
    ask("A sheet shows 14.4 after you pressed the decrease-decimal button on 14.4375. A later formula uses that cell. Which value does it use?",
        ["14.4375, because the button only changes how it looks", "14.4, because that's what the cell shows on screen", "14.44, because spreadsheets round money automatically", "Nothing, because the cell has been turned into text"], 0,
        "Display buttons don't change the value. Use ROUND when the rounded number must be used later."),
]}

# ---------------------------------------------------------------- quest 3: count and add with conditions

Q3 = {"id": "q3", "title": "Count and add with conditions", "minutes": 30,
      "source": {"title": "Microsoft Support: SUMIFS function", "url": "https://support.microsoft.com/en-us/office/sumifs-function-c9e748f5-7ea7-455d-9406-611cebce642b"},
      "win": "You can count and total only the rows that match one or more tests, and label rows with IF.",
      "steps": [
    inp("s1", "Count the matches",
        "`COUNTIF` counts the cells in a range that match a test, called the **criteria**. Text criteria go in double quotes.\n\n"
        "Example on a different sheet: `=COUNTIF(C2:C40, \"Late\")` counts how many deliveries in C2 to C40 say Late. Case doesn't matter: late and Late both count.",
        "How many claims are still **Pending**?",
        A["pending_n"],
        ["Function: COUNTIF on the status column (H).", "Shape: `=COUNTIF(H2:H___, \"_______\")`."],
        "These are claims nobody has signed off yet.",
        deeper="**Why it works**\nCOUNTIF walks down the range and adds 1 for every cell that passes the test. "
               "The test can be text (\"Late\"), a number (10) or a comparison in quotes (\">10\").\n\n"
               "**Worked example**\nA help desk sheet has a `priority` column. `=COUNTIF(D2:D200, \"High\")` gives the number of high-priority tickets. "
               "`=COUNTIF(E2:E200, \">3\")` counts tickets open for more than 3 days.\n\n"
               "**Common mistakes**\n- Forgetting the quotes around text. Without them the spreadsheet looks for a named range and gives an error or 0.\n"
               "- A stray space in the data. \"Late \" with a space doesn't match \"Late\".\n"
               "- Counting the wrong column. The range is where the test is checked, so it must be the status column."),
    inp("s2", "Add up the matches",
        "`SUMIF` adds the numbers on the rows that pass a test. It takes three things: the range to test, the criteria, and the range to add.\n\n"
        "Example on a different sheet: `=SUMIF(B2:B40, \"Paper\", D2:D40)` adds the costs in column D on every row where column B says Paper.",
        "How much was claimed for **Travel** in total?",
        A["travel"],
        ["Function: SUMIF. Test the category column, add the amount column.", "Shape: `=SUMIF(E2:E___, \"______\", F2:F___)`."],
        "Travel is often the biggest category, so it's the one people ask about first.",
        deeper="**Why it works**\nSUMIF lines the two ranges up row by row. Where the test range passes, it adds the number from the same row in the sum range. "
               "That's why both ranges must start and end on the same rows.\n\n"
               "**Worked example**\nA stock sheet: column B is `supplier`, column E is `cost`. `=SUMIF(B2:B90, \"Northside\", E2:E90)` is everything bought from Northside. "
               "Change the criteria to a cell, like `=SUMIF(B2:B90, H1, E2:E90)`, and you can type any supplier into H1.\n\n"
               "**Common mistakes**\n- Ranges of different sizes, like E2:E61 and F2:F60. The total comes out wrong or errors.\n"
               "- Swapping the order. The test range comes first, the sum range last.\n"
               "- Forgetting the Software typo fix. On the raw file, Software totals would miss three claims."),
    inp("s3", "More than one test",
        "`SUMIFS` adds numbers on rows that pass **every** test you give it. The order is different from SUMIF: the range to add comes **first**, then pairs of test range and criteria.\n\n"
        "Example on a different sheet: `=SUMIFS(D2:D40, B2:B40, \"Paper\", C2:C40, \"Jan\")` adds Paper costs in January only. "
        "`COUNTIFS` works the same way but counts instead of adding.",
        "How much has **Ella** claimed that's **Approved**?",
        A["ella_ok"],
        ["Function: SUMIFS. Sum range first, then person and status tests.", "Shape: `=SUMIFS(F2:F___, D2:D___, \"____\", H2:H___, \"________\")`."],
        "Both tests must pass on the same row.",
        deeper="**Why it works**\nEach extra pair narrows the rows down. A row only counts when it passes every test, so two tests means \"this AND that\". "
               "The same pattern, with COUNTIFS, answers \"how many\" questions with several conditions.\n\n"
               "**Worked example**\nA rota sheet: `hours` in E, `name` in B, `week` in C. `=SUMIFS(E2:E80, B2:B80, \"Sam\", C2:C80, \"Week 3\")` is Sam's hours in week 3. "
               "`=COUNTIFS(B2:B80, \"Sam\", E2:E80, \">8\")` counts Sam's shifts over 8 hours.\n\n"
               "**Common mistakes**\n- Putting the sum range last, out of habit from SUMIF. SUMIFS wants it first.\n"
               "- Expecting OR. SUMIFS is always AND. For \"Ella or Ben\", add two SUMIFS together.\n"
               "- Mixing range sizes between pairs."),
    inp("s4", "Label rows with IF",
        "`IF` checks a test and returns one value when it's true, another when it's false. `AND` is true only when all its tests are true.\n\n"
        "Example on a different sheet: `=IF(AND(C2>10, D2=\"No\"), \"Chase\", \"Fine\")` labels an order Chase when it's over 10 and not paid. "
        "Type it in row 2 of an empty column, then double-click the small square at the cell's corner to fill it down.",
        "Make a new column `flag` that says **Check** when a claim is **over 50 pounds** and has **no receipt**, and **OK** otherwise. How many rows say Check?",
        A["flag_n"],
        ["Functions: IF with AND inside, then COUNTIF on the new column.", "Shape: `=IF(AND(F2>__, G2=\"__\"), \"Check\", \"OK\")`, filled down, then `=COUNTIF(I2:I___, \"Check\")`."],
        "These are the claims a finance team would ask about first.",
        deeper="**Why it works**\nA helper column like `flag` turns a rule into a value on every row. Once it's there, COUNTIF and SUMIFS can use it like any other column. "
               "It's also easy for someone else to read and check.\n\n"
               "**Worked example**\nA course sheet: `score` in C, `attended` in D. `=IF(AND(C2>=60, D2=\"Yes\"), \"Pass\", \"Retake\")` filled down labels everyone. "
               "`=COUNTIF(E2:E40, \"Retake\")` then gives the retake list size.\n\n"
               "**Common mistakes**\n- Writing over 50 as `>=50`. Over means strictly more than.\n"
               "- Forgetting to fill the formula down, so only row 2 has a label.\n"
               "- Typing the labels slightly differently in the IF and the COUNTIF, like Check and Checks."),
    explain("s5", ask("A manager asks for Travel claims in March that are still Pending, added up. Which approach fits best?",
                      ["One SUMIFS with three pairs: category, month and status",
                       "One SUMIF on category, then take away March by hand",
                       "COUNTIFS with the same three tests, then times the average",
                       "SUM on the whole column with a filter for each of the tests"], 0,
                      "SUMIFS takes as many tests as you need, all on the same row. COUNTIFS counts rows, it doesn't add amounts.")),
], "quiz": [
    ask("You want total spend on the Paper supplier from costs in E and suppliers in B. Which formula is written in the right order?",
        ["=SUMIF(B2:B90, \"Paper\", E2:E90)", "=SUMIF(E2:E90, \"Paper\", B2:B90)", "=SUMIFS(B2:B90, \"Paper\", E2:E90)", "=SUMIF(\"Paper\", B2:B90, E2:E90)"], 0,
        "SUMIF tests the first range and adds the last one. SUMIFS puts the sum range first, so the SUMIF order there is wrong."),
    ask("Your COUNTIF for \"Approved\" returns 0, but you can see Approved rows. The cells look normal. What's the most likely cause?",
        ["The cells hold a hidden space, like Approved with a space", "COUNTIF only counts numbers, so text always gives 0", "The rows are upper case, and COUNTIF is case sensitive", "COUNTIF needs the whole column, not a range of rows"], 0,
        "A trailing space makes a different value. COUNTIF ignores case, so that isn't it."),
    ask("A rota needs shifts that are over 8 hours and on a weekend counted. Which function handles both tests in one go?",
        ["COUNTIFS with an hours test and a day test", "COUNTIF with both tests in the same quotes", "SUMIF with the hours test and then the day", "IF with OR around the two tests, then SUM"], 0,
        "COUNTIFS takes several test pairs and counts rows that pass them all. OR would count rows passing either test."),
]}

# ---------------------------------------------------------------- quest 4: mixed practice

Q4 = {"id": "q4", "title": "Mixed practice", "minutes": 25, "mixed": True,
      "source": {"title": "Google Docs Editors Help: Google Sheets function list", "url": "https://support.google.com/docs/table/25273"},
      "win": "You can pick the right formula for a plain-English question with no hints about which one to use.",
      "steps": [
    inp("s1", "Busy month",
        "No labels this time. Read the question, decide which function fits, then write it.",
        "How many **Meals** claims were made in **February**?",
        A["meals_feb"],
        ["Two tests, counted.", "COUNTIFS with category and month."],
        "Two tests at once, counted."),
    inp("s2", "The typical training cost",
        "Some questions need two functions together. Think about what each part of the question asks for.",
        "What's the average **Training** claim, rounded to 2 decimal places?",
        A["training_avg"],
        ["An average is a total divided by a count, both for Training only.", "`=ROUND(SUMIF(...) / COUNTIF(...), 2)`."],
        "Training total divided by the number of Training claims, then rounded."),
    inp("s3", "Who had the most turned down?",
        "When a question asks who has the most, work out the value for each one, then compare.",
        "Whose **Rejected** claims add up to the most money? Type the name.",
        A["rejected_top"],
        ["One total per person, Rejected rows only.", "SUMIFS for each name (amount, person, status), then compare the six results."],
        "Worth a chat about what the expenses policy allows."),
    inp("s4", "Missing receipts",
        "A share is a part divided by the whole. Format the answer as a percentage, or times it by 100.",
        "What percentage of all claims have **no receipt**? Round to a whole number.",
        A["no_receipt_pct"],
        ["Count the No receipts, divide by the count of all claims.", "`=ROUND(COUNTIF(G2:G___, \"No\") / COUNTA(A2:A___) * 100, 0)`."],
        "Part divided by whole, times 100."),
], "quiz": [
    ask("You need the number of claims by Dev in Feb that are over 30 pounds. Which formula fits?",
        ["COUNTIFS with person, month and an amount test", "SUMIFS with person, month and an amount test", "COUNTIF on person, then a filter for the rest", "IF with AND on each row, then SUM the column"], 0,
        "How many means count, and three tests means COUNTIFS. SUMIFS would add the money instead."),
    ask("Your share of missing receipts comes out as 0.18 and your manager expected a percentage. What's the quickest fix?",
        ["Format the cell as a percentage, which shows 18%", "Divide the result by 100 again to make it bigger", "Use SUMIF instead of COUNTIF on the receipt column", "Round it to 0 decimal places, which shows 18 too"], 0,
        "0.18 is 18%: percentage format shows it that way. Rounding 0.18 to 0 places gives 0."),
    ask("To find whose claims add up to the most, a teammate sorts the sheet by amount and reads the top row. What's wrong with that?",
        ["The top row is one big claim, not the biggest total per person", "Sorting changes the amounts, so the totals no longer add up", "Sorting only works on text columns, not on money amounts", "Nothing, the top row is always the person with the most"], 0,
        "One big claim isn't the same as the biggest total. Total per person first, then compare."),
]}

# ---------------------------------------------------------------- quest 5: the boss

Q5 = {"id": "q5", "title": "Boss: the quarter-end summary", "minutes": 60, "boss": True,
      "source": {"title": "Microsoft Support: SUMIFS function", "url": "https://support.microsoft.com/en-us/office/sumifs-function-c9e748f5-7ea7-455d-9406-611cebce642b"},
      "win": "A one-page summary of the quarter that updates itself when the data changes.",
      "steps": [
    do("s1", "Set up the summary tab",
       "The boss fight builds the project: a **Summary** tab that answers the questions a team lead asks every quarter. "
       "Add a new tab. Put the five categories down column A (A2 to A6) and Jan, Feb, Mar and Total across row 1 (B1 to E1). "
       "Each cell in the grid will hold one formula that reads the data tab.",
       "Add the Summary tab with the category and month labels. Then answer the check question.",
       ask("You're about to fill the grid. Why type the labels into cells instead of writing \"Travel\" and \"Jan\" inside every formula?",
           ["The formulas can point at the label cells, so one formula fills the whole grid",
            "Spreadsheets can't use text inside a formula unless it sits in a cell first",
            "Labels in cells make the formulas run faster on a very large data tab",
            "The Summary tab can only read the data tab when the labels are in row 1"], 0,
           "With criteria in cells, you write one formula, fill it across and down, and each cell picks up its own labels. Text inside formulas works too, it's just 15 formulas to type."),
       deeper="**Why it works**\nA summary grid is the same question asked many times: total for this category in this month. "
              "Writing it once and filling it saves time and stops typos, because every cell uses the same logic.\n\n"
              "**Worked example**\nA sales grid has products in A2:A4 and regions in B1:D1. One SUMIFS in B2 points at A2 for the product and B1 for the region. "
              "Fill it across and down and all nine cells are done.\n\n"
              "**Common mistakes**\n- Typing labels with different spelling from the data, like Meal for Meals. The total comes out as 0.\n"
              "- Putting the summary on the data tab, where a sort or filter can move it.\n"
              "- Leaving no Total column, so nobody can check the grid against the grand total."),
    inp("s2", "Fill the grid",
        "In B2, write one SUMIFS that adds the amounts where the category matches the label in column A **and** the month matches the label in row 1. "
        "Refer to the data tab by its name, like `'team-expenses'!F2:F61`. Add `$` signs so the ranges and label positions stay put as you fill: `$A2` keeps column A, `B$1` keeps row 1.",
        "Fill the grid. What's the total for **Travel** in **March**?",
        A["travel_mar"],
        ["SUMIFS with two tests: category against $A2, month against B$1.", "Shape: `=SUMIFS(data!$F$2:$F$61, data!$E$2:$E$61, $A2, data!$C$2:$C$61, B$1)`, with your tab's name for data."],
        "One formula, filled across and down.",
        deeper="**Why it works**\nWhen you fill a formula, cell references move with it. A `$` in front of a column letter or row number stops that part moving. "
               "`$A2` always reads column A but moves down rows. `B$1` always reads row 1 but moves across columns. The data ranges get `$` on both, so they never move.\n\n"
               "**Worked example**\nA price grid: sizes in A2:A4, colours in B1:D1. `=SUMIFS(Stock!$E$2:$E$90, Stock!$B$2:$B$90, $A2, Stock!$C$2:$C$90, B$1)` filled to D4 gives every size and colour.\n\n"
               "**Common mistakes**\n- No `$` on the data ranges, so they slide down as you fill and miss rows.\n"
               "- `$` in the wrong place, so every cell reads the same label.\n"
               "- A tab name with a space or hyphen not wrapped in single quotes."),
    inp("s3", "Month totals",
        "Add a **Total** row under the grid (row 7) with a SUM for each month. Then check it: the Total row plus the Total column should both add up to the grand total from quest 2.",
        "What's the total for **Feb**, all categories together?",
        A["feb_total"],
        ["SUM down the Feb column of your grid.", "Shape: `=SUM(C2:C6)` on the Summary tab."],
        "If the grand totals match quest 2, your grid is right."),
    inp("s4", "Money waiting on approval",
        "A team lead always asks how much is still waiting. Add a line under the grid labelled **Pending** with one formula.",
        "How much money is in **Pending** claims?",
        A["pending_money"],
        ["SUMIF on the status column.", "Shape: `=SUMIF(data!H2:H61, \"Pending\", data!F2:F61)`."],
        "Money not yet signed off."),
    inp("s5", "Money to check",
        "Add one more line: the money in the claims your `flag` column marks Check. The flag column is on the data tab, so point at it there.",
        "How much money is in rows flagged **Check**?",
        A["flag_money"],
        ["SUMIF on the flag column, adding the amounts.", "Shape: `=SUMIF(data!I2:I61, \"Check\", data!F2:F61)`."],
        "Your summary now flags the risk as well as the totals."),
    do("s6", "Explain your summary",
       "Read your Summary tab as if you were the team lead seeing it for the first time. Add a text box or a cell with **two findings**, in plain words: what stands out, and what to do about it.",
       "Write two findings on the Summary tab. Then answer the check question.",
       ask("Which finding would help a team lead most when they read your summary?",
           ["Travel was highest in March and three claims still need receipts, so chase those first",
            "The summary uses SUMIFS with dollar signs so it fills across the whole grid at once",
            "The data tab has 60 rows and 8 columns of made-up team expenses for the quarter",
            "Spreadsheets can add up money by category and month using a summary grid of formulas"], 0,
           "A finding says what the numbers mean and what to do. Describing the formulas or the data is the work, not the insight.")),
], "quiz": [
    ask("You fill a SUMIFS from B2 across to D2 and every cell shows the same total as B2. Which fix is most likely needed?",
        ["Change the month criteria to B$1 so it moves across", "Change the month criteria to $B$1 so it stays put", "Remove the $ from the data ranges so they move too", "Add a fourth test pair for the month column again"], 0,
        "The month label has to move across: B$1 locks only the row. $B$1 locks both, which is what's causing the same answer."),
    ask("Your grid's grand total is 40 pounds lower than the SUM from quest 2. What should you check first?",
        ["A category label in column A that doesn't match the data", "Whether ROUND was used on the quest 2 total as well", "Whether the Summary tab is to the left of the data tab", "The number of decimal places shown on the grid cells"], 0,
        "A label that doesn't match makes a row of zeros, so money goes missing. Tab order and display formats don't change values."),
    ask("Next quarter, the new export has 75 rows instead of 60. Your formulas use rows 2 to 61. What happens to the summary?",
        ["The last 15 claims are left out, so totals come out too low", "The formulas grow by themselves to cover the new rows", "Every formula shows an error until the ranges are fixed", "The summary double counts the first 15 rows of claims"], 0,
        "Fixed ranges stop where you told them. Use whole columns (F:F) or a range with room to spare in a reusable template."),
]}

# ---------------------------------------------------------------- quest 6: use it at work

Q6 = {"id": "q6", "title": "Use it at work", "minutes": 30, "ship": True,
      "source": {"title": "Microsoft Support: IF function", "url": "https://support.microsoft.com/en-us/office/if-function-69aed7c9-4e8a-4755-a9bc-aa8bbff73be2"},
      "win": "A reusable template with notes, and one real task at work done with formulas instead of by hand.",
      "steps": [
    do("s1", "Turn it into a template",
       "A **template** is a copy of your workbook with the formulas kept and the data cleared, ready for next quarter. "
       "Save a copy with a new name. On the data tab, delete the claim rows but keep the header row. Change the summary ranges to whole columns, like `F:F`, so they pick up any number of rows.",
       "Save a template copy with no data and whole-column ranges. Then answer the check question.",
       ask("You paste next quarter's claims into the template's empty data tab. What should the Summary tab do?",
           ["Fill itself in, because the formulas read whole columns",
            "Show errors until you type each SUMIFS in again by hand",
            "Keep last quarter's totals until you press a refresh button",
            "Copy the old data back in, since templates keep a backup"], 0,
           "Formulas recalculate as soon as the data changes. Whole-column ranges mean new rows are included."),
       deeper="**Why it works**\nThe work in a report is the logic, not the numbers. Once the logic lives in formulas, next quarter's report is a paste and a quick check. "
              "Whole-column ranges like `F:F` include any row you add, and SUMIFS ignores the header text.\n\n"
              "**Worked example**\nA monthly timesheet template has a Summary tab with SUMIFS by person. Each month someone pastes the new export into the data tab and the summary is done in a minute.\n\n"
              "**Common mistakes**\n- Clearing the header row with the data, so the column names are gone.\n"
              "- Saving over the original instead of a copy.\n"
              "- Leaving a total row inside a whole-column range, which then gets counted twice."),
    do("s2", "Write the notes",
       "Add a **Notes** tab. One line per formula: what it answers, in plain words. Then one line on where the data comes from and how to paste it in. "
       "Notes are what make a template usable by someone else, or by you in three months.",
       "Write the Notes tab. Then answer the check question.",
       ask("A new teammate opens your template next quarter. Which note helps them most?",
           ["Paste the expenses export into the data tab, row 2 down, and check the grand total",
            "This workbook was built with SUMIFS, COUNTIF and IF formulas over several weeks",
            "The Summary tab is the second tab and has a grid of numbers with labels on it",
            "Formulas are a way to work out values from other cells in a spreadsheet file"], 0,
           "Good notes say what to do and how to check it. A list of functions or tabs doesn't help someone run it."),
       deeper="**Why it works**\nA workbook without notes only works for the person who built it. One plain line per formula lets anyone check it, fix it or reuse it. "
              "It also makes you spell out what each number means, which often shows up a mistake.\n\n"
              "**Worked example**\nNotes tab, line 1: \"Data: paste the expenses export into the data tab from row 2. Check: the grid's grand total matches the SUM of the amount column.\" "
              "Line 2: \"Pending: money in claims nobody has approved yet.\"\n\n"
              "**Common mistakes**\n- Writing the formula out again instead of saying what it answers.\n"
              "- Notes that only make sense to you, like \"see my email\".\n"
              "- Forgetting the check step, so nobody knows how to tell the summary is right."),
    do("s3", "Use it on your own work",
       "Pick one task at work you do by hand in a spreadsheet: adding things up by type, counting by status, or checking rows against a rule. "
       "Do it this time with COUNTIFS, SUMIFS or an IF flag. Keep your work files on your computer: never type their numbers, names or details into this page.",
       "Do one real task at work with formulas instead of by hand. Then answer the check question.",
       ask("You've rebuilt a weekly tally with COUNTIFS. Before you trust it, what's the best check?",
           ["Compare its result with last week's hand count for the same data",
            "Paste the work data into this page so the checker can mark it",
            "Delete the hand-made version so nobody mixes up the two of them",
            "Ask a colleague to type the COUNTIFS again from memory as well"], 0,
           "Check a new formula against a result you already trust. Work data stays on your computer, never on this page."),
       deeper="**Why it works**\nA skill sticks when you use it on something real. The same few formulas cover a lot of hand work: COUNTIFS for tallies by status, "
              "SUMIFS for totals by type and month, and an IF flag for rows that break a rule.\n\n"
              "**Worked example**\nSomeone ticks off a weekly list of requests by hand and counts the open ones. One COUNTIFS on the status and week columns does it, "
              "and next week it's already there. They check it once against their hand count, then stop counting by hand.\n\n"
              "**Common mistakes**\n- Picking a huge task first. Start with one tally or one total.\n"
              "- Not checking the formula against a result you trust.\n"
              "- Pasting work numbers, names or details into this page or into Ask Claude. They stay in your own files."),
    do("s4", "Share it safely",
       "Share the **template**, not the data. A template with notes and no real claims is safe to pass round your team. "
       "If you save it to a shared drive, name it clearly, like `expenses-summary-template`.",
       "Share or save your template where your team can use it. Then answer the check question.",
       ask("A colleague asks for your expenses summary so they can do the same for their team. What should you send?",
           ["The template with notes and the data tab empty",
            "The full workbook with this quarter's claims in it",
            "A screenshot of your Summary tab with the totals",
            "The formulas typed out in a chat message for them"], 0,
           "The template is what they need. Real claims hold other people's details, so they stay with you.")),
], "quiz": [
    ask("You switch a template's ranges from F2:F61 to F:F. Next quarter there are 90 claims. What does the summary now include?",
        ["All 90 claims, because the whole column is read", "Only the first 60 claims, as the template was set", "None of them, since F:F only reads the header", "The 90 claims twice, as F:F reads every tab"], 0,
        "A whole-column range reads every row in that column on that tab. SUMIFS skips the header text."),
    ask("Which of these is safe to share with another team as an example of your work?",
        ["A template with formulas and made-up sample rows", "The live workbook with real names and amounts in it", "A copy of the real data with the names deleted only", "Screenshots of real claims with the amounts showing"], 0,
        "Made-up rows show how it works without anyone's real details. Deleting names alone can still leave private details."),
    ask("Three months on, you open your template and can't remember what the Pending line does. What would have prevented this?",
        ["A Notes tab with one line per formula in plain words", "Longer formulas with more brackets around each part", "Colouring the Pending cell red so it stands out more", "Moving the Pending line to the top of the summary tab"], 0,
        "Notes explain the why. Colours and positions don't say what a formula answers."),
]}

QUESTS = [Q1, Q2, Q3, Q4, Q5, Q6]

# ---------------------------------------------------------------- the rest of the topic

GUIDE = {"npc": "mentor",
         "offer": {"title": "The Expenses Ledger",
                   "pitch": "Most spreadsheets get added up by hand, one row at a time. Let's change that. "
                            "We'll take one made-up quarter of team expenses and, by the end, you'll build a summary that fills itself in, then use the same formulas on a task of your own.",
                   "reward": ["New skill: spreadsheet formulas, with Rank Trials up to Competent (3/7)",
                              "Project: a quarter-end expenses summary that updates itself",
                              "A reusable template with notes for your team"],
                   "effort": "6 quests, about 3 hours", "ceiling": "Competent (3/7)",
                   "note": "Done in your own Excel or Google Sheets. The page checks the values your formulas return."},
         "lines": {"accept": "Good. Quest 1 is short: we open the sheet and look before we add anything up.",
                   "hello": "Here's the quarter's expenses. Let's see what's in them.",
                   "back": ["Welcome back. Your sheet's where you left it.", "Good to see you. One quest at a time.", "Back again. That's how this sticks."],
                   "step": ["Say the question in plain words first. Then the formula.", "Check your range starts at row 2.", "Small formula first. Build it up."],
                   "pass": ["That's it. Exactly the number.", "Clean. On to the next.", "Right first time. Nice work."],
                   "fail": ["Close. Check your range covers every row.", "Not yet. Check the spelling inside your quotes.", "Look at the order of the parts in your formula."],
                   "quiz": "Three questions. Two to pass. Think about the situation, not the function name.",
                   "boss": "Boss fight. The team lead wants the quarter-end summary. Everything you've learned, all at once.",
                   "done": "Summary built and template shared. You turned a raw export into something your team can reuse.",
                   "combo": ["Three in a row, first time.", "You're on a roll. Keep it steady.", "Every one first time. Impressive."]}}

MISSION = {"why": "Answer everyday questions from a spreadsheet with formulas, instead of adding things up by hand.",
           "success": ["Open a CSV in your own spreadsheet and fix messy values before using it",
                       "Write SUM, AVERAGE, COUNTIF, SUMIFS and IF from a blank cell to answer a plain-English question",
                       "Build a summary grid that fills itself in when the data changes",
                       "Pass the Competent (3/7) Rank Trial"],
           "constraints": "Sessions of 20-30 minutes in Excel or Google Sheets. Made-up data only.",
           "outOfScope": "Lookups, pivot tables and charts come in a later topic."}

TROPHIES = [
    {"id": "ex-clean-sweep", "ch": 1, "name": "The Clean Sweep", "art": "rake", "need": "Clear \"Open the expenses sheet\".",
     "lore": "You read the export before anyone asked. The typo didn't stand a chance.", "when": {"quest": "q1"}},
    {"id": "ex-counting-stones", "ch": 2, "name": "The Counting Stones", "art": "stones", "need": "Clear \"Totals and averages\".",
     "lore": "Sixty claims, and you knew the whole quarter in four formulas.", "when": {"quest": "q2"}},
    {"id": "ex-sharp-eye", "ch": 2, "name": "Lens of Criteria", "art": "lens", "need": "Clear \"Count and add with conditions\".",
     "lore": "You only counted what mattered. The rest could wait.", "when": {"quest": "q3"}},
    {"id": "ex-no-labels", "ch": 2, "name": "Hourglass of Habit", "art": "hourglass", "need": "Clear \"Mixed practice\".",
     "lore": "No hints on the jar. You picked the right formula anyway.", "when": {"quest": "q4"}},
    {"id": "ex-summary", "ch": 3, "name": "The Living Grid", "need": "Beat the boss: the quarter-end summary.",
     "lore": "Paste in the data and the grid fills itself. The team lead noticed.", "when": {"quest": "q5"},
     "sprite": ["kkkkkkkkkkkk", "knnnnnnnnnnk", "kwwkwwwkwwwk", "kkkkkkkkkkkk", "kwwkwwwkwwwk", "kkkkkkkkkkkk",
                "kwwkwwwkgggk", "kkkkkkkkkkkk", "kwwkwwwkgggk", "kkkkkkkkkkkk", "kwwkwwwkGGGk", "kkkkkkkkkkkk"]},
    {"id": "ex-handed-on", "ch": 3, "name": "The Key Handed On", "art": "key", "need": "Use it at work and share the template.",
     "lore": "Next quarter's report takes a minute now, and not only for you.", "when": {"quest": "q6"}},
]

REFERENCE = [
    {"title": "The shape of a formula",
     "body": "```\n=FUNCTION(range, criteria, ...)\n```\nStarts with `=`. Ranges are first cell, colon, last cell (`F2:F61`). Text criteria go in double quotes. Comparisons go in quotes too: `\">50\"`."},
    {"title": "The expenses sheet",
     "body": "One row per claim, one quarter of made-up team expenses.\n\n- **id** claim number\n- **date** YYYY-MM-DD\n- **month** Jan, Feb or Mar\n"
             "- **person** who claimed\n- **category** Travel, Meals, Software, Office, Training (watch for `Softwear`)\n- **amount** pounds\n"
             "- **receipt** Yes or No\n- **status** Approved, Pending or Rejected"},
    {"title": "Which formula when",
     "body": "- How many rows: **COUNTA**\n- One total or average: **SUM / AVERAGE**, with **ROUND** for money\n- Biggest, smallest: **MAX / MIN**\n"
             "- How many match a test: **COUNTIF** (several tests: **COUNTIFS**)\n- Add up the matches: **SUMIF** (several tests: **SUMIFS**, sum range first)\n"
             "- A label per row: **IF**, with **AND** for several tests\n- Messy text: a **filter** to spot, **Find and Replace** to fix"},
]

GLOSSARY = [
    {"term": "cell", "def": "One box in a sheet, named by its column letter and row number, like F2.", "quest": "q1"},
    {"term": "column", "def": "One kind of value running down a sheet, such as amount or status.", "avoid": ["field"], "quest": "q1"},
    {"term": "CSV", "def": "A text file with one row per line and commas between values. The usual export format.", "quest": "q1"},
    {"term": "range", "def": "A block of cells, written first cell, colon, last cell: F2:F61.", "quest": "q1"},
    {"term": "filter", "def": "Arrows on the headers that list each value in a column and hide rows you don't want to see.", "quest": "q1"},
    {"term": "formula", "def": "Anything in a cell that starts with = and works out a value.", "quest": "q2"},
    {"term": "criteria", "def": "The test a COUNTIF, SUMIF or SUMIFS checks each row against, like \"Travel\" or \">50\".", "quest": "q3"},
    {"term": "helper column", "def": "An extra column that works out a value per row, like a Check or OK flag, for other formulas to use.", "quest": "q3"},
    {"term": "template", "def": "A copy of a workbook with the formulas kept and the data cleared, ready to reuse.", "quest": "q6"},
]

COMMUNITIES = [
    {"name": "r/excel", "url": "https://www.reddit.com/r/excel/", "why": "Large and well moderated. Good for 'is there a better formula for this?'"},
    {"name": "Google Docs Editors Community", "url": "https://support.google.com/docs/community", "why": "Google's own help forum for Sheets questions."},
]

CARDS = [
    ("q1", "Why look at a column with a filter before adding it up?", "To spot typos like Softwear, which formulas treat as a different value."),
    ("q1", "How do you count rows without the header?", "`=COUNTA(A2:A___)`: start the range at row 2."),
    ("q1", "Fix one misspelling across the whole sheet?", "Find and Replace (Ctrl+H), then Replace all. Find the whole misspelling."),
    ("q2", "Average to the penny?", "`=ROUND(AVERAGE(range), 2)`. Round once, on the outside."),
    ("q2", "Do the decimal buttons change a value?", "No, only how it looks. ROUND changes the value."),
    ("q3", "SUMIF vs SUMIFS: where does the sum range go?", "SUMIF: last. SUMIFS: first."),
    ("q3", "Text criteria in COUNTIF?", "In double quotes: `\"Pending\"`. Case doesn't matter, spelling and spaces do."),
    ("q3", "IF with two tests that must both be true?", "`=IF(AND(test1, test2), \"yes value\", \"no value\")`."),
    ("q4", "An average for one category only?", "SUMIF divided by COUNTIF for that category, then ROUND."),
    ("q4", "A share as a percentage?", "Part divided by whole. Format as % or times by 100."),
    ("q5", "What does $ do in B$1?", "Locks the row, so filling across moves the column but always reads row 1."),
    ("q5", "Check a summary grid?", "Its grand total should match a plain SUM of the whole amount column."),
    ("q6", "Why whole columns like F:F in a template?", "They include any number of rows, so next quarter's data just works."),
    ("q6", "What do you share with another team?", "The template with notes and no real data."),
]

# ---------------------------------------------------------------- Rank Trials (levels 1-3)


def L(level, name, can, proof, benchmark, quest, evidence=None):
    x = {"level": level, "name": name, "can": can, "proof": proof, "benchmark": benchmark, "quest": quest}
    if evidence:
        x["evidence"] = evidence
    return x


TRIAL = "Timed Rank Trial on the page: 6 problems, 5 to pass, no hints."
UNSEEN = "Timed Rank Trial on the page, at least half on data or scenarios you haven't practised: 6 problems, 5 to pass, no hints."
LADDER = [
    L(1, "Novice", "Open a CSV in a spreadsheet and work out totals, averages, biggest and smallest values and counts on a range: SUM, AVERAGE, MIN, MAX, COUNTA, ROUND.",
      TRIAL, "Can answer simple 'how much in total' questions from a sheet.", "Become a spreadsheet beginner"),
    L(2, "Beginner", "Count and add with conditions (COUNTIF, COUNTIFS, SUMIF, SUMIFS), label rows with IF and AND, and clean messy text before counting it.",
      TRIAL, "Where a typical intro spreadsheet course leaves you.", "Become a spreadsheet beginner"),
    L(3, "Competent", "Combine formulas to summarise a sheet you haven't seen: several conditions at once, averages for a subset, shares as percentages and a summary grid with $ references.",
      UNSEEN, "Builds a reliable summary from a new export without help.", "Summarise any sheet with confidence"),
    L(4, "Proficient", "Lookups (XLOOKUP, or INDEX with MATCH), pivot tables, data validation and tidy multi-tab workbooks, on unfamiliar data.",
      UNSEEN, "The person the team asks to fix a broken workbook.", "Master lookups and pivots"),
    L(5, "Advanced", "Dynamic array formulas (FILTER, UNIQUE, SORT), LET and LAMBDA, and repeatable data cleaning with Power Query or a similar tool.",
      "Rank Trial on hard problems, plus outside evidence.", "Builds workbooks others run every week without breaking.", "Become the team's spreadsheet fixer",
      "A real certification at an expert level for your spreadsheet tool, or a public workbook using dynamic arrays and repeatable cleaning, reviewed by an experienced user."),
    L(6, "Expert", "Designs workbook models others rely on, audits formulas for errors, and keeps large workbooks fast and readable.",
      "Rank Trial plus outside evidence, reviewed by an experienced modeller.", "Trusted to build and review models for a whole department.", "Become the lead workbook designer",
      "A public model on open data with documentation and an error audit, reviewed and signed off by an experienced modeller."),
    L(7, "Master", "Top-level spreadsheet knowledge: calculation engine behaviour, advanced modelling standards, and teaching and reviewing others' workbooks.",
      "Outside evidence of standing, plus peer review. No page trial can prove this level.", "Recognised beyond your own team as a spreadsheet authority.", "Become a spreadsheet master",
      "Public teaching or answers others rely on, plus a written review of your work by a recognised expert."),
]


def P(pid, goal, accept, unseen=False):
    assert accept, pid
    p = {"id": pid, "kind": "input", "goal": goal, "accept": accept}
    if unseen:
        p["unseen"] = True
    return p


def C(pid, qn, options, answer, why):
    return {"id": pid, "kind": "choice", "q": qn, "options": options, "answer": answer, "why": why}


def block(month):
    return where(TEAM, month=month)


TEAM_FILE = {"name": "team-expenses.csv", "path": f"{TID}/team-expenses.csv"}
TRIP_FILE = {"name": "trip-expenses.csv", "path": f"{TID}/trip-expenses.csv"}
ALL_AMOUNTS = [r["amount"] for r in TEAM]
TAXI_BY = {p: total(where(TRIP, traveller=p, type="Taxi"), "cost") for p in TRAVELLERS}
MONTH_TOTALS = {m: total(block(m)) for m, _ in MONTHS}
APPROVED = where(TEAM, status="Approved")
RAW_SOFTWARE = [r for r in RAW if r["category"] in (FIXED, TYPO)]
assert where(RAW, category=FIXED) and len(RAW_SOFTWARE) > len(where(RAW, category=FIXED))
FEMI_PENDING = total(where(TEAM, person="Femi", status="Pending"))
assert FEMI_PENDING > 0, "the level 2 Pending question needs a non-zero answer"
LEEDS_TRAIN_LATE = where(TRIP, trip="Leeds", type="Train", booked_early="No")
assert LEEDS_TRAIN_LATE, "need some late-booked Leeds trains"

TRIALS = [
    {"level": 1, "pick": 6, "passMark": 5, "placementPick": 4, "placementPass": 3, "minutes": 20, "tool": TOOL, "dataFiles": [TEAM_FILE],
     "problems": [
        P("n1", "In `team-expenses.csv` as downloaded, January is rows 2-21. What's the **total** of the January claims?", money(total(block("Jan")))),
        P("n2", "February is rows 22-41. What's the **average** February claim, rounded to 2 decimal places?", money(avg_money(block("Feb")))),
        P("n3", "March is rows 42-61. What's the **biggest** March claim?", money(max(r["amount"] for r in block("Mar")))),
        P("n4", "What's the **smallest** January claim (rows 2-21)?", money(min(r["amount"] for r in block("Jan")))),
        P("n5", "What's the **total** of February and March together (rows 22-61)?", money(total(block("Feb")) + total(block("Mar")))),
        P("n6", "How far apart are the biggest and smallest claims in the whole sheet? Type the difference.", money(max(ALL_AMOUNTS) - min(ALL_AMOUNTS))),
        P("n7", "What's the average **January** claim (rows 2-21), rounded to the **nearest whole pound**?",
          count(rnd(Fraction(total(block("Jan")), 100 * len(block("Jan"))), 0))),
        C("c1", "A sheet has prices in C2 to C40 and a total row at C41. Which formula gives the average price without the total row?",
          ["=AVERAGE(C2:C40)", "=AVERAGE(C1:C41)", "=AVERAGE(C2:C41)", "=SUM(C2:C40)/41"], 0,
          "Stop the range above the total row. Dividing by 41 counts a row that isn't a price."),
        C("c2", "You need the number of rows in a list of names in B2 to B90. Which formula counts them?",
          ["=COUNTA(B2:B90)", "=SUM(B2:B90)", "=MAX(B2:B90)", "=COUNTA(B1:B1)"], 0,
          "COUNTA counts filled cells, including text. SUM and MAX only work on numbers."),
        C("c3", "A report needs money to the penny, and a later formula uses the value. What should you use?",
          ["ROUND(value, 2) in the formula itself", "The decrease-decimal button twice", "Format the cell as currency only", "Type the rounded number over it"], 0,
          "ROUND changes the value. Display formats only change how it looks."),
    ]},
    {"level": 2, "pick": 6, "passMark": 5, "placementPick": 4, "placementPass": 3, "minutes": 20, "tool": TOOL, "dataFiles": [TEAM_FILE],
     "problems": [
        P("g1", "How many claims did **Ben** make?", count(len(where(TEAM, person="Ben")))),
        P("g2", "How much was claimed for **Meals** in total?", money(total(where(TEAM, category="Meals")))),
        P("g3", "How much was claimed for **Software** in total? Careful: this is the file as downloaded.", money(total(RAW_SOFTWARE))),
        P("g4", "How many claims are **over 100 pounds**?", count(len([r for r in TEAM if r["amount"] > 10000]))),
        P("g5", "How much does **Femi** have in **Pending** claims?", money(FEMI_PENDING)),
        P("g6", "How many **Travel** claims have **no receipt**?", count(len(where(TEAM, category="Travel", receipt="No")))),
        P("g7", "Label claims of **200 pounds or more** as Big. How many Big claims are there?", count(len([r for r in TEAM if r["amount"] >= 20000]))),
        C("c1", "A manager wants the total cost on rows where region is North and status is Open. Which formula fits?",
          ["SUMIFS with the cost range first, then two test pairs", "SUMIF with both tests inside one set of quotes", "COUNTIFS with the two tests, then add the cost", "SUM of the cost column with a filter left on"], 0,
          "SUMIFS takes several tests and adds the matching costs. COUNTIFS counts rows, it doesn't add money."),
        C("c2", "Your COUNTIF for \"Closed\" misses some rows that clearly say Closed. What's the likely cause?",
          ["Some cells hold a hidden space or a typo", "COUNTIF only counts upper-case text", "COUNTIF can't count more than 50 rows", "The rows are sorted in the wrong order"], 0,
          "Spaces and typos make different values. COUNTIF ignores case and sort order."),
        C("c3", "You want a column saying Late when days is over 5 and paid is No. Which formula is right for row 2?",
          ["=IF(AND(C2>5, D2=\"No\"), \"Late\", \"OK\")", "=IF(C2>5, D2=\"No\", \"Late\", \"OK\")", "=IF(OR(C2>5, D2=\"No\"), \"Late\", \"OK\")", "=AND(IF(C2>5), D2=\"No\", \"Late\")"], 0,
          "Both tests must be true, so AND goes inside IF. OR would label rows that pass only one test."),
    ]},
    {"level": 3, "pick": 6, "passMark": 5, "placementPick": 4, "placementPass": 3, "minutes": 30, "tool": TOOL, "dataFiles": [TRIP_FILE, TEAM_FILE],
     "problems": [
        P("u1", "`trip-expenses.csv` lists the costs of three team trips. What did the **Glasgow** trip cost in total?",
          money(total(where(TRIP, trip="Glasgow"), "cost")), True),
        P("u2", "In `trip-expenses.csv`, what's the average **Hotel** cost, rounded to 2 decimal places?",
          money(avg_money(where(TRIP, type="Hotel"), "cost")), True),
        P("u3", "In `trip-expenses.csv`, who spent the most on **Taxi** across all trips? Type the name.", [top(TAXI_BY)], True),
        P("u4", "In `trip-expenses.csv`, what percentage of bookings were **booked early**? Round to a whole number.",
          count(percent(len(where(TRIP, booked_early="Yes")), len(TRIP))) + [str(percent(len(where(TRIP, booked_early="Yes")), len(TRIP))) + "%"], True),
        P("u5", "In `trip-expenses.csv`, how much did **Train** tickets for **Leeds** cost when they were **not** booked early?",
          money(total(LEEDS_TRAIN_LATE, "cost")), True),
        P("n6", "Back on `team-expenses.csv` (Software fixed): what's the average **Approved** claim, rounded to 2 decimal places?", money(avg_money(APPROVED))),
        P("n7", "In `team-expenses.csv`, which month had the most money claimed? Type Jan, Feb or Mar.", [top(MONTH_TOTALS)]),
        C("c1", "You fill =SUMIFS(D2:D50, B2:B50, $A2, C2:C50, B$1) down and across a grid, and the totals drift wrong lower down. What's missing?",
          ["$ signs on the data ranges, so they stop moving", "A $ on the A in $A2, which already has one there", "A ROUND around the SUMIFS to tidy the decimals", "An extra test pair for the row labels in column A"], 0,
          "Without $ the data ranges slide down as you fill, and miss rows. Lock them with $D$2:$D$50 and so on."),
        C("c2", "A team lead wants the average order value for the North region only. Which formula works with SUMIF and COUNTIF?",
          ["SUMIF of North orders divided by COUNTIF of North", "SUMIF of North orders divided by COUNTA of all rows", "COUNTIF of North divided by SUMIF of North orders", "SUM of all orders divided by COUNTIF of North rows"], 0,
          "An average for a subset is that subset's total over that subset's count. Dividing by all rows gives a share, not an average."),
        C("c3", "A summary grid's grand total doesn't match the plain SUM of the data. What do you check first?",
          ["Labels in the grid that don't match the data's spelling", "Whether the grid is on a tab to the left of the data", "The number of decimal places shown in each cell", "Whether the data tab has its filter turned on"], 0,
          "A label that doesn't match makes zeros, so money goes missing. Tab order and display don't change values."),
    ]},
]

# ---------------------------------------------------------------- write it all


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


def save_csv(name, text):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main():
    spread([it for qu in QUESTS for it in qu["quiz"] + [s["check"] for s in qu["steps"] if s["kind"] == "do"]])
    for t in TRIALS:
        spread([p for p in t["problems"] if p.get("kind") == "choice"])
    for qu in QUESTS:
        for s in qu["steps"]:
            assert words(s["teach"]) < 40 or s.get("deeper"), f"{qu['id']}/{s['id']} needs deeper"
    topic = {"title": "Spreadsheet formulas on team expenses", "stat": STAT, "statName": STAT_NAME, "area": "job", "category": "spreadsheets",
             "project": "A quarter-end expenses summary in Excel or Google Sheets that fills itself in, turned into a template for the team",
             "sourceUrl": "https://support.google.com/docs/table/25273", "sourceTitle": "Spreadsheet function help (Microsoft Support and Google Docs Editors Help)",
             "sourceLength": "Reference docs; 6 quests, about 3 hours",
             "sources": [{"title": "Microsoft Support: SUM function", "url": "https://support.microsoft.com/en-us/office/sum-function-043e1c7d-7726-4e80-8f32-07b23e057f89", "addedOn": "2026-01-05"},
                         {"title": "Microsoft Support: SUMIFS function", "url": "https://support.microsoft.com/en-us/office/sumifs-function-c9e748f5-7ea7-455d-9406-611cebce642b", "addedOn": "2026-01-05"},
                         {"title": "Google Docs Editors Help: Google Sheets function list", "url": "https://support.google.com/docs/table/25273", "addedOn": "2026-01-05"}],
             "dataSource": "Made-up team expenses for one quarter (Jan-Mar 2026), written by gen_pack.py in this folder with a fixed seed. Not real data. "
                           "The learner opens team-expenses.csv in their own spreadsheet.",
             "status": "offered", "createdOn": None,
             "fromRole": True, "gapId": "spreadsheet-formulas", "placementStart": 1,
             "placement": {"1": ["q1", "q2"], "2": ["q3"], "3": ["q4"]},
             "guide": GUIDE, "mission": MISSION, "trophies": TROPHIES, "reference": REFERENCE, "glossary": GLOSSARY,
             "communities": COMMUNITIES, "quests": QUESTS}
    n, cards = {}, []
    for qid, front, back in CARDS:
        n[qid] = n.get(qid, 0) + 1
        cards.append({"id": f"{TID}-{qid}-{n[qid]}", "quest": qid, "front": front, "back": back})
    save_csv("team-expenses.csv", TEAM_CSV)
    save_csv("trip-expenses.csv", TRIP_CSV)
    dump(os.path.join(HERE, "pack.json"), {"topic": topic, "cards": cards})
    dump(os.path.join(HERE, "trials", f"{STAT}.json"),
         {"stat": STAT, "statName": STAT_NAME, "ladder": LADDER, "trials": TRIALS})
    print(f"team-expenses.csv: {len(TEAM)} rows, trip-expenses.csv: {len(TRIP)} rows. pack.json: {len(QUESTS)} quests, "
          f"{sum(len(x['steps']) for x in QUESTS)} steps, {len(cards)} cards. trials/{STAT}.json: levels {[t['level'] for t in TRIALS]}.")


if __name__ == "__main__":
    main()
