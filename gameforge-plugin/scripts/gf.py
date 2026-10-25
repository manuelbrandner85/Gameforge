#!/usr/bin/env python3
"""gf – Werkzeug des GAMEFORGE-Plugins für Claude Code (nur Python-Standardbibliothek).

Claude ruft es auf; Ausgaben sind deutsch und ehrlich: geplant / vorhanden / geprüft.
Aufruf:  gf <befehl> [optionen]      (Hilfe: gf hilfe)
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, socket, sqlite3, subprocess, sys, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gflib import art_direction, prompts, quality, imagecheck, comfy, hardware  # noqa: E402

PLUGIN = HERE.parent
HOME = PLUGIN.parent                                   # GAMEFORGE-Ordner (enthält engines/ mit ComfyUI)

sys.path.insert(0, str(HOME))
try:                                                    # gemeinsamer Kern: Smart GPU Commander + Auftragswarteschlange
    from gameforge_core import gpu_commander as gc, jobs as gjobs  # noqa: E402
except ImportError:                                     # Plugin ohne GAMEFORGE-Ordner: ohne Wächter, aber ehrlich gemeldet
    gc = gjobs = None


class _GpuGuard:
    """Ein GPU-Schwerjob gleichzeitig: wartet auf Token + VRAM, misst den Spitzenbedarf und lernt ihn je Jobtyp."""

    def __init__(self, name, job_type, default_mb, timeout_s=1800, make_room=None):
        self.name, self.job_type, self.timeout_s, self.make_room = name, job_type, timeout_s, make_room
        self.need = gc.estimate_need(job_type, default_mb) if gc else default_mb
        self._last, self._peak, self._stop = 0.0, 0, None

    def _wait(self, msg):
        if time.time() - self._last > 60:
            out('WARTET – ' + msg)
            self._last = time.time()

    def _sample(self, base):
        while not self._stop.wait(2):
            m = gc.measure()
            if m['measured']:
                self._peak = max(self._peak, m['vram_used_mb'] - base)

    def __enter__(self):
        if not gc:
            out('Hinweis: GPU-Wächter nicht gefunden – Job läuft ohne Warteschlange.')
            return self
        import threading
        self._cm = gc.gpu_slot(self.name, 'heavy', self.need, self.timeout_s, 15, self._wait, self.make_room)
        try:
            info = self._cm.__enter__()
        except RuntimeError as e:
            raise SystemExit('BLOCKIERT – ' + str(e).replace('RESOURCE_BLOCKED: ', '') + ' Die Qualität wird nicht automatisch gesenkt.')
        before = info.get('before') or {}
        out(f'GPU frei für „{self.name}“ ({info.get("preflight")}).')
        if before.get('measured'):
            self._stop = threading.Event()
            self._t = threading.Thread(target=self._sample, args=(before['vram_used_mb'],), daemon=True)
            self._t.start()
        return self

    def __exit__(self, et, ev, tb):
        if not gc:
            return False
        if self._stop:
            self._stop.set(); self._t.join(5)
            if et is None and self._peak > 200:
                gc.record_peak(self.job_type, self._peak)
                out(f'Gemessener zusätzlicher VRAM-Bedarf: {self._peak} MB (für künftige Planung gespeichert).')
        return self._cm.__exit__(et, ev, tb)

GAMES = Path(os.environ.get('GAMEFORGE_SPIELE') or Path.home() / 'Desktop' / 'GAMEFORGE Spiele')
FILMS = Path(os.environ.get('GAMEFORGE_FILME') or GAMES.parent / 'GAMEFORGE Filme')
REGISTRY = GAMES / '_projekte.json'          # extern liegende Projekte: nur Verweis, nie verschoben
BACKUPS = GAMES / '_Sicherungen'
TRASH = GAMES / '_Papierkorb'

FIELDS = [
    ('vision', 'Spielvision & Ziele'), ('game_rules', 'Spielregeln & Gameplay-Loop'), ('canon', 'Story-Kanon (verbindlich)'),
    ('story', 'Handlung / Akte'), ('prologue', 'Prolog'), ('chapters', 'Kapitel & Hauptmissionen'), ('sidequests', 'Nebenmissionen & Geheimnisse'),
    ('dialogue', 'Dialoge & Entscheidungen'), ('endings', 'Enden & Konsequenzen'), ('characters', 'Helden & Charaktere'),
    ('bosses', 'Bosse & Gegner'), ('npcs', 'NPCs & lebendige Welt'), ('world', 'Welt, Orte & Karten'),
    ('environments', 'Gebäude, Landschaften & Props'), ('combat', 'Kampfsystem & Fähigkeiten'), ('movement', 'Bewegung & Steuerung'),
    ('physics', 'Physik, Fahrzeuge & Wasser'), ('ai', 'NPC-, Gegner- & Boss-KI'), ('items', 'Waffen, Inventar & Ausrüstung'),
    ('progression', 'Fortschritt & Balancing'), ('ui', 'Menü, HUD & UX'), ('cinematics', 'Zwischensequenzen & Kamera'),
    ('audio', 'Musik, Sprache & Geräusche'), ('save_load', 'Speichern / Laden'), ('accessibility', 'Barrierefreiheit, Untertitel & Optionen'),
    ('localization', 'Lokalisierung'), ('performance', 'Performance & Streaming'), ('technical', 'Unreal-/Blender-Bauplan & MCP'),
    ('qa', 'Testfälle & Abnahmekriterien'), ('release', 'Build, Distribution & Updates'), ('legal', 'Lizenzen & Bild-/Musikrechte')]
REQUIRED = ['vision', 'game_rules', 'canon', 'story', 'prologue', 'chapters', 'characters', 'world', 'movement', 'ui', 'save_load', 'technical', 'qa', 'release']
DLC_FIELDS = [('story', 'Story & Kanon'), ('quests', 'DLC-Missionen'), ('new_characters', 'Neue Charaktere'), ('new_world', 'Neue Regionen / Level'),
              ('new_assets', 'Neue 3D-Assets'), ('gameplay', 'Gameplay / Fähigkeiten'), ('integration', 'Integration, Savegames & Kompatibilität'),
              ('qa', 'DLC-Tests & Abnahme')]
VIEWS = {'character': ['front', 'side', 'back', 'face', 'scale'], 'boss': ['front', 'side', 'back', 'face', 'scale'],
         'npc': ['front', 'side', 'back', 'face'], 'creature': ['front', 'side', 'back', 'scale'], 'weapon': ['front', 'side', 'detail', 'scale'],
         'building': ['front', 'side', 'back', 'entrance', 'material'], 'vehicle': ['front', 'side', 'back', 'detail'],
         'environment': ['overview', 'landmarks', 'lighting'], 'prop': ['front', 'side', 'detail'], 'ui': ['layout', 'states', 'icons']}
TASKS = [
    ('01 Bestandsaufnahme', 'Originalunterlagen und Projektdateien erfassen', 'Inventar mit Quellen und Versionsstand geprüft'),
    ('02 Kanon & Gamedesign', 'Spielbibel und Kanon abgleichen', 'Konsistente, freigegebene Spielbibel'),
    ('02 Kanon & Gamedesign', 'Story, Prolog, Missionen und Enden', 'Durchgängiger Ablaufplan ohne lose Enden'),
    ('02 Kanon & Gamedesign', 'Core Loop, Regeln und Fortschritt', 'Test- und Zustandsregeln für alle Kernmechaniken'),
    ('03 Welt & Assets', 'Weltkarte und Orte', 'Vollständiges Level-Konzept'),
    ('03 Welt & Assets', 'Asset-Liste mit Größen', 'Asset-Matrix ohne fehlende Pflichtobjekte'),
    ('04 Referenzen', 'Pflichtreferenzen erzeugen und freigeben', 'Alle nötigen Ansichten freigegeben'),
    ('05 Blender', '3D-Modelle und Materialien', 'Echte .blend-/.fbx-Dateien geprüft'),
    ('05 Blender', 'Rigs und Animationen', 'Animationscheck in Unreal ohne Fehler'),
    ('06 Unreal', 'Projektgrundlage und Build-Pipeline', 'Kompilierter Stand, reproduzierbarer Build'),
    ('06 Unreal', 'Steuerung, Kampf, Fähigkeiten', 'Spielbare Kontrolle mit Gameplaytest'),
    ('06 Unreal', 'Gegner-KI, Bosse, NPCs', 'Funktionierende Szenarien mit Testnachweis'),
    ('06 Unreal', 'Missionen, Inventar, Speichern', 'Quest-/Save-Load-Tests bestanden'),
    ('07 UI, Audio & Cinematics', 'Menüs, HUD, Optionen, Barrierefreiheit', 'Alle Bildschirme getestet'),
    ('07 UI, Audio & Cinematics', 'Prolog, Cinematics, Abspann', 'Sequenzen starten/enden korrekt'),
    ('07 UI, Audio & Cinematics', 'Musik, Sprache, Geräusche', 'Audio-Check bestanden'),
    ('08 Integration', 'Alles zusammenführen', 'Durchspielbar ohne Blocker'),
    ('09 Test & Optimierung', 'Qualitätstests', 'Testprotokoll mit Belegen'),
    ('09 Test & Optimierung', 'Performance', 'FPS-Ziele auf Zielhardware erreicht'),
    ('10 Release', 'Finaler Build und Installer', 'Installierbarer Build geprüft'),
    ('10 Release', 'Rechteprüfung und Abnahme', 'Release-Checkliste freigegeben')]
FILM_FIELDS = [
    ('logline', 'Logline (ein Satz)'), ('treatment', 'Treatment / Inhalt'), ('canon', 'Kanon & Vorgaben (verbindlich)'),
    ('script', 'Drehbuch / Szenen'), ('characters', 'Figuren & Besetzung'), ('locations', 'Schauplätze'),
    ('shotlist', 'Shotliste'), ('storyboard', 'Storyboard'), ('look', 'Look, Kamera & Farbe'), ('music', 'Musik, Ton & Sprache'),
    ('edit', 'Schnitt & Länge'), ('render', 'Render & Technik (Unreal Sequencer / Blender)'), ('qa', 'Abnahme & Prüfungen'),
    ('rights', 'Rechte & Lizenzen')]
FILM_REQUIRED = ['logline', 'treatment', 'script', 'characters', 'shotlist', 'look', 'music', 'render']
FILM_DIRS = ('referenzen/entwuerfe', 'referenzen/freigegeben', 'storyboard', 'blender', 'unreal', 'schnitt', 'ton', 'renders', 'export', 'originale', 'versionen')
STANDARD_DIRS = ('referenzen/entwuerfe', 'referenzen/freigegeben', 'blender', 'export', 'unreal', 'dlc', 'originale', 'versionen')
TASK_STATES = ['Offen', 'In Arbeit', 'Umgesetzt', 'Getestet', 'Abgenommen']


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def out(text=''):
    sys.stdout.write(str(text) + '\n')


def safe_name(title):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title).strip().rstrip('.')
    if not name or name.upper() in ('CON', 'PRN', 'AUX', 'NUL') or name.startswith('_'):
        raise SystemExit('Ungültiger Spielname.')
    return name[:80]


def read_json(p, default=None):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def write_json(p, data):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, p)


def _own(root, marker):
    if not root.is_dir():
        return []
    return sorted([d for d in root.iterdir() if d.is_dir() and not d.name.startswith(('_', '.')) and (d / marker).is_file()],
                  key=lambda d: d.name.lower())


def games():
    return _own(GAMES, 'spiel.json')


def films():
    return _own(FILMS, 'film.json')


def external():
    return [x for x in (read_json(REGISTRY, []) or []) if Path(x.get('path', '')).is_dir()]


def all_projects():
    """(Anzeigename, Typ, Pfad, extern?) für alle bekannten Spiele und Filme."""
    out = [(g.name, 'spiel', g, False) for g in games()] + [(f.name, 'film', f, False) for f in films()]
    out += [(x['title'], x['kind'], Path(x['path']), True) for x in external()]
    return out


def detect(path):
    """Erkennt, ob ein Ordner (oder ein übergeordneter) ein Spiel- oder Filmprojekt ist.
    Reihenfolge: GAMEFORGE-Marker und vermerkte Projekte zuerst, dann Unreal-Projekt/CLAUDE.md."""
    chain = [Path(path).resolve()]
    chain += list(chain[0].parents)[:4]
    reg = {Path(x['path']).resolve(): x for x in external()}
    for d in chain:
        if (d / 'spiel.json').is_file():
            return d, 'spiel', 'GAMEFORGE-Spiel'
        if (d / 'film.json').is_file():
            return d, 'film', 'GAMEFORGE-Film'
        if d in reg:
            return d, reg[d]['kind'], 'vermerktes Projekt'
    film_words = ('trailer', 'film', 'kino', 'cinema', 'movie render', 'drehbuch')
    for i, d in enumerate(chain):
        up = list(d.glob('*.uproject')) + list(d.glob('*/*.uproject'))
        md = next((c / 'CLAUDE.md' for c in chain[i:] if (c / 'CLAUDE.md').is_file()), None)
        text = md.read_text(encoding='utf-8', errors='replace')[:6000].lower() if md else ''
        if not up and not (d / 'CLAUDE.md').is_file():
            continue
        root = md.parent if md and md.parent in chain[i:i + 3] and not up else d
        film_score = sum(text.count(w) for w in film_words + ('sequencer', 'shot', 'szene', 'render'))
        game_score = sum(text.count(w) for w in ('gameplay', 'spielbar', 'spielprojekt', 'level', 'quest', 'mission', 'savegame', 'menü'))
        if film_score > game_score:
            return root, 'film', 'Film-/Unreal-Projekt (eigene Regeln)'
        if up or any(w in text for w in ('spiel', 'game', 'unreal')):
            return root, 'spiel', 'Spiel-/Unreal-Projekt (eigene Regeln)'
    return None, None, None


def find_game(name):
    """Findet ein Projekt (Spiel oder Film) über Namen, Ordnerpfad oder „.“ (aktueller Ordner)."""
    raw = (name or '').strip()
    if raw in ('.', '') or Path(raw).is_absolute() or Path(raw).is_dir():
        d, kind, _ = detect(raw or '.')
        if d:
            return d
        if raw:
            raise SystemExit(f'„{raw}“ ist kein erkennbares Spiel- oder Filmprojekt.')
    name = raw.lower()
    ps = all_projects()
    exact = [p for p in ps if p[0].lower() == name]
    if len(exact) == 1:
        return exact[0][2]
    part = [p for p in ps if name and name in p[0].lower()]
    if len(part) == 1:
        return part[0][2]
    if not ps:
        raise SystemExit('Noch kein Projekt vorhanden. Mit „gf neu --titel …“ anlegen.')
    raise SystemExit(f'Projekt „{raw}“ nicht eindeutig gefunden. Vorhanden: ' + ', '.join(f'{p[0]} ({p[1]})' for p in ps))


def is_gameforge(root):
    return (root / 'spiel.json').is_file() or (root / 'film.json').is_file()


def need_gameforge(root, what):
    if not is_gameforge(root):
        raise SystemExit(f'„{root.name}“ ist ein eigenständiges Projekt mit eigenen Regeln. {what} geht dort nur nach dessen CLAUDE.md – '
                         'GAMEFORGE legt in fremden Projekten keine eigenen Ordner oder Dateien an.')


# ------------------------------------------------------------------ Spielbibel (SPIEL.md)
def bible_md(title, bible, intro='Spielbibel'):
    lines = [f'# {title}', '', f'> {intro}. Abschnitte mit „(offen)“ sind noch nicht ausgearbeitet – GAMEFORGE erfindet dort nichts.',
             '> Der Abschnitt „Story-Kanon (verbindlich)“ wird nur nach ausdrücklicher Zustimmung geändert.', '']
    for key, label in FIELDS:
        lines += [f'## {label}', '', (bible.get(key) or '').strip() or '(offen)', '']
    return '\n'.join(lines)


def parse_md(path):
    sections, cur, buf = {}, None, []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            if cur:
                sections[cur] = '\n'.join(buf).strip()
            cur, buf = line[3:].strip(), []
        elif cur:
            buf.append(line)
    if cur:
        sections[cur] = '\n'.join(buf).strip()
    return sections


def filled(text):
    return bool(text) and text.strip() not in ('(offen)', '')


def claude_md(title):
    return f'''# Spiel: {title}

Dieser Ordner gehört ausschließlich zum Spiel **{title}**. Nichts mit anderen Spielen vermischen.
- Verbindliche Spielbibel: `SPIEL.md` (Kanon nur nach ausdrücklicher Zustimmung ändern).
- Stilvorgaben: `art-direction.json`. Aufgaben: `aufgaben.json`. Ehrlicher Stand: `gf stand "{title}"`.
- Referenzen: `referenzen/freigegeben/` (offiziell) und `referenzen/entwuerfe/` (noch nicht freigegeben).
- Blender-Dateien: `blender/`, Exporte: `export/`, Unreal-Projekt: `unreal/`, Originale (nie verändern): `originale/`.
'''


def film_md(title, data):
    lines = [f'# {title}', '', '> Filmbibel. Abschnitte mit „(offen)“ sind noch nicht ausgearbeitet – GAMEFORGE erfindet dort nichts.',
             '> „Kanon & Vorgaben (verbindlich)“ wird nur nach ausdrücklicher Zustimmung geändert.', '']
    for key, label in FILM_FIELDS:
        lines += [f'## {label}', '', (data.get(key) or '').strip() or '(offen)', '']
    return '\n'.join(lines)


def create_film(title, idea='', style='', length='', fmt='', basis=''):
    name = safe_name(title)
    root = FILMS / name
    if root.exists():
        raise SystemExit(f'Es gibt bereits einen Filmordner „{name}“. Nichts überschrieben.')
    for sub in FILM_DIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)
    meta = {'id': hashlib.sha256((name + now()).encode()).hexdigest()[:12], 'kind': 'film', 'title': title, 'status': 'Idee', 'version': 'v0.1',
            'style': style, 'length': length, 'format': fmt, 'based_on': basis, 'engine': 'Unreal Engine 5 (Sequencer / Movie Render Queue)',
            'created_at': now(), 'updated_at': now()}
    write_json(root / 'film.json', meta)
    (root / 'FILM.md').write_text(film_md(title, {'treatment': idea, 'edit': ('Ziellänge: ' + length) if length else ''}), encoding='utf-8')
    (root / 'CLAUDE.md').write_text(f'''# Film: {title}

Dieser Ordner gehört ausschließlich zum Film **{title}**{(' (basiert auf ' + basis + ')') if basis else ''}.
- Verbindliche Filmbibel: `FILM.md` (Kanon nur nach ausdrücklicher Zustimmung ändern).
- Stil: `art-direction.json`. Ehrlicher Stand: `gf stand "{title}"`.
- Status nur mit Nachweis: geplant → gebaut → gerendert → geprüft → freigegeben.
''', encoding='utf-8')
    prof = art_direction.build_profile({'title': title, 'style': style or 'cinematic', 'genre': 'Film', 'camera': '', 'engine': 'Unreal Engine 5', 'bible': {'vision': idea}})
    write_json(root / 'art-direction.json', {'profile': prof, 'source': 'automatisch', 'approved': False, 'updated_at': now()})
    write_json(root / 'referenzen' / 'auftraege.json', [])
    return root


def create_game(title, vision='', genre='', style='', camera='', platform='', wishes='', summary='', engine='Unreal Engine 5', bible=None, extra=None):
    name = safe_name(title)
    root = GAMES / name
    if root.exists():
        raise SystemExit(f'Es gibt bereits einen Ordner „{name}“. Nichts überschrieben.')
    for sub in STANDARD_DIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)
    b = dict(bible or {})
    if vision and not b.get('vision'):
        b['vision'] = vision
    if platform and not b.get('release'):
        b['release'] = 'Zielplattform (deine Angabe): ' + platform
    if wishes and not b.get('game_rules'):
        b['game_rules'] = 'Deine Wünsche (noch nicht ausgearbeitet):\n' + wishes
    gid = hashlib.sha256((name + now()).encode()).hexdigest()[:12]
    meta = {'id': gid, 'title': title, 'summary': summary or vision[:200], 'status': 'Idee', 'version': 'v0.1', 'genre': genre, 'style': style,
            'camera': camera, 'engine': engine, 'platform': platform, 'created_at': now(), 'updated_at': now()}
    meta.update(extra or {})
    write_json(root / 'spiel.json', meta)
    (root / 'SPIEL.md').write_text(bible_md(title, b), encoding='utf-8')
    (root / 'CLAUDE.md').write_text(claude_md(title), encoding='utf-8')
    prof = art_direction.build_profile({'title': title, 'style': style, 'genre': genre, 'camera': camera, 'engine': engine, 'bible': b})
    write_json(root / 'art-direction.json', {'profile': prof, 'source': 'automatisch', 'approved': False, 'updated_at': now()})
    write_json(root / 'aufgaben.json', [{'phase': p, 'title': t, 'acceptance': a, 'status': 'Offen', 'evidence': ''} for p, t, a in TASKS])
    write_json(root / 'referenzen' / 'auftraege.json', [])
    return root


# ------------------------------------------------------------------ Befehle
def cmd_neu(a):
    if a.typ == 'film':
        root = create_film(a.titel, a.idee or '', a.stil or '', a.laenge or '', a.format or '', a.basis or '')
        out(f'FILM ANGELEGT: {root}')
        out('Enthalten: FILM.md (Logline, Treatment, Drehbuch, Shotliste, Look, Ton …), art-direction.json, Ordner storyboard/blender/unreal/schnitt/ton/renders/export, CLAUDE.md.')
        return
    root = create_game(a.titel, a.idee or '', a.genre or '', a.stil or '', a.perspektive or '', a.plattform or '', a.wuensche or '', a.kurz or '')
    prof = read_json(root / 'art-direction.json')['profile']
    out(f'ANGELEGT: {root}')
    out(f'Grafikstil erkannt: {prof["style_label"]} ({prof["style_reason"]}) · Qualität AUTO: {prof["quality_auto"]}')
    out('Enthalten: SPIEL.md (Spielbibel), art-direction.json, aufgaben.json (21 Aufgaben), Ordner referenzen/blender/export/unreal/dlc/originale/versionen, CLAUDE.md.')


def cmd_liste(a):
    ps = all_projects()
    if not ps:
        out(f'Noch keine Projekte (Spiele: {GAMES}, Filme: {FILMS}).')
        return
    for name, kind, path, ext in ps:
        m = read_json(path / ('spiel.json' if kind == 'spiel' else 'film.json'), {}) or {}
        info = f'{m.get("status", "?")} · {m.get("version", "")}' if m else 'eigene Regeln (CLAUDE.md des Projekts)'
        out(f'- {"🎮" if kind == "spiel" else "🎬"} {name} ({kind}) · {info} · {path}' + (' · extern vermerkt' if ext else ''))


def cmd_erkennen(a):
    d, kind, how = detect(a.pfad or '.')
    if not d:
        out('KEIN PROJEKT erkannt in diesem Ordner. Für Neues: „gf neu“ (Spiel) oder „gf neu --typ film“.')
        return
    rules = [x for x in ('CLAUDE.md', '.claude/agents', '.claude/settings.json', 'hooks') if (d / x).exists()]
    out(f'PROJEKT: {d.name} · Typ: {kind} · erkannt als: {how} · Ordner: {d}')
    out('Eigene Regeln vorhanden (haben Vorrang): ' + (', '.join(rules) if rules else 'keine'))


def cmd_registrieren(a):
    d = Path(a.pfad).resolve()
    if not d.is_dir():
        raise SystemExit('Ordner nicht gefunden.')
    reg = [x for x in (read_json(REGISTRY, []) or []) if Path(x['path']).resolve() != d]
    reg.append({'title': a.titel or d.name, 'kind': a.typ, 'path': str(d), 'registered_at': now(), 'note': a.notiz or ''})
    GAMES.mkdir(parents=True, exist_ok=True)
    write_json(REGISTRY, reg)
    out(f'VERMERKT: {a.titel or d.name} ({a.typ}) → {d}  (nur Verweis – im Projekt wurde nichts verändert)')


def external_status(root):
    """Nur lesender Überblick über ein eigenständiges Projekt."""
    count = lambda pat: sum(1 for _ in root.rglob(pat)) if root.is_dir() else 0
    up = list(root.glob('*.uproject')) + list(root.glob('*/*.uproject'))
    branch = ''
    try:
        branch = subprocess.run(['git', '-C', str(root), 'branch', '--show-current'], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    lines = [f'# Stand: {root.name} (eigenständiges Projekt – nur gelesen)', '',
             f'- Ordner: {root}' + (f' · Git-Zweig: {branch}' if branch else ''),
             f'- Unreal-Projekt: {", ".join(p.name for p in up) or "keins"}',
             f'- Unreal-Dateien (.umap / .uasset): {count("*.umap")} / {count("*.uasset")}',
             f'- Blender-Dateien: {count("*.blend")} · FBX: {count("*.fbx")}',
             f'- Videos (.mp4/.mov): {count("*.mp4") + count("*.mov")} · Audio (.wav): {count("*.wav")}',
             f'- Eigene Regeln: ' + ', '.join(x for x in ('CLAUDE.md', '.claude', 'hooks') if (root / x).exists()), '',
             'Die genauen Status-Regeln stehen in der CLAUDE.md des Projekts – sie haben Vorrang. Hier wurde nichts verändert.']
    return '\n'.join(lines)


def blend_ok(p):
    return imagecheck_like(p, (b'BLENDER', b'\x28\xb5\x2f\xfd', b'\x1f\x8b'))


def imagecheck_like(p, heads):
    try:
        with open(p, 'rb') as f:
            h = f.read(32)
        return p.stat().st_size > 0 and any(h.startswith(x) for x in heads)
    except OSError:
        return False


def fbx_ok(p):
    return imagecheck_like(p, (b'Kaydara FBX Binary', b'; FBX'))


def game_status(root):
    meta = read_json(root / 'spiel.json', {})
    sec = parse_md(root / 'SPIEL.md') if (root / 'SPIEL.md').is_file() else {}
    labels = dict(FIELDS)
    missing = [labels[k] for k in REQUIRED if not filled(sec.get(labels[k], ''))]
    approved = sorted(p.relative_to(root).as_posix() for p in (root / 'referenzen' / 'freigegeben').rglob('*.png'))
    drafts = sorted(p.relative_to(root).as_posix() for p in (root / 'referenzen' / 'entwuerfe').rglob('*.png'))
    orders = read_json(root / 'referenzen' / 'auftraege.json', []) or []
    blends = [(p, blend_ok(p)) for p in (root / 'blender').rglob('*.blend')]
    fbx = [(p, fbx_ok(p)) for p in list((root / 'export').rglob('*.fbx')) + list((root / 'blender').rglob('*.fbx'))]
    uprojects = list((root / 'unreal').rglob('*.uproject'))
    uassets = list((root / 'unreal').rglob('Content/GAMEFORGE/**/*.uasset'))
    tasks = read_json(root / 'aufgaben.json', []) or []
    builds = [p for p in (root / 'export').rglob('*') if p.is_file() and p.suffix.lower() in ('.exe', '.zip', '.pak')]
    dlcs = [d.name for d in (root / 'dlc').iterdir() if d.is_dir()] if (root / 'dlc').is_dir() else []
    return {'meta': meta, 'missing': missing, 'approved': approved, 'drafts': drafts, 'orders': orders, 'blends': blends, 'fbx': fbx,
            'uprojects': uprojects, 'uassets': uassets, 'tasks': tasks, 'builds': builds, 'dlcs': dlcs}


def film_status(root):
    sec = parse_md(root / 'FILM.md') if (root / 'FILM.md').is_file() else {}
    labels = dict(FILM_FIELDS)
    missing = [labels[k] for k in FILM_REQUIRED if not filled(sec.get(labels[k], ''))]
    m = read_json(root / 'film.json', {})
    count = lambda sub, *ext: sum(1 for p in (root / sub).rglob('*') if p.suffix.lower() in ext) if (root / sub).is_dir() else 0
    lines = [f'# Stand: {root.name} (Film)', f'_Automatisch aus echten Dateien ermittelt am {dt.datetime.now().strftime("%d.%m.%Y %H:%M")}_', '',
             f'- Status: {m.get("status")} · Version: {m.get("version")} · Ziellänge: {m.get("length") or "offen"}',
             f'- Filmbibel: {len(FILM_REQUIRED) - len(missing)}/{len(FILM_REQUIRED)} Pflichtbereiche' + (f' – offen: {", ".join(missing)}' if missing else ''),
             f'- Referenzen: {count("referenzen/freigegeben", ".png")} freigegeben, {count("referenzen/entwuerfe", ".png")} Entwürfe · Storyboard-Bilder: {count("storyboard", ".png", ".jpg")}',
             f'- Unreal-Projekt: {"ja" if list((root / "unreal").rglob("*.uproject")) else "nein"} · Blender-Dateien: {count("blender", ".blend")}',
             f'- Gerenderte Clips: {count("renders", ".mp4", ".mov", ".exr", ".png")} · Schnittdateien: {count("schnitt", ".mlt", ".otio", ".kdenlive")} · Ton: {count("ton", ".wav", ".flac")}',
             f'- Fertige Fassungen in export/: {count("export", ".mp4", ".mov")}', '',
             'Nur was als Datei nachgewiesen ist, gilt als gebaut bzw. gerendert.']
    return '\n'.join(lines)


def cmd_stand(a):
    root = find_game(a.spiel)
    if not is_gameforge(root):
        out(external_status(root))
        return
    if (root / 'film.json').is_file():
        text = film_status(root)
        (root / 'STAND.md').write_text(text + '\n', encoding='utf-8')
        out(text)
        return
    s = game_status(root)
    m = s['meta']
    t = s['tasks']
    lines = [f'# Stand: {root.name}', f'_Automatisch aus echten Dateien ermittelt am {dt.datetime.now().strftime("%d.%m.%Y %H:%M")}_', '',
             f'- Status: {m.get("status")} · Version: {m.get("version")} · Stil: {m.get("style") or "offen"}',
             f'- Spielbibel: {14 - len(s["missing"])}/14 Pflichtbereiche ausgefüllt' + (f' – offen: {", ".join(s["missing"])}' if s['missing'] else ''),
             f'- Referenzbilder: {len(s["approved"])} freigegeben, {len(s["drafts"])} Entwürfe warten auf Prüfung',
             f'- Blender: {sum(ok for _, ok in s["blends"])} gültige .blend-Dateien' + (f' ({sum(not ok for _, ok in s["blends"])} ungültig)' if any(not ok for _, ok in s['blends']) else ''),
             f'- Exporte: {sum(ok for _, ok in s["fbx"])} gültige .fbx-Dateien',
             f'- Unreal: {"Projekt vorhanden" if s["uprojects"] else "kein .uproject im Ordner unreal/"} · {len(s["uassets"])} importierte GAMEFORGE-Assets',
             f'- Aufgaben: ' + ', '.join(f'{st}: {sum(x["status"] == st for x in t)}' for st in TASK_STATES),
             f'- Spielversionen (Builds) in export/: {len(s["builds"])}',
             f'- DLCs: {", ".join(s["dlcs"]) or "keine"}', '',
             'Hinweis: Nur was oben als Datei nachgewiesen ist, gilt als gebaut. Pläne und Ideen stehen in SPIEL.md.']
    text = '\n'.join(lines)
    (root / 'STAND.md').write_text(text + '\n', encoding='utf-8')
    out(text)


def port_open(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=0.5):
            return True
    except OSError:
        return False


def cmd_system(a):
    claude = shutil.which('claude')
    out('== GAMEFORGE Systemprüfung (echte Messung) ==')
    if claude:
        r = subprocess.run([claude, 'auth', 'status'], capture_output=True, text=True, timeout=30, errors='replace', stdin=subprocess.DEVNULL)
        try:
            auth = json.loads(r.stdout[r.stdout.index('{'):r.stdout.rindex('}') + 1])
        except ValueError:
            auth = {}
        out(f'Claude Code: gefunden · angemeldet: {"ja" if auth.get("loggedIn") else "NEIN – „claude auth login“ ausführen"}')
        r = subprocess.run([claude, 'mcp', 'list'], capture_output=True, text=True, timeout=90, errors='replace', stdin=subprocess.DEVNULL, cwd=str(GAMES) if GAMES.is_dir() else None)
        for line in r.stdout.splitlines():
            if line.startswith(('blender:', 'unreal-mcp:')):
                out('MCP ' + line.split(':')[0] + ': ' + ('verbunden' if '✔' in line or '✓' in line else 'NICHT verbunden'))
        if 'blender:' not in r.stdout:
            out('MCP blender: nicht eingetragen (im Ordner GAMEFORGE Spiele)')
    else:
        out('Claude Code: NICHT gefunden')
    out(f'Blender-Programm erreichbar (MCP-Add-on, Port 9876): {"ja" if port_open(9876) else "nein – Blender öffnen, MCP-Add-on starten"}')
    out(f'Unreal-Editor erreichbar (MCP, Port 8000): {"ja" if port_open(8000) else "nein – Unreal-Projekt öffnen, MCP-Plugin aktiv"}')
    b = shutil.which('blender') or next(iter(sorted(Path(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Blender Foundation').glob('Blender*/blender.exe'), reverse=True)), None)
    out(f'Blender installiert: {b or "nein"}')
    ue = sorted(Path(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Epic Games').glob('UE_*'))
    out('Unreal installiert: ' + (', '.join(p.name for p in ue) or 'nein'))
    root = comfy.find_root(HOME)
    c = comfy.Comfy(HOME, HOME / 'engines' / 'logs')
    out(f'ComfyUI (lokale Bild-KI): {"installiert" if root else "NICHT installiert"}{" · läuft" if c.online() else ""}')
    if root:
        for rel in ('diffusion_models/flux-2-klein-4b.safetensors', 'text_encoders/qwen_3_4b.safetensors', 'vae/flux2-vae.safetensors'):
            p = root / 'ComfyUI' / 'models' / rel
            out(f'  Modell {rel}: {"vorhanden" if p.is_file() else "FEHLT"}')
    g = hardware.gpu_status()
    for x in g.get('gpus', []):
        out(f'Grafikkarte: {x["name"]} · VRAM {x.get("vram_used_mb")}/{x.get("vram_total_mb")} MB belegt')
    out(f'Spieleordner: {GAMES} ({len(games())} Spiele)')


def ref_orders(root):
    return read_json(root / 'referenzen' / 'auftraege.json', []) or []


def cmd_prompt(a):
    root = find_game(a.spiel)
    prof = read_json(root / 'art-direction.json')['profile']
    ref = {'name': a.asset, 'category': a.art, 'view': a.ansicht, 'details': a.details or ''}
    p, _ = prompts.build(prof, ref, root.name)
    out(p)


def _next_version(folder, view):
    vs = [int(m.group(1)) for f in folder.glob(f'{view}_v*.png') if (m := re.search(r'_v(\d+)\.png$', f.name))]
    return max(vs, default=0) + 1


def cmd_bild(a):
    need_gameforge(find_game(a.spiel), 'Bilder ablegen')
    """Erzeugt Referenzbilder lokal über ComfyUI (127.0.0.1). Ein Bild nach dem anderen."""
    root = find_game(a.spiel)
    prof = read_json(root / 'art-direction.json')['profile']
    q, qp = quality.resolve(a.qualitaet, prof)
    views = [v.strip() for v in (a.ansichten or '').split(',') if v.strip()] or VIEWS.get(a.art, ['front'])
    asset_dir = safe_name(a.asset)
    c = comfy.Comfy(HOME, HOME / 'engines' / 'logs')
    if not comfy.find_root(HOME):
        raise SystemExit('ComfyUI ist nicht installiert (erwartet unter ' + str(HOME / 'engines') + '). Alternative: „gf prompt“ und das Bild in ChatGPT erzeugen.')
    post = prof.get('postprocess') or {}
    started = not c.online()
    out(f'Stil: {prof["style_label"]} · Qualität: {q} ({qp["label"]}) · Ansichten: {", ".join(views)}')
    if started:
        out('ComfyUI wird gestartet (nur lokal, 127.0.0.1) …')
    def _room():                                       # nur ComfyUIs eigene Modelle entladen, wenn dort nichts läuft
        q_ = c.queue_state() or {}
        return not q_.get('queue_running') and not q_.get('queue_pending') and c.free()
    guard = _GpuGuard(f'bild:{root.name}/{a.asset}', 'comfy_flux2_klein', 7000, make_room=_room)
    guard.__enter__()
    try:
        c.start()
        _bild_views(a, root, prof, q, qp, views, asset_dir, c, post)
    finally:
        guard.__exit__(*sys.exc_info())
    out('Alle Bilder brauchen deine Sichtprüfung (Anatomie, Design, Kanon). Freigeben mit: gf freigeben "<Spiel>" "<Bildpfad>"')


def _bild_views(a, root, prof, q, qp, views, asset_dir, c, post):
    orders = ref_orders(root)
    for view in views:
        approved = root / 'referenzen' / 'freigegeben' / asset_dir / f'{view}.png'
        if approved.is_file() and not a.neu:
            out(f'ÜBERSPRUNGEN {view}: freigegebene Referenz vorhanden ({approved.relative_to(root)}) – wird wiederverwendet. Mit --neu neu erzeugen.')
            continue
        ref = {'name': a.asset, 'category': a.art, 'view': view, 'details': a.details or ''}
        prompt, dhash = prompts.build(prof, ref, root.name)
        w, h = quality.dimensions(qp['long_side'], view, a.art)
        folder = root / 'referenzen' / 'entwuerfe' / asset_dir
        folder.mkdir(parents=True, exist_ok=True)
        for var in range(qp['variants']):
            ver = _next_version(folder, view)
            seed = prompts.asset_seed(root.name, a.asset, ver - 1 if a.neu else var)
            ok = False
            for attempt in range(qp['max_attempts']):
                s = seed + attempt * 104729
                wf = comfy.klein_t2i(prompt, s, w, h, 4, 1.0, prefix=f'gameforge/{asset_dir}_{view}', pixel=post if post.get('pixel_grid') else None)
                missing = c.missing_nodes(wf)
                if missing:
                    raise SystemExit('ComfyUI-Version kennt benötigte Bausteine nicht: ' + ', '.join(missing))
                t0 = time.time()
                pid = c.queue(wf)
                hist = None
                while time.time() - t0 < 1800:
                    hist = c.history(pid)
                    if hist and (hist.get('status', {}).get('completed') or hist.get('status', {}).get('status_str') == 'error'):
                        break
                    time.sleep(1)
                if not hist or hist['status'].get('status_str') == 'error':
                    msgs = [m for m in (hist or {}).get('status', {}).get('messages', []) if m[0] == 'execution_error']
                    err = msgs[0][1].get('exception_message', '') if msgs else 'keine Antwort'
                    if gc and gc.detect_oom(err):
                        raise SystemExit(f'BLOCKIERT bei {view}: Grafikspeicher voll ({err[:200]}). Die Qualität wird NICHT automatisch gesenkt – Unreal/Blender speichern und schließen oder warten, dann erneut starten.')
                    raise SystemExit(f'FEHLER bei {view}: {err[:400]}')
                imgs = [im for o in hist.get('outputs', {}).values() for im in o.get('images', [])]
                data = c.fetch_image(imgs[0]['filename'], imgs[0].get('subfolder', ''), imgs[0].get('type', 'output'))
                target = folder / f'{view}_v{ver}.png'
                with open(target, 'xb') as f:
                    f.write(data)
                g = post.get('pixel_grid')
                qc = imagecheck.check_image(target, (w // g) * g if g else w, (h // g) * g if g else h, pixel_grid=g, max_colors=post.get('colors'))
                meta = {'game': root.name, 'asset': a.asset, 'asset_type': a.art, 'view': view, 'style': prof['style_id'], 'model': 'FLUX.2 klein 4B (bf16, Apache 2.0)',
                        'prompt': prompt, 'seed': s, 'width': w, 'height': h, 'quality': q, 'postprocess': post, 'version': ver,
                        'design_hash': dhash, 'seconds': round(time.time() - t0, 1), 'created_at': now(), 'qc': qc, 'review': 'Zur Freigabe' if qc['ok'] else 'Technisch fehlerhaft',
                        'blender_file': None, 'unreal_asset': None}
                write_json(target.with_suffix('.json'), meta)
                checks = ' · '.join(('✓ ' if x['ok'] else '✗ ') + x['name'] for x in qc['checks'])
                out(f'BILD {target.relative_to(root)} · {w}×{h} · {meta["seconds"]} s · {checks}')
                if qc['ok']:
                    ok = True
                    break
                out('  Technische Prüfung nicht bestanden – neuer Versuch mit anderem Seed …' if attempt + 1 < qp['max_attempts'] else '  Technische Prüfung endgültig nicht bestanden.')
            orders = [o for o in orders if not (o['asset'] == a.asset and o['view'] == view)] + [{'asset': a.asset, 'type': a.art, 'view': view, 'details': a.details or '', 'state': 'Entwurf' if ok else 'Fehlerhaft', 'updated_at': now()}]
    write_json(root / 'referenzen' / 'auftraege.json', orders)


def cmd_freigeben(a):
    need_gameforge(find_game(a.spiel), 'Freigeben')
    root = find_game(a.spiel)
    src = (root / a.bild).resolve() if not Path(a.bild).is_absolute() else Path(a.bild).resolve()
    if root.resolve() not in src.parents or not src.is_file():
        raise SystemExit('Bild nicht im Spieleordner gefunden.')
    meta = read_json(src.with_suffix('.json'), {}) or {}
    if meta.get('review') == 'Technisch fehlerhaft':
        raise SystemExit('Technisch fehlerhafte Bilder können nicht freigegeben werden.')
    view = meta.get('view') or re.sub(r'_v\d+$', '', src.stem)
    asset_dir = src.parent.name
    dest = root / 'referenzen' / 'freigegeben' / asset_dir / f'{view}.png'
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        old = dest.parent / '_frueher'; old.mkdir(exist_ok=True)
        stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.move(str(dest), old / f'{view}_{stamp}.png')
        if dest.with_suffix('.json').exists():
            shutil.move(str(dest.with_suffix('.json')), old / f'{view}_{stamp}.json')
    shutil.copy2(src, dest)
    meta['review'] = 'Freigegeben'; meta['approved_at'] = now(); meta['approved_from'] = src.relative_to(root).as_posix()
    write_json(dest.with_suffix('.json'), meta)
    orders = ref_orders(root)
    for o in orders:
        if o.get('view') == view and safe_name(o.get('asset', '')) == asset_dir:
            o['state'] = 'Freigegeben'; o['updated_at'] = now()
    write_json(root / 'referenzen' / 'auftraege.json', orders)
    out(f'FREIGEGEBEN: {dest.relative_to(root)} (frühere Freigabe liegt ggf. unter _frueher/)')


def cmd_blender_auftrag(a):
    need_gameforge(find_game(a.spiel), 'Ein Blender-Auftrag')
    root = find_game(a.spiel)
    prof = read_json(root / 'art-direction.json')['profile']
    asset_dir = safe_name(a.asset)
    refs = sorted(p.relative_to(root).as_posix() for p in (root / 'referenzen' / 'freigegeben' / asset_dir).glob('*.png'))
    rigged = a.art in ('character', 'boss', 'npc', 'creature')
    spec = {'game': root.name, 'asset': a.asset, 'type': a.art, 'status': 'GEPLANT – NOCH NICHT MODELLIERT', 'created_at': now(),
            'references_approved': refs, 'description': a.details or '', 'target_dimensions': a.masse or 'aus Referenz/Beschreibung ableiten und im Bericht angeben',
            'art_direction': {k: prof.get(k) for k in ('style_id', 'style_label', 'lighting', 'color_palette', 'material_style', 'poly_budget', 'texture_budget', 'platform', 'engine')},
            'production': {'units': 'Meter, Unit Scale 1.0, Transforms angewendet', 'uv': 'überlappungsfrei' if prof.get('style_id') != 'low_poly' else 'einfach / Farbpalette',
                           'rigging': 'Unreal-kompatibles Skelett, ein Root-Knochen, Add Leaf Bones aus' if rigged else 'nicht erforderlich',
                           'export': {'format': 'FBX', 'apply_scale': 'FBX Units Scale', 'axes': 'Standard, per Testimport prüfen'}},
            'outputs': {'blend': f'blender/{asset_dir}/{asset_dir}.blend', 'fbx': f'export/{asset_dir}/{asset_dir}.fbx',
                        'unreal_destination': f'/Game/GAMEFORGE/{re.sub(r"[^A-Za-z0-9_]", "_", asset_dir)}'},
            'checks': ['Referenztreue', 'Maßstab', 'UV/Material', 'Geometrie (Normalen, nicht-mannigfaltige Kanten)', 'Unreal-Import', 'Testszene']}
    write_json(root / 'blender' / asset_dir / 'AUFTRAG.json', spec)
    out(f'AUFTRAG: blender/{asset_dir}/AUFTRAG.json · {len(refs)} freigegebene Referenzen' + ('' if refs else ' – ACHTUNG: keine freigegebene Referenz, nur Beschreibung'))
    out(f'Ziel: {spec["outputs"]["blend"]} und {spec["outputs"]["fbx"]} · Unreal: {spec["outputs"]["unreal_destination"]}')


def cmd_asset_pruefen(a):
    root = find_game(a.spiel)
    asset_dir = safe_name(a.asset)
    spec = read_json(root / 'blender' / asset_dir / 'AUFTRAG.json', {}) or {}
    o = spec.get('outputs', {'blend': f'blender/{asset_dir}/{asset_dir}.blend', 'fbx': f'export/{asset_dir}/{asset_dir}.fbx'})
    b, f = root / o['blend'], root / o['fbx']
    stage = 'geplant' if spec else 'kein Auftrag'
    if spec.get('references_approved'):
        stage = 'Referenzen freigegeben'
    out(f'.blend: {"OK " + str(b.stat().st_size) + " Bytes" if blend_ok(b) else ("UNGÜLTIG" if b.exists() else "fehlt")}  ({o["blend"]})')
    out(f'.fbx:   {"OK " + str(f.stat().st_size) + " Bytes" if fbx_ok(f) else ("UNGÜLTIG" if f.exists() else "fehlt")}  ({o["fbx"]})')
    if blend_ok(b) and fbx_ok(f):
        stage = 'Datei erstellt'
        ue = [p for p in (root / 'unreal').rglob('*.uasset') if 'GAMEFORGE' in p.as_posix() and asset_dir.replace(' ', '_').lower() in p.as_posix().lower()]
        out(f'Unreal-Assets: {len(ue)}')
        if ue:
            stage = 'Unreal importiert'
            qa = root / 'blender' / asset_dir / 'QA_BERICHT.md'
            if qa.is_file() and qa.stat().st_size > 40:
                stage = 'getestet'
    out(f'STUFE: {stage}   (geplant → Referenzen freigegeben → Datei erstellt → Unreal importiert → getestet → freigegeben)')


BLENDER_TEST = r'''
import bpy, json, os, sys
out = sys.argv[sys.argv.index('--') + 1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'; bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5)); o = bpy.context.active_object; o.name = 'GF_TestCrate'
m = o.modifiers.new('Bevel', 'BEVEL'); m.width = 0.02; m.segments = 3; bpy.ops.object.modifier_apply(modifier='Bevel')
o.data.materials.append(bpy.data.materials.new('M_GF_TestCrate'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'GF_TestCrate.blend'))
bpy.ops.export_scene.fbx(filepath=os.path.join(out, 'GF_TestCrate.fbx'), apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', add_leaf_bones=False)
print('GF_RESULT=' + json.dumps({'dims': [round(x, 3) for x in o.dimensions], 'version': bpy.app.version_string}))
'''


def cmd_blender_test(a):
    b = shutil.which('blender') or next(iter(sorted(Path(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Blender Foundation').glob('Blender*/blender.exe'), reverse=True)), None)
    if not b:
        raise SystemExit('Blender nicht gefunden.')
    outdir = GAMES / '_Systemtest' / dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir.mkdir(parents=True)
    script = outdir / 'test.py'; script.write_text(BLENDER_TEST, encoding='utf-8')
    with _GpuGuard('blender-test', 'blender_background', 1500):
        r = subprocess.run([str(b), '-b', '--factory-startup', '--python', str(script), '--', str(outdir)], capture_output=True, text=True, timeout=600, errors='replace', stdin=subprocess.DEVNULL)
    m = re.search(r'GF_RESULT=(\{.*\})', r.stdout)
    ok = bool(m) and blend_ok(outdir / 'GF_TestCrate.blend') and fbx_ok(outdir / 'GF_TestCrate.fbx')
    out(('BESTANDEN' if ok else 'FEHLGESCHLAGEN') + f' – Blender-Hintergrundtest in {outdir}' + (f' · {json.loads(m.group(1))}' if m else '\n' + (r.stdout + r.stderr)[-1500:]))


def cmd_dlc(a):
    need_gameforge(find_game(a.spiel), 'Ein DLC')
    root = find_game(a.spiel)
    d = root / 'dlc' / safe_name(a.titel)
    if d.exists():
        raise SystemExit('DLC existiert bereits.')
    for sub in ('referenzen/entwuerfe', 'referenzen/freigegeben', 'blender', 'export'):
        (d / sub).mkdir(parents=True)
    write_json(d / 'dlc.json', {'title': a.titel, 'base_game': root.name, 'requires_version': a.basisversion or read_json(root / 'spiel.json', {}).get('version'), 'status': 'Idee', 'created_at': now()})
    lines = [f'# DLC: {a.titel}', f'> Gehört zu {root.name}. Kanon des Hauptspiels gilt.', '']
    for _, label in DLC_FIELDS:
        lines += [f'## {label}', '', '(offen)', '']
    if a.idee:
        lines[lines.index('## Story & Kanon') + 2] = a.idee
    (d / 'DLC.md').write_text('\n'.join(lines), encoding='utf-8')
    out(f'DLC ANGELEGT: {d}')


def zip_folder(src, target):
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for p in sorted(src.rglob('*')):
            if p.is_file():
                z.write(p, Path(src.name) / p.relative_to(src), compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ('.zip', '.png', '.jpg', '.fbx', '.uasset') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(target) as z:
        bad = z.testzip()
        if bad:
            target.unlink()
            raise SystemExit('Sicherung fehlerhaft (' + bad + '). Nichts verändert.')
        return len(z.namelist())


def cmd_sichern(a):
    root = find_game(a.spiel)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    target = BACKUPS / f'{root.name}_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    n = zip_folder(root, target)
    out(f'GESICHERT: {target} ({n} Dateien, {target.stat().st_size // 1024} KB, geprüft)')


def cmd_loeschen(a):
    root = find_game(a.spiel)
    need_gameforge(root, 'Löschen')
    if a.bestaetigen != root.name:
        raise SystemExit(f'Zum Löschen muss --bestaetigen exakt „{root.name}“ lauten.')
    TRASH.mkdir(parents=True, exist_ok=True)
    target = TRASH / f'{root.name}_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    n = zip_folder(root, target)
    shutil.rmtree(root)
    out(f'IN DEN PAPIERKORB: {target} ({n} Dateien geprüft gesichert). Wiederherstellen: gf wiederherstellen "{target.name}"')


def cmd_wiederherstellen(a):
    p = TRASH / Path(a.datei).name
    if not p.is_file():
        p = BACKUPS / Path(a.datei).name
    if not p.is_file():
        raise SystemExit('Datei weder im Papierkorb noch bei den Sicherungen gefunden.')
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        top = {n.split('/')[0] for n in names}
        if len(top) != 1 or any('..' in n.split('/') or n.startswith('/') or ':' in n for n in names):
            raise SystemExit('Unerwarteter Inhalt – Wiederherstellung abgebrochen.')
        top_name = top.pop()
        base = FILMS if any(n == f'{top_name}/film.json' for n in names) else GAMES
        base.mkdir(parents=True, exist_ok=True)
        dest = base / top_name
        if dest.exists():
            raise SystemExit(f'„{dest.name}“ existiert bereits – nichts überschrieben. Vorher umbenennen.')
        z.extractall(base)
    for sub in (FILM_DIRS if base == FILMS else STANDARD_DIRS):
        (dest / sub).mkdir(parents=True, exist_ok=True)
    out(f'WIEDERHERGESTELLT: {dest}')


def cmd_comfy(a):
    c = comfy.Comfy(HOME, HOME / 'engines' / 'logs')
    if a.aktion == 'start':
        c.start(); out('ComfyUI läuft auf http://127.0.0.1:8188 (nur lokal).')
    elif a.aktion == 'stop':
        try:
            c._req('/free', {'unload_models': True, 'free_memory': True})
        except Exception:
            pass
        killed = False
        if os.name == 'nt':
            r = subprocess.run(['powershell', '-NoProfile', '-Command',
                                "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ComfyUI*main.py*--port 8188*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $_.ProcessId }"],
                               capture_output=True, text=True, timeout=30)
            killed = bool(r.stdout.strip())
        out('ComfyUI beendet, Grafikspeicher frei.' if killed else 'ComfyUI lief nicht (oder wurde nicht von GAMEFORGE gestartet).')
    else:
        st = c.online()
        out('ComfyUI läuft.' if st else 'ComfyUI läuft nicht.')
        if st:
            out(json.dumps(st.get('devices', []), ensure_ascii=False)[:600])


def cmd_migrieren(a):
    """Übernimmt Spiele aus der alten GAMEFORGE-Datenbank (nur lesend) in Spieleordner."""
    db = Path(a.db)
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    base = db.parent
    for g in con.execute('SELECT * FROM games'):
        bible = json.loads(g['bible'] or '{}')
        try:
            root = create_game(g['title'], genre=g['genre'], style=g['style'], camera=g['camera'], summary=g['summary'], engine=g['engine'], bible=bible,
                               extra={'status': g['status'], 'version': g['version'], 'migrated_from': f'GAMEFORGE-Datenbank ({g["id"]})'})
        except SystemExit as e:
            out(f'ÜBERSPRUNGEN {g["title"]}: {e}')
            continue
        meta = read_json(root / 'spiel.json'); meta['legacy_id'] = g['id']; write_json(root / 'spiel.json', meta)
        tasks = [dict(x) for x in con.execute('SELECT phase,title,acceptance,status,evidence FROM production_tasks WHERE game_id=? AND dlc_id IS NULL', (g['id'],))]
        if tasks:
            write_json(root / 'aufgaben.json', [{**t, 'status': {'Implementiert': 'Umgesetzt'}.get(t['status'], t['status'])} for t in tasks])
        orders = []
        for r in con.execute('SELECT * FROM ref_tasks WHERE game_id=?', (g['id'],)):
            orders.append({'asset': r['name'], 'type': r['category'], 'view': r['view'], 'details': r['details'], 'state': 'Freigegeben' if r['approved'] else 'Offen', 'updated_at': r['updated_at']})
            if r['image_path'] and (base / 'refs' / r['image_path']).is_file():
                sub = 'freigegeben' if r['approved'] else 'entwuerfe'
                dst = root / 'referenzen' / sub / safe_name(r['name']) / (f'{r["view"]}.png' if r['approved'] else f'{r["view"]}_v1.png')
                dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(base / 'refs' / r['image_path'], dst)
        write_json(root / 'referenzen' / 'auftraege.json', orders)
        for d in con.execute('SELECT * FROM dlcs WHERE game_id=?', (g['id'],)):
            dd = root / 'dlc' / safe_name(d['title']); dd.mkdir(parents=True, exist_ok=True)
            write_json(dd / 'dlc.json', {'title': d['title'], 'base_game': g['title'], 'requires_version': d['compatible_version'], 'status': d['status'], 'summary': d['summary']})
            des = json.loads(d['design'] or '{}')
            (dd / 'DLC.md').write_text(f'# DLC: {d["title"]}\n\n' + '\n'.join(f'## {k}\n\n{v or "(offen)"}\n' for k, v in des.items()), encoding='utf-8')
        n = 0
        for f in con.execute('SELECT * FROM imported_files WHERE game_id=?', (g['id'],)):
            src = base / 'imports' / f['stored_name']
            if src.is_file():
                dst = root / 'originale' / f['relpath']; dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    shutil.copy2(src, dst); n += 1
        for arc in con.execute('SELECT * FROM archives WHERE game_id=?', (g['id'],)):
            src = base / 'uploads' / arc['file_path']
            if src.is_file():
                dst = root / 'originale' / '_archive' / arc['original_name']; dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    shutil.copy2(src, dst); n += 1
        ideas = [dict(x) for x in con.execute("SELECT title,detail,section,status FROM idea_suggestions WHERE game_id=? AND status='Angenommen'", (g['id'],))]
        if ideas:
            write_json(root / 'ideen_angenommen.json', ideas)
        out(f'ÜBERNOMMEN: {g["title"]} → {root} ({len(orders)} Bildaufträge, {n} Originaldateien)')
    con.close()
    out('Die alte Datenbank wurde nur gelesen, nicht verändert.')


def cmd_gpu(a):
    if not gc:
        raise SystemExit('GPU-Wächter (gameforge_core) nicht gefunden.')
    out(gc.status_text())


def cmd_jobs(a):
    if not gjobs:
        raise SystemExit('Auftragskern (gameforge_core) nicht gefunden.')
    if a.aktion == 'liste':
        rows = gjobs.listing(a.projekt)
        if not rows:
            out('Keine Aufträge in der Warteschlange.')
        for r in rows:
            out(f'#{r["id"]} {r["status"]:<12} {r["project"]} · {r["title"]}' + (f' – {r["reason"]}' if r['reason'] else ''))
    elif a.aktion == 'arbeiten':
        n = gjobs.recover()
        if n:
            out(f'{n} abgebrochene Aufträge wieder eingereiht.')
        gjobs.work('gf', on_wait=lambda m: out('WARTET – ' + m), on_done=lambda r: out(f'#{r["id"]} → {r["status"]}' + (f' ({r["reason"]})' if r['reason'] else '')), max_idle_s=a.leerlauf)
    elif a.aktion in ('abbrechen', 'erneut'):
        if not a.id:
            raise SystemExit('Bitte Auftragsnummer angeben, z. B. gf jobs abbrechen 3')
        if not gjobs.get(a.id):
            raise SystemExit(f'Auftrag #{a.id} nicht gefunden.')
        try:
            (gjobs.cancel if a.aktion == 'abbrechen' else gjobs.retry)(a.id)
        except ValueError as e:
            raise SystemExit(str(e))
        out(f'#{a.id} → {gjobs.get(a.id)["status"]}')


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if stream.encoding and stream.encoding.lower() not in ('utf-8', 'utf8'):
            stream.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(prog='gf', description='GAMEFORGE-Werkzeug')
    sp = p.add_subparsers(dest='cmd', required=True)
    x = sp.add_parser('neu'); x.add_argument('--titel', required=True); x.add_argument('--typ', default='spiel', choices=['spiel', 'film'])
    x.add_argument('--laenge'); x.add_argument('--format'); x.add_argument('--basis'); x.add_argument('--idee'); x.add_argument('--genre'); x.add_argument('--stil')
    x.add_argument('--perspektive'); x.add_argument('--plattform'); x.add_argument('--wuensche'); x.add_argument('--kurz'); x.set_defaults(f=cmd_neu)
    sp.add_parser('liste').set_defaults(f=cmd_liste)
    x = sp.add_parser('erkennen'); x.add_argument('pfad', nargs='?', default='.'); x.set_defaults(f=cmd_erkennen)
    x = sp.add_parser('registrieren'); x.add_argument('--pfad', required=True); x.add_argument('--typ', required=True, choices=['spiel', 'film'])
    x.add_argument('--titel'); x.add_argument('--notiz'); x.set_defaults(f=cmd_registrieren)
    x = sp.add_parser('stand'); x.add_argument('spiel'); x.set_defaults(f=cmd_stand)
    sp.add_parser('system').set_defaults(f=cmd_system)
    x = sp.add_parser('prompt'); x.add_argument('spiel'); x.add_argument('--asset', required=True); x.add_argument('--art', default='character', choices=list(VIEWS))
    x.add_argument('--ansicht', default='front'); x.add_argument('--details'); x.set_defaults(f=cmd_prompt)
    x = sp.add_parser('bild'); x.add_argument('spiel'); x.add_argument('--asset', required=True); x.add_argument('--art', default='character', choices=list(VIEWS))
    x.add_argument('--ansichten'); x.add_argument('--details'); x.add_argument('--qualitaet', default='AUTO', choices=['AUTO', 'DRAFT', 'STANDARD', 'HIGH', 'CINEMATIC_MASTER'])
    x.add_argument('--neu', action='store_true'); x.set_defaults(f=cmd_bild)
    x = sp.add_parser('freigeben'); x.add_argument('spiel'); x.add_argument('bild'); x.set_defaults(f=cmd_freigeben)
    x = sp.add_parser('blender-auftrag'); x.add_argument('spiel'); x.add_argument('--asset', required=True); x.add_argument('--art', default='character', choices=list(VIEWS))
    x.add_argument('--details'); x.add_argument('--masse'); x.set_defaults(f=cmd_blender_auftrag)
    x = sp.add_parser('asset-pruefen'); x.add_argument('spiel'); x.add_argument('--asset', required=True); x.set_defaults(f=cmd_asset_pruefen)
    sp.add_parser('blender-test').set_defaults(f=cmd_blender_test)
    x = sp.add_parser('dlc'); x.add_argument('spiel'); x.add_argument('--titel', required=True); x.add_argument('--idee'); x.add_argument('--basisversion'); x.set_defaults(f=cmd_dlc)
    x = sp.add_parser('sichern'); x.add_argument('spiel'); x.set_defaults(f=cmd_sichern)
    x = sp.add_parser('loeschen'); x.add_argument('spiel'); x.add_argument('--bestaetigen', required=True); x.set_defaults(f=cmd_loeschen)
    x = sp.add_parser('wiederherstellen'); x.add_argument('datei'); x.set_defaults(f=cmd_wiederherstellen)
    x = sp.add_parser('comfy'); x.add_argument('aktion', choices=['start', 'stop', 'status']); x.set_defaults(f=cmd_comfy)
    sp.add_parser('gpu').set_defaults(f=cmd_gpu)
    x = sp.add_parser('jobs'); x.add_argument('aktion', nargs='?', default='liste', choices=['liste', 'arbeiten', 'abbrechen', 'erneut'])
    x.add_argument('id', nargs='?', type=int); x.add_argument('--projekt'); x.add_argument('--leerlauf', type=int, default=5); x.set_defaults(f=cmd_jobs)
    x = sp.add_parser('migrieren'); x.add_argument('--db', required=True); x.set_defaults(f=cmd_migrieren)
    a = p.parse_args(argv)
    a.f(a)


if __name__ == '__main__':
    main()
