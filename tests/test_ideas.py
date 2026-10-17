import tempfile,unittest,sys,zipfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import Store

class IdeasTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.s=Store(Path(self.tmp.name))
 def tearDown(self):
  self.s.conn.close();self.tmp.cleanup()
 def test_initial_and_offline_ideas(self):
  feed=self.s.idea_feed('aion-2026')
  self.assertEqual(len(feed['messages']),0)
  feed=self.s.brainstorm('aion-2026',{'message':'Poseidon hat einen Tempel mit bosskampf','provider':'offline'})
  self.assertEqual(len(feed['messages']),2)
  self.assertEqual(len(feed['suggestions']),3)
  self.assertEqual(feed['suggestions'][0]['status'],'Vorgeschlagen')
 def test_approval_and_export(self):
  self.s.brainstorm('aion-2026',{'message':'Neue Geschichte und Prolog'})
  idea=self.s.idea_feed('aion-2026')['suggestions'][0]
  self.s.decide_idea('aion-2026',idea['id'],'accept')
  out,_=self.s.zip_package('aion-2026')
  with zipfile.ZipFile(out) as z:
   accepted=json.loads(z.read('CREATIVE_DIRECTOR/ACCEPTED_IDEAS.json'))
   self.assertEqual(len(accepted),1)
   self.assertEqual(accepted[0]['id'],idea['id'])
  out.close()
  before=self.s.game('aion-2026')['bible']['story']
  self.s.decide_idea('aion-2026',idea['id'],'integrate')
  self.assertIn(idea['title'],self.s.game('aion-2026')['bible']['story'])
  self.assertIn(before,self.s.game('aion-2026')['bible']['story'])
  self.assertEqual(len(self.s.snapshots('aion-2026')),1)
 def test_dlc_separation(self):
  did=self.s.add_dlc('aion-2026',{'title':'Meer'})
  f=self.s.brainstorm('aion-2026',{'dlc_id':did,'message':'Neue Unterwasserstadt'})
  self.assertEqual(len(self.s.idea_feed('aion-2026')['messages']),0)
  idea=f['suggestions'][0]
  self.s.decide_idea('aion-2026',idea['id'],'accept')
  self.s.decide_idea('aion-2026',idea['id'],'integrate')
  self.assertTrue(any(idea['title'] in v for v in self.s.dlcs('aion-2026')[0]['design'].values()))
  out,_=self.s.zip_package('aion-2026',dlc_id=did)
  with zipfile.ZipFile(out) as z:
   self.assertEqual(len(json.loads(z.read('CREATIVE_DIRECTOR/ACCEPTED_IDEAS.json'))),1)
  out.close()
 def test_reject_and_backup(self):
  self.s.brainstorm('genesis',{'message':'Genre Mechanik'})
  idea=self.s.idea_feed('genesis')['suggestions'][0]
  self.s.decide_idea('genesis',idea['id'],'reject')
  with self.assertRaises(ValueError):self.s.decide_idea('genesis',idea['id'],'integrate')
  out,_=self.s.zip_package('genesis')
  with zipfile.ZipFile(out) as z:
   self.assertEqual(json.loads(z.read('CREATIVE_DIRECTOR/ACCEPTED_IDEAS.json')),[])
  out.close()
  backup=self.s.create_backup()
  with zipfile.ZipFile(backup) as z:self.assertIn('GAMEFORGE_DATA/gameforge.sqlite3',z.namelist())
  backup.close()

if __name__=='__main__':unittest.main()
