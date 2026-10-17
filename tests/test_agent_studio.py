import io, json, tempfile, unittest, zipfile
from pathlib import Path
from http.client import HTTPConnection
from threading import Thread
from app import Store, Server
import agent_studio

class AgentStudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(Path(self.tmp.name)/'data')
        self.gid='aion-2026'
        self.work=Path(self.tmp.name)/'game_project'
        self.work.mkdir()
    def tearDown(self):
        self.store.conn.close()
        self.tmp.cleanup()
    def test_roster_exactly_20_unique_and_roles(self):
        r=agent_studio.roster()
        self.assertEqual(len(r),20)
        self.assertEqual(len({a['slug'] for a in r}),20)
        self.assertEqual(r[0]['slug'],'studio-director')
        self.assertEqual(r[-1]['slug'],'dlc-release')
    def test_package_contains_20_claude_subagents(self):
        files=agent_studio.package_files(self.store.game(self.gid))
        defs={k:v for k,v in files.items() if k.startswith('.claude/agents/')}
        self.assertEqual(len(defs),20)
        self.assertTrue(all(v.startswith('---\nname: ') for v in defs.values()))
        self.assertIn('mcp__blender__*',defs['.claude/agents/blender-3d.md'])
        self.assertIn('mcp__unreal-mcp__*',defs['.claude/agents/unreal-programming.md'])
        self.assertIn('mcp__*',defs['.claude/agents/reference-director.md'])
        self.assertNotIn('mcp__blender__*',defs['.claude/agents/story-narrative.md'].split('tools: ')[1].split('\n')[0])
    def test_install_preserves_existing_files_and_rejects_overwrite(self):
        self.store.direct.configure(self.gid,{'workspace':str(self.work)})
        (self.work/'CLAUDE.md').write_text('ORIGINAL NICHT VERAENDERN',encoding='utf-8')
        result=agent_studio.install(self.store.game(self.gid),self.work)
        self.assertEqual(result['agents'],20)
        self.assertEqual((self.work/'CLAUDE.md').read_text(encoding='utf-8'),'ORIGINAL NICHT VERAENDERN')
        with self.assertRaises(ValueError):agent_studio.install(self.store.game(self.gid),self.work)
        self.assertTrue((self.work/'.claude'/'agents'/'studio-director.md').is_file())
    def test_dlc_scope_and_zip_export(self):
        did=self.store.add_dlc(self.gid,{'title':'Poseidons Rückkehr'})
        dlc=self.store.dlcs(self.gid)[0]
        blob=agent_studio.package_bytes(self.store.game(self.gid),dlc)
        with zipfile.ZipFile(blob) as z:
            v=json.loads(z.read('.gameforge/AGENT_PROJECT.json'))
            self.assertEqual(v['dlc_id'],did)
            self.assertEqual(v['dlc_title'],'Poseidons Rückkehr')
            self.assertEqual(len([f for f in z.namelist() if f.startswith('.claude/agents/')]),20)
    def test_export_claude_includes_agents_and_roadmap(self):
        b,_=self.store.zip_package(self.gid)
        with zipfile.ZipFile(b) as z:
            self.assertIn('AGENT_STUDIO/.claude/agents/studio-director.md',z.namelist())
            self.assertIn('GAMEFORGE_ROADMAP/ROADMAP_APPROVED_1_40.json',z.namelist())
    def test_api_install_download_and_roster(self):
        self.store.direct.configure(self.gid,{'workspace':str(self.work)})
        srv=Server(('127.0.0.1',0),self.store)
        thread=Thread(target=srv.serve_forever,daemon=True);thread.start()
        conn=HTTPConnection('127.0.0.1',srv.server_address[1],timeout=8)
        try:
            conn.request('GET','/api/agents');r=conn.getresponse();data=json.loads(r.read())
            self.assertEqual(data['approved_count'],20)
            conn.request('GET','/api/games/aion-2026/agents/export');r=conn.getresponse()
            self.assertEqual(r.status,200)
            self.assertTrue(zipfile.is_zipfile(io.BytesIO(r.read())))
            data=json.dumps({}).encode('utf-8')
            conn.request('POST','/api/games/aion-2026/agents/install',body=data,headers={'Content-Type':'application/json'})
            r=conn.getresponse();ans=json.loads(r.read())
            self.assertEqual(ans['agents'],20)
        finally:
            conn.close();srv.shutdown();srv.server_close()
if __name__=='__main__':unittest.main()
