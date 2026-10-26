# STANDARD-SETUP & ARBEITSWEISE – ALLE SPIELE UND FILME (Unreal + Blender + Claude)

> Verbindlicher Standard von Manuel (übernommen am 26.10.2026). Gilt für alle Spiele und Filme, auch künftige Projekte, inkl. GENESIS.
> Projektspezifische Regeln (z. B. Kanon-, Freigabe- und Repo-Schutzregeln von GENESIS) haben bei Konflikten Vorrang.

## 1. Technische Umgebung (bereits eingerichtet)
- Unreal Engine 5.8.4 (Windows), Blender 5.2, PC mit 32 GB RAM.
- Unreal ist per **nativem Unreal MCP** mit Claude verbunden: Endpoint `http://127.0.0.1:8000/mcp`, Server startet automatisch beim Öffnen jedes Projekts (benutzerweit in `Dokumente\Unreal Engine\Engine\Config\UserEditorPerProjectUserSettings.ini`: `bAutoStartServer=True`).
- In der Claude-Desktop-App ist der lokale MCP-Server „Unreal“ eingetragen: command `cmd`, args `["/c","npx","-y","mcp-remote","http://127.0.0.1:8000/mcp"]`. Blender ist ebenfalls per MCP verbunden.
- **VibeUE** (Fab, in Engine 5.8 installiert) erweitert den Unreal-MCP um ~35 Dienste: Landscape, Foliage, Map Blockout, Animation, Niagara-Tiefe, MetaSound/SoundCue, UMG/MVVM, StateTree, Performance-Messung, Undo-Transaktionen, Python-Ausführung.
- Unreal muss mit einem Projekt geöffnet sein, damit die KI es steuern kann.
- **GAMEFORGE-Unreal-Brücke (seit 27.10.2026)**: Der MCP-Server „Unreal“ in Claude Code und in der Claude-App ist `gameforge_core/unreal_mcp_bridge.py`. Sie ist immer verbunden und leitet 1:1 an den nativen Unreal-MCP inkl. VibeUE weiter. Läuft Unreal nicht, startet sie es beim ersten Unreal-Werkzeug automatisch mit dem passenden Projekt (oder gezielt mit dem Werkzeug `unreal_starten`, Argument `projekt`) und verbindet sich neu – kein Neustart in der Claude-App nötig.
- **Unreal öffnen/schließen**: Öffnen übernimmt die Brücke (Bildschirmsteuerung nur noch als Notlösung). Schließen ebenfalls per Bildschirmsteuerung, vorher alles per MCP speichern. Bildschirmsteuerung nur zum Öffnen/Schließen – alle eigentliche Arbeit in Unreal per MCP. (Ein vom Nutzer geöffnetes Unreal schließt die KI nicht ungefragt.)

## 2. Pflicht-Plugins in JEDEM Unreal-Projekt
- Editor-only (`TargetAllowList ["Editor"]`): PythonScriptPlugin, EditorScriptingUtilities, ModelContextProtocol, ToolsetRegistry, EditorToolset, AllToolsets, VibeUE
- Runtime: PCG, Niagara, Metasound, MovieRenderPipeline
- Neues Projekt einrichten (einmalig, dann Editor neu starten), in der Unreal-Konsole oder per MCP:
  `py "C:/Users/manue/Documents/Unreal Projects/_Claude-Standard/claude_unreal_standard.py"`
  Das Skript schaltet die Plugins ein, sichert vorher die .uproject unter `Saved\`, ergänzt die CLAUDE.md um diesen Standard (ohne etwas zu löschen) und startet den MCP-Server.

## 3. Grundregel: Unreal zuerst, Blender danach
1. **In Unreal blocken**: Spiele = Level/Gameplay mit Platzhaltern (`BLOCK_<Name>`) bauen und anspielen, bis Abstände, Tempo, Sichtlinien stimmen. Filme = Szene, Kamera und Timing im Sequencer als Animatic blocken, bevor Details gebaut werden.
2. **Vorhandenes nutzen**: Fab/Megascans, Landscape, Foliage, PCG für große Flächen und Variation.
3. **Fehlendes in Blender**: nur Objekte bauen, die danach noch fehlen – in den Maßen aus dem Blockout (vorher Liste mit Maßen in cm). Ausnahme: Hero-Assets (Hauptfiguren, Story-Objekte, zentrale Bauwerke, Stil-Tests) dürfen früh entstehen.
4. **Import in Unreal**, Platzhalter ersetzen; Licht, Post-Process und Look zum Schluss.
Vor jedem Blender-Auftrag prüfen, ob PCG, Niagara oder Fab das Problem schon lösen.

## 4. Standardwerkzeuge
- **PCG**: Verteilung/Variation (Wälder, Felsen, Streuobjekte, Ränder).
- **Niagara**: alle Effekte (Feuer, Rauch, Staub, Magie, Wetter).
- **MetaSound**: prozeduraler Ton und Ambience.
- **Sequencer + Movie Render Queue**: Cinematics und Filme; finale Bilder nur über Movie Render Queue.

## 5. Konventionen Blender ↔ Unreal
- 1 Unreal-Einheit = 1 cm; Z oben, X vorwärts; Pivot dort, wo das Objekt in der Welt steht.
- Präfixe: `SM_` Static Mesh, `SK_` Skeletal Mesh, `M_` Material, `MI_` Material-Instanz, `T_` Textur (`_D`, `_N`, `_ORM`), `BP_` Blueprint, `NS_` Niagara-System, `LS_` Level Sequence, `UCX_` Kollision, `BLOCK_` Platzhalter.

## 6. Arbeitsregeln für die KI
- In Unreal: erst Tools/Skills entdecken (`list_toolsets` / `describe_toolset`), dann aufrufen. Größere Editor-Änderungen als **eine Undo-Transaktion** bündeln.
- Vor großen Änderungen Sicherung bzw. Git-Commit; **nie Assets importieren, löschen oder überschreiben ohne Manuels Freigabe**.
- Performance-Probleme erst mit VibeUE PerformanceService messen (CPU- vs. GPU-gebunden, Insights-Trace), dann gezielt optimieren. Speicher schonen: Blender nur öffnen, wenn ein Objekt gebaut wird, danach schließen; Instancing/Nanite statt schwerer Einzelmeshes.
- Nichts als „fertig“ melden ohne echten Test im Editor bzw. Build. Berichte auf Deutsch.

## 7. Projekte
- GENESIS: `C:\Users\manue\Desktop\Genesis-Games` (Git-Repo manuelbrandner85/Genesis-Games, Branch v4/neustart). Eigene CLAUDE.md mit Kanon-, Freigabe- und Schutzregeln hat Vorrang. Vorlage für neue Spiele: `templates/new_game/Genesis.uproject` (enthält die Pflicht-Plugins).
- PANTHEON, C00_AssetDepot (Asset-Depot für GENESIS C00), UEIntroProject: `C:\Users\manue\Documents\Unreal Projects\` – alle mit Pflicht-Plugins und Autostart.

## 8. Unreal-Wachhund (Windows-Aufgabe)
Beendet alle 2 Minuten hängende Unreal-SDK-Prüfungen (cmd.exe mit ValidatePlatforms > 2 Min). Seit 15.10.2026 kein Eingriff nötig, daher pausierbar. Steuerung: `Dokumente\Unreal Wachhund\wachhund-ausschalten.cmd` / `wachhund-einschalten.cmd`. Wieder einschalten, wenn Unreal beim Start minutenlang im Ladebildschirm hängt.

## Ergänzung durch GAMEFORGE (kein Widerspruch zum Standard)
- GPU-Schwerarbeit (Movie Render Queue, Blender-Render, Bild-KI, Twinmotion) läuft über den Smart GPU Commander (`gf gpu`): immer nur ein Schwerjob, offene Editoren werden nie geschlossen, Final-Qualität wird nie still gesenkt.
- Twinmotion nur zur Vorvisualisierung, nie als Final-Renderer.
- Blender wird immer **sichtbar** geöffnet (normal starten, keine Bildschirmsteuerung) und über den Blender-MCP im Fenster bedient, damit Manuel zusehen kann.
