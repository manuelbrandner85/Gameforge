# Bekannte Fallen (Unreal 5.8 + Blender 5.2 über MCP) – geprüft am 27.10.2026

Vor Unreal-/Blender-Arbeit lesen. Jede Falle ist echt aufgetreten; die Lösung ist getestet.

## Unreal – Materialien (Python/MCP)
- **Partikelfarbe-Alpha:** `MaterialExpressionParticleColor` – Standardausgang ist RGB (float3). Alpha über den Ausgang `"A"` verbinden (`connect_material_expressions(pc, "A", …)`), **nicht** per ComponentMask. Sonst: „Not enough components … component mask 0001“ und Unreal zeigt das karierte Ersatzmaterial.
- **„Kompiliert erfolgreich“ heißt nichts:** `recompile_material`/`compile_material` melden auch dann Erfolg. Immer im Log `Saved/Logs/<Projekt>.log` nach `Failed to compile Material` suchen – die Zeile darunter nennt den Knoten.
- `MaterialExpressionRadialGradientExponential` gibt es nicht (ist eine Materialfunktion) – radialen Verlauf aus TexCoord/Length/OneMinus/Power selbst bauen.
- Kariertes Ersatzmaterial auf einer **Landschaft** trotz fehlerfreiem Material: Level speichern und neu laden (`save_current_level` + `load_level`) – erst dann baut Unreal die interne Landschafts-Materialinstanz neu.

## Unreal – Niagara
- Im **Editor-Viewport laufen Partikel nach `reinitialize_system` nicht weiter**, wenn der Viewport nicht in Echtzeit läuft. Für Sichtprüfung kurz `LevelEditorSubsystem.editor_play_simulate()` starten, ein paar Sekunden warten, `capture_image`, danach `editor_request_end_play()`.
- Lightweight-Vorlagen (`…Lightweight`) haben keine bearbeitbaren Renderer – Standard-Emitter (z. B. `Fountain`) per `AddEmitter` nehmen.
- Werte bequem über `unreal.NiagaraService.set_rapid_iteration_param(system, emitter, "Constants.<Emitter>.<Modul>.<Input>", "<Wert>")` setzen und mit `list_rapid_iteration_params` zurücklesen. Renderer-Material per Toolset `SetRendererData` (`propertyValues` als JSON-String), zurücklesen mit `GetRendererData`.
- Emitter-Verweise brauchen alle Felder: `{"system":{"refPath":…},"emitterName":…,"scriptName":"","moduleName":"","rendererIndex":-1|0,"inputNameStack":[]}`.

## Unreal – PCG
- Graph per Python bauen (`PCGGraph.add_node_of_type`, `add_edge`) – die Toolset-Knotennamen sind eingedeutscht.
- `add_edge` meldet auch bei **falschem Pin-Namen** Erfolg. Pins prüfen: Dichtefilter-Ausgang heißt `Out` (nicht „In Filter“), Oberflächen-Sampler-Eingang `Surface`, Differenz `Source`/`Differences`.
- Ergebnis immer nachzählen (Instanzen der `InstancedStaticMeshComponent`s am PCG-Volumen) und Zwischenstände mit `GetNodeDataView` prüfen.
- `mesh_selector_parameters` ist ein eingebettetes Objekt: Einträge direkt am Objekt setzen, nicht neu zuweisen.
- Freihalten (z. B. um ein Lagerfeuer): `TriggerVolume` (keine Kollision) mit Tag + `GetVolumeData` (BY_TAG) + `Difference`.

## Unreal – Sonstiges
- Werte an platzierten Actors über Python (`set_editor_property`, `set_intensity` …) funktionieren – **immer zurücklesen**.
- Scheite/Objekte mit Pivot in der Mitte drehen sich um die Mitte: Position aus unterem Ende + halber Länge entlang der Neigung berechnen.
- `get_editor_world`/`editor_set_game_view` aus `EditorLevelLibrary` sind veraltet → `UnrealEditorSubsystem`/`LevelEditorSubsystem`.

## Blender
- Blender **sichtbar** starten (Nutzerwunsch); MCP-Port 9876 per Verbindungsversuch prüfen – `netstat`-Ausgabe ist deutsch („ABHÖREN“) und bricht naive Filter.
- Hintergrund-Variante (`execute_blender_code_for_cli`) hat ein Zeitlimit von 120 s – große Aufgaben in mehrere Aufrufe teilen.
- Icosphere mit Radius 1 hat Durchmesser 2 – Maße danach messen und melden.

## Windows / Werkzeuge
- Der Unreal-MCP läuft über die GAMEFORGE-Brücke (`gameforge_core/unreal_mcp_bridge.py`); Protokoll in `GAMEFORGE_DATA/logs/unreal_mcp_bridge.log`.
