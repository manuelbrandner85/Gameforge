import json, sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Store, RESOURCE

class RoadmapTests(unittest.TestCase):
    def test_accepted_and_rejected_decisions(self):
        data=json.loads((RESOURCE/'ROADMAP_APPROVED_1_40.json').read_text(encoding='utf-8'))
        expected=list(range(1,21))+list(range(24,37))+[38,40]
        self.assertEqual([f['id'] for f in data['features']],expected)
        self.assertEqual([f['id'] for f in data['rejected']],[21,22,23,37,39])
        self.assertTrue(all(f['approved'] and f['implementation_status']=='geplant' for f in data['features']))
        self.assertTrue(all(f['scope'] and f['acceptance_criteria'] for f in data['features']))
        self.assertEqual(data['decision_summary']['approved_count'],35)
        self.assertEqual(data['decision_summary']['rejected_count'],5)
        allowed=set(expected)
        self.assertTrue(all(set(f['depends_on']).issubset(allowed) for f in data['features']))
    def test_claude_package_contains_current_plan_not_old(self):
        with tempfile.TemporaryDirectory() as td:
            st=Store(Path(td))
            try:
                out,_=st.zip_package('aion-2026')
                with zipfile.ZipFile(out) as z:
                    names=z.namelist()
                    self.assertIn('GAMEFORGE_ROADMAP/ROADMAP_APPROVED_1_40.json',names)
                    self.assertIn('GAMEFORGE_ROADMAP/ENTWICKLUNGSPLAN_1_40.md',names)
                    self.assertNotIn('GAMEFORGE_ROADMAP/ROADMAP_APPROVED_1_20.json',names)
                    data=json.loads(z.read('GAMEFORGE_ROADMAP/ROADMAP_APPROVED_1_40.json'))
                    self.assertEqual(len(data['features']),35)
                    self.assertEqual(len(data['rejected']),5)
                out.close()
            finally: st.conn.close()

if __name__=='__main__': unittest.main()
