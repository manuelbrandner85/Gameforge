"""Godot-Brücke: Godot 4 (MIT, kostenlos) als zweite Spiel-Engine neben Unreal.

- Godot hat eine vollwertige Kommandozeile (--headless, --path, --import, -e). Damit erledigt Python
  Einrichten, Import und Prüfung; im Editor arbeitet Claude über den Godot-MCP (@coding-solo/godot-mcp, MIT, lokal).
- Installation nur nach Zustimmung: offizielles GitHub-Release, SHA512-geprüft, in GAMEFORGE_DATA/tools/godot/.
- Nichts gilt als importiert/geprüft, solange Godot es nicht selbst ohne Fehler eingelesen hat.
"""
from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, urllib.request, zipfile
from pathlib import Path

VERSION = '4.7.1'
RELEASE = f'https://github.com/godotengine/godot/releases/download/{VERSION}-stable'
ZIP = f'Godot_v{VERSION}-stable_win64.exe.zip'
MCP_PACKAGE = '@coding-solo/godot-mcp@0.1.1'
MODEL_EXT = ('.glb', '.gltf', '.fbx', '.obj', '.blend')

# Grundeinstellungen je Ausrichtung. 3D = höchste sinnvolle Qualität (Forward+, Jolt, MSAA 4x, große weiche Schatten).
PROFILES = {
    '3d': {'renderer': 'forward_plus', 'feature': 'Forward Plus', 'extra': [
        ('physics', '3d/physics_engine="Jolt Physics"'),
        ('rendering', 'anti_aliasing/quality/msaa_3d=2'),
        ('rendering', 'lights_and_shadows/directional_shadow/size=8192'),
        ('rendering', 'lights_and_shadows/directional_shadow/soft_shadow_filter_quality=4'),
    ]},
    '2d': {'renderer': 'forward_plus', 'feature': 'Forward Plus', 'extra': []},
    'pixel': {'renderer': 'forward_plus', 'feature': 'Forward Plus', 'extra': [
        ('rendering', 'textures/canvas_textures/default_texture_filter=0'),
        ('display', 'window/stretch/mode="viewport"'),
    ]},
    'web': {'renderer': 'gl_compatibility', 'feature': 'GL Compatibility', 'extra': []},
}


def _candidates(data: Path):
    if os.environ.get('GODOT_PATH'):
        yield Path(os.environ['GODOT_PATH'])
    yield from sorted((data / 'tools' / 'godot').glob('*/Godot_v*_win64.exe'), reverse=True)
    w = shutil.which('godot') or shutil.which('godot4')
    if w:
        yield Path(w)
    for base in (os.environ.get('ProgramFiles', r'C:\Program Files'), os.environ.get('LOCALAPPDATA', ''),
                 r'C:\Program Files (x86)\Steam\steamapps\common'):
        if base:
            yield from sorted(Path(base).glob('Godot*/Godot_v*win64.exe'), reverse=True)
            yield from sorted(Path(base).glob('Godot*/godot.windows.*.exe'), reverse=True)


def find_exe(data: Path):
    """Godot-Programm (Fensterfassung, nicht _console)."""
    for p in _candidates(data):
        if p.is_file() and not p.stem.endswith('_console'):
            return p
    return None


def console_exe(exe: Path) -> Path:
    """Die _console-Fassung liefert Ausgaben ins Terminal (für Prüfungen)."""
    c = exe.with_name(exe.stem + '_console.exe')
    return c if c.is_file() else exe


def version(exe: Path):
    try:
        r = subprocess.run([str(console_exe(exe)), '--version'], capture_output=True, text=True, timeout=60, errors='replace')
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (r.stdout.strip().splitlines() or [None])[-1]


def running():
    """PIDs laufender Godot-Fenster (nur lesen)."""
    if os.name != 'nt':
        return []
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              "Get-Process | Where-Object { $_.ProcessName -like 'Godot*' -and $_.MainWindowTitle -ne '' } | ForEach-Object { $_.Id }"],
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [int(x) for x in out.split() if x.isdigit()]


def _get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'GAMEFORGE'}), timeout=timeout)


def expected_sha512(sums_text: str, name: str):
    for line in sums_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip('*') == name:
            return parts[0].lower()
    return None


def install(data: Path, max_mb=200, fetch=_get):
    """Lädt das offizielle Release, prüft SHA512 und entpackt nach GAMEFORGE_DATA/tools/godot/<Version>/."""
    dest = data / 'tools' / 'godot' / VERSION
    have = sorted(dest.glob('Godot_v*_win64.exe'))
    if have:
        return have[0], False
    want = expected_sha512(fetch(f'{RELEASE}/SHA512-SUMS.txt').read().decode(), ZIP)
    if not want:
        raise ValueError(f'{ZIP} steht nicht in SHA512-SUMS.txt – Abbruch, nichts installiert.')
    tmp = data / 'tmp' / ZIP
    tmp.parent.mkdir(parents=True, exist_ok=True)
    h, size = hashlib.sha512(), 0
    with fetch(f'{RELEASE}/{ZIP}', timeout=600) as r, open(tmp, 'wb') as f:
        for chunk in iter(lambda: r.read(1 << 20), b''):
            size += len(chunk)
            if size > max_mb * 1e6:
                f.close(); tmp.unlink()
                raise ValueError(f'Download größer als {max_mb} MB – abgebrochen.')
            h.update(chunk); f.write(chunk)
    if h.hexdigest() != want:
        tmp.unlink()
        raise ValueError('Prüfsumme stimmt nicht (SHA512) – Datei verworfen, nichts installiert.')
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(tmp) as z:
        for n in z.namelist():                      # nur flache .exe-Dateien, keine Pfade aus dem Archiv übernehmen
            if n.lower().endswith('.exe') and '/' not in n.strip('/') and '..' not in n:
                (dest / n).write_bytes(z.read(n))
    tmp.unlink()
    exe = next(iter(sorted(p for p in dest.glob('Godot_v*_win64.exe'))), None)
    if not exe:
        raise ValueError('Im Archiv war kein Godot-Programm.')
    return exe, True


def project_dir(root: Path):
    """Godot-Projekt eines Spiels: <Spiel>/godot/project.godot oder ein Godot-Projekt direkt im Ordner."""
    for d in (root / 'godot', root):
        if (d / 'project.godot').is_file():
            return d
    return None


def project_godot(title: str, profile='3d', major_minor=VERSION.rsplit('.', 1)[0]):
    p = PROFILES[profile]
    sections = {'application': [f'config/name="{title}"', f'config/features=PackedStringArray("{major_minor}", "{p["feature"]}")'],
                'rendering': [f'renderer/rendering_method="{p["renderer"]}"']}
    for sec, line in p['extra']:
        sections.setdefault(sec, []).append(line)
    out = ['; Angelegt von GAMEFORGE. Einheiten: 1 = 1 Meter, Y oben (wie glTF aus Blender).', '', 'config_version=5', '']
    for sec, lines in sections.items():
        out += [f'[{sec}]', '', *lines, '']
    return '\n'.join(out)


def create_project(root: Path, title: str, profile='3d'):
    d = root / 'godot'
    if (d / 'project.godot').exists():
        raise FileExistsError(f'In {d} gibt es schon ein Godot-Projekt – nichts überschrieben.')
    d.mkdir(parents=True, exist_ok=True)
    (d / 'project.godot').write_text(project_godot(title, profile), encoding='utf-8')
    (d / '.gitignore').write_text('.godot/\n*.tmp\n', encoding='utf-8')
    return d


ERR = re.compile(r'^(ERROR|SCRIPT ERROR|USER ERROR|Parse Error)\b|Failed loading resource|Error importing', re.I)
WARN = re.compile(r'^(WARNING|USER WARNING)\b', re.I)


def parse_log(text: str):
    errors, warnings = [], []
    for line in text.splitlines():
        s = line.strip()
        if ERR.search(s):
            errors.append(s[:300])
        elif WARN.search(s):
            warnings.append(s[:300])
    return {'ok': not errors, 'fehler': errors, 'warnungen': warnings}


def check_project(exe: Path, proj: Path, timeout=600, run=subprocess.run):
    """Godot liest das Projekt ohne Fenster ein (importiert alle Dateien) und beendet sich. Ergebnis aus dem echten Log."""
    r = run([str(console_exe(exe)), '--headless', '--path', str(proj), '--import'],
            capture_output=True, text=True, timeout=timeout, errors='replace')
    res = parse_log((r.stdout or '') + '\n' + (r.stderr or ''))
    if r.returncode not in (0, None):
        res['ok'] = False
        res['fehler'].append(f'Godot beendet mit Code {r.returncode}')
    return res


def imported(proj: Path, rel: str) -> bool:
    """Hat Godot die Datei wirklich importiert? (neben der Datei liegt <name>.import)"""
    return (proj / (rel + '.import')).is_file()


def start_editor(exe: Path, proj: Path):
    subprocess.Popen([str(exe), '-e', '--path', str(proj)], close_fds=True, creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0))


def mcp_entry(exe: Path):
    """Eintrag für Claude Code: lokaler Godot-MCP über npx, Godot-Pfad fest gesetzt."""
    cmd = ['cmd', '/c', 'npx', '-y', MCP_PACKAGE] if os.name == 'nt' else ['npx', '-y', MCP_PACKAGE]
    return {'type': 'stdio', 'command': cmd[0], 'args': cmd[1:], 'env': {'GODOT_PATH': str(exe)}}


def register_mcp(exe: Path, claude='claude'):
    entry = json.dumps(mcp_entry(exe))
    subprocess.run([claude, 'mcp', 'remove', 'godot', '--scope', 'user'], capture_output=True, text=True, timeout=60)
    r = subprocess.run([claude, 'mcp', 'add-json', 'godot', entry, '--scope', 'user'], capture_output=True, text=True, timeout=60, errors='replace')
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return entry
