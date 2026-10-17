"""Modellverwaltung und Model Router.

Fähigkeiten werden nur eingetragen, wenn sie für dieses Modell belegt sind (Herstellerangabe) – und als
„auf diesem PC getestet“ erst nach einem erfolgreichen echten Lauf (siehe verified_capabilities).
Neue Modelle: Eintrag in MODELS ergänzen, Dateien in ComfyUI/models ablegen – Projekte müssen nicht
neu konfiguriert werden.
"""
from __future__ import annotations
import json
from pathlib import Path

MODELS = [
    {
        'id': 'flux2-klein-4b',
        'name': 'FLUX.2 [klein] 4B (destilliert)',
        'vendor': 'Black Forest Labs',
        'license': 'Apache 2.0', 'license_url': 'https://huggingface.co/black-forest-labs/FLUX.2-klein-4B',
        'commercial_use': True,
        'source': 'https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b (identische Prüfsumme wie Original von Black Forest Labs)',
        'files': {
            'diffusion_models/flux-2-klein-4b.safetensors': 'ec3d4e733a771f61c052fb4856c48b336c55eaf2c65487c2a1faeb9bbda7a343',
            'text_encoders/qwen_3_4b.safetensors': '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a',
            'vae/flux2-vae.safetensors': '868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3',
        },
        'vram_min_gb': 8,
        'capabilities': ['text_to_image', 'postprocess_pixelate'],
        'capabilities_not_wired': ['image_edit (Referenzbild-Bearbeitung laut Hersteller möglich, in GAMEFORGE noch nicht angebunden)', 'inpainting', 'outpainting', 'upscaling'],
        'steps': 4, 'cfg': 1.0,
        # Eignung je Stil: gut / mit Nachbearbeitung / eingeschränkt
        'styles': {'aaa_photoreal': 'gut', 'realistic': 'gut', 'semi_realistic': 'gut', 'stylized_3d': 'gut', 'cartoon': 'gut',
                   'anime': 'gut', 'fantasy': 'gut', 'low_poly': 'eingeschränkt', 'pixel_art': 'mit Nachbearbeitung',
                   'flat_2d': 'gut', 'mobile': 'gut', 'retro_indie': 'gut'},
    },
]


def comfy_models_dir(comfy_root):
    return Path(comfy_root) / 'ComfyUI' / 'models' if comfy_root else None


def installed(comfy_root):
    out = []
    base = comfy_models_dir(comfy_root)
    for m in MODELS:
        files = {}
        for rel in m['files']:
            p = base / rel if base else None
            files[rel] = {'exists': bool(p and p.is_file()), 'size': p.stat().st_size if p and p.is_file() else 0}
        out.append({**m, 'installed': all(f['exists'] for f in files.values()), 'file_state': files})
    return out


def route(comfy_root, style_id, capability='text_to_image', vram_gb=None, verified=None):
    """Wählt ein installiertes, lizenzgeprüftes Modell für Stil und Aufgabe. Begründung wird mitgeliefert."""
    candidates = []
    for m in installed(comfy_root):
        if not m['installed']:
            continue
        if capability not in m['capabilities']:
            continue
        if vram_gb and vram_gb < m['vram_min_gb']:
            continue
        fit = m['styles'].get(style_id)
        if not fit:
            continue
        rank = {'gut': 0, 'mit Nachbearbeitung': 1, 'eingeschränkt': 2}[fit]
        candidates.append((rank, m, fit))
    if not candidates:
        return {'ok': False, 'model': None,
                'reason': 'Kein installiertes Modell kann diesen Stil bzw. diese Aufgabe zuverlässig erzeugen. '
                          'Modell nachinstallieren oder Stil/Auftrag anpassen.'}
    rank, m, fit = sorted(candidates, key=lambda c: c[0])[0]
    note = {'gut': 'geeignet', 'mit Nachbearbeitung': 'geeignet mit fester Nachbearbeitung (Raster + Palette)',
            'eingeschränkt': 'nur eingeschränkt geeignet – Ergebnis unbedingt prüfen'}[fit]
    return {'ok': True, 'model': m['id'], 'model_name': m['name'], 'fit': fit,
            'reason': f'{m["name"]}: für diesen Stil {note}. Lizenz {m["license"]}.',
            'verified_on_this_pc': bool(verified and m['id'] in verified)}


def verified_set(store):
    row = store.one("SELECT value FROM schema_meta WHERE key='ref_verified_models'")
    return set(json.loads(row['value'])) if row else set()


def mark_verified(store, model_id):
    s = verified_set(store); s.add(model_id)
    store.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('ref_verified_models',?)", (json.dumps(sorted(s)),))
