"""Unreal-MCP-Brücke: verbindet sich auch ohne laufendes Unreal und meldet fehlendes Projekt ehrlich."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[1] / 'gameforge_core' / 'unreal_mcp_bridge.py'


class UnrealBridge(unittest.TestCase):
    def run_bridge(self, lines, cwd):
        env = dict(os.environ, GAMEFORGE_DATA_DIR=self.data, GAMEFORGE_UNREAL_MCP_URL='http://127.0.0.1:8999/mcp',
                   GAMEFORGE_UNREAL_PROJEKT='', LOCALAPPDATA=self.data, PYTHONIOENCODING='utf-8')
        r = subprocess.run([sys.executable, '-u', str(BRIDGE)], input='\n'.join(json.dumps(x) for x in lines) + '\n',
                           capture_output=True, text=True, encoding='utf-8', env=env, cwd=cwd, timeout=60)
        return {m['id']: m for m in map(json.loads, r.stdout.splitlines()) if 'id' in m}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = str(Path(self.tmp.name) / 'data')

    def tearDown(self):
        self.tmp.cleanup()

    def test_ohne_unreal(self):
        out = self.run_bridge([
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18', 'capabilities': {}}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'list_toolsets', 'arguments': {}}},
            {'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call', 'params': {'name': 'unreal_starten', 'arguments': {'projekt': self.tmp.name}}},
        ], self.tmp.name)
        self.assertEqual(out[1]['result']['capabilities'], {'tools': {'listChanged': False}})
        self.assertIn('unreal_starten', [t['name'] for t in out[2]['result']['tools']])
        self.assertTrue(out[3]['result']['isError'])
        self.assertIn('kein Projekt', out[3]['result']['content'][0]['text'])
        self.assertTrue(out[4]['result']['isError'])            # Ordner ohne .uproject → ehrlicher Fehler, kein Start


if __name__ == '__main__':
    unittest.main()
