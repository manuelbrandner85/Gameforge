"""Lokale und datensparsame Claude Subagent-Hook-Telemetrie (pro Projekt)."""
from __future__ import annotations
import json, os, sys, datetime as dt
from pathlib import Path

# Dieses Skript wird in den Projektordner kopiert und von Claude Hooks aufgerufen.
HOOK_PROGRAM = r'''
from pathlib import Path
import json, os, sys, datetime as dt
try:
    payload=json.load(sys.stdin)
    event=str(payload.get('hook_event_name',''))
    if event not in {'SessionStart','SessionEnd','SubagentStart','SubagentStop','PostToolUseFailure'}:
        raise SystemExit(0)
    row={'at':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
         'event':event,'agent':str(payload.get('agent_type') or 'Studio Director')[:100],
         'agent_id':str(payload.get('agent_id') or '')[:100],
         'session_id':str(payload.get('session_id') or '')[:140]}
    if event=='PostToolUseFailure':
        row['tool']=str(payload.get('tool_name') or '')[:120]
    root=Path(__file__).resolve().parent
    with (root/'agent_events.jsonl').open('a',encoding='utf-8') as out:
        out.write(json.dumps(row,ensure_ascii=False)+'\n')
except Exception:
    # Monitoring darf Claude niemals unterbrechen.
    pass
'''

HOOK_EVENTS=('SessionStart','SessionEnd','SubagentStart','SubagentStop','PostToolUseFailure')
LEGACY_COMMAND='python .gameforge/agent_hook.py'

def hook_command():
    """Absoluter Pfad zum laufenden Python, damit der Hook auch ohne „python“ im PATH funktioniert."""
    # Vorwärts-Schrägstriche funktionieren sowohl in cmd als auch in Git Bash.
    exe=(sys.executable or 'python').replace('\\','/')
    return f'"{exe}" .gameforge/agent_hook.py' if ' ' in exe else f'{exe} .gameforge/agent_hook.py'

def _is_gameforge_hook(command):
    return isinstance(command,str) and command.rstrip().endswith('.gameforge/agent_hook.py')

def install(workspace):
    root=Path(workspace).expanduser().resolve(strict=True)
    if not root.is_dir() or root==Path(root.anchor):
        raise ValueError('Ungültiger Projektordner')
    gf=root/'.gameforge'; gf.mkdir(parents=True,exist_ok=True)
    hook=gf/'agent_hook.py'
    if hook.exists() and hook.read_text(encoding='utf-8')!=HOOK_PROGRAM:
        raise ValueError('Vorhandener Agent-Hook weicht ab; keine Überschreibung.')
    if not hook.exists():hook.write_text(HOOK_PROGRAM,encoding='utf-8')
    cfg=root/'.claude'/'settings.local.json'; cfg.parent.mkdir(parents=True,exist_ok=True)
    if cfg.exists():
        try: data=json.loads(cfg.read_text(encoding='utf-8'))
        except Exception as e:raise ValueError('Bestehende Claude-Einstellungen sind kein lesbares JSON: '+str(e))
        if not isinstance(data,dict):raise ValueError('Bestehende Claude-Einstellungen sind ungültig')
    else:data={}
    hooks=data.setdefault('hooks',{})
    if not isinstance(hooks,dict):raise ValueError('Bestehender Hooks-Abschnitt ist ungültig')
    changed=False
    command=hook_command()
    for event in HOOK_EVENTS:
        entries=hooks.setdefault(event,[])
        if not isinstance(entries,list):raise ValueError('Ungültige Hook-Liste: '+event)
        found=False
        for entry in entries:
            if not isinstance(entry,dict):continue
            for h in entry.get('hooks',[]):
                if isinstance(h,dict) and _is_gameforge_hook(h.get('command')):
                    found=True
                    # v1.0 rief „python“ auf – unter Windows oft nur der Store-Platzhalter.
                    if h.get('command')!=command:
                        h['command']=command;changed=True
        if not found:
            entries.append({'hooks':[{'type':'command','command':command,'timeout':10}]})
            changed=True
    if changed:
        if cfg.exists():
            backup=cfg.with_name('settings.local.gameforge-backup-'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
            backup.write_bytes(cfg.read_bytes())
        tmp=cfg.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.replace(tmp,cfg)
    return {'hooks_installed':True,'events':list(HOOK_EVENTS),'settings_path':str(cfg),
            'changed':changed,'note':'Claude-Code-Projekt-Hooks vorbereitet. Nur tatsächliche unterstützte Projekt-Sitzungen erzeugen Live-Daten.'}

def status(workspace,roster):
    if not workspace or not Path(workspace).is_dir():
        return {'configured':False,'events':[],'active_count':0,'message':'Erst lokalen Projektordner verbinden.',
                'agents':[{'name':a['name'],'slug':a['slug'],'status':'Keine aktive Meldung','state':'Keine Verbindung',
                           'started_at':None,'last_event':None,'last_event_at':None,'errors':[],'event_count':0} for a in roster]}
    root=Path(workspace)
    config=root/'.claude'/'settings.local.json'
    file=root/'.gameforge'/'agent_events.jsonl'
    records=[]
    if file.is_file():
        with file.open('rb') as handle:
            handle.seek(0,2); end=handle.tell(); handle.seek(max(0,end-1_000_000))
            if end>1_000_000:handle.readline()
            for line in handle:
                try:
                    row=json.loads(line)
                    if isinstance(row,dict) and row.get('event') in HOOK_EVENTS:records.append(row)
                except (UnicodeError,ValueError):continue
    records=records[-180:]
    now=dt.datetime.now(dt.timezone.utc)
    active={}
    for e in records:
        if e.get('event')=='SubagentStart':active[e.get('agent_id') or e.get('agent')]=e
        if e.get('event')=='SubagentStop':active.pop(e.get('agent_id') or e.get('agent'),None)
        if e.get('event')=='SessionEnd':
            session=e.get('session_id')
            active={k:v for k,v in active.items() if v.get('session_id')!=session}
    live={}
    for e in active.values():
        try:age=(now-dt.datetime.fromisoformat(e['at'])).total_seconds()
        except Exception:age=10**10
        if age<=900:live[e.get('agent')]=e
    configured=False
    if config.is_file():
        try:
            hooks=json.loads(config.read_text(encoding='utf-8')).get('hooks',{})
            configured=any(_is_gameforge_hook(h.get('command')) for entries in hooks.values() for item in entries if isinstance(item,dict) for h in item.get('hooks',[]) if isinstance(h,dict))
        except Exception:pass
    # Pro Agent: nur aus echten Hook-Ereignissen abgeleitete Zustände, keine Prozentwerte.
    roles=[]
    for a in roster:
        mine=[e for e in records if e.get('agent')==a['slug']]
        last=mine[-1] if mine else None
        starts=[e for e in mine if e.get('event')=='SubagentStart']
        errors=[e for e in mine if e.get('event')=='PostToolUseFailure']
        if not configured:
            state='Unbekannt'
        elif a['slug'] in live:
            state='Arbeitet'
        elif last and last.get('event')=='PostToolUseFailure':
            state='Fehler'
        elif last and last.get('event')=='SubagentStop':
            state='Abgeschlossen'
        elif last and last.get('event')=='SubagentStart':
            state='Unbekannt'  # Start ohne Abschluss, älter als 15 Minuten
        else:
            state='Wartet'
        roles.append({'name':a['name'],'slug':a['slug'],
                      'status':'Aktiv (gemeldet)' if state=='Arbeitet' else 'Keine aktive Meldung',
                      'state':state,'started_at':starts[-1]['at'] if starts else None,
                      'last_event':last.get('event') if last else None,'last_event_at':last.get('at') if last else None,
                      'errors':[{'at':e.get('at'),'tool':e.get('tool','')} for e in errors[-5:]],'event_count':len(mine)})
    return {'configured':configured,'agents':roles,'events':records[-60:][::-1],
           'active_count':len(live),'hook_command_ok':configured and Path(sys.executable or '').is_file(),
           'message':'Nur Hook-Ereignisse aus dieser Projektkonfiguration. Keine Einsicht in beliebige fremde Claude-Sitzungen; nach 15 Minuten ohne Abschluss wird Aktivität nicht mehr als live angezeigt.'}
