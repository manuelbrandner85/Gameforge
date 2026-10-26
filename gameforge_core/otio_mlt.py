"""GAMEFORGE film adapter: OpenTimelineIO cut plan -> MLT render (masterprompt F9).

The cut plan lives in an .otio file (Apache-2.0 OpenTimelineIO, venv C:\\Users\\manue\\AI-Tools\\GAMEFORGE\\otio).
Kdenlive has no automation API; MLT's melt renders the timeline. This module turns the first video track of an OTIO
timeline into a melt command (clip, in, out) and renders it.  Run inside the OTIO venv:
  <otio venv python> gameforge_core/otio_mlt.py smoke <clipA> <clipB> <outdir>
"""
import json
import subprocess
import sys
from pathlib import Path

import opentimelineio as otio

MELT_BIN = Path.home() / "AppData/Local/Programs/Kdenlive/bin"   # melt only finds its DLLs with this working dir


def build_timeline(name, clips, fps=24):
    """clips: list of (media_path, in_frame, out_frame_inclusive)"""
    tl = otio.schema.Timeline(name=name)
    track = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    tl.tracks.append(track)
    for path, fin, fout in clips:
        rng = otio.opentime.TimeRange(otio.opentime.RationalTime(fin, fps), otio.opentime.RationalTime(fout - fin + 1, fps))
        track.append(otio.schema.Clip(name=Path(path).stem, media_reference=otio.schema.ExternalReference(target_url=str(path)),
                                      source_range=rng))
    return tl


def melt_args(tl, out_file, profile="atsc_720p_24"):
    args = [str(MELT_BIN / "melt.exe"), "-profile", profile]
    for clip in tl.tracks[0]:
        sr = clip.source_range
        fin = int(sr.start_time.value)
        args += [clip.media_reference.target_url, f"in={fin}", f"out={fin + int(sr.duration.value) - 1}"]
    return args + ["-consumer", f"avformat:{out_file}", "vcodec=libx264", "acodec=aac", "real_time=-1"]


def render(tl, out_file, timeout=600):
    r = subprocess.run(melt_args(tl, out_file), cwd=MELT_BIN, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stderr[-2000:]


if __name__ == "__main__" and len(sys.argv) >= 5 and sys.argv[1] == "smoke":
    a, b, out = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    tl = build_timeline("gameforge_otio_smoke", [(a, 0, 47), (b, 12, 35)])        # 48 + 24 frames = 72
    otio_file = out / "smoke_timeline.otio"
    otio.adapters.write_to_file(tl, str(otio_file))
    tl2 = otio.adapters.read_from_file(str(otio_file))                             # round trip
    frames = int(tl2.duration().value)
    code, err = render(tl2, out / "otio_timeline.mp4")
    pr = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                         "stream=nb_read_frames:format=duration", "-of", "json", str(out / "otio_timeline.mp4")],
                        capture_output=True, text=True)
    rendered = int(json.loads(pr.stdout)["streams"][0]["nb_read_frames"]) if pr.returncode == 0 else None
    res = {"otio_version": otio.__version__, "otio_file": str(otio_file), "timeline_frames": frames, "melt_exit": code,
           "rendered_frames": rendered, "adapters": sorted(otio.adapters.available_adapter_names()),
           "ok": code == 0 and frames == 72 and rendered == 72}
    (out / "otio_validation.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    print("OTIO_SMOKE", json.dumps(res))
