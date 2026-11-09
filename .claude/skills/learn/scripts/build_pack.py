"""Check a /learn topic pack and write the files that load it onto the Skill Tree.

Usage: python -I -X utf8 build_pack.py <topic folder>
Reads <folder>/pack.json: {"topic": {...}, "cards": [...]} (shape in references/playbook.md).
Exits 1 with a list of problems. On success writes, in the same folder:
  topic.json   the topics/<id> document
  writes.json  an ArtifactData batch: newStats (each with its ladder when a trials file exists) + topic + cards
"""
import csv
import json
import math
import os
import re
import sqlite3
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LEARN = os.path.join(ROOT, "skill-tree")
PALETTE = set(".kgGsSwrRbBoycpun")
problems, notes = [], []


def bad(where, msg):
    problems.append(f"{where}: {msg}")


def words(text):
    return len(re.sub(r"```[\s\S]*?```", "", text or "").split())


def load_dataset(sb):
    path = os.path.join(LEARN, sb["dataset"])
    if not os.path.exists(path):
        bad("sandbox", f"dataset {sb['dataset']} not found under skill-tree/")
        return None
    return json.load(open(path, encoding="utf-8"))


def fresh_db(data, sb, raw):
    con = sqlite3.connect(":memory:")
    cols = ", ".join("id INTEGER PRIMARY KEY" if c == "id" else c for c in data["columns"])
    con.execute(f"CREATE TABLE {data['table']} ({cols})")
    con.executemany(f"INSERT INTO {data['table']} VALUES ({','.join('?' * len(data['columns']))})", data["rows"])
    if sb.get("setup"):
        con.executescript(sb["setup"])
    if raw:
        con.execute("CREATE TABLE raw_results (" + ", ".join('"' + c.replace('"', '""') + '"' for c in raw[0]) + ")")
        con.executemany(f"INSERT INTO raw_results VALUES ({','.join('?' * len(raw[0]))})", raw[1:])
    return con


def run(con, sql):
    cols, rows = [], []
    for stmt in [x for x in sql.split(";") if x.strip()]:
        cur = con.execute(stmt)
        if cur.description:
            cols, rows = [d[0] for d in cur.description], cur.fetchall()
    return cols, rows


def check_sprite(where, rows):
    if not isinstance(rows, list) or len(rows) != 12 or any(len(r) != 12 for r in rows):
        bad(where, "sprite must be 12 rows of 12 characters")
    elif set("".join(rows)) - PALETTE:
        bad(where, f"sprite uses unknown colours {sorted(set(''.join(rows)) - PALETTE)}")


BUILTIN_NPCS = {"mentor", "professor"}
GUIDE_LINES = ("accept", "hello", "back", "step", "pass", "fail", "quiz", "boss", "done", "combo")


def check_guide(t):
    """Every topic has a guide NPC: offers it on the Quest Board (status offered) and talks the learner through it."""
    g = t.get("guide")
    if t.get("status") not in ("offered", "active"):
        bad("topic", "status must be offered (new topic, waits on the Quest Board) or active (already accepted)")
    if not g:
        bad("guide", "missing: every topic needs a guide NPC (built-in npc or its own 14x20 sprite)")
        return
    if g.get("npc"):
        if g["npc"] not in BUILTIN_NPCS:
            bad("guide", f"npc must be one of {sorted(BUILTIN_NPCS)}, or give name/role/col/rows instead")
    else:
        for f in ("name", "role", "col", "rows"):
            if not g.get(f):
                bad("guide", f"missing {f}")
        rows, col = g.get("rows") or [], g.get("col") or {}
        if len(rows) != 20 or any(len(r) != 14 for r in rows):
            bad("guide", "sprite must be 20 rows of 14 characters")
        unknown = set("".join(rows)) - set(col) - {"."}
        if unknown:
            bad("guide", f"sprite uses colours not in col: {sorted(unknown)}")
    lines = g.get("lines", {})
    for k in GUIDE_LINES:
        if not lines.get(k):
            bad("guide", f"lines.{k} missing")
    for k in ("back", "step", "pass", "fail", "combo"):
        if isinstance(lines.get(k), list) and len(lines[k]) < 3:
            bad("guide", f"lines.{k}: give at least 3 so it doesn't repeat")
    for k, v in lines.items():
        for line in v if isinstance(v, list) else [v]:
            if words(line) > 30:
                bad("guide", f"lines.{k} too long ({words(line)} words, max 30): {line[:40]}")
    if t.get("status") == "offered":
        o = g.get("offer") or {}
        for f in ("title", "pitch", "reward", "effort"):
            if not o.get(f):
                bad("guide.offer", f"missing {f} (offered topics show on the Quest Board)")
        if o.get("pitch") and words(o["pitch"]) > 70:
            bad("guide.offer", f"pitch is {words(o['pitch'])} words: keep it under 70")


def trials_spec(stat, folder):
    """The stat's trials file: <topic folder>/trials/<stat>.json first, then skill-tree/trials/<stat>.json. None if neither."""
    for base in (os.path.join(folder, "trials"), os.path.join(LEARN, "trials")):
        path = os.path.join(base, f"{stat}.json")
        if os.path.exists(path):
            try:
                spec = json.load(open(path, encoding="utf-8"))
                return spec if isinstance(spec, dict) else {}
            except ValueError:
                return {}
    return None


def role_trial_levels(t, folder):
    """Levels in the stat's trials file (see trials_spec)."""
    spec = trials_spec(t.get("stat"), folder) or {}
    trials = spec.get("trials", [])
    return [x.get("level") for x in trials if isinstance(x, dict)] if isinstance(trials, list) else []


def check_role_topic(t, folder):
    """Topics built from a role gap: gapId, a placement start level and trials for levels 1 to max(3, placementStart)."""
    if not isinstance(t.get("gapId"), str) or not t.get("gapId"):
        bad("topic", "role topics need gapId (the role gap it was built from)")
    ps = t.get("placementStart")
    if isinstance(ps, bool) or not isinstance(ps, int) or not 1 <= ps <= 4:
        bad("topic", "role topics need placementStart: a whole number from 1 to 4")
    top = max(3, ps) if isinstance(ps, int) and not isinstance(ps, bool) and 1 <= ps <= 4 else 3
    levels = role_trial_levels(t, folder)
    if not set(range(1, top + 1)) <= set(levels):
        bad("topic", f"role topics need trials for levels 1-{top} (1-3, or up to placementStart when it's 4) "
                     f"(<topic folder>/trials/{t.get('stat')}.json or skill-tree/trials/{t.get('stat')}.json)")


def check_balance(where, items):
    """Quizzes must not be guessable: right answer not usually the longest, positions spread out."""
    items = [it for it in items if len(it.get("options", [])) >= 3 and 0 <= it.get("answer", -1) < len(it["options"])]
    if len(items) < 6:
        return
    longest = 0
    for it in items:
        lens = [len(o) for o in it["options"]]
        right = lens[it["answer"]]
        others = [x for i, x in enumerate(lens) if i != it["answer"]]
        if right > max(others) * 1.15:
            longest += 1
    if longest / len(items) > 1 / 3:
        bad(where, f"right answer is clearly the longest option in {longest} of {len(items)} questions (max a third). Even out option lengths.")
    pos = {}
    for it in items:
        pos[it["answer"]] = pos.get(it["answer"], 0) + 1
    top = max(pos.values())
    if top / len(items) > 0.4:
        bad(where, f"right answer sits in slot {'ABCD'[max(pos, key=pos.get)]} for {top} of {len(items)} questions (max 40%). Vary positions.")
    # Harder questions: a real situation to apply, and every wrong option a believable mistake.
    short = [it for it in items if len(it.get("q", "").split()) < 12]
    if len(short) * 3 > len(items):
        bad(where, f"{len(short)} of {len(items)} questions are under 12 words. Most should set a scene "
                   "(a situation to apply the idea to), not ask for a definition.")
    for it in items:
        lens = [len(o) for o in it["options"]]
        if min(lens) < max(lens) * 0.35:
            bad(where, f"options very uneven, so the odd one out gives it away: {it.get('q', '')[:50]}")
    for it in items:
        if any(re.search(r"\b(all|none) of the above\b", o, re.I) for o in it["options"]):
            bad(where, f"'all/none of the above' in: {it.get('q', '')[:50]}")


def trials(path):
    """Check a skill's mastery ladder and Rank Trials (skill-tree/trials/<stat>.json)."""
    spec = json.load(open(path, encoding="utf-8"))
    stat = spec.get("stat")
    if len(spec.get("ladder", [])) != 7 or [x.get("level") for x in spec["ladder"]] != list(range(1, 8)):
        bad("ladder", "needs exactly levels 1-7")
    for x in spec.get("ladder", []):
        if not (x.get("name") and x.get("can") and x.get("benchmark")):
            bad(f"ladder {x.get('level')}", "needs name, can, benchmark")
        # Skill audit: say how each level is proven and name its level-up quest.
        # Levels 5-7 can't be proven by a page trial alone: they need outside evidence Claude checks.
        if not (x.get("proof") and x.get("quest")):
            bad(f"ladder {x.get('level')}", "needs proof (how it's proven) and quest (the level-up quest name)")
        if x.get("level", 0) >= 5 and not x.get("evidence"):
            bad(f"ladder {x.get('level')}", "levels 5-7 need evidence: outside proof (public platform, real cert, reviewed work)")
    sb = data = None
    if spec.get("sandbox"):
        sb = json.load(open(os.path.join(LEARN, spec["sandbox"], "pack.json"), encoding="utf-8"))["topic"]["sandbox"]
        data = load_dataset(sb)
    levels = [t.get("level") for t in spec.get("trials", [])]
    if levels != list(range(1, len(levels) + 1)):
        bad("trials", "levels must run 1, 2, 3... with no gaps")
    writes = []
    for t in spec.get("trials", []):
        w = f"trial L{t.get('level')}"
        probs = t.get("problems", [])
        pick, mark = t.get("pick", 0), t.get("passMark", 0)
        # Tough bar: 6+ problems, ~80% to pass, a pool big enough that retries differ.
        if pick < 6:
            bad(w, "pick at least 6 problems so one lucky guess can't carry a trial")
        if not math.ceil(pick * 0.8) <= mark <= pick:
            bad(w, f"passMark must be at least 80% of pick ({math.ceil(pick * 0.8)} of {pick})")
        pp, pm = t.get("placementPick"), t.get("placementPass")
        if not (isinstance(pp, int) and isinstance(pm, int)) or isinstance(pp, bool) or isinstance(pm, bool):
            bad(w, "needs placementPick and placementPass (whole numbers): the placement test used when a role topic starts here")
        else:
            if not 3 <= pp <= pick:
                bad(w, f"placementPick must be between 3 and pick ({pick}), got {pp}")
            if pm < math.ceil(0.75 * pp) or pm > pp:
                bad(w, f"placementPass must be at least 75% of placementPick ({math.ceil(0.75 * pp)} of {pp}) and no more than placementPick")
        # Trial data files are published with the page at the same path, relative to skill-tree/.
        for f in t.get("dataFiles") or []:
            if not (isinstance(f, dict) and f.get("path")):
                bad(w, "dataFiles entries need a path (relative to skill-tree/)")
            elif not os.path.exists(os.path.join(LEARN, f["path"])):
                bad(w, f"dataFiles {f['path']} not found under skill-tree/")
        if len(probs) < pick + 3:
            bad(w, "pool needs at least pick + 3 problems so each attempt differs")
        # Skill audit: from level 3 up, at least half of each attempt is on data or scenarios the learner hasn't practised on.
        if t.get("level", 0) >= 3 and sum(1 for p in probs if p.get("unseen")) < math.ceil(pick / 2):
            bad(w, f"level 3+ needs at least {math.ceil(pick / 2)} unseen: true problems (data or scenarios not used in quests)")
        if t.get("level", 0) >= 5 and not t.get("evidence"):
            bad(w, "level 5+ trials need evidence: what outside proof to send, checked by Claude before mastery is given")
        choice = [p for p in probs if p.get("kind") == "choice"]
        if spec.get("handsOn", True) and len(choice) * 3 > len(probs):
            bad(w, "trials are hands-on: at most a third choice questions (SQL or input problems for the rest), "
                   "or set handsOn: false with handsOnWhy for a skill with no checkable tool work")
        if spec.get("handsOn") is False and not spec.get("handsOnWhy"):
            bad("trials", "handsOn: false needs handsOnWhy")
        for p in probs:
            pw = f"{w}/{p.get('id')}"
            if p.get("kind") == "choice":
                if not (0 <= p.get("answer", -1) < len(p.get("options", []))) or not p.get("q"):
                    bad(pw, "choice needs q, options, answer")
                continue
            if p.get("kind") == "input":
                if not (p.get("goal") and p.get("accept")):
                    bad(pw, "input needs goal and accept (every answer form, e.g. 1140 and 1,140)")
                continue
            if not (p.get("goal") and p.get("answer")):
                bad(pw, "needs goal and answer")
                continue
            if not data:
                bad(pw, "SQL problem but no sandbox")
                continue
            db = fresh_db(data, sb, None)
            try:
                cols, rows = run(db, p["answer"])
                if not rows:
                    bad(pw, "answer returns no rows")
                p["rows"] = len(rows)
            except sqlite3.Error as e:
                bad(pw, f"answer fails: {e}")
            db.close()
        check_balance(w, [p for p in probs if p.get("kind") == "choice"])
        writes.append({"op": "set", "collection": "trials", "doc_id": f"{stat}-L{t['level']}",
                       "data": {"stat": stat, "sandboxTopic": spec.get("sandbox"), **t}})
    if problems:
        print(f"{len(problems)} problems:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    out = os.path.splitext(path)[0] + ".writes.json"
    json.dump({"statUpdate": {"collection": "stats", "doc_id": stat, "data": {"ladder": spec["ladder"]}}, "writes": writes},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK {stat}: ladder 1-7, trials for levels {levels}. Wrote {os.path.basename(out)}.")
    print("Next: a new stat gets its ladder from the topic's newStats set; an existing stat gets a ladder update "
          "(pinned). Then push the trial docs, then the topic and cards.")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--trials":
        return trials(os.path.abspath(sys.argv[2]))
    if len(sys.argv) != 2:
        sys.exit(__doc__ + "\n       python build_pack.py --trials <skill-tree/trials/stat.json>")
    folder = os.path.abspath(sys.argv[1])
    pack = json.load(open(os.path.join(folder, "pack.json"), encoding="utf-8"))
    t, cards = pack["topic"], pack.get("cards", [])
    tid = os.path.basename(folder)
    for f in ("title", "stat", "statName", "project", "sourceUrl", "sourceTitle", "status", "quests"):
        if not t.get(f):
            bad("topic", f"missing {f}")
    sb = t.get("sandbox")
    data = load_dataset(sb) if sb else None
    if sb and not t.get("dataSource"):
        bad("topic", "sandbox topics must say where the data comes from (dataSource)")
    raw = None
    if sb and sb.get("rawSample"):
        # Same rule as dataset: the path is relative to skill-tree/, which is where the page fetches it from.
        raw_path = os.path.join(LEARN, sb["rawSample"])
        if not os.path.exists(raw_path):
            bad("sandbox", f"rawSample {sb['rawSample']} not found under skill-tree/")
        else:
            with open(raw_path, encoding="utf-8-sig", newline="") as f:
                raw = [r for r in csv.reader(f) if any(r)]

    quests = t.get("quests", [])
    if len(quests) < 3:
        bad("topic", "needs at least 3 quests")
    if sb and not any(q.get("keepDb") or any(s.get("upload") for s in q.get("steps", [])) for q in quests[:1]):
        notes.append("first quest doesn't load data: data topics should start by teaching collect/load/clean")
    if not any(q.get("boss") for q in quests):
        bad("topic", "needs a boss quest (boss: true) that builds the project")
    ids = set()
    for qi, q in enumerate(quests):
        w = q.get("id", f"quest {qi}")
        if w in ids:
            bad(w, "duplicate quest id")
        ids.add(w)
        quiz = q.get("quiz", [])
        if len(quiz) != 3:
            bad(w, "quiz needs exactly 3 questions")
        for i, item in enumerate(quiz):
            if not (0 <= item.get("answer", -1) < len(item.get("options", []))) or len(item.get("options", [])) < 3 or not item.get("why"):
                bad(f"{w} quiz {i + 1}", "needs 3+ options, a valid answer index and a why")
        steps = q.get("steps")
        if steps is None:
            if not (q.get("explain") and q.get("task")):
                bad(w, "needs steps, or explain + task")
            continue
        if not 3 <= len(steps) <= 8:
            bad(w, f"{len(steps)} steps: keep quests to 3-8 steps")
        con = fresh_db(data, sb, raw) if (data and q.get("keepDb")) else None
        sids = set()
        for s in steps:
            sw = f"{w}/{s.get('id')}"
            if s.get("id") in sids:
                bad(sw, "duplicate step id")
            sids.add(s.get("id"))
            for f in ("title", "teach", "goal"):
                if not s.get(f):
                    bad(sw, f"missing {f}")
            if words(s.get("teach")) > 170:
                bad(sw, f"teach is {words(s.get('teach'))} words (max 170, beginner-sized)")
            # Go deeper: lessons stay short, with an optional deeper layer from the source.
            if words(s.get("teach")) >= 40:
                dw = words(s.get("deeper"))
                if not dw:
                    bad(sw, "needs deeper: why it works, a worked example, common mistakes (from the source)")
                elif not 80 <= dw <= 350:
                    bad(sw, f"deeper is {dw} words (80-350)")
            kind = s.get("kind", "sql")
            if kind == "do":
                c = s.get("check") or {}
                if not (0 <= c.get("answer", -1) < len(c.get("options", []))) or not c.get("why"):
                    bad(sw, "do-step needs check {q, options, answer, why}")
                continue
            if len(s.get("hints", [])) != 2:
                bad(sw, "needs exactly 2 hints")
            if kind == "input":
                if not s.get("accept"):
                    bad(sw, "input step needs accept: [answers]")
                continue
            if not sb:
                bad(sw, "SQL step in a topic with no sandbox")
                continue
            if not s.get("answer"):
                bad(sw, "SQL step needs an answer (used for Show answer and checking)")
                continue
            db = con or fresh_db(data, sb, raw)
            try:
                cols, rows = run(db, s["answer"])
                if s.get("verify"):
                    if run(db, s["verify"])[1][0][0] != 1:
                        bad(sw, "answer doesn't pass its own verify")
                elif s.get("matchSql"):
                    if run(db, s["matchSql"])[1] != rows:
                        bad(sw, "answer doesn't match its matchSql")
                elif s.get("contains"):
                    if not any(s["contains"] in str(v) for r in rows for v in r):
                        bad(sw, f"answer result doesn't contain {s['contains']}")
                else:
                    if not rows:
                        bad(sw, "answer returns no rows")
                    s["rows"] = len(rows)
            except sqlite3.Error as e:
                bad(sw, f"answer fails: {e}" + ("" if raw or "raw_results" not in s["answer"] else ""))
            if not con:
                db.close()
        if con:
            con.close()
        qc = [c for c in cards if c.get("quest") == q.get("id")]
        if len(qc) < 2:
            bad(w, f"only {len(qc)} review cards (need 2-3 per quest)")

    # Teaching-quality rules adapted from mattpocock/skills `teach` (MIT).
    m = t.get("mission") or {}
    if not m.get("why") or len(m.get("success", [])) < 2:
        bad("topic", "needs mission {why, success: [2+ observable abilities]}")
    for q in quests:
        if not (q.get("source") or {}).get("url"):
            bad(q.get("id"), "needs source {title, url}: one high-trust primary source")
        if not q.get("win"):
            bad(q.get("id"), "needs win: the one tangible thing the learner can do after it")
    if len(quests) >= 5 and not any(q.get("mixed") for q in quests):
        bad("topic", "5+ quests need a mixed practice quest (mixed: true) before the boss")
    check_balance("topic", [it for q in quests for it in q.get("quiz", [])]
                  + [s["check"] for q in quests for s in q.get("steps", []) if s.get("kind") == "do" and s.get("check")])
    for g in t.get("glossary", []):
        if not (g.get("term") and g.get("def")):
            bad(f"glossary {g.get('term')}", "needs term and def")
        if g.get("quest") not in ids:
            bad(f"glossary {g.get('term')}", f"quest {g.get('quest')} doesn't exist (terms unlock with their quest)")
        for alias in g.get("avoid", []):
            used = [f"{q['id']}/{s['id']}" for q in quests for s in q.get("steps", []) if re.search(rf"\b{re.escape(alias)}\b", s.get("teach", ""), re.I)]
            if used:
                notes.append(f"glossary: '{alias}' (avoid, use '{g['term']}') appears in {', '.join(used[:3])}")
    if not t.get("glossary") or not t.get("reference"):
        notes.append("no glossary or reference: the Field Guide will be empty")
    for lv, qids in (t.get("placement") or {}).items():
        for qid in qids:
            if qid not in ids:
                bad(f"placement {lv}", f"quest {qid} doesn't exist")
    if not 1 <= len(t.get("communities", [])) <= 3:
        notes.append("communities: list 1-3 well-run ones (Ask real people)")

    for i, tr in enumerate(t.get("trophies", [])):
        w = f"trophy {tr.get('id', i)}"
        for f in ("id", "name", "need", "lore", "when"):
            if not tr.get(f):
                bad(w, f"missing {f}")
        if tr.get("sprite"):
            check_sprite(w, tr["sprite"])
        elif not tr.get("art"):
            bad(w, "needs sprite (12x12) or art (built-in name)")
        when = tr.get("when", {})
        if "quest" in when and when["quest"] not in ids:
            bad(w, f"when.quest {when['quest']} isn't a quest")
    check_guide(t)
    if t.get("fromRole"):
        check_role_topic(t, folder)
    if len(t.get("trophies", [])) < len(quests):
        notes.append(f"{len(t.get('trophies', []))} trophies for {len(quests)} quests: aim for one per quest")

    for c in cards:
        if not (c.get("id") and c.get("front") and c.get("back") and c.get("quest")):
            bad(f"card {c.get('id')}", "needs id, quest, front, back")

    for n in notes:
        print("note:", n)
    if problems:
        print(f"{len(problems)} problems:")
        for p in problems:
            print(" -", p)
        sys.exit(1)

    topic = {k: v for k, v in t.items() if k != "statName"}
    topic.setdefault("createdOn", None)
    for q in topic["quests"]:
        q.setdefault("quizBest", 0)
        q.setdefault("completedOn", None)
        if "steps" in q:
            q.setdefault("stepsDone", 0)
            q.setdefault("taskDone", False)
        else:
            q.setdefault("taskDone", False)
    json.dump(topic, open(os.path.join(folder, "topic.json"), "w", encoding="utf-8"), ensure_ascii=False)
    stats = {t["stat"]: t["statName"], **{q["stat"]: q.get("statName", q["stat"]) for q in t["quests"] if q.get("stat")}}
    writes = [{"op": "set", "collection": "topics", "doc_id": tid, "file_path": os.path.join(folder, "topic.json")}]
    writes += [{"op": "set", "collection": "cards", "doc_id": c["id"], "data": {
        "topic": tid, "quest": c["quest"], "stat": c.get("stat") or next((q.get("stat") for q in t["quests"] if q["id"] == c["quest"] and q.get("stat")), t["stat"]),
        "front": c["front"], "back": c["back"], "due": None, "gapIdx": 0}} for c in cards]
    new_stats = []
    for k, v in stats.items():
        data = {"name": v, "area": t.get("area", "job"), "xp": 0}
        spec = trials_spec(k, folder)
        # A brand new stat gets its ladder in the same set, so a later ladder update can't be lost or wiped.
        if spec and isinstance(spec.get("ladder"), list) and len(spec["ladder"]) == 7:
            data.update(ladder=spec["ladder"], mastery=0)
        new_stats.append({"op": "set", "collection": "stats", "doc_id": k, "data": data})
    json.dump({"newStats": new_stats,
               "writes": writes}, open(os.path.join(folder, "writes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    size = len(json.dumps(topic).encode())
    if size > 200_000:
        print(f"warning: topic doc is {size} bytes (limit 256 KiB)")
    print(f"OK {tid}: {len(quests)} quests, {sum(len(q.get('steps', [])) for q in quests)} steps, {len(cards)} cards, "
          f"{len(t.get('trophies', []))} trophies, {size // 1024} KB. Stats: {', '.join(stats)}.")
    print("Next, in this order: newStats set (skip ones that exist), ladder update for existing stats, trial docs, "
          "then writes (topic, then cards). Publish new data files first.")


if __name__ == "__main__":
    main()
