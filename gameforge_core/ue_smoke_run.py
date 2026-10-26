"""GAMEFORGE Unreal smoke test runner (masterprompt H/B1.5): setup headless -> MRQ command-line render of 5 frames ->
validation -> optional packaging (BuildCookRun). Isolated project projects/_smoke/UE_Smoke; takes the GPU lock.
  python gameforge_core/ue_smoke_run.py [--package]
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gameforge_core.gpu_lock import gpu_job  # noqa: E402

UE = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine")
CMD = UE / "Binaries/Win64/UnrealEditor-Cmd.exe"
PROJ = ROOT / "projects/_smoke/UE_Smoke/UE_Smoke.uproject"
STAMP = time.strftime("%Y%m%d_%H%M%S")
EV = ROOT / "audit/evidence" / f"ue_smoke_{STAMP}"
EV.mkdir(parents=True, exist_ok=True)
FBX = sorted((ROOT / "audit/evidence").glob("smoke_cpu_*/bl_smoke.fbx"))[-1]
res = {"project": str(PROJ)}


def run(name, args, timeout, env=None):
    t0 = time.time()
    with open(EV / f"{name}.log", "w", encoding="utf8", errors="replace") as log:
        r = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=timeout, env=env)
    txt = (EV / f"{name}.log").read_text(encoding="utf8", errors="replace")
    return r.returncode, round(time.time() - t0), txt


with gpu_job("ue_smoke", need_mb=3500):
    env = dict(os.environ, GF_SMOKE_FBX=str(FBX), GF_SMOKE_OUT=str(EV / "frames"))
    code, sec, txt = run("setup", [str(CMD), str(PROJ), "-run=pythonscript", f"-script={ROOT / 'gameforge_core/ue_smoke_setup.py'}",
                                   "-unattended", "-nosplash", "-nop4", "-stdout", "-FullStdOutLogOutput"], 1800, env)
    line = next((l for l in txt.splitlines() if "GF_UE_SMOKE " in l and "LogPython" in l), "")
    res["setup"] = {"exit": code, "sec": sec, "result": json.loads(line.split("GF_UE_SMOKE ", 1)[1]) if line else None}
    code, sec, txt = run("render", [str(CMD), str(PROJ), "/Game/Smoke/L_Smoke", "-game", "-LevelSequence=/Game/Smoke/LS_Smoke",
                                    "-MoviePipelineConfig=/Game/Smoke/MRQ_Smoke", "-windowed", "-ResX=640", "-ResY=360",
                                    "-NoLoadingScreen", "-Unattended", "-NoSplash"], 1800)
    frames = sorted((EV / "frames").glob("smoke.*.png"))
    sizes = [f.stat().st_size for f in frames]
    res["render"] = {"exit": code, "sec": sec, "frames": len(frames), "distinct": len(set(f.read_bytes() for f in frames)),
                     "finished": "Finished rendering" in txt or "MoviePipeline" in txt}
if "--package" in sys.argv:
    uat = UE / "Build/BatchFiles/RunUAT.bat"
    code, sec, txt = run("package", ["cmd", "/c", str(uat), "BuildCookRun", f"-project={PROJ}", "-noP4", "-platform=Win64",
                                     "-clientconfig=Development", "-cook", "-allmaps", "-stage", "-pak", "-archive",
                                     f"-archivedirectory={EV / 'package'}", "-unattended", "-utf8output"], 3600)
    exe = list((EV / "package").rglob("*.exe"))
    res["package"] = {"exit": code, "sec": sec, "exe": [str(e) for e in exe][:3], "ok": code == 0 and bool(exe),
                      "tail": [l for l in txt.splitlines() if "BUILD" in l or "ERROR" in l.upper()][-5:]}
setup_ok = bool(res["setup"]["result"]) and res["setup"]["result"].get("import_ok")
res["ok"] = setup_ok and res["render"]["frames"] == 5 and res["render"]["distinct"] >= 2
(EV / "validation.json").write_text(json.dumps(res, indent=1), encoding="utf8")
print("UE_SMOKE", json.dumps(res))
