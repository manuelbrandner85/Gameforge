"""Reference Engine: persistente Warteschlange, ein GPU-Auftrag gleichzeitig, echte Statusmeldungen."""
from __future__ import annotations
import datetime as dt
import json
import shutil
import threading
import time
import uuid
from pathlib import Path

from . import art_direction, comfy as comfy_mod, hardware, imagecheck, models, prompts, quality

JOB_STATES = ('Wartend', 'Aktiv', 'Abgeschlossen', 'Fehlgeschlagen', 'Abgebrochen')
REVIEW_STATES = ('Zur Freigabe', 'Freigegeben', 'Abgelehnt', 'Ersetzt', 'Technisch fehlerhaft')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def uid():
    return uuid.uuid4().hex[:16]


SCHEMA = '''
CREATE TABLE IF NOT EXISTS art_profiles(game_id TEXT PRIMARY KEY REFERENCES games(id), profile TEXT NOT NULL,
  source TEXT NOT NULL, approved INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ref_jobs(id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id), dlc_id TEXT,
  ref_task_id TEXT, asset_name TEXT NOT NULL, category TEXT NOT NULL, view TEXT NOT NULL, style_id TEXT NOT NULL,
  model_id TEXT NOT NULL, quality TEXT NOT NULL, variant INTEGER NOT NULL DEFAULT 0, prompt TEXT NOT NULL,
  design_hash TEXT NOT NULL, seed INTEGER NOT NULL, width INTEGER NOT NULL, height INTEGER NOT NULL,
  postprocess TEXT NOT NULL DEFAULT '{}', status TEXT NOT NULL, step TEXT NOT NULL DEFAULT '', comfy_prompt_id TEXT,
  error TEXT NOT NULL DEFAULT '', attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 2,
  image_id TEXT, qc TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, started_at TEXT, ended_at TEXT);
CREATE TABLE IF NOT EXISTS ref_images(id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id), ref_task_id TEXT,
  job_id TEXT, file TEXT NOT NULL, version INTEGER NOT NULL, meta TEXT NOT NULL, review TEXT NOT NULL, created_at TEXT NOT NULL);
'''


class ReferenceEngine:
    def __init__(self, store, app_root):
        self.store = store
        self.app_root = Path(app_root)
        self.out_dir = store.base / 'refs' / 'generated'
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.comfy = comfy_mod.Comfy(app_root, store.base / 'logs')
        self.wake = threading.Event()
        self.cancel_flags = set()
        self.worker = None
        self.lock = threading.RLock()
        # Unterbrochene Aufträge nach Neustart wieder einreihen (Wiederaufnahme).
        store.execute("UPDATE ref_jobs SET status='Wartend', step='Nach Neustart wieder eingereiht' WHERE status='Aktiv'")
        if store.one("SELECT id FROM ref_jobs WHERE status='Wartend' LIMIT 1"):
            self._ensure_worker()

    # ------------------------------------------------------------ Profile & Status
    def profile(self, gid):
        return art_direction.ensure_profile(self.store, gid)

    def status(self, gid=None):
        st = self.store
        counts = {s: st.one('SELECT COUNT(*) n FROM ref_jobs WHERE status=?' + (' AND game_id=?' if gid else ''), (s, gid) if gid else (s,))['n'] for s in JOB_STATES}
        review = st.one("SELECT COUNT(*) n FROM ref_images WHERE review='Zur Freigabe'" + (' AND game_id=?' if gid else ''), (gid,) if gid else ())['n']
        active = st.one("SELECT * FROM ref_jobs WHERE status='Aktiv' ORDER BY started_at LIMIT 1")
        root = self.comfy.root
        return {'comfy': self.comfy.status(), 'gpu': hardware.gpu_status(), 'counts': counts, 'to_review': review,
                'active': active, 'worker_running': bool(self.worker and self.worker.is_alive()),
                'models': [{k: m[k] for k in ('id', 'name', 'license', 'license_url', 'commercial_use', 'installed', 'capabilities',
                                              'capabilities_not_wired', 'styles', 'vram_min_gb', 'source', 'file_state')}
                           for m in models.installed(root)],
                'verified_models': sorted(models.verified_set(st))}

    # ------------------------------------------------------------ Aufträge anlegen
    def create(self, gid, data):
        st = self.store
        game = st.game(gid)
        if not game:
            raise ValueError('Spiel nicht gefunden')
        prof = self.profile(gid)['profile']
        q, qp = quality.resolve(data.get('quality'), prof)
        dlc_id = data.get('dlc_id') or None
        ref_ids = list(data.get('ref_task_ids') or [])
        if not ref_ids:
            name = str(data.get('name', '')).strip()
            cat = str(data.get('category', 'character'))
            views = data.get('views') or []
            if not name:
                raise ValueError('Bitte beschreiben, was abgebildet werden soll.')
            payload = {'name': name, 'category': cat, 'details': str(data.get('details', ''))[:4000], 'dlc_id': dlc_id}
            if views:
                ref_ids = [st.add_ref(gid, dict(payload, view=v)) for v in views]
            else:
                ref_ids = st.add_ref_bundle(gid, payload)
        route = models.route(self.comfy.root, prof['style_id'], verified=models.verified_set(st))
        if not route['ok']:
            raise ValueError(route['reason'])
        created, skipped = [], []
        force = bool(data.get('force'))
        for rid in ref_ids:
            ref = st.one('SELECT * FROM ref_tasks WHERE id=? AND game_id=?', (rid, gid))
            if not ref:
                raise ValueError('Referenzauftrag gehört nicht zu diesem Spiel')
            prompt, dhash = prompts.build(prof, ref, game['title'])
            w, h = quality.dimensions(qp['long_side'], ref['view'], ref['category'])
            if not force:
                if ref['approved'] and ref['image_path']:
                    skipped.append({'ref': rid, 'reason': f'{ref["name"]} / {ref["view"]}: freigegebene Referenz vorhanden – wird wiederverwendet'})
                    continue
                dup = st.one("SELECT j.id FROM ref_jobs j WHERE j.ref_task_id=? AND j.design_hash=? AND j.width=? AND j.height=? AND j.model_id=? "
                             "AND j.status IN ('Wartend','Aktiv','Abgeschlossen') AND NOT EXISTS (SELECT 1 FROM ref_images i WHERE i.job_id=j.id AND i.review IN ('Abgelehnt','Technisch fehlerhaft')) LIMIT 1",
                             (rid, dhash, w, h, route['model']))
                if dup:
                    skipped.append({'ref': rid, 'reason': f'{ref["name"]} / {ref["view"]}: identischer Auftrag existiert bereits (keine doppelte Berechnung)'})
                    continue
            # Neue Varianten bekommen neue Seeds; vorhandene Versionen bleiben erhalten.
            last = st.one('SELECT MAX(variant) m FROM ref_jobs WHERE ref_task_id=?', (rid,))['m']
            base_variant = 0 if last is None else last + 1
            for v in range(qp['variants']):
                variant = base_variant + v
                jid = uid()
                st.execute('INSERT INTO ref_jobs(id,game_id,dlc_id,ref_task_id,asset_name,category,view,style_id,model_id,quality,variant,prompt,design_hash,seed,width,height,postprocess,status,step,max_attempts,created_at) '
                           'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                           (jid, gid, ref['dlc_id'], rid, ref['name'], ref['category'], ref['view'], prof['style_id'], route['model'], q, variant,
                            prompt, dhash, prompts.asset_seed(gid, ref['name'], variant), w, h, json.dumps(prof.get('postprocess') or {}),
                            'Wartend', 'In der Warteschlange', qp['max_attempts'], now()))
                created.append(jid)
        if created:
            self._ensure_worker()
        return {'created': created, 'skipped': skipped, 'quality': q, 'route': route}

    def cancel(self, jid):
        j = self.store.one('SELECT * FROM ref_jobs WHERE id=?', (jid,))
        if not j:
            raise ValueError('Auftrag nicht gefunden')
        if j['status'] == 'Wartend':
            self.store.execute("UPDATE ref_jobs SET status='Abgebrochen',step='Vor dem Start abgebrochen',ended_at=? WHERE id=?", (now(), jid))
        elif j['status'] == 'Aktiv':
            self.cancel_flags.add(jid)
            self.comfy.interrupt()
        else:
            raise ValueError('Nur wartende oder laufende Aufträge können abgebrochen werden.')
        return self.job(jid)

    def retry(self, jid):
        j = self.job(jid)
        if j['status'] not in ('Fehlgeschlagen', 'Abgebrochen'):
            raise ValueError('Nur fehlgeschlagene oder abgebrochene Aufträge können erneut gestartet werden.')
        self.store.execute("UPDATE ref_jobs SET status='Wartend',step='Erneut eingereiht',error='',attempts=0,ended_at=NULL WHERE id=?", (jid,))
        self._ensure_worker()
        return self.job(jid)

    def job(self, jid):
        j = self.store.one('SELECT * FROM ref_jobs WHERE id=?', (jid,))
        if not j:
            raise ValueError('Auftrag nicht gefunden')
        j['qc'] = json.loads(j['qc'] or '{}')
        return j

    def jobs(self, gid, limit=60):
        rows = self.store.all('SELECT * FROM ref_jobs WHERE game_id=? ORDER BY created_at DESC, rowid DESC LIMIT ?', (gid, limit))
        for r in rows:
            r['qc'] = json.loads(r['qc'] or '{}')
        return rows

    def images(self, gid, ref_task_id=None):
        q = 'SELECT * FROM ref_images WHERE game_id=?' + (' AND ref_task_id=?' if ref_task_id else '') + ' ORDER BY created_at DESC'
        rows = self.store.all(q, (gid, ref_task_id) if ref_task_id else (gid,))
        for r in rows:
            r['meta'] = json.loads(r['meta'])
        return rows

    def image_path(self, gid, iid):
        r = self.store.one('SELECT * FROM ref_images WHERE id=? AND game_id=?', (iid, gid))
        if not r:
            raise ValueError('Bild nicht gefunden')
        p = self.out_dir / gid / r['file']
        if not p.is_file():
            raise ValueError('Bilddatei fehlt')
        return p

    def review(self, gid, iid, action):
        img = self.store.one('SELECT * FROM ref_images WHERE id=? AND game_id=?', (iid, gid))
        if not img:
            raise ValueError('Bild nicht gefunden')
        if action == 'reject':
            self.store.execute("UPDATE ref_images SET review='Abgelehnt' WHERE id=?", (iid,))
            return {'review': 'Abgelehnt'}
        if action != 'approve':
            raise ValueError('Unbekannte Aktion')
        if img['review'] == 'Technisch fehlerhaft':
            raise ValueError('Technisch fehlerhafte Bilder können nicht freigegeben werden.')
        src = self.image_path(gid, iid)
        # In die bestehende Referenzverwaltung übernehmen (eigene Kopie, Originalversion bleibt erhalten).
        target_name = uid() + '.png'
        shutil.copy2(src, self.store.base / 'refs' / target_name)
        meta = json.loads(img['meta'])
        self.store.execute('UPDATE ref_tasks SET image_path=?,image_name=?,approved=1,updated_at=? WHERE id=? AND game_id=?',
                           (target_name, f'GAMEFORGE_{meta.get("model_id")}_v{img["version"]}.png', now(), img['ref_task_id'], gid))
        self.store.execute("UPDATE ref_images SET review='Ersetzt' WHERE ref_task_id=? AND review='Freigegeben' AND id<>?", (img['ref_task_id'], iid))
        self.store.execute("UPDATE ref_images SET review='Freigegeben' WHERE id=?", (iid,))
        return {'review': 'Freigegeben', 'ref_task_id': img['ref_task_id']}

    # ------------------------------------------------------------ Worker
    def _ensure_worker(self):
        with self.lock:
            if not (self.worker and self.worker.is_alive()):
                self.worker = threading.Thread(target=self._loop, name='gameforge-reference-engine', daemon=True)
                self.worker.start()
            self.wake.set()

    def _loop(self):
        while True:
            j = self.store.one("SELECT * FROM ref_jobs WHERE status='Wartend' ORDER BY created_at, rowid LIMIT 1")
            if not j:
                self.wake.clear()
                if not self.wake.wait(30):
                    if not self.store.one("SELECT id FROM ref_jobs WHERE status='Wartend' LIMIT 1"):
                        return
                continue
            self._run(j)

    def _set(self, jid, **kw):
        cols = ', '.join(f'{k}=?' for k in kw)
        self.store.execute(f'UPDATE ref_jobs SET {cols} WHERE id=?', tuple(kw.values()) + (jid,))

    def _run(self, j):
        jid = j['id']
        attempts = j['attempts'] + 1
        self._set(jid, status='Aktiv', step='Vorbereitung', started_at=now(), attempts=attempts, error='')
        try:
            free_gb = shutil.disk_usage(self.store.base).free / 1024**3
            if free_gb < 2:
                raise RuntimeError(f'Zu wenig Speicherplatz ({free_gb:.1f} GB frei).')
            self._set(jid, step='ComfyUI wird gestartet' if not self.comfy.online() else 'ComfyUI bereit')
            self.comfy.start()
            post = json.loads(j['postprocess'] or '{}')
            m = next(x for x in models.MODELS if x['id'] == j['model_id'])
            wf = comfy_mod.klein_t2i(j['prompt'], j['seed'] + (attempts - 1) * 104729, j['width'], j['height'], m['steps'], m['cfg'],
                                     prefix=f'gameforge/{j["game_id"]}/{jid}', pixel=post if post.get('pixel_grid') else None)
            missing = self.comfy.missing_nodes(wf)
            if missing:
                raise RuntimeError('In dieser ComfyUI-Version fehlen benötigte Bausteine: ' + ', '.join(missing))
            self._set(jid, step='Modell wird geladen / Bild wird erzeugt')
            pid = self.comfy.queue(wf)
            self._set(jid, comfy_prompt_id=pid)
            t0 = time.time()
            hist = None
            while time.time() - t0 < 1800:
                if jid in self.cancel_flags:
                    self.cancel_flags.discard(jid)
                    self._set(jid, status='Abgebrochen', step='Vom Nutzer abgebrochen', ended_at=now())
                    return
                hist = self.comfy.history(pid)
                if hist and hist.get('status', {}).get('completed') is not None and (hist['status'].get('completed') or hist['status'].get('status_str') == 'error'):
                    break
                time.sleep(1)
            if not hist:
                raise RuntimeError('ComfyUI hat innerhalb von 30 Minuten kein Ergebnis geliefert.')
            if hist['status'].get('status_str') == 'error':
                msgs = [m for m in hist['status'].get('messages', []) if m[0] == 'execution_error']
                detail = msgs[0][1].get('exception_message', '') if msgs else 'unbekannter Fehler'
                if 'out of memory' in detail.lower() or 'allocation' in detail.lower():
                    raise RuntimeError('Grafikspeicher reicht nicht. Niedrigere Qualitätsstufe wählen oder Blender/Unreal schließen. (' + detail[:200] + ')')
                raise RuntimeError('ComfyUI-Fehler: ' + detail[:600])
            self._set(jid, step='Datei wird gespeichert und geprüft')
            imgs = [im for out in hist.get('outputs', {}).values() for im in out.get('images', [])]
            if not imgs:
                raise RuntimeError('ComfyUI meldet Erfolg, aber es wurde keine Bilddatei ausgegeben.')
            data = self.comfy.fetch_image(imgs[0]['filename'], imgs[0].get('subfolder', ''), imgs[0].get('type', 'output'))
            folder = self.out_dir / j['game_id']; folder.mkdir(parents=True, exist_ok=True)
            fname = f'{jid}_a{attempts}.png'
            with open(folder / fname, 'xb') as f:
                f.write(data)
            g = post.get('pixel_grid')
            qc = imagecheck.check_image(folder / fname, (j['width'] // g) * g if g else j['width'], (j['height'] // g) * g if g else j['height'],
                                        pixel_grid=g, max_colors=post.get('colors'))
            seconds = round(time.time() - t0, 1)
            version = (self.store.one('SELECT MAX(version) v FROM ref_images WHERE ref_task_id=?', (j['ref_task_id'],))['v'] or 0) + 1
            meta = {'project_id': j['game_id'], 'asset_id': j['ref_task_id'], 'asset_name': j['asset_name'], 'asset_type': j['category'],
                    'view': j['view'], 'style': j['style_id'], 'model_id': j['model_id'], 'model_version': 'FLUX.2 klein 4B (bf16)',
                    'prompt': j['prompt'], 'seed': j['seed'] + (attempts - 1) * 104729, 'width': j['width'], 'height': j['height'],
                    'quality': j['quality'], 'postprocess': post, 'created_at': now(), 'image_version': version,
                    'generation_seconds': seconds, 'blender_file': None, 'unreal_asset': None, 'qc': qc}
            (folder / (fname + '.json')).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
            review = 'Zur Freigabe' if qc['ok'] else 'Technisch fehlerhaft'
            iid = uid()
            self.store.execute('INSERT INTO ref_images(id,game_id,ref_task_id,job_id,file,version,meta,review,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                               (iid, j['game_id'], j['ref_task_id'], jid, fname, version, json.dumps(meta, ensure_ascii=False), review, now()))
            if not qc['ok'] and attempts < j['max_attempts']:
                self._set(jid, status='Wartend', step=f'Technische Prüfung nicht bestanden – neuer Versuch {attempts + 1}/{j["max_attempts"]}',
                          image_id=iid, qc=json.dumps(qc))
                return
            models.mark_verified(self.store, j['model_id'])
            self._set(jid, status='Abgeschlossen' if qc['ok'] else 'Fehlgeschlagen',
                      step=f'Fertig in {seconds} s – wartet auf deine Freigabe' if qc['ok'] else 'Technische Prüfung nicht bestanden',
                      error='' if qc['ok'] else 'Technische Prüfung: ' + '; '.join(c['name'] + ': ' + c['detail'] for c in qc['checks'] if not c['ok']),
                      image_id=iid, qc=json.dumps(qc), ended_at=now())
        except Exception as e:  # echte Fehlermeldung ins Protokoll
            self._set(jid, status='Fehlgeschlagen', step='Fehler', error=str(e)[:1500], ended_at=now())
