"""Check and replay skill-tree/state/pending-writes.json (a prebuilt kit's page writes).

  python -I -X utf8 pending_writes.py check <pending file>        (exit 1 on problems)
  python -I -X utf8 pending_writes.py next <pending file>         (prints the next ArtifactData call as JSON)
  python -I -X utf8 pending_writes.py done <pending file> <count> (drops the first <count> writes once they landed)

The file is {"writes": [{"op": "set" | "update", "collection": "...", "doc_id": "...", "data": {...}}]}, in the
write order: stats sets, stats ladder updates, trials, topics, cards, offers, requests.

`next` never asks you to paste a big document. A single write's data goes to a learner-local file,
skill-tree/state/load-<collection>-<doc_id>.json, and the call uses file_path. A run of card writes goes
as one batch (cards are small). `done` removes the writes the call covered, deletes the load files, and
deletes the pending file once it's empty, so an interrupted load resumes without duplicates.
"""
import glob
import json
import os
import re
import sys

USAGE = "usage: pending_writes.py check <file> | next <file> | done <file> <count>"
OPS = ("set", "update")
ORDER = {("stats", "set"): 0, ("stats", "update"): 1, "trials": 2, "topics": 3, "cards": 4, "offers": 5, "requests": 6}
SAFE = re.compile(r"[^A-Za-z0-9_-]+")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")


def rank(w):
    c = w.get("collection")
    return ORDER.get((c, w.get("op")), ORDER.get(c))


def check(doc):
    p = []
    writes = doc.get("writes") if isinstance(doc, dict) else None
    if not isinstance(writes, list):
        return ["file must be {\"writes\": [...]}"]
    last = -1
    for n, w in enumerate(writes):
        tag = "write %d" % (n + 1)
        if not isinstance(w, dict):
            p.append("%s: not an object" % tag)
            continue
        tag += " (%s/%s)" % (w.get("collection"), w.get("doc_id"))
        if w.get("op") not in OPS:
            p.append("%s: op must be set or update" % tag)
        if not (isinstance(w.get("doc_id"), str) and w["doc_id"]):
            p.append("%s: doc_id required" % tag)
        if "file_path" in w:
            p.append("%s: no file_path (paths from the builder's machine don't exist here); put the data inline" % tag)
        if not isinstance(w.get("data"), dict) or not w["data"]:
            p.append("%s: data must be a non-empty object" % tag)
        r = rank(w)
        if r is None:
            p.append("%s: unknown collection (stats, trials, topics, cards, offers, requests)" % tag)
        elif r < last:
            p.append("%s: out of order (stats sets, ladder updates, trials, topic, cards, offers, requests)" % tag)
        else:
            last = r
    return p


def load_dir(path):
    return os.path.dirname(os.path.abspath(path))


def next_call(path):
    """The next ArtifactData call and how many writes it covers, or None when nothing is left."""
    writes = load(path)["writes"]
    if not writes:
        return None
    w = writes[0]
    if w["collection"] == "cards":
        run = []
        for x in writes:
            if x["collection"] != "cards":
                break
            run.append({"op": x["op"], "collection": "cards", "doc_id": x["doc_id"], "data": x["data"]})
        return {"count": len(run), "call": {"action": "batch", "writes": run}}
    name = "load-%s-%s.json" % (SAFE.sub("_", w["collection"]), SAFE.sub("_", w["doc_id"]))
    out = os.path.join(load_dir(path), name)
    save(out, w["data"])
    return {"count": 1, "call": {"action": w["op"], "collection": w["collection"], "doc_id": w["doc_id"], "file_path": out}}


def done(path, count):
    doc = load(path)
    doc["writes"] = doc["writes"][count:]
    for f in glob.glob(os.path.join(load_dir(path), "load-*.json")):
        os.remove(f)
    if doc["writes"]:
        save(path, doc)
    else:
        os.remove(path)
    return len(doc["writes"])


def main(argv):
    if len(argv) < 3 or argv[1] not in ("check", "next", "done"):
        print(USAGE)
        return 2
    path = argv[2]
    if not os.path.exists(path):
        if argv[1] == "next":
            print(json.dumps({"count": 0, "call": None}))  # already fully loaded (the file is deleted when empty)
            return 0
        print("cannot read %s: not found" % path)
        return 1
    try:
        doc = load(path)
    except ValueError as e:
        print("cannot read %s: %s" % (path, e))
        return 1
    problems = check(doc)
    if problems:
        for line in problems:
            print(line)
        return 1
    if argv[1] == "check":
        print("OK %d writes, in order" % len(doc["writes"]))
        return 0
    if argv[1] == "next":
        nxt = next_call(path)
        print(json.dumps(nxt if nxt else {"count": 0, "call": None}, ensure_ascii=False))
        return 0
    try:
        count = int(argv[3])
    except (IndexError, ValueError):
        print(USAGE)
        return 2
    if count < 1:
        print("count must be 1 or more. " + USAGE)
        return 2
    left = done(path, count)
    print("%d writes left" % left if left else "all writes loaded; pending file deleted")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
