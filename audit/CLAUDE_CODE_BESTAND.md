# Claude-Code-Bestand und Gesundheitsprüfung (Baseline)

**Stand:** 25.10.2026 · **Art:** nur lesend (Masterprompt V1.2, B2.1/B2.2) · **Werkzeug:** `gameforge_core/doctor.py --mcp`
**Rohdaten:** `audit/claude-config-inventory.json` (ohne Einstellungswerte, ohne Geheimnisse), `audit/claude-health-baseline.json` (inkl. SHA-256 aller 42 GENESIS-Canon-Dateien)

## 1. Was aktiv ist

| Bereich | Befund | Beleg |
|---|---|---|
| Claude Code | 2.1.309, `C:\Users\manue\.local\bin\claude`, `CLAUDE_CONFIG_DIR` nicht gesetzt (Standard `~/.claude`) | `claude --version` |
| Nutzer-Settings | `~/.claude/settings.json` gültig: Theme, Auto-Modus, Plugins, Marktplätze; **keine** Hooks, **keine** Rechte-Freigaben | JSON-Parser |
| Projekt-Settings GENESIS | `Genesis-Games/.claude/settings.json`: 2 PreToolUse-Hooks (Canon-/Push-Schutz, Installations-Schutz) | JSON-Parser + Probe |
| Desktop / GAMEFORGE / Trailer / AION | keine `.claude/settings*.json`, keine Agenten | Dateisuche |
| Verwaltete Richtlinien | keine gefunden | Dateisuche |
| Plugins | `gameforge@gameforge-lokal` 3.0.0 **aktiv** (20 Agenten, 10 Skills, keine Hooks/MCP); `vecom-analyse`, `vecom-3d` installiert, **deaktiviert** | `installed_plugins.json` |
| Agenten | GENESIS 24, GAMEFORGE-Plugin 20 – alle mit gültigem Frontmatter (`name`, `description`) | Frontmatter-Parser |
| Skills | GENESIS 36, Plugin 10, Nutzer 2 (`maximum-realism-visual-fidelity`, `reverse-engineer-anything`) – alle gültig | Frontmatter-Parser |
| MCP lokal | `blender` ✔ verbunden · `rea` ✔ verbunden · `unreal-mcp` ✘ **ECONNREFUSED** (Nutzer-Scope, `http://127.0.0.1:8000/mcp`) | `claude mcp list` |
| MCP claude.ai | Docs, Gmail, Drive, Netlify, Supabase, Supermetrics, Higgsfield ✔; HeyGen, Canva, Amplitude, Cloudflare „Needs authentication“ | `claude mcp list` |
| Unreal-Fernsteuerung | `bRemoteExecution=True` (Genesis), `tools/v4/g4/ue_remote.py` über Python-Remote-Execution – heute über 100-mal erfolgreich genutzt | Sitzungsprotokoll |

## 2. Funde

| ID | Grad | Fund | Beleg / Test | Ursache |
|---|---|---|---|---|
| H-01 | **WARN** | GENESIS-Schutzhooks (Canon, Push, Installationen) greifen **nur**, wenn Claude Code im Ordner `Genesis-Games` gestartet wird. Sitzungen ab `Desktop` (diese, die Trailer-Sitzung) arbeiten ohne diesen Schutz. | Hooks isoliert geprüft: blockieren korrekt mit Exit 2; in dieser Desktop-Sitzung liefen `git push` ohne Hook | Projekt-Settings gelten nur für die Projektwurzel der Sitzung |
| H-02 | **WARN** (Regelkonflikt) | `claude_pretool_guard.py` sperrt **jeden** `git push`; die gespeicherte Nutzerregel sagt „GENESIS-Commits immer pushen“. | Probe `git push -q origin v4/neustart` → Exit 2 | zwei Regeln aus verschiedenen Zeitpunkten |
| H-03 | **WARN** | `unreal-mcp` ist im Nutzer-Scope eingetragen, aber kein Unreal-MCP-Server existiert (kein MCP-Plugin im Projekt, Port 8000 leer). Bei jedem Sitzungsstart Fehlermeldung. | `claude mcp get unreal-mcp`, Plugin-/Portsuche | verwaister Eintrag; funktionierender Ersatz ist die Python-Remote-Execution |
| H-04 | **WARN** | Parallele Sitzungen teilen sich eine GPU (12 GB), ein Blender und Unreal-Instanzen: heute VRAM-Erschöpfung (Unreal „1868 MB over budget“), eine fremde Sitzung hat die offene Blender-Datei umgespeichert, Remote-Aufrufe kollidierten am Port 6776. | Logs/Screenshots dieser Sitzung | kein gemeinsames Ressourcen-Lock |
| H-05 | INFO (behoben) | Remote-Execution-Portkollision zwischen zwei Sitzungen | `ue_remote.py` wählt seit Commit `428a8a9` (Genesis) einen freien Port | – |
| H-06 | INFO | `melt.exe` hängt ohne Ausgabe, wenn nicht im Ordner `Kdenlive\bin` gestartet | Smoke-Test | DLL-Suchpfad; Adapter setzt den Arbeitsordner |
| H-07 | INFO | Audacity 4.0.1 hat kein `mod-script-pipe` → keine Fernsteuerung | Dateisuche | neue Audacity-Generation; Fallback FFmpeg (getestet) |
| H-08 | INFO | Cloud-Konnektoren (Higgsfield, HeyGen usw.) sind im Konto vorhanden. Für GAMEFORGE gilt: nicht verwenden (Regel 1 – keine zusätzlichen/kostenpflichtigen KI-Dienste). | `claude mcp list` | Kontoeinstellungen |
| H-09 | INFO | GAMEFORGE-Bericht vom 17.10. meldete „Claude nicht angemeldet“ – heute angemeldet, MCP-Liste lädt | `claude mcp list` | erledigt |

**Keine** `CRITICAL`- und **keine** `ERROR`-Funde. Canon-Hashes als Baseline gesichert; Genesis-Repo auf `v4/neustart` mit offenen Änderungen der laufenden C00-Sitzung (nicht von dieser Prüfung).

## 3. Gate-Status

- **Film-/Spiel-Pipeline:** `READY mit Auflagen`. Pflichtwerkzeuge erreichbar und getestet (siehe `setup/INSTALLATIONSBERICHT.md`). Offene WARN H-01 bis H-04 betreffen Schutz und Parallelbetrieb, nicht die Funktion.
- Vor produktiven GENESIS-Jobs aus einer Desktop-Sitzung: H-01 lösen oder die Sitzung in `Genesis-Games` starten.
