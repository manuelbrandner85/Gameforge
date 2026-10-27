"""Freie Asset-Quellen für Spiele und Filme – ein Register, eine Suche.

Nur Quellen, deren Inhalte kostenlos UND für eigene (auch kommerzielle) Spiele/Filme nutzbar sind.
Jede Quelle hat eine Lizenzangabe; CC-BY verlangt Namensnennung – GAMEFORGE schreibt sie in CREDITS.
Zugang: auto = suchen und laden ohne Konto; suche = suchen ohne Konto, Laden braucht Konto/Schlüssel;
browser = nur über den Browser (Fab, Cloudflare-geschützt); manuell = geprüfter Link, keine Schnittstelle.
Nur Python-Standardbibliothek.
"""
from __future__ import annotations
import html, json, os, re, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path

UA = {'User-Agent': 'Mozilla/5.0 GAMEFORGE-local/3.7 (lokale Spiel- und Filmproduktion)'}

QUELLEN = {
    'polyhaven':   {'name': 'Poly Haven', 'inhalt': 'HDRIs, PBR-Texturen, gescannte Modelle', 'lizenz': 'CC0', 'zugang': 'auto', 'url': 'https://polyhaven.com', 'fuer': 'Spiel, Film'},
    'ambientcg':   {'name': 'ambientCG', 'inhalt': 'PBR-Materialien, HDRIs', 'lizenz': 'CC0', 'zugang': 'auto', 'url': 'https://ambientcg.com', 'fuer': 'Spiel, Film'},
    'kenney':      {'name': 'Kenney', 'inhalt': 'Spiel-Pakete (3D, 2D, UI, Sound) – stilisiert', 'lizenz': 'CC0', 'zugang': 'auto', 'url': 'https://kenney.nl/assets', 'fuer': 'Spiel'},
    'opengameart': {'name': 'OpenGameArt (nur CC0-Filter)', 'inhalt': '3D, 2D, Musik, Sounds', 'lizenz': 'CC0 (gefiltert)', 'zugang': 'auto', 'url': 'https://opengameart.org', 'fuer': 'Spiel'},
    'sketchfab':   {'name': 'Sketchfab (CC0/CC-BY, herunterladbar)', 'inhalt': 'Scans, Modelle, Museumsobjekte', 'lizenz': 'CC0 oder CC-BY (Namensnennung)', 'zugang': 'suche', 'url': 'https://sketchfab.com', 'fuer': 'Spiel, Film', 'schluessel': 'SKETCHFAB_TOKEN (kostenloses Konto)'},
    'freesound':   {'name': 'Freesound (CC0-Filter)', 'inhalt': 'Geräusche, Atmo, Foley', 'lizenz': 'CC0 (gefiltert)', 'zugang': 'suche', 'url': 'https://freesound.org', 'fuer': 'Spiel, Film', 'schluessel': 'FREESOUND_KEY (kostenloses Konto)'},
    'fab':         {'name': 'Fab (Epic)', 'inhalt': 'Megaplants, Epic-Beispielprojekte, freie VFX/Assets', 'lizenz': 'Fab-Standard (meist NoAI) – nur Einträge ohne Lizenzauswahl sind für Unreal gratis', 'zugang': 'browser', 'url': 'https://www.fab.com/search?is_free=1', 'fuer': 'Spiel, Film'},
    'quaternius':  {'name': 'Quaternius', 'inhalt': 'Low-Poly-Pakete, Figuren mit Animation', 'lizenz': 'CC0', 'zugang': 'manuell', 'url': 'https://quaternius.com', 'fuer': 'Spiel'},
    'sharetextures': {'name': 'ShareTextures', 'inhalt': 'PBR-Texturen, Modelle', 'lizenz': 'CC0', 'zugang': 'manuell', 'url': 'https://www.sharetextures.com', 'fuer': 'Spiel, Film'},
    'cgbookcase':  {'name': 'cgbookcase', 'inhalt': 'PBR-Texturen', 'lizenz': 'CC0', 'zugang': 'manuell', 'url': 'https://www.cgbookcase.com', 'fuer': 'Spiel, Film'},
    'mixamo':      {'name': 'Mixamo (Adobe)', 'inhalt': 'Figuren-Animationen (Motion Capture)', 'lizenz': 'kostenlos für eigene Spiele/Filme (Adobe-Konto), Rohdateien nicht weitergeben', 'zugang': 'manuell', 'url': 'https://www.mixamo.com', 'fuer': 'Spiel, Film'},
    'google_fonts': {'name': 'Google Fonts', 'inhalt': 'Schriften für UI/Titel', 'lizenz': 'SIL OFL / Apache', 'zugang': 'manuell', 'url': 'https://fonts.google.com', 'fuer': 'Spiel, Film'},
    'blender_add_ons': {'name': 'extensions.blender.org', 'inhalt': 'Blender-Add-ons', 'lizenz': 'GPL', 'zugang': 'auto (gf blender-einrichten)', 'url': 'https://extensions.blender.org', 'fuer': 'Spiel, Film'},
}


def _get(url, timeout=60, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _text(url):
    return _get(url).decode('utf-8', errors='replace')


def _download(url, target: Path, headers=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size > 0:
        return target
    tmp = target.with_suffix(target.suffix + '.part')
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=900) as r, open(tmp, 'wb') as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, target)
    return target


def remote_size(url):
    try:
        req = urllib.request.Request(url, method='HEAD', headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get('Content-Length') or 0)
    except (urllib.error.URLError, OSError, ValueError):
        return 0


def _safe_extract(z: Path, dest: Path):
    with zipfile.ZipFile(z) as zf:
        for n in zf.namelist():
            if '..' in n.replace('\\', '/').split('/') or n.startswith(('/', '\\')) or ':' in n:
                raise ValueError('unerwarteter Inhalt im ZIP')
        zf.extractall(dest)


# ------------------------------------------------------------------ Kenney (CC0)
def _kenney_slugs(url):
    skip = ('category', 'tag', 'series', 'page', 'search')
    try:
        page = _text(url)
    except (urllib.error.URLError, OSError):            # einzelne Kenney-Seite nicht erreichbar → überspringen
        return []
    return [m for m in re.findall(r'kenney\.nl/assets/([a-z0-9-]+)', page) if not m.startswith(skip)]


def kenney_search(query, limit=10):
    """Schlagwort-Seiten (tag:) und Namensabgleich über alle Übersichtsseiten."""
    words = [w.lower() for w in query.split()]
    found = []
    for w in words:
        for slug in _kenney_slugs('https://kenney.nl/assets/tag:' + urllib.parse.quote(w)):
            if slug not in found:
                found.append(slug)
    for page in range(1, 20):
        slugs = _kenney_slugs(f'https://kenney.nl/assets/page:{page}')
        if not slugs:
            break
        for slug in slugs:
            if slug not in found and any(w in slug for w in words):
                found.append(slug)
        if len(found) >= limit * 2:
            break
    return [{'id': s, 'name': s.replace('-', ' ').title(), 'quelle': 'kenney', 'typ': 'paket', 'lizenz': 'CC0', 'url': f'https://kenney.nl/assets/{s}'} for s in found[:limit]]


def kenney_fetch(slug, root: Path, max_mb=300):
    page = _text(f'https://kenney.nl/assets/{slug}')
    links = re.findall(r'https://kenney\.nl/media/[^"\' ]+\.zip', page)
    if not links:
        raise ValueError(f'Kenney: kein Download für {slug} gefunden')
    mb = remote_size(links[0]) / 1e6
    if mb > max_mb:
        raise ValueError(f'Kenney {slug}: {mb:.0f} MB – über dem Limit von {max_mb} MB. Mit --max-mb erlauben.')
    dest = root / 'kenney' / slug
    z = _download(links[0], dest / Path(urllib.parse.urlparse(links[0]).path).name)
    size = z.stat().st_size
    _safe_extract(z, dest)
    z.unlink()
    return dest, size


# ------------------------------------------------------------------ OpenGameArt (nur CC0)
OGA_TYPES = {'3d': 10, '2d': 9, 'musik': 12, 'sound': 13, 'textur': 14}


def oga_search(query, typ='3d', limit=10):
    tid = OGA_TYPES.get(typ, 10)
    q = urllib.parse.quote(query)
    page = _text(f'https://opengameart.org/art-search-advanced?keys={q}&field_art_type_tid%5B%5D={tid}&field_art_licenses_tid%5B%5D=4')
    # Navigationslinks (FAQ, Wettbewerbe …) stehen auch auf einer leeren Suche – die werden abgezogen
    nav = set(re.findall(r'href="/content/([a-z0-9-]+)"', _text('https://opengameart.org/art-search-advanced?keys=zzqqxxnichts')))
    slugs = []
    for s in re.findall(r'href="/content/([a-z0-9-]+)"', page):
        if s not in slugs and s not in nav:
            slugs.append(s)
    return [{'id': s, 'name': s.replace('-', ' '), 'quelle': 'opengameart', 'typ': typ, 'lizenz': 'CC0 (vor dem Laden geprüft)', 'url': f'https://opengameart.org/content/{s}'} for s in slugs[:limit]]


def oga_fetch(slug, root: Path, max_mb=300):
    page = _text(f'https://opengameart.org/content/{slug}')
    lic = set(m.lower() for m in re.findall(r'(CC0|CC-BY-SA [0-9.]+|CC-BY [0-9.]+|GPL [0-9.]+|OGA-BY [0-9.]+)', page))
    if lic != {'cc0'}:
        raise ValueError(f'OpenGameArt {slug}: Lizenz nicht eindeutig CC0 ({", ".join(sorted(lic)) or "unbekannt"}) – nicht geladen')
    files = sorted(set(re.findall(r'https://opengameart\.org/sites/default/files/[^"]+\.(?:zip|blend|fbx|glb|gltf|obj|png|ogg|wav|mp3)', page)))
    files = [f for f in files if '/css/' not in f and '/styles/' not in f]
    badges = re.compile(r'/(cc0|cc-by[^/]*|gpl[^/]*|oga-by[^/]*)\.png$', re.I)
    files = [f for f in files if not badges.search(f)]
    if not files:
        raise ValueError(f'OpenGameArt {slug}: keine Dateien gefunden')
    total = sum(remote_size(html.unescape(f)) for f in files)
    if total > max_mb * 1e6:
        raise ValueError(f'OpenGameArt {slug}: {total / 1e6:.0f} MB – über dem Limit von {max_mb} MB. Mit --max-mb erlauben.')
    dest = root / 'opengameart' / slug
    size = 0
    for f in files:
        t = _download(html.unescape(f), dest / urllib.parse.unquote(Path(urllib.parse.urlparse(f).path).name))
        size += t.stat().st_size
        if t.suffix == '.zip':
            _safe_extract(t, dest / t.stem)
            t.unlink()
    return dest, size


# ------------------------------------------------------------------ Sketchfab (CC0 / CC-BY)
def sketchfab_search(query, limit=10, include_cc_by=True):
    out = []
    for lic in (['cc0', 'by'] if include_cc_by else ['cc0']):
        q = urllib.parse.quote(query)
        d = json.loads(_text(f'https://api.sketchfab.com/v3/search?type=models&q={q}&downloadable=true&license={lic}&count={limit}'))
        for r in d.get('results', []):
            out.append({'id': r['uid'], 'name': r['name'], 'quelle': 'sketchfab', 'typ': 'modell', 'lizenz': (r.get('license') or {}).get('label', lic),
                        'autor': (r.get('user') or {}).get('displayName', ''), 'url': f"https://sketchfab.com/3d-models/{r['uid']}",
                        'dreiecke': r.get('faceCount')})
    return out[:limit]


def sketchfab_fetch(uid, root: Path):
    token = os.environ.get('SKETCHFAB_TOKEN')
    if not token:
        raise PermissionError('Sketchfab-Download braucht ein kostenloses Konto: Token unter sketchfab.com/settings/password als Umgebungsvariable SKETCHFAB_TOKEN hinterlegen.')
    meta = json.loads(_text(f'https://api.sketchfab.com/v3/models/{uid}'))
    d = json.loads(_get(f'https://api.sketchfab.com/v3/models/{uid}/download', headers={'Authorization': f'Token {token}'}).decode('utf-8'))
    item = d.get('gltf') or d.get('glb') or d.get('source')
    dest = root / 'sketchfab' / uid
    z = _download(item['url'], dest / f'{uid}.zip')
    size = z.stat().st_size
    if zipfile.is_zipfile(z):
        _safe_extract(z, dest)
        z.unlink()
    return dest, size, (meta.get('license') or {}).get('label', '?'), (meta.get('user') or {}).get('displayName', '?')


# ------------------------------------------------------------------ Freesound (CC0)
def freesound_search(query, limit=10):
    key = os.environ.get('FREESOUND_KEY')
    if not key:
        raise PermissionError('Freesound braucht einen kostenlosen API-Schlüssel (freesound.org/apiv2/apply) als Umgebungsvariable FREESOUND_KEY.')
    q = urllib.parse.quote(query)
    d = json.loads(_text(f'https://freesound.org/apiv2/search/text/?query={q}&filter=license:%22Creative%20Commons%200%22&fields=id,name,license,duration,username,previews&page_size={limit}&token={key}'))
    return [{'id': str(r['id']), 'name': r['name'], 'quelle': 'freesound', 'typ': 'sound', 'lizenz': 'CC0', 'autor': r.get('username'),
             'url': f"https://freesound.org/s/{r['id']}/", 'dauer_s': r.get('duration')} for r in d.get('results', [])]
