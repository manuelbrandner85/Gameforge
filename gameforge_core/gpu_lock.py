"""Kompatibilitäts-Hülle (Phase 0, Fund H-04): leitet auf den Smart GPU Commander weiter.

Gleiche Sperrdatei (GAMEFORGE_DATA/locks/gpu.lock) und gleiche API wie zuvor, damit ältere Skripte unverändert laufen:
    from gameforge_core.gpu_lock import gpu_job
    with gpu_job("ue_smoke", need_mb=6000): ...
"""
import contextlib
import json
import sys

try:
    from . import gpu_commander as _gc
except ImportError:                                   # direkter Aufruf als Skript
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from gameforge_core import gpu_commander as _gc

LOCKS = _gc.LOCKS


def vram():
    m = _gc.measure()
    return {"used_mb": m["vram_used_mb"], "total_mb": m["vram_total_mb"], "free_mb": m["vram_free_mb"], "util_pct": m["util_pct"]}


@contextlib.contextmanager
def gpu_job(name, need_mb=4000, timeout_s=3600, poll_s=20, resource="gpu"):
    with _gc.gpu_slot(name, "heavy", need_mb, timeout_s=timeout_s, poll_s=poll_s):
        yield vram()


if __name__ == "__main__" and sys.argv[1:] == ["status"]:
    print(json.dumps({"vram": vram(), "locks": [p.name for p in LOCKS.glob("*.lock")] if LOCKS.exists() else []}))
