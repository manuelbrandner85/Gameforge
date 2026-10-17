import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from http.client import HTTPConnection
from threading import Thread

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import Store, Server

class GameforgeTests(unittest.TestCase):
    def setUp(self):
        self.tdir = tempfile.TemporaryDirectory()
        self.store=Store(Path(self.tdir.name))
    def tearDown(self):
        self.store.conn.close()
        self.tdir.cleanup()

    def test_seed_games(self):
        names={r['title'] for r in self.store.games()}
        self.assertEqual(names,{'AION 2026','GENESIS'})
        self.assertFalse(self.store.completeness('aion-2026')['full_source_imported'])
        aion=self.store.game('aion-2026')
        self.assertIn('1102',aion['bible']['canon'])
        self.assertIn('v18.0',aion['version'])

    def test_dlc_and_snapshot(self):
        did=self.store.add_dlc('aion-2026',{'title':'Erweiterung der Knoten','compatible_version':'v18.0'})
        self.store.update_dlc('aion-2026',did,{'status':'Konzept','design':{'story':'Neue Missionen','qa':'Regressionstest'}})
        self.assertEqual(self.store.dlcs('aion-2026')[0]['title'],'Erweiterung der Knoten')
        self.assertIn('Neue Missionen',self.store.dlcs('aion-2026')[0]['design']['story'])
        sid=self.store.snapshot('aion-2026','v18.0-test','Vor DLC')
        self.assertTrue(sid)
        self.assertEqual(len(self.store.snapshots('aion-2026')),1)

    def test_references_import_approve_and_claude_package(self):
        gid='aion-2026'
        rid=self.store.add_ref(gid,{'name':'Zeus','category':'boss','view':'face','details':'weißer Bart'})
        self.assertIn('ASSET-ID',self.store.prompt(gid,rid))
        self.assertIn('weißer Bart',self.store.prompt(gid,rid))
        # Valid 1x1 PNG bytes with expected PNG signature
        img=bytes.fromhex('89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000B49444154789C636000020000050001A5F645400000000049454E44AE426082')
        self.store.save_upload(io.BytesIO(img),len(img),filename='zeus.png',kind='Referenzen',game_id=gid,reference_id=rid)
        self.store.set_ref_approved(gid,rid,True)
        r=self.store.one('SELECT * FROM ref_tasks WHERE id=?',(rid,))
        self.assertTrue(r['approved'])
        package,name=self.store.zip_package(gid)
        with zipfile.ZipFile(package) as z:
            files=z.namelist()
            self.assertIn('DATA/GAME.json',files)
            self.assertIn('DATA/REFERENCE_TASKS.json',files)
            self.assertIn('GAME_BIBLE/GAME_BIBLE.md',files)
            self.assertTrue(any(f.startswith('REFERENCES/') for f in files))
            self.assertIn('QUALITY_CONTROL/MODULE_CATALOG.json',files)
        self.assertTrue(name.endswith('.zip'))
        package.close()

    def test_archive_storage_backup_and_embedded_project(self):
        blob=io.BytesIO()
        with zipfile.ZipFile(blob,'w') as z:z.writestr('AION.uproject','test data, not a real game')
        data=blob.getvalue()
        archive=self.store.save_upload(io.BytesIO(data),len(data),filename='AION_Source.zip',kind='Vollprojekt',game_id='aion-2026',version='v18')
        self.assertEqual(archive['size'],len(data))
        self.assertTrue(self.store.completeness('aion-2026')['full_source_imported'])
        pkg,_=self.store.zip_package('aion-2026',include_source=True)
        with zipfile.ZipFile(pkg) as z:
            self.assertTrue(any(x.startswith('PROJECT_SOURCE/') for x in z.namelist()))
        pkg.close()
        backup=self.store.create_backup()
        with zipfile.ZipFile(backup) as z:
            self.assertIn('GAMEFORGE_DATA/gameforge.sqlite3',z.namelist())
            self.assertIn('GAMEFORGE_DATA/uploads/'+self.store.one('SELECT file_path FROM archives')['file_path'],z.namelist())
        backup.close()

    def test_bulk_references_and_safe_restore(self):
        gid='genesis'
        ids=self.store.add_ref_bundle(gid,{'name':'Drachenritter','category':'character','details':'Gleiche Figur in allen Ansichten'})
        self.assertEqual(len(ids),7)
        current=self.store.game(gid)
        sid=self.store.snapshot(gid,'v1','Startplanung')
        self.store.update_game(gid,{'title':'GENESIS NEXT'})
        self.store.restore_snapshot(gid,sid)
        self.assertEqual(self.store.game(gid)['title'],current['title'])
        self.assertEqual(len(self.store.snapshots(gid)),2)

    def test_server_api(self):
        srv=Server(('127.0.0.1',0),self.store)
        thread=Thread(target=srv.serve_forever,daemon=True)
        thread.start()
        try:
            c=HTTPConnection('127.0.0.1',srv.server_address[1],timeout=5)
            c.request('GET','/api/games')
            r=c.getresponse()
            self.assertEqual(r.status,200)
            self.assertEqual(len(json.loads(r.read())),2)
            c.request('GET','/api/games/aion-2026')
            r=c.getresponse(); body=json.loads(r.read())
            self.assertIn('dlcs',body)
            c.request('GET','/api/games/aion-2026/export')
            r=c.getresponse()
            self.assertEqual(r.status,200)
            self.assertTrue(zipfile.is_zipfile(io.BytesIO(r.read())))
        finally:
            srv.shutdown(); srv.server_close()

if __name__=='__main__':unittest.main()
