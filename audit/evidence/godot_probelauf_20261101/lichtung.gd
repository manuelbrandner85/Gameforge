extends Node3D
## Waldlichtung (GAMEFORGE-Probelauf): stellt Sonne und Kamera, misst die echten Modellgrößen.
## Mit „-- --beleg“ gestartet: wartet, bis Licht und SDFGI stehen, speichert ein Bildschirmfoto und beendet sich.

@onready var kamera: Camera3D = $Kamera
@onready var sonne: DirectionalLight3D = $Sonne


func _ready() -> void:
	sonne.rotation_degrees = Vector3(-38.0, -35.0, 0.0)
	kamera.position = Vector3(0.0, 1.3, 3.6)
	kamera.look_at(Vector3(0.0, 0.35, -0.4))
	for n in get_children():
		if n is Node3D and n.scene_file_path != "":
			print("MASS ", n.name, " ", _box(n).size)
	if "--beleg" in OS.get_cmdline_user_args():
		for i in 120:
			await get_tree().process_frame
		var bild: Image = get_viewport().get_texture().get_image()
		var pfad: String = ProjectSettings.globalize_path("res://beleg_lichtung.png")
		print("BELEG ", bild.save_png(pfad), " ", pfad, " ", bild.get_size())
		get_tree().quit()


func _box(n: Node) -> AABB:
	var box := AABB()
	var erstes := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = m.global_transform * m.get_aabb()
		box = b if erstes else box.merge(b)
		erstes = false
	return box
