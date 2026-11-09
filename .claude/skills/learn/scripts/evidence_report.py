"""Turn Skill Tree evidence into candidate learning records.

Usage: python -I -X utf8 evidence_report.py <state folder>
The state folder is what ArtifactData list writes with out_dir (skill-tree/state/):
<state>/topics/<id>.json, <state>/stats/<id>.json, <state>/log/<YYYY-MM>.json.
Prints proven skills, struggles and misconceptions. Claude reads this, writes
records to skill-tree/learner/records/ and adapts topics. It never writes files.
"""
import glob
import json
import os
import sys


def docs(folder, collection):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, collection, "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        out.append((os.path.splitext(os.path.basename(path))[0], d.get("data", d) if isinstance(d, dict) else d))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = sys.argv[1]
    proven, struggles, misses = [], [], []
    for tid, t in docs(folder, "topics"):
        titles = {q["id"]: q.get("title", q["id"]) for q in t.get("quests", [])}
        for q in t.get("quests", []):
            steps = {s["id"]: s for s in q.get("steps", [])}
            for sid, ev in (q.get("evidence") or {}).items():
                name = f"{tid}/{q['id']}/{sid} ({steps.get(sid, {}).get('title', sid)})"
                if ev.get("revealed") or ev.get("fails", 0) >= 3:
                    struggles.append(f"{name}: {ev.get('fails', 0)} wrong runs, {ev.get('hints', 0)} hints{', answer shown' if ev.get('revealed') else ''}")
            clean = [ev for ev in (q.get("evidence") or {}).values() if not ev.get("revealed") and ev.get("fails", 0) == 0 and ev.get("hints", 0) == 0]
            if q.get("completedOn") and not q.get("placed") and steps and len(clean) == len(steps) and (q.get("quizBest") or 0) == len(q.get("quiz", [])):
                proven.append(f"{tid}/{q['id']} ({titles[q['id']]}): every step first time, no hints, flawless quiz")
    for sid, st in docs(folder, "stats"):
        if st.get("mastery"):
            lad = (st.get("ladder") or [{}] * 7)[st["mastery"] - 1]
            proven.append(f"{st.get('name', sid)}: proven {lad.get('name', '')} ({st['mastery']}/7) on {st.get('masteryOn', '?')}")
    for cid, c in docs(folder, "cards"):
        if c.get("lapses", 0) >= 2:
            struggles.append(f"card {cid} ({c.get('topic')}/{c.get('quest')}): forgotten {c['lapses']} times: {c.get('front', '')}")
    for _, lg in docs(folder, "log"):
        for e in lg.get("entries", []):
            if e.get("type") in ("quizmiss", "trialresult") and ("missed" in e.get("note", "")):
                misses.append(f"{e.get('on')} {e.get('type')}: {e.get('note')}")
    print("PROVEN (record if not already):")
    print("\n".join(f" - {x}" for x in proven) or " - none yet")
    print("STRUGGLES (record as misconception, add remedial cards or a short quest):")
    print("\n".join(f" - {x}" for x in struggles) or " - none")
    print("MISSES (look for patterns across 2+ entries before recording):")
    print("\n".join(f" - {x}" for x in misses[-15:]) or " - none")


if __name__ == "__main__":
    main()
