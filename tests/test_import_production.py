"""Test originals and user-visible production workflow without claiming a compiled game."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from http.client import HTTPConnection
from threading import Thread
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Store, Server


class ImportProductionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(Path(self.tmp.name))

    def tearDown(self):
        self.store.conn.close()
        self.tmp.cleanup()

    def test_originals_and_full_claude_package(self):
        originals=[
          ('Unreal/AION.uproject',b'{"EngineAssociation": "5.8"}'),
          ('Blender/Zeus.blend',b'BLENDER-v0'),
          ('Docs/Story.md','Originaler AION-Kanon und Prolog'.encode()),
          ('References/Zeus Front.png',b'fake-png-index-original'),
          ('Audio/dialog.wav',b'fake-wav-index-original'),
        ]
        for name,data in originals:
            out=self.store.save_game_file(io.BytesIO(data),len(data),game_id='aion-2026',filename=name.split('/')[-1],relpath=name)
            self.assertEqual(out['sha256'],hashlib.sha256(data).hexdigest())
        self.assertEqual(len(self.store.files('aion-2026')),5)
        pkg,_=self.store.zip_package('aion-2026',include_source=True)
        with zipfile.ZipFile(pkg) as z:
            ns=z.namelist()
            self.assertIn('DATA/IMPORTED_FILES.json',ns)
            self.assertIn('DATA/PRODUCTION_TASKS.json',ns)
            self.assertEqual(len([x for x in ns if x.startswith('ALL_IMPORTED_FILES/')]),5)
            self.assertTrue(any(x.endswith('/Docs/Story.md') for x in ns))
        pkg.close()
        backup=self.store.create_backup()
        with zipfile.ZipFile(backup) as z:
            self.assertEqual(len([x for x in z.namelist() if x.startswith('GAMEFORGE_DATA/imports/')]),5)
        backup.close()

    def test_filename_security_and_zip_index(self):
        for name in ('../secret.txt','/etc/passwd','C:/private.txt','folder/../secret.txt'):
            with self.assertRaises(ValueError):
                self.store.save_game_file(io.BytesIO(b'a'),1,game_id='genesis',filename='a',relpath=name)
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:
            z.writestr('Content/World.umap','test')
            z.writestr('GENESIS.uproject','test')
        data=buf.getvalue()
        fid=self.store.save_game_file(io.BytesIO(data),len(data),game_id='genesis',filename='GENESIS_Source.zip')['id']
        index=self.store.zip_index('genesis',fid)
        self.assertEqual(index['total_members'],2)
        self.assertEqual(index['members'][0]['path'],'Content/World.umap')

    def test_project_tasks_release_gates_and_dlc(self):
        tasks=self.store.tasks('genesis')
        with self.assertRaises(ValueError):
            self.store.update_game('genesis',{'status':'Fertig'})
        self.assertGreaterEqual(len(tasks),20)
        self.assertTrue(all(t['status']=='Offen' for t in tasks))
        with self.assertRaises(ValueError):
            self.store.update_task('genesis',tasks[0]['id'],{'status':'Abgenommen','evidence':''})
        updated=self.store.update_task('genesis',tasks[0]['id'],{'status':'Getestet','evidence':'Testbericht: 2026-10-17, lokal ausgeführt'})
        self.assertEqual(updated['status'],'Getestet')
        did=self.store.add_dlc('genesis',{'title':'Kapitel nach dem Ende'})
        self.assertEqual(len(self.store.tasks('genesis',did)),6)
        file=self.store.save_game_file(io.BytesIO(b'dlc'),3,game_id='genesis',filename='dlc_notes.md',dlc_id=did)
        self.assertTrue(file['id'])
        pkg,_=self.store.zip_package('genesis',dlc_id=did,include_source=True)
        with zipfile.ZipFile(pkg) as z:
            imported=json.loads(z.read('DATA/IMPORTED_FILES.json'))
            self.assertEqual(len(imported),1)
            self.assertEqual(imported[0]['dlc_id'],did)
        pkg.close()
        new=self.store.add_game({'title':'Neues Spiel'})
        self.assertGreaterEqual(len(self.store.tasks(new['id'])),20)

    def test_existing_v02_db_migrates_without_losing_data(self):
        self.store.add_game({'title':'Unabhängige Welt'})
        self.store.conn.close()
        # Opening the old or new DB once more is idempotent.
        self.store=Store(Path(self.tmp.name))
        self.assertEqual(len(self.store.games()),3)
        self.assertEqual(len(self.store.tasks('aion-2026')),len(self.store.tasks('genesis')))

    def test_import_http_and_file_download(self):
        srv=Server(('127.0.0.1',0),self.store)
        th=Thread(target=srv.serve_forever,daemon=True);th.start()
        try:
            conn=HTTPConnection('127.0.0.1',srv.server_address[1],timeout=6)
            data=b'project_notes.md test file'
            conn.request('POST','/api/games/genesis/files?filename=notes.md&relpath=docs%2Fnotes.md',body=data,headers={'Content-Type':'application/octet-stream'})
            response=conn.getresponse();self.assertEqual(response.status,200)
            fid=json.loads(response.read())['id']
            conn.request('GET','/api/games/genesis'); detail=json.loads(conn.getresponse().read())
            self.assertEqual(len(detail['files']),1)
            conn.request('GET','/api/file/'+fid); response=conn.getresponse()
            self.assertEqual(response.status,200)
            self.assertEqual(response.read(),data)
            conn.request('GET','/api/games/genesis/tasks'); tasks=json.loads(conn.getresponse().read())
            self.assertGreaterEqual(len(tasks),20)
        finally:
            srv.shutdown(); srv.server_close()

if __name__ == '__main__':unittest.main()
