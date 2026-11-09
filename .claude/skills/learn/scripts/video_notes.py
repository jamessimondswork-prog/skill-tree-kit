"""Turn a local video (a saved TikTok, a screen recording) into notes /learn can teach from.

Writes, next to OUT_DIR:
  transcript.txt  speech with [m:ss] timestamps (faster-whisper, runs locally, nothing leaves the laptop)
  frames/         one JPEG every few seconds, for on-screen text and code (read them with the Read tool)

Usage (no -I: the transcriber needs user site-packages): python -X utf8 video_notes.py <video.mp4> <out_dir> [--every 3] [--model base]
Install: python -m pip install faster-whisper av
Check: python -X utf8 -c "import faster_whisper, av"   (setup records the result as deps.faster_whisper)
"""
import argparse
import sys
from pathlib import Path


def stamp(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def frames(video, out, every):
    import av
    out.mkdir(parents=True, exist_ok=True)
    saved, next_t = [], 0.0
    with av.open(str(video)) as box:
        stream = box.streams.video[0]
        for frame in box.decode(stream):
            t = float(frame.time or 0)
            if t < next_t:
                continue
            img = frame.to_image()
            img.thumbnail((720, 720))
            path = out / f"{stamp(t).replace(':', 'm')}s.jpg"
            img.save(path, quality=80)
            saved.append(path)
            next_t = t + every
    return saved


def audio_16k(video):
    # Decode here: faster-whisper's own loader breaks on newer PyAV.
    import av
    import numpy as np
    chunks = []
    with av.open(str(video)) as box:
        if not box.streams.audio:
            raise ValueError("no audio track")
        rs = av.AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in box.decode(box.streams.audio[0]):
            for f in rs.resample(frame):
                chunks.append(f.to_ndarray().reshape(-1))
        for f in rs.resample(None):
            chunks.append(f.to_ndarray().reshape(-1))
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def transcript(video, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_16k(video), vad_filter=True)
    lines = [f"[{stamp(s.start)}] {s.text.strip()}" for s in segments if s.text.strip()]
    return lines, info.language, info.duration


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--every", type=float, default=3.0, help="seconds between frames")
    ap.add_argument("--model", default="base", help="whisper size: tiny, base, small")
    a = ap.parse_args()
    video, out = Path(a.video), Path(a.out_dir)
    if not video.is_file():
        sys.exit(f"No file at {video}")
    out.mkdir(parents=True, exist_ok=True)

    shots = frames(video, out / "frames", a.every)
    try:
        lines, lang, dur = transcript(video, a.model)
    except ImportError as e:
        sys.exit(f"Transcriber missing ({e}). Run: python -m pip install faster-whisper")
    except Exception as e:  # no audio track
        lines, lang, dur = [], "?", 0
        print(f"Transcription failed ({e.__class__.__name__}: {e})")
    (out / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{video.name}: {stamp(dur)} long, language {lang}, {len(lines)} speech lines, {len(shots)} frames")
    print(f"Transcript: {out / 'transcript.txt'}")
    print(f"Frames: {out / 'frames'}")
    if not lines:
        print("No speech. Teach from the frames (on-screen text) and say so in the hand-over.")


if __name__ == "__main__":
    main()
