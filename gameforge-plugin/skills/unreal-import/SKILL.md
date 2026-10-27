---
name: unreal-import
description: Blender-Exporte in Unreal Engine 5 importieren, prüfen und in eine Testszene einbauen – für Spiele und Filme (Sequencer-Kulissen) – über den nativen Unreal-MCP (Server „Unreal“, Toolsets + VibeUE). Auch für Unreal-Gameplay- und Sequencer-Aufgaben.
---

# Unreal-Import

1. **Voraussetzungen prüfen**: Liegt ein Unreal-Projekt (`.uproject`) im Ordner `unreal/` des Spiels? Existiert der Export (`gf.cmd asset-pruefen "<Spiel>" --asset "<Name>"` → „Datei erstellt“)? Wenn nicht: zuerst Skill `blender-asset`.
2. **Verbindung (nativer Unreal-MCP)**: Unreal muss mit dem Projekt geöffnet sein (MCP-Server startet dann automatisch auf `127.0.0.1:8000/mcp`). Der MCP-Server „Unreal“ ist die GAMEFORGE-Brücke: Läuft Unreal nicht, startet sie es selbst. Gezielt mit Projekt: Werkzeug `unreal_starten` (`projekt` = Pfad zur .uproject). Danach `list_toolsets`. Meldet die Brücke einen Fehler, diesen wörtlich nennen – nichts als importiert melden.
   - Neues Projekt ohne Pflicht-Plugins: einmalig `py "C:/Users/manue/Documents/Unreal Projects/_Claude-Standard/claude_unreal_standard.py"` (per `execute_python_code` oder Unreal-Konsole), danach Editor-Neustart durch den Nutzer.
   - Ablauf: erst `list_toolsets`/`describe_toolset`, dann `call_tool`; Python nur über `execute_python_code` (`import unreal`). Größere Änderungen als **eine Undo-Transaktion** bündeln. Sichtbeleg mit `capture_image`.
   - Ohne offenen Editor (z. B. Stapelarbeit) ausnahmsweise: `UnrealEditor-Cmd.exe "<Projekt>.uproject" -run=pythonscript -script="<skript>.py" -unattended` – nie parallel zu einem offenen Editor desselben Projekts.
3. **Freigabe & Sicherheit**: Import, Löschen oder Überschreiben von Assets **nur nach Freigabe** durch den Nutzer; vorher Sicherung bzw. Git-Commit. Den Editor nie selbst beenden. Render-/Cook-/Build-Läufe (Movie Render Queue, Packaging) sind GPU-Schwerarbeit → vorher `gf.cmd gpu`, immer nur einer.
4. **Importieren** (Unreal zuerst: ersetzt einen `BLOCK_`-Platzhalter aus dem Blockout; Namen `SM_`/`SK_`/`M_`/`MI_`/`T_`, Kollision `UCX_`) nach `/Game/GAMEFORGE/<Asset>` (Pfad aus `blender/<Asset>/AUFTRAG.json`), nie bestehende Assets überschreiben. Prüfen: Maßstab (Unreal rechnet in cm – ein 1-m-Objekt ist 100 cm), Materialien, Normalen, Kollision, bei Figuren Skeleton/Animationen, LOD/Nanite je nach Stilprofil.
5. **Testszene**: Asset in einer Testmap platzieren, Screenshot/Log erstellen und dem Nutzer zeigen.
6. **Bericht** schreiben: `blender/<Asset>/QA_BERICHT.md` mit echten Prüfergebnissen und offenen Fehlern (Agent `gameforge:quality-testing`). Danach `gf.cmd asset-pruefen` → Stufe „getestet“. Freigabe gibt nur der Nutzer.

Gameplay-Programmierung, KI, Kampf: `gameforge:unreal-programming`, `gameforge:combat-enemy-ai`. Nie zwei Agenten gleichzeitig im Editor.
Windows-Spielversion bauen erst nach Zustimmung (dauert lange): RunUAT BuildCookRun → Ergebnis nach `export/`.
