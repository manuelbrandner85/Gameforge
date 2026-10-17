import io
import os
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from app import Store


class DirectStudioTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.db=Store(Path(self.t.name)/'data')
        self.gid='aion-2026'
        self.work=Path(self.t.name)/'aionrepo'
        self.work.mkdir()

    def tearDown(self):
        self.db.conn.close()
        self.t.cleanup()

    def test_config_and_isolation(self):
        c=self.db.direct.configure(self.gid,{'workspace':str(self.work)})
        self.assertEqual(c['workspace'],str(self.work))
        self.assertFalse(self.db.direct.check(self.gid)['claude_cli_detected'] and self.db.direct.check(self.gid)['workspace_valid'] is False)
        with self.assertRaises(ValueError):
            self.db.direct.configure(self.gid,{'workspace':str(self.work/'nicht-da')})
        with self.assertRaises(ValueError):
            self.db.direct.settings('fremdes-spiel')

    def test_import_files_stage_and_task_context(self):
        self.db.direct.configure(self.gid,{'workspace':str(self.work)})
        data=b'Originaler Charakter-Entwurf'
        self.db.save_game_file(io.BytesIO(data),len(data),game_id=self.gid,filename='poseidon.txt',relpath='docs/poseidon.txt')
        brief=self.db.direct.task_prompt(self.gid,'plan',None,'Plane den Tempel','abc123')
        self.assertIn('SESSION_abc123.json',brief)
        manifest=(self.work/'.gameforge/INPUT_MANIFEST.json').read_text(encoding='utf-8')
        self.assertIn('poseidon.txt',manifest)
        context=(self.work/'.gameforge/SESSION_abc123.json').read_text(encoding='utf-8')
        self.assertIn('Plane den Tempel',context)

    def test_archive_extract_no_overwrite_and_zip_slip_rejected(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('Game/Aion.uproject','{}')
            z.writestr('Game/Story.txt','Bestehende Story')
        stream.seek(0)
        saved=self.db.save_upload(stream,len(stream.getvalue()),filename='AION.zip',kind='Vollprojekt',game_id=self.gid)
        result=self.db.direct.extract_archive(self.gid,saved['id'])
        self.assertTrue(result['uproject_found'])
        self.assertEqual((Path(result['workspace'])/'Story.txt').read_text(),'Bestehende Story')
        self.assertEqual(Path(result['workspace']).name,'Game')
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z: z.writestr('../evil.txt','NO')
        stream.seek(0)
        bad=self.db.save_upload(stream,len(stream.getvalue()),filename='bad.zip',kind='Vollprojekt',game_id=self.gid)
        with self.assertRaises(ValueError): self.db.direct.extract_archive(self.gid,bad['id'])
        self.assertFalse((Path(self.t.name)/'evil.txt').exists())

    def test_mock_claude_plan_logs_and_return(self):
        self.db.direct.configure(self.gid,{'workspace':str(self.work)})
        class Result:
            returncode=0
            stdout='ECHTE MOCK-ANTWORT: Plan erstellt'
            stderr=''
        with patch('direct_studio.shutil.which',return_value='/mock/claude'), patch('direct_studio.subprocess.run',return_value=Result()) as mock_run:
            job=self.db.direct.start(self.gid,{'kind':'plan','instruction':'Analyse'})
            for _ in range(200):
                j=self.db.direct.job(self.gid,job['id'])
                if j['status']!='Läuft':break
                time.sleep(.01)
            self.assertEqual(j['status'],'Abgeschlossen')
            self.assertIn('MOCK-ANTWORT',j['log'])
            args=mock_run.call_args[0][0]
            self.assertIn('--permission-mode',args)
            self.assertEqual(args[args.index('--permission-mode')+1],'plan')
        self.assertTrue((self.work/'.gameforge/INPUT_MANIFEST.json').exists())

    def test_archive_real_sources(self):
        self.db.direct.configure(self.gid,{'workspace':str(self.work)})
        (self.work/'AION.uproject').write_text('{}',encoding='utf-8')
        (self.work/'Secret.env').write_text('SENSITIVE=1',encoding='utf-8')
        (self.work/'.env').write_text('token=secret',encoding='utf-8')
        (self.work/'Content').mkdir()
        (self.work/'Content'/'Main.umap').write_bytes(b'map bytes')
        result=self.db.direct.archive_workspace(self.gid)
        self.assertEqual(result['kind'],'Vollprojekt')
        arc=self.db.one('SELECT * FROM archives WHERE id=?',(result['archive_id'],))
        with zipfile.ZipFile(self.db.base/'uploads'/arc['file_path']) as z:
            self.assertIn('AION.uproject',z.namelist())
            self.assertIn('Content/Main.umap',z.namelist())
            self.assertNotIn('.env',z.namelist())

    def test_no_cli_no_job(self):
        self.db.direct.configure(self.gid,{'workspace':str(self.work)})
        with patch('direct_studio.shutil.which',return_value=None):
            with self.assertRaises(ValueError):
                self.db.direct.start(self.gid,{'kind':'implement','instruction':'Baue Inventar'})
        self.assertEqual(self.db.direct.jobs(self.gid),[])

if __name__=='__main__':unittest.main()
