"""GAMEFORGE RenderFarmLocal (audit fund H-04): one GPU job at a time, only with enough free VRAM.

Several Claude sessions share one RTX 5070 (12 GB), one Blender and Unreal editors. A GPU job takes a lock file under
GAMEFORGE_DATA/locks (exclusive create, holder PID + job name + time), waits while another live holder exists, and
starts only when nvidia-smi reports at least `need_mb` free VRAM. Stale locks (dead PID) are taken over.
Other sessions are never killed or paused - they just are not run in parallel by GAMEFORGE.

    from gameforge_core.gpu_lock import gpu_job
    with gpu_job("ue_smoke", need_mb=6000):
        ...
CLI:  python gameforge_core/gpu_lock.py status
"""
import contextlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

LOCKS = Path(__file__).resolve().parents[1] / "GAMEFORGE_DATA/locks"


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.split(",")
    used, total, util = (int(x) for x in out)
    return {"used_mb": used, "total_mb": total, "free_mb": total - used, "util_pct": util}


def _alive(pid):
    r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True)
    return str(pid) in r.stdout


@contextlib.contextmanager
def gpu_job(name, need_mb=4000, timeout_s=3600, poll_s=20, resource="gpu"):
    LOCKS.mkdir(parents=True, exist_ok=True)
    lock = LOCKS / f"{resource}.lock"
    start = time.time()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"pid": os.getpid(), "job": name, "since": time.time()}).encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                holder = json.loads(lock.read_text())
                if not _alive(holder["pid"]):
                    lock.unlink(missing_ok=True)            # stale lock of a dead process
                    continue
            except (ValueError, KeyError, OSError):
                lock.unlink(missing_ok=True)
                continue
        if time.time() - start > timeout_s:
            raise TimeoutError(f"{resource} belegt durch {lock.read_text()}")
        time.sleep(poll_s)
    try:
        while vram()["free_mb"] < need_mb:                   # other (non-GAMEFORGE) GPU users
            if time.time() - start > timeout_s:
                raise TimeoutError(f"zu wenig VRAM frei: {vram()}")
            time.sleep(poll_s)
        yield vram()
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__" and sys.argv[1:] == ["status"]:
    print(json.dumps({"vram": vram(), "locks": [p.name for p in LOCKS.glob("*.lock")] if LOCKS.exists() else []}))
