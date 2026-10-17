"""Tests für GAMEFORGE 2.0: Migration, Löschen/Papierkorb, Scanner, Pipeline, Live-Monitor, Agenten, API."""
import io, json, sqlite3, subprocess, sys, tempfile, time, unittest, zipfile
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app
from app import Store, Server
import agent_live, agent_studio, studio_v2, game_trash

PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 64


class V2Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = Store(self.root / 'data')

    def tearDown(self):
        self.db.conn.close()
        self.tmp.cleanup()


class MigrationTests(unittest.TestCase):
    def test_v1_database_is_migrated_with_backup_and_data_kept(self):
        with tempfile.TemporaryDirectory() as t:
            base = Path(t) / 'data'; base.mkdir()
            con = sqlite3.connect(base / 'gameforge.sqlite3')
            # Minimales v1-Schema mit einem Spiel und einem Auftrag
            con.executescript('''CREATE TABLE games(id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Konzept', genre TEXT NOT NULL DEFAULT '', style TEXT NOT NULL DEFAULT '', engine TEXT NOT NULL DEFAULT 'Unreal Engine 5', camera TEXT NOT NULL DEFAULT '', version TEXT NOT NULL DEFAULT 'v0.1', bible TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
              CREATE TABLE direct_jobs(id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id), kind TEXT NOT NULL, task_id TEXT, status TEXT NOT NULL, instruction TEXT NOT NULL, log TEXT NOT NULL DEFAULT '', exit_code INTEGER, created_at TEXT NOT NULL, ended_at TEXT);''')
            con.execute("INSERT INTO games VALUES('aion-2026','AION 2026','Original','Konzept','','','Unreal Engine 5','','v18.0','{\"canon\":\"1102 v. Chr.\"}','2026-01-01','2026-01-01')")
            con.execute("INSERT INTO direct_jobs VALUES('j1','aion-2026','plan',NULL,'Abgeschlossen','x','log',0,'2026-01-01','2026-01-01')")
            con.commit(); con.close()
            s = Store(base)
            try:
                self.assertEqual(s.schema_version, app.SCHEMA_VERSION)
                self.assertTrue(list((base / 'backups').glob('vor_migration_v2_*.sqlite3')))
                g = s.game('aion-2026')
                self.assertEqual(g['summary'], 'Original')
                self.assertIn('1102', g['bible']['canon'])
                self.assertEqual(len(s.games()), 1, 'GENESIS darf nicht nachträglich in eine bestehende Bibliothek eingefügt werden')
                cols = [r[1] for r in s.conn.execute('PRAGMA table_info(direct_jobs)')]
                self.assertIn('user_instruction', cols)
                self.assertEqual(s.direct.job('aion-2026', 'j1')['log'], 'log')
            finally:
                s.conn.close()
            # Zweiter Start: keine erneute Migration/Sicherung
            s2 = Store(base); s2.conn.close()
            self.assertEqual(len(list((base / 'backups').glob('*.sqlite3'))), 1)


class GameLifecycleTests(V2Base):
    def test_wizard_fields_are_stored_as_user_input(self):
        g = self.db.add_game({'title': 'OLYMPUS', 'vision': 'Götter-Open-World', 'platform': 'Windows-PC', 'wishes': 'Bosskämpfe', 'style': 'Stilisiert'})
        self.assertEqual(g['bible']['vision'], 'Götter-Open-World')
        self.assertIn('Windows-PC', g['bible']['release'])
        self.assertIn('Bosskämpfe', g['bible']['game_rules'])
        self.assertEqual(g['bible']['story'], '', 'Es dürfen keine Inhalte erfunden werden')
        self.assertEqual(len(self.db.tasks(g['id'])), 25)

    def test_delete_moves_to_trash_and_restore_brings_everything_back(self):
        gid = 'aion-2026'
        did = self.db.add_dlc(gid, {'title': 'Tiefen'})
        rid = self.db.add_ref(gid, {'name': 'Zeus', 'category': 'boss', 'view': 'front'})
        self.db.save_upload(io.BytesIO(PNG), len(PNG), filename='zeus.png', kind='Referenzen', game_id=gid, reference_id=rid)
        f = self.db.save_game_file(io.BytesIO(b'Kanon-Dokument'), 14, game_id=gid, filename='kanon.md')
        self.db.add_idea_message(gid, 'Idee', dlc_id=did)
        before = self.db.game(gid)
        with self.assertRaises(ValueError):
            game_trash.delete_game(self.db, gid, 'falscher Name')
        self.assertIsNotNone(self.db.game(gid))
        res = game_trash.delete_game(self.db, gid, 'AION 2026')
        self.assertIsNone(self.db.game(gid))
        self.assertFalse((self.db.base / 'imports' / f['id']).exists())
        self.assertEqual(self.db.one('SELECT COUNT(*) n FROM dlcs WHERE game_id=?', (gid,))['n'], 0)
        self.assertIsNotNone(self.db.game('genesis'), 'Andere Spiele bleiben unberührt')
        trash = game_trash.trash_list(self.db)
        self.assertEqual(trash[0]['title'], 'AION 2026')
        self.assertTrue(trash[0]['restorable'])
        with zipfile.ZipFile(self.db.base / 'papierkorb' / res['trash_file']) as z:
            self.assertIsNone(z.testzip())
        game_trash.restore_game(self.db, res['trash_file'])
        after = self.db.game(gid)
        self.assertEqual(after['bible'], before['bible'])
        self.assertEqual(self.db.dlcs(gid)[0]['title'], 'Tiefen')
        self.assertEqual((self.db.base / 'imports' / f['id']).read_bytes(), b'Kanon-Dokument')
        self.assertTrue(self.db.refs(gid)[-1]['image_path'] or any(r['image_path'] for r in self.db.refs(gid)))
        self.assertEqual(len(self.db.idea_feed(gid, did)['messages']), 1)
        self.assertEqual(game_trash.trash_list(self.db), [], 'Wiederhergestellter Eintrag wird umbenannt')

    def test_purge_needs_explicit_word_and_deleted_seed_games_stay_deleted(self):
        r1 = game_trash.delete_game(self.db, 'genesis', 'GENESIS')
        with self.assertRaises(ValueError):
            game_trash.purge(self.db, r1['trash_file'], 'ja')
        game_trash.purge(self.db, r1['trash_file'], 'ENDGÜLTIG')
        game_trash.delete_game(self.db, 'aion-2026', 'AION 2026')
        self.db.conn.close()
        self.db = Store(self.root / 'data')
        self.assertEqual(self.db.games(), [], 'Gelöschte Startprojekte dürfen beim Neustart nicht wieder erscheinen')
        with self.assertRaises(ValueError):
            game_trash.purge(self.db, '../gameforge.sqlite3', 'ENDGÜLTIG')

    def test_backup_zip_contains_database(self):
        b = self.db.create_backup()
        with zipfile.ZipFile(b) as z:
            self.assertIn('GAMEFORGE_DATA/gameforge.sqlite3', z.namelist())


class ScannerAndPipelineTests(V2Base):
    def test_scanner_reports_duplicates_and_missing(self):
        a = self.db.save_game_file(io.BytesIO(b'gleich'), 6, game_id='aion-2026', filename='a.txt')
        self.db.save_game_file(io.BytesIO(b'gleich'), 6, game_id='aion-2026', filename='b.txt')
        first = studio_v2.project_scan(self.db, 'aion-2026')
        self.assertTrue(first['ok'])
        self.assertEqual(len(first['duplicates']), 1)
        (self.db.base / 'imports' / a['id']).unlink()
        scan = studio_v2.project_scan(self.db, 'aion-2026')
        self.assertFalse(scan['ok'])
        self.assertEqual(scan['missing'][0]['name'], 'a.txt')

    def test_pipeline_stages_come_only_from_real_files(self):
        ws = self.root / 'ws'; ws.mkdir()
        self.db.direct.configure('aion-2026', {'workspace': str(ws)})
        spec = __import__('asset_pipeline').prepare(self.db, 'aion-2026', {'name': 'Dreizack', 'type': 'weapon', 'requirements': '2 m lang'})
        aid = spec['asset_id']
        stage = lambda: studio_v2.pipeline_assets(self.db, 'aion-2026')['assets'][0]['stage']
        self.assertEqual(stage(), 'geplant')
        out = ws / 'Assets' / aid; out.mkdir(parents=True)
        (out / f'{aid}.blend').write_bytes(b'')  # leere Datei zählt nicht
        (out / f'{aid}.fbx').write_bytes(b'Kaydara FBX Binary  \x00')
        self.assertEqual(stage(), 'geplant')
        (out / f'{aid}.blend').write_bytes(b'BLENDER-v405' + b'\x00' * 32)
        self.assertEqual(stage(), 'Datei erstellt')
        with self.assertRaises(ValueError):
            studio_v2.approve_asset(self.db, 'aion-2026', aid)
        ue = ws / 'Content' / 'GAMEFORGE' / aid; ue.mkdir(parents=True)
        (ue / 'SM_Dreizack.uasset').write_bytes(b'\xc1\x83\x2a\x9e')
        self.assertEqual(stage(), 'Unreal importiert')
        (ws / '.gameforge' / 'asset_pipeline' / aid / 'QA_REPORT.md').write_text('Import geprüft, Maßstab 2 m korrekt, Kollision vorhanden, PIE-Test ohne Fehler.', encoding='utf-8')
        self.assertEqual(stage(), 'getestet')
        studio_v2.approve_asset(self.db, 'aion-2026', aid)
        self.assertEqual(stage(), 'freigegeben')
        self.assertEqual(studio_v2.pipeline_assets(self.db, 'genesis')['assets'], [], 'Projekte bleiben getrennt')

    @unittest.skipUnless(studio_v2.find_blender(), 'Blender nicht installiert')
    def test_real_blender_background_run_creates_valid_files(self):
        ws = self.root / 'ws'; ws.mkdir()
        self.db.direct.configure('aion-2026', {'workspace': str(ws)})
        job = studio_v2.start_blender_test(self.db, 'aion-2026')
        for _ in range(300):
            j = self.db.direct.job('aion-2026', job['id'])
            if j['status'] != 'Läuft': break
            time.sleep(1)
        self.assertEqual(j['status'], 'Abgeschlossen', j['log'])
        self.assertIn('OK  GF_TestCrate.blend', j['log'])
        self.assertIn('[1.0, 1.0, 1.0]', j['log'])
        files = list((ws / '.gameforge' / 'system_tests').rglob('GF_TestCrate.*'))
        self.assertEqual({p.suffix for p in files} & {'.blend', '.fbx', '.glb'} >= {'.blend'}, True)


class AgentTests(V2Base):
    def test_roster_defines_inputs_scope_and_handoff_for_all_20(self):
        rows = agent_studio.roster(detailed=True)
        self.assertEqual(len(rows), 20)
        for r in rows:
            self.assertTrue(r['inputs'] and r['handoff'] and r['write_scope'], r['slug'])
            self.assertNotIn('bypassPermissions', r['permission_mode'])
        files = agent_studio.package_files(self.db.game('aion-2026'))
        md = files['.claude/agents/blender-3d.md']
        self.assertIn('Übergabe an: animation-rigging, materials-visual', md)
        self.assertIn('permissionMode: default', md)
        self.assertIn('mcpServers:', md)

    def test_hook_uses_real_interpreter_and_upgrades_v1_command(self):
        work = self.root / 'repo'; (work / '.claude').mkdir(parents=True)
        cfg = work / '.claude' / 'settings.local.json'
        cfg.write_text(json.dumps({'hooks': {'SubagentStart': [{'hooks': [{'type': 'command', 'command': agent_live.LEGACY_COMMAND}]}]}}), encoding='utf-8')
        res = agent_live.install(work)
        self.assertTrue(res['changed'])
        data = json.loads(cfg.read_text(encoding='utf-8'))
        commands = [h['command'] for e in data['hooks'].values() for i in e for h in i['hooks']]
        self.assertNotIn(agent_live.LEGACY_COMMAND, commands)
        self.assertEqual(len([c for c in data['hooks']['SubagentStart'][0]['hooks']]), 1, 'Kein doppelter Hook')
        # Hook mit genau dem eingetragenen Befehl ausführen (echte Shell)
        cmd = commands[0]
        for ev in ({'hook_event_name': 'SubagentStart', 'agent_id': 'x1', 'agent_type': 'blender-3d', 'session_id': 's'},
                   {'hook_event_name': 'PostToolUseFailure', 'agent_id': 'x2', 'agent_type': 'unreal-programming', 'session_id': 's', 'tool_name': 'mcp__unreal-mcp__import'}):
            r = subprocess.run(cmd, shell=True, cwd=work, input=json.dumps(ev), text=True, capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
        st = agent_live.status(work, agent_studio.roster())
        states = {a['slug']: a['state'] for a in st['agents']}
        self.assertEqual(states['blender-3d'], 'Arbeitet')
        self.assertEqual(states['unreal-programming'], 'Fehler')
        self.assertEqual(states['story-narrative'], 'Wartet')
        self.assertEqual(agent_live.status(None, agent_studio.roster())['agents'][0]['state'], 'Keine Verbindung')


class ChatAndStatusTests(V2Base):
    def test_status_question_is_answered_from_real_data_without_ai(self):
        feed = self.db.brainstorm('aion-2026', {'message': 'Wie weit sind wir? Was ist wirklich fertig?', 'provider': 'offline'})
        last = feed['messages'][-1]
        self.assertEqual(last['provider'], 'data')
        self.assertIn('0 von 25 abgenommen', last['body'])
        self.assertEqual(feed['changes'], [])

    def test_helpers(self):
        out = 'Checking MCP server health...\n\nblender: uvx blender-mcp - ✓ Connected\nunreal-mcp: python srv.py - ✗ Failed to connect\n'
        s = studio_v2.parse_mcp_list(out)
        self.assertEqual([(x['name'], x['state']) for x in s], [('blender', 'Verbunden'), ('unreal-mcp', 'Fehlgeschlagen')])
        self.assertTrue(studio_v2.is_auth_error('Failed to authenticate: OAuth session expired'))
        self.assertFalse(studio_v2.is_auth_error('Timeout beim Import'))

    def test_retry_only_for_failed_jobs(self):
        self.db.execute("INSERT INTO direct_jobs(id,game_id,kind,status,instruction,created_at) VALUES('ok1','aion-2026','plan','Abgeschlossen','x','2026')")
        with self.assertRaises(ValueError):
            self.db.direct.retry('aion-2026', 'ok1')

    def test_roadmap_status_is_honest(self):
        rm = json.loads((app.RESOURCE / 'ROADMAP_APPROVED_1_40.json').read_text(encoding='utf-8'))
        rs = studio_v2.roadmap_status(rm)
        ids = {f['id'] for f in rs['features']}
        self.assertEqual(len(ids), 35)
        self.assertFalse(ids & {21, 22, 23, 37, 39})
        self.assertEqual(rs['counts']['fertig'], 0, 'Keine Erweiterung darf ohne Abnahme als fertig gelten')


class ApiTests(V2Base):
    def setUp(self):
        super().setUp()
        self.srv = Server(('127.0.0.1', 0), self.db)
        Thread(target=self.srv.serve_forever, daemon=True).start()
        self.port = self.srv.server_address[1]

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close()
        super().tearDown()

    def req(self, method, path, body=None):
        c = HTTPConnection('127.0.0.1', self.port, timeout=30)
        c.request(method, path, body=json.dumps(body) if body is not None else None, headers={'Content-Type': 'application/json'})
        r = c.getresponse(); data = r.read(); c.close()
        return r.status, data

    def test_endpoints(self):
        for path in ('/', '/app.js', '/styles.css', '/api/config', '/api/home', '/api/roadmap/status', '/api/trash', '/api/agents',
                     '/api/games/aion-2026', '/api/games/aion-2026/scan', '/api/games/aion-2026/pipeline', '/api/games/aion-2026/live'):
            st, _ = self.req('GET', path)
            self.assertEqual(st, 200, path)
        st, d = self.req('GET', '/api/config')
        self.assertEqual(json.loads(d)['version'], app.VERSION)
        st, d = self.req('GET', '/api/agents')
        self.assertIn('handoff', json.loads(d)['agents'][0])
        st, d = self.req('DELETE', '/api/games/genesis?confirm=falsch')
        self.assertEqual(st, 400)
        st, d = self.req('DELETE', '/api/games/genesis?confirm=GENESIS')
        self.assertEqual(st, 200)
        name = json.loads(d)['trash_file']
        st, d = self.req('POST', '/api/trash/' + name + '/restore', {})
        self.assertEqual(st, 200)
        st, d = self.req('GET', '/api/games/genesis')
        self.assertEqual(st, 200)
        st, _ = self.req('GET', '/api/gibtesnicht')
        self.assertEqual(st, 404)


if __name__ == '__main__':
    unittest.main()
