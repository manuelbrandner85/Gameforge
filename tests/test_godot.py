"""Godot-Brücke: Installation nur mit gültiger Prüfsumme, Projektdatei, Log-Auswertung, GPU-Erkennung – ohne Netz und ohne Godot."""
import hashlib, io, os, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'gameforge-plugin' / 'scripts'))
sys.path.insert(0, str(ROOT))
from gflib import godot  # noqa: E402
from gameforge_core import gpu_commander as gc  # noqa: E402


def _zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr(f'Godot_v{godot.VERSION}-stable_win64.exe', b'MZ-fenster')
        z.writestr(f'Godot_v{godot.VERSION}-stable_win64_console.exe', b'MZ-konsole')
        z.writestr('../boese.exe', b'x')
    return buf.getvalue()


def _fetcher(payload, sha):
    def fetch(url, timeout=120):
        if url.endswith('SHA512-SUMS.txt'):
            return io.BytesIO(f'{sha}  {godot.ZIP}\nabc  anderes.zip\n'.encode())
        return io.BytesIO(payload)
    return fetch


class Godot(unittest.TestCase):
    def test_installation_mit_gueltiger_pruefsumme(self):
        data = _zip_bytes()
        with tempfile.TemporaryDirectory() as d:
            exe, neu = godot.install(Path(d), fetch=_fetcher(data, hashlib.sha512(data).hexdigest()))
            self.assertTrue(neu)
            self.assertEqual(exe.name, f'Godot_v{godot.VERSION}-stable_win64.exe')
            self.assertTrue(godot.console_exe(exe).name.endswith('_console.exe'))
            self.assertFalse((Path(d) / 'tools' / 'boese.exe').exists())
            self.assertEqual(godot.find_exe(Path(d)), exe)

    def test_falsche_pruefsumme_installiert_nichts(self):
        data = _zip_bytes()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as e:
                godot.install(Path(d), fetch=_fetcher(data, '0' * 128))
            self.assertIn('Prüfsumme', str(e.exception))
            self.assertFalse(list(Path(d).rglob('*.exe')))
            self.assertFalse(list(Path(d).rglob('*.zip')))

    def test_projektdatei_und_kein_ueberschreiben(self):
        with tempfile.TemporaryDirectory() as d:
            proj = godot.create_project(Path(d), 'Testspiel', '3d')
            text = (proj / 'project.godot').read_text(encoding='utf-8')
            self.assertIn('config_version=5', text)
            self.assertIn('renderer/rendering_method="forward_plus"', text)
            self.assertIn('Jolt Physics', text)
            self.assertEqual(godot.project_dir(Path(d)), proj)
            with self.assertRaises(FileExistsError):
                godot.create_project(Path(d), 'Testspiel')
        self.assertIn('gl_compatibility', godot.project_godot('Web', 'web'))
        self.assertIn('default_texture_filter=0', godot.project_godot('Pixel', 'pixel'))

    def test_log_auswertung(self):
        log = 'Godot Engine v4.7.1\nWARNING: veraltet\nERROR: Failed loading resource: res://x.glb\nSCRIPT ERROR: Parse Error: x\nfertig'
        r = godot.parse_log(log)
        self.assertFalse(r['ok'])
        self.assertEqual(len(r['fehler']), 2)
        self.assertEqual(len(r['warnungen']), 1)
        self.assertTrue(godot.parse_log('Godot Engine v4.7.1\nalles gut')['ok'])
        echt = "ERROR: 1 RID allocations of type 'N17RendererSceneCull6CameraE' were leaked at exit."   # echte Godot-4.7.1-Ausgabe
        self.assertTrue(godot.parse_log(echt)['ok'])

    def test_pruefung_wertet_exitcode(self):
        fake = lambda *a, **k: subprocess.CompletedProcess(a, 1, 'ok', '')
        self.assertFalse(godot.check_project(Path('godot.exe'), Path('.'), run=fake)['ok'])

    def test_mcp_eintrag(self):
        e = godot.mcp_entry(Path(r'C:\g\Godot.exe'), Path(r'C:\d\index.js'), 'node.exe')
        self.assertEqual((e['command'], e['args']), ('node.exe', [r'C:\d\index.js']))
        self.assertEqual(e['env']['GODOT_PATH'], r'C:\g\Godot.exe')
        self.assertRegex(godot.MCP_PACKAGE, r'@\d+\.\d+\.\d+$')      # feste Version, kein „latest“

    def test_mcp_installation_meldet_fehler(self):
        fail = lambda *a, **k: subprocess.CompletedProcess(a, 1, '', 'npm ERR! 404')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError) as e:
                godot.install_mcp(Path(d), run=fail)
            self.assertIn('404', str(e.exception))

    def test_neues_godot_spiel_per_kommandozeile(self):
        with tempfile.TemporaryDirectory() as d:
            spiel = Path(d) / 'Mondgarten'
            spiel.mkdir()
            env = dict(os.environ, GAMEFORGE_DATA_DIR=str(Path(d) / 'data'), PYTHONIOENCODING='utf-8', GAMEFORGE_GPU_FAKE_APPS='[]')
            gf = [sys.executable, str(ROOT / 'gameforge-plugin' / 'scripts' / 'gf.py')]
            r = subprocess.run(gf + ['neu', '--titel', 'Mondgarten', '--engine', 'godot', '--stil', 'Pixel-Art', '--ordner', str(spiel)],
                               capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('Godot 4', r.stdout)
            self.assertIn('06 Godot', (spiel / 'aufgaben.json').read_text(encoding='utf-8'))
            self.assertIn('godot/', (spiel / 'CLAUDE.md').read_text(encoding='utf-8'))
            r = subprocess.run(gf + ['godot', 'projekt', str(spiel), '--profil', 'pixel'], capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((spiel / 'godot' / 'project.godot').is_file())
            r = subprocess.run(gf + ['godot', 'import', str(spiel), '--asset', 'fehlt'], capture_output=True, text=True, env=env, timeout=120)
            self.assertNotEqual(r.returncode, 0)                    # ohne Godot bzw. Exportdatei: klare Meldung, nichts kopiert
            self.assertFalse((spiel / 'godot' / 'assets').exists())

    def test_gpu_waechter_erkennt_godot(self):
        self.assertEqual(gc.classify('Godot_v4.7.1-stable_win64.exe', 'Godot.exe -e --path x'), ('Godot', 'Fenster (Editor)'))
        self.assertEqual(gc.classify('Godot_v4.7.1-stable_win64_console.exe', 'x --headless --import'), ('Godot', 'Kommandozeile'))


if __name__ == '__main__':
    unittest.main()
