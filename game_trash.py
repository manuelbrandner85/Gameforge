"""Spiele löschen – mit Papierkorb und Wiederherstellung.

Ablauf beim Löschen:
1. Alle Datensätze des Spiels (inkl. DLCs, Referenzen, Chat, Aufgaben, Aufträge) und alle zugehörigen
   Dateien (Archive, Referenzbilder, importierte Originale) werden in ein ZIP im Papierkorb geschrieben.
2. Das ZIP wird vollständig geprüft (CRC aller Einträge).
3. Erst danach werden Datensätze und Dateien aus der aktiven Bibliothek entfernt.
Lokale Projektordner (Unreal/Blender) werden NIE gelöscht – sie gehören dir.
"""
from __future__ import annotations
import datetime as dt
import json
import re
import zipfile
from pathlib import Path

# Reihenfolge: abhängige Tabellen zuerst (Fremdschlüssel).
TABLES = ['ref_images', 'ref_jobs', 'art_profiles', 'asset_approvals', 'direct_jobs', 'direct_settings', 'production_tasks', 'idea_changes',
          'idea_suggestions', 'idea_messages', 'imported_files', 'snapshots', 'archives', 'ref_tasks', 'dlcs', 'games']
NAME_RE = re.compile(r'^[A-Za-z0-9_-]+\.zip$')


def _trash(store):
    folder = store.base / 'papierkorb'
    folder.mkdir(exist_ok=True)
    return folder


def _files_of(store, gid):
    """(Pfad im ZIP, echter Pfad) aller Dateien, die ausschließlich diesem Spiel gehören."""
    out = []
    for a in store.all('SELECT file_path FROM archives WHERE game_id=?', (gid,)):
        out.append(('files/uploads/' + a['file_path'], store.base / 'uploads' / a['file_path']))
    for r in store.all('SELECT image_path FROM ref_tasks WHERE game_id=? AND image_path IS NOT NULL', (gid,)):
        out.append(('files/refs/' + r['image_path'], store.base / 'refs' / r['image_path']))
    for f in store.all('SELECT stored_name FROM imported_files WHERE game_id=?', (gid,)):
        out.append(('files/imports/' + f['stored_name'], store.base / 'imports' / f['stored_name']))
    gen = store.base / 'refs' / 'generated' / gid
    if gen.is_dir():
        for p in sorted(gen.iterdir()):
            if p.is_file():
                out.append(('files/generated/' + gid + '/' + p.name, p))
    return out


def delete_game(store, gid, confirm_title):
    game = store.game(gid)
    if not game:
        raise ValueError('Spiel nicht gefunden')
    if str(confirm_title).strip() != game['title']:
        raise ValueError('Zur Sicherheit bitte den Spielnamen exakt so eingeben, wie er angezeigt wird: ' + game['title'])
    if any(j['status'] == 'Läuft' for j in store.direct.jobs(gid)):
        raise ValueError('Für dieses Spiel läuft gerade ein Auftrag. Bitte warten, bis er beendet ist.')
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = re.sub(r'[^A-Za-z0-9_-]+', '_', game['title'])[:40].strip('_') or 'spiel'
    target = _trash(store) / f'{slug}_{gid}_{stamp}.zip'
    with store.lock:
        rows = {t: store.all(f'SELECT * FROM {t} WHERE {"id" if t == "games" else "game_id"}=?', (gid,)) for t in TABLES}
        files = _files_of(store, gid)
        workspace = (store.direct.settings(gid) or {}).get('workspace') or ''
        meta = {'format': 'gameforge-trash-1', 'game_id': gid, 'title': game['title'], 'deleted_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
                'row_counts': {t: len(v) for t, v in rows.items()}, 'file_count': sum(1 for _, p in files if p.is_file()),
                'workspace_not_deleted': workspace}
        try:
            with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, allowZip64=True) as z:
                z.writestr('meta.json', json.dumps(meta, ensure_ascii=False, indent=2))
                z.writestr('data.json', json.dumps(rows, ensure_ascii=False))
                for arc, path in files:
                    if path.is_file():
                        z.write(path, arc, compress_type=zipfile.ZIP_STORED if path.suffix.lower() == '.zip' else zipfile.ZIP_DEFLATED)
            with zipfile.ZipFile(target) as z:
                bad = z.testzip()
                if bad:
                    raise ValueError('Sicherung im Papierkorb ist fehlerhaft (' + bad + '). Es wurde nichts gelöscht.')
        except Exception:
            target.unlink(missing_ok=True)
            raise
        # Erst jetzt löschen – in einer Transaktion.
        try:
            for t in TABLES:
                store.conn.execute(f'DELETE FROM {t} WHERE {"id" if t == "games" else "game_id"}=?', (gid,))
            store.conn.commit()
        except Exception:
            store.conn.rollback()
            raise
    removed = 0
    for _, path in files:
        if path.is_file():
            path.unlink()
            removed += 1
    gen = store.base / 'refs' / 'generated' / gid
    if gen.is_dir() and not any(gen.iterdir()):
        gen.rmdir()
    return {'deleted': gid, 'title': game['title'], 'trash_file': target.name, 'files_moved': removed,
            'workspace_kept': workspace,
            'note': 'Spiel liegt im Papierkorb und kann wiederhergestellt werden.' + (
                f' Der lokale Projektordner {workspace} wurde nicht angerührt.' if workspace else '')}


def trash_list(store):
    items = []
    for p in sorted(_trash(store).glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with zipfile.ZipFile(p) as z:
                meta = json.loads(z.read('meta.json'))
        except (zipfile.BadZipFile, KeyError, ValueError, OSError):
            meta = {'title': p.name, 'game_id': None, 'deleted_at': None, 'broken': True}
        items.append({'name': p.name, 'size': p.stat().st_size, 'title': meta.get('title'), 'game_id': meta.get('game_id'),
                      'deleted_at': meta.get('deleted_at'), 'file_count': meta.get('file_count'),
                      'workspace_not_deleted': meta.get('workspace_not_deleted', ''), 'broken': meta.get('broken', False),
                      'restorable': not meta.get('broken') and not store.game(meta.get('game_id') or '')})
    return items


def _trash_file(store, name):
    if not NAME_RE.match(str(name)):
        raise ValueError('Ungültiger Papierkorb-Eintrag')
    p = _trash(store) / name
    if not p.is_file():
        raise ValueError('Eintrag nicht im Papierkorb gefunden')
    return p


def restore_game(store, name):
    p = _trash_file(store, name)
    with zipfile.ZipFile(p) as z:
        meta = json.loads(z.read('meta.json'))
        rows = json.loads(z.read('data.json'))
        gid = meta['game_id']
        if store.game(gid):
            raise ValueError('Ein Spiel mit dieser ID existiert bereits – Wiederherstellung abgebrochen, damit nichts überschrieben wird.')
        members = set(z.namelist())
        expected = []
        gen_prefix = 'files/generated/' + gid + '/'
        for name in members:
            if name.startswith(gen_prefix) and '/' not in name[len(gen_prefix):] and name[len(gen_prefix):]:
                (store.base / 'refs' / 'generated' / gid).mkdir(parents=True, exist_ok=True)
                expected.append((name, store.base / 'refs' / 'generated' / gid / name[len(gen_prefix):]))
        for a in rows.get('archives', []):
            expected.append(('files/uploads/' + a['file_path'], store.base / 'uploads' / a['file_path']))
        for r in rows.get('ref_tasks', []):
            if r.get('image_path'):
                expected.append(('files/refs/' + r['image_path'], store.base / 'refs' / r['image_path']))
        for f in rows.get('imported_files', []):
            expected.append(('files/imports/' + f['stored_name'], store.base / 'imports' / f['stored_name']))
        written = []
        try:
            for arc, dest in expected:
                if arc not in members:
                    continue
                if dest.exists():
                    raise ValueError('Datei existiert bereits: ' + dest.name)
                if not dest.resolve().is_relative_to(store.base.resolve()):
                    raise ValueError('Unsicherer Pfad im Papierkorb-Eintrag')
                with z.open(arc) as src, open(dest, 'xb') as out:
                    while chunk := src.read(4 * 1024 * 1024):
                        out.write(chunk)
                written.append(dest)
            with store.lock:
                try:
                    for t in reversed(TABLES):
                        cols = [c[1] for c in store.conn.execute(f'PRAGMA table_info({t})')]
                        for row in rows.get(t, []):
                            keys = [k for k in row if k in cols]
                            store.conn.execute(f'INSERT INTO {t}({",".join(keys)}) VALUES({",".join("?" * len(keys))})', [row[k] for k in keys])
                    store.conn.commit()
                except Exception:
                    store.conn.rollback()
                    raise
        except Exception:
            for d in written:
                d.unlink(missing_ok=True)
            raise
    p.rename(p.with_name(p.stem + '.wiederhergestellt'))
    return {'restored': gid, 'title': meta['title'], 'files': len(written)}


def purge(store, name, confirm):
    p = _trash_file(store, name)
    if confirm != 'ENDGÜLTIG':
        raise ValueError('Zum endgültigen Löschen bitte ENDGÜLTIG eingeben.')
    p.unlink()
    return {'purged': name}
