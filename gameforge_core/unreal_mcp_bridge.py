"""GAMEFORGE Unreal-MCP-Brücke (stdio) für den nativen Unreal-MCP inkl. VibeUE.

Claude Code / Claude-App starten diese Brücke als MCP-Server „Unreal“. Sie ist sofort verbunden – auch wenn
Unreal noch nicht läuft – und leitet jede Anfrage 1:1 an den nativen Server (http://127.0.0.1:8000/mcp) weiter.
Läuft Unreal nicht, wenn ein Unreal-Werkzeug gebraucht wird, startet sie den Editor mit dem passenden Projekt,
wartet auf den MCP-Server (Autostart im Projekt) und baut die Sitzung neu auf. Unreal wird nie beendet.

Projektwahl: Werkzeug „unreal_starten“ (Argument projekt) > GAMEFORGE_UNREAL_PROJEKT > .uproject im Arbeitsordner
(bzw. unreal/*/, bis zu 3 Ebenen darüber) > zuletzt benutztes Projekt.
Nur Python-Standardbibliothek.
"""
from __future__ import annotations
import json, os, socket, subprocess, sys, threading, time, urllib.error, urllib.request
from pathlib import Path

URL = os.environ.get('GAMEFORGE_UNREAL_MCP_URL', 'http://127.0.0.1:8000/mcp')
HOST, PORT = '127.0.0.1', int(URL.split(':')[2].split('/')[0])
ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('GAMEFORGE_DATA_DIR') or ROOT / 'GAMEFORGE_DATA')
CACHE = DATA / 'unreal_mcp_tools.json'
LAST = DATA / 'unreal_letztes_projekt.json'
LOG = DATA / 'logs' / 'unreal_mcp_bridge.log'
EDITOR = Path(os.environ.get('GAMEFORGE_UNREAL_EDITOR') or r'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe')
START_TOOL = {
    'name': 'unreal_starten',
    'description': 'GAMEFORGE: Startet den Unreal Editor mit einem Projekt (falls er nicht läuft) und wartet, bis der native '
                   'Unreal-MCP (inkl. VibeUE) bereit ist. Ohne projekt: Projekt aus dem Arbeitsordner bzw. das zuletzt benutzte.',
    'inputSchema': {'type': 'object', 'properties': {'projekt': {'type': 'string', 'description': 'Pfad zur .uproject oder zum Projektordner'}}},
}
_lock = threading.Lock()
_state = {'sid': None, 'proto': '2025-06-18', 'client_init': None}


def log(*a):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + ' '.join(str(x) for x in a) + '\n')
    except OSError:
        pass


def port_open():
    try:
        with socket.create_connection((HOST, PORT), timeout=1):
            return True
    except OSError:
        return False


def find_project(hint=None):
    if hint:
        p = Path(hint)
        if p.is_dir():
            ups = sorted(p.glob('*.uproject')) or sorted(p.glob('*/*.uproject'))
            p = ups[0] if ups else p
        if p.suffix == '.uproject' and p.is_file():
            return p
        raise FileNotFoundError(f'Kein Unreal-Projekt gefunden: {hint}')
    env = os.environ.get('GAMEFORGE_UNREAL_PROJEKT')
    if env and Path(env).is_file():
        return Path(env)
    here = Path.cwd().resolve()
    for d in [here, *list(here.parents)[:3]]:
        ups = sorted(d.glob('*.uproject')) or sorted(d.glob('unreal/*/*.uproject')) or sorted(d.glob('UE/*.uproject'))
        if ups:
            return ups[0]
    try:
        p = Path(json.loads(LAST.read_text(encoding='utf-8'))['projekt'])
        if p.is_file():
            return p
    except (OSError, ValueError, KeyError):
        pass
    return None


def start_unreal(project, timeout=420):
    """Startet den Editor (nur wenn der MCP-Port zu ist) und wartet auf den nativen MCP-Server."""
    if port_open():
        return 'Unreal-MCP läuft bereits.'
    if not EDITOR.is_file():
        raise FileNotFoundError(f'Unreal Editor nicht gefunden: {EDITOR}')
    log('starte Unreal', project)
    subprocess.Popen([str(EDITOR), str(project)], close_fds=True,
                     creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0) | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
    try:
        DATA.mkdir(parents=True, exist_ok=True)
        LAST.write_text(json.dumps({'projekt': str(project), 'zeit': time.time()}), encoding='utf-8')
    except OSError:
        pass
    t0 = time.time()
    while time.time() - t0 < timeout:
        if port_open():
            time.sleep(3)                                  # Toolsets fertig registrieren lassen
            _state['sid'] = None
            return f'Unreal gestartet mit {project.name}; nativer MCP bereit nach {int(time.time() - t0)} s.'
        time.sleep(2)
    raise TimeoutError(f'Unreal-MCP nach {timeout} s nicht erreichbar (Projekt geöffnet? Plugin ModelContextProtocol aktiv?).')


def _post(msg, with_sid=True):
    data = json.dumps(msg).encode('utf-8')
    req = urllib.request.Request(URL, data=data, method='POST', headers={
        'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
        'MCP-Protocol-Version': _state['proto'], **({'Mcp-Session-Id': _state['sid']} if with_sid and _state['sid'] else {})})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=900) as r:
        sid = r.headers.get('Mcp-Session-Id')
        body = r.read().decode('utf-8', errors='replace')
        ctype = r.headers.get('Content-Type', '')
    msgs = []
    if 'text/event-stream' in ctype:
        for line in body.splitlines():
            if line.startswith('data:'):
                try:
                    msgs.append(json.loads(line[5:].strip()))
                except ValueError:
                    pass
    elif body.strip():
        x = json.loads(body)
        msgs.extend(x if isinstance(x, list) else [x])
    return sid, msgs


def _ensure_session():
    if _state['sid']:
        return
    init = _state['client_init'] or {'protocolVersion': _state['proto'], 'capabilities': {}, 'clientInfo': {'name': 'gameforge-bridge', 'version': '1'}}
    sid, msgs = _post({'jsonrpc': '2.0', 'id': 'gf-init', 'method': 'initialize', 'params': init}, with_sid=False)
    _state['sid'] = sid or ''
    for m in msgs:
        v = (m.get('result') or {}).get('protocolVersion')
        if v:
            _state['proto'] = v
    _post({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
    log('upstream-Sitzung', _state['sid'])


def forward(msg):
    """Leitet eine Anfrage weiter; bei abgelaufener Sitzung (Unreal neu gestartet) einmal neu verbinden."""
    for attempt in (1, 2):
        try:
            _ensure_session()
            _, msgs = _post(msg)
            if 'id' in msg:
                return next((m for m in msgs if m.get('id') == msg['id']), None)
            return None
        except urllib.error.HTTPError as e:
            log('HTTP', e.code, msg.get('method'))
            _state['sid'] = None
            if attempt == 2 or e.code not in (400, 404, 409):
                raise
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            _state['sid'] = None
            if attempt == 2:
                raise
            time.sleep(2)


def _err(mid, text):
    return {'jsonrpc': '2.0', 'id': mid, 'result': {'content': [{'type': 'text', 'text': text}], 'isError': True}}


def _ok_text(mid, text):
    return {'jsonrpc': '2.0', 'id': mid, 'result': {'content': [{'type': 'text', 'text': text}]}}


def cached_tools():
    try:
        return json.loads(CACHE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []


def handle(msg):
    mid, method = msg.get('id'), msg.get('method')
    if method == 'initialize':
        _state['client_init'] = msg.get('params') or {}
        _state['proto'] = _state['client_init'].get('protocolVersion', _state['proto'])
        return {'jsonrpc': '2.0', 'id': mid, 'result': {
            'protocolVersion': _state['proto'], 'capabilities': {'tools': {'listChanged': False}},
            'serverInfo': {'name': 'Unreal (GAMEFORGE-Brücke)', 'version': '1.0'},
            'instructions': 'Nativer Unreal-MCP inkl. VibeUE. Läuft Unreal nicht, startet die Brücke es beim ersten Unreal-Werkzeug '
                            'automatisch (oder gezielt mit unreal_starten). Erst list_toolsets/describe_toolset, dann call_tool.'}}
    if method and method.startswith('notifications/'):
        if port_open() and _state['sid'] and method != 'notifications/initialized':
            try:
                forward(msg)
            except Exception as e:                       # noqa: BLE001 – Benachrichtigungen sind unkritisch
                log('notify', e)
        return None
    if method == 'ping':
        return {'jsonrpc': '2.0', 'id': mid, 'result': {}}
    if method == 'tools/list':
        tools = cached_tools()
        if port_open():
            try:
                r = forward(msg)
                tools = (r or {}).get('result', {}).get('tools', tools)
                DATA.mkdir(parents=True, exist_ok=True)
                CACHE.write_text(json.dumps(tools, ensure_ascii=False), encoding='utf-8')
            except Exception as e:                       # noqa: BLE001
                log('tools/list', e)
        return {'jsonrpc': '2.0', 'id': mid, 'result': {'tools': [START_TOOL] + [t for t in tools if t.get('name') != 'unreal_starten']}}
    if method == 'tools/call' and (msg.get('params') or {}).get('name') == 'unreal_starten':
        try:
            proj = find_project((msg['params'].get('arguments') or {}).get('projekt'))
            if not proj and not port_open():
                return _err(mid, 'Kein Unreal-Projekt bekannt. Bitte projekt angeben (Pfad zur .uproject).')
            return _ok_text(mid, start_unreal(proj) if not port_open() else 'Unreal-MCP läuft bereits.')
        except Exception as e:                           # noqa: BLE001
            return _err(mid, f'Unreal konnte nicht gestartet werden: {e}')
    if method in ('resources/list', 'prompts/list', 'resources/templates/list') and not port_open():
        key = {'resources/list': 'resources', 'prompts/list': 'prompts', 'resources/templates/list': 'resourceTemplates'}[method]
        return {'jsonrpc': '2.0', 'id': mid, 'result': {key: []}}
    if not port_open():
        if method == 'tools/call':
            proj = find_project()
            if not proj:
                return _err(mid, 'Unreal läuft nicht und kein Projekt ist bekannt. Erst unreal_starten mit projekt aufrufen.')
            try:
                start_unreal(proj)
            except Exception as e:                       # noqa: BLE001
                return _err(mid, f'Unreal läuft nicht und konnte nicht gestartet werden: {e}')
        else:
            return {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32000, 'message': 'Unreal läuft nicht'}}
    try:
        r = forward(msg)
        return r if r is not None else {'jsonrpc': '2.0', 'id': mid, 'result': {}}
    except Exception as e:                               # noqa: BLE001
        log('Fehler', method, e)
        return _err(mid, f'Unreal-MCP-Fehler: {e}') if method == 'tools/call' else \
            {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32000, 'message': str(e)}}


def main():
    out_lock = threading.Lock()

    def reply(resp):
        if resp is not None:
            with out_lock:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + '\n')
                sys.stdout.flush()

    def work(msg):
        try:
            with _lock:                                   # Unreal-Aufrufe nacheinander (eine Editor-Sitzung)
                reply(handle(msg))
        except Exception as e:                           # noqa: BLE001
            log('unerwartet', e)
            if 'id' in msg:
                reply({'jsonrpc': '2.0', 'id': msg['id'], 'error': {'code': -32603, 'message': str(e)}})

    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    log('Brücke gestartet, cwd', Path.cwd())
    pending = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if msg.get('method') in ('initialize', 'ping') or (msg.get('method') or '').startswith('notifications/'):
            reply(handle(msg)) if not (msg.get('method') or '').startswith('notifications/') else handle(msg)
        else:
            t = threading.Thread(target=work, args=(msg,), daemon=True)
            t.start()
            pending.append(t)
    for t in pending:                                     # Eingabe zu Ende: offene Antworten noch abschicken
        t.join(timeout=900)


if __name__ == '__main__':
    main()
