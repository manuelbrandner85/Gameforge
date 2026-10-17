# GAMEFORGE 2.0 – Dein KI-Spielestudio

GAMEFORGE läuft komplett auf deinem PC. Du beschreibst dein Spiel in normaler Sprache, GAMEFORGE plant es mit dir, verteilt die Arbeit an ein Team aus 20 KI-Agenten (Claude Code) und zeigt dir ehrlich, was wirklich fertig ist.

---

## 1. Installation und erster Start

1. Das ZIP in einen **neuen, leeren Ordner** entpacken, z. B. `C:\GAMEFORGE_2_0`.
2. Doppelklick auf **`START_GAMEFORGE_WINDOWS.bat`**.
3. Der Browser öffnet sich mit GAMEFORGE. Das schwarze Fenster offen lassen – es ist der GAMEFORGE-Server. Zum Beenden das Fenster schließen oder dort Strg+C drücken.

**Python:** GAMEFORGE braucht Python 3.11 oder neuer. Die Startdatei sucht es automatisch:
1. eine normale Python-Installation, sonst
2. das **in Blender mitgelieferte Python** (auf deinem PC: Blender 5.2 → Python 3.13).
Du musst also nichts zusätzlich installieren, solange Blender installiert ist.

## 2. Deine bisherigen Daten (AION, GENESIS, DLCs) übernehmen

1. Alte GAMEFORGE-Version **beenden**.
2. Den kompletten Ordner **`GAMEFORGE_DATA`** aus dem alten GAMEFORGE-Ordner in den neuen Ordner (neben `app.py`) **kopieren** – nicht verschieben.
3. GAMEFORGE 2.0 starten.

Beim ersten Start mit alten Daten legt GAMEFORGE automatisch eine Sicherung der Datenbank an:
`GAMEFORGE_DATA\backups\vor_migration_v2_<Datum>.sqlite3`.
Die Aktualisierung ergänzt nur neue Felder und Tabellen – es wird nichts gelöscht oder überschrieben. Die alte Version 1.0 kann die Datenbank danach weiterhin öffnen.
**Rückweg:** GAMEFORGE schließen, die Sicherungsdatei nach `GAMEFORGE_DATA\gameforge.sqlite3` zurückkopieren.

## 3. Die fünf Bereiche

| Bereich | Wofür |
|---|---|
| **Startseite** | Begrüßung, „Weiter an … arbeiten“, echter Stand jedes Projekts, nächste sinnvolle Schritte, Prüfung von Claude/Blender/Unreal |
| **Meine Spiele** | Bibliothek mit Suche und Statusfilter, Projektübersicht („Was ist die Idee? Was ist wirklich gebaut? Was fehlt? Was jetzt?“), DLCs, Versionen, **Spiel löschen** und **Papierkorb** |
| **Kreativstudio** | Ideen & Entscheidungen aus dem Chat, Spielbibel (Story, Missionen, Figuren, Welt …), Referenzbilder mit kopierbaren ChatGPT-Prompts |
| **Produktion** | Produktionskette, Blender → Unreal, 20 Agenten, Live-Monitor, Direkt-Studio (Claude Code), Aufgaben A–Z, Ausbauplan |
| **Archiv** | Downloads (Originalprojekt, Claude-Paket, gebautes Spiel, DLC-Pakete), Originaldateien, Projekt-ZIPs, Prüfung, Komplettsicherung |

Oben rechts wählst du jederzeit **Projekt** und **Basisspiel/DLC** – alles, was du tust, wird genau diesem Spiel zugeordnet.

**Einfach / Profi** (links unten): Im Profi-Modus siehst du zusätzlich MCP-Details, Logs, Agentenrechte, Prüfsummen und Buildparameter. Der Wechsel ändert keine Daten.

## 4. Der Chat – „Mit GAMEFORGE sprechen“

Der türkise Knopf unten rechts ist überall erreichbar. Oben im Chat siehst du, für welches Spiel/DLC du gerade sprichst.

- **Claude (echte KI):** antwortet über deine lokale Claude-Code-Anmeldung (dein Claude-Abo, keine kostenpflichtige API). Vorschläge und Änderungen erscheinen direkt im Chat.
- **Offline:** keine KI. Fragen wie „Was ist wirklich fertig?“ beantwortet GAMEFORGE dann mit echten Zahlen aus der Datenbank; sonst gibt es klar markierte Vorlagen.
- Jede Änderung zeigt **Vorher/Nachher**. Erst „Übernehmen“ schreibt in die Spielbibel – vorher wird automatisch ein Versionsstand gesichert.
- Statusleiter je Vorschlag: Idee → Vorgeschlagen → Von dir genehmigt → In Projektdaten gespeichert → Im Spiel umgesetzt → Getestet. Die letzten beiden Stufen entstehen nur über die Produktion.

### Claude Code anmelden (einmalig)
Auf deinem PC ist Claude Code installiert, aber **die Anmeldung war beim Test abgelaufen**. So meldest du dich an:
1. Windows-Taste, `cmd` tippen, Enter.
2. `claude auth login` eingeben, Enter, im Browser anmelden.
3. In GAMEFORGE auf **„Erneut prüfen“** klicken.

## 5. Neues Spiel anlegen
Startseite → **Neues Spiel**: Name & Idee → Genre, Stil, Perspektive, Plattform → optionale Wünsche → Zusammenfassung → **Projekt anlegen**.
GAMEFORGE legt an: eigenes Projekt, Spielbibel mit deinen Angaben (nichts dazuerfunden), 25 Entwicklungsaufgaben, eigenen Arbeitsordner mit den 20 Agentenrollen. Alles bleibt später änderbar.

## 6. Referenzbilder (ChatGPT, ohne OpenAI-API)
Kreativstudio → **Referenzbilder** → „Komplettes Bildset“ → **Prompt kopieren** → in ChatGPT einfügen → Bild speichern → **Bild hinzufügen** → prüfen → **Freigeben**.
Referenzbilder sind Vorlagen, keine 3D-Modelle.

## 7. Blender → Unreal
Produktion → **Blender → Unreal**:
1. **Blender-Echttest** – beweist, dass Blender auf dem PC arbeitet (echte .blend + .fbx, 1-m-Würfel, Dateien werden geprüft).
2. **3D-Auftrag anlegen** – mit freigegebenen Referenzen oder genauer Beschreibung.
3. **Claude: Blender → Unreal ausführen** – Claude Code modelliert über die MCP-Verbindung, exportiert und importiert nach `/Game/GAMEFORGE/<Asset-ID>`.
4. Die Stufen (geplant → Referenzen freigegeben → Blender läuft → Datei erstellt → Unreal importiert → getestet → freigegeben) werden **nur aus echten Dateien** abgeleitet.

### MCP einrichten (Schnittstelle von Claude Code zu Blender/Unreal)
Beim Test war in Claude Code **kein MCP-Server eingerichtet**. Ohne MCP kann Claude Blender/Unreal nicht selbst steuern.
- Die Agenten erwarten die Servernamen **`blender`** und **`unreal-mcp`**.
- Blender: Blender-MCP-Add-on in Blender aktivieren und den zugehörigen Server in Claude Code eintragen (`claude mcp add blender …` – den genauen Befehl liefert die Anleitung des jeweiligen Add-ons).
- Unreal 5.8: im Editor das MCP-Plugin aktivieren und die Client-Konfiguration für Claude Code erzeugen.
- Danach in GAMEFORGE **„Erneut prüfen“** – GAMEFORGE testet die Verbindung live mit `claude mcp list`.

## 8. Zwei Wege zur Entwicklung
- **A · Claude-Paket als ZIP:** Archiv → Downloads → „Claude-Paket“. In Claude Desktop → Code → Local öffnen.
- **B · Direkt-Studio:** Produktion → Direkt-Studio. GAMEFORGE startet eine **eigene** lokale Claude-Code-Sitzung im Projektordner und zeigt Ergebnisse, Logs und Fehler. Fehlgeschlagene Aufträge: „Fehler anzeigen“ und „Erneut versuchen“.
Chatverläufe von Claude Desktop und Direkt-Studio sind nicht automatisch synchron.

## 9. Live-Monitor
Produktion → **Live-Monitor** → „Einrichten“. Danach meldet Claude Code Start/Ende/Fehler jedes Agenten. Zustände: Keine Verbindung, Unbekannt, Wartet, Arbeitet, Fehler, Abgeschlossen – keine erfundenen Prozentwerte. Es werden keine Chat-Inhalte gespeichert.

## 10. Sichern, Exportieren, Löschen
- **Versionsstand:** „Projekt sichern“ (oder automatisch vor jeder Chat-Übernahme).
- **Komplettsicherung:** Archiv → Sicherung → „Komplettsicherung herunterladen“ (Datenbank + alle Dateien).
- **Downloads:** (A) Originalprojekt, (B) Claude-Paket, (C) gebautes Spiel, (D) DLC-Pakete – jeweils nur, wenn wirklich vorhanden.
- **Spiel löschen:** Meine Spiele → Projekt → „Spiel löschen …“ → Namen eintippen. Das Spiel wird zuerst als geprüftes ZIP in den **Papierkorb** (`GAMEFORGE_DATA\papierkorb`) gelegt und kann dort wiederhergestellt werden. Endgültig löschen erst nach Eingabe von „ENDGÜLTIG“. Dein lokaler Unreal-/Blender-Projektordner wird nie gelöscht.

## 11. Tests
`python -m unittest discover -s tests` (oder mit dem Blender-Python). Stand dieser Version: **52 Tests bestanden**. Details und ehrliche Statusübersicht: `BESTANDSAUFNAHME_UND_TESTBERICHT.md`.
