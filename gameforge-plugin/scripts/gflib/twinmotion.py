"""Twinmotion-Brücke: alles, was sich um Twinmotion herum per Python erledigen lässt.

Twinmotion selbst hat keine Skript-Schnittstelle (Python-Baustein ist in der ausgelieferten Version abgeschaltet).
Deshalb: Python bereitet Dateien und Aufträge vor, startet Twinmotion und prüft die Ergebnisse; die Klicks in
Twinmotion macht Claudes Computersteuerung (bzw. der Nutzer nach Anleitung). Nichts wird als erledigt gemeldet,
solange keine geprüfte Datei existiert.
"""
from __future__ import annotations
import json, os, shutil, subprocess
from pathlib import Path

EXE_REL = Path('Twinmotion/Binaries/Win64/TwinmotionCookedEditor-Win64-Shipping.exe')
EXPORT_EXT = {'.png', '.jpg', '.jpeg', '.exr', '.mp4', '.mov', '.avi'}
IMPORT_EXT = ('.fbx', '.glb', '.gltf', '.obj', '.usd', '.usdz', '.udatasmith')

# Standard-Shotliste für Vorvisualisierung: wenige, aussagekräftige Ansichten
DEFAULT_SHOTS = [
    {'name': 'totale', 'beschreibung': 'Totale, Augenhöhe 1,70 m, Objekt ganz im Bild', 'brennweite_mm': 24},
    {'name': 'halbnah', 'beschreibung': 'Halbnah, leicht von unten (Heldenperspektive)', 'brennweite_mm': 50},
    {'name': 'detail', 'beschreibung': 'Detail auf Material/Oberfläche', 'brennweite_mm': 85},
]
DEFAULT_LOOKS = ['Mittag, klar', 'Goldene Stunde', 'Bedeckt / Regen', 'Nacht']


def find_exe():
    base = Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Epic Games'
    hits = sorted(base.glob('Twinmotion*/' + EXE_REL.as_posix()))
    return hits[-1] if hits else None


def running():
    """PIDs laufender Twinmotion-Hauptprozesse (nur lesen)."""
    if os.name != 'nt':
        return []
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              "Get-Process TwinmotionCookedEditor-Win64-Shipping -ErrorAction SilentlyContinue | "
                              "Where-Object { $_.MainWindowTitle -ne '' } | ForEach-Object { $_.Id }"],
                             capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [int(x) for x in out.split() if x.isdigit()]


def start():
    exe = find_exe()
    if not exe:
        raise FileNotFoundError('Twinmotion ist nicht installiert (Epic Games Launcher → Twinmotion).')
    if running():
        return False
    subprocess.Popen([str(exe)], close_fds=True, creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0))
    return True


def prepare(root: Path, asset: str, source: Path, shots=None, looks=None, video_seconds=5):
    """Legt twinmotion/<asset>/ an: Quelldatei mit festem Namen (für Neu-Import), Auftrag mit Shots/Looks/Export."""
    if source.suffix.lower() not in IMPORT_EXT:
        raise ValueError(f'Twinmotion importiert {", ".join(IMPORT_EXT)} – nicht {source.suffix}')
    d = root / 'twinmotion' / asset
    (d / 'export').mkdir(parents=True, exist_ok=True)
    target = d / f'{asset}{source.suffix.lower()}'
    shutil.copy2(source, target)              # fester Name: Twinmotion liest dieselbe Datei nach Änderungen neu ein
    order = {
        'asset': asset, 'quelle': str(source), 'twinmotion_import': str(target), 'export_ordner': str(d / 'export'),
        'zweck': 'Vorvisualisierung / Look-Probe (kein Final-Render – Final macht Unreal)',
        'shots': shots or DEFAULT_SHOTS, 'looks': looks or DEFAULT_LOOKS,
        'export': {'bild': {'format': 'PNG', 'aufloesung': '1920x1080'},
                   'video': {'format': 'MP4', 'aufloesung': '1920x1080', 'sekunden': video_seconds, 'fps': 30}},
        'klickweg': [
            'Twinmotion → Home → New scene',
            'unten „Import“ → „+“ → Datei: ' + str(target) + ' → Import',
            'Neu-Import nach Änderung: Datei wird von GAMEFORGE unter demselben Namen ersetzt → in Twinmotion beim Objekt „Reimport/Synchronize“',
            'Media → Bild „+“ je Shot; Media → Video „+“ (Kamerafahrt mit Keyframes)',
            'Export → Image/Video auswählen → ganz nach unten → „Start export“ → Ordner: ' + str(d / 'export'),
        ],
    }
    (d / 'TWINMOTION_AUFTRAG.json').write_text(json.dumps(order, ensure_ascii=False, indent=2), encoding='utf-8')
    return d, order


def check_outputs(folder: Path, media_info):
    """Prüft exportierte Bilder/Videos wirklich (Dateikopf bzw. ffprobe). media_info kommt aus dem GPU-Commander."""
    res = []
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.suffix.lower() in EXPORT_EXT:
            info = media_info(p) if p.stat().st_size > 0 else None
            res.append({'datei': str(p), 'bytes': p.stat().st_size, 'info': info,
                        'ok': bool(info and info.get('width') and info.get('height'))})
    return res
