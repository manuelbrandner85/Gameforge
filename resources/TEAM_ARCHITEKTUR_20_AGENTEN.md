# GAMEFORGE GODMODE – Studio-Agenten-Architektur

Version 0.9 · Oktober 2026 · Status: verbindlich genehmigtes Rollenmodell, erste lokale Konfigurationsimplementierung.

## Ziel und Grenzen

Ein Master-Agent plant und koordiniert 19 spezialisierte Claude-Code-Subagents. GAMEFORGE verwaltet AION 2026, GENESIS und je Spiel eigene DLCs. GAMEFORGE erzeugt Story-, Referenz- und Produktionseingaben, exportiert sie oder verbindet einen echten lokalen Projektordner. Claude Code steuert Blender und Unreal mithilfe vom Nutzer eingerichteter MCP-Server. Ein freigegebenes Spiel entsteht **erst** nach realem Build, Playtest und QA-Freigabe. Keine Agentendefinition allein erstellt ein Spiel.

### Architektur

Du → GAMEFORGE Ideen-Chat / Claude Desktop Code (Local) → Claude-Hauptsitzung (operative Studioleitung) → bei Bedarf Studio Director Agent → jeweils zuständige Subagents → Blender/Unreal-MCP (je nach Rolle) → Testbeweise → GAMEFORGE-Bibliothek / Versionsarchiv.

**Die Desktop-App bietet Subagents/Dynamic Workflows innerhalb einer Sitzung. Experimentelle Agent Teams (mehrere eigenständige Team-Sitzungen) sind zurzeit nur über die CLI verfügbar.** Die hier mitgelieferten Dateien nutzen daher das reguläre Subagent-System.

**Keine vorgetäuschte Desktop-Integration:** GAMEFORGE Direkt-Studio v0.9 ruft für eigene Aufträge die lokale `claude`-CLI auf. Dieser Ablauf ist eine separate Claude-Sitzung, nicht dieselbe laufende Unterhaltung in der Claude-Desktop-App. Die 20 Agenten sind projektlokal in beiden Umgebungen lesbar, sofern Claude Code die Dateien im gewählten Ordner lädt.

### Projekt-Abgrenzung

- `aion-2026`: Hauptspiel-AION. Seine Dateien, Story und DLCs isoliert verwalten.
- `genesis`: Hauptspiel-GENESIS. Keine implizite Übernahme von AION-Daten.
- DLC: Jedes DLC bleibt mit `game_id` und `dlc_id` eindeutig seinem Basisspiel zugeordnet; Referenzen, Story, Basisversions-Kompatibilität und Tests getrennt führen.
- Die in GAMEFORGE vorbelegten Daten sind Konzepte, keine importierten Original-UE-Projekte oder fertigen Builds.

## Die 20 festen Rollen

| Agent | Lieferobjekt | Zugriff | Fachliche Verantwortung |
|---|---|---|---|
| 01 Studio Director | Arbeitsaufträge/Abnahmereports | Lesen/Agent | Masterkoordination |
| 02 Game Design Director | Spielregeln/Design-Dokumente | Dateien | Gamedesign und neue Ideen |
| 03 Story & Narrative | Szenen/Storyverzweigungen | Dateien | Story, Prolog, Enden |
| 04 Mission & Quest | Quests und State Machines | Dateien | Missionen, Deadlock-Checks |
| 05 Character & Boss | Charakter-/Boss-Sheets | Dateien | Figuren und Bossphasen |
| 06 Reference Director | Bildprompts/Referenzkatalog | Dateien | Externe ChatGPT-Referenzbilder |
| 07 World Building | Weltatlas/PCG-Plan | Dateien | Welten, Regionen, Biome |
| 08 Blender 3D | .blend/3D-Asset-Berichte | Blender MCP | Modellbau/UV/LOD |
| 09 Animation & Rigging | Rig-/Anim-Bibliothek | Blender MCP | Animationen/Retargeting |
| 10 Materials & Visual | PBR/Shader-/Bildprüfung | Blender + Unreal MCP | Materialien/Rendering |
| 11 Unreal Programming | C++-/Blueprint-Artefakte | Unreal MCP | UE-Framework/Code |
| 12 Combat & Enemy AI | kampf- und KI-fähige Module | Unreal MCP | Kampf/Gegnerverhalten |
| 13 Physics & Vehicle | Physiktests/Fahrzeugsysteme | Unreal MCP | Chaos/Kollisionen |
| 14 Cinematic Director | Sequencer/Timecodes | Unreal MCP | Prolog/Cutscenes |
| 15 UI & Menu | Widget-/UX-Tests | Unreal MCP | UI/HUD/Menüs |
| 16 Sound & Dialogue | Audio-IDs/Cues/Lizenzen | Dateien | Audio/Sprachplanung |
| 17 Game Systems | Savegame-/Inventar-Code | Unreal MCP | Persistenz/Spielmechaniken |
| 18 Performance | Profilergebnisse | Unreal MCP | FPS/VRAM/Streaming |
| 19 Quality & Testing | reale QA-Evidenz | lokale Tests | Abnahme/Fehleranalyse |
| 20 DLC & Release | DLC-/Release-Manifest | lokale Buildtools | DLC/Packaging |

*Dateizugriff ist keine Sicherheits-Sandbox; die Agenten erhalten nur die in ihrer Frontmatter angegebenen Tools. Lokal gestartete Prozesse und weitere geteilte Sitzungsrechte müssen zusätzlich durch Claude Desktop/CLI-Berechtigungen, Worktrees und Backups abgesichert werden.*

## Delegationsregeln

1. Jedes Arbeitspaket erhält Projekt-ID, optional DLC-ID, eindeutige Task-ID, Eingabedateien, Spezifikation und akzeptierte Anforderungen.
2. Hauptsitzung lädt nur relevante Informationen; keine vollständigen Project-Bibles an jeden Agenten bei jeder Aktion senden.
3. Story- und Gamedesign-Aufträge zuerst klären; fehlende ChatGPT-Referenzbilder als echte Blocker kennzeichnen.
4. Blender erstellt Assets unter stabilen IDs; Unreal integriert und prüft sie erst danach. Keine parallelen Änderungen am selben Editorprojekt.
5. Unreal MCP führt Editor-Tool-Calls seriell aus (Engine-Thread). Parallele Agenten dürfen an getrennten Dokumentationen oder Git-Worktrees arbeiten, nicht gleichzeitig denselben Live-Editor verändern.
6. Nach jeder Änderung schlägt der zuständige Agent Tests vor; unabhängiger QA-Agent prüft tatsächlich vorliegende Artefakte und Buildlogs.
7. Nur geprüfte, akzeptierte Änderungen wandern als neuer Projektstand ins Versionsarchiv. Kein autonomer Release ohne Nutzerfreigabe.

## Beispielauftrag: AION – Poseidon-Boss

| Schritt | Agent | Ausgabe | Freigabe/Prüfung |
|---|---|---|---|
| 1 | Studio Director | Auftrag, Abhängigkeiten, Game-Bible-Referenzen | Projekt eindeutig |
| 2 | Story & Narrative + Mission & Quest | Storyanknüpfung, Quest-Stati, Trigger | keine Logik-Sackgassen |
| 3 | Character & Boss | Boss-Design, drei Kampfphasen, Maßstab | Gameplay-Vorgaben genehmigt |
| 4 | Reference Director | Front/Seite/Rückseite, Tempel, Waffe, Pose-Prompts | ChatGPT-Bilder importiert + freigegeben |
| 5 | Blender 3D + Animation | Mesh, UV, Rig, Animation | echte .blend-Dateien, Sichtprüfung |
| 6 | Unreal Programming, Combat & AI | Combat, Levelintegration, Boss-AI | Build/Gameplay-Tests |
| 7 | Cinematic Director + Sound & Dialogue | Intro, Effekte, Dialog und Audio | Trigger/Timing/Untertitel |
| 8 | Performance + Quality & Testing | Performance-Messung, Regression, offene Bugs | QA-Gate oder Fehlerliste |
| 9 | DLC & Release (erst bei Release) | Build und archivierte Projektdaten | manueller Release-Gate |

## Claude-App und Handy

- **Windows:** In Claude Desktop den Tab **Code**, Umgebung **Local**, korrekten AION- oder GENESIS-Ordner wählen. Die projektbezogenen Dateien unter `.claude/agents/` werden von Claude Code geladen. Falls sie in einem vorher nicht existierenden Agentenordner erst während der Sitzung entstanden sind, Claude-Code-Sitzung neu starten.
- **Echtes Editor-MCP:** Unreal Engine muss lokal laufen; UE 5.8 Unreal MCP und All Toolsets aktivieren, im Editor `ModelContextProtocol.GenerateClientConfig ClaudeCode` ausführen. Prüfen, dass `.mcp.json` im ausgewählten Projektordner auf den korrekten lokalen MCP-Endpunkt zeigt. Blender-MCP separat passend zur Installation konfigurieren, benenne den Server `blender` oder passe die Agentdateien an.
- **Telefon:** In Claude Mobile eine unterstützte Desktop-Local-Sitzung über Remote Control bedienen. Der Rechner mit Unreal und Blender bleibt eingeschaltet. Eine reine Cloud-Sitzung besitzt keinen automatischen Zugang zu lokalen 127.0.0.1-MCP-Servern.
- **Claude Code CLI:** Alternativ im Projektordner eine separate Claude-CLI-Sitzung nutzen. Bei eigenem `claude -p`-Start durch GAMEFORGE entstehen nicht automatisch die gleichen Desktop-Chat-Verläufe.

## Sicherheitskontrollen

- Standardmäßig Manual-Modus und individuelle Freigaben. `--dangerously-skip-permissions`, `bypassPermissions` oder pauschales Freigeben von Shellbefehlen sind nicht Teil dieser Installation.
- MCP für Kreativ- und Planungsteams gesperrt. Unreal/Blender-Agenten erhalten nur jeweils deklarierte Servernamen, zusätzlich gelten Claude Codes Eltern-/Benutzerrechte.
- Keine geheimen Zugangsdaten, API-Tokens oder fremden personenbezogenen Daten in exports, Cloud oder Logs.
- Keine automatische Installation von MCP-Servern auf dem PC: die Konfiguration bleibt explizit und überprüfbar.
- Agenten müssen echte Dateien und Prüfberichte nennen; fehlende Assets bleiben offen.

## Bereitgestellte Dateien

In GAMEFORGE unter **KI-Agenten (20)**:
- **Agenten-ZIP herunterladen** für Hauptspiel oder DLC: `.claude/agents/*.md` und `GAMEFORGE_AGENT_RULES.md`, `GAMEFORGE_AGENTS_START_HIER.md`, Projekt-ID-Metadaten.
- **Agenten installieren** schreibt diese Dateien in den zuvor verbundenen lokalen Projektordner, nur wenn keine Zieldateien existieren. Bestehende `CLAUDE.md` bleibt unberührt.
- Auch jedes normale Claude-Code-Produktionspaket enthält die Agentendateien zusätzlich unter `AGENT_STUDIO/`.

## Validierungsstufen

1. **Konfiguriert:** 20 Dateien auf Platte und valide Claude-Code-Frontmatter.
2. **Verfügbar:** Claude Desktop erkennt die Rollen in einer Code-Local-Sitzung.
3. **Verbunden:** Der jeweilige Agent sieht passende MCP-Tools.
4. **Funktional getestet:** Blender und Unreal führen jeweils eine nicht-destruktive Testaktion aus.
5. **Produktion:** Reale Asset- und Gameplay-Arbeit; Build und QA separat.

GAMEFORGE v0.9 erreicht in automatischen Tests Stufe 1. Stufen 2–5 erfordern Tests auf dem Windows-PC des Nutzers.
