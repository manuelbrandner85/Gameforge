---
name: blender-asset
description: 3D-Modelle für ein Spiel oder einen Film in Blender erstellen (Figuren, Bosse, Waffen, Rüstungen, Gebäude, Fahrzeuge, Props, Kulissen) über die Blender-MCP-Verbindung, als .blend speichern, als .fbx exportieren und prüfen.
---

# Blender-Asset erstellen

Werkzeug: `gf.cmd` (Pfad siehe Skill `gameforge-studio`). Zusätzlich den Skill `maximum-realism-visual-fidelity` laden (Qualitätsanspruch; bei stilisierten Spielen im Stil des Spiels).

0. **Unreal zuerst (Standard)**: Gibt es den Blockout/Platzhalter (`BLOCK_<Name>`) schon und die Maßliste in cm? Lösen Fab/Megascans, PCG oder Niagara das Problem bereits? Dann **nicht** in Blender bauen. Ausnahme: Hero-Assets (Hauptfiguren, Story-Objekte, zentrale Bauwerke, Stil-Tests). Maße aus dem Blockout übernehmen (1 UE = 1 cm, Z oben, X vorwärts, Pivot am Aufstellpunkt).
1. **Verbindung prüfen**: ein lesendes Blender-Werkzeug aufrufen (`mcp__blender__get_objects_summary`). Antwortet Blender nicht („Cannot connect to Blender at localhost:9876“): dem Nutzer genau sagen: *Blender öffnen → Bearbeiten → Einstellungen → Add-ons → „MCP“ → Server starten (optional „Autostart“ anhaken).* Dann erneut prüfen. Ohne Verbindung **nichts** als erstellt melden.
2. **Auftrag anlegen**: `gf.cmd blender-auftrag "<Spiel>" --asset "<Name>" --art <art> --details "<…>" --masse "<z. B. 2,1 m hoch>"`. Er enthält Stil, Polygon-/Texturbudget, Rigging- und Exportvorgaben und die freigegebenen Referenzen (`referenzen/freigegeben/<Asset>/`). Referenzbilder mit dem Read-Werkzeug ansehen.
3. **Modellieren** mit den Blender-Werkzeugen: Szene zuerst untersuchen, nichts Bestehendes zerstören, Meter/Scale 1.0, reale Maße, saubere Topologie, UVs, Materialien im Stil des Spiels; bei Figuren Rig nach Auftrag. Größere Arbeit an `gameforge:blender-3d` (danach ggf. `gameforge:materials-visual`, `gameforge:animation-rigging`) übergeben.
4. **Speichern und exportieren** genau an die Pfade aus `AUFTRAG.json` (`blender/<Asset>/<Asset>.blend`, `export/<Asset>/<Asset>.fbx`, FBX mit „FBX Units Scale“, Add Leaf Bones aus).
5. **Sichtprüfung**: Vorschaubild rendern (`render_viewport_to_path` nach `blender/<Asset>/vorschau.png`), ansehen und dem Nutzer zeigen.
6. **Nachweis**: `gf.cmd asset-pruefen "<Spiel>" --asset "<Name>"` – erst bei „Datei erstellt“ als erstellt melden. Grenzen offen nennen (z. B. Feinheiten, die manuell nachgearbeitet werden sollten).
7. Namen nach Standard: Mesh `SM_<Name>` (Skelett `SK_`), Materialien `M_`/`MI_`, Texturen `T_<Name>_D/_N/_ORM`, Kollision `UCX_SM_<Name>`.
8. Speicher schonen: Hat Claude Blender nur für dieses Objekt geöffnet, Blender nach dem Speichern schließen. Vom Nutzer geöffnetes Blender nie schließen.
9. Nächster Schritt anbieten: Skill `unreal-import` (Import nur nach Freigabe).

Schneller Funktionstest ohne MCP: `gf.cmd blender-test` (Blender im Hintergrund, echter .blend/.fbx-Export).
