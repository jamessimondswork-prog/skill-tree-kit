"""Rebuild a big upload from the Skill Tree's base64 parts.

The page splits files over 20 MB (and .mov) into text/plain parts holding base64. Download each part
with Artifact `read` (`path` = part id, in the order listed in the request's `files[].parts`), then:

Usage: python -I -X utf8 join_parts.py <out_file> <part1> <part2> ... [--size BYTES]
"""
import base64
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    size = None
    if "--size" in args:
        i = args.index("--size")
        size = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    out, parts = Path(args[0]), [Path(p) for p in args[1:]]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        for p in parts:
            f.write(base64.b64decode(p.read_text(encoding="utf-8").strip(), validate=True))
    got = out.stat().st_size
    if size is not None and got != size:
        sys.exit(f"Size mismatch: built {got} bytes, page said {size}. A part is missing or out of order.")
    print(f"Joined {len(parts)} parts into {out} ({got / 1048576:.1f} MB)")


if __name__ == "__main__":
    main()
