"""GAMEFORGE Natron smoke test (masterprompt H: "Testkomposition aus zwei Bildsequenzen, Headless-Ausgabe, Farbraumcheck").

1. FFmpeg makes two 5-frame PNG sequences: a mid-grey plate (128,128,128) and an overlay with a 50 % transparent
   pure red square.
2. NatronRenderer (headless, Python) reads both, merges overlay over plate, writes 5 PNG frames.
3. Check: frame count, and the centre pixel against the expected "over" result in sRGB. Natron works linear
   internally; a missing/incorrect colour-space conversion shows up as a clearly different value.
   Usage:  python gameforge_core/natron_smoke.py <outdir>
"""
import json
import subprocess
import sys
from pathlib import Path

NATRON = Path.home() / "AppData/Local/Programs/Natron/bin/NatronRenderer.exe"   # WinGet installs Natron per user
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
plate, over, res = out / "plate_###.png", out / "over_###.png", out / "comp_###.png"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x808080:s=320x180:r=24:d=0.25",
                "-frames:v", "6", "-start_number", "0", str(out / "plate_%03d.png")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red@0.5:s=320x180:r=24:d=0.25,format=rgba",
                "-frames:v", "6", "-start_number", "0", str(out / "over_%03d.png")], check=True)
script = out / "natron_comp.py"
script.write_text(f'''
a = app1
p = a.createNode("fr.inria.openfx.ReadOIIO"); p.getParam("filename").setValue(r"{plate}")
o = a.createNode("fr.inria.openfx.ReadOIIO"); o.getParam("filename").setValue(r"{over}")
fp = o.getParam("filePremult")   # PNG alpha is straight (unassociated): read as unpremultiplied, else edges go too bright
fp.setValue(2) if fp is not None else None
m = a.createNode("net.sf.openfx.MergePlugin")
m.connectInput(0, p)      # B
m.connectInput(1, o)      # A (over)
w = a.createNode("fr.inria.openfx.WriteOIIO"); w.getParam("filename").setValue(r"{res}")
w.connectInput(0, m)
a.render(w, 1, 5)
''', encoding="utf8")
r = subprocess.run([str(NATRON), "-t", str(script)], capture_output=True, text=True, timeout=600,
                   stdin=subprocess.DEVNULL)   # -t is interpreter mode: it waits for more input unless stdin is closed
(out / "natron.stdout.log").write_text(r.stdout, encoding="utf8")
(out / "natron.stderr.log").write_text(r.stderr, encoding="utf8")
frames = sorted(out.glob("comp_*.png"))
px = None
if frames:
    h = int(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=height", "-of", "csv=p=0", str(frames[0])],
                           capture_output=True, text=True).stdout.strip() or 180)
    # Natron keeps the 320x180 inputs at the bottom-left of its project format: centre of the input = (160, h-90)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(frames[0]), "-vf", f"crop=1:1:160:{h - 90}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    px = list(raw[:3]) if len(raw) >= 3 else None


def srgb_to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return round(max(0.0, min(1.0, c)) * 255)


# "over" in linear light, premultiplied red 0.5 over grey 128
g = srgb_to_lin(128)
expected = [lin_to_srgb(1.0 * 0.5 + g * 0.5), lin_to_srgb(g * 0.5), lin_to_srgb(g * 0.5)]
ok = len(frames) == 5 and px is not None and all(abs(a - b) <= 6 for a, b in zip(px, expected))
res_json = {"natron_exit": r.returncode, "note_exit": "0xC0000005 beim Beenden nach EOF auf stdin (nach dem Rendern)" if r.returncode == 3221225477 else None, "frames": len(frames), "centre_pixel_srgb": px, "expected_linear_over_srgb": expected,
            "ok": ok}
(out / "natron_validation.json").write_text(json.dumps(res_json, indent=1), encoding="utf8")
print("NATRON_SMOKE", json.dumps(res_json))
