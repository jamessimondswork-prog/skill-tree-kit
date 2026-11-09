"""Check and rank role-gaps.json, and scan built files for private terms.

  python -I -X utf8 role_gaps.py check <file> [--terms "a,b"]        (exit 1 on problems)
  python -I -X utf8 role_gaps.py rank <file>                        (open gap ids by priority)
  python -I -X utf8 role_gaps.py scan <file-or-folder> [<more> ...] --terms "a,b" [--all-text] [--exclude <path>[,<path>]]
                                                                    (every .json/.md, exit 1 on hits)

scan options:
  --all-text   scan every text type a kit ships: .json .md .py .csv .txt .sql .html
  --exclude    skip these files or folders (comma-separated), e.g. skill-tree/example

--terms takes one quoted, comma-separated value. An empty or missing value is a usage error (exit 2).
"""
import json
import os
import re
import sys

USAGE = ('usage: role_gaps.py check <file> [--terms "a,b"] | rank <file> | '
         'scan <file-or-folder> [<more> ...] --terms "a,b" [--all-text] [--exclude <path>[,<path>]]')
SCAN_EXT = (".json", ".md")
ALL_TEXT_EXT = (".json", ".md", ".py", ".csv", ".txt", ".sql", ".html")

PRIORITIES = ("high", "medium", "low")
STATUSES = ("open", "offered", "built", "covered")
SOURCES = ("setup", "work-project", "target-role")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def check(data, terms=()):
    p = []
    if not isinstance(data, dict):
        return ["file is not a JSON object"]
    u = data.get("updatedOn")
    if u is not None and not (isinstance(u, str) and DATE.match(u)):
        p.append("updatedOn must be YYYY-MM-DD or null")
    srcs = data.get("sources")
    if not isinstance(srcs, list) or any(s not in SOURCES for s in srcs):
        p.append("sources must be a list of: " + ", ".join(SOURCES))
    gaps = data.get("gaps")
    if not isinstance(gaps, list):
        return p + ["gaps must be a list"]
    seen = set()
    for n, g in enumerate(gaps):
        gid = g.get("id") if isinstance(g, dict) else None
        tag = "gap %s" % (gid if isinstance(gid, str) and gid else "#%d" % n)
        if not isinstance(g, dict):
            p.append("%s: not an object" % tag)
            continue
        if not (isinstance(gid, str) and KEBAB.match(gid)):
            p.append("%s: id must be kebab-case" % tag)
        elif gid in seen:
            p.append("%s: duplicate id" % tag)
        seen.add(gid)
        for k in ("skill", "why"):
            if not (isinstance(g.get(k), str) and g[k].strip()):
                p.append("%s: %s required" % (tag, k))
        if g.get("priority") not in PRIORITIES:
            p.append("%s: priority must be high, medium or low" % tag)
        r = g.get("resource")
        if not (isinstance(r, dict) and isinstance(r.get("title"), str) and isinstance(r.get("url"), str)):
            p.append("%s: resource needs title and url strings" % tag)
        sr = g.get("selfRating")
        if sr is not None:
            ok = isinstance(sr, dict) and isinstance(sr.get("question"), str) and isinstance(sr.get("answer"), str)
            if not ok:
                p.append("%s: selfRating needs question and answer strings" % tag)
            lvl = sr.get("startLevel") if isinstance(sr, dict) else None
            if isinstance(lvl, bool) or not isinstance(lvl, int) or not 1 <= lvl <= 4:
                p.append("%s: selfRating startLevel must be an integer 1-4" % tag)
        if g.get("status") not in STATUSES:
            p.append("%s: status must be open, offered, built or covered" % tag)
        t = g.get("topicId")
        if t is not None and not isinstance(t, str):
            p.append("%s: topicId must be a string or null" % tag)
        if g.get("status") == "built" and not (isinstance(t, str) and t):
            p.append("%s: topicId required when status is built" % tag)
        for s in strings(g):
            for term in terms:
                if term and term.lower() in s.lower():
                    p.append("%s: contains term '%s'" % (tag, term))
    return p


def _skipped(path, excludes):
    a = os.path.normcase(os.path.abspath(path))
    return any(a == e or a.startswith(e + os.sep) for e in excludes)


def scan_files(paths, exts=SCAN_EXT, exclude=()):
    if isinstance(paths, str):
        paths = [paths]
    excludes = [os.path.normcase(os.path.abspath(e)) for e in exclude]
    out = []
    for path in paths:
        if _skipped(path, excludes):
            continue
        if os.path.isfile(path):
            out.append(path)
            continue
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = sorted(d for d in dirnames if not _skipped(os.path.join(dirpath, d), excludes))
            out += [os.path.join(dirpath, n) for n in sorted(filenames)
                    if n.lower().endswith(exts) and not _skipped(os.path.join(dirpath, n), excludes)]
    return out


def scan(paths, terms, exts=SCAN_EXT, exclude=()):
    """Every (file, line, term) where a term appears, case-insensitive."""
    hits = []
    for f in scan_files(paths, exts, exclude):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            low = line.lower()
            for term in terms:
                if term.lower() in low:
                    hits.append((f, n, term))
    return hits


def parse_terms(argv):
    """None when --terms isn't given; raises ValueError when it's given with no usable value."""
    if "--terms" not in argv:
        return None
    i = argv.index("--terms")
    value = argv[i + 1] if i + 1 < len(argv) else ""
    if value.startswith("--"):
        value = ""
    terms = [t.strip() for t in value.split(",") if t.strip()]
    if not terms:
        raise ValueError("--terms needs a value")
    return terms


def rank(data):
    open_gaps = [g for g in data.get("gaps", []) if g.get("status") == "open"]
    return [g["id"] for pr in PRIORITIES for g in open_gaps if g.get("priority") == pr]


def main(argv):
    if len(argv) < 3 or argv[1] not in ("check", "rank", "scan"):
        print(USAGE)
        return 2
    try:
        terms = parse_terms(argv)
    except ValueError as e:
        print("%s. %s" % (e, USAGE))
        return 2
    if argv[1] == "scan":
        if terms is None:
            print("scan needs --terms. " + USAGE)
            return 2
        paths, exclude, exts, i = [], [], SCAN_EXT, 2
        while i < len(argv):
            a = argv[i]
            if a == "--terms":
                i += 2
                continue
            if a == "--all-text":
                exts = ALL_TEXT_EXT
            elif a == "--exclude":
                value = argv[i + 1] if i + 1 < len(argv) else ""
                exclude += [e.strip() for e in value.split(",") if e.strip()]
                if not value.strip() or value.startswith("--"):
                    print("--exclude needs a value. " + USAGE)
                    return 2
                i += 1
            elif a.startswith("--"):
                print("unknown option %s. %s" % (a, USAGE))
                return 2
            else:
                paths.append(a)
            i += 1
        if not paths:
            print(USAGE)
            return 2
        for path in paths:
            if not os.path.exists(path):
                print("cannot read %s: not found" % path)
                return 1
        hits = scan(paths, terms, exts, exclude)
        for f, n, term in hits:
            print("%s:%d: %s" % (f, n, term))
        if hits:
            return 1
        print("OK %d files, no terms found" % len(scan_files(paths, exts, exclude)))
        return 0
    try:
        data = load(argv[2])
    except (OSError, ValueError) as e:
        print("cannot read %s: %s" % (argv[2], e))
        return 1
    if argv[1] == "rank":
        for i in rank(data):
            print(i)
        return 0
    problems = check(data, terms or [])
    for line in problems:
        print(line)
    if problems:
        return 1
    print("OK %d gaps" % len(data["gaps"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
