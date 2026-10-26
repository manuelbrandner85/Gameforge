"""GAMEFORGE CPU smoke tests (masterprompt V1.2, H + B1.5): real jobs with real files, validated content.

Runs only CPU tools so it never competes with GPU renders of other sessions:
  Blender (.blend + GLB + FBX + render), FFmpeg/FFprobe (transcode + metadata), MLT melt (two-clip timeline with
  checked cut point), Krita (CLI export), Piper (German TTS sentence), faster-whisper (transcribes the TTS back),
  FFmpeg audio clean-up (loudness measured with ebur128).
Output: audit/evidence/smoke_cpu_<timestamp>/ with every artefact, stdout/stderr logs and validation.json.
GPU tests (Unreal render, ACE-Step, ComfyUI/FLUX) run separately when the GPU is free: smoke_gpu (Phase 1).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
STAMP = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "audit/evidence" / f"smoke_cpu_{STAMP}"
OUT.mkdir(parents=True, exist_ok=True)
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
KD = HOME / "AppData/Local/Programs/Kdenlive/bin"
KRITA = Path(r"C:\Program Files\Krita (x64)\bin\krita.exe")
AI = HOME / "AI-Tools/GENESIS"
results = {}


def run(name, cmd, cwd=None, timeout=300, env=None, stdin=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env, input=stdin,
                           encoding="utf8", errors="replace")
        code, so, se = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        code, so, se = "timeout", "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        code, so, se = "missing", "", str(e)
    (OUT / f"{name}.stdout.log").write_text(so, encoding="utf8")
    (OUT / f"{name}.stderr.log").write_text(se, encoding="utf8")
    return code, so + se


def probe(path, entries="stream=codec_name,width,height,r_frame_rate,sample_rate:format=duration", count=False):
    cmd = ["ffprobe", "-v", "error"] + (["-count_frames"] if count else []) + ["-show_entries", entries, "-of", "json", str(path)]
    code, out = run("ffprobe_" + Path(path).stem, cmd)
    return json.loads(out) if code == 0 else {}


def record(tool, ok, evidence, status_fail="failed"):
    results[tool] = {"status": "getestet" if ok else status_fail, "evidence": evidence}


# Blender -----------------------------------------------------------------------------------------------
bl_script = OUT / "bl_smoke.py"
bl_script.write_text(r'''
import bpy, os, json
out = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5)); cube = bpy.context.object
bpy.ops.object.camera_add(location=(2.5, -2.5, 2.0)); cam = bpy.context.object
cam.rotation_euler = ((cube.location - cam.location).to_track_quat("-Z", "Y")).to_euler(); sc.camera = cam
bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16
sc.render.resolution_x, sc.render.resolution_y = 320, 180
sc.render.filepath = os.path.join(out, "bl_render.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "bl_smoke.blend"))
bpy.ops.export_scene.gltf(filepath=os.path.join(out, "bl_smoke.glb"), export_format="GLB")
bpy.ops.export_scene.fbx(filepath=os.path.join(out, "bl_smoke.fbx"))
bpy.ops.render.render(write_still=True)
print("BL_SMOKE", json.dumps({"dims": list(cube.dimensions)}))
''', encoding="utf8")
code, out = run("blender", [str(BLENDER), "-b", "--python", str(bl_script)], timeout=600)
m = re.search(r"BL_SMOKE (\{.*\})", out)
files = {f: (OUT / f).exists() and (OUT / f).stat().st_size > 0 for f in ("bl_smoke.blend", "bl_smoke.glb", "bl_smoke.fbx", "bl_render.png")}
glb_ok = (OUT / "bl_smoke.glb").exists() and (OUT / "bl_smoke.glb").read_bytes()[:4] == b"glTF"
record("blender", code == 0 and all(files.values()) and glb_ok and m is not None,
       {"exit": code, "files": files, "glb_magic": glb_ok, "cube_dims_m": json.loads(m.group(1))["dims"] if m else None})

# FFmpeg / FFprobe ----------------------------------------------------------------------------------------
for name, src, freq in (("clipA", "testsrc2", 440), ("clipB", "smptebars", 660)):
    run(f"ffmpeg_{name}", ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}=size=640x360:rate=24:duration=2", "-f", "lavfi",
                           "-i", f"sine=frequency={freq}:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                           "-shortest", str(OUT / f"{name}.mp4")])
code, _ = run("ffmpeg_prores", ["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "clipA.mp4"), "-c:v", "prores_ks", "-profile:v", "3",
                                 "-c:a", "pcm_s24le", str(OUT / "clipA_prores.mov")])
p = probe(OUT / "clipA_prores.mov")
codecs = [s.get("codec_name") for s in p.get("streams", [])]
record("ffmpeg_ffprobe", code == 0 and "prores" in codecs and abs(float(p["format"]["duration"]) - 2.0) < 0.05,
       {"exit": code, "codecs": codecs, "duration_s": p.get("format", {}).get("duration")})

# MLT melt: two clips (48 frames each) -> 96-frame timeline, cut point checked by frame content ---------------
code, _ = run("melt", [str(KD / "melt.exe"), "-profile", "atsc_720p_24", str(OUT / "clipA.mp4"), "in=0", "out=47",
                       str(OUT / "clipB.mp4"), "in=0", "out=47", "-consumer", f"avformat:{OUT / 'melt_timeline.mp4'}",
                       "vcodec=libx264", "acodec=aac", "real_time=-1"], cwd=KD, timeout=200)
p = probe(OUT / "melt_timeline.mp4", "stream=nb_read_frames,width,height,r_frame_rate:format=duration", count=True)
frames = int(p["streams"][0]["nb_read_frames"]) if p.get("streams") else 0
# one frame from each half of the timeline: clip A (testsrc2) at 1 s, clip B (smptebars) at 3 s must differ
for t in (1.0, 3.0):
    run(f"melt_png_{int(t)}", ["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(OUT / "melt_timeline.mp4"), "-frames:v", "1",
                               str(OUT / f"melt_t{int(t)}.png")])
cut_ok = (OUT / "melt_t1.png").exists() and (OUT / "melt_t3.png").exists() and \
    (OUT / "melt_t1.png").read_bytes() != (OUT / "melt_t3.png").read_bytes()
record("mlt_melt", code == 0 and frames == 96 and cut_ok,
       {"exit": code, "frames": frames, "expected_frames": 96, "duration_s": p.get("format", {}).get("duration"),
        "cut_frames_differ": cut_ok, "note": "melt muss mit Arbeitsordner Kdenlive\\bin laufen (DLL-Suche)"})

# Krita CLI export -----------------------------------------------------------------------------------------
code, _ = run("krita", [str(KRITA), "--export", "--export-filename", str(OUT / "krita_out.png"), str(OUT / "bl_render.png")], timeout=180)
ok = (OUT / "krita_out.png").exists() and (OUT / "krita_out.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
record("krita", code == 0 and ok, {"exit": code, "png": ok})

# Piper TTS (German) -> faster-whisper back-transcription ------------------------------------------------------
SENT = "Dies ist ein Test der deutschen Sprachausgabe."
env = dict(os.environ, PYTHONUTF8="1")
code, _ = run("piper", [str(AI / "piper/venv/Scripts/python.exe"), "-m", "piper", "-m", str(AI / "piper/voices/de_DE-thorsten-high.onnx"),
                        "-f", str(OUT / "tts_de.wav")], env=env, stdin=SENT, timeout=180)
p = probe(OUT / "tts_de.wav")
wh = (r"from faster_whisper import WhisperModel" "\n"
      rf"m=WhisperModel('small',device='cpu',compute_type='int8',download_root=r'{AI / 'faster-whisper/models'}',local_files_only=True)" "\n"
      rf"s,_=m.transcribe(r'{OUT / 'tts_de.wav'}',language='de')" "\n"
      r"print('WHISPER:'+' '.join(x.text.strip() for x in s))")
c2, o2 = run("whisper", [str(AI / "faster-whisper/venv/Scripts/python.exe"), "-c", wh], env=env, timeout=400)
heard = (re.search(r"WHISPER:(.*)", o2) or [None, ""])[1].strip()
words = [w for w in re.findall(r"\w+", SENT.lower())]
hit = sum(1 for w in words if w in heard.lower()) / len(words)
record("piper_tts", code == 0 and p.get("format") is not None, {"exit": code, "voice": "de_DE-thorsten-high", "wav": p})
record("faster_whisper", c2 == 0 and hit >= 0.8, {"exit": c2, "heard": heard, "word_match": round(hit, 2)})

# Audio clean-up (Audacity 4 has no mod-script-pipe -> FFmpeg fallback) ------------------------------------------
code, _ = run("audio_clean", ["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "tts_de.wav"), "-af",
                              "highpass=f=80,afftdn=nf=-30,loudnorm=I=-23:TP=-2:LRA=7", "-ar", "48000", "-c:a", "pcm_s24le",
                              str(OUT / "tts_de_clean.wav")])
c2, o2 = run("ebur128", ["ffmpeg", "-hide_banner", "-i", str(OUT / "tts_de_clean.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"])
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", o2)
pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o2)
lufs = float(I[-1]) if I else None
record("audio_cleanup_ffmpeg", code == 0 and lufs is not None and -24.5 < lufs < -21.5,
       {"exit": code, "integrated_lufs": lufs, "true_peak_dbfs": float(pk[-1]) if pk else None, "target": "-23 LUFS / -2 dBTP"})

summary = {"timestamp": STAMP, "out": str(OUT), "results": results,
           "passed": sum(r["status"] == "getestet" for r in results.values()), "total": len(results)}
(OUT / "validation.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf8")
print("SMOKE_CPU", json.dumps({k: v["status"] for k, v in results.items()}, ensure_ascii=False))
