"""GAMEFORGE Smart GPU Commander (Verbesserung 11 + Detailplan SMART_GPU_COMMANDER).

Für JEDES Spiel- und Filmprojekt. Grundsätze:
- GPU-Last (%) und VRAM-Füllstand werden getrennt gemessen. Was nicht messbar ist, heißt "unknown" – nie geschätzt.
- Nur EIN gpu_class="heavy"-Job von GAMEFORGE gleichzeitig pro physischer GPU (Sperrdatei, kompatibel mit gpu_lock.py).
- Vor einem Heavy-Job: freier VRAM >= Bedarf + Reserve (Standard 20 % des dedizierten Speichers, aus Messungen kalibriert).
  Ist der VRAM unbekannt: konservativer Modus – nur wenn keine fremde GPU-Anwendung erkannt wird.
- Offene Unreal-Editoren, Blender-Fenster oder ComfyUI werden erkannt und NIE geschlossen; GAMEFORGE wartet und sagt, wer belegt.
- Finale Qualität: versionierter Quality Contract mit SHA-256; Preview-Profile getrennt; keine automatische Reduktion.
"""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("GAMEFORGE_DATA_DIR") or ROOT / "GAMEFORGE_DATA")
LOCKS = DATA / "locks"
CALIB = DATA / "gpu_calibration.json"
RESERVE_DEFAULT = 0.20

# Bekannte GPU-Großverbraucher (Prozessname -> Anzeigename). Hintergrund-Blender (-b) zählt nur, wenn er von GAMEFORGE kommt.
GPU_APPS = {"unrealeditor": "Unreal Editor", "unrealeditor-cmd": "Unreal (Kommandozeile)", "blender": "Blender",
            "comfyui": "ComfyUI", "natronrenderer": "Natron", "davinci": "DaVinci Resolve"}

OOM_PATTERNS = [r"out of memory", r"CUDA_ERROR_OUT_OF_MEMORY", r"cudaErrorMemoryAllocation", r"OutOfVideoMemory",
                r"ran out of video memory", r"out of video memory", r"DXGI_ERROR_DEVICE_REMOVED", r"DXGI_ERROR_DEVICE_HUNG",
                r"GPU crashed", r"System is out of GPU memory", r"torch\.(cuda\.)?OutOfMemoryError", r"VK_ERROR_OUT_OF_DEVICE_MEMORY",
                r"over budget"]


def _run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace", stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return -1, ""


# ------------------------------------------------------------------ Messung
def measure():
    """Echte GPU-Messung. Nicht verfügbare Werte sind None (= unknown)."""
    fake = os.environ.get("GAMEFORGE_GPU_FAKE")                           # nur für automatische Tests
    if fake:
        return json.loads(fake)
    if os.environ.get("GAMEFORGE_GPU_SIMULATE_UNKNOWN") == "1":          # nur für Tests
        return {"vendor": "unknown", "name": None, "vram_total_mb": None, "vram_used_mb": None, "vram_free_mb": None,
                "util_pct": None, "temp_c": None, "driver": None, "source": "simuliert", "measured": False}
    smi = shutil.which("nvidia-smi")
    if smi:
        code, out = _run([smi, "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,driver_version",
                          "--format=csv,noheader,nounits"])
        if code == 0 and out.strip():
            p = [x.strip() for x in out.strip().splitlines()[0].split(",")]
            num = lambda v: None if not v or "N/A" in v else int(float(v))
            total, used = num(p[1]), num(p[2])
            return {"vendor": "NVIDIA", "name": p[0], "vram_total_mb": total, "vram_used_mb": used,
                    "vram_free_mb": (total - used) if total is not None and used is not None else None,
                    "util_pct": num(p[3]), "temp_c": num(p[4]), "driver": p[5], "source": "nvidia-smi", "measured": True}
    name = None
    if os.name == "nt":
        code, out = _run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name"])
        name = out.strip() or None
    vendor = "AMD" if name and ("AMD" in name or "Radeon" in name) else "Intel" if name and "Intel" in name else "unknown"
    # AMD/Intel: VRAM-Budget nicht seriös messbar ohne geprüfte DXGI-Abfrage -> unknown (konservativ seriell).
    return {"vendor": vendor, "name": name, "vram_total_mb": None, "vram_used_mb": None, "vram_free_mb": None,
            "util_pct": None, "temp_c": None, "driver": None, "source": "WMI (nur Name)", "measured": False}


def gpu_apps():
    """Laufende GPU-Großverbraucher, die NICHT von GAMEFORGE gestartet wurden (werden nie beendet)."""
    found = []
    if os.environ.get("GAMEFORGE_GPU_FAKE_APPS") is not None:             # nur für automatische Tests
        return json.loads(os.environ["GAMEFORGE_GPU_FAKE_APPS"])
    if os.name == "nt":
        code, out = _run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(UnrealEditor|blender|python|NatronRenderer|Resolve)' } | "
                          "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' + [int]($_.WorkingSetSize/1MB) + '|' + $_.CommandLine }"], timeout=20)
        for line in out.splitlines():
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            pid, name, ram, cmd = parts
            low, cmdl = name.lower().replace(".exe", ""), cmd.lower()
            if low == "python" or low == "pythonw":
                if "comfyui" in cmdl and "main.py" in cmdl:
                    found.append({"pid": int(pid), "app": "ComfyUI", "ram_mb": int(ram), "mode": "Server"})
                continue
            label = GPU_APPS.get(low)
            if not label:
                continue
            mode = "Hintergrund" if low == "blender" and (" -b " in f" {cmdl} " or "--background" in cmdl) else \
                   "Kommandozeile" if "-cmd" in low or "-run=" in cmdl else "Fenster (Editor)"
            found.append({"pid": int(pid), "app": label, "ram_mb": int(ram), "mode": mode})
    return found


# ------------------------------------------------------------------ Kalibrierung
def calibration():
    try:
        return json.loads(CALIB.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"reserve_fraction": RESERVE_DEFAULT, "jobs": {}}


def record_peak(job_type, peak_delta_mb):
    """Gemessenen VRAM-Mehrverbrauch eines Jobtyps speichern (gleitendes Maximum der letzten 10 Läufe)."""
    if peak_delta_mb is None:
        return
    c = calibration()
    hist = c["jobs"].setdefault(job_type, [])
    hist.append(int(peak_delta_mb))
    c["jobs"][job_type] = hist[-10:]
    DATA.mkdir(parents=True, exist_ok=True)
    CALIB.write_text(json.dumps(c, indent=2), encoding="utf-8")


def estimate_need(job_type, default_mb):
    hist = calibration()["jobs"].get(job_type)
    return max(hist) if hist else default_mb


def preflight(gpu_class, need_mb, m=None, apps=None):
    """Entscheidet, ob ein Job jetzt starten darf. Rückgabe: (ok, grund, details). Beendet nie fremde Programme."""
    if gpu_class != "heavy":
        return True, "kein GPU-Schwerjob", {}
    m = m or measure()
    apps = apps if apps is not None else gpu_apps()
    foreign = [a for a in apps if a["mode"] != "Hintergrund"]
    if not m["measured"] or m["vram_free_mb"] is None:
        if foreign:
            return False, "VRAM nicht messbar (unknown) und fremde GPU-Anwendung offen – konservativ warten: " + \
                   ", ".join(f'{a["app"]} ({a["mode"]})' for a in foreign), {"vram": "unknown", "apps": foreign}
        return True, "VRAM nicht messbar (unknown) – konservativer Modus: keine fremde GPU-Anwendung erkannt, ein Job seriell", {"vram": "unknown"}
    reserve = int(m["vram_total_mb"] * calibration().get("reserve_fraction", RESERVE_DEFAULT))
    required = need_mb + reserve
    if m["vram_free_mb"] < required:
        who = ", ".join(f'{a["app"]} ({a["mode"]}, PID {a["pid"]})' for a in foreign) or "unbekannte Prozesse"
        return False, (f'zu wenig VRAM frei: {m["vram_free_mb"]} MB frei, benötigt {need_mb} MB + {reserve} MB Reserve. '
                       f'Belegt durch: {who}. GAMEFORGE schließt nichts – bitte speichern und schließen oder warten.'), \
               {"free_mb": m["vram_free_mb"], "need_mb": need_mb, "reserve_mb": reserve, "apps": foreign}
    return True, f'{m["vram_free_mb"]} MB frei ≥ {need_mb} MB + {reserve} MB Reserve', {"free_mb": m["vram_free_mb"]}


# ------------------------------------------------------------------ Exklusives GPU-Token (kompatibel mit gpu_lock.py)
def _alive(pid):
    if os.name == "nt":
        code, out = _run(["tasklist", "/FI", f"PID eq {pid}", "/NH"])
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def lock_holder(resource="gpu"):
    lock = LOCKS / f"{resource}.lock"
    try:
        h = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    h["alive"] = _alive(h.get("pid", -1))
    return h


def try_acquire(name, resource="gpu", pid=None):
    """Einmaliger Versuch, das Token zu nehmen. Verwaiste Sperren (toter Prozess) werden übernommen und protokolliert."""
    LOCKS.mkdir(parents=True, exist_ok=True)
    lock = LOCKS / f"{resource}.lock"
    for _ in range(3):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"pid": pid or os.getpid(), "job": name, "since": time.time()}).encode())
            os.close(fd)
            return True
        except FileExistsError:
            h = lock_holder(resource)
            if h is None or not h["alive"]:
                with contextlib.suppress(OSError):
                    with (LOCKS / "verwaiste_sperren.log").open("a", encoding="utf-8") as f:
                        f.write(json.dumps({"at": time.time(), "lock": h}) + "\n")
                    lock.unlink()
                continue
            return False
    return False


def release(resource="gpu", pid=None):
    lock = LOCKS / f"{resource}.lock"
    h = lock_holder(resource)
    if h and h.get("pid") == (pid or os.getpid()):
        lock.unlink(missing_ok=True)


@contextlib.contextmanager
def gpu_slot(name, gpu_class="heavy", need_mb=4000, timeout_s=3600, poll_s=15, on_wait=None, make_room=None):
    """Kontext: wartet auf Token UND VRAM-Freigabe. Bei Zeitablauf: RuntimeError('RESOURCE_BLOCKED: …').
    make_room: optionaler Rückruf, der einmalig NUR eigene Zwischenspeicher leeren darf (z. B. ComfyUI-Modelle entladen,
    wenn dessen Warteschlange leer ist). Fremde Programme werden nie beendet."""
    if gpu_class != "heavy":
        yield {"gpu_class": gpu_class}
        return
    start = time.time()
    while not try_acquire(name):
        h = lock_holder() or {}
        if on_wait:
            on_wait(f'GPU-Token belegt durch GAMEFORGE-Job „{h.get("job")}“ (PID {h.get("pid")})')
        if time.time() - start > timeout_s:
            raise RuntimeError(f'RESOURCE_BLOCKED: GPU-Token seit {int(time.time() - start)} s belegt durch {h.get("job")}')
        time.sleep(poll_s)
    try:
        while True:
            ok, why, det = preflight(gpu_class, need_mb)
            if ok:
                break
            if make_room:
                room, make_room = make_room, None
                if room():
                    time.sleep(3)
                    continue
            if on_wait:
                on_wait(why)
            if time.time() - start > timeout_s:
                raise RuntimeError("RESOURCE_BLOCKED: " + why)
            time.sleep(poll_s)
        yield {"gpu_class": gpu_class, "preflight": why, "before": measure()}
    finally:
        release()


# ------------------------------------------------------------------ OOM-Erkennung
def detect_oom(*texts):
    blob = "\n".join(t or "" for t in texts)
    for pat in OOM_PATTERNS:
        m = re.search(pat, blob, re.I)
        if m:
            line = blob[max(0, blob.rfind("\n", 0, m.start()) + 1): blob.find("\n", m.end()) if blob.find("\n", m.end()) > 0 else len(blob)]
            return {"oom": True, "pattern": pat, "line": line.strip()[:300]}
    return {"oom": False}


# ------------------------------------------------------------------ Quality Contract (Final vs. Preview)
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lock_contract(path):
    """Final-Vertrag sperren: locked=true, allow_automatic_quality_reduction=false, SHA-256 in <name>.sha256 festhalten."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("profile", "final") != "final":
        raise ValueError("Nur Final-Profile werden gesperrt; Preview-Profile sind getrennte Dateien.")
    data["locked"] = True
    data["allow_automatic_quality_reduction"] = False
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    digest = sha256_file(p)
    p.with_suffix(p.suffix + ".sha256").write_text(digest + "\n", encoding="utf-8")
    return digest


def verify_contract(path):
    """True nur, wenn der Final-Vertrag gesperrt ist und seine Prüfsumme der gesperrten entspricht."""
    p = Path(path)
    ref = p.with_suffix(p.suffix + ".sha256")
    if not p.is_file() or not ref.is_file():
        return False, "Kein gesperrter Final-Vertrag (Datei oder .sha256 fehlt)."
    data = json.loads(p.read_text(encoding="utf-8"))
    if not data.get("locked") or data.get("allow_automatic_quality_reduction"):
        return False, "Final-Vertrag ist nicht gesperrt."
    cur, want = sha256_file(p), ref.read_text(encoding="utf-8").strip()
    if cur != want:
        return False, f"Final-Vertrag wurde verändert (SHA-256 {cur[:12]}… ≠ gesperrt {want[:12]}…) – Job gestoppt."
    return True, want


def make_preview(final_path, preview_path, **overrides):
    """Preview-Profil als GETRENNTE Datei aus dem Final-Vertrag ableiten. Das Final-Profil bleibt byte-identisch."""
    fp, pp = Path(final_path), Path(preview_path)
    if fp.resolve() == pp.resolve():
        raise ValueError("Preview darf nicht in die Final-Vertragsdatei schreiben.")
    before = sha256_file(fp)
    data = json.loads(fp.read_text(encoding="utf-8"))
    data.update(overrides)
    data.update({"profile": "preview", "locked": False, "derived_from": fp.name, "derived_from_sha256": before})
    pp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if sha256_file(fp) != before:
        raise RuntimeError("Final-Vertrag hat sich beim Ableiten verändert – abgebrochen.")
    return pp


def media_info(path):
    """Echte Maße einer Ausgabedatei: PNG/JPG direkt aus dem Dateikopf, Video über ffprobe (falls vorhanden)."""
    import struct
    p = Path(path)
    head = p.read_bytes()[:32] if p.is_file() else b""
    if head[:8] == bytes.fromhex("89504e470d0a1a0a"):
        w, h = struct.unpack(">II", head[16:24])
        return {"width": w, "height": h, "fps": None}
    probe = shutil.which("ffprobe")
    if probe and p.suffix.lower() in (".mp4", ".mov", ".mkv", ".exr", ".jpg", ".jpeg", ".webm"):
        code, out = _run([probe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "json", str(p)], timeout=60)
        try:
            st = json.loads(out)["streams"][0]
            num, den = (st.get("r_frame_rate") or "0/1").split("/")
            return {"width": st["width"], "height": st["height"], "fps": round(int(num) / int(den), 3) if int(den) else None}
        except (ValueError, KeyError, IndexError, ZeroDivisionError):
            pass
    return None


def check_against_contract(paths, contract_path):
    """Final-Ausgaben gegen den gesperrten Vertrag prüfen (Auflösung, FPS). Abweichung = FAIL, nie stillschweigend akzeptiert."""
    c = json.loads(Path(contract_path).read_text(encoding="utf-8"))
    want = c.get("master_resolution") or {}
    problems, checked = [], 0
    for p in paths:
        info = media_info(p)
        if not info:
            continue
        checked += 1
        if want and (info["width"], info["height"]) != (want.get("width"), want.get("height")):
            problems.append(f'{Path(p).name}: {info["width"]}×{info["height"]} statt {want.get("width")}×{want.get("height")}')
        if c.get("fps") and info.get("fps") and abs(info["fps"] - c["fps"]) > 0.01:
            problems.append(f'{Path(p).name}: {info["fps"]} fps statt {c["fps"]}')
    return {"ok": not problems, "checked": checked, "problems": problems}


def status_text():
    m = measure()
    apps = gpu_apps()
    h = lock_holder()
    lines = ["== GAMEFORGE Smart GPU Commander =="]
    if m["measured"]:
        lines.append(f'{m["name"]} · VRAM {m["vram_used_mb"]}/{m["vram_total_mb"]} MB belegt ({m["vram_free_mb"]} MB frei) · '
                     f'Last {m["util_pct"]} % · {m["temp_c"]} °C · Treiber {m["driver"]}')
    else:
        lines.append(f'{m["name"] or "GPU unbekannt"} · VRAM: unknown (nicht messbar) → konservativer Modus, Jobs strikt nacheinander')
    c = calibration()
    reserve = int((m["vram_total_mb"] or 0) * c.get("reserve_fraction", RESERVE_DEFAULT)) if m["vram_total_mb"] else None
    lines.append(f'Sicherheitsreserve: {reserve} MB ({int(c.get("reserve_fraction", RESERVE_DEFAULT) * 100)} %)' if reserve else "Sicherheitsreserve: unknown")
    lines.append("GAMEFORGE-GPU-Token: " + (f'belegt durch „{h["job"]}“ (PID {h["pid"]}, {"läuft" if h["alive"] else "verwaist"})' if h else "frei"))
    lines.append("Andere GPU-Programme (werden nie beendet): " + (", ".join(f'{a["app"]} [{a["mode"]}, PID {a["pid"]}, {a["ram_mb"]} MB RAM]' for a in apps) or "keine erkannt"))
    if c["jobs"]:
        lines.append("Gemessener VRAM-Bedarf je Jobtyp: " + ", ".join(f"{k}: max {max(v)} MB" for k, v in c["jobs"].items()))
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(status_text() if sys.argv[1:] in ([], ["status"]) else json.dumps(measure(), indent=2))
