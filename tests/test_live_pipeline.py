import io, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from app import Store
import agent_live, agent_studio, asset_pipeline

class LivePipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Store(Path(self.tmp.name)/'data')
    def tearDown(self):
        self.db.conn.close();self.tmp.cleanup()

    def test_new_project_is_separate_workspace_with_agents(self):
        a=self.db.add_game({'title':'ATLANTIS','summary':'Testprojekt'})
        b=self.db.add_game({'title':'VULKAN','summary':'Testprojekt 2'})
        aw=Path(self.db.direct.settings(a['id'])['workspace'])
        bw=Path(self.db.direct.settings(b['id'])['workspace'])
        self.assertNotEqual(aw,bw)
        self.assertTrue((aw/'.claude/agents/studio-director.md').is_file())
        self.assertTrue((bw/'.claude/agents/blender-3d.md').is_file())
        self.assertEqual(self.db.direct.settings('aion-2026')['workspace'],'')

    def test_hooks_report_real_subagent_events_and_preserve_existing_settings(self):
        work=Path(self.tmp.name)/'repo';work.mkdir()
        config=work/'.claude'/'settings.local.json';config.parent.mkdir()
        config.write_text(json.dumps({'permissions':{'allow':['Read']}}),encoding='utf-8')
        x=agent_live.install(work)
        self.assertTrue(x['changed'])
        self.assertEqual(json.loads(config.read_text())['permissions']['allow'],['Read'])
        self.assertEqual(agent_live.install(work)['changed'],False)
        self.assertTrue(list(config.parent.glob('settings.local.gameforge-backup-*.json')))
        hook=work/'.gameforge/agent_hook.py'
        for action in ('SubagentStart','SubagentStop'):
            payload={'hook_event_name':action,'agent_id':'a77','agent_type':'blender-3d','session_id':'s1',
                     'last_assistant_message':'NEVER_RECORD_THIS_PRIVATE_MESSAGE'}
            r=subprocess.run([sys.executable,str(hook)],input=json.dumps(payload),capture_output=True,text=True,cwd=work)
            self.assertEqual(r.returncode,0,r.stderr)
        events=agent_live.status(work,agent_studio.roster())
        self.assertTrue(events['configured'])
        self.assertEqual(len(events['events']),2)
        self.assertEqual(events['active_count'],0)
        self.assertNotIn('NEVER_RECORD_THIS_PRIVATE_MESSAGE',(work/'.gameforge/agent_events.jsonl').read_text())
        self.assertNotIn('}\\n{',(work/'.gameforge/agent_events.jsonl').read_text())

    def test_asset_handoff_contains_real_reference_copy_not_fake_3d(self):
        gid='aion-2026'
        w=Path(self.tmp.name)/'AION';w.mkdir()
        self.db.direct.configure(gid,{'workspace':str(w)})
        image=self.db.base/'refs'/'test.png';image.write_bytes(b'PNG_REF_TEST')
        self.db.execute('INSERT INTO ref_tasks(id,game_id,dlc_id,name,category,view,details,required,approved,image_path,image_name,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        ('ref-test',gid,None,'Zeus','Charakter','front','',1,1,'test.png','test.png','now','now'))
        res=asset_pipeline.prepare(self.db,gid,{'name':'Zeus','type':'character','reference_ids':['ref-test'],
                                               'requirements':'30 Meter groß, Hammer, Blitz'})
        jobdir=w/'.gameforge'/'asset_pipeline'/res['asset_id']
        self.assertEqual((jobdir/'references/01_ref-test.png').read_bytes(),b'PNG_REF_TEST')
        spec=json.loads((jobdir/'asset_spec.json').read_text())
        self.assertIn('NICHT MODELLIERT',spec['status'])
        self.assertTrue((jobdir/'BLENDER_TASK.md').exists())
        self.assertTrue((jobdir/'UNREAL_TASK.md').exists())
        self.assertTrue((jobdir/'unreal_import_template.py').exists())
        self.assertFalse((w/'Assets'/res['asset_id']/(res['asset_id']+'.blend')).exists())
        with self.assertRaises(ValueError):asset_pipeline.prepare(self.db,gid,{'name':'Ares','type':'character','reference_ids':['missing']})
        alt=asset_pipeline.prepare(self.db,gid,{'name':'Schild','type':'static','reference_ids':[],'requirements':'Runder Bronzeschild mit 1m Durchmesser'})
        content=json.loads((w/'.gameforge/asset_pipeline'/alt['asset_id']/'asset_spec.json').read_text())
        self.assertEqual(content['source_type'],'claude_entwurf_aus_beschreibung')

if __name__=='__main__':unittest.main()
