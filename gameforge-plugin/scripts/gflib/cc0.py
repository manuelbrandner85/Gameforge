"""CC0-Asset-Quellen: Poly Haven und ambientCG (beide Creative Commons CC0 – keine Einschränkung, auch kommerziell und mit KI).

Lädt über die offiziellen, freien Schnittstellen in die GAMEFORGE-Asset-Bibliothek und macht jedes Asset in Blender
als Asset nutzbar (Asset-Browser, Bibliothek „GAMEFORGE CC0“). Nur Python-Standardbibliothek.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, urllib.parse, urllib.request, zipfile
from pathlib import Path

UA = {'User-Agent': 'GAMEFORGE-local/3.6 (+lokale Spiel- und Filmproduktion)'}
PH_API = 'https://api.polyhaven.com'
ACG_API = 'https://ambientcg.com/api/v2/full_json'
PH_TYPES = {'textur': 'textures', 'modell': 'models', 'hdri': 'hdris'}


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _json(url):
    return json.loads(_get(url).decode('utf-8'))


def _download(url, target: Path, md5=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and (not md5 or hashlib.md5(target.read_bytes()).hexdigest() == md5):
        return target
    tmp = target.with_suffix(target.suffix + '.part')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r, open(tmp, 'wb') as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    if md5 and hashlib.md5(tmp.read_bytes()).hexdigest() != md5:
        tmp.unlink()
        raise IOError(f'Prüfsumme falsch: {url}')
    os.replace(tmp, target)
    return target


# ------------------------------------------------------------------ Poly Haven
def ph_search(query, typ='textur', limit=10):
    assets = _json(f'{PH_API}/assets?t={PH_TYPES[typ]}')
    q = query.lower().split()
    hits = []
    for aid, a in assets.items():
        text = ' '.join([aid, a.get('name', ''), ' '.join(a.get('tags', [])), ' '.join(a.get('categories', []))]).lower()
        if all(w in text for w in q):
            hits.append({'id': aid, 'name': a.get('name'), 'quelle': 'polyhaven', 'typ': typ, 'downloads': a.get('download_count', 0),
                         'lizenz': 'CC0', 'url': f'https://polyhaven.com/a/{aid}'})
    return sorted(hits, key=lambda h: -h['downloads'])[:limit]


def ph_fetch(aid, typ, res, root: Path):
    """Lädt .blend (Textur/Modell) bzw. .exr (HDRI) samt aller Texturen. Rückgabe: Hauptdatei, Bytes."""
    files = _json(f'{PH_API}/files/{aid}')
    dest = root / 'polyhaven' / aid
    if typ == 'hdri':
        f = files['hdri'][res]['exr']
        main = _download(f['url'], dest / Path(urllib.parse.urlparse(f['url']).path).name, f.get('md5'))
        return main, f['size']
    b = files['blend'][res]['blend']
    main = _download(b['url'], dest / Path(urllib.parse.urlparse(b['url']).path).name, b.get('md5'))
    size = b['size']
    for rel, inc in (b.get('include') or {}).items():
        _download(inc['url'], dest / rel, inc.get('md5'))
        size += inc['size']
    return main, size


# ------------------------------------------------------------------ ambientCG
def acg_search(query, limit=10):
    q = urllib.parse.quote(query)
    d = _json(f'{ACG_API}?q={q}&type=Material&include=downloadData,tagData&limit={limit}&sort=Popular')
    return [{'id': a['assetId'], 'name': a.get('displayName') or a['assetId'], 'quelle': 'ambientcg', 'typ': 'textur',
             'downloads': a.get('downloadCount', 0), 'lizenz': 'CC0', 'url': f"https://ambientcg.com/a/{a['assetId']}"}
            for a in d.get('foundAssets', [])]


def acg_fetch(aid, res, root: Path):
    d = _json(f'{ACG_API}?id={aid}&include=downloadData')
    a = d['foundAssets'][0]
    dl = a['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads']
    want = f'{res.upper()}-JPG'
    item = next((x for x in dl if x['attribute'] == want), None)
    if not item:
        raise ValueError(f'{aid}: Auflösung {want} nicht verfügbar ({", ".join(x["attribute"] for x in dl)})')
    dest = root / 'ambientcg' / aid
    z = _download(item['downloadLink'], dest / f'{aid}_{want}.zip')
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if '..' in n or n.startswith(('/', '\\')):
                raise ValueError('unerwarteter Inhalt im ZIP')
        zf.extractall(dest)
    z.unlink()
    return dest, item['size']


# ------------------------------------------------------------------ Blender: als Asset markieren
MARK_SCRIPT = r'''
import bpy, sys, os, glob
args = sys.argv[sys.argv.index("--") + 1:]
mode, src, out, name = args[0], args[1], args[2], args[3]
if mode == "acg":
    bpy.ops.wm.read_homefile(use_empty=True)
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; o = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    def tex(suffix, noncolor=True):
        f = (glob.glob(os.path.join(src, f"*_{suffix}.jpg")) + glob.glob(os.path.join(src, f"*_{suffix}.png")))
        if not f: return None
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(f[0])
        if noncolor: n.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    c = tex("Color", False)
    if c: nt.links.new(c.outputs["Color"], b.inputs["Base Color"])
    r = tex("Roughness")
    if r: nt.links.new(r.outputs["Color"], b.inputs["Roughness"])
    mt = tex("Metalness")
    if mt: nt.links.new(mt.outputs["Color"], b.inputs["Metallic"])
    nm = tex("NormalGL")
    if nm:
        nmap = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(nm.outputs["Color"], nmap.inputs["Color"]); nt.links.new(nmap.outputs["Normal"], b.inputs["Normal"])
    dp = tex("Displacement")
    if dp:
        dn = nt.nodes.new("ShaderNodeDisplacement"); dn.inputs["Scale"].default_value = 0.02
        nt.links.new(dp.outputs["Color"], dn.inputs["Height"]); nt.links.new(dn.outputs["Displacement"], o.inputs["Displacement"])
    m.asset_mark(); m.asset_data.tags.new("ambientCG"); m.asset_data.tags.new("CC0"); m.asset_data.description = "ambientCG CC0 – " + name
    bpy.ops.wm.save_as_mainfile(filepath=out, relative_remap=True)
else:
    bpy.ops.wm.open_mainfile(filepath=src)
    marked = 0
    for coll in (bpy.data.materials, bpy.data.objects, bpy.data.worlds):
        for idb in coll:
            if idb.library or idb.name in ("Dots Stroke",): continue
            if coll is bpy.data.objects and idb.type not in {"MESH", "CURVE"}: continue
            if not idb.asset_data:
                idb.asset_mark(); marked += 1
            idb.asset_data.tags.new("PolyHaven"); idb.asset_data.tags.new("CC0")
            try: idb.asset_generate_preview()
            except Exception: pass
    bpy.ops.wm.save_mainfile()
    print("GF_MARKED", marked)
'''


def blender_exe():
    base = Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Blender Foundation'
    hits = sorted(base.glob('Blender*/blender.exe'))
    return hits[-1] if hits else None


def mark_assets(mode, src: Path, out: Path, name, tmpdir: Path):
    exe = blender_exe()
    if not exe:
        raise FileNotFoundError('Blender nicht gefunden')
    script = tmpdir / 'gf_mark_assets.py'
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(MARK_SCRIPT, encoding='utf-8')
    r = subprocess.run([str(exe), '-b', '--factory-startup', '--python', str(script), '--', mode, str(src), str(out), name],
                       capture_output=True, text=True, errors='replace', timeout=600, stdin=subprocess.DEVNULL)
    if r.returncode != 0 or (mode == 'ph' and 'GF_MARKED' not in r.stdout) or (mode == 'acg' and not out.is_file()):
        raise RuntimeError('Asset-Markierung fehlgeschlagen: ' + (r.stdout + r.stderr)[-600:])
    return out
