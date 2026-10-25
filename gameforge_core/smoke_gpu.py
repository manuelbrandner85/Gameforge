"""GAMEFORGE GPU smoke tests (masterprompt H, "1 selbst erzeugtes Musikstueck", Bild-KI mit Modell-/Lizenznachweis).

Runs one after the other under the GAMEFORGE GPU lock (never in parallel with another GAMEFORGE GPU job):
- ACE-Step 1.5: 10 s instrumental cue (DiT turbo, local), validated by duration and loudness (not silence)
- FLUX.2 klein 4B via local ComfyUI (127.0.0.1 only): one 768x512 image with provenance (prompt, seed, model hashes);
  a ComfyUI started by this test is stopped again afterwards to free the VRAM
Reuses the GENESIS adapters tools/v4_1/ace_step_smoke.py and flux_klein_ref.py unchanged (read-only use).
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gameforge_core.gpu_lock import gpu_job  # noqa: E402

GEN = Path(r"C:\Users\manue\Desktop\Genesis-Games\tools\v4_1")
ACE_PY = Path(r"C:\Users\manue\AI-Tools\GENESIS\ace-step\ACE-Step-1.5\.venv\Scripts\python.exe")
EV = ROOT / "audit/evidence" / time.strftime("smoke_gpu_%Y%m%d_%H%M%S")
EV.mkdir(parents=True, exist_ok=True)
res = {}


def comfy_online():
    try:
        urllib.request.build_opener(urllib.request.ProxyHandler({})).open("http://127.0.0.1:8188/system_stats", timeout=3)
        return True
    except Exception:
        return False


with gpu_job("ace_step_smoke", need_mb=5000):
    t0 = time.time()
    r = subprocess.run([str(ACE_PY), str(GEN / "ace_step_smoke.py"), "--out", str(EV / "ace_step"), "--seconds", "10"],
                       capture_output=True, text=True, encoding="utf8", errors="replace", timeout=1800, env=dict(__import__("os").environ, PYTHONUTF8="1",
                       ACESTEP_CHECKPOINTS_DIR=r"C:\Users\manue\AI-Tools\GENESIS\ace-step\checkpoints"))
    (EV / "ace_step.log").write_text((r.stdout or "") + (r.stderr or ""), encoding="utf8")
    wavs = sorted((EV / "ace_step").rglob("*.wav"))
    dur = lufs = None
    if wavs:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(wavs[0])],
                           capture_output=True, text=True)
        dur = float(json.loads(p.stdout)["format"]["duration"])
        e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wavs[0]), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        I = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
        lufs = float(I[-1]) if I else None
    res["ace_step"] = {"exit": r.returncode, "sec": round(time.time() - t0), "wav": str(wavs[0]) if wavs else None,
                       "duration_s": dur, "lufs": lufs,
                       "ok": r.returncode == 0 and dur is not None and dur >= 9 and lufs is not None and lufs > -50}

with gpu_job("flux_smoke", need_mb=7000):
    was_online = comfy_online()
    t0 = time.time()
    r = subprocess.run([sys.executable, str(GEN / "flux_klein_ref.py"), "--asset", "GF_SMOKE", "--view", "test", "--seed", "11",
                        "--width", "768", "--height", "512", "--out", str(EV / "flux"),
                        "--prompt", "photograph of a wooden table with a ceramic cup in soft morning window light, realistic"],
                       capture_output=True, text=True, encoding="utf8", errors="replace", timeout=1800)
    (EV / "flux.log").write_text((r.stdout or "") + (r.stderr or ""), encoding="utf8")
    pngs = sorted((EV / "flux").rglob("*.png"))
    prov = sorted((EV / "flux").rglob("*.json"))
    res["flux"] = {"exit": r.returncode, "sec": round(time.time() - t0), "png": str(pngs[0]) if pngs else None,
                   "provenance": str(prov[0]) if prov else None, "ok": r.returncode == 0 and bool(pngs) and bool(prov)}
    if not was_online and comfy_online():                 # started by this test: stop it again (frees ~7 GB VRAM)
        ps = ("Get-NetTCPConnection -LocalPort 8188 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess | "
              "ForEach-Object { Stop-Process -Id $_ -Force }")
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
        res["flux"]["comfy_stopped"] = not comfy_online()

(EV / "validation.json").write_text(json.dumps(res, indent=1), encoding="utf8")
print("SMOKE_GPU", json.dumps(res))
