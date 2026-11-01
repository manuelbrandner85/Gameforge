---
name: godot-projekt
description: Spiele mit der Godot Engine (Godot 4, kostenlos/MIT) entwickeln – Godot-Projekt anlegen, Szenen und Nodes, GDScript, Blender-Modelle als glTF nach Godot bringen, im Editor arbeiten (Godot-MCP), Projekt prüfen und exportieren. Für 2D-, Pixel-Art-, stilisierte, kleine, Web- und Mobile-Spiele oder wenn der Nutzer Godot wünscht.
---

# Godot-Projekt

Werkzeug: `gf.cmd` (Pfad siehe Skill `gameforge-studio`). Godot ist die **zweite Spiel-Engine** neben Unreal.

## Wann Godot, wann Unreal
- **Unreal bleibt Standard** – besonders für fotorealistische 3D-Spiele, Open World, Filme/Cinematics (Sequencer, Movie Render Queue) und alle bestehenden Unreal-Projekte (z. B. GENESIS – dort nie die Engine wechseln).
- **Godot**, wenn der Nutzer es wünscht oder es klar besser passt: 2D und Pixel-Art, stilisierte/Low-Poly-3D-Spiele, kleine und mittlere Indie-Spiele, Browser- (Web) und Mobile-Spiele, schwache Zielhardware, schnelle Prototypen, vollständig quelloffene Engine (MIT, keine Umsatzbeteiligung).
- Unklar? Als Ja/Nein-Vorschlag fragen, Empfehlung zuerst mit einem Satz Begründung. Nie heimlich wechseln.

## Ablauf
1. **Godot vorhanden?** `gf.cmd godot status`. Fehlt Godot: Zustimmung holen (offizielles Release von GitHub, ca. 85 MB, MIT), dann `gf.cmd godot installieren` (SHA512-geprüft, nach `GAMEFORGE_DATA/tools/godot/`). Danach einmalig `gf.cmd godot mcp-einrichten` (Godot-MCP `@coding-solo/godot-mcp`, MIT, läuft lokal über Node) – wirkt in neuen Claude-Code-Sitzungen.
2. **Neues Spiel mit Godot**: `gf.cmd neu --titel "<Name>" --engine godot …` (wie Skill `neues-spiel`), dann `gf.cmd godot projekt "<Spiel>" --profil 3d|2d|pixel|web` → `godot/project.godot`.
   - `3d`: Forward+, Jolt-Physik, MSAA 4x, 8K-Schatten (höchste sinnvolle Qualität). `2d`: Forward+. `pixel`: scharfe Pixel (Nearest-Filter), Viewport-Skalierung. `web`: Compatibility-Renderer für Browser/schwache Geräte.
   - Bestehendes Godot-Projekt (Ordner mit `project.godot`): eigene Regeln/CLAUDE.md haben Vorrang, nichts anlegen.
3. **Im Editor arbeiten**: `gf.cmd godot start "<Spiel>"` (nur nach GPU-Prüfung) bzw. Godot-MCP-Werkzeuge (`launch_editor`, `create_scene`, `add_node`, `save_scene`, `run_project`, `get_debug_output`, `stop_project`). Szenen (`.tscn`), Skripte (`.gd`) und Ressourcen (`.tres`) sind Textdateien – Claude darf sie direkt schreiben; danach immer prüfen (Schritt 5).
   - Konventionen: Dateien und Ordner `snake_case` (`player.tscn`, `player.gd`), Nodes und Klassen `PascalCase`, Signale/Funktionen `snake_case`, Konstanten `UPPER_CASE`; statisch typisiertes GDScript (`var speed: float = 5.0`).
   - Ordner im Godot-Projekt: `assets/<Asset>/`, `scenes/`, `scripts/`, `ui/`, `audio/` – erst anlegen, wenn etwas hineinkommt.
4. **Modelle aus Blender** (Skill `blender-asset`): als **glTF binär (`.glb`)** exportieren – Godots natives 3D-Format, PBR-Materialien bleiben erhalten. 1 Godot-Einheit = 1 m (wie Blender), Y oben (der glTF-Export dreht automatisch). Kollision per Namenszusatz in Blender: `-col` (sichtbar + Kollision), `-colonly` (nur Kollision), `-convcolonly` (konvexe Kollision). Ablage `export/<Asset>/<Asset>.glb`.
   Import **nur nach Freigabe**: `gf.cmd godot import "<Spiel>" --asset "<Name>"` (kopiert nach `godot/assets/<Asset>/`, Godot liest sie echt ein; Überschreiben nur mit `--ueberschreiben` + automatischer Sicherung).
5. **Prüfen** (Pflicht vor jeder Fertigmeldung): `gf.cmd godot pruefen "<Spiel>"` – Godot öffnet das Projekt ohne Fenster, importiert alles und meldet Fehler aus dem echten Log (`GAMEFORGE_PRUEFUNG.json`). Spielbares mit `run_project` + `get_debug_output` testen; Bildbeleg per Screenshot.
6. **Assets**: kostenlose Quellen wie gewohnt (`gf.cmd assets suchen …` – Kenney und Poly Haven passen besonders gut zu Godot). Fab/Megascans-Inhalte sind laut Fab-Lizenz nicht auf Unreal beschränkt, aber Lizenz je Inhalt prüfen; „NoAI“-Inhalte nie in die Bild-KI.
7. **Export (Build)**: braucht die Godot-Exportvorlagen (`Godot_v<Version>-stable_export_templates.tpz`, ca. 1 GB) – nur nach Zustimmung laden. Ohne Vorlagen keinen Build als fertig melden.

## Qualität
Skill `maximum-realism-visual-fidelity` gilt auch hier, im Stil des Spiels: in 3D PBR-Materialien aus Blender/Poly Haven, WorldEnvironment mit filmischem Tonemapping (AgX/Filmic), SDFGI oder VoxelGI für indirektes Licht, Volumetric Fog sparsam, echte Maße. Braucht ein Projekt kompromisslosen Fotorealismus, Unreal empfehlen.

## Grenzen (ehrlich nennen)
- Der Godot-MCP startet/steuert Godot über die Kommandozeile und ein mitgeliefertes Skript; er sieht keine live laufende Editor-Sitzung wie der Unreal-MCP.
- GPU: Godot-Editor und laufendes Spiel belegen Grafikspeicher; der GPU-Wächter erkennt Godot, schließt es nie.
