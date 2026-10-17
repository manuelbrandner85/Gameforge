"""GAMEFORGE 2.0 – echte System-, Pipeline- und Projektprüfungen.

Grundsatz: Jeder Status stammt aus einer tatsächlich ausgeführten Prüfung
(Dateisystem, Prozessaufruf, Datenbank). Fehlt eine Prüfung, lautet der Status
"Unbekannt" oder "Nicht geprüft" – niemals "OK".
"""
from __future__ import annotations
import datetime as dt
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def _uid():
    return uuid.uuid4().hex[:16]


# ---------------------------------------------------------------- Programme finden

def find_blender():
    """Blender im PATH oder in der Standardinstallation finden (neueste Version)."""
    found = shutil.which('blender')
    if found:
        return found
    candidates = []
    for base in (os.environ.get('ProgramFiles', r'C:\Program Files'), os.environ.get('ProgramFiles(x86)', '')):
        if base:
            candidates += glob.glob(os.path.join(base, 'Blender Foundation', 'Blender*', 'blender.exe'))
    candidates.sort(key=lambda p: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', p)], reverse=True)
    return candidates[0] if candidates else None


def find_unreal():
    """Unreal-Engine-Installationen (Epic-Launcher-Standardpfad) auflisten."""
    base = os.environ.get('ProgramFiles', r'C:\Program Files')
    result = []
    for root in sorted(glob.glob(os.path.join(base, 'Epic Games', 'UE_*')), reverse=True):
        editor = os.path.join(root, 'Engine', 'Binaries', 'Win64', 'UnrealEditor-Cmd.exe')
        uat = os.path.join(root, 'Engine', 'Build', 'BatchFiles', 'RunUAT.bat')
        result.append({'version': os.path.basename(root).replace('UE_', ''), 'root': root,
                       'editor_cmd': editor if os.path.isfile(editor) else None,
                       'run_uat': uat if os.path.isfile(uat) else None})
    return result


# ---------------------------------------------------------------- Systemprüfung

_health_cache = {}
_health_lock = threading.Lock()


def _run(cmd, cwd=None, timeout=20):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           errors='replace', stdin=subprocess.DEVNULL)
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        return -2, 'Zeitüberschreitung'
    except OSError as e:
        return -3, str(e)


LOGIN_HINT = ('Claude Code ist auf diesem PC nicht angemeldet. So behebst du es: Eingabeaufforderung öffnen, '
              '„claude auth login“ eingeben und im Browser anmelden. Danach in GAMEFORGE „Erneut prüfen“ klicken.')
_auth_cache = {}


def claude_auth(refresh=False):
    """Echter Anmeldestatus über `claude auth status` (JSON). Ergebnis 60 s zwischengespeichert."""
    cached = _auth_cache.get('v')
    if cached and not refresh and time.time() - cached[0] < 60:
        return cached[1]
    claude = shutil.which('claude')
    result = {'checked': False, 'logged_in': None, 'method': None}
    if claude:
        code, out = _run([claude, 'auth', 'status'], timeout=30)
        try:
            data = json.loads(out[out.index('{'):out.rindex('}') + 1])
            result = {'checked': True, 'logged_in': bool(data.get('loggedIn')), 'method': data.get('authMethod')}
        except ValueError:
            pass
    _auth_cache['v'] = (time.time(), result)
    return result


def is_auth_error(text):
    t = (text or '').lower()
    return any(w in t for w in ('failed to authenticate', 'oauth', 'not logged in', 'please run /login', 'invalid api key', 'authentication'))


def parse_mcp_list(text):
    """Ausgabe von `claude mcp list` in Servername + echten Verbindungsstatus übersetzen."""
    servers = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'^([A-Za-z0-9_.@\-]+):\s+(.*)$', line)
        if not m or m.group(1).lower() in ('checking', 'note', 'warning', 'error'):
            continue
        rest = m.group(2)
        if '✓' in rest or 'Connected' in rest:
            state = 'Verbunden'
        elif '✗' in rest or 'Failed' in rest or 'failed' in rest:
            state = 'Fehlgeschlagen'
        elif 'auth' in rest.lower():
            state = 'Anmeldung nötig'
        else:
            state = 'Unbekannt'
        servers.append({'name': m.group(1), 'state': state, 'detail': rest[:300]})
    return servers


def system_health(workspace=None, refresh=False):
    """Echte Prüfung der lokalen Werkzeuge. Ergebnis wird 2 Minuten zwischengespeichert."""
    key = str(workspace or '')
    with _health_lock:
        cached = _health_cache.get(key)
        if cached and not refresh and time.time() - cached[0] < 120:
            return cached[1]
    cwd = workspace if workspace and Path(workspace).is_dir() else None
    claude = shutil.which('claude')
    claude_version = None
    mcp = {'checked': False, 'servers': [], 'message': ''}
    auth = claude_auth(refresh) if claude else {'checked': False, 'logged_in': None, 'method': None}
    if claude:
        code, out = _run([claude, '--version'], timeout=20)
        claude_version = out.strip().splitlines()[0][:80] if code == 0 and out.strip() else None
        code, out = _run([claude, 'mcp', 'list'], cwd=cwd, timeout=60)
        mcp['checked'] = code in (0, 1)
        mcp['servers'] = parse_mcp_list(out)
        if 'No MCP servers configured' in out:
            mcp['message'] = 'In Claude Code ist kein MCP-Server eingerichtet. Blender und Unreal sind für Claude Code damit noch nicht erreichbar.'
        elif code == -2:
            mcp['message'] = 'Die MCP-Prüfung hat zu lange gedauert (Zeitlimit).'
        elif not mcp['servers']:
            mcp['message'] = 'Keine MCP-Server erkannt. Ausgabe: ' + out.strip()[:300]
        else:
            mcp['message'] = 'Ergebnis der Live-Prüfung durch "claude mcp list".'
    blender = find_blender()
    unreal = find_unreal()
    names = [s['name'].lower() for s in mcp['servers']]
    connected = [s['name'].lower() for s in mcp['servers'] if s['state'] == 'Verbunden']
    result = {
        'checked_at': now(),
        'workspace': key,
        'claude': {'found': bool(claude), 'path': claude, 'version': claude_version,
                   'logged_in': auth['logged_in'], 'auth_checked': auth['checked'], 'auth_method': auth['method'],
                   'login_hint': LOGIN_HINT if auth['logged_in'] is False else '',
                   'note': 'Programm gefunden und Version abgefragt.' if claude_version else
                           ('Claude Code gefunden, Versionsabfrage fehlgeschlagen.' if claude else 'Claude Code ist nicht installiert oder nicht im PATH.')},
        'mcp': mcp,
        'blender': {'found': bool(blender), 'path': blender,
                    'mcp_configured': any('blender' in n for n in names),
                    'mcp_connected': any('blender' in n for n in connected)},
        'unreal': {'found': bool(unreal), 'installs': unreal,
                   'mcp_configured': any('unreal' in n for n in names),
                   'mcp_connected': any('unreal' in n for n in connected)},
    }
    with _health_lock:
        _health_cache[key] = (time.time(), result)
    return result


# ---------------------------------------------------------------- Projekt-Scanner (#1, Teilumfang)

def project_scan(store, gid):
    """Prüft importierte Originaldateien: fehlende Dateien, Hash-Abweichungen, Duplikate."""
    if not store.game(gid):
        raise ValueError('Spiel nicht gefunden')
    files = store.all('SELECT * FROM imported_files WHERE game_id=? ORDER BY created_at', (gid,))
    archives = store.all('SELECT * FROM archives WHERE game_id=? ORDER BY created_at', (gid,))
    missing, mismatched, by_hash = [], [], {}
    for f in files:
        path = store.base / 'imports' / f['stored_name']
        if not path.is_file():
            missing.append({'name': f['relpath'], 'id': f['id'], 'type': 'Originaldatei'})
            continue
        if path.stat().st_size != f['size']:
            mismatched.append({'name': f['relpath'], 'id': f['id'], 'problem': 'Dateigröße weicht ab'})
        by_hash.setdefault(f['sha256'], []).append(f['relpath'])
    for a in archives:
        path = store.base / 'uploads' / a['file_path']
        if not path.is_file():
            missing.append({'name': a['original_name'], 'id': a['id'], 'type': 'Archiv'})
        by_hash.setdefault(a['sha256'], []).append(a['original_name'])
    duplicates = [{'sha256': h[:16], 'files': names} for h, names in by_hash.items() if len(names) > 1]
    refs = store.refs(gid)
    ref_missing = [r['name'] + ' / ' + r['view'] for r in refs if r['image_path'] and not (store.base / 'refs' / r['image_path']).is_file()]
    return {'checked_at': now(), 'files_checked': len(files), 'archives_checked': len(archives),
            'missing': missing, 'size_mismatch': mismatched, 'duplicates': duplicates,
            'reference_images_missing': ref_missing,
            'ok': not (missing or mismatched or ref_missing),
            'note': 'Geprüft: Vorhandensein, Dateigröße und identische Inhalte (SHA-256). '
                    'Inhaltliche Widersprüche in Story oder Code erkennt dieser Scanner noch nicht.'}


# ---------------------------------------------------------------- Asset-Pipeline-Status

PIPELINE_STAGES = ['geplant', 'Referenzen freigegeben', 'Blender läuft', 'Datei erstellt',
                   'Unreal importiert', 'getestet', 'freigegeben']


def _file_kind_ok(path):
    """Prüft den Dateikopf: echte .blend / .fbx / .glb statt leerer Platzhalter."""
    try:
        with open(path, 'rb') as f:
            head = f.read(32)
    except OSError:
        return False
    suffix = path.suffix.lower()
    if suffix == '.blend':
        return head.startswith(b'BLENDER') or head[:2] == b'\x28\xb5' or head[:2] == b'\x1f\x8b'
    if suffix == '.fbx':
        return head.startswith(b'Kaydara FBX Binary') or head.lstrip().startswith(b';')
    if suffix == '.glb':
        return head.startswith(b'glTF')
    if suffix == '.gltf':
        return head.lstrip().startswith(b'{')
    return path.stat().st_size > 0


def _describe(path, root):
    if not path.is_file():
        return {'path': str(path.relative_to(root)) if root in path.parents else str(path), 'exists': False}
    return {'path': str(path.relative_to(root)), 'exists': True, 'size': path.stat().st_size,
            'format_ok': _file_kind_ok(path),
            'modified': dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(timespec='seconds')}


def pipeline_assets(store, gid):
    settings = store.direct.settings(gid)
    ws = settings.get('workspace')
    if not ws or not Path(ws).is_dir():
        return {'workspace': None, 'assets': [], 'stages': PIPELINE_STAGES,
                'message': 'Noch kein lokaler Projektordner verbunden.'}
    root = Path(ws).resolve()
    base = root / '.gameforge' / 'asset_pipeline'
    jobs = store.direct.jobs(gid)
    approvals = {r['asset_id']: r for r in store.all('SELECT * FROM asset_approvals WHERE game_id=?', (gid,))}
    assets = []
    if base.is_dir():
        for spec_file in sorted(base.glob('*/asset_spec.json'), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                spec = json.loads(spec_file.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                continue
            if spec.get('game_id') != gid:
                continue
            aid = spec.get('asset_id', spec_file.parent.name)
            outputs = spec.get('outputs', {})
            blend = _describe(root / outputs.get('blend', f'Assets/{aid}/{aid}.blend'), root)
            fbx = _describe(root / outputs.get('fbx', f'Assets/{aid}/{aid}.fbx'), root)
            uprojects = list(root.glob('*.uproject'))
            content = (root / 'Content' / 'GAMEFORGE' / aid)
            uassets = sorted(str(p.relative_to(root)) for p in content.rglob('*.uasset')) if content.is_dir() else []
            qa = spec_file.parent / 'QA_REPORT.md'
            qa_ok = qa.is_file() and qa.stat().st_size > 40
            running = [j for j in jobs if j['status'] == 'Läuft' and aid in (j.get('instruction') or '')]
            failed = [j for j in jobs if j['status'] == 'Fehlgeschlagen' and aid in (j.get('instruction') or '')]
            stage = 'geplant'
            if spec.get('references'):
                stage = 'Referenzen freigegeben'
            if running:
                stage = 'Blender läuft'
            if blend['exists'] and blend.get('format_ok') and fbx['exists'] and fbx.get('format_ok'):
                stage = 'Datei erstellt'
                if uassets:
                    stage = 'Unreal importiert'
                    if qa_ok:
                        stage = 'getestet'
                        if aid in approvals:
                            stage = 'freigegeben'
            assets.append({'asset_id': aid, 'name': spec.get('name'), 'type': spec.get('type'),
                           'stage': stage, 'stage_index': PIPELINE_STAGES.index(stage),
                           'references': len(spec.get('references', [])),
                           'blend': blend, 'fbx': fbx, 'unreal_assets': uassets[:30],
                           'unreal_project_found': bool(uprojects),
                           'qa_report': str(qa.relative_to(root)) if qa.is_file() else None,
                           'job_running': bool(running), 'last_error_job': failed[0]['id'] if failed else None,
                           'created_at': spec.get('created_at')})
    return {'workspace': str(root), 'assets': assets, 'stages': PIPELINE_STAGES,
            'message': 'Jede Stufe wird aus echten Dateien abgeleitet: .blend/.fbx mit gültigem Dateikopf, '
                       '.uasset unter Content/GAMEFORGE/<Asset-ID>, QA_REPORT.md und deiner Freigabe.'}


def approve_asset(store, gid, aid):
    data = pipeline_assets(store, gid)
    asset = next((a for a in data['assets'] if a['asset_id'] == aid), None)
    if not asset:
        raise ValueError('Asset-Auftrag nicht gefunden')
    if asset['stage'] not in ('getestet', 'freigegeben'):
        raise ValueError('Freigabe erst möglich, wenn Unreal-Import und Testbericht nachweisbar vorliegen (aktuell: ' + asset['stage'] + ').')
    store.execute('INSERT OR REPLACE INTO asset_approvals(game_id,asset_id,approved_at) VALUES(?,?,?)', (gid, aid, now()))
    return {'asset_id': aid, 'stage': 'freigegeben'}


# ---------------------------------------------------------------- Blender-Echttest

BLENDER_TEST_SCRIPT = r'''
import bpy, json, os, sys
out = sys.argv[sys.argv.index('--') + 1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
# 1-m-Referenzwürfel (Maßstabsprüfung in Unreal: 100 cm), Einheiten Meter / Scale 1.0
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = 'GF_TestCrate'
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bev = obj.modifiers.new('Bevel', 'BEVEL'); bev.width = 0.02; bev.segments = 3
mat = bpy.data.materials.new('M_GF_TestCrate')
obj.data.materials.append(mat)
bpy.ops.object.modifier_apply(modifier='Bevel')
blend = os.path.join(out, 'GF_TestCrate.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend)
exported = None
try:
    fbx = os.path.join(out, 'GF_TestCrate.fbx')
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', add_leaf_bones=False)
    exported = fbx
except Exception as e:
    glb = os.path.join(out, 'GF_TestCrate.glb')
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB')
    exported = glb
dims = list(obj.dimensions)
print('GAMEFORGE_RESULT=' + json.dumps({'blend': blend, 'export': exported, 'dimensions_m': [round(x, 4) for x in dims],
      'vertices': len(obj.data.vertices), 'materials': [m.name for m in obj.data.materials],
      'blender_version': bpy.app.version_string}))
'''


def start_blender_test(store, gid):
    """Startet Blender im Hintergrund, erstellt ein kleines Testobjekt, speichert .blend + Export
    und prüft die Dateien danach unabhängig. Läuft als normaler Auftrag im Protokoll."""
    store.direct._check_game(gid)
    cfg = store.direct.settings(gid)
    if not cfg.get('workspace') or not Path(cfg['workspace']).is_dir():
        raise ValueError('Zuerst einen Projektordner verbinden.')
    blender = find_blender()
    if not blender:
        raise ValueError('Blender wurde auf diesem PC nicht gefunden.')
    with store.direct.guard:
        if any(j['status'] == 'Läuft' for j in store.direct.jobs(gid)):
            raise ValueError('Für dieses Spiel läuft bereits ein Auftrag.')
        jid = _uid()
        out = Path(cfg['workspace']).resolve() / '.gameforge' / 'system_tests' / ('blender_' + jid)
        store.execute('INSERT INTO direct_jobs(id,game_id,kind,task_id,status,instruction,created_at,user_instruction) VALUES(?,?,?,?,?,?,?,?)',
                      (jid, gid, 'blender_test', None, 'Läuft', 'Blender-Echttest: Testobjekt erzeugen, .blend speichern, exportieren, prüfen.', now(), 'Blender-Echttest'))
    threading.Thread(target=_blender_test_worker, args=(store, jid, blender, out), daemon=True).start()
    return store.direct.job(gid, jid)


def _blender_test_worker(store, jid, blender, out):
    log, code = '', -1
    try:
        script = out.parent / ('blender_test_' + jid + '.py')
        out.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(BLENDER_TEST_SCRIPT, encoding='utf-8')
        r = subprocess.run([blender, '-b', '--factory-startup', '--python', str(script), '--', str(out)],
                           capture_output=True, text=True, timeout=600, errors='replace', stdin=subprocess.DEVNULL)
        script.unlink(missing_ok=True)
        code = r.returncode
        match = re.search(r'GAMEFORGE_RESULT=(\{.*\})', r.stdout or '')
        if not match:
            code = code or 1
            log = 'Blender hat kein Ergebnis gemeldet.\n' + ((r.stdout or '') + (r.stderr or ''))[-6000:]
        else:
            res = json.loads(match.group(1))
            checks = []
            for key in ('blend', 'export'):
                p = Path(res[key])
                ok = p.is_file() and p.stat().st_size > 0 and _file_kind_ok(p)
                checks.append(f"{'OK' if ok else 'FEHLER'}  {p.name}  ({p.stat().st_size if p.is_file() else 0} Bytes, Dateikopf {'gültig' if ok else 'ungültig'})")
                if not ok:
                    code = 1
            log = ('Blender ' + res['blender_version'] + ' im Hintergrund ausgeführt.\n'
                   + '\n'.join(checks) + '\n'
                   + f"Maße (m): {res['dimensions_m']}  ·  Eckpunkte: {res['vertices']}  ·  Materialslots: {', '.join(res['materials'])}\n"
                   + 'Ordner: ' + str(out) + '\n'
                   + 'Geprüft: Blender startet, speichert .blend und exportiert. Nicht geprüft: Blender-MCP und Unreal-Import.')
    except subprocess.TimeoutExpired:
        code, log = -2, 'Blender hat das Zeitlimit von 10 Minuten überschritten.'
    except Exception as e:  # Fehler ehrlich protokollieren
        code, log = -3, 'Fehler: ' + str(e)[:800]
    store.execute('UPDATE direct_jobs SET status=?,log=?,exit_code=?,ended_at=? WHERE id=?',
                  ('Abgeschlossen' if code == 0 else 'Fehlgeschlagen', log, code, now(), jid))


# ---------------------------------------------------------------- Startseite

def next_steps(store, gid):
    c = store.completeness(gid)
    steps = []
    if c['missing_sections']:
        steps.append({'text': f"{len(c['missing_sections'])} Pflichtbereiche der Spielbibel ausfüllen (z. B. {c['missing_sections'][0]})", 'area': 'studio', 'tab': 'bible'})
    if c['reference_open']:
        steps.append({'text': f"{c['reference_open']} Referenzbilder in ChatGPT erzeugen, importieren und freigeben", 'area': 'studio', 'tab': 'refs'})
    if not c['full_source_imported']:
        steps.append({'text': 'Vorhandenes Original-Projekt als Vollprojekt-ZIP ins Archiv legen', 'area': 'archive', 'tab': 'zips'})
    if not store.direct.settings(gid).get('workspace'):
        steps.append({'text': 'Lokalen Projektordner für die Produktion verbinden', 'area': 'production', 'tab': 'direct'})
    if not steps:
        steps.append({'text': 'Nächste Entwicklungsaufgabe in „Aufgaben A–Z“ starten', 'area': 'production', 'tab': 'tasks'})
    return steps[:4]


def home_overview(store):
    games = store.games()
    rows = []
    for g in games:
        c = store.completeness(g['id'])
        jobs = store.direct.jobs(g['id'])[:3]
        rows.append({'id': g['id'], 'title': g['title'], 'status': g['status'], 'version': g['version'],
                     'summary': g['summary'], 'updated_at': g['updated_at'], 'dlc_count': g['dlc_count'],
                     'sections_missing': len(c['missing_sections']), 'reference_open': c['reference_open'],
                     'reference_total': c['reference_total'], 'tasks_total': c['tasks_total'],
                     'tasks_approved': c['tasks_approved'], 'tasks_tested': c['tasks_tested'],
                     'full_source_imported': c['full_source_imported'],
                     'workspace': store.direct.settings(g['id']).get('workspace') or '',
                     'recent_jobs': [{'kind': j['kind'], 'status': j['status'], 'created_at': j['created_at']} for j in jobs],
                     'next_steps': next_steps(store, g['id'])})
    return {'games': rows, 'data_dir': str(store.base), 'schema_version': store.schema_version}


# ---------------------------------------------------------------- Ehrlicher Roadmap-Status

ROADMAP_STATUS = {
    1: ('teilweise umgesetzt', 'Projekt-Scanner prüft Vorhandensein, Dateigröße und SHA-256-Duplikate (Archiv › Prüfen). Story-/Code-Konfliktanalyse fehlt.'),
    2: ('Grundlage vorhanden', 'Spielbibel mit 31 Bereichen und Chat-Änderungsentwürfe. Keine automatische Kanon-Konfliktprüfung.'),
    8: ('teilweise umgesetzt', 'Blender-Auftrag, Blender-Echttest (Hintergrundlauf mit .blend/Export) und Dateiprüfung. Modellierung selbst erfolgt durch Claude + MCP.'),
    10: ('Grundlage vorhanden', 'Aufgaben A–Z mit Pflicht-Prüfbeleg. Kein automatischer QA-Agentenlauf.'),
    14: ('Grundlage vorhanden', 'Bildformatprüfung beim Import und manuelle Freigabe. Keine inhaltliche Bildprüfung.'),
    15: ('teilweise umgesetzt', 'DLCs mit eigener Planung, Aufgaben, Referenzen, Chat und Export. Kompatibilitätsprüfung fehlt.'),
    16: ('Grundlage vorhanden', 'Versionsstände mit Wiederherstellung.'),
    18: ('teilweise umgesetzt', 'Claude-Produktionspaket als ZIP mit Spielbibel, Referenzen, Aufgaben und 20 Agenten.'),
    20: ('Grundlage vorhanden', 'Windows-Build über RunUAT als Auftrag. Kein Veröffentlichungsprozess.'),
    25: ('teilweise umgesetzt', 'Asset-Pipeline prüft .blend/.fbx auf Dateikopf und Größe sowie .uasset-Dateien im Unreal-Projekt.'),
}


def roadmap_status(roadmap):
    out = []
    for f in roadmap.get('features', []):
        status, note = ROADMAP_STATUS.get(f['id'], ('geplant', 'Noch nicht gebaut.'))
        out.append({'id': f['id'], 'title': f['title'], 'phase': f['phase'], 'status': status, 'evidence': note})
    return {'features': out, 'rejected': roadmap.get('rejected', []),
            'counts': {s: sum(1 for x in out if x['status'] == s) for s in ('geplant', 'Grundlage vorhanden', 'teilweise umgesetzt', 'fertig')}}


# ---------------------------------------------------------------- Lokale Statusantwort (keine KI)

def status_answer(store, gid, dlc_id=None):
    """Faktenbasierte Antwort aus der Datenbank – für Fragen wie „Was ist wirklich fertig?“."""
    g = store.game(gid)
    c = store.completeness(gid)
    jobs = store.direct.jobs(gid)
    pipe = pipeline_assets(store, gid)
    lines = [f"Stand von {g['title']} laut GAMEFORGE-Daten (keine KI-Einschätzung):",
             f"• Spielbibel: {len(c['missing_sections'])} Pflichtbereiche noch leer.",
             f"• Referenzbilder: {c['reference_approved']} freigegeben, {c['reference_open']} Pflichtbilder offen (von {c['reference_total']}).",
             f"• Entwicklungsaufgaben: {c['tasks_approved']} von {c['tasks_total']} abgenommen, {c['tasks_tested']} getestet oder abgenommen.",
             f"• Original-Vollprojekt im Archiv: {'ja' if c['full_source_imported'] else 'nein'}."]
    if pipe['assets']:
        lines.append('• 3D-Assets: ' + ', '.join(f"{a['name']} ({a['stage']})" for a in pipe['assets'][:6]) + '.')
    else:
        lines.append('• 3D-Assets: noch kein Blender/Unreal-Auftrag angelegt.')
    finished = [j for j in jobs if j['status'] == 'Abgeschlossen']
    failed = [j for j in jobs if j['status'] == 'Fehlgeschlagen']
    lines.append(f"• Lokale Claude-/Blender-Aufträge: {len(finished)} abgeschlossen, {len(failed)} fehlgeschlagen, "
                 f"{sum(j['status'] == 'Läuft' for j in jobs)} laufen gerade.")
    lines.append('• Die 20 Agenten sind als Rollen eingerichtet. Echte Agentenarbeit zeigt nur die Live-Übersicht unter Produktion.')
    return '\n'.join(lines)


STATUS_WORDS = ('wie weit', 'was ist fertig', 'wirklich fertig', 'status', 'stand ', 'was fehlt', 'fortschritt')


def is_status_question(text):
    t = text.lower()
    return any(w in t for w in STATUS_WORDS)
