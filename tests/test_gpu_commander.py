"""Abnahmetests Smart GPU Commander (Verb. 11) und Job-Kern (Verb. 04/10/13). Ohne echte GPU-Last: Messwerte werden injiziert."""
import importlib, json, os, struct, sys, tempfile, threading, time, unittest, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PY = sys.executable
PLENTY = {"vendor": "NVIDIA", "name": "Test-GPU", "vram_total_mb": 12000, "vram_used_mb": 1000, "vram_free_mb": 11000,
          "util_pct": 5, "temp_c": 40, "driver": "test", "source": "test", "measured": True}


def png(path, w, h):
    raw = b"".join(b"\x00" + bytes([x % 256, y % 256, 90]) * 1 for y in range(h) for x in [0]) if False else b"".join(b"\x00" + bytes(3 * w) for _ in range(h))
    def ch(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b""))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = Path(self.tmp.name)
        self.proj = self.t / "Projekt A"; self.proj.mkdir()
        self.other = self.t / "Projekt B"; self.other.mkdir()
        os.environ["GAMEFORGE_DATA_DIR"] = str(self.t / "data")
        os.environ["GAMEFORGE_GPU_FAKE"] = json.dumps(PLENTY)
        os.environ["GAMEFORGE_GPU_FAKE_APPS"] = "[]"
        import gameforge_core.gpu_commander as g, gameforge_core.jobs as j
        self.g = importlib.reload(g); self.j = importlib.reload(j)

    def tearDown(self):
        self.j.close_all()
        for k in ("GAMEFORGE_DATA_DIR", "GAMEFORGE_GPU_FAKE", "GAMEFORGE_GPU_FAKE_APPS", "GAMEFORGE_GPU_SIMULATE_UNKNOWN"):
            os.environ.pop(k, None)
        self.tmp.cleanup()

    def script(self, name, code):
        p = self.proj / name; p.write_text(code, encoding="utf-8"); return str(p)


class GpuTests(Base):
    def test_AT_11_01_two_heavy_jobs_never_overlap(self):
        log = self.proj / "times.txt"
        s = self.script("heavy.py", f"import time,sys\nopen(r'{log}','a').write(f'start {{time.time()}}\\n')\ntime.sleep(1.5)\nopen(r'{log}','a').write(f'end {{time.time()}}\\n')\nopen(sys.argv[1],'w').write('x')\n")
        for i in range(2):
            self.j.submit("A", self.proj, "blender_render", f"heavy{i}", [PY, s, str(self.proj / f"out{i}.txt")], self.proj, [f"out{i}.txt"], gpu_class="heavy", need_mb=100)
        ts = [threading.Thread(target=self.j.run_one, args=(f"w{i}",)) for i in range(2)]
        [t.start() for t in ts]; [t.join(60) for t in ts]
        ev = [l.split() for l in log.read_text().splitlines()]
        self.assertEqual([e[0] for e in ev], ["start", "end", "start", "end"], "Zweiter Heavy-Job darf erst nach Ende des ersten starten")

    def test_AT_11_02_unknown_vram_is_conservative(self):
        os.environ["GAMEFORGE_GPU_SIMULATE_UNKNOWN"] = "1"; os.environ.pop("GAMEFORGE_GPU_FAKE")
        ok, why, _ = self.g.preflight("heavy", 3000, apps=[])
        self.assertTrue(ok); self.assertIn("unknown", why)
        ok, why, _ = self.g.preflight("heavy", 3000, apps=[{"pid": 1, "app": "Unreal Editor", "mode": "Fenster (Editor)", "ram_mb": 1}])
        self.assertFalse(ok); self.assertIn("unknown", why); self.assertIn("Unreal Editor", why)
        self.assertNotIn("% frei", self.g.status_text())

    def test_low_vram_waits_and_names_holder_never_kills(self):
        m = dict(PLENTY, vram_used_mb=11000, vram_free_mb=1000)
        ok, why, det = self.g.preflight("heavy", 2000, m=m, apps=[{"pid": 4242, "app": "Unreal Editor", "mode": "Fenster (Editor)", "ram_mb": 3000}])
        self.assertFalse(ok); self.assertIn("Unreal Editor", why); self.assertIn("schließt nichts", why)
        self.assertTrue(self.g.preflight("light", 99999, m=m, apps=[])[0], "Leichte Jobs brauchen kein GPU-Token")

    def test_AT_11_03_preview_cannot_change_final(self):
        c = self.proj / "master_quality.json"
        c.write_text(json.dumps({"profile": "final", "master_resolution": {"width": 64, "height": 32}, "fps": 24}), encoding="utf-8")
        sha = self.g.lock_contract(c)
        with self.assertRaises(ValueError):
            self.g.make_preview(c, c, master_resolution={"width": 8, "height": 4})
        pv = self.g.make_preview(c, self.proj / "preview.json", master_resolution={"width": 8, "height": 4})
        self.assertEqual(self.g.sha256_file(c), sha); self.assertEqual(json.loads(pv.read_text())["profile"], "preview")
        self.assertTrue(self.g.verify_contract(c)[0])
        c.write_text(c.read_text().replace('"width": 64', '"width": 32'), encoding="utf-8")   # heimliche Reduktion
        ok, why = self.g.verify_contract(c); self.assertFalse(ok); self.assertIn("verändert", why)
        with self.assertRaises(ValueError):
            self.j.submit("A", self.proj, "unreal_mrq", "final", [PY, "-c", "pass"], self.proj, ["x.png"], gpu_class="heavy", profile="final", contract=c)

    def test_AT_11_04_final_output_must_match_contract(self):
        c = self.proj / "master_quality.json"
        c.write_text(json.dumps({"profile": "final", "master_resolution": {"width": 64, "height": 32}, "fps": 24}), encoding="utf-8")
        self.g.lock_contract(c)
        maker = self.script("mk.py", "import sys,struct,zlib\nfrom pathlib import Path\nw,h=int(sys.argv[2]),int(sys.argv[3])\nraw=b''.join(b'\\x00'+bytes(3*w) for _ in range(h))\nch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)\nPath(sys.argv[1]).write_bytes(b'\\x89PNG\\r\\n\\x1a\\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))\n")
        good, _ = self.j.submit("A", self.proj, "unreal_mrq", "ok", [PY, maker, str(self.proj / "f1.png"), "64", "32"], self.proj, ["f1.png"], gpu_class="heavy", need_mb=10, profile="final", contract=c)
        bad, _ = self.j.submit("A", self.proj, "unreal_mrq", "zu klein", [PY, maker, str(self.proj / "f2.png"), "32", "16"], self.proj, ["f2.png"], gpu_class="heavy", need_mb=10, profile="final", contract=c)
        self.j.work()
        self.assertEqual(self.j.get(good["id"])["status"], "needs_review", "Final wartet auf Sichtabnahme, nicht 'passed'")
        b = self.j.get(bad["id"]); self.assertEqual(b["status"], "failed"); self.assertIn("32×16 statt 64×32", b["reason"])

    def test_oom_is_blocked_not_downgraded(self):
        s = self.script("oom.py", "import sys\nsys.stderr.write('RuntimeError: CUDA error: out of memory\\n')\nsys.exit(1)\n")
        job, _ = self.j.submit("A", self.proj, "comfy_flux", "oom", [PY, s], self.proj, ["nie.png"], gpu_class="heavy", need_mb=10, max_attempts=3)
        self.j.work()
        r = self.j.get(job["id"])
        self.assertEqual((r["status"], r["error_class"], r["attempts"]), ("blocked", "RESOURCE_BLOCKED", 1), "OOM: kein automatischer Neuversuch")
        self.assertIn("NICHT automatisch reduziert", r["reason"])
        self.assertTrue((self.j.LOGS / job["id"] / "validation.json").is_file())

    def test_stale_lock_is_taken_over(self):
        self.g.LOCKS.mkdir(parents=True, exist_ok=True)
        (self.g.LOCKS / "gpu.lock").write_text(json.dumps({"pid": 999999, "job": "tot", "since": 0}))
        self.assertTrue(self.g.try_acquire("neu")); self.assertEqual(self.g.lock_holder()["job"], "neu")
        self.g.release()
        self.assertTrue((self.g.LOCKS / "verwaiste_sperren.log").is_file())


class JobTests(Base):
    def test_AT_04_01_missing_tool_is_blocked(self):
        job, _ = self.j.submit("A", self.proj, "blender_render", "ohne blender", [str(self.proj / "gibt_es_nicht.exe")], self.proj, ["o.blend"], gpu_class="heavy", need_mb=10)
        self.j.work()
        r = self.j.get(job["id"]); self.assertEqual((r["status"], r["error_class"]), ("blocked", "UNAVAILABLE"))

    def test_AT_04_02_03_no_duplicates_no_overwrite(self):
        s = self.script("w.py", "import sys,time\nopen(sys.argv[1],'w').write(str(time.time()))\n")
        a, new1 = self.j.submit("A", self.proj, "export", "exp", [PY, s, str(self.proj / "e.txt")], self.proj, ["e.txt"], idem_key="A:exp:1")
        b, new2 = self.j.submit("A", self.proj, "export", "exp", [PY, s, str(self.proj / "e.txt")], self.proj, ["e.txt"], idem_key="A:exp:1")
        self.assertTrue(new1); self.assertFalse(new2); self.assertEqual(a["id"], b["id"])
        self.j.work(); first = (self.proj / "e.txt").read_text()
        con = self.j.connect(); con.execute("UPDATE jobs SET status='queued' WHERE id=?", (a["id"],))   # z. B. nach Absturz erneut eingereiht
        self.j.work()
        self.assertEqual((self.proj / "e.txt").read_text(), first, "Vorhandenes geprüftes Artefakt wurde nicht überschrieben")
        self.assertIn("nicht erneut erzeugt", self.j.get(a["id"])["reason"])

    def test_AT_04_04_foreign_project_rejected(self):
        with self.assertRaises(ValueError) as e:
            self.j.submit("A", self.proj, "export", "x", [PY, "-c", "pass"], self.proj, [str(self.other / "fremd.txt")])
        self.assertIn("getrennt", str(e.exception))

    def test_AT_10_01_missing_artifact_fails(self):
        job, _ = self.j.submit("A", self.proj, "export", "lügt", [PY, "-c", "print('fertig!')"], self.proj, ["soll_da_sein.fbx"])
        self.j.work()
        r = self.j.get(job["id"]); self.assertEqual((r["status"], r["error_class"]), ("failed", "QA_FAILED"))

    def test_AT_10_03_resume_after_crash(self):
        s = self.script("ok.py", "import sys\nopen(sys.argv[1],'w').write('x')\n")
        job, _ = self.j.submit("A", self.proj, "export", "nach Absturz", [PY, s, str(self.proj / "r.txt")], self.proj, ["r.txt"])
        con = self.j.connect(); con.execute("UPDATE jobs SET status='running', pid=999999 WHERE id=?", (job["id"],))
        self.assertEqual(self.j.recover(), 1)
        self.j.work(); self.assertEqual(self.j.get(job["id"])["status"], "passed")

    def test_dependencies_and_retry_budget(self):
        fail = self.script("f.py", "import sys\nsys.exit(3)\n")
        a, _ = self.j.submit("A", self.proj, "blender", "kaputt", [PY, fail], self.proj, ["a.fbx"], max_attempts=1)
        b, _ = self.j.submit("A", self.proj, "unreal", "abhängig", [PY, "-c", "pass"], self.proj, ["b.uasset"], depends=[a["id"]])
        self.j.work()
        self.assertEqual(self.j.get(a["id"])["status"], "failed")
        self.assertEqual(self.j.get(b["id"])["status"], "blocked", "Abhängiger Job startet nicht nach Fehlschlag")


if __name__ == "__main__":
    unittest.main()
