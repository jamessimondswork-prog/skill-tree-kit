"""Save a YouTube video's transcript as timestamped text.

Usage (no -I: the package sits in user site-packages): python -X utf8 transcript.py <youtube url or id> <out.txt>
Install: python -m pip install youtube_transcript_api
Check: python -X utf8 -c "import youtube_transcript_api"
Public captions only. Exits 2 with a reason if none are available.
"""
import re
import sys

from youtube_transcript_api import YouTubeTranscriptApi


def video_id(link):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{11})", link)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", link):
        return link
    sys.exit(f"Can't find a video id in: {link}")


def stamp(seconds):
    s = int(seconds)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    vid, out = video_id(sys.argv[1]), sys.argv[2]
    try:
        snippets = YouTubeTranscriptApi().fetch(vid, languages=["en", "en-GB", "en-US"])
    except Exception as e:  # no captions, private, region-locked
        print(f"No transcript: {type(e).__name__}", file=sys.stderr)
        sys.exit(2)
    lines = [f"[{stamp(s.start)}] {s.text}" for s in snippets]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    last = snippets[-1] if len(snippets) else None
    length = stamp(last.start + last.duration) if last else "0:00:00"
    print(f"{vid}: {len(lines)} lines, {length} long -> {out}")


if __name__ == "__main__":
    main()
