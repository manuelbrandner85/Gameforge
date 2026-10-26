
import bpy, os, json
out = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5)); cube = bpy.context.object
bpy.ops.object.camera_add(location=(2.5, -2.5, 2.0)); cam = bpy.context.object
cam.rotation_euler = ((cube.location - cam.location).to_track_quat("-Z", "Y")).to_euler(); sc.camera = cam
bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16
sc.render.resolution_x, sc.render.resolution_y = 320, 180
sc.render.filepath = os.path.join(out, "bl_render.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "bl_smoke.blend"))
bpy.ops.export_scene.gltf(filepath=os.path.join(out, "bl_smoke.glb"), export_format="GLB")
bpy.ops.export_scene.fbx(filepath=os.path.join(out, "bl_smoke.fbx"))
bpy.ops.render.render(write_still=True)
print("BL_SMOKE", json.dumps({"dims": list(cube.dimensions)}))
