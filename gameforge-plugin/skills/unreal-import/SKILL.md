---
name: unreal-import
description: Blender-Exporte in Unreal Engine 5 importieren, prüfen und in eine Testszene einbauen – für Spiele und Filme (Sequencer-Kulissen) – Claude steuert Unreal direkt über PowerShell und Unreal-Python (ohne MCP). Auch für Unreal-Gameplay- und Sequencer-Aufgaben.
---

# Unreal-Import

1. **Voraussetzungen prüfen**: Liegt ein Unreal-Projekt (`.uproject`) im Ordner `unreal/` des Spiels? Existiert der Export (`gf.cmd asset-pruefen "<Spiel>" --asset "<Name>"` → „Datei erstellt“)? Wenn nicht: zuerst Skill `blender-asset`.
2. **So wird Unreal gesteuert (kein MCP)**: Claude schreibt ein Unreal-Python-Skript (`unreal`-Modul, z. B. `AssetImportTask`, `EditorAssetLibrary`) und startet es per PowerShell ohne Fenster:
   `& "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "<Projekt>.uproject" -run=pythonscript -script="<skript>.py" -unattended -nosplash`
   Ergebnis nur aus Log/Exitcode und geprüften Dateien melden – ohne Nachweis nichts als importiert melden.
3. **Offener Editor**: Ist dasselbe Projekt gerade im Unreal Editor offen, nicht parallel ohne Fenster öffnen – den Nutzer bitten zu speichern und zu schließen, oder den Schritt später machen. Den Editor nie selbst beenden. Render-/Cook-/Build-Läufe sind GPU-Schwerarbeit → vorher `gf.cmd gpu`, es läuft immer nur einer.
4. **Importieren** nach `/Game/GAMEFORGE/<Asset>` (Pfad aus `blender/<Asset>/AUFTRAG.json`), nie bestehende Assets überschreiben. Prüfen: Maßstab (Unreal rechnet in cm – ein 1-m-Objekt ist 100 cm), Materialien, Normalen, Kollision, bei Figuren Skeleton/Animationen, LOD/Nanite je nach Stilprofil.
5. **Testszene**: Asset in einer Testmap platzieren, Screenshot/Log erstellen und dem Nutzer zeigen.
6. **Bericht** schreiben: `blender/<Asset>/QA_BERICHT.md` mit echten Prüfergebnissen und offenen Fehlern (Agent `gameforge:quality-testing`). Danach `gf.cmd asset-pruefen` → Stufe „getestet“. Freigabe gibt nur der Nutzer.

Gameplay-Programmierung, KI, Kampf: `gameforge:unreal-programming`, `gameforge:combat-enemy-ai`. Nie zwei Agenten gleichzeitig im Editor.
Windows-Spielversion bauen erst nach Zustimmung (dauert lange): RunUAT BuildCookRun → Ergebnis nach `export/`.
