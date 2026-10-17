"""Tests der Reference Engine ohne GPU (ComfyUI wird durch eine leere Test-Installation ersetzt und nie gestartet)."""
import json, struct, sys, tempfile, unittest, zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Store
import game_trash
from reference_engine import art_direction, comfy, imagecheck, models, prompts, quality


def write_png(path, w, h, pixel):
    raw = b''.join(b'\x00' + b''.join(bytes(pixel(x, y)) for x in range(w)) for y in range(h))
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


class RefBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.db = Store(self.root / 'data')
        self.eng = self.db.refengine
        # Test-ComfyUI: Struktur + leere Modelldateien, Worker wird nie gestartet.
        fake = self.root / 'app'; base = fake / 'engines' / 'ComfyUI_windows_portable' / 'ComfyUI'
        (base).mkdir(parents=True); (base / 'main.py').write_text('')
        for rel in models.MODELS[0]['files']:
            p = base / 'models' / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b'x')
        self.eng.comfy.app_root = fake
        self.eng._ensure_worker = lambda: None

    def tearDown(self):
        self.db.conn.close(); self.tmp.cleanup()


class ArtDirectionTests(RefBase):
    def test_profiles_follow_each_games_style(self):
        aion = self.eng.profile('aion-2026')['profile']
        self.assertEqual(aion['style_id'], 'aaa_photoreal')
        self.assertEqual(aion['quality_auto'], 'CINEMATIC_MASTER')
        self.assertIn('1102', aion['canon_excerpt'])
        pix = self.db.add_game({'title': 'Pixel Quest', 'style': 'Pixel-Art', 'genre': 'Jump & Run'})
        p = self.eng.profile(pix['id'])['profile']
        self.assertEqual(p['style_id'], 'pixel_art')
        self.assertEqual(p['postprocess']['pixel_grid'], 8)
        toon = self.db.add_game({'title': 'Toonland', 'style': 'Cartoon'})
        self.assertEqual(self.eng.profile(toon['id'])['profile']['quality_auto'], 'STANDARD', 'Cartoon wird nicht auf Fotorealismus hochgestuft')
        self.assertIsNotNone(self.db.one('SELECT game_id FROM art_profiles WHERE game_id=?', (toon['id'],)), 'Neues Spiel bekommt Profil automatisch')

    def test_user_edits_are_kept_and_validated(self):
        art_direction.update_profile(self.db, 'genesis', {'style_id': 'stylized_3d', 'color_palette': 'Erdtöne', 'approved': True})
        p = self.eng.profile('genesis')
        self.assertEqual(p['profile']['style_id'], 'stylized_3d'); self.assertEqual(p['approved'], 1)
        self.assertEqual(p['source'], 'vom Nutzer bearbeitet')
        with self.assertRaises(ValueError):
            art_direction.update_profile(self.db, 'genesis', {'style_id': 'gibtsnicht'})


class RouterQualityPromptTests(RefBase):
    def test_router_and_missing_models(self):
        r = models.route(self.eng.comfy.root, 'pixel_art')
        self.assertTrue(r['ok']); self.assertEqual(r['fit'], 'mit Nachbearbeitung')
        self.assertFalse(models.route(None, 'realistic')['ok'])
        self.assertFalse(models.route(self.eng.comfy.root, 'realistic', capability='inpainting')['ok'], 'Nicht angebundene Fähigkeiten werden nicht behauptet')

    def test_quality_and_dimensions(self):
        q, qp = quality.resolve('AUTO', {'quality_auto': 'HIGH'})
        self.assertEqual(q, 'HIGH'); self.assertEqual(qp['variants'], 2)
        w, h = quality.dimensions(1024, 'front', 'boss')
        self.assertEqual((w % 16, h % 16), (0, 0)); self.assertGreater(h, w)
        w, h = quality.dimensions(1024, 'overview', 'environment'); self.assertGreater(w, h)

    def test_prompt_and_consistent_seed(self):
        prof = self.eng.profile('aion-2026')['profile']
        ref = {'name': 'Zeus', 'category': 'boss', 'view': 'front', 'details': 'goldene Rüstung'}
        p1, h1 = prompts.build(prof, ref, 'AION 2026')
        p2, h2 = prompts.build(prof, dict(ref, view='side'), 'AION 2026')
        self.assertIn('goldene Rüstung', p1); self.assertIn('front view', p1); self.assertIn('No text', p1)
        self.assertEqual(h1, h2, 'Ansicht ändert das Design nicht')
        self.assertEqual(prompts.asset_seed('aion-2026', 'Zeus'), prompts.asset_seed('aion-2026', ' zeus '))
        self.assertNotEqual(prompts.asset_seed('aion-2026', 'Zeus', 1), prompts.asset_seed('aion-2026', 'Zeus', 0))

    def test_workflow_contains_pixel_postprocess(self):
        wf = comfy.klein_t2i('x', 1, 1024, 768, pixel={'pixel_grid': 8, 'colors': 16})
        types = {n['class_type'] for n in wf.values()}
        self.assertTrue({'ImageQuantize', 'SaveImage', 'UNETLoader'} <= types)
        self.assertEqual(wf['22']['inputs']['upscale_method'], 'nearest-exact')


class ImageCheckTests(unittest.TestCase):
    def test_checks(self):
        with tempfile.TemporaryDirectory() as t:
            ok = Path(t) / 'ok.png'
            write_png(ok, 64, 48, lambda x, y: ((x * 4) % 256, (y * 5) % 256, (x * y) % 256))
            r = imagecheck.check_image(ok, 64, 48)
            self.assertTrue(r['ok'], r); self.assertTrue(r['needs_human_review'])
            black = Path(t) / 'black.png'; write_png(black, 32, 32, lambda x, y: (0, 0, 0))
            self.assertFalse(imagecheck.check_image(black)['ok'])
            pix = Path(t) / 'pix.png'
            write_png(pix, 64, 64, lambda x, y: ((x // 8) * 30 % 256, (y // 8) * 40 % 256, 90))
            self.assertTrue(imagecheck.check_image(pix, pixel_grid=8, max_colors=80)['ok'])
            self.assertFalse(imagecheck.check_image(ok, pixel_grid=8)['ok'], 'Kein echtes Pixelraster')
            bad = Path(t) / 'bad.png'; bad.write_bytes(b'nope')
            self.assertFalse(imagecheck.check_image(bad)['ok'])


class JobTests(RefBase):
    def _image_for(self, jid, review='Zur Freigabe'):
        j = self.eng.job(jid)
        folder = self.eng.out_dir / j['game_id']; folder.mkdir(parents=True, exist_ok=True)
        write_png(folder / (jid + '.png'), 16, 16, lambda x, y: (x * 9, y * 9, 50))
        self.db.execute('INSERT INTO ref_images(id,game_id,ref_task_id,job_id,file,version,meta,review,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                        ('img' + jid[:8], j['game_id'], j['ref_task_id'], jid, jid + '.png', 1, json.dumps({'model_id': j['model_id']}), review, '2026'))
        self.db.execute("UPDATE ref_jobs SET status='Abgeschlossen' WHERE id=?", (jid,))
        return 'img' + jid[:8]

    def test_create_reuse_cancel_retry_and_isolation(self):
        r = self.eng.create('aion-2026', {'name': 'Zeus', 'category': 'boss', 'views': ['front', 'side'], 'quality': 'STANDARD', 'details': 'Bart'})
        self.assertEqual(len(r['created']), 2); self.assertEqual(r['quality'], 'STANDARD')
        again = self.eng.create('aion-2026', {'ref_task_ids': [self.eng.job(r['created'][0])['ref_task_id']], 'quality': 'STANDARD'})
        self.assertEqual(again['created'], []); self.assertIn('identischer Auftrag', again['skipped'][0]['reason'])
        self.assertEqual(self.eng.jobs('genesis'), [], 'Projekte bleiben getrennt')
        c = self.eng.cancel(r['created'][1]); self.assertEqual(c['status'], 'Abgebrochen')
        self.assertEqual(self.eng.retry(r['created'][1])['status'], 'Wartend')
        with self.assertRaises(ValueError):
            self.eng.retry(r['created'][0])

    def test_approve_feeds_existing_reference_and_reuse(self):
        r = self.eng.create('aion-2026', {'name': 'Poseidon', 'category': 'boss', 'views': ['front'], 'quality': 'DRAFT'})
        jid = r['created'][0]; iid = self._image_for(jid)
        res = self.eng.review('aion-2026', iid, 'approve')
        ref = self.db.one('SELECT * FROM ref_tasks WHERE id=?', (res['ref_task_id'],))
        self.assertEqual(ref['approved'], 1); self.assertTrue((self.db.base / 'refs' / ref['image_path']).is_file())
        skip = self.eng.create('aion-2026', {'ref_task_ids': [ref['id']]})
        self.assertIn('wiederverwendet', skip['skipped'][0]['reason'])
        forced = self.eng.create('aion-2026', {'ref_task_ids': [ref['id']], 'force': True, 'quality': 'DRAFT'})
        self.assertEqual(self.eng.job(forced['created'][0])['variant'], 1, 'Neue Variante bekommt neuen Seed')
        bad = self._image_for(forced['created'][0], 'Technisch fehlerhaft')
        with self.assertRaises(ValueError):
            self.eng.review('aion-2026', bad, 'approve')

    def test_trash_includes_generated_images(self):
        r = self.eng.create('genesis', {'name': 'Held', 'category': 'character', 'views': ['front'], 'quality': 'DRAFT'})
        self._image_for(r['created'][0])
        res = game_trash.delete_game(self.db, 'genesis', 'GENESIS')
        self.assertFalse((self.eng.out_dir / 'genesis').exists())
        self.assertIsNone(self.db.one("SELECT id FROM ref_jobs WHERE game_id='genesis'"))
        game_trash.restore_game(self.db, res['trash_file'])
        self.assertEqual(len(self.eng.images('genesis')), 1)
        self.assertTrue(self.eng.image_path('genesis', self.eng.images('genesis')[0]['id']).is_file())


if __name__ == '__main__':
    unittest.main()
