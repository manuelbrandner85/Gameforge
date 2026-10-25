"""GAMEFORGE Job-Kern (Verbesserungen 04 Production Commander, 10 QA, 13 Self-Healing; GPU über gpu_commander).

EIN gemeinsamer, persistenter Auftragskern für alle Spiel- und Filmprojekte:
- SQLite (WAL) unter GAMEFORGE_DATA/gameforge_core.sqlite3 – übersteht Neustarts.
- Aufträge sind Programmaufrufe (argv, nie Shell-Text) mit erwarteten Artefakten, Projekt, GPU-Klasse und Profil.
- Idempotent: gleicher idem_key -> kein doppelter Auftrag; vorhandene, geprüfte Artefakte werden nicht überschrieben.
- Projektisolation: Arbeitsordner und Artefakte müssen im Ordner des angegebenen Projekts liegen.
- GPU-Schwerjobs nur über das Smart-GPU-Token; Speicherüberlauf -> BLOCKED (nie stille Qualitätsreduktion).
- Status nur aus echten Ereignissen: Exitcode, Logdateien, vorhandene Dateien mit SHA-256.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import sqlite3
import subprocess
import threading
import time
import uuid
from pathlib import Path

from . import gpu_commander as gpu

DB = gpu.DATA / "gameforge_core.sqlite3"
LOGS = gpu.DATA / "jobs"
STATES = ("queued", "waiting", "running", "passed", "needs_review", "failed", "blocked", "cancelled")
SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs(
  id TEXT PRIMARY KEY, project TEXT NOT NULL, project_root TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL,
  argv TEXT NOT NULL, cwd TEXT NOT NULL, expected TEXT NOT NULL, gpu_class TEXT NOT NULL, need_mb INTEGER,
  profile TEXT NOT NULL, contract TEXT, contract_sha TEXT, depends TEXT NOT NULL DEFAULT '[]', idem_key TEXT UNIQUE,
  status TEXT NOT NULL, reason TEXT NOT NULL DEFAULT '', error_class TEXT NOT NULL DEFAULT '', attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 2, timeout_s INTEGER NOT NULL DEFAULT 7200, pid INTEGER, worker TEXT,
  created_at TEXT NOT NULL, started_at TEXT, ended_at TEXT, not_before REAL NOT NULL DEFAULT 0,
  artifacts TEXT NOT NULL DEFAULT '[]', peak_vram_mb INTEGER, exit_code INTEGER);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT, at TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL);
"""


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


_local = threading.local()
_all = []
_all_lock = threading.Lock()


def connect():
    """Eine wiederverwendete Verbindung pro Thread (sonst bleiben unter Windows Dateisperren offen)."""
    con = getattr(_local, "con", None)
    if con is not None and getattr(_local, "db", None) == str(DB):
        return con
    gpu.DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=30, isolation_level=None, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    _local.con, _local.db = con, str(DB)
    with _all_lock:
        _all.append(con)
    return con


def close_all():
    with _all_lock:
        for c in _all:
            try:
                c.close()
            except sqlite3.Error:
                pass
        _all.clear()
    _local.con = None


def event(con, job_id, kind, detail):
    con.execute("INSERT INTO events(job_id,at,kind,detail) VALUES(?,?,?,?)", (job_id, now(), kind, json.dumps(detail, ensure_ascii=False)[:4000]))


def _inside(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def submit(project, project_root, kind, title, argv, cwd, expected, gpu_class="none", need_mb=None, profile="none",
           contract=None, depends=(), idem_key=None, max_attempts=2, timeout_s=7200):
    """Neuen Auftrag einreihen. Gibt (job, neu?) zurück. Lehnt projektfremde Pfade ab (INVALID_INPUT)."""
    if gpu_class not in ("heavy", "light", "none"):
        raise ValueError("INVALID_INPUT: gpu_class muss heavy, light oder none sein")
    if profile not in ("final", "preview", "none"):
        raise ValueError("INVALID_INPUT: profile muss final, preview oder none sein")
    root = Path(project_root)
    if not root.is_dir():
        raise ValueError(f"INVALID_INPUT: Projektordner {root} existiert nicht")
    for p in [cwd, *expected]:
        if not _inside(p if Path(p).is_absolute() else root / p, root):
            raise ValueError(f"INVALID_INPUT: {p} liegt nicht im Projekt „{project}“ – Projekte bleiben getrennt")
    if not argv or not isinstance(argv, (list, tuple)):
        raise ValueError("INVALID_INPUT: argv muss eine Liste sein (keine Shell-Befehle)")
    contract_sha = None
    if profile == "final":
        if not contract:
            raise ValueError("INVALID_INPUT: Final-Aufträge brauchen einen gesperrten Quality Contract")
        ok, info = gpu.verify_contract(contract)
        if not ok:
            raise ValueError("INVALID_INPUT: " + info)
        contract_sha = info
    con = connect()
    if idem_key:
        row = con.execute("SELECT * FROM jobs WHERE idem_key=?", (idem_key,)).fetchone()
        if row:
            if row["project"] != project:
                raise ValueError("INVALID_INPUT: gleicher Auftragsschlüssel gehört zu anderem Projekt")
            return dict(row), False
    jid = uuid.uuid4().hex[:12]
    con.execute("""INSERT INTO jobs(id,project,project_root,kind,title,argv,cwd,expected,gpu_class,need_mb,profile,contract,contract_sha,
                   depends,idem_key,status,max_attempts,timeout_s,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (jid, project, str(root.resolve()), kind, title, json.dumps(list(argv)), str(Path(cwd).resolve()),
                 json.dumps([str(Path(p) if Path(p).is_absolute() else root / p) for p in expected]), gpu_class, need_mb, profile,
                 str(Path(contract).resolve()) if contract else None, contract_sha, json.dumps(list(depends)), idem_key, "queued",
                 max_attempts, timeout_s, now()))
    event(con, jid, "submitted", {"title": title, "kind": kind, "gpu_class": gpu_class, "profile": profile})
    return get(jid), True


def get(jid):
    row = connect().execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
    return dict(row) if row else None


def listing(project=None, limit=50):
    con = connect()
    q = "SELECT * FROM jobs" + (" WHERE project=?" if project else "") + " ORDER BY created_at DESC LIMIT ?"
    return [dict(r) for r in con.execute(q, (project, limit) if project else (limit,))]


def recover():
    """Self-Healing: Aufträge mit totem Prozess nach Neustart wieder einreihen (Artefakte bleiben, Idempotenz prüft sie)."""
    con = connect()
    n = 0
    for r in con.execute("SELECT * FROM jobs WHERE status IN ('running','waiting')").fetchall():
        if not r["pid"] or not gpu._alive(r["pid"]):
            con.execute("UPDATE jobs SET status='queued', reason='nach Abbruch/Neustart wieder eingereiht', pid=NULL WHERE id=?", (r["id"],))
            event(con, r["id"], "recovered", {"old_status": r["status"], "pid": r["pid"]})
            n += 1
    return n


def cancel(jid):
    con = connect()
    r = get(jid)
    if not r:
        raise ValueError("Auftrag nicht gefunden")
    if r["status"] in ("queued", "waiting", "failed", "blocked"):
        con.execute("UPDATE jobs SET status='cancelled', reason='vom Nutzer abgebrochen', ended_at=? WHERE id=?", (now(), jid))
        event(con, jid, "cancelled", {})
        return True
    raise ValueError(f"Auftrag im Status {r['status']} kann nicht abgebrochen werden")


def retry(jid):
    con = connect()
    r = get(jid)
    if r["status"] not in ("failed", "blocked", "cancelled"):
        raise ValueError("Nur fehlgeschlagene, blockierte oder abgebrochene Aufträge können erneut eingereiht werden")
    con.execute("UPDATE jobs SET status='queued', reason='erneut eingereiht', error_class='', attempts=0, not_before=0 WHERE id=?", (jid,))
    event(con, jid, "retry", {})


def _artifacts(paths):
    out = []
    for p in paths:
        fp = Path(p)
        out.append({"path": str(fp), "exists": fp.is_file(), "size": fp.stat().st_size if fp.is_file() else 0,
                    "sha256": gpu.sha256_file(fp) if fp.is_file() and fp.stat().st_size else None})
    return out


def _already_done(r):
    """Idempotenz: gleicher Auftrag lief bereits erfolgreich und alle Artefakte sind unverändert vorhanden."""
    prev = json.loads(r["artifacts"] or "[]")
    if not prev or r["status"] not in ("queued",) or not all(a.get("sha256") for a in prev):
        return False
    return all(Path(a["path"]).is_file() and gpu.sha256_file(a["path"]) == a["sha256"] for a in prev)


def _deps_ready(con, r):
    deps = json.loads(r["depends"] or "[]")
    if not deps:
        return True, ""
    rows = {x["id"]: x["status"] for x in con.execute(f"SELECT id,status FROM jobs WHERE id IN ({','.join('?' * len(deps))})", deps)}
    bad = [d for d in deps if rows.get(d) in ("failed", "blocked", "cancelled")]
    if bad:
        return None, f"Abhängigkeit fehlgeschlagen/blockiert: {', '.join(bad)}"
    return all(rows.get(d) in ("passed", "needs_review") for d in deps), "wartet auf Abhängigkeiten"


def run_one(worker="worker", on_wait=None):
    """Nächsten startbereiten Auftrag ausführen. Rückgabe: Job-Dict oder None (nichts zu tun)."""
    con = connect()
    recover()
    for r in con.execute("SELECT * FROM jobs WHERE status='queued' AND not_before<=? ORDER BY created_at", (time.time(),)).fetchall():
        ready, why = _deps_ready(con, r)
        if ready is None:
            con.execute("UPDATE jobs SET status='blocked', error_class='INVALID_INPUT', reason=? WHERE id=?", (why, r["id"]))
            event(con, r["id"], "blocked", {"reason": why})
            continue
        if not ready:
            continue
        # Atomar beanspruchen (mehrere Worker möglich)
        cur = con.execute("UPDATE jobs SET status='waiting', worker=?, pid=? WHERE id=? AND status='queued'", (worker, os.getpid(), r["id"]))
        if cur.rowcount != 1:
            continue
        return _execute(con, dict(r), worker, on_wait)
    return None


def _execute(con, r, worker, on_wait):
    jid = r["id"]
    expected = json.loads(r["expected"])
    if _already_done(r):
        con.execute("UPDATE jobs SET status='passed', reason='Artefakte bereits vorhanden und unverändert – nicht erneut erzeugt', ended_at=? WHERE id=?", (now(), jid))
        event(con, jid, "skipped_idempotent", {})
        return get(jid)
    logdir = LOGS / jid
    logdir.mkdir(parents=True, exist_ok=True)
    need = r["need_mb"] or gpu.estimate_need(r["kind"], 4000)
    try:
        with gpu.gpu_slot(f'{r["project"]}:{r["title"]}', r["gpu_class"], need, timeout_s=min(r["timeout_s"], 3600),
                          on_wait=lambda msg: (con.execute("UPDATE jobs SET reason=? WHERE id=?", (msg, jid)), on_wait and on_wait(msg))) as slot:
            if r["profile"] == "final":
                ok, info = gpu.verify_contract(r["contract"])
                if not ok or info != r["contract_sha"]:
                    raise RuntimeError("QA_FAILED: " + (info if not ok else "Final-Vertrag weicht vom freigegebenen Stand ab"))
            before = slot.get("before") or {}
            con.execute("UPDATE jobs SET status='running', started_at=?, attempts=attempts+1, reason='läuft' WHERE id=?", (now(), jid))
            event(con, jid, "started", {"preflight": slot.get("preflight"), "vram_before": before.get("vram_used_mb")})
            out_f, err_f = open(logdir / "stdout.log", "w", encoding="utf-8", errors="replace"), open(logdir / "stderr.log", "w", encoding="utf-8", errors="replace")
            try:
                proc = subprocess.Popen(json.loads(r["argv"]), cwd=r["cwd"], stdout=out_f, stderr=err_f, stdin=subprocess.DEVNULL)
            except OSError as e:
                out_f.close(); err_f.close()
                raise RuntimeError(f"UNAVAILABLE: Programm nicht startbar ({e}) – Werkzeug fehlt oder Pfad falsch")
            con.execute("UPDATE jobs SET pid=? WHERE id=?", (proc.pid, jid))
            peak = [before.get("vram_used_mb")]
            stop = threading.Event()

            def sample():
                while not stop.wait(2):
                    m = gpu.measure()
                    if m["vram_used_mb"] is not None:
                        peak[0] = max(peak[0] or 0, m["vram_used_mb"])
            t = threading.Thread(target=sample, daemon=True)
            if r["gpu_class"] == "heavy":
                t.start()
            try:
                code = proc.wait(timeout=r["timeout_s"])
            except subprocess.TimeoutExpired:
                proc.kill()
                code = -9
            stop.set()
            out_f.close(); err_f.close()
            if r["profile"] == "final":
                ok, info = gpu.verify_contract(r["contract"])
                if not ok or info != r["contract_sha"]:
                    raise RuntimeError("QA_FAILED: Final-Vertrag hat sich während des Auftrags verändert")
    except RuntimeError as e:
        cls = str(e).split(":", 1)[0] if ":" in str(e) else "EXECUTION_FAILED"
        status = "blocked" if cls in ("RESOURCE_BLOCKED", "UNAVAILABLE", "LICENSE_BLOCKED") else "failed"
        con.execute("UPDATE jobs SET status=?, error_class=?, reason=?, ended_at=? WHERE id=?", (status, cls, str(e)[:900], now(), jid))
        event(con, jid, status, {"reason": str(e)[:900]})
        return get(jid)
    stdout = (logdir / "stdout.log").read_text(encoding="utf-8", errors="replace")[-200000:]
    stderr = (logdir / "stderr.log").read_text(encoding="utf-8", errors="replace")[-200000:]
    oom = gpu.detect_oom(stdout, stderr)
    delta = (peak[0] - before["vram_used_mb"]) if peak[0] is not None and before.get("vram_used_mb") is not None else None
    if r["gpu_class"] == "heavy" and delta is not None and code == 0:
        gpu.record_peak(r["kind"], max(delta, 0))
    arts = _artifacts(expected)
    (logdir / "artifacts.json").write_text(json.dumps(arts, indent=2), encoding="utf-8")
    if oom["oom"]:
        status, cls, reason = "blocked", "RESOURCE_BLOCKED", ("Speicherüberlauf (OOM) erkannt: " + oom["line"] +
                  " – Qualität wird NICHT automatisch reduziert. Optionen: andere GPU-Programme schließen und erneut versuchen, "
                  "Shot/Frames in kleineren Teilen rendern, CPU-Render nach Freigabe.")
    elif code != 0:
        r2 = get(jid)
        if r2["attempts"] < r["max_attempts"]:
            backoff = 30 * (2 ** (r2["attempts"] - 1))
            con.execute("UPDATE jobs SET status='queued', exit_code=?, error_class='EXECUTION_FAILED', reason=?, not_before=?, artifacts=? WHERE id=?",
                        (code, f"Exitcode {code} – neuer Versuch in {backoff} s", time.time() + backoff, json.dumps(arts), jid))
            event(con, jid, "retry_scheduled", {"exit": code, "backoff_s": backoff})
            return get(jid)
        status, cls, reason = "failed", "EXECUTION_FAILED", f"Exitcode {code} nach {r2['attempts']} Versuchen – Logs: {logdir}"
    elif not all(a["exists"] and a["size"] > 0 for a in arts):
        missing = [a["path"] for a in arts if not (a["exists"] and a["size"] > 0)]
        status, cls, reason = "failed", "QA_FAILED", "Programm meldete Erfolg, aber Artefakte fehlen/leer: " + ", ".join(missing)
    elif r["profile"] == "final" and not (qa := gpu.check_against_contract([a["path"] for a in arts], r["contract"]))["ok"]:
        status, cls, reason = "failed", "QA_FAILED", "Ausgabe entspricht nicht dem Final-Vertrag: " + "; ".join(qa["problems"])
    else:
        status, cls = ("needs_review" if r["profile"] == "final" else "passed"), ""
        reason = "fertig – Artefakte geprüft" + (" (Final: wartet auf deine Sichtabnahme)" if r["profile"] == "final" else "")
    con.execute("UPDATE jobs SET status=?, error_class=?, reason=?, exit_code=?, ended_at=?, artifacts=?, peak_vram_mb=? WHERE id=?",
                (status, cls, reason, code, now(), json.dumps(arts), peak[0], jid))
    event(con, jid, status, {"exit": code, "oom": oom, "peak_vram_mb": peak[0], "vram_delta_mb": delta})
    (logdir / "validation.json").write_text(json.dumps({"status": status, "error_class": cls, "reason": reason, "exit": code,
                                                         "oom": oom, "peak_vram_mb": peak[0], "vram_delta_mb": delta,
                                                         "artifacts": arts, "at": now()}, indent=2, ensure_ascii=False), encoding="utf-8")
    return get(jid)


def work(worker="worker", on_wait=None, on_done=None, max_idle_s=600):
    """Arbeitet die Warteschlange ab, ein Auftrag nach dem anderen. Endet, wenn nichts mehr startbar ist."""
    done, idle_since = 0, None
    while True:
        j = run_one(worker, on_wait)
        if j is not None:
            done, idle_since = done + 1, None
            if on_done:
                on_done(j)
            continue
        con = connect()
        queued = con.execute("SELECT MIN(not_before) m, COUNT(*) n FROM jobs WHERE status='queued'").fetchone()
        running = con.execute("SELECT COUNT(*) n FROM jobs WHERE status IN ('running','waiting')").fetchone()["n"]
        if not queued["n"]:
            return done
        if queued["m"] > time.time():                       # geplanter Wiederholversuch
            time.sleep(min(30, queued["m"] - time.time()))
            continue
        if not running:                                     # nur noch Aufträge mit offenen Abhängigkeiten, die nie fertig werden
            return done
        idle_since = idle_since or time.time()
        if time.time() - idle_since > max_idle_s:
            return done
        time.sleep(5)
