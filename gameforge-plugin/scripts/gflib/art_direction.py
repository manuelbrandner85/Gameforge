"""Universal Game Art Director: projektspezifisches Art-Direction-Profil.

Grundsätze:
- Der Spielstil bestimmt Modell und Workflow – nie umgekehrt.
- Festgelegte Nutzerangaben (Spielbibel, Stilfeld) haben Vorrang vor Automatik.
- Ein vom Nutzer gespeichertes/freigegebenes Profil wird nie automatisch überschrieben.
"""
from __future__ import annotations
import datetime as dt
import json

# 12 Grundstile (erweiterbar). quality_auto: Qualitätsstufe im AUTO-Modus.
STYLES = {
    'aaa_photoreal': {'label': 'AAA+ Hyper-Fotorealismus', 'keywords': ['aaa', 'fotoreal', 'photoreal', 'hyperreal', 'hyper-real', 'cinematic'],
        'prompt': 'hyper-photorealistic production reference, shot on a full-frame cinema camera, 50mm lens, physically based materials, natural skin and eye detail, film-grade lighting, ultra detailed textures',
        'lighting': 'filmisches, physikalisch plausibles Licht', 'quality_auto': 'CINEMATIC_MASTER', 'poly_budget': 'Hero-Asset, Nanite-geeignet (hoch)', 'texture': '4K PBR'},
    'realistic': {'label': 'Realistische 3D-Spiele', 'keywords': ['realist'],
        'prompt': 'realistic 3D game asset reference, physically plausible materials, natural proportions, neutral studio lighting, high detail',
        'lighting': 'neutrales Studiolicht', 'quality_auto': 'HIGH', 'poly_budget': '30–80k Dreiecke (Figur)', 'texture': '2K–4K PBR'},
    'semi_realistic': {'label': 'Semi-realistisch', 'keywords': ['semi'],
        'prompt': 'semi-realistic stylized proportions with realistic material detail, artistically heightened design, clean readable forms',
        'lighting': 'leicht überhöhtes Studiolicht', 'quality_auto': 'HIGH', 'poly_budget': '20–60k Dreiecke', 'texture': '2K PBR'},
    'stylized_3d': {'label': 'Stylized 3D', 'keywords': ['stylized', 'stilisiert'],
        'prompt': 'stylized 3D game art, bold defined shapes, clean consistent color palette, hand-crafted look, readable silhouette',
        'lighting': 'weiches, gerichtetes Licht', 'quality_auto': 'STANDARD', 'poly_budget': '10–30k Dreiecke', 'texture': '1K–2K, handbemalt oder PBR-light'},
    'cartoon': {'label': 'Cartoon', 'keywords': ['cartoon', 'comic', 'toon'],
        'prompt': 'cartoon game character art, simplified shapes, exaggerated proportions, cel shading, clean outlines, vibrant flat colors',
        'lighting': 'Cel-Shading', 'quality_auto': 'STANDARD', 'poly_budget': '5–20k Dreiecke', 'texture': '1K, flache Farben'},
    'anime': {'label': 'Anime', 'keywords': ['anime', 'manga'],
        'prompt': 'anime style game art, consistent anime character design, clean line art, cel shaded, expressive faces',
        'lighting': 'Anime-Schattierung', 'quality_auto': 'STANDARD', 'poly_budget': '10–30k Dreiecke', 'texture': '1K–2K, Toon-Shader'},
    'fantasy': {'label': 'Fantasy', 'keywords': ['fantasy', 'magie', 'magic'],
        'prompt': 'high fantasy game art, magical details, ornate design language, epic atmosphere',
        'lighting': 'atmosphärisch, magische Akzente', 'quality_auto': 'HIGH', 'poly_budget': 'projektabhängig', 'texture': '2K'},
    'low_poly': {'label': 'Low-Poly', 'keywords': ['low poly', 'low-poly', 'lowpoly'],
        'prompt': 'low poly 3D game art, flat shaded facets, clear geometric forms, minimal detail, simple color palette',
        'lighting': 'flaches, klares Licht', 'quality_auto': 'STANDARD', 'poly_budget': '< 3k Dreiecke', 'texture': 'Farbpalette / 256 px'},
    'pixel_art': {'label': 'Pixel-Art', 'keywords': ['pixel'],
        'prompt': 'pixel art game sprite, crisp hard pixel edges, limited color palette, no anti-aliasing, flat shading, readable silhouette',
        'lighting': 'flach, 2–3 Schattenstufen', 'quality_auto': 'STANDARD', 'poly_budget': '2D-Sprite', 'texture': 'Palette 16–32 Farben',
        'postprocess': {'pixel_grid': 8, 'colors': 24}},
    'flat_2d': {'label': '2D-Spiele', 'keywords': ['2d', 'zweidimensional', 'side-scroll', 'seitenansicht (2d)'],
        'prompt': '2D game illustration, clean layered artwork, flat background separation, crisp edges',
        'lighting': 'illustrativ', 'quality_auto': 'STANDARD', 'poly_budget': '2D', 'texture': 'Ebenen, Transparenz'},
    'mobile': {'label': 'Mobile Games', 'keywords': ['mobil', 'mobile'],
        'prompt': 'mobile game art, bold readable shapes at small sizes, simplified detail, strong contrast',
        'lighting': 'kontraststark, einfach', 'quality_auto': 'STANDARD', 'poly_budget': '< 10k Dreiecke', 'texture': '512 px – 1K'},
    'retro_indie': {'label': 'Indie & Retro', 'keywords': ['retro', 'indie', 'handgezeichnet', 'hand-drawn', 'minimal'],
        'prompt': 'indie game art, hand-drawn aesthetic, distinctive retro look, minimal and charming',
        'lighting': 'stilisiert', 'quality_auto': 'STANDARD', 'poly_budget': 'projektabhängig', 'texture': 'handgezeichnet'},
}
# Erkennungsreihenfolge: spezifische Stile vor allgemeinen.
DETECT_ORDER = ['pixel_art', 'low_poly', 'anime', 'cartoon', 'semi_realistic', 'aaa_photoreal', 'stylized_3d', 'realistic',
                'mobile', 'flat_2d', 'retro_indie', 'fantasy']


def detect_style(game):
    """Liefert (style_id, Begründung). Das Stilfeld des Spiels hat Vorrang, danach Genre/Kamera/Spielbibel."""
    style_field = (game.get('style') or '').lower()
    for sid in DETECT_ORDER:
        if any(k in style_field for k in STYLES[sid]['keywords']):
            return sid, f'Aus dem Stilfeld des Projekts: „{game.get("style")}“'
    bible = game.get('bible') or {}
    text = ' '.join([game.get('genre') or '', game.get('camera') or '', bible.get('vision', ''), bible.get('technical', ''), bible.get('release', '')]).lower()
    for sid in DETECT_ORDER:
        if any(k in text for k in STYLES[sid]['keywords']):
            return sid, 'Aus Genre/Kamera/Spielbibel abgeleitet'
    return 'realistic', 'Kein Stil angegeben – neutraler Standard „Realistisch“ (bitte prüfen)'


def build_profile(game):
    sid, reason = detect_style(game)
    st = STYLES[sid]
    bible = game.get('bible') or {}
    platform = bible.get('release', '')
    mobile = 'mobil' in platform.lower() or 'mobile' in platform.lower()
    return {
        'style_id': sid, 'style_label': st['label'], 'style_reason': reason,
        'game_title': game['title'], 'genre': game.get('genre') or '', 'camera': game.get('camera') or '',
        'platform': platform or 'nicht festgelegt', 'engine': game.get('engine') or 'Unreal Engine 5',
        'style_prompt': st['prompt'], 'lighting': st['lighting'],
        'color_palette': '', 'material_style': '', 'animation_style': '',
        'canon_excerpt': (bible.get('canon') or '')[:900],
        'quality_auto': 'STANDARD' if mobile and st['quality_auto'] == 'CINEMATIC_MASTER' else st['quality_auto'],
        'poly_budget': st['poly_budget'], 'texture_budget': '1K mobil-optimiert' if mobile else st['texture'],
        'postprocess': st.get('postprocess', {}),
        'locked_designs': [],
        'notes': '',
    }


EDITABLE = ('style_id', 'style_prompt', 'lighting', 'color_palette', 'material_style', 'animation_style', 'quality_auto',
            'poly_budget', 'texture_budget', 'notes', 'platform')


def ensure_profile(store, gid):
    """Profil laden oder (nur additiv) neu anlegen. Bestehende Projektdaten werden nicht verändert."""
    row = store.one('SELECT * FROM art_profiles WHERE game_id=?', (gid,))
    if row:
        return {**row, 'profile': json.loads(row['profile'])}
    game = store.game(gid)
    if not game:
        raise ValueError('Spiel nicht gefunden')
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    prof = build_profile(game)
    store.execute('INSERT OR IGNORE INTO art_profiles(game_id,profile,source,approved,updated_at) VALUES(?,?,?,?,?)',
                  (gid, json.dumps(prof, ensure_ascii=False), 'automatisch', 0, now))
    return ensure_profile(store, gid)


def update_profile(store, gid, data):
    cur = ensure_profile(store, gid)
    prof = cur['profile']
    for k in EDITABLE:
        if k in data:
            v = str(data[k])[:4000]
            if k == 'style_id':
                if v not in STYLES:
                    raise ValueError('Unbekannter Grafikstil')
                if v != prof['style_id']:
                    prof['style_label'] = STYLES[v]['label']
                    prof['postprocess'] = STYLES[v].get('postprocess', {})
                    if 'style_prompt' not in data:
                        prof['style_prompt'] = STYLES[v]['prompt']
                    prof['style_reason'] = 'Von dir festgelegt'
            if k == 'quality_auto' and v not in ('DRAFT', 'STANDARD', 'HIGH', 'CINEMATIC_MASTER'):
                raise ValueError('Unbekannte Qualitätsstufe')
            prof[k] = v
    approved = 1 if data.get('approved') else cur['approved']
    store.execute('UPDATE art_profiles SET profile=?,source=?,approved=?,updated_at=? WHERE game_id=?',
                  (json.dumps(prof, ensure_ascii=False), 'vom Nutzer bearbeitet', approved,
                   dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), gid))
    return ensure_profile(store, gid)
