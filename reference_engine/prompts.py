"""Prompt-Erzeugung aus Art-Direction-Profil + Referenzauftrag. Deterministisch und nachvollziehbar."""
from __future__ import annotations
import hashlib

VIEW_TEXT = {
    'front': 'full body, front view, facing camera, neutral A-pose, orthographic-like, entire figure visible head to toe',
    'side': 'full body, exact side profile view, neutral A-pose, orthographic-like, entire figure visible',
    'back': 'full body, back view, seen from behind, neutral A-pose, entire figure visible',
    'face': 'head and shoulders close-up, front view, detailed face, neutral expression',
    'outfit': 'full body, outfit and armor focus, three-quarter view',
    'scale': 'full body next to a 1.8 meter tall human silhouette for scale, side by side, neutral pose',
    'pose': 'dynamic but readable pose, full body',
    'combat_pose': 'combat stance, full body, readable silhouette',
    'detail': 'close-up of design details, materials and ornaments',
    'grip': 'close-up of the grip and handle',
    'entrance': 'entrance view at eye level',
    'material': 'material and surface close-up, flat lighting',
    'cockpit': 'interior view of the cockpit',
    'overview': 'wide establishing view of the whole environment',
    'map': 'top-down map view',
    'landmarks': 'view of the most important landmarks',
    'materials': 'material study sheet of the environment surfaces',
    'lighting': 'mood and lighting study',
    'layout': 'game user interface layout screen',
    'states': 'UI states: normal, hover, pressed, disabled',
    'icons': 'game icon set, consistent style',
    'typography': 'typography and title lettering study',
}
CATEGORY_TEXT = {'character': 'game character', 'boss': 'boss character', 'npc': 'non-player character', 'weapon': 'weapon',
                 'building': 'building / architecture', 'vehicle': 'vehicle', 'environment': 'game environment', 'prop': 'prop / object',
                 'ui': 'user interface', 'creature': 'creature'}
NEUTRAL_BG = {'front', 'side', 'back', 'scale', 'outfit', 'grip', 'detail', 'face'}


def build(profile, ref, game_title):
    """Liefert (prompt, design_hash). design_hash ändert sich nur, wenn sich die Vorgaben ändern (für Wiederverwendung)."""
    view = ref['view']
    parts = [
        f'{CATEGORY_TEXT.get(ref["category"], "game asset")} reference image for the game "{game_title}": {ref["name"]}.',
        VIEW_TEXT.get(view, view) + '.',
    ]
    if ref.get('details'):
        parts.append('Fixed design details that must be followed exactly: ' + ref['details'].strip() + '.')
    if profile.get('canon_excerpt') and ref['category'] in ('character', 'boss', 'npc', 'creature', 'building', 'environment'):
        parts.append('Lore context (do not contradict): ' + profile['canon_excerpt'][:400] + '.')
    parts.append('Art style: ' + profile['style_prompt'] + '.')
    if profile.get('color_palette'):
        parts.append('Color palette: ' + profile['color_palette'] + '.')
    if profile.get('material_style'):
        parts.append('Materials: ' + profile['material_style'] + '.')
    if view in NEUTRAL_BG:
        parts.append('Plain neutral light-grey studio background, even lighting, no cast shadows on background.')
    parts.append('Single subject, nothing cut off, clean silhouette. No text, no letters, no watermark, no logo, no frame, no collage.')
    prompt = ' '.join(parts)
    design = '|'.join([ref['name'], ref['category'], ref.get('details') or '', profile['style_id'], profile['style_prompt'],
                       profile.get('color_palette', ''), profile.get('material_style', '')])
    return prompt, hashlib.sha256(design.encode('utf-8')).hexdigest()[:16]


def asset_seed(game_id, asset_name, variant=0):
    """Gleicher Seed für alle Ansichten eines Assets → bessere Konsistenz zwischen Front/Seite/Rücken."""
    h = hashlib.sha256(f'{game_id}|{asset_name.strip().lower()}'.encode('utf-8')).hexdigest()
    return (int(h[:12], 16) + variant * 7919) % (2**48)
