"""Freie Asset-Quellen: Lizenzprüfung und Größenlimit greifen, ohne Netz (Seiten werden simuliert)."""
import sys, tempfile, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gameforge-plugin' / 'scripts'))
from gflib import quellen  # noqa: E402


class Quellen(unittest.TestCase):
    def test_register_nur_freie_quellen_mit_lizenz(self):
        for k, q in quellen.QUELLEN.items():
            self.assertTrue(q['lizenz'], k)
            self.assertIn(q['zugang'].split()[0], ('auto', 'suche', 'browser', 'manuell'), k)

    def test_opengameart_laedt_nur_eindeutig_cc0(self):
        page = '<div>License(s): CC-BY 3.0 CC0</div><a href="https://opengameart.org/sites/default/files/fels.zip">x</a>'
        with mock.patch.object(quellen, '_text', return_value=page), tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as e:
                quellen.oga_fetch('fels', Path(d))
            self.assertIn('nicht eindeutig CC0', str(e.exception))

    def test_lizenzabzeichen_ist_keine_datei(self):
        page = 'CC0 <img src="https://opengameart.org/sites/default/files/cc0.png">'
        with mock.patch.object(quellen, '_text', return_value=page), tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as e:
                quellen.oga_fetch('nur-abzeichen', Path(d))
            self.assertIn('keine Dateien', str(e.exception))

    def test_groessenlimit(self):
        page = 'CC0 <a href="https://opengameart.org/sites/default/files/riesig.zip">x</a>'
        with mock.patch.object(quellen, '_text', return_value=page), mock.patch.object(quellen, 'remote_size', return_value=900_000_000), \
                tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as e:
                quellen.oga_fetch('riesig', Path(d), max_mb=300)
            self.assertIn('Limit', str(e.exception))


if __name__ == '__main__':
    unittest.main()
