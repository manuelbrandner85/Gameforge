"""Blender-Grundausstattung für Spiel- und Filmproduktion (alles kostenlos, offizieller Katalog extensions.blender.org, GPL).

SETUP_CODE läuft unverändert in beiden Wegen:
- im offenen Blender über den Blender-MCP (execute_blender_code) – bevorzugt, Manuel sieht es,
- im Hintergrund: blender -b --online-mode --python-expr … (nur wenn kein Blender offen ist).
Installiert nur Fehlendes, trägt die Asset-Bibliothek „GAMEFORGE CC0“ ein, speichert die Einstellungen.
"""
ADDONS = [
    # Natur, Gelände, Verteilen
    'sapling_tree_gen', 'antlandscape', 'Bagapie', 'scatter_objects', 'PlaceHelper', 'ivygen',
    # Modellieren
    'bool_tool', 'archimesh', 'edit_mesh_tools', 'f2', 'snap_utilities_line', 'auto_mirror', 'curve_tools', 'copy_attributes_menu',
    'measureit', 'looptools', 'extra_mesh_objects',
    # Spiele
    'proto_game_asset_tools', 'asset_optimizer', 'lodify_optimizer', 'expLODe', 'texel_density_checker', 'io_scene_psk_psa',
    'PolyQuilt_Fork', 'bsurfaces_gpl_edition', 'cell_fracture',
    # Materialien / Bake
    'ambientcg_material_importer', 'material_utilities', 'bake_to_single_material', 'thebetterbaker',
    # Film
    'add_camera_rigs', 'camera_shakify', 'storypencil_storyboard_tools', 'storytools', 'stored_views', 'sun_position', 'amaranth',
]


def setup_code(asset_library_path: str) -> str:
    return f'''
import bpy, os
wanted = {ADDONS!r}
lib = r"{asset_library_path}"
res = {{"neu": [], "schon_da": [], "fehler": {{}}}}
prefs = bpy.context.preferences
active = set(prefs.addons.keys())
missing = [p for p in wanted if f"bl_ext.blender_org.{{p}}" not in active]
if missing:
    bpy.ops.extensions.repo_sync_all()
    repo = next(i for i, r in enumerate(prefs.extensions.repos) if "extensions.blender.org" in (r.remote_url or ""))
    for pid in missing:
        try:
            bpy.ops.extensions.package_install(repo_index=repo, pkg_id=pid, enable_on_install=True)
            (res["neu"] if f"bl_ext.blender_org.{{pid}}" in prefs.addons.keys() else res["fehler"].setdefault(pid, "nicht aktiv"))
            if f"bl_ext.blender_org.{{pid}}" in prefs.addons.keys(): res["neu"].append(pid)
        except Exception as ex:
            res["fehler"][pid] = str(ex)[:160]
res["schon_da"] = [p for p in wanted if p not in missing]
os.makedirs(lib, exist_ok=True)
libs = prefs.filepaths.asset_libraries
if not any(os.path.normcase(os.path.normpath(l.path)) == os.path.normcase(lib) for l in libs):
    bpy.ops.preferences.asset_library_add(directory=lib); libs[-1].name = "GAMEFORGE CC0"; res["bibliothek"] = "neu eingetragen"
else:
    res["bibliothek"] = "schon eingetragen"
bpy.ops.wm.save_userpref()
result = res
print("GF_SETUP", result)
'''
