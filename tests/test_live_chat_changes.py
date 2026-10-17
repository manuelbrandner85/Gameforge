import json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch,MagicMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import Store

class LiveChatChanges(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.s=Store(Path(self.tmp.name))
 def tearDown(self):
  self.s.conn.close();self.tmp.cleanup()
 def test_apply_manual_change_and_snapshot(self):
  g=self.s.game('aion-2026');before=g['bible']['world']
  cid=self.s.propose_change('aion-2026',section='world',summary='Meeresstadt ergänzen',mode='append',new_text='Unterwasserstadt mit 3 Prüfungen.')
  self.assertEqual(before,self.s.game('aion-2026')['bible']['world'])
  self.assertEqual(self.s.change_decision('aion-2026',cid,'apply')['status'],'Übernommen')
  self.assertIn('Unterwasserstadt',self.s.game('aion-2026')['bible']['world'])
  self.assertEqual(len(self.s.snapshots('aion-2026')),1)
  with self.assertRaises(ValueError):self.s.change_decision('aion-2026',cid,'apply')
  out,_=self.s.zip_package('aion-2026')
  with zipfile.ZipFile(out) as z:
   data=json.loads(z.read('CREATIVE_DIRECTOR/APPLIED_CHANGES.json'))
   self.assertEqual(data[0]['id'],cid)
  out.close()
 def test_exact_replace_and_stale_protection(self):
  orig=self.s.game('aion-2026')['bible']['story']
  part='Ein Auserwählter'
  self.assertIn(part,orig)
  cid=self.s.propose_change('aion-2026',section='story',summary='Protagonist umbenannt',mode='replace_text',old_text=part,new_text='Eine Auserwählte')
  self.s.change_decision('aion-2026',cid,'apply')
  new=self.s.game('aion-2026')['bible']['story']
  self.assertIn('Eine Auserwählte',new);self.assertNotIn(part,new)
  other=self.s.propose_change('aion-2026',section='world',summary='Neue Insel',mode='append',new_text='Verborgene Insel')
  bible=self.s.game('aion-2026')['bible'];bible['world']+=' Inzwischen anderer Text.'
  self.s.update_game('aion-2026',{'bible':bible})
  with self.assertRaisesRegex(ValueError,'inzwischen verändert'):self.s.change_decision('aion-2026',other,'apply')
 def test_dlc_scope_and_rejection(self):
  did=self.s.add_dlc('aion-2026',{'title':'Ozean-DLC'})
  cid=self.s.propose_change('aion-2026',dlc_id=did,section='quests',summary='DLC-Mission',mode='append',new_text='Geheimnis des Riffs.')
  self.assertEqual(self.s.idea_feed('aion-2026')['changes'],[])
  self.assertEqual(len(self.s.idea_feed('aion-2026',did)['changes']),1)
  self.s.change_decision('aion-2026',cid,'apply')
  self.assertIn('Riffs',self.s.dlcs('aion-2026')[0]['design']['quests'])
  self.assertNotIn('Riffs',str(self.s.game('aion-2026')['bible']))
  reject=self.s.propose_change('aion-2026',dlc_id=did,section='story',summary='Nein',mode='append',new_text='Abgelehnter Inhalt')
  self.s.change_decision('aion-2026',reject,'reject')
  self.assertNotIn('Abgelehnter Inhalt',str(self.s.dlcs('aion-2026')[0]['design']))
 def test_real_claude_mock_conversation_and_feedback(self):
  def run(args, **kwargs):
   payload=json.loads(kwargs['input'])
   self.assertTrue(payload['latest_user_message'])
   self.assertEqual(args[0],'claude')
   self.assertEqual(args[args.index('--permission-mode')+1],'plan')
   return MagicMock(returncode=0,stdout=json.dumps({'reply':'Ich habe verstanden: Wir ändern den Prolog; Auswirkungen auf Intro und Kamera beachten.','suggestions':[],
      'changes':[{'summary':'Prolog ergänzen','section':'prologue','mode':'append','new_text':'Neue Einstiegsszene mit Tempel.'}]},ensure_ascii=False),stderr='')
  with patch('app.shutil.which',return_value='/usr/bin/claude'),patch('app.subprocess.run',side_effect=run):
   feed=self.s.brainstorm('aion-2026',{'message':'Ändere den Prolog','provider':'claude'})
   self.assertEqual(feed['messages'][-1]['provider'],'claude')
   self.assertIn('verstanden',feed['messages'][-1]['body'])
   self.assertEqual(len(feed['changes']),1)
   self.assertNotIn('Neue Einstiegsszene',self.s.game('aion-2026')['bible']['prologue'])
   cid=feed['changes'][0]['id'];self.s.change_decision('aion-2026',cid,'apply')
   self.assertIn('Neue Einstiegsszene',self.s.game('aion-2026')['bible']['prologue'])
 def test_cli_failure_does_not_write_changes(self):
  with patch('app.shutil.which',return_value=None):
   with self.assertRaisesRegex(ValueError,'nicht installiert'):
    self.s.brainstorm('aion-2026',{'message':'Ändere die Kamera','provider':'claude'})
  feed=self.s.idea_feed('aion-2026')
  self.assertEqual(len(feed['messages']),1)
  self.assertEqual(len(feed['changes']),0)
  self.assertIn('Kamera',feed['messages'][0]['body'])

if __name__=='__main__':unittest.main()
