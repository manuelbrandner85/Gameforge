"""Qualitätsprofile. CINEMATIC MASTER = höchste sinnvolle Qualität IM STIL des Spiels (nicht automatisch Fotorealismus).

FLUX.2 klein (destilliert) ist für 4 Schritte ausgelegt; mehr Schritte verbessern es nicht. Die Stufen
unterscheiden sich daher in Auflösung, Anzahl Varianten und Wiederholungsgrenze.
"""
PROFILES = {
    'DRAFT': {'label': 'Entwurf', 'long_side': 768, 'variants': 1, 'max_attempts': 1, 'desc': 'Schnelle Vorschau zur Ideenfindung'},
    'STANDARD': {'label': 'Standard', 'long_side': 1024, 'variants': 1, 'max_attempts': 2, 'desc': 'Produktionsnahe Referenz'},
    'HIGH': {'label': 'Hohe Qualität', 'long_side': 1280, 'variants': 2, 'max_attempts': 2, 'desc': 'Zwei Varianten zur Auswahl, zusätzliche Prüfung'},
    'CINEMATIC_MASTER': {'label': 'Cinematic Master', 'long_side': 1536, 'variants': 2, 'max_attempts': 3, 'desc': 'Maximale sinnvolle Qualität im Projektstil'},
}

# Seitenverhältnis je Ansicht/Asset: Figuren hochkant, Umgebungen quer.
PORTRAIT_VIEWS = {'front', 'side', 'back', 'outfit', 'pose', 'combat_pose', 'scale'}
LANDSCAPE_VIEWS = {'overview', 'map', 'landmarks', 'lighting', 'layout'}


def resolve(quality, profile):
    q = profile.get('quality_auto', 'STANDARD') if quality in (None, '', 'AUTO') else quality
    if q not in PROFILES:
        raise ValueError('Unbekannte Qualitätsstufe')
    return q, PROFILES[q]


def dimensions(long_side, view, category):
    def r16(v):
        return max(256, int(round(v / 16)) * 16)
    if view in PORTRAIT_VIEWS or category in ('character', 'boss', 'npc', 'creature'):
        return r16(long_side * 3 / 4), r16(long_side)
    if view in LANDSCAPE_VIEWS or category == 'environment':
        return r16(long_side), r16(long_side * 9 / 16)
    return r16(long_side), r16(long_side)
