"""Bild → 3D (TRELLIS.2): Workflow entspricht der offiziellen Vorlage, NoAI-Inhalte werden abgewiesen."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'gameforge-plugin'
sys.path.insert(0, str(PLUGIN / 'scripts'))
from gflib import comfy  # noqa: E402


class Workflow(unittest.TestCase):
    def test_entspricht_vorlage(self):
        wf = comfy.trellis2_i2m('x.png', seed=42)
        # Seeds wie in der Vorlage (56 Struktur, 42 Form, 42 Hochskalierung, 43 Textur)
        self.assertEqual([wf[k]['inputs']['seed'] for k in ('3', '18', '23', '12')], [56, 42, 42, 43])
        self.assertEqual(wf['94']['inputs']['target_resolution'], 1536)
        self.assertEqual(wf['147']['inputs']['texture_size'], 4096)
        self.assertEqual(wf['400']['class_type'], 'SaveGLB')
        # alle Verweise zeigen auf vorhandene Knoten
        for nid, n in wf.items():
            for v in n['inputs'].values():
                if isinstance(v, list):
                    self.assertIn(v[0], wf, f'{nid} verweist auf fehlenden Knoten {v[0]}')
        # Modelle im Workflow == Modellliste (nichts Undokumentiertes)
        names = {Path(r).name for r, _, _ in comfy.TRELLIS2_MODELS}
        used = {v for n in wf.values() for k, v in n['inputs'].items() if isinstance(v, str) and v.endswith('.safetensors')}
        self.assertEqual(used, names)

    def test_ohne_freistellen_nutzt_bildmaske(self):
        self.assertEqual(comfy.trellis2_i2m('x.png', remove_bg=False)['312']['inputs']['masks'], ['122', 1])

    def test_fehlende_modelle(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(len(comfy.trellis2_missing(d)), 5)


class NoAI(unittest.TestCase):
    def test_fab_bild_wird_abgewiesen(self):
        with tempfile.TemporaryDirectory() as d:
            spiel = Path(d) / 'Probe'
            spiel.mkdir()
            env = dict(os.environ, GAMEFORGE_DATA_DIR=str(Path(d) / 'data'), PYTHONIOENCODING='utf-8', GAMEFORGE_GPU_FAKE_APPS='[]')
            gf = [sys.executable, str(PLUGIN / 'scripts' / 'gf.py')]
            r = subprocess.run(gf + ['neu', '--titel', 'Probe', '--ordner', str(spiel)], capture_output=True, text=True, env=env, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr)
            fab = spiel / 'Fab' / 'kiste.png'
            fab.parent.mkdir()
            fab.write_bytes(b'\x89PNG\r\n\x1a\n')
            r = subprocess.run(gf + ['3d', 'Probe', '--asset', 'Kiste', '--bild', str(fab)], capture_output=True, text=True,
                               env=env, timeout=120, cwd=str(spiel))
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('NoAI', r.stdout + r.stderr)
            self.assertFalse((spiel / 'blender').exists())


if __name__ == '__main__':
    unittest.main()
