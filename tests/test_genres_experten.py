"""Übernahmen aus UltraGameStudio: Genre-Vorlagen, Experten-Rat, Agenten – vollständig und ohne Kanon-Eingriff."""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'gameforge-plugin'
sys.path.insert(0, str(PLUGIN / 'scripts'))
from gflib import genres  # noqa: E402


class Genres(unittest.TestCase):
    def test_dreissig_vollstaendige_vorlagen(self):
        self.assertEqual(len(genres.GENRES), 30)
        for gid, g in genres.GENRES.items():
            for k in ('name', 'kernschleife', 'grenzen'):
                self.assertTrue(g[k], (gid, k))
            for k in ('spielbibel', 'systeme', 'assets', 'abnahme', 'engines'):
                self.assertGreaterEqual(len(g[k]), 1, (gid, k))
            self.assertFalse(re.search(r'[一-鿿]', json.dumps(g, ensure_ascii=False)), f'{gid}: noch chinesischer Text')

    def test_engine_filter(self):
        self.assertTrue(genres.passt(genres.GENRES['metroidvania'], 'godot'))
        self.assertFalse(genres.passt(genres.GENRES['metroidvania'], 'unreal'))
        self.assertIn('⚠', genres.vorlage_md(genres.GENRES['metroidvania'], 'unreal'))

    def test_neues_spiel_mit_vorlage_aendert_spielbibel_nicht(self):
        with tempfile.TemporaryDirectory() as d:
            spiel = Path(d) / 'Kellerflucht'
            spiel.mkdir()
            env = dict(os.environ, GAMEFORGE_DATA_DIR=str(Path(d) / 'data'), PYTHONIOENCODING='utf-8', GAMEFORGE_GPU_FAKE_APPS='[]')
            gf = [sys.executable, str(PLUGIN / 'scripts' / 'gf.py')]
            r = subprocess.run(gf + ['neu', '--titel', 'Kellerflucht', '--genre-vorlage', 'horror_escape_room', '--ordner', str(spiel)],
                               capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('VORSCHLAG', (spiel / 'GENRE_VORLAGE.md').read_text(encoding='utf-8'))
            tasks = json.loads((spiel / 'aufgaben.json').read_text(encoding='utf-8'))
            self.assertEqual(sum(t['phase'] == '02 Genre-Kern' for t in tasks), 5)
            self.assertNotIn('Rätselkette', (spiel / 'SPIEL.md').read_text(encoding='utf-8'))
            self.assertEqual(json.loads((spiel / 'spiel.json').read_text(encoding='utf-8'))['genre_vorlage'], 'horror_escape_room')
            leer = Path(d) / 'Leer'
            leer.mkdir()
            r = subprocess.run(gf + ['neu', '--titel', 'X', '--genre-vorlage', 'gibtesnicht', '--ordner', str(leer)],
                               capture_output=True, text=True, env=env, timeout=120)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse((leer / 'spiel.json').exists())          # bei falscher Vorlage wird nichts angelegt


class ExpertenUndAgenten(unittest.TestCase):
    def test_experten_rat_hat_52_rollen_und_lizenz(self):
        text = (PLUGIN / 'skills' / 'gameforge-studio' / 'EXPERTEN.md').read_text(encoding='utf-8')
        rows = [l for l in text.splitlines() if l.startswith('| ') and not l.startswith('| Rolle') and not l.startswith('|---')]
        self.assertEqual(len(rows), 52)
        self.assertIn('MIT', (PLUGIN / 'THIRD_PARTY_NOTICES.md').read_text(encoding='utf-8'))

    def test_agenten_vollstaendig_und_benannt(self):
        files = sorted((PLUGIN / 'agents').glob('*.md'))
        self.assertEqual(len(files), 22)
        for f in files:
            text = f.read_text(encoding='utf-8')
            self.assertRegex(text, rf'(?m)^name: {re.escape(f.stem)}$', f.name)
            self.assertIn('/22)', text, f.name)
            self.assertIn('Abschlussbericht', text, f.name)


if __name__ == '__main__':
    unittest.main()
