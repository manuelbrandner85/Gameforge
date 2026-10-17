# GAMEFORGE GODMODE v1.0 – KI-Agenten-Studio für AION, GENESIS und DLCs

**NEU:** 20 bestätigte Claude-Code-Agenten mit konkreten Rollen, Tool- und MCP-Zuständigkeiten. Der zusätzliche Reiter **KI-Agenten (20)** ermöglicht den Download eines projektbezogenen ZIPs oder die ausdrücklich bestätigte Installation in einen zuvor im Direkt-Studio ausgewählten lokalen Projektordner. Alle bisherigen Daten-/DLC-/Ideen-/Referenz-/Direkt-Studio-Funktionen bleiben unverändert.

**Windows-Start:** ZIP in einen **neuen Ordner** entpacken; `START_GAMEFORGE_WINDOWS.bat` doppelklicken (Python 3.11+ vorausgesetzt). Projekt AION 2026 bzw. GENESIS anklicken → KI-Agenten (20).

**Bestehende Bibliothek mitnehmen:** Alte Version vollständig beenden und `GAMEFORGE_DATA` aus dem bisherigen GAMEFORGE-Ordner sichern, dann in den neuen Programmordner kopieren. NIEMALS einen leeren Ordner über das vorhandene Datenverzeichnis kopieren. Beim Installieren der Agenten auf einen echten Projektordner werden alte Agentendateien nicht überschrieben.

**Claude-App am PC:** Im Claude Desktop im Tab **Code** eine **Local**-Sitzung direkt im ausgewählten AION-/GENESIS-Arbeitsordner starten. Die dortigen `.claude/agents/`-Dateien stehen Claude als Spezialisten zur Verfügung. Blender-/Unreal-MCPs müssen separat eingerichtet werden und die Server-Namen `blender` und `unreal-mcp` erhalten. Studio Director im Hauptchat ansprechen. Keine automatische Verknüpfung mit bereits laufender Desktop-Sitzung.

**Claude-App am Handy:** Eine unterstützte Desktop-Local-Sitzung kann per Remote Control erreichbar sein, während der PC läuft; Cloud-Sitzungen können nicht automatisch den lokalen Unreal-/Blender-MCP erreichen.

**Wichtig:** 34 automatisierte Tests bestanden; ein realer Windows-Desktop-, Blender- und Unreal-End-to-End-Test ist weiterhin offen. Keine fertigen Spiele werden behauptet. Ausführliche Rollen-, MCP- und Ablaufarchitektur unter `resources/TEAM_ARCHITEKTUR_20_AGENTEN.md`.

---

# GAMEFORGE GODMODE v0.8 – AION & GENESIS mit optionalem Direkt-Studio

**START:** ZIP entpacken, auf Windows `START_GAMEFORGE_WINDOWS.bat` starten. Ein aktuelles Python 3 ist erforderlich. V0.8 bleibt eine lokal laufende Web-App in deinem Browser.

**NEU:** Spielebibliothek → AION oder GENESIS → **Direkt-Studio**. Optional Claude Code direkt für Planung/Arbeit am eigenen Projektordner nutzen, ursprüngliches Vollprojekt-ZIP sicher in eigenen Arbeitsordner übernehmen, Claude-/Unreal-Ausgaben ansehen, Windows-Builds bei vorhandenem Unreal lokal erstellen und Quellenstände archivieren. Die klassische manuelle ZIP-Übergabe bleibt erhalten. Komplette Anleitung im letzten Kapitel `GAMEFORGE GODMODE v0.8`.

**UPGRADE:** v0.8 in einen **neuen** Ordner entpacken. Vorher alte GAMEFORGE-App vollständig beenden und gesamtes bisheriges `GAMEFORGE_DATA` sichern. Danach den vollständigen alten Ordner `GAMEFORGE_DATA` in das neue v0.8-Verzeichnis kopieren, dann v0.8 starten. Nicht allein SQLite-Datei ohne Uploads kopieren. Bereits vorhandene AION-/GENESIS-Projekteinträge bleiben bestehen.

**WICHTIG:** Diese Vorversion baut ohne funktionsfähige lokale Claude-Code-/Blender-/Unreal-Installation noch keine echten Spiele. Auf dem Entwicklungsrechner wurden 28 Python-Tests bestanden, nicht jedoch ein vollständiger Windows-Unreal-MCP-Build. Die älteren Hinweise weiter unten beziehen sich teilweise auf v0.6 und frühere Versionen.

---

# NEU IN v0.6 — GAMEFORGE Creative Director / Ideen-Chat

- In AION, GENESIS oder jedem anderen Spiel den Reiter **Ideen-Chat** öffnen. Den DLC-Bereich optional separat auswählen.
- **Vorschläge aus Vorlagen** speichert Ideen lokal und bietet drei kontextbezogene Vorschläge ohne KI-Anbindung. Diese sind regelbasiert und nicht mit echter KI-Beratung zu verwechseln.
- **Mit Claude Ideen entwickeln** startet den lokal installierten, angemeldeten Claude Code im Planungsmodus über `claude -p`. Dabei werden die aktuelle Nutzereingabe, einige vorherige Chatnachrichten und ausgewählte Spielbibel-Felder zur Auswertung an Anthropic übertragen. Dafür wird dein vorhandenes Claude-Konto im Rahmen seiner aktuellen Tarif-/Verbrauchsregeln genutzt (Limits und ggf. Kosten beachten). Es gibt keine OpenAI-Bild-API und keine MCP-Entwicklung in diesem Chatmodus.
- Der Ideen-Chat arbeitet mit dem lokalen Claude-Code-CLI, wenn es auf dem Rechner installiert und im `PATH` erreichbar ist. Ohne Claude bitte den Vorlagenmodus verwenden.
- Vorschläge sind zunächst **Vorgeschlagen**. Über **Annehmen** oder **Ablehnen** entscheidet der Nutzer. Nur **angenommene** Vorschläge werden in `CREATIVE_DIRECTOR/ACCEPTED_IDEAS.json` des Claude-Exportpakets aufgenommen.
- Über **In Spielbibel übernehmen** wird die Idee zusätzlich als gekennzeichneter Text im passenden Spielbibel- oder DLC-Feld hinterlegt. Vor einer Integration ins Basisspiel wird ein Planungssnapshot erzeugt. Vorhandene Inhalte werden nicht gelöscht.
- Chats und Vorschläge werden persistent in derselben lokalen SQLite-Datenbank gespeichert und über die **Gesamte Bibliothek sichern**-Funktion mitgesichert.
- Wichtig: Der Chat analysiert noch nicht selbstständig den Inhalt hochgeladener alter PDFs, 3D-Modelle oder Unreal-Projekte. Dieser Schritt bleibt eine später umzusetzende Funktion.

---

# GAMEFORGE GODMODE – v0.6 · Spielebibliothek, Altdatenimport und Produktionsplanung

**AION 2026 und GENESIS sind als getrennte, weiterbearbeitbare Projekte vorbelegt.** Sie sind **keine fertigen Spiele**. Bisher liegen in dieser Downloadversion nur die bekannten kurzen Konzeptangaben und offenen Referenzaufträge vor. Die echten bestehenden Daten, Builds, GitHub-Repository-Inhalte, Modelle und Dokumente können über den Import ergänzt werden. GAMEFORGE greift nicht automatisch auf deinen PC oder GitHub zu.

## Neu in v0.6: genehmigter Erweiterungs-Fahrplan 1–40

Die 35 angenommenen Nutzerentscheidungen 1–20, 24–36, 38 und 40 vom 17. Oktober 2026 sind als **verbindliche, aber noch nicht umgesetzte** Entwicklungsanforderungen eingebaut. Öffne AION oder GENESIS und klicke auf **Ausbauplan 1–40**. Dort findest du die fünf Phasen, vollständige Beschreibung, Voraussetzungen und überprüfbare Abnahmekriterien für jedes Feature. Der Plan wird auch in **jedes Claude-Code-ZIP** eingebunden. Außerdem liegt der Plan in `resources/ENTWICKLUNGSPLAN_1_40.md` und `resources/ROADMAP_APPROVED_1_40.json`.

**Keine falschen Fertigmeldungen:** Die 35 Funktionen wurden genehmigt, nicht alle programmiert. Die Funktionen 21–23, 37 und 39 wurden abgelehnt und bleiben außerhalb des Entwicklungsplans. Die existierenden Funktionen für Referenzen, Import, DLCs, Spielbibel, Produktionsaufgaben und ZIP-Export bleiben erhalten. Es wird keine OpenAI-API integriert; Referenzen entstehen weiterhin hier im ChatGPT-Chat und werden zurückimportiert.

**Upgrade von v0.4:** Programm beenden, Bibliothek separat sichern, v0.6 in neuen Ordner entpacken und bei bereits eingerichteter v0.4 den vollständigen Ordner `GAMEFORGE_DATA` übernehmen; anschließend v0.6 starten. Die Roadmap-Dateien sind im Programmordner, nicht in der SQLite-Datenbank. Originalarchive und Referenzen bleiben im Datenordner.

## Start unter Windows

1. ZIP entpacken (nicht aus dem ZIP starten).
2. Python 3.11 oder neuer installieren; bei Python.org die Option **Add Python to PATH** aktivieren.
3. `START_GAMEFORGE_WINDOWS.bat` doppelklicken.
4. Die lokale Oberfläche öffnet sich unter `http://127.0.0.1:8765` (falls dieser Port belegt ist, steht der aktuelle Port im Terminal).
5. Im Bereich **Spielebibliothek** AION 2026 oder GENESIS anklicken.

Benötigt keine kostenpflichtige API. Das Programm verwendet nur Pythons Standardbibliothek und läuft lokal auf 127.0.0.1. Externe KI-Modelle, Blender und Unreal sind *nicht* im Programm enthalten.

## Alle bestehenden AION- oder GENESIS-Daten übernehmen

1. Spiel öffnen und den Reiter **Vorhandene Daten** anklicken.
2. **Dateien auswählen** für einzelne Unterlagen oder **Gesamten Projektordner auswählen** für eine ganze Ordnerstruktur.
3. **Ausgewählte Dateien importieren** bzw. **Gesamten Ordner importieren** klicken.
4. Für komplette Unreal-Projekte, alte Claude-Produktionspakete oder GitHub-Repositories empfehlen wir zusätzlich **ein einziges ZIP pro gesichertem Versionsstand**. GitHub: im jeweiligen Repository **Code → Download ZIP** wählen und die Datei anschließend in GAMEFORGE importieren.
5. Wiederholen, bis alle früheren Story-Dateien, Videos, Referenzen, 3D-Dateien, Texturen, Skripte, `.uproject`, `.uasset`, `.umap` und Blender-Projekte eingelagert sind.
6. Im Reiter **Entwicklung A–Z** die erste Phase **Bestandsaufnahme** anhand der importierten Daten durchführen. Den Status nur aktualisieren, wenn tatsächlich Nachweise vorliegen.
7. **Prüfung & Export → Vollpaket** erzeugt ein Claude-Code-ZIP mit der Planung, allen **eingelagerten** Originaldateien und dem Aufgabenplan.

Für ChatGPT-Referenzen bitte weiter den Reiter **Referenzbilder** nutzen: Prompt kopieren → ChatGPT Bild erstellen → Bild dem richtigen Auftrag zuordnen → selbst freigeben. Allgemeine Bilddateien aus alten Projekten können stattdessen ebenfalls über **Vorhandene Daten** übernommen werden.

**Vorsicht bei sehr großen Projekten:** Import von Einzeldateien erfolgt nacheinander. Vollprojekt-ZIPs sind robuster. Pro Einzeldatei gilt derzeit ein Limit von 8 GB. Die tatsächliche Gesamtkapazität hängt vom freien Speicher auf deinem PC ab. Sehr viele kleine Dateien oder große Einzeldateien können länger dauern; während des Imports den Browser offen lassen.

## Entwicklungsplan bis zum Release

Der neue Tab **Entwicklung A–Z** enthält 25 konkrete Aufgaben für:

- Bestand, Kanon, Gameplay und Story inklusive Prolog / Enden
- Weltlogik, NPCs, Charaktere, Bosse, Waffen, Referenzen
- Blender: Modellierung, UV, Materialien, Rigging, Animationen
- Unreal: C++, Blueprints, Spielsysteme, Missionen, Physik, KI, Speichern
- Menü, HUD, Ton, Sprachausgabe, Cinematics, Lokalisierung
- Integration, Testläufe, Performance, Release / Installer
- Updates und DLC-Kompatibilität

Jede Aufgabe besitzt Ziel, Akzeptanzkriterium und Status. Die Software erstellt **nicht** automatisch die 3D-Objekte oder spielbare Unreal-Funktionen: Claude Code kann solche Arbeiten anschließend über vorher eingerichtete Blender-/Unreal-MCP-Verbindungen umsetzen. Die Statusanzeige ersetzt keine realen Builds und QA-Abnahmen. "Getestet" und "Abgenommen" erfordern zumindest einen dokumentierten Prüfbeleg; GAMEFORGE validiert diesen Beleg nicht automatisch. Um das Basisspiel erstmals als "Fertig" zu markieren, müssen alle Basisspiel-Aufgaben abgenommen, Pflichtbilder freigegeben und ein Vollprojekt-ZIP sowie ein Windows-Build-ZIP eingelagert sein.

## DLCs und Versionen

- DLCs dauerhaft dem jeweiligen Spiel zuordnen und über **Entwicklung A–Z** auswählen. Jeder DLC hat sechs eigene Produktionsaufgaben und ein eigenes ZIP-Exportpaket.
- **Dateiarchiv** hält ältere vollständige ZIP-Projekte und Builds bereit, ohne die Originale zu überschreiben.
- **Version sichern** erstellt Snapshots der Spielplanung. Die Versionswiederherstellung ändert nur die Spielbibel, nicht importierte Originaldateien, DLCs oder Aufgabenstände.
- **Gesamte Bibliothek sichern** enthält die Datenbank und alle eingelagerten Dateien (auch Einzelimporte).

## Upgrade von GAMEFORGE v0.2

1. GAMEFORGE v0.2 schließen.
2. **Gesamte Bibliothek sichern** anklicken und das Backup sicher verwahren.
3. Das v0.6 ZIP in einen **neuen** Ordner entpacken.
4. Den kompletten Ordner `GAMEFORGE_DATA` von v0.2 nach v0.3 kopieren, sofern er bereits existiert. Nicht die einzelnen SQLite-Dateien bei laufender Anwendung kopieren.
5. v0.3 starten. Die Datenbank wird um die neuen Tabellen erweitert; bestehende Spiele, DLCs, Referenzen und Archive bleiben erhalten. **Kopiere nicht bloß die Datenbank ohne Upload- und Referenzordner.**
6. Erst wenn alles sichtbar ist, alte Installationen aufräumen. Backups separat behalten.

## Was diese Version noch nicht kann

- Importierte PDFs und Dokumente werden zunächst **unverändert gespeichert und manifestiert**, nicht automatisch in die Spielbibel oder einen gesicherten Kanon übernommen.
- Das Paket enthält **keinen echten fertigen AION-/GENESIS-Build**, kein fertiges UE-/Blender-Spiel und **keine integrierte KI-Anbindung**.
- Spiele werden nicht selbstständig gebaut; GAMEFORGE ist hier die zentrale Planungs-, Import- und Exportanwendung. Die ausführende Produktion erfolgt mit Claude Code und eingerichteten MCP-Schnittstellen.
- Der Benutzer muss hochgeladene Dateien auf Vollständigkeit und Nutzungsrechte prüfen.

## Tests

Unter Windows mit Python-Terminal im Programmordner:

`python -m unittest discover -s tests -v`

Keine Quellprogramme aus fremden ZIP-Archiven automatisch starten; Archive zuerst auf Vertrauenswürdigkeit prüfen. Der lokale Server sollte nicht ohne zusätzliche Authentifizierung für externe Netzwerke freigegeben werden.

## Ergänzung v0.6 – Beschlüsse 21–40

15 neue Erweiterungen (24–36, 38 und 40) genehmigt. Abgelehnt sind 21, 22, 23, 37 und 39. Keine abgelehnte Erweiterung wird neu implementiert. Die genehmigten Erweiterungen sind derzeit lediglich als nachprüfbare Anforderungen dokumentiert, **nicht als lauffähige Funktionen**. Die Statusprüfung unter „Ausbauplan 1–40“ unterscheidet diese Punkte von den schon bestehenden Basisfunktionen. Bestehende AION-/GENESIS-Daten bleiben beim Übernehmen des gesamten `GAMEFORGE_DATA` erhalten.

---

## GAMEFORGE GODMODE v0.8 – OPTIONALER DIREKT-STUDIO-MODUS

Die bisherige ZIP-Übergabe an Claude Code bleibt verfügbar. Im neuen Projekt-Reiter **Direkt-Studio** kann GAMEFORGE lokale Claude-Code-Arbeitsaufträge direkt starten und deren tatsächlichen Status und Ausgabe anzeigen. Nicht mit dem Ideen-Chat verwechseln: Der Ideen-Chat erzeugt nach Freigabe Änderungen an den GAMEFORGE-Konzeptdaten; der Direktmodus beauftragt Claude, im lokalen echten Projektordner zu arbeiten.

**Anleitung:**

1. AION oder GENESIS öffnen → **Direkt-Studio**. Windows-PC: Claude Code installieren und anmelden; Blender installieren; Unreal Engine installieren und die jeweiligen MCP-Integrationen für Claude Code einrichten. Informationen zu Unreal MCP für UE 5.8: https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor (derzeit experimentell).
2. Einen bestehenden Projektordner hinterlegen und **Speicherort verbinden** drücken. Alternativ einen separaten leeren Arbeitsordner in GAMEFORGE anlegen. Wenn ein originales Vollprojekt-ZIP bereits in GAMEFORGE importiert wurde, im Direkt-Studio auswählen und mit **Gewähltes ZIP sicher entpacken** in einen neuen Ordner übernehmen. Andere vorhandene Ordner werden dabei nicht überschrieben.
3. **Verbindungstest** ansehen. Das Vorhandensein von EXE, Konfiguration oder einer erreichbaren Portnummer beweist noch keine tatsächliche funktionierende MCP-Verbindung. Claude-Code-Anmeldung, Unreal-MCP und Blender-MCP müssen lokal geprüft werden.
4. Einen Auftrag eingeben. **Plan erstellen** nutzt Claude Code im Plan-Modus ohne beabsichtigte Dateibearbeitung. **Änderungen ausführen** nutzt Claude Code mit `acceptEdits` im gewählten Arbeitsordner; vor der Ausführung erscheint eine ausdrückliche Bestätigung. Nicht alle Werkzeuge oder MCP-Aktionen lassen sich ohne zusätzliche Berechtigung ausführen. Wir umgehen keine Claude-Sicherheitsfreigaben.
5. Unter **Auftragsprotokoll** erscheinen die echten Prozessantworten, Fehler und der laufende bzw. abgeschlossene Status. Ein Auftrag wird nicht automatisch als umgesetzt oder getestet markiert, nur weil Claude einen Text zurückgibt.
6. Freigegebene Einzeldateien und freigegebene ChatGPT-Referenzbilder aus der gewählten GAMEFORGE-Bibliothek werden vor Plan-/Umsetzungsaufträgen bis zu einer Gesamtgröße von 3 GB in eine projektbezogene `.gameforge/project_inputs`-Ablage kopiert und in `.gameforge/INPUT_MANIFEST.json` aufgeführt. Zu große Einzelimporte werden im Manifest vermerkt und nicht stillschweigend übernommen. Vollprojekt-ZIPs müssen separat über die Schaltfläche entpackt oder im bestehenden Arbeitsordner vorhanden sein. Kein fremder Code wird beim Entpacken ausgeführt.
7. Optional im Direkt-Studio den absoluten Pfad zu `RunUAT.bat` eintragen. Sind ein echtes `.uproject` im Projekt-Hauptordner und eine funktionierende Windows-Umgebung vorhanden, kann **Windows-Build erstellen** Unreal BuildCookRun ausführen. Nur nach tatsächlichem erfolgreichem Paketierungsvorgang mit Dateien wird das Build-ZIP in **Dateiarchiv** gespeichert. Dieser Schritt wurde bislang nicht mit Unreal auf einem Windows-PC getestet.
8. **Aktuelle Quelldateien als ZIP archivieren** speichert den tatsächlichen, lokalen Arbeitsstand als Download in **Dateiarchiv**. Engine-Caches, `.env`-Dateien und lokale MCP-Konfiguration werden nicht mit archiviert. Der Quellstand und die Windows-Spiel-Builds sind getrennte Archive.

**Sicherheits- und Reifehinweise:** Die Software bindet weiterhin nur an `127.0.0.1`. Der Direktmodus ist ein erster integrierter Produktionsablauf, kein fertiger autonomer AAA+-Spielgenerator. Aufträge laufen nacheinander, benötigen Installation, freien Speicher, eigene Eingabe und aktive lokale Programme. Nutzer sollten vor Änderungen Git-Commits und vollständige Backups der echten Projektordner anlegen. Claude Code und Plugins können eigene Nutzungsbedingungen, Berechtigungen und Limits haben. Ein erfolgreiches Packaging ist nicht automatisch die Freigabe des Spiels. Ungetestet bleiben die reale Windows-GUI, Claude-Login/MCP-End-to-End und Windows-Unreal-Packaging; Offline-Tests verwenden kontrollierte Simulationen.

28 automatische Python-Funktionstests in `tests/`; ausführen mit `python -m unittest discover -s tests -v`. Der Stand der ursprünglichen genehmigten GAMEFORGE-Erweiterungen 1–40 bleibt unverändert.


## GAMEFORGE v1.0 – Pro Spiel Agenten-Sessions, Live-Status, Blender→Unreal

- **Bei neu angelegten Spielen** wird im lokalen GAMEFORGE_DATA-Verzeichnis ein eigener Projektordner angelegt und werden die 20 Agentenbeschreibungen automatisch vorbereitet (kein automatisches Claude-Login, keine Unreal-Projektdatei erfunden).
- **Claude Desktop**: Code → Local → denselben Projektordner wählen. **GAMEFORGE Direkt-Studio** startet dagegen selbst eine lokale Claude-CLI-Sitzung im verbundenen Ordner. Beide Sitzungen sind unabhängig; GAMEFORGE übernimmt nicht automatisch deinen bisherigen Desktop-Chatverlauf.
- **Live-Agenten & 3D**: Über „Live-Hooks installieren“ werden Claude-Code-Hooks `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `PostToolUseFailure` im verbundenen Projekt konfiguriert. Bestehende `.claude/settings.local.json` bleibt erhalten; bei erforderlicher Ergänzung wird vorher eine Kopie angelegt. Nur Ereignisse dieser tatsächlich mit dem Projekt gestarteten Claude-Sitzungen werden in `.gameforge/agent_events.jsonl` gespeichert. Chat-Inhalte werden nicht mitgeschrieben. Die Übersicht aktualisiert sich alle 3 Sekunden. Ohne Ereignisse: „Keine aktive Meldung“ und keine erfundenen Tätigkeiten. Eine Sitzung kann bei fehlendem `SubagentStop` nach 15 Minuten als inaktiv erscheinen; das ist keine genaue Arbeitszeitmessung.
- **Blender→Unreal**: Freigegebene ChatGPT-Referenzen auswählen, Asset-Typ und Anforderungen eingeben, Handoff erzeugen. In `.gameforge/asset_pipeline/<ID>/` entstehen eine JSON-Spezifikation, Kopien freigegebener Bilder, `BLENDER_TASK.md`, `UNREAL_TASK.md` und ein konservatives Unreal-Python-Importtemplate. Das sind technische **Arbeitsaufträge**, noch keine erzeugten Modelle. Im Direkt-Studio kann Claude Code die Schritte mit eingerichteten Blender-/Unreal-MCPs umsetzen. Besonders Skeletal Meshes benötigen ein angepasstes Unreal-Importsetup.
- Unreal-Import über FBX/Interchange ist von Epic dokumentiert. Blender, Unreal, MCP, Claude und GPU müssen auf dem Ziel-PC praktisch geprüft werden. Keine Behauptung, dass hier ein 3D-Modell erstellt oder eine MCP-Verbindung erfolgreich getestet wurde.
- **Bestehende Projekte** AION/GENESIS müssen nicht überschrieben werden. Falls du ihre Originalprojektordner verwendest, im Direkt-Studio zuerst den entsprechenden Ordner verbinden und die Agenten/Hooks dort ausdrücklich installieren. Für jedes neue Spiel bleibt auch ZIP-Export verfügbar.

**NEU:** Ein 3D-Auftrag kann auch ohne Bildreferenzen vorbereitet werden, sofern eine ausführliche Designbeschreibung vorhanden ist. Die eigentliche Modellierung wird nach expliziter Freigabe durch Claude Code über Blender-MCP beauftragt, anschließend ist ein überprüfbarer Unreal-Import vorgesehen.
