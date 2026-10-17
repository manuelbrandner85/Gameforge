"""Echte Hardware-Erkennung (keine Annahmen). Ergebnisse werden kurz zwischengespeichert."""
from __future__ import annotations
import os, platform, shutil, subprocess, time

_cache = {}


def _run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors='replace', stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return -1, ''


def gpu_status():
    """GPU-Name, VRAM gesamt/belegt, Treiber über nvidia-smi. Für AMD/Intel: nur Name per WMI."""
    smi = shutil.which('nvidia-smi')
    if smi:
        code, out = _run([smi, '--query-gpu=name,memory.total,memory.used,driver_version,utilization.gpu',
                          '--format=csv,noheader,nounits'])
        if code == 0 and out.strip():
            gpus = []
            for line in out.strip().splitlines():
                p = [x.strip() for x in line.split(',')]
                if len(p) >= 5:
                    gpus.append({'vendor': 'NVIDIA', 'name': p[0], 'vram_total_mb': int(float(p[1])),
                                 'vram_used_mb': int(float(p[2])), 'driver': p[3], 'utilization_pct': int(float(p[4]))})
            if gpus:
                return {'checked': True, 'source': 'nvidia-smi', 'gpus': gpus}
    if os.name == 'nt':
        code, out = _run(['powershell', '-NoProfile', '-Command',
                          'Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + "|" + $_.DriverVersion }'])
        gpus = []
        for line in out.splitlines():
            if '|' in line:
                n, d = line.split('|', 1)
                vendor = 'AMD' if 'AMD' in n or 'Radeon' in n else 'Intel' if 'Intel' in n else 'NVIDIA' if 'NVIDIA' in n else 'Unbekannt'
                gpus.append({'vendor': vendor, 'name': n.strip(), 'driver': d.strip(), 'vram_total_mb': None, 'vram_used_mb': None})
        return {'checked': bool(gpus), 'source': 'WMI', 'gpus': gpus}
    return {'checked': False, 'source': None, 'gpus': []}


def system_info(base_dir, refresh=False):
    cached = _cache.get('sys')
    if cached and not refresh and time.time() - cached[0] < 300:
        info = dict(cached[1])
    else:
        ram = None
        if os.name == 'nt':
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [('l', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong), ('avail', ctypes.c_ulonglong),
                            ('tp', ctypes.c_ulonglong), ('ap', ctypes.c_ulonglong), ('tv', ctypes.c_ulonglong), ('av', ctypes.c_ulonglong), ('ae', ctypes.c_ulonglong)]
            m = MS(); m.l = ctypes.sizeof(MS)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                ram = {'total_gb': round(m.total / 1024**3, 1), 'free_gb': round(m.avail / 1024**3, 1)}
        cpu = platform.processor()
        if os.name == 'nt':
            code, out = _run(['powershell', '-NoProfile', '-Command', '(Get-CimInstance Win32_Processor).Name'])
            cpu = out.strip() or cpu
        info = {'os': platform.platform(), 'cpu': cpu, 'ram': ram}
        _cache['sys'] = (time.time(), info)
    du = shutil.disk_usage(base_dir)
    info['disk'] = {'path': str(base_dir), 'free_gb': round(du.free / 1024**3, 1), 'total_gb': round(du.total / 1024**3, 1)}
    info['gpu'] = gpu_status()
    return info
