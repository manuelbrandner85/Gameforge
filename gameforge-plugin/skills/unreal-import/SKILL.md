---
name: unreal-import
description: Fertige Blender-Exporte (.fbx) eines GAMEFORGE-Spiels in Unreal Engine 5 importieren, prüfen und in eine Testszene einbauen – über die Unreal-MCP-Verbindung (unreal-mcp). Auch für Unreal-Gameplay-Aufgaben im Spielprojekt.
---

# Unreal-Import

1. **Voraussetzungen prüfen**: Liegt ein Unreal-Projekt (`.uproject`) im Ordner `unreal/` des Spiels? Existiert der Export (`gf.cmd asset-pruefen "<Spiel>" --asset "<Name>"` → „Datei erstellt“)? Wenn nicht: zuerst Skill `blender-asset`.
2. **Verbindung prüfen**: die Werkzeuge des MCP-Servers `unreal-mcp` auflisten/aufrufen. Ist er nicht verbunden (Port 8000 geschlossen): dem Nutzer sagen: *Das Unreal-Projekt im Unreal Editor öffnen; das MCP-Plugin muss aktiv sein.* Danach erneut prüfen. Ohne Verbindung nichts als importiert melden.
3. **Werkzeuge nicht raten**: zuerst ansehen, welche Unreal-MCP-Werkzeuge es tatsächlich gibt, und nur diese verwenden.
4. **Importieren** nach `/Game/GAMEFORGE/<Asset>` (Pfad aus `blender/<Asset>/AUFTRAG.json`), nie bestehende Assets überschreiben. Prüfen: Maßstab (Unreal rechnet in cm – ein 1-m-Objekt ist 100 cm), Materialien, Normalen, Kollision, bei Figuren Skeleton/Animationen, LOD/Nanite je nach Stilprofil.
5. **Testszene**: Asset in einer Testmap platzieren, Screenshot/Log erstellen und dem Nutzer zeigen.
6. **Bericht** schreiben: `blender/<Asset>/QA_BERICHT.md` mit echten Prüfergebnissen und offenen Fehlern (Agent `gameforge:quality-testing`). Danach `gf.cmd asset-pruefen` → Stufe „getestet“. Freigabe gibt nur der Nutzer.

Gameplay-Programmierung, KI, Kampf: `gameforge:unreal-programming`, `gameforge:combat-enemy-ai`. Nie zwei Agenten gleichzeitig im Editor.
Windows-Spielversion bauen erst nach Zustimmung (dauert lange): RunUAT BuildCookRun → Ergebnis nach `export/`.
