"""Startskript für sichtbares Blender: stellt sicher, dass der Blender-MCP-Server (Port 9876) läuft.

Aufruf:  blender.exe --python gameforge_core/blender_mcp_start.py [datei.blend]
Schreibt den Zustand nach GAMEFORGE_DATA/logs/blender_mcp_start.log. Ändert keine Einstellungen dauerhaft.
"""
import os, socket, time, traceback
import bpy

LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'GAMEFORGE_DATA', 'logs', 'blender_mcp_start.log')


def log(msg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + msg + '\n')


def port_open():
    try:
        with socket.create_connection(('127.0.0.1', 9876), timeout=1):
            return True
    except OSError:
        return False


def check():
    try:
        addons = [k for k in bpy.context.preferences.addons.keys() if 'mcp' in k.lower()]
        log(f'online_access={bpy.app.online_access} addons={addons} port_offen={port_open()}')
        if not port_open():
            bpy.ops.blmcp.server_start()
            time.sleep(0.5)
            log(f'server_start aufgerufen, port_offen={port_open()}')
    except Exception:
        log('FEHLER ' + traceback.format_exc())
    return None


bpy.app.timers.register(check, first_interval=4.0, persistent=True)
