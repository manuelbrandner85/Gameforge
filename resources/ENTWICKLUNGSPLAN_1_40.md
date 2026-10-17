# GAMEFORGE GODMODE – verbindlicher Entwicklungsplan 1–40

**Stand: 17. Oktober 2026 · 35 genehmigt · 5 abgelehnt**

Diese Angaben sind genehmigte ANFORDERUNGEN, **keine fertig entwickelten GAMEFORGE-Module**. Echte Tests und Dateinachweise sind separat zu erfassen.

Alle bestehenden v0.4-Bibliotheks-, Dateiimport-, Referenz- und Exportfunktionen bleiben bestehen. AION und GENESIS sind vorhandene Startprojekte, keine fertigen Spiele.

## Entscheidungen

**Genehmigt:** 1–20; 24–36; 38; 40.

**Abgelehnt (nicht neu implementieren):** 21 Master Canon Lock; 22 Intelligenter Projekt-Merger; 23 Design-DNA Studio; 37 Gameplay Replay Analyzer; 39 Disaster Recovery Engine.

Abgelehnte Erweiterungen entfernen keine bereits existierenden Datensicherungs-, Story- oder Importfunktionen.

## Phase I – Bestandsaufnahme

Bestehende Projekte bewahren und korrekt erfassen

### 1. GODMODE Projekt-Scanner

**Status:** geplant / genehmigt
**Umfang:** Importe mit SHA-256, Manifest, Herkunft und Duplikaterkennung prüfen; Story-, Code-, Asset- und Versionskonflikte als offene Punkte ausgeben.
**Abnahmekriterium:** Für Testprojekt findet Scanner Duplikate, fehlende Dateien und widersprüchliche Datensätze mit Quellenbezug.
**Abhängigkeiten:** keine

### 7. Asset Dependency Brain

**Status:** geplant / genehmigt
**Umfang:** Assets, Missionen, Dialoge, Audio, Animationen und Cinematics über unveränderliche IDs und Referenzbeziehungen nachverfolgen.
**Abnahmekriterium:** Änderung an einem Asset liefert vollständigen Änderungsfolgen-Bericht und Warnung bei fehlenden Referenzen.
**Abhängigkeiten:** 1

### 30. Asset Rights Vault

**Status:** geplant / genehmigt
**Umfang:** Pro Datei die Herkunft, Urheber, Quellenlink, Lizenz, Kauf- oder Nutzungsnachweis, erlaubte Verbreitungsarten und erforderliche Credits dokumentieren.
**Abnahmekriterium:** Veröffentlichung ist gesperrt, wenn für genutzte Fremdassets kein ausreichender Lizenznachweis oder keine passende Freigabe eingetragen ist.
**Abhängigkeiten:** 1, 7, 20

### 40. Production Feasibility Brain

**Status:** geplant / genehmigt
**Umfang:** Vor Erstellung großer Claude-Aufträge Engine-Version, erforderliche Plugins, RAM/VRAM, Speicherbedarf, Assets, Personalzeit und offene Abhängigkeiten prüfen.
**Abnahmekriterium:** Machbarkeitsreport enthält Annahmen, Risikoampel, Grobaufwand, harte Blocker, Versionsmatrix und Minimalumfang für erstes Release.
**Abhängigkeiten:** 1, 7, 17, 18

## Phase II – Kreative Spezifikation

Story, Welt, Figuren, Gameplay und Cinematics ohne Widersprüche beschreiben

### 2. Story Intelligence Engine

**Status:** geplant / genehmigt
**Umfang:** Mehraktige Story, Kanon, Timeline, Verzweigungen, Dialoge, Charakterziele, Endbedingungen und Konfliktprüfung als strukturierte Game-Bible ausarbeiten.
**Abnahmekriterium:** Alle Hauptpfade besitzen Zustandsübergänge, keine unaufgelösten Kanonkonflikte; Entscheidungen sind exportierbar.
**Abhängigkeiten:** 1

### 3. Ultimate Character Creator

**Status:** geplant / genehmigt
**Umfang:** Charakter-Steckbriefe, Biografien, Geometrie-/Rig-Vorgaben, Fähigkeiten, Animation-Sets und Bildprompt-Sets mit stabilen IDs.
**Abnahmekriterium:** Figur wird inklusive Daten, Bildbedarf, Ausrüstungs- und Animationsliste eindeutig exportiert.
**Abhängigkeiten:** 2

### 4. World Architect

**Status:** geplant / genehmigt
**Umfang:** Regionen, Welt- und Levelkoordinaten, Level-Streaming, Zugänge, Interaktionszonen, Dungeons und Umgebungs-Assets systematisch modellieren.
**Abnahmekriterium:** Weltzonen und Mission-Standorte sind eindeutig verlinkt; keine unerreichbaren Pflichtorte.
**Abhängigkeiten:** 2

### 5. Boss & Combat Designer

**Status:** geplant / genehmigt
**Umfang:** Kampfschleife, Waffen, Trefferfenster, Zustandsmaschinen, Bossphasen, Verhalten und Balancing-Kriterien ausarbeiten.
**Abnahmekriterium:** Jeder Boss besitzt mindestens eine vollständige testbare Ablaufdefinition mit Phasen und Fehlschlagszenarien.
**Abhängigkeiten:** 3, 4

### 6. Cinematic Director

**Status:** geplant / genehmigt
**Umfang:** Prologe, Zwischensequenzen und Outro als Shotlisten, Kamera-/Audio-Timelines und Gameplay-Übergaben definieren.
**Abnahmekriterium:** Alle verpflichtenden Storyszenen haben Timing, Assets, Eingangstrigger und Endzustand.
**Abhängigkeiten:** 2, 3, 4

### 11. KI-Missionsgenerator

**Status:** geplant / genehmigt
**Umfang:** Haupt- und Nebenmissionen mit Vorbedingungen, Schritten, Quest-State, Belohnungen, Scheitern und Wiederaufnahme modellieren.
**Abnahmekriterium:** Alle Missionsschritte besitzen eindeutige Auslöser, erfolgreiche und fehlerhafte Pfade.
**Abhängigkeiten:** 2, 4

### 12. Living World Simulator

**Status:** geplant / genehmigt
**Umfang:** NPC-Routinen, Fraktionen, Weltzustände, Handel, Tageszeiten, Wetter und reaktive Events ausarbeiten.
**Abnahmekriterium:** NPC-/Weltzustandsübergänge sind definiert, kompatibel mit Quests und speicherbar.
**Abhängigkeiten:** 4, 11

### 24. Procedural World Lab

**Status:** geplant / genehmigt
**Umfang:** Biom-Baupläne, Terrain-Höhenkarten, deterministische Seeds, Wege, Vegetationsregeln, World-Partition-Zellen und PCG-Aufträge für Unreal erstellen.
**Abnahmekriterium:** Jede Region hat Seed, Maßeinheit, Eingaben, PCG-Parameter, Streaming-Budget, World-Partition-Plan und sichtbare Referenzen.
**Abhängigkeiten:** 4, 9, 17

### 26. Quest Deadlock Simulator

**Status:** geplant / genehmigt
**Umfang:** Quest- und Dialog-Graphen auf erreichbare Ziele, Sackgassen, unerfüllbare Bedingungen, widersprüchliche Zustände und fehlende Fortschrittswege simulieren.
**Abnahmekriterium:** Alle definierten Pflichtmissionen können unter dokumentierten Startbedingungen abgeschlossen werden; blockierende Wege erzeugen reproduzierbare Gegenbeispiele.
**Abhängigkeiten:** 2, 11

## Phase III – Produktionsvorbereitung

Freigegebene Referenzen und präzise Blender-/Unreal-Aufträge erstellen

### 8. Blender Production Master

**Status:** geplant / genehmigt
**Umfang:** Vorgaben für Maßstab, Polygonziele, Topologie, UV, PBR, LOD, Rigs, Animationen, Kollisionsobjekte und Exportprofile erstellen.
**Abnahmekriterium:** Blender-Auftrag enthält Eingaben, Modell-/Exportnamen, technische Limits und überprüfbare Asset-Abnahme.
**Abhängigkeiten:** 3, 7, 14

### 9. Unreal Blueprint Architect

**Status:** geplant / genehmigt
**Umfang:** Versionierte UE-Architektur mit C++-Klassen, Blueprint-Interfaces, Datenobjekten, Input, Speichern und Build-Tests spezifizieren.
**Abnahmekriterium:** Claude-Export besitzt Modulgraph, Reihenfolge, Schnittstellen, Definition-of-Done und Testanforderungen.
**Abhängigkeiten:** 4, 5, 7

### 13. Sound & Voice Director

**Status:** geplant / genehmigt
**Umfang:** Sound-Cue-Katalog, Musikmotive, Dialogline-IDs, Stimmrollen, Raumklang, Untertitel-Synchronität und Rechteangaben.
**Abnahmekriterium:** Jede verpflichtende Szene und Aktion referenziert Audio oder dokumentiert bewusst stumme Ausführung.
**Abhängigkeiten:** 2, 6

### 14. Referenzbild-Qualitätsprüfer

**Status:** geplant / genehmigt
**Umfang:** ChatGPT-Referenzprompts, Bildansichten, Dimensionsregeln, Stil-Konsistenz und menschliche Freigabe nach Import verwalten.
**Abnahmekriterium:** Pflichtbilder werden pro Asset gezählt; Inkonsistenzen sperren Bild-Freigabe, bis behoben/begründet.
**Abhängigkeiten:** 3, 4, 7

### 25. Real Asset Validator

**Status:** geplant / genehmigt
**Umfang:** Importierte .blend- und 3D-Asset-Berichte auf Größe, Achsen, Polygonbudget, UVs, PBR-Texturen, LODs, Rigging, Namenskonventionen und Exportparameter prüfen. Binäre Prüfung braucht passende Prüftools.
**Abnahmekriterium:** Für jedes geprüfte Asset liegt ein maschinenlesbarer Bericht mit Datei-Hash, Prüfregeln, Fehlern, Warnungen und nachprüfbarem Resultat vor.
**Abhängigkeiten:** 8, 14

### 28. Reusable Game Systems

**Status:** geplant / genehmigt
**Umfang:** Wiederverwendbare, versionierte Vorlagen für Inventar, Save/Load, Input, Kamera, Quest-Tracking und Dialoge definieren; projektspezifische Logik getrennt halten.
**Abnahmekriterium:** Systemvorlage hat klaren Vertrag, dokumentierte Versionsnummer, Ein- und Ausgaben und einen isolierten Integrationstest pro Zielprojekt.
**Abhängigkeiten:** 7, 9

### 32. Animation Retarget Studio

**Status:** geplant / genehmigt
**Umfang:** Skelettstandards, Animationsbenennungen, Retarget-Profile, Motion-Matching-Daten und Übergänge als Blender- und Unreal-Aufträge definieren.
**Abnahmekriterium:** Bewegungsclips sind zugewiesen und auf Zielrig mit definierten Testposen geprüft; Fußgleiten, Root Motion und Bone-Fehler dokumentiert.
**Abhängigkeiten:** 3, 8, 9

### 33. Physics Reality Suite

**Status:** geplant / genehmigt
**Umfang:** Masse, Skalierung, Gravitation, Kollisionen, Chaos-Constraints, Fahrzeuge, Wasserreaktionen und physikalische Extremfälle als testbare Vorgaben planen.
**Abnahmekriterium:** Szenen mit messbaren Sollwerten für Stabilität, Geschwindigkeit, Kollision und Frame-Budget besitzen nachgewiesene Tests in Unreal.
**Abhängigkeiten:** 4, 8, 9, 17

### 35. Dialogue & Lip-Sync Director

**Status:** geplant / genehmigt
**Umfang:** Sprecherrollen, Sprachdatei-IDs, Lokalisierung, Phoneme, Gesichtsanimationen, Kamera- und Untertitel-Timings je Dialog verknüpfen.
**Abnahmekriterium:** Dialogsequenzen enthalten vollständige Event-Timelines, Audio-Assets, Fallbacks und synchronisierte Abnahmetests.
**Abhängigkeiten:** 2, 3, 6, 13

### 36. Multiplayer Architecture Switch

**Status:** geplant / genehmigt
**Umfang:** Optionales Multiplayer-Profil mit Serverautorität, Zustandsreplikation, Sessions, Netzausfällen, Lobby- und Anti-Cheat-Anforderungen planen; standardmäßig Singleplayer.
**Abnahmekriterium:** Nur bei aktivem Multiplayer-Profil werden Netzwerkaufträge exportiert; mit Profil liegen Topologie, Security-Threats und Synchronisationstests vor.
**Abhängigkeiten:** 9, 10

## Phase IV – Umsetzung & Qualität

Claude-Handoff, Tests, Performance und Token-Optimierung absichern

### 10. Autonomous QA Director

**Status:** geplant / genehmigt
**Umfang:** Tests für Kompilierung, Gameplay, Save/Load, Regression, visuelle Checks, Performance und manuelle Gates definieren.
**Abnahmekriterium:** Jeder Fertigstatus verlangt realen Testbeleg; rote Tests sperren Releasefreigabe.
**Abhängigkeiten:** 9, 18

### 17. Performance Architect

**Status:** geplant / genehmigt
**Umfang:** Ziel-Hardware, Framerate, Auflösung, Speichergrenzen, Streaming, LOD und GPU-/CPU-Budgets je Grafikstil definieren.
**Abnahmekriterium:** Performance-Budget und Messprofil sind im Produktionspaket festgelegt; Abweichungen werden protokolliert.
**Abhängigkeiten:** 8, 9

### 18. Claude Precision Export

**Status:** geplant / genehmigt
**Umfang:** Präzise ZIP-Handoff-Pakete mit Game-Bible, Bildreferenzen, Dateiindex, DAG-Aufträgen, MCP-Checkliste, Tests und Fortsetzungszustand.
**Abnahmekriterium:** Jede Task besitzt Eingaben, Schritte, Abhängigkeiten, Abnahme und gültige Pfade; Paket ist reproduzierbar.
**Abhängigkeiten:** 1, 7, 8, 9, 11, 14

### 19. Kosten- und Tokenoptimierung

**Status:** geplant / genehmigt
**Umfang:** Kontext selektiv laden, Prompt-Deduplizierung, Versions-Deltas, zwischengespeicherte Analysen und nachvollziehbares Budget.
**Abnahmekriterium:** Export/Arbeitsauftrag verarbeitet bei unveränderten Quellen nur notwendige Deltas ohne Kanonverlust.
**Abhängigkeiten:** 1, 7, 18

### 27. Vertical Slice Studio

**Status:** geplant / genehmigt
**Umfang:** Aus kompletter Spielbibel einen kleinen, tatsächlich spielbaren Abschnitt mit klaren Grenzen, referenzierten Assets, Aufgaben und echten Tests definieren.
**Abnahmekriterium:** Abgenommener Slice hat startbaren Build, Spielstart, mindestens einen vollständigen Gameplay-Loop, gespeicherten Testbeleg und Abnahmereport.
**Abhängigkeiten:** 8, 9, 10, 18

### 29. Savegame Migration Lab

**Status:** geplant / genehmigt
**Umfang:** Versionierte Savegame-Schemata und Migrationspfade für Hauptspiel-Updates und DLCs samt Rückwärtskompatibilität und Test-Szenarien spezifizieren.
**Abnahmekriterium:** Referenz-Speicherstände werden in einer Testumgebung fehlerfrei migriert, Ausnahmen protokolliert und Datenverlust ausgeschlossen oder explizit begründet.
**Abhängigkeiten:** 9, 15, 16

### 31. Accessibility & Controls Lab

**Status:** geplant / genehmigt
**Umfang:** Matrizen für remappbare Steuerung, alternative Eingaben, Untertitel, Kontraste, Lesbarkeit, Barrierefreiheitsoptionen und reale Controller-Tests erstellen.
**Abnahmekriterium:** Alle gewählten Zielplattformen besitzen Eingabeprofile, Abnahmefälle und dokumentierte praktische Tests oder ausdrücklich erfasste Lücken.
**Abhängigkeiten:** 9, 10, 20

### 34. Visual Fidelity Benchmark

**Status:** geplant / genehmigt
**Umfang:** Freigegebene Konzeptreferenzen mit standardisierten Unreal-Screenshots vergleichen und Abweichungen bei Licht, Material, Silhouette und Stimmung dokumentieren.
**Abnahmekriterium:** Jeder Vergleich speichert Referenz, Render, Kameraparameter, Bewertungsrubrik und dokumentierte Abnahme durch Nutzer.
**Abhängigkeiten:** 8, 10, 14, 17

## Phase V – Release & Erweiterungen

Versionierte Releases und DLC-Produktionsstrecken herstellen

### 15. DLC Expansion Studio

**Status:** geplant / genehmigt
**Umfang:** DLCs dem Basisspiel zuordnen, Story-/Asset-Abhängigkeiten und Kompatibilität gegen konkrete Spielversionen prüfen.
**Abnahmekriterium:** Ein DLC lässt sich separat exportieren und meldet inkompatible Basisversionen und fehlende Asset-IDs.
**Abhängigkeiten:** 7, 9, 18

### 16. Game Evolution System

**Status:** geplant / genehmigt
**Umfang:** Bestehende Releases versioniert verbessern: Änderungswünsche, Regressionen, Branches, Migrationspläne und Patch-Freigaben.
**Abnahmekriterium:** Ein Nachfolge-Release bewahrt Originalstände und zeigt alle Änderungen sowie Rückrollmöglichkeit.
**Abhängigkeiten:** 7, 10, 15

### 20. Release & Publishing Center

**Status:** geplant / genehmigt
**Umfang:** Reproduzierbare Builds, Installer, Plattformprofile, Credits, Rechte, Controller, Barrierefreiheit, Lokalisierung und Store-Pakete vorbereiten.
**Abnahmekriterium:** Freigabe nur mit bestandenem Testplan, Build-Artefakt, Quellenarchiv und überprüfter Release-Checkliste.
**Abhängigkeiten:** 10, 15, 16, 17, 18

### 38. Modding & Community Studio

**Status:** geplant / genehmigt
**Umfang:** Optionales Modding-Konzept mit Plugin-/Content-Format, Versionskompatibilität, Sandbox-Regeln, Berechtigungen und kontrolliertem Installationsprozess.
**Abnahmekriterium:** Mod-Paket kann in einer isolierten Testumgebung installiert und entfernt werden; fremde Dateien dürfen keine ungeprüften Produktionsskripte starten.
**Abhängigkeiten:** 15, 16, 20

## Claude-Code-Umsetzungshinweise

- Erst vorhandene Daten importieren und auf Vollständigkeit prüfen; Originaldateien niemals überschreiben.
- Jede Aufgabe enthält Inputs, Outputs, verbindliche Quellen, klare Grenzen und überprüfbare Akzeptanzkriterien.
- Referenzbilder werden weiterhin separat hier in ChatGPT erzeugt und anschließend importiert; keine integrierte OpenAI-API.
- Blender/Unreal werden erst in der eigentlichen Produktion über konfigurierte MCP-Integrationen von Claude Code bedient.
- Keine abgeschlossenen Builds oder aktive MCP-Verbindung vortäuschen.
- Rejected-IDs strikt aus neuen Feature-Entwicklungsaufträgen ausschließen.


---

## Zusätzlich freigegeben: Claude-Code-Agenten 1–20

Alle 20 Rollen (Studio Director, Game Design, Story, Mission, Character/Boss, Reference, World, Blender, Animation, Material, Unreal, Combat/AI, Physics, Cinematic, UI, Sound, Game Systems, Performance, QA, DLC/Release) sind vom Nutzer verbindlich genehmigt. Rollen, Toolrechte, MCP-Abgrenzung, Desktop-/Handy-Nutzung und Beispiel-Workflows siehe `TEAM_ARCHITEKTUR_20_AGENTEN.md`. Agenten-Definitionen werden projektbezogen unter `.claude/agents/` eingerichtet. **Genehmigt und vorbereitet bedeutet nicht laufend, verbunden, vollständig implementiert oder getestet.**
