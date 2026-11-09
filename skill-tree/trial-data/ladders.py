"""Mastery ladders, one per skill. Starts empty: /learn adds a ladder when a topic needs one.

Usage: python -I -X utf8 skill-tree/trial-data/ladders.py
Writes each ladder into the "ladder" of that skill's trials file, then re-check it with
python -I -X utf8 .claude/skills/learn/scripts/build_pack.py --trials <trials file>

Where the trials file is: skill-tree/trials/<stat>.json (role topics too). A topic folder's own
trials/<stat>.json is updated as well if one exists. The worked example in skill-tree/example/
is never touched.

Rules for every ladder:
- 7 levels: Novice, Beginner, Competent, Proficient, Advanced, Expert, Master.
- Each level says what you can DO (knowledge and skill, not a job title), how it's PROVEN,
  a real-world benchmark, and the level-up quest name. Master means top-level knowledge in the area.
- Levels 1-4: proven by timed Rank Trials on the page. From level 3 up, at least half the problems
  use data or scenarios the learner hasn't practised on (unseen: true).
- Levels 5-7: a Rank Trial is not enough on its own. Each also needs outside evidence (`evidence`):
  public platforms, real certifications, or work reviewed by someone experienced. Claude checks it.
- Ground the benchmarks in real sources (official certification outlines, job ads, interview banks).

Example (shape only):
LADDERS = {
 "sql": [
  L(1, "Novice", "Pull and filter rows from one table: SELECT, WHERE, ORDER BY, LIMIT.",
    TRIAL, "Answers simple lookup questions from one table.", "Become a SQL beginner"),
  ... levels 2-7, with evidence on 5-7 ...
 ],
}
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LEARN = os.path.dirname(HERE)


def L(level, name, can, proof, benchmark, quest, evidence=None):
    x = {"level": level, "name": name, "can": can, "proof": proof, "benchmark": benchmark, "quest": quest}
    if evidence:
        x["evidence"] = evidence
    return x


TRIAL = "Timed Rank Trial on the page: 6 problems, 5 to pass, no hints."
UNSEEN = "Timed Rank Trial on the page, at least half on data you've never practised on: 6 problems, 5 to pass, no hints."

LADDERS = {}


def trial_files(stat):
    main = os.path.join(LEARN, "trials", stat + ".json")
    found = [main] if os.path.exists(main) else []
    for p in sorted(glob.glob(os.path.join(LEARN, "*", "trials", stat + ".json"))):
        if os.path.basename(os.path.dirname(os.path.dirname(p))) != "example":
            found.append(p)
    return found


def main():
    if not LADDERS:
        print("no ladders yet")
        return
    for stat, ladder in LADDERS.items():
        assert [x["level"] for x in ladder] == list(range(1, 8)), stat + ": needs levels 1-7"
        paths = trial_files(stat)
        if not paths:
            print(stat, "no trials file yet, skipped")
            continue
        for path in paths:
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
            spec["ladder"] = ladder
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(spec, ensure_ascii=False, indent=1) + "\n")
            print(stat, "ladder written to", os.path.relpath(path, LEARN))


if __name__ == "__main__":
    main()
