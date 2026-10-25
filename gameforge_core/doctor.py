"""gameforge doctor (read-only) - Phase 0 of the GAMEFORGE game+film extension (masterprompt V1.2, B1.1 + B2.1).

Inventories hardware, installed programs, Claude Code scopes (settings, hooks, agents, skills, plugins, MCP) and the
GENESIS canon baseline WITHOUT changing anything. Writes:
  setup/hardware.json, setup/tool-inventory.json, audit/claude-config-inventory.json, audit/claude-health-baseline.json
Settings are reported by key names only (no values: no tokens, no secrets). Run:  python gameforge_core/doctor.py [--mcp]
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DESK = HOME / "Desktop"
ROOT = Path(__file__).resolve().parents[1]
NOW = _dt.datetime.now().isoformat(timespec="seconds")


def run(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding="utf8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:                                  # missing program, timeout
        return None, f"{type(e).__name__}: {e}"


def first_line(s):
    return s.splitlines()[0].strip() if s else ""


def file_version(p: Path):
    if not p.exists():
        return None
    code, out = run(["powershell", "-NoProfile", "-Command", f"(Get-Item '{p}').VersionInfo.ProductVersion"])
    return out or "unbekannt"


# ------------------------------------------------------------------ hardware (B1.1)
def hardware():
    code, gpu = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    code2, sysinfo = run(["powershell", "-NoProfile", "-Command",
                          "$o=Get-CimInstance Win32_OperatingSystem;$c=Get-CimInstance Win32_Processor;"
                          "\"$($o.Caption)|$($o.BuildNumber)|$($c.Name)|$($c.NumberOfCores)|$($c.NumberOfLogicalProcessors)|$([math]::Round($o.TotalVisibleMemorySize/1MB,1))\""])
    parts = (sysinfo or "").split("|")
    disks = {}
    for d in ("C:\\",):
        u = shutil.disk_usage(d)
        disks[d] = {"free_gb": round(u.free / 2**30, 1), "total_gb": round(u.total / 2**30, 1)}
    return {"timestamp": NOW, "method": "nvidia-smi, WMI (Win32_OperatingSystem/Processor), shutil.disk_usage",
            "os": parts[0] if parts else None, "build": parts[1] if len(parts) > 1 else None,
            "cpu": parts[2].strip() if len(parts) > 2 else None, "cores": parts[3] if len(parts) > 3 else None,
            "threads": parts[4] if len(parts) > 4 else None, "ram_gb": parts[5] if len(parts) > 5 else None,
            "gpu": gpu, "disks": disks}


# ------------------------------------------------------------------ programs (B1.1 point 3)
def tools():
    ue = Path(r"C:\Program Files\Epic Games\UE_5.8")
    kd = HOME / "AppData/Local/Programs/Kdenlive/bin"
    ai = HOME / "AI-Tools"
    comfy = ROOT / "engines/ComfyUI_windows_portable/ComfyUI"
    t = {}

    def add(name, found, version=None, path=None, how="", note=""):
        t[name] = {"found": bool(found), "version": version, "path": str(path) if path else None, "method": how, "note": note}

    c, o = run(["claude", "--version"]); add("claude_code", c == 0, first_line(o), shutil.which("claude"), "claude --version")
    c, o = run([sys.executable, "--version"]); add("python", c == 0, first_line(o), sys.executable, "--version")
    c, o = run(["git", "--version"]); add("git", c == 0, first_line(o), shutil.which("git"), "--version")
    c, o = run(["git", "lfs", "version"]); add("git_lfs", c == 0, first_line(o), None, "git lfs version")
    c, o = run(["winget", "--version"]); add("winget", c == 0, first_line(o), shutil.which("winget"), "--version")
    bl = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
    c, o = run([str(bl), "--version"], timeout=90) if bl.exists() else (None, "")
    add("blender", bl.exists(), first_line(o), bl, "blender --version")
    bv = ue / "Engine/Build/Build.version"
    if bv.exists():
        d = json.loads(bv.read_text(encoding="utf8"))
        add("unreal_engine", True, f'{d["MajorVersion"]}.{d["MinorVersion"]}.{d["PatchVersion"]} CL{d["Changelist"]}', ue, "Build.version")
    else:
        add("unreal_engine", False)
    for plug in ("PythonScriptPlugin", "MovieRenderPipeline", "SequencerScripting", "MetaHumanCharacter",
                 "MetaHuman", "MetaHumanAnimationTools", "ControlRig", "PCG", "Niagara", "RemoteControl"):
        hits = list((ue / "Engine/Plugins").rglob(f"{plug}.uplugin")) if ue.exists() else []
        add(f"ue_plugin_{plug}", bool(hits), None, hits[0] if hits else None, "*.uplugin im Engine-Ordner")
    c, o = run(["ffmpeg", "-version"]); add("ffmpeg", c == 0, first_line(o), shutil.which("ffmpeg"), "-version")
    c, o = run(["ffprobe", "-version"]); add("ffprobe", c == 0, first_line(o), shutil.which("ffprobe"), "-version")
    c, o = run([str(kd / "melt.exe"), "-version"], cwd=kd) if (kd / "melt.exe").exists() else (None, "")
    add("mlt_melt", c == 0, first_line(o), kd / "melt.exe", "melt -version (cwd=bin: DLL-Suche)",
        "nur mit Arbeitsordner = Kdenlive\\bin startfähig; sonst hängt melt ohne Ausgabe")
    add("kdenlive", (kd / "kdenlive.exe").exists(), None, kd / "kdenlive.exe", "Dateisuche", "GUI zur Sichtkorrektur")
    kr = Path(r"C:\Program Files\Krita (x64)\bin\krita.exe"); add("krita", kr.exists(), file_version(kr), kr, "VersionInfo")
    au = Path(r"C:\Program Files\Audacity 4\bin\Audacity4.exe")
    mod = list(Path(r"C:\Program Files\Audacity 4").rglob("*mod-script-pipe*")) if au.exists() else []
    add("audacity", au.exists(), file_version(au), au, "VersionInfo",
        "mod-script-pipe vorhanden" if mod else "kein mod-script-pipe-Modul in Audacity 4 gefunden: nur manuell")
    nat = [p for d in (Path(r"C:\Program Files"), HOME / "AppData/Local/Programs") if d.exists()
           for p in d.glob("Natron*/bin/NatronRenderer.exe")]
    add("natron", bool(nat), None, nat[0] if nat else None, "Dateisuche NatronRenderer.exe")
    c, o = run([sys.executable, "-c", "import opentimelineio as o;print(o.__version__)"])
    add("opentimelineio", c == 0, first_line(o) if c == 0 else None, None, "import im System-Python")
    for name, rel in (("piper_tts", "GENESIS/piper/venv/Scripts/python.exe"),
                      ("faster_whisper", "GENESIS/faster-whisper/venv/Scripts/python.exe"),
                      ("ace_step_1_5", "GENESIS/ace-step/ACE-Step-1.5"),
                      ("chatterbox_tts", "GENESIS_TRAILER/chatterbox")):
        p = ai / rel
        add(name, p.exists(), None, p, "Ordner/venv vorhanden")
    add("comfyui", comfy.exists(), None, comfy, "Ordner")
    models = sorted(x.name for x in (comfy / "models/diffusion_models").glob("*.safetensors")) if comfy.exists() else []
    t["comfyui"]["note"] = "Modelle: " + ", ".join(models)
    c, o = run([str(HOME / "AppData/Local/Programs/Ollama/ollama.exe"), "--version"])
    add("ollama", c == 0, first_line(o), None, "--version", "lokale LLM-Laufzeit; nicht Teil der Pipeline")
    for name in ("rhubarb", "material_maker", "freemocap", "davinci_resolve"):
        add(name, bool(shutil.which(name)), None, shutil.which(name), "PATH")
    return t


# ------------------------------------------------------------------ Claude Code scopes (B2.1)
FRONT = re.compile(r"^---\s*\n(.*?)\n---", re.S)


def frontmatter(p: Path):
    try:
        m = FRONT.match(p.read_text(encoding="utf8", errors="replace"))
    except Exception as e:
        return {"error": str(e)}
    if not m:
        return {"error": "kein Frontmatter"}
    keys = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            keys[k.strip()] = v.strip()[:80]
    return keys


def settings_file(p: Path):
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        return {"path": str(p), "valid_json": False, "error": str(e)}
    hooks = []
    for event, groups in (d.get("hooks") or {}).items():
        for g in groups:
            for h in g.get("hooks", []):
                cmd = h.get("command", "")
                script = re.findall(r'[\w${}/\\:.-]+\.py', cmd)
                hooks.append({"event": event, "matcher": g.get("matcher"), "timeout": h.get("timeout"), "script": script})
    perms = d.get("permissions") or {}
    return {"path": str(p), "valid_json": True, "keys": sorted(d.keys()), "hooks": hooks,
            "permissions": {"allow": len(perms.get("allow", [])), "deny": len(perms.get("deny", [])),
                            "defaultMode": perms.get("defaultMode")}}


def claude_inventory(with_mcp: bool):
    projects = {"user": HOME, "desktop": DESK, "genesis_game": DESK / "Genesis-Games",
                "gameforge": ROOT, "genesis_trailer": DESK / "GENESIS_CINEMA_TRAILER",
                "aion_game": DESK / "Aion-Game", "aion_v21": DESK / "AION_2026_V21"}
    inv = {"timestamp": NOW, "claude_config_dir": os.environ.get("CLAUDE_CONFIG_DIR") or "(nicht gesetzt: ~/.claude)",
           "scopes": {}, "plugins": {}, "mcp": None}
    for scope, base in projects.items():
        c = base / ".claude"
        entry = {"base": str(base), "claude_md": (base / "CLAUDE.md").exists()}
        for f in ("settings.json", "settings.local.json"):
            s = settings_file(c / f)
            if s:
                entry[f] = s
        agents = sorted((c / "agents").glob("*.md")) if (c / "agents").exists() else []
        entry["agents"] = [{"file": a.name, "name": frontmatter(a).get("name"), "has_description": "description" in frontmatter(a),
                            "error": frontmatter(a).get("error")} for a in agents]
        skills = sorted((c / "skills").glob("*/SKILL.md")) if (c / "skills").exists() else []
        entry["skills"] = [{"dir": s.parent.name, "name": frontmatter(s).get("name"), "error": frontmatter(s).get("error")}
                           for s in skills]
        entry["mcp_json"] = (base / ".mcp.json").exists()
        inv["scopes"][scope] = entry
    ip = HOME / ".claude/plugins/installed_plugins.json"
    if ip.exists():
        d = json.loads(ip.read_text(encoding="utf8"))
        us = json.loads((HOME / ".claude/settings.json").read_text(encoding="utf8")).get("enabledPlugins", {})
        for k, v in d.get("plugins", {}).items():
            path = Path(v[0]["installPath"]) if v else None
            agents = sorted((path / "agents").glob("*.md")) if path and (path / "agents").exists() else []
            skills = sorted((path / "skills").glob("*/SKILL.md")) if path and (path / "skills").exists() else []
            inv["plugins"][k] = {"version": v[0].get("version") if v else None, "enabled": us.get(k),
                                 "agents": [{"file": a.name, "name": frontmatter(a).get("name"), "error": frontmatter(a).get("error")} for a in agents],
                                 "skills": [{"dir": s.parent.name, "name": frontmatter(s).get("name")} for s in skills],
                                 "hooks": (path / "hooks").exists() if path else False, "mcp_json": (path / ".mcp.json").exists() if path else False}
    if with_mcp:
        code, out = run(["claude", "mcp", "list"], timeout=240)
        servers = []
        for line in out.splitlines():
            m = re.match(r"^(.+?): (.+?) - (.+)$", line.strip())
            if m:
                servers.append({"name": m.group(1), "target": re.sub(r"(token|key|secret)=\S+", r"\1=***", m.group(2)),
                                "status": m.group(3)})
        inv["mcp"] = servers
    return inv


def canon_baseline():
    base = DESK / "Genesis-Games/canon_sources"
    files = {}
    if base.exists():
        for p in sorted(base.rglob("*")):
            if p.is_file():
                files[str(p.relative_to(base)).replace("\\", "/")] = hashlib.sha256(p.read_bytes()).hexdigest()
    code, out = run(["git", "status", "--short"], cwd=DESK / "Genesis-Games")
    code2, br = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=DESK / "Genesis-Games")
    return {"canon_root": str(base), "files": len(files), "sha256": files, "git_branch": br,
            "git_uncommitted": len([l for l in out.splitlines() if l.strip()])}


if __name__ == "__main__":
    with_mcp = "--mcp" in sys.argv
    (ROOT / "setup").mkdir(exist_ok=True)
    (ROOT / "audit").mkdir(exist_ok=True)
    hw, tl = hardware(), tools()
    inv = claude_inventory(with_mcp)
    canon = canon_baseline()
    (ROOT / "setup/hardware.json").write_text(json.dumps(hw, indent=1, ensure_ascii=False), encoding="utf8")
    (ROOT / "setup/tool-inventory.json").write_text(json.dumps({"timestamp": NOW, "tools": tl}, indent=1, ensure_ascii=False), encoding="utf8")
    (ROOT / "audit/claude-config-inventory.json").write_text(json.dumps(inv, indent=1, ensure_ascii=False), encoding="utf8")
    base = {"timestamp": NOW, "phase": "BASELINE_BEFORE_CHANGES", "canon_genesis": canon}
    (ROOT / "audit/claude-health-baseline.json").write_text(json.dumps(base, indent=1, ensure_ascii=False), encoding="utf8")
    print("DOCTOR", json.dumps({"tools_found": sum(v["found"] for v in tl.values()), "tools": len(tl),
                                "canon_files": canon["files"], "mcp": len(inv["mcp"] or [])}))
