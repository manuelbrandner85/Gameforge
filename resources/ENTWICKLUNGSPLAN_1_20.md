# GAMEFORGE GODMODE – verbindlicher Entwicklungsplan (Erweiterungen 1–20)

**Freigabe:** 17.10.2026 – alle 20 Erweiterungen vom Nutzer bestätigt.
**Status:** ANFORDERUNGEN GENEHMIGT; noch nicht automatisch in GAMEFORGE v0.4 implementiert.
**Feste Architektur:** GAMEFORGE plant und exportiert; Referenzbilder entstehen separat in ChatGPT und werden importiert; Claude Code setzt Blender/Unreal über MCP um.
**Projekte:** AION 2026 und GENESIS bleiben getrennt; bestehende Dateien müssen importiert und auf Herkunft geprüft werden.

## Reihenfolge und Abhängigkeiten
Die Phasen sind grobe Planung. Innerhalb einer Phase entscheidet der Abhängigkeitsgraph und die verfügbare Bestandsaufnahme über die Umsetzungsreihenfolge. Der kleinste spielbare Vertical Slice muss vor breitem Asset-Bau getestet werden.

## I – Bestandsaufnahme

### 1. GODMODE Projekt-Scanner
**Umfang:** Importe mit SHA-256, Manifest, Herkunft und Duplikaterkennung prüfen; Story-, Code-, Asset- und Versionskonflikte als offene Punkte ausgeben.
**Abnahme:** Für Testprojekt findet Scanner Duplikate, fehlende Dateien und widersprüchliche Datensätze mit Quellenbezug.
**Voraussetzungen:** keine
**Status:** geplant

### 7. Asset Dependency Brain
**Umfang:** Assets, Missionen, Dialoge, Audio, Animationen und Cinematics über unveränderliche IDs und Referenzbeziehungen nachverfolgen.
**Abnahme:** Änderung an einem Asset liefert vollständigen Änderungsfolgen-Bericht und Warnung bei fehlenden Referenzen.
**Voraussetzungen:** 1
**Status:** geplant

## II – Kreative Spezifikation

### 2. Story Intelligence Engine
**Umfang:** Mehraktige Story, Kanon, Timeline, Verzweigungen, Dialoge, Charakterziele, Endbedingungen und Konfliktprüfung als strukturierte Game-Bible ausarbeiten.
**Abnahme:** Alle Hauptpfade besitzen Zustandsübergänge, keine unaufgelösten Kanonkonflikte; Entscheidungen sind exportierbar.
**Voraussetzungen:** 1
**Status:** geplant

### 3. Ultimate Character Creator
**Umfang:** Charakter-Steckbriefe, Biografien, Geometrie-/Rig-Vorgaben, Fähigkeiten, Animation-Sets und Bildprompt-Sets mit stabilen IDs.
**Abnahme:** Figur wird inklusive Daten, Bildbedarf, Ausrüstungs- und Animationsliste eindeutig exportiert.
**Voraussetzungen:** 2
**Status:** geplant

### 4. World Architect
**Umfang:** Regionen, Welt- und Levelkoordinaten, Level-Streaming, Zugänge, Interaktionszonen, Dungeons und Umgebungs-Assets systematisch modellieren.
**Abnahme:** Weltzonen und Mission-Standorte sind eindeutig verlinkt; keine unerreichbaren Pflichtorte.
**Voraussetzungen:** 2
**Status:** geplant

### 5. Boss & Combat Designer
**Umfang:** Kampfschleife, Waffen, Trefferfenster, Zustandsmaschinen, Bossphasen, Verhalten und Balancing-Kriterien ausarbeiten.
**Abnahme:** Jeder Boss besitzt mindestens eine vollständige testbare Ablaufdefinition mit Phasen und Fehlschlagszenarien.
**Voraussetzungen:** 3, 4
**Status:** geplant

### 6. Cinematic Director
**Umfang:** Prologe, Zwischensequenzen und Outro als Shotlisten, Kamera-/Audio-Timelines und Gameplay-Übergaben definieren.
**Abnahme:** Alle verpflichtenden Storyszenen haben Timing, Assets, Eingangstrigger und Endzustand.
**Voraussetzungen:** 2, 3, 4
**Status:** geplant

### 11. KI-Missionsgenerator
**Umfang:** Haupt- und Nebenmissionen mit Vorbedingungen, Schritten, Quest-State, Belohnungen, Scheitern und Wiederaufnahme modellieren.
**Abnahme:** Alle Missionsschritte besitzen eindeutige Auslöser, erfolgreiche und fehlerhafte Pfade.
**Voraussetzungen:** 2, 4
**Status:** geplant

### 12. Living World Simulator
**Umfang:** NPC-Routinen, Fraktionen, Weltzustände, Handel, Tageszeiten, Wetter und reaktive Events ausarbeiten.
**Abnahme:** NPC-/Weltzustandsübergänge sind definiert, kompatibel mit Quests und speicherbar.
**Voraussetzungen:** 4, 11
**Status:** geplant

## III – Produktionsvorbereitung

### 8. Blender Production Master
**Umfang:** Vorgaben für Maßstab, Polygonziele, Topologie, UV, PBR, LOD, Rigs, Animationen, Kollisionsobjekte und Exportprofile erstellen.
**Abnahme:** Blender-Auftrag enthält Eingaben, Modell-/Exportnamen, technische Limits und überprüfbare Asset-Abnahme.
**Voraussetzungen:** 3, 7, 14
**Status:** geplant

### 9. Unreal Blueprint Architect
**Umfang:** Versionierte UE-Architektur mit C++-Klassen, Blueprint-Interfaces, Datenobjekten, Input, Speichern und Build-Tests spezifizieren.
**Abnahme:** Claude-Export besitzt Modulgraph, Reihenfolge, Schnittstellen, Definition-of-Done und Testanforderungen.
**Voraussetzungen:** 4, 5, 7
**Status:** geplant

### 13. Sound & Voice Director
**Umfang:** Sound-Cue-Katalog, Musikmotive, Dialogline-IDs, Stimmrollen, Raumklang, Untertitel-Synchronität und Rechteangaben.
**Abnahme:** Jede verpflichtende Szene und Aktion referenziert Audio oder dokumentiert bewusst stumme Ausführung.
**Voraussetzungen:** 2, 6
**Status:** geplant

### 14. Referenzbild-Qualitätsprüfer
**Umfang:** ChatGPT-Referenzprompts, Bildansichten, Dimensionsregeln, Stil-Konsistenz und menschliche Freigabe nach Import verwalten.
**Abnahme:** Pflichtbilder werden pro Asset gezählt; Inkonsistenzen sperren Bild-Freigabe, bis behoben/begründet.
**Voraussetzungen:** 3, 4, 7
**Status:** geplant

## IV – Umsetzung & Qualität

### 10. Autonomous QA Director
**Umfang:** Tests für Kompilierung, Gameplay, Save/Load, Regression, visuelle Checks, Performance und manuelle Gates definieren.
**Abnahme:** Jeder Fertigstatus verlangt realen Testbeleg; rote Tests sperren Releasefreigabe.
**Voraussetzungen:** 9, 18
**Status:** geplant

### 17. Performance Architect
**Umfang:** Ziel-Hardware, Framerate, Auflösung, Speichergrenzen, Streaming, LOD und GPU-/CPU-Budgets je Grafikstil definieren.
**Abnahme:** Performance-Budget und Messprofil sind im Produktionspaket festgelegt; Abweichungen werden protokolliert.
**Voraussetzungen:** 8, 9
**Status:** geplant

### 18. Claude Precision Export
**Umfang:** Präzise ZIP-Handoff-Pakete mit Game-Bible, Bildreferenzen, Dateiindex, DAG-Aufträgen, MCP-Checkliste, Tests und Fortsetzungszustand.
**Abnahme:** Jede Task besitzt Eingaben, Schritte, Abhängigkeiten, Abnahme und gültige Pfade; Paket ist reproduzierbar.
**Voraussetzungen:** 1, 7, 8, 9, 11, 14
**Status:** geplant

### 19. Kosten- und Tokenoptimierung
**Umfang:** Kontext selektiv laden, Prompt-Deduplizierung, Versions-Deltas, zwischengespeicherte Analysen und nachvollziehbares Budget.
**Abnahme:** Export/Arbeitsauftrag verarbeitet bei unveränderten Quellen nur notwendige Deltas ohne Kanonverlust.
**Voraussetzungen:** 1, 7, 18
**Status:** geplant

## V – Release & Erweiterungen

### 15. DLC Expansion Studio
**Umfang:** DLCs dem Basisspiel zuordnen, Story-/Asset-Abhängigkeiten und Kompatibilität gegen konkrete Spielversionen prüfen.
**Abnahme:** Ein DLC lässt sich separat exportieren und meldet inkompatible Basisversionen und fehlende Asset-IDs.
**Voraussetzungen:** 7, 9, 18
**Status:** geplant

### 16. Game Evolution System
**Umfang:** Bestehende Releases versioniert verbessern: Änderungswünsche, Regressionen, Branches, Migrationspläne und Patch-Freigaben.
**Abnahme:** Ein Nachfolge-Release bewahrt Originalstände und zeigt alle Änderungen sowie Rückrollmöglichkeit.
**Voraussetzungen:** 7, 10, 15
**Status:** geplant

### 20. Release & Publishing Center
**Umfang:** Reproduzierbare Builds, Installer, Plattformprofile, Credits, Rechte, Controller, Barrierefreiheit, Lokalisierung und Store-Pakete vorbereiten.
**Abnahme:** Freigabe nur mit bestandenem Testplan, Build-Artefakt, Quellenarchiv und überprüfter Release-Checkliste.
**Voraussetzungen:** 10, 15, 16, 17, 18
**Status:** geplant

## Qualitätsgates und Grenzen

1. Datenarchiv und Kanonprüfung, bevor neue Inhalte als verbindlich angenommen werden.
2. Projekt- und DLC-Dateien niemals vorgeben, wenn sie nicht importiert oder wirklich erzeugt wurden.
3. ChatGPT-Referenzbilder bleiben ein separater manueller Schritt und brauchen sichtbare Freigabe.
4. Claude-Paket nur als „vollständig spezifiziert“ markieren, wenn Pflichtreferenzen, Parameter und Tests beschrieben sind; „implementiert“/„spielbar“/„getestet“ erst mit realen Belegen.
5. Vor jedem größeren Eingriff Version/Sicherung; vorhandener Story-Kanon bleibt maßgeblich.
6. DLCs müssen Basisspielversion, neue Asset-IDs, Savegame-Kompatibilität und Regressionen angeben.
7. Falls MCP, UE-Version oder Plugins fehlen, als Blocker melden und keine automatische Erledigung behaupten.
