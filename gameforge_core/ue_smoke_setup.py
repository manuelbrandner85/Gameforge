"""GAMEFORGE Unreal smoke test, step 1 (runs headless: UnrealEditor-Cmd <UE_Smoke.uproject> -run=pythonscript -script=...).

Builds in the isolated test project projects/_smoke/UE_Smoke (never in GENESIS):
- level /Game/Smoke/L_Smoke with floor, sun, sky light
- imports the Blender smoke cube (bl_smoke.fbx) and checks its bounds (1 m Blender -> 100 cm Unreal)
- level sequence /Game/Smoke/LS_Smoke (24 fps, 5 frames) with a cine camera and camera cut
- Movie Render Queue preset /Game/Smoke/MRQ_Smoke (PNG, 640x360) for the command-line render
Env GF_SMOKE_FBX = path of bl_smoke.fbx, GF_SMOKE_OUT = PNG output folder. Prints GF_UE_SMOKE {...}.
"""
import json
import os

import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
V, R = unreal.Vector, unreal.Rotator
FBX, OUT = os.environ["GF_SMOKE_FBX"], os.environ["GF_SMOKE_OUT"]
res = {}


def spawn_mesh(mesh, loc):
    """headless: spawn_actor_from_object(mesh) spawns nothing in the commandlet; a StaticMeshActor + mesh works"""
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, loc, R(0, 0, 0))
    a.static_mesh_component.set_static_mesh(mesh)
    return a

# headless commandlet: the LevelEditorSubsystem has no editor world; new map via EditorLoadingAndSavingUtils
world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
unreal.EditorLoadingAndSavingUtils.save_map(world, "/Game/Smoke/L_Smoke")
world = unreal.EditorLoadingAndSavingUtils.load_map("/Game/Smoke/L_Smoke")   # spawning needs the loaded editor world
res["world"] = world.get_name() if world else None
floor = spawn_mesh(eal.load_asset("/Engine/BasicShapes/Plane"), V(0, 0, 0))
floor.set_actor_scale3d(V(10, 10, 1))
sun = eas.spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 500), R(0, -45, 30))
eas.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 300), R(0, 0, 0))
eas.spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0), R(0, 0, 0))

# Blender -> Unreal import check
task = unreal.AssetImportTask()
task.filename, task.destination_path, task.destination_name = FBX, "/Game/Smoke", "SM_BlenderCube"
task.automated, task.replace_existing, task.save = True, True, True
opt = unreal.FbxImportUI()
opt.import_mesh, opt.import_as_skeletal, opt.import_materials = True, False, True
opt.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
opt.static_mesh_import_data.set_editor_property("combine_meshes", True)
task.options = opt
at.import_asset_tasks([task])
mesh = eal.load_asset("/Game/Smoke/SM_BlenderCube")
bb = mesh.get_bounding_box()
size = [round(v, 1) for v in (bb.max - bb.min).to_tuple()]
res["import_size_cm"] = size
res["import_ok"] = all(abs(s - 100.0) < 1.0 for s in size)
cube = spawn_mesh(mesh, V(0, 0, 50))

# camera + level sequence (5 frames @ 24 fps)
cam = eas.spawn_actor_from_class(unreal.CineCameraActor, V(-300, -250, 200), R(0, -20, 40))
seq = at.create_asset("LS_Smoke", "/Game/Smoke", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(24, 1))
seq.set_playback_start(0)
seq.set_playback_end(5)
binding = seq.add_possessable(cam)
cut = seq.add_track(unreal.MovieSceneCameraCutTrack)
sec = cut.add_section()
sec.set_range(0, 5)
sec.set_camera_binding_id(seq.get_binding_id(binding))
cube_b = seq.add_possessable(cube)
tr = cube_b.add_track(unreal.MovieScene3DTransformTrack)
ts = tr.add_section()
ts.set_range(0, 5)
yaw = ts.get_all_channels()[5]                             # rotation Z (yaw): the cube turns -> frames differ
yaw.add_key(unreal.FrameNumber(0), 0.0)
yaw.add_key(unreal.FrameNumber(4), 40.0)
eal.save_loaded_asset(seq)
unreal.EditorLoadingAndSavingUtils.save_map(world, "/Game/Smoke/L_Smoke")

# MRQ preset: PNG sequence, 640x360
cfg = at.create_asset("MRQ_Smoke", "/Game/Smoke", unreal.MoviePipelinePrimaryConfig, unreal.MoviePipelinePrimaryConfigFactory())
cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
out = cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
out.set_editor_property("output_resolution", unreal.IntPoint(640, 360))
d = unreal.DirectoryPath()
d.set_editor_property("path", OUT)
out.set_editor_property("output_directory", d)
out.set_editor_property("file_name_format", "smoke.{frame_number}")
eal.save_loaded_asset(cfg)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
res.update({"level": "/Game/Smoke/L_Smoke", "sequence": seq.get_path_name(), "frames": 5, "preset": cfg.get_path_name()})
print("GF_UE_SMOKE " + json.dumps(res))
