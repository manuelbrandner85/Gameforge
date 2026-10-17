"""Optionaler lokaler Direktmodus für GAMEFORGE.
Arbeitet nur nach expliziten Schaltflächenaktionen; keine unbeaufsichtigte Endlosautomatisierung.
"""
from __future__ import annotations
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
import uuid
import zipfile
import stat
import re


def uid(): return uuid.uuid4().hex[:16]
def now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


class DirectStudio:
    def __init__(self, store):
        self.store=store
        self.guard=threading.RLock()
        self.live={}
        store.conn.executescript('''
          CREATE TABLE IF NOT EXISTS direct_settings(
             game_id TEXT PRIMARY KEY REFERENCES games(id), workspace TEXT NOT NULL DEFAULT '',
             uat_path TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS direct_jobs(
             id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
             kind TEXT NOT NULL, task_id TEXT, status TEXT NOT NULL,
             instruction TEXT NOT NULL, log TEXT NOT NULL DEFAULT '',
             exit_code INTEGER, created_at TEXT NOT NULL, ended_at TEXT);
        ''')
        store.conn.commit()
        store.execute("UPDATE direct_jobs SET status='Unterbrochen',ended_at=?,log=log||'\\nProgramm wurde vor Abschluss beendet. Lokale Änderungen bitte überprüfen.' WHERE status='Läuft'",(now(),))

    def settings(self,gid):
        self._check_game(gid)
        return self.store.one('SELECT * FROM direct_settings WHERE game_id=?',(gid,)) or {'game_id':gid,'workspace':'','uat_path':'','updated_at':''}

    def _check_game(self,gid):
        if not self.store.game(gid): raise ValueError('Unbekanntes Spiel')

    def configure(self,gid,data):
        self._check_game(gid)
        workspace=str(data.get('workspace','')).strip().strip('"')
        uat_path=str(data.get('uat_path','')).strip().strip('"')
        if not workspace: raise ValueError('Bitte einen vorhandenen lokalen Projektordner auswählen.')
        p=Path(workspace).expanduser().resolve()
        if not p.is_dir(): raise ValueError('Projektordner nicht gefunden. Erstellt keine Ordner auf fremden Pfaden.')
        if uat_path and not Path(uat_path).expanduser().is_file(): raise ValueError('RunUAT.bat wurde nicht gefunden.')
        # Keine destruktive Änderung an den lokalen Quelldateien.
        self.store.execute('INSERT INTO direct_settings(game_id,workspace,uat_path,updated_at) VALUES(?,?,?,?) ON CONFLICT(game_id) DO UPDATE SET workspace=excluded.workspace,uat_path=excluded.uat_path,updated_at=excluded.updated_at',(gid,str(p),str(Path(uat_path).expanduser().resolve()) if uat_path else '',now()))
        return self.settings(gid)

    def create_workspace(self,gid):
        self._check_game(gid)
        p=self.store.base/'workspaces'/gid
        p.mkdir(parents=True,exist_ok=True)
        old=self.settings(gid)
        return self.configure(gid,{'workspace':str(p),'uat_path':old.get('uat_path','')})

    def extract_archive(self,gid,archive_id):
        """Expliziter, begrenzter ZIP-Import in einen NEUEN Arbeitsordner."""
        self._check_game(gid)
        arc=self.store.one('SELECT * FROM archives WHERE game_id=? AND id=?',(gid,archive_id))
        if not arc or arc['kind'] not in ('Vollprojekt','DLC-Vollprojekt'):
            raise ValueError('Bitte ein vorhandenes Vollprojekt-Archiv auswählen.')
        source=self.store.base/'uploads'/arc['file_path']
        if not source.is_file(): raise ValueError('Archivdatei fehlt')
        root=self.store.base/'workspaces'/gid/('import_'+uid())
        root.mkdir(parents=True,exist_ok=False)
        try:
            with zipfile.ZipFile(source) as z:
                entries=z.infolist()
                if len(entries)>50000: raise ValueError('ZIP enthält zu viele Dateien.')
                if sum(i.file_size for i in entries)>30*1024**3:
                    raise ValueError('Entpacktes ZIP überschreitet 30 GB.')
                for i in entries:
                    n=i.filename.replace(chr(92),'/')
                    seg=n.rstrip('/').split('/')
                    if (not n or n.startswith('/') or re.match(r'^[A-Za-z]:',n) or
                        any(c in ('','.','..') for c in seg) or chr(0) in n or
                        any(part.endswith((':',' ')) for part in seg) or len(n)>800):
                        raise ValueError('Ungültiger ZIP-Pfad: '+n[:150])
                    if stat.S_ISLNK((i.external_attr >> 16) & 0xffff):
                        raise ValueError('Symlinks werden nicht automatisch entpackt.')
                    dest=root.joinpath(*seg)
                    if i.is_dir(): dest.mkdir(parents=True,exist_ok=True)
                    else:
                        if dest.exists(): raise ValueError('ZIP enthält doppelte Dateinamen.')
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        with z.open(i) as src,open(dest,'xb') as dst:
                            shutil.copyfileobj(src,dst,2*1024*1024)
            matches=list(root.rglob('*.uproject'))
            effective=matches[0].parent if len(matches)==1 else root
            old=self.settings(gid)
            self.configure(gid,{'workspace':str(effective),'uat_path':old.get('uat_path','')})
            return {'workspace':str(effective),'files':len(entries),
                    'uproject_found':len(matches)==1,
                    'note':'In neuen Ordner entpackt; bestehende Projekte unverändert. Keine Skripte ausgeführt.'}
        except Exception:
            shutil.rmtree(root,ignore_errors=True)
            raise

    def stage_inputs(self,gid,workspace):
        """Nur zu diesem Spiel gehörende Originalimporte und freigegebene Referenzen kopieren."""
        base=workspace/'.gameforge'/'project_inputs'
        base.mkdir(parents=True,exist_ok=True)
        manifest=[]
        max_bytes=3*1024**3
        used=0
        for entry in self.store.files(gid):
            path=self.store.base/'imports'/entry['id']
            if not path.is_file(): continue
            if entry['size']>max_bytes-used:
                manifest.append({'name':entry['relpath'],'state':'zu gross, nicht kopiert'})
                continue
            dest=base/'imports'/entry['id']/Path(entry['relpath']).name
            dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.is_file() or dest.stat().st_size!=path.stat().st_size:
                shutil.copy2(path,dest)
            used+=entry['size']
            manifest.append({'name':entry['relpath'],'state':'kopiert','path':str(dest.relative_to(workspace))})
        for ref in self.store.refs(gid):
            if not ref['image_path'] or not ref['approved']: continue
            src=self.store.base/'refs'/ref['image_path']
            if not src.is_file() or src.stat().st_size>max_bytes-used: continue
            dst=base/'references'/(ref['id']+src.suffix)
            dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.is_file() or dst.stat().st_size!=src.stat().st_size:
                shutil.copy2(src,dst)
            used+=src.stat().st_size
            manifest.append({'name':ref['name']+' / '+ref['view'],'state':'kopiert',
                            'path':str(dst.relative_to(workspace))})
        mf=workspace/'.gameforge'/'INPUT_MANIFEST.json'
        mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        return manifest

    def archive_workspace(self,gid):
        """Zipped echte lokale Projektquellen auf explizite Anforderung, keine Cache-Ordner."""
        import hashlib
        self._check_game(gid)
        cfg=self.settings(gid)
        workspace=Path(cfg['workspace']) if cfg['workspace'] else None
        if not workspace or not workspace.is_dir():
            raise ValueError('Bitte zunächst einen vorhandenen Projektordner verbinden.')
        ignored={'.git','.svn','.hg','Intermediate','Saved','DerivedDataCache','.venv',
                 '__pycache__','node_modules','.vs','Binaries'}
        files=[]
        for f in workspace.rglob('*'):
            if not f.is_file() or f.is_symlink(): continue
            rel=f.relative_to(workspace)
            if any(x in ignored for x in rel.parts):continue
            if rel.name.startswith('.env') or rel.name=='.mcp.json':continue
            files.append((f,rel.as_posix()))
        if not files:raise ValueError('Der Arbeitsordner enthält noch keine archivierungsfähigen Projektdateien.')
        upload_dir=self.store.base/'uploads'
        name='GAMEFORGE_Quellprojekt_'+gid+'_'+uid()+'.zip'
        path=upload_dir/name
        try:
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=3,allowZip64=True) as z:
                for file,rel in files:z.write(file,arcname=rel)
            digest=hashlib.sha256()
            with open(path,'rb') as f:
                for block in iter(lambda:f.read(4*1024*1024),b''):digest.update(block)
            kind='Vollprojekt' if any(rel.endswith('.uproject') for _,rel in files) else 'Andere'
            aid=uid()
            self.store.execute('INSERT INTO archives(id,game_id,dlc_id,kind,label,version,original_name,file_path,size,sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                (aid,gid,None,kind,'Lokaler Entwicklungsstand / Quellprojekt',self.store.game(gid)['version'],
                 name,name,path.stat().st_size,digest.hexdigest(),now()))
            return {'archive_id':aid,'files':len(files),'size':path.stat().st_size,
                    'kind':kind,'note':'Quellprojekt archiviert. Temporaere Caches, Buildordner, .env und .mcp.json ausgeschlossen. Kein Nachweis fertigen Spiels.'}
        except Exception:
            path.unlink(missing_ok=True)
            raise

    def check(self,gid):
        c=self.settings(gid)
        workspace=Path(c['workspace']) if c['workspace'] else None
        has_workspace=bool(workspace and workspace.is_dir())
        cli=shutil.which('claude')
        blender=shutil.which('blender')
        mcp=[]
        for loc in ([workspace/'.mcp.json'] if has_workspace else []):
            if loc.is_file():
                try:
                    data=json.loads(loc.read_text(encoding='utf-8'))
                    mcp=list((data.get('mcpServers') or {}).keys())
                except (ValueError,OSError):
                    mcp=['Konfiguration unlesbar']
        online=False
        try:
            with socket.create_connection(('127.0.0.1',8000),timeout=0.3): online=True
        except (OSError,TimeoutError): pass
        return {'settings':c,'claude_cli_detected':bool(cli),'blender_executable_detected':bool(blender),
                'workspace_valid':has_workspace,'uprojects':[x.name for x in workspace.glob('*.uproject')][:20] if has_workspace else [],
                'mcp_names':mcp,'unreal_local_port_8000_open':online,
                'uat_configured':bool(c['uat_path'] and Path(c['uat_path']).is_file()),
                'note':'Erkennung bedeutet nicht Anmeldung oder funktionierendes MCP. Ports und .mcp.json allein beweisen keine Verbindung.'}

    def jobs(self,gid):
        self._check_game(gid)
        return self.store.all('SELECT * FROM direct_jobs WHERE game_id=? ORDER BY created_at DESC,rowid DESC LIMIT 25',(gid,))

    def job(self,gid,jid):
        self._check_game(gid)
        j=self.store.one('SELECT * FROM direct_jobs WHERE game_id=? AND id=?',(gid,jid))
        if not j: raise ValueError('Arbeitsauftrag nicht gefunden')
        return j

    def task_prompt(self,gid,kind,task_id,instruction,job_id):
        game=self.store.game(gid)
        c=self.settings(gid)
        tasks=self.store.tasks(gid)
        task=next((t for t in tasks if t['id']==task_id),None) if task_id else None
        if task_id and not task: raise ValueError('Aufgabe nicht gefunden')
        content={'game':{'title':game['title'],'genre':game['genre'],'style':game['style'],'version':game['version']},
                 'game_bible':{key:str(value)[:9000] for key,value in game['bible'].items() if value},
                 'selected_task':{k:task[k] for k in ('phase','title','description','acceptance','status') } if task else None,
                 'user_instruction':instruction,
                 'reference_tasks':[{'name':r['name'],'view':r['view'],'approved':bool(r['approved']),
                         'image_file_in_gameforge':bool(r['image_path'])} for r in self.store.refs(gid)][:500]}
        workspace=Path(c['workspace'])
        self.stage_inputs(gid,workspace)
        p=workspace/'.gameforge'
        p.mkdir(exist_ok=True)
        context=p/f'SESSION_{job_id}.json'
        context.write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
        return ('Du arbeitest lokal im GAMEFORGE GODMODE Direktstudio. Lies zuerst .gameforge/'+context.name+'. '
          'Vorhandene Originalimporte und freigegebene Referenzen findest du in .gameforge/INPUT_MANIFEST.json und .gameforge/project_inputs/. '
          'Arbeite ausschließlich am geöffneten Spiel und innerhalb dieses lokalen Projektordners. '
          'Unterscheide zwingend geplant, umgesetzt, getestet und freigegeben. '
          'Unbekannte Originaldateien niemals erraten; importierte GAMEFORGE-Dateien sind nicht zwangsläufig bereits im Arbeitsordner. '
          'Niemals Daten löschen, fremde Konten aufrufen, veröffentlichen oder kostenpflichtige Dienste auslösen. '
          'Keinen Story-Kanon unbeauftragt überschreiben. '
          'Nutze die konfigurierten Blender- und Unreal-MCP-Tools, falls verfügbar, sonst melde präzise, was fehlt. '
          'Berichte auf Deutsch über tatsächlich geänderte Dateien, Testergebnisse, Fehler und nächste Schritte. '
          + ('Erstelle einen ausführlichen Umsetzungsplan. Noch nichts ändern oder bauen.' if kind=='plan' else
             'Setze ausschließlich den angegebenen Teilarbeitsauftrag um. Teste soweit technisch möglich und berichte ehrlich.'))

    def retry(self,gid,jid):
        """Fehlgeschlagenen oder unterbrochenen Auftrag mit identischem Auftragstext neu starten."""
        job=self.job(gid,jid)
        if job['status'] not in ('Fehlgeschlagen','Unterbrochen'):
            raise ValueError('Nur fehlgeschlagene oder unterbrochene Aufträge können erneut gestartet werden.')
        if job['kind']=='blender_test':
            import studio_v2
            return studio_v2.start_blender_test(self.store,gid)
        try: options=json.loads(job.get('options') or '{}')
        except ValueError: options={}
        return self.start(gid,dict(options,kind=job['kind'],instruction=job.get('user_instruction') or '',task_id=job.get('task_id') or ''))

    def start(self,gid,data):
        self._check_game(gid)
        kind=str(data.get('kind',''))
        if kind not in ('plan','implement','build'): raise ValueError('Unbekannter Produktionsmodus')
        c=self.settings(gid)
        if not c['workspace'] or not Path(c['workspace']).is_dir(): raise ValueError('Zuerst einen Projektordner verbinden.')
        if kind in ('plan','implement') and not shutil.which('claude'):
            raise ValueError('Claude Code nicht gefunden. Bitte installieren und im Terminal anmelden.')
        if kind=='build':
            if os.name!='nt': raise ValueError('Windows-Paketierung ist nur auf einem eingerichteten Windows-PC verfügbar.')
            if not c['uat_path'] or not Path(c['uat_path']).is_file(): raise ValueError('Für Windows-Build zuerst RunUAT.bat konfigurieren.')
            uprojs=list(Path(c['workspace']).glob('*.uproject'))
            if len(uprojs)!=1: raise ValueError('Genau eine .uproject-Datei im Projekt-Hauptordner erforderlich.')
        instruction=str(data.get('instruction','')).strip()
        if not instruction and kind!='build': raise ValueError('Bitte einen konkreten Auftrag eingeben.')
        if len(instruction)>12000: raise ValueError('Auftrag ist zu lang.')
        taskid=str(data.get('task_id','')).strip() or None
        # MCP-Freigabe nur auf ausdrücklichen Wunsch und nur für Blender/Unreal-Server.
        options={'allow_mcp':bool(data.get('allow_mcp')),'max_turns':max(4,min(int(data.get('max_turns') or 16),80))}
        with self.guard:
            if any(j['status']=='Läuft' for j in self.jobs(gid)):
                raise ValueError('Für dieses Spiel läuft bereits ein Produktionsauftrag.')
            jid=uid()
            brief=self.task_prompt(gid,kind,taskid,instruction,jid) if kind!='build' else instruction
            self.store.execute('INSERT INTO direct_jobs(id,game_id,kind,task_id,status,instruction,created_at,user_instruction,options) VALUES(?,?,?,?,?,?,?,?,?)',(jid,gid,kind,taskid,'Läuft',brief,now(),instruction,json.dumps(options)))
            thread=threading.Thread(target=self._perform,args=(gid,jid,kind,brief,c,options),daemon=True,name='gameforge-'+jid)
            self.live[jid]=thread
            thread.start()
        return self.job(gid,jid)

    def _perform(self,gid,jid,kind,brief,c,options=None):
        options=options or {}
        cwd=Path(c['workspace'])
        out=''
        code=-1
        try:
            if kind=='build':
                upro=list(cwd.glob('*.uproject'))[0]
                destination=self.store.base/'build_outputs'/gid/jid
                destination.mkdir(parents=True,exist_ok=True)
                cmd=[c['uat_path'],'BuildCookRun','-noP4',f'-project={upro}','-build','-cook','-stage',
                    '-pak','-package','-archive',f'-archivedirectory={destination}','-targetplatform=Win64',
                    '-clientconfig=Development','-utf8output']
                # Keine Shell: insbesondere keine Befehlsinjektion über Pfadangaben.
                r=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True,timeout=10800,errors='replace')
                code=r.returncode
                out=(r.stdout+'\n'+r.stderr)[-120000:]
                if code==0:
                    artifacts=[f for f in destination.rglob('*') if f.is_file()]
                    if not artifacts: raise RuntimeError('UAT meldet Erfolg, aber es wurde kein Paketierungsartefakt gefunden.')
                    upload_dir=self.store.base/'uploads'
                    upload_dir.mkdir(exist_ok=True)
                    name=f'{self.store.game(gid)["title"].replace(" ","_")}_Windows_Build_{jid}.zip'
                    safe_name='GAMEFORGE_Windows_Build_'+jid+'.zip'
                    zpath=upload_dir/safe_name
                    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
                        for f in artifacts: z.write(f,arcname=f.relative_to(destination).as_posix())
                    import hashlib
                    h=hashlib.sha256()
                    with open(zpath,'rb') as f:
                        for block in iter(lambda:f.read(4*1024*1024),b''): h.update(block)
                    aid=uid()
                    self.store.execute('INSERT INTO archives(id,game_id,dlc_id,kind,label,version,original_name,file_path,size,sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                        (aid,gid,None,'Windows-Build','GAMEFORGE automatisierter Windows-Build',self.store.game(gid)['version'],name,safe_name,zpath.stat().st_size,h.hexdigest(),now()))
                    out+='\nErstelltes Windows-Build-ZIP im Dateiarchiv hinterlegt. Ein erfolgreicher Build ersetzt keine Spielabnahme.'
            else:
                mode='plan' if kind=='plan' else 'acceptEdits'
                cmd=[shutil.which('claude') or 'claude','-p',brief,'--output-format','text','--permission-mode',mode,'--max-turns',str(options.get('max_turns',16))]
                if options.get('allow_mcp') and kind=='implement':
                    # Ohne Freigabe lehnt Claude im Hintergrundmodus jeden MCP-Aufruf ab.
                    cmd+=['--allowedTools','mcp__blender','mcp__unreal-mcp']
                r=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True,timeout=7200,errors='replace',stdin=subprocess.DEVNULL)
                code=r.returncode
                out=(r.stdout+'\n'+r.stderr)[-120000:]
            if code and not out.strip(): out='Auftrag ist fehlgeschlagen. Claude-Anmeldung, Berechtigungen oder lokale Tools prüfen.'
            if code and kind!='build':
                import studio_v2
                if studio_v2.is_auth_error(out): out=studio_v2.LOGIN_HINT+'\n\nOriginalmeldung:\n'+out
        except subprocess.TimeoutExpired as e:
            code=-2;out='Zeitlimit überschritten. Prüfe den lokalen Projektordner auf teilweise erstellte Dateien. '+str(e)[:400]
        except Exception as e:
            code=-3;out='Fehler: '+str(e)[:800]
        finally:
            status='Abgeschlossen' if code==0 else 'Fehlgeschlagen'
            self.store.execute('UPDATE direct_jobs SET status=?,log=?,exit_code=?,ended_at=? WHERE id=?',(status,out,code,now(),jid))
            with self.guard: self.live.pop(jid,None)
