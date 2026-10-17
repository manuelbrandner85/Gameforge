# GAMEFORGE GODMODE — Vollständigkeitskatalog (80 Module)

**Grundsatz:** Kein Modul ausblenden: entweder `required/specification_pending`, `specified`, oder mit belegter Begründung `not_applicable`. `specified` ist NICHT `implemented`, `tested`, `approved`.


## 01 Design

### GF-001 · Spielvision (Immer)
- Arbeitstitel und Pitch
- Zielgruppe und Altersrahmen
- Genre und Subgenre
- USP und Spielerlebnis
- Zielplattformen und Eingabegeräte
- Erfolgsdefinition
**Abnahme:** Eine dritte Person kann Spielziel, Spielerrolle und Zielplattform ohne Rückfragen erklären.

### GF-002 · Umfang und Produktionsplan (Immer)
- Spielumfang und Feature-Priorität
- Meilensteine und Abhängigkeiten
- Aufwands und Hardwarebudget
- MVP und Vertical Slice
- Risiken und Notfallumfang
- Definition of Done
**Abnahme:** Für alle Meilensteine liegen überprüfbare Ergebnisse und Grenzen vor.

### GF-003 · Design Bible und Kanon (Immer)
- Verbindliche Terminologie und Schreibregeln
- Stilregeln und Inspirationsabgrenzung
- Unveränderliche Entscheidungen
- Entscheidungsprotokoll
- Veto und Freigabeprozess
- Kanon-Versionierung
**Abnahme:** Widersprüche zwischen Dokumenten werden erkannt und aufgelöst.

### GF-004 · Game Loop und Spielregeln (Immer)
- Sekunden- und Minuten-Spielschleife
- Ziel und Versagensbedingungen
- Grundmechaniken mit Zahlenwerten
- Schwierigkeitskurve
- Feedback und Belohnungen
- Pausen und Neustartverhalten
**Abnahme:** Eine minimal spielbare Regelrunde ist eindeutig formulierbar.

### GF-005 · Genre-Profile (Immer)
- Vordefinierte Spieltypen
- Retro/Pixel/Low Poly/Stylized/Realistisch/AAA-Look
- 2D/2.5D/3D
- Perspektiven
- Einzelspieler/Koop/Multiplayer
- Optionale Funktionen mit begründetem N/A
**Abnahme:** Aktivierte Funktionen widersprechen nicht Plattform oder Projektumfang.

### GF-006 · Spielerführung und Onboarding (Immer)
- Tutorial und kontextuelle Hilfen
- Erste 5 Spielminuten
- Hints und Ziele
- Fehlereingaben und Rückmeldung
- Schwierigkeitsanpassung
- Wiedereinstieg
**Abnahme:** Spielende verstehen ohne externe Erklärung, wie sie beginnen und Fortschritte erzielen.


## 02 Narrative

### GF-007 · Weltenkanon und Lore (Bedingt: narrative)
- Historie und Zeitachse
- Orte und Fraktionen
- Magie/Technik/Religion als Spielweltregeln
- Kartenbezüge
- Ursache-Wirkung-Konflikte
- Wissen der NPCs
**Abnahme:** Keine widersprüchlichen Ereignisse, Orte oder Figurenbeziehungen.

### GF-008 · Hauptstory komplett (Bedingt: narrative)
- Prämisse und Themen
- Prolog und Einstieg
- Alle Akte und Kapitel
- Wendepunkte und Enthüllungen
- Finale und Abspann
- Chronologie und Spannungsbogen
**Abnahme:** Jeder Handlungsabschnitt hat Auslöser, Ablauf, Ergebnis und Abhängigkeiten.

### GF-009 · Dialogskripte (Bedingt: narrative)
- Dialog-IDs
- Sprechende und Hörer
- Alle Textzeilen
- Antwortauswahl
- Bedingungen und Konsequenzen
- Audio/Untertitel und Sprecherhinweise
**Abnahme:** Jede Dialogverzweigung endet definiert oder führt zu einem gültigen Knoten.

### GF-010 · Questdesign (Bedingt: quests)
- Main- und Sidequests
- Quest-IDs
- Startbedingungen
- Ziele und Zwischenziele
- Fehler-/Abbruchfälle
- Belohnungen und Rückwirkungen
- Quest-Sperren und Zustandsautomaten
**Abnahme:** Es gibt keine unerreichbaren Hauptquests oder Sackgassen ohne Lösung.

### GF-011 · Entscheidungen und Enden (Bedingt: narrative)
- Knoten-/Variablenliste
- Karma/Ansehen und Fraktionswerte
- Bedingungen der Enden
- Speicherkonsequenzen
- Endsequenzen
- Logische Erreichbarkeit
**Abnahme:** Alle vorgesehenen Enden sind unter dokumentierten Bedingungen erreichbar.

### GF-012 · Cutscenes Prolog Epilog (Bedingt: cinematics)
- Shotlist und Storyboard
- Dialog und Timing
- Kamerapositionen
- Animations-/VFX-/Audio-Cues
- Gameplay-Übergänge
- Überspringen/Wiederholen
- Fehlerfälle und Speicherpunkte
**Abnahme:** Eine Szene ist von Beginn bis Rückgabe der Spielersteuerung vollständig beschrieben.


## 03 Referenzen

### GF-013 · Visuelle Art Bible (Immer)
- Farbpalette und Kontrast
- Stilebene pro Assetklasse
- Beleuchtung und Look
- Materialkatalog
- Größenreferenzen
- Bildsprache und UI-Stil
**Abnahme:** Jedes neue Asset lässt sich auf den gewählten Stil abgleichen.

### GF-014 · Referenzbild-Sets (Immer)
- Eindeutige IDs und Dateipfade
- Front/Seite/Rücken und Detailansichten wo sinnvoll
- Farben und Material-Callouts
- Maßstab
- Posen und Silhouetten
- Version und Freigabe
- Urheber-/Nutzungsnachweis
**Abnahme:** Referenzsets decken Herstellungsansichten ab; fehlende Bilddateien blockieren Export.

### GF-015 · 2D/Sprite/Retro-Pipeline (Bedingt: retro_2d)
- Pixelauflösung und Seitenverhältnis
- Sprite Sheets und Flipbooks
- Animationsraster und FPS
- Tile-Sets und Levelkacheln
- Collision Shapes
- Scaling/Filtering
- Palette und UI-Sprites
**Abnahme:** Sprites sind als testbare Animationen und Kollisionen spezifiziert.

### GF-016 · 3D-Modellbau (Bedingt: three_d)
- Maße und Achsen
- High-/Low-Poly
- Topology und Polygonbudget
- UV-Unwrapping
- Collision Meshes
- LOD/HLOD Strategie
- Dateiformat .blend und Export
- Asset-Pivot und Benennung
**Abnahme:** Ein Import-Test erzeugt korrekte Skala, Ausrichtung, Pivot und Materialsätze.

### GF-017 · Materialien Texturen Shader (Bedingt: three_d)
- PBR-Maps
- Texel-Density und Auflösung
- UV-Packing
- Materialslots und Shaderverwendung
- Transparenz und SSS
- Performancebudgets
- Import- und Farbmanagement
**Abnahme:** Material ist in Engine reproduzierbar und bewegt sich im Speicherbudget.

### GF-018 · Rigging und Animationen (Bedingt: three_d)
- Skelett-Hierarchie
- Root Motion Regeln
- IK/Retargeting
- Facial Blendshapes
- Bewegungsbibliothek
- Animation-State-Machine
- Montages und Events
- Export und Tests
**Abnahme:** Animationsliste deckt die vorgesehenen Gameplayzustände und Übergänge ab.

### GF-019 · Charakterproduktion (Bedingt: characters)
- Character-ID und Biografie
- Körperform und Proportionen
- Outfit-Varianten
- Gesichts- und Haarreferenzen
- Materialien und Rig
- Hitboxes
- Ausrüstungs-Sockets
- LOD
- Stimmprofil
**Abnahme:** Jede Figur besitzt zusammengehörige Daten, Ansichten und Unreal-Zuordnung.

### GF-020 · Props Waffen Gebäude (Bedingt: three_d)
- Objektliste und eindeutige IDs
- Funktion und interaktive Zustände
- Größe und Maßstab
- Kollisionsregeln
- Material- und LOD-Vorgaben
- Varianten und Instancing
- Positionen und Referenzbilder
**Abnahme:** Jedes Objekt ist korrekt einer Szene oder einem Spielsystem zugeordnet.


## 04 Welt

### GF-021 · Leveldesign und Navigation (Immer)
- Levelübersicht
- Start/Exit/Respawn
- Landmarks und Orientierung
- Laufwege und Sichtlinien
- Begegnungsdesign
- Sammelobjekte/Trigger
- Navigation und Blockaden
**Abnahme:** Der gesamte kritische Weg ist mit den vorgesehenen Fähigkeiten erreichbar.

### GF-022 · Open World und Streaming (Bedingt: open_world)
- Weltkarte mit Regionen
- Koordinaten und Maßstab
- World Partition Zellen
- Data Layers
- POIs und Reisepfade
- Streaming/Spawn Budgets
- Sicherheits-/Fallbackzonen
- Schnellreise
**Abnahme:** Weltregionen laden und entladen ohne verlorenen Questfortschritt.

### GF-023 · Biomes Wetter Tageszeiten (Bedingt: weather)
- Biome-Liste
- Jahreszeiten und Wetterwahrscheinlichkeiten
- Tag/Nacht-Zyklus
- Beleuchtung
- Gameplayauswirkungen
- Audio/Partikel
- Speicherzustand und Performance
**Abnahme:** Zustandswechsel zeigen konsistente Grafik- und Gameplayreaktionen.

### GF-024 · Prozedurale Generierung (Bedingt: procedural)
- Seed und Reproduzierbarkeit
- Generierungsalgorithmen
- Regel- und Qualitätsgrenzen
- POI-Placement
- Navigation
- Optimierung und Bake-Schritte
- Regenerationsschutz
**Abnahme:** Gleicher Seed liefert reproduzierbaren nutzbaren Inhalt.

### GF-025 · Interaktion Rätsel und Trigger (Immer)
- Interaktionsarten und Prioritäten
- Öffnen/Schließen/Benutzen
- Puzzles und Hinweise
- Triggerzustände
- Reset/Fehlerbehandlung
- Bedienoberfläche/Audio-Feedback
**Abnahme:** Alle notwendigen Interaktionen sind auslösbar, rückmeldend und zustandssicher.


## 05 Gameplay

### GF-026 · Steuerung und Input (Immer)
- Keyboard Maus Gamepad und Rebinding
- Input Actions/Contexts
- Tastenbelegung
- Dead Zones und Sensitivität
- Controller Icons
- Pause und Menüsteuerung
- Konfliktbehandlung
**Abnahme:** Kernspiel ist auf allen ausgewählten Eingabegeräten bedienbar.

### GF-027 · Kamera und Perspektiven (Immer)
- First/Third/Top Down/Fixed
- Kameraabstand/FOV
- Kollision und Sichtschutz
- Zielen und Lock-On
- Cinematic Übergänge
- Motion Sickness und Einstellungen
**Abnahme:** Keine spielkritische Sichtblockade in wichtigen Situationen.

### GF-028 · Bewegung Fortbewegung (Immer)
- Laufen/Springen/Schwimmen/Klettern je Profil
- Beschleunigung und Trägheit
- Stamina und Gelände
- Treppen/Abgründe
- Animation Sync
- Sonderfälle und Anti-Stuck
**Abnahme:** Bewegungszustände haben konkrete Übergänge und Kollisionsregeln.

### GF-029 · Kampf Schadenssystem (Bedingt: combat)
- Treffer-/Block-/Ausweichfenster
- Schadensformeln und Resistenz
- Nah-/Fernkampf
- Lock-On und Kamera
- Hit-Reactions
- Balancewerte
- Tod/Respawn
- PvE/PvP Varianten
**Abnahme:** Alle Angriffsarten haben Start, Trefferprüfung, Konsequenz und Ende.

### GF-030 · Fähigkeiten und Statuswerte (Bedingt: abilities)
- Attribute und Ressourcen
- Fähigkeits-IDs
- Kosten/Cooldowns
- Gameplay Tags/Effekte
- Freischaltung
- VFX/SFX/Animation
- Abbruchfälle
- Persistenz
**Abnahme:** Fähigkeiten überschneiden sich nicht widersprüchlich und sind testbar.

### GF-031 · Gegner KI und Verhalten (Bedingt: enemies)
- KI-Archetypen
- Wahrnehmung und Sicht
- Navigation/Patrouille
- Suche/Angriff/Rückzug
- Gruppenkoordination
- Schwierigkeit
- Debug-Modi
- Loot und Respawn
**Abnahme:** Gegner reagieren stabil auf Spieleraktion und scheitern nicht an Navigation.

### GF-032 · Bosskämpfe und Phasen (Bedingt: bosses)
- Boss-Biografie und Arena
- Telegraphing
- Phasen und Zustandswechsel
- Movesets/Cooldowns
- Balancing
- Audio/VFX/Animationen
- Checkpoints
- Loot/Story-Ergebnis
- Fehlerrücksetzung
**Abnahme:** Jede Bossphase ist spielbar, lesbar und zuverlässig abschließbar.

### GF-033 · NPCs Fraktionen Tagesroutinen (Bedingt: npcs)
- NPC-Profile
- Dialog und Beziehungen
- Tagesablauf und Jobs
- Quest-Schnittstellen
- Verhalten bei Gewalt/Alarm
- Inventar/Handel
- Reputationssystem
- Fallback-Spawn
**Abnahme:** Wichtige NPCs bleiben erreichbar und verursachen keine Questblockaden.

### GF-034 · Inventar Ausrüstung Items (Bedingt: inventory)
- Item-IDs und Kategorien
- Gewicht/Slots/Stacks
- Ausrüstungsslots
- Loot Tables
- Drop/Pickup
- Seltenheit/Stats
- UI und Sortierung
- Verlust und Persistenz
**Abnahme:** Keine Duplizierung/Verluste bei Speichern, Wechsel oder Tod.

### GF-035 · Ressourcen Handel Wirtschaft (Bedingt: economy)
- Währungen und Preise
- Händler
- Preisregeln und Handelslimits
- Belohnungen und Sinks
- Loot-Balance
- Anti-Exploit
- UI und Speicherstände
**Abnahme:** Wirtschaftssimulation hat definierte Preise und verhindert triviale Exploits.

### GF-036 · Crafting Bauen Rezepte (Bedingt: crafting)
- Ressourcen und Werkzeuge
- Rezept-IDs
- Produktionszeiten
- Werkbänke
- Fehlschlag und Rückgabe
- Bauen/Platzieren
- Persistenz
- UI
**Abnahme:** Jede Rezeptabhängigkeit ist erfüllbar und sicher speicherbar.

### GF-037 · Fortschritt Skills Upgrades (Bedingt: progression)
- XP/Level-/Skillkurven
- Skilltrees und Voraussetzungen
- Respec
- Klassen/Ränge
- Stat-Balance
- Freischaltbedingungen
- New Game Plus ggf.
**Abnahme:** Keine toten Skillpfade und kein unabsichtlicher Fortschrittsverlust.

### GF-038 · Stealth Alarm Tarnung (Bedingt: stealth)
- Sicht-/Hörreichweiten
- Deckung
- Verdachtszustände
- Alarmverteilung
- Takedowns
- Ablenkungen
- UI/Audiofeedback
- Resetregeln
**Abnahme:** Erkennung ist nachvollziehbar und reproduzierbar testbar.


## 06 Physik

### GF-039 · Kollision und Physikgrundlagen (Immer)
- Kollisionsebenen/Kanäle
- Masse/Schwerkraft
- Physikmaterialien
- Ragdoll falls benötigt
- Interaktive Physik
- Numerische Stabilität
- Maximalbudgets und Fallbacks
**Abnahme:** Keine fallenden Spieler, endlosen Kollisionen oder unerklärlichen Physiksprünge.

### GF-040 · Fahrzeuge Reiten Flug (Bedingt: vehicles)
- Fahrzeugklassen
- Steuerung/Kamera
- Reifen/Antrieb/Traktion
- Kollision/Schaden
- Ein-/Aussteigen
- KI-Verkehr
- Audio und VFX
- Netzwerk/Persistenz ggf.
**Abnahme:** Fahrzeug kann vollständig benutzt und wieder verlassen werden.

### GF-041 · Wasser Schwimmen Tauchen (Bedingt: water)
- Wasserzonen
- Buoyancy/Wellen
- Schwimm-/Tauchsteuerung
- Sauerstoff und Strömung
- Unterwasserkamera
- Audio/Shader
- Kollision und Performance
**Abnahme:** Übergang zwischen Land und Wasser funktioniert stabil.

### GF-042 · Zerstörung Feuer Stoff Haar (Bedingt: destruction)
- Zerstörbare Teile
- Chaos Fracturing
- Partikel und Debris
- Feuer-/Rauchregeln
- Cloth/Hair falls benutzt
- Baukosten/LOD
- Zurücksetzen und Savezustand
**Abnahme:** Dynamische Effekte bleiben deterministisch genug und performant.


## 07 Präsentation

### GF-043 · Hauptmenü Settings HUD (Immer)
- Splash/Start/Hauptmenü
- Spiel neu/laden/weiter
- Pause/Settings/Verlassen
- HUD-Layouts und Zustände
- Navigation und Fokus
- Auflösungen/Skalierung
- Fehlermeldungen und Ladeanzeigen
**Abnahme:** Alle Menüpfade inklusive Abbruch und Zurück führen zum korrekten Ziel.

### GF-044 · Ton Geräusche Musik (Immer)
- Musikthemen/Loops
- SFX-Liste
- Ambience und Räume
- Dynamische Musik-Cues
- 3D-Audio/Attenuation
- Lautstärke-Mixer
- Lizenz und Format
- Fallback ohne Audio
**Abnahme:** Jede spielkritische Aktion hat passendes akustisches oder visuelles Feedback.

### GF-045 · Sprachausgabe und Lipsync (Bedingt: voice)
- Sprecherliste und Castingprofil
- Dialog-Audio-IDs
- Voiceover-Aufnahmeanweisungen
- Lipsync/Face Animation
- Timing und Emotion
- Versionen/Lizenzen
- Fallback-Text
**Abnahme:** Sprachdatei, Sprecher, Untertitel und Szene sind exakt verknüpft.

### GF-046 · VFX und Gamefeel (Immer)
- Hit-Feedback
- Partikelkatalog
- Haptik/Kamera-Impulse
- Übergänge und Interaktionsfeedback
- Visuelle Lesbarkeit
- Accessibility-Schalter
- Performance-Limits
**Abnahme:** Spielkritische Rückmeldung ist visuell/akustisch klar, nicht überladen.

### GF-047 · Untertitel Accessibility (Immer)
- Untertitel/Audio-Captions
- Textgröße/Kontrast
- Farbenblindheitsoptionen
- Input-Remapping
- Motion-Reduction
- Schwierigkeitshilfen
- Testfälle
**Abnahme:** Kerninformationen sind nicht nur über Sound oder Farbe zugänglich.

### GF-048 · Lokalisierung Sprachen (Immer)
- Zielsprachen inkl. DE/EN/IT falls gewünscht
- String IDs
- UI-Längenregeln
- Datums/Zahlenformat
- Schriftzeichen
- Sprecher/Untertitelvarianten
- Übersetzungsworkflow
**Abnahme:** Keine fest codierten Texte in dafür vorgesehenen Oberflächen.


## 08 Grundtechnik

### GF-049 · Unreal Projektarchitektur (Immer)
- Engineversion
- C++ Klassenstruktur und Module
- GameInstance/GameMode/Controller/Pawn
- Subsysteme
- Blueprints vs C++
- Plugininventar und Kompatibilität
- Konfiguration
**Abnahme:** Projekt kompiliert auf gewählter Engine mit minimalem Testlevel.

### GF-050 · Datenmodell und Referenzen (Immer)
- Eindeutige IDs
- Game Data Tabellen/Assets
- Verweise und Beziehungen
- Tag-Namensräume
- Schemas und Versionen
- Konsistenzvalidator
- Migrationen
**Abnahme:** Keine kaputten internen Verweise und kein unbenannter Pflichtdatensatz.

### GF-051 · Speichern Laden Checkpoints (Immer)
- Persistente Zustandsliste
- SaveGame-Versionierung
- Autosave/Manual Save
- Quests/Inventar/Position
- Recovery nach Crash
- Mehrere Slots
- Integrität/Backup
- New Game/Reset
**Abnahme:** Save->Exit->Load reproduziert wesentliche Spielzustände.

### GF-052 · Mehrspieler Netcode (Bedingt: multiplayer)
- Koop/PvP/Servermodell
- Replikation und Prediction
- Lobby/Matchmaking
- Join/Leave
- Datenautorität
- Lag/Disconnect-Reconnect
- Netzwerktests
- Serverbetrieb
**Abnahme:** Mindestens zwei Clients erhalten konsistente entscheidende Zustände.

### GF-053 · Online Dienste Datenschutz (Bedingt: online)
- Account/Auth wenn benötigt
- Cloud-Saves/Erfolge
- Serverstatus
- Datenerhebung und Opt-in
- Moderation/Meldung
- Datenschutz und Löschprozesse
- Servicefehler und Offlineverhalten
**Abnahme:** Ausfälle und Privatsphäreanforderungen sind ausdrücklich getestet.

### GF-054 · Mobile VR Konsolenprofile (Bedingt: special_platforms)
- Plattformspezifische Eingaben
- Auflösung und Touch/VR-Komfort
- Shader- und Speicherlimits
- Rechte/SDKs
- Offline/Online Policies
- Store Vorgaben
- Device-Matrix
**Abnahme:** Zielhardware-spezifische Anforderungen haben eigene Tests.

### GF-055 · Blender Asset-Pipeline (Bedingt: three_d)
- Versionsfixierung
- Datei-/Assetnamen
- Maßstab Achsen/Rotation
- Export FBX/glTF nach Eignung
- UV/Animation/Testimport
- Assetregistrierung
- Reimport und Fehlerlog
**Abnahme:** Exportiertes Modell kann reproduzierbar in Unreal importiert werden.

### GF-056 · Claude MCP Handoff (Immer)
- CLAUDE.md Einstiegsdatei
- Unreal MCP Preflight
- Blender MCP Preflight
- Tool Capability Matrix
- Arbeitsaufträge in Reihenfolge
- Erlaubnisse/Sicherheitsgrenzen
- Fehler- und Retryprotokoll
- Tokenbudget
**Abnahme:** Keine MCP-Aktion ohne erfolgreiche lokale Verfügbarkeitsprüfung.

### GF-057 · Repository Backups Versionen (Immer)
- Git Branches und Tags
- Assetstrategien Git LFS/Perforce
- Backups vor destruktiven Schritten
- Versionspinning
- Rebuild/Reproduzierbarkeit
- Rollback/Ownership
- Keine Secrets im Repo
**Abnahme:** Restore-Test funktioniert nach simulierter fehlerhafter Änderung.


## 09 Testing

### GF-058 · Testpyramide und Testfälle (Immer)
- Unit/Integration/Systemtests
- Level Smoke Tests
- Mission- und Branch-Tests
- Save/Load Tests
- Asset Validation
- Screenshots/Regression
- Hardware-Tests
- Fehlerpriorität
**Abnahme:** Alle Freigabepunkte verweisen auf ausgeführte Tests mit Ergebnisbeleg.

### GF-059 · Performancebudgets (Immer)
- Ziel-FPS und Framezeit
- CPU/GPU/RAM/VRAM
- Auflösung und Hardwareklasse
- LOD/Nanite/Streaming
- Lastszenen
- Profiling Logs
- Shader/Builddauer Budgets
- Fallbackstufen
**Abnahme:** Worst-Case-Tests liegen innerhalb definierter Hardwarebudgets.

### GF-060 · Stabilität Sicherheitschecks (Immer)
- Crash-/Hang-Protokolle
- Datei/Modding-Sicherheit
- Input-Validation
- Abhängigkeitenscans
- Anti-Cheat wenn MP
- Privacy-Security
- Save-Korruption
- Berechtigungen
**Abnahme:** Keine bekannten Blocker der höchsten Priorität vor Freigabe.

### GF-061 · Balance Spielbarkeit Abnahme (Immer)
- Qualitative Spieltests
- Kampf- und Schwierigkeitstests
- Sackgassen
- Quest-Logik
- Framerate und Lesbarkeit
- Usability
- Abnahmeprotokoll
- Offene Issues
**Abnahme:** Feature ist erst fertig bei realem Build-Test und Nutzerfreigabe.


## 10 Release

### GF-062 · Build Packaging Installer (Immer)
- Target Windows/weitere Plattformen
- Development/Shipping Config
- Cook/Package/Sign falls nötig
- Abhängigkeiten/Redistributables
- Erster Start und Updateprozess
- Buildlog/Checksums
- Offline-Start
- Deinstallation
**Abnahme:** Ein sauberer Zielrechner kann das gebaute Spiel starten und spielen.

### GF-063 · Rechte Lizenzen und Einwilligungen (Immer)
- Asset-Herkunft und Nutzungsrechte
- KI-Inhalte und Nutzungsbedingungen
- Musik/Synchron/Likeness Rechte
- Open-Source-Lizenzen
- Marken/Datenschutz
- Credits
- Freigaben
- Drittanbieter-Regeln
**Abnahme:** Keine Produktionsassets ohne nachvollziehbare Herkunft und Erlaubnis.

### GF-064 · Store und Veröffentlichung (Bedingt: release)
- Storetexte und Tags
- Trailer/Screenshots/Kapseln
- Preis/Regionen
- Ratings soweit nötig
- Systemanforderungen
- Steam/Epic Store Review
- Release Notes
- Supportkontakt
**Abnahme:** Store- und Build-Freigabechecklisten für gewählte Plattform erfüllt.

### GF-065 · Updates Wartung Support (Bedingt: release)
- Patch-Versionierung
- Bug-Triage
- Save-Kompatibilität
- Telemetrie nur mit Rechtsbasis
- Rollbackstrategie
- Support-FAQ
- Crash-Reporting
- Roadmap
**Abnahme:** Patch verändert bestehende Spielstände ohne unbeabsichtigten Datenverlust.


## 11 Zusätze

### GF-066 · Strategie Aufbau Simulation (Bedingt: strategy)
- Ressourcenketten
- Bau- und Produktionslogik
- Einheiten-KI
- Pfadfindung
- Balance
- Ökonomie
- Tech Trees
- Siegesregeln
**Abnahme:** Simulationsergebnisse folgen reproduzierbaren Regeln.

### GF-067 · Racing Rennspiel (Bedingt: racing)
- Fahrphysik
- Strecken und Checkpoints
- Rundenzeiten und Regeln
- KI-Gegner
- Tuning
- Menüs/HUD
- Replay
- Kollisionsstrafen
**Abnahme:** Eine vollständige Runde mit gültiger Zeitwertung ist spielbar.

### GF-068 · RPG Rollenspiel (Bedingt: rpg)
- Klassen
- Skills und Stats
- Quests
- Gegenstände
- Dialog-/Beziehungsentscheidungen
- Fortschritt
- Schadenslogik
- Balance
**Abnahme:** Jeder vorgesehenen Character Build hat einen erreichbaren Spielpfad.

### GF-069 · Horror/Survival (Bedingt: survival)
- Angst/Spannungsbogen
- Licht und Sound
- Verstecken und Ressourcen
- Überlebensregeln
- Gegnerwahrnehmung
- Sichtbarkeit und Fairness
- Schock- und Safety-Optionen
**Abnahme:** Kernressourcen reichen unter dokumentierten Bedingungen zum Durchspielen.

### GF-070 · Eingabe/Plattform-Sonderfälle (Immer)
- Alt-Tab/Focus Lost
- Audio Device Disconnect
- Keyboard/Gamepad Hot-Swap
- Fenster-/Vollbildwechsel
- No Internet
- Erste-Installation
- Controller Disconnect
- Tastatur-Layoutvarianten
**Abnahme:** Kein Datenverlust oder Softlock bei typischen Umgebungswechseln.

### GF-071 · Kameras Fotomodus Replay (Bedingt: photo_mode)
- Photo-Mode Pause und Kamera
- UI-Hide
- DOF/Belichtung
- Speicherpfad
- Replay Daten
- Speicherkosten
- Urheberlogos
**Abnahme:** Foto und Wiederholung beeinträchtigen keine Missionen.

### GF-072 · Analytics und Nutzerauswertung (Bedingt: analytics)
- Ziel-/Erfolgsmessung
- Event IDs
- Einwilligung/Löschbarkeit
- Anonymisierung
- Dashboard
- Fehlerberichte
- Keine Geheimdaten
**Abnahme:** Alle Events sind dokumentiert und auf gewünschte Privatsphäre begrenzt.

### GF-073 · Mods UGC Editor (Bedingt: mods)
- Modding-API und Datenformat
- Sandbox
- Freigaben und Rechte
- Performancebudgets
- Import/Export
- Vertrauensmodell
- Kompatibilität
**Abnahme:** Fremdinhalte beeinflussen Kernspiel und Nutzerdateien nicht unkontrolliert.

### GF-074 · Achievements Leaderboards (Bedingt: achievements)
- Achievement IDs
- Trigger und Bedingungen
- Offline/Online Verhalten
- Fortschritt
- UI
- Missbrauchsprävention
- Store API Zuordnung
**Abnahme:** Erfolge werden nur bei erfüllter Bedingung ausgelöst und gespeichert.


## 12 Nachvollziehbarkeit

### GF-075 · Claude Aufgabenmatrix (Immer)
- Kleine atomare Tasks
- Eingabedateien und konkrete Outputs
- Abhängigkeiten
- MCP/Toolvoraussetzungen
- Akzeptanztests
- Status und Evidence-Pfade
- Retry/Blocker/Owner
**Abnahme:** Jeder Auftrag kann isoliert ausgeführt und nachweislich geprüft werden.

### GF-076 · Bild-/Asset-Authentizität (Immer)
- Datei ist vorhanden und lesbar
- Inhalt entspricht der Referenz
- Assetquelle und License
- Hash/Version
- Style/Model/Scene Mapping
- Status getrennt nach geplant/erzeugt/freigegeben
**Abnahme:** Kein Platzhalter wird als endgültiger 3D-/Bild-Asset gemeldet.

### GF-077 · Ende-zu-Ende Qualitätstore (Immer)
- G1 Design vollständig
- G2 Referenzen vorhanden
- G3 Claude Handoff konsistent
- G4 Vertical Slice testbar
- G5 Content vollständig
- G6 Performance/QA
- G7 Release und Abnahme
**Abnahme:** Ein Gate kann nur mit dokumentierten Beweisen auf bestanden wechseln.

### GF-078 · Komplexität Kosten Ressourcen (Immer)
- Hardwareprofil
- Kosten- und Zeitrahmen als Schätzung
- Anzahl Assets/Dialogzeilen/Levels
- Risiken und Engpässe
- Token-/API-Budget
- Jobpriorität
- Asset-Reuse
**Abnahme:** Unerfüllbare Zielvorgaben werden vor Produktion markiert.

### GF-079 · Referenz- und Logikgraph (Immer)
- Figuren-/Objekt-/Orts-IDs
- Crosslinks Quest zu Szene zu Asset
- Fehlende Referenzen
- Zyklische Taskabhängigkeiten
- Kanonkonflikte
- Versionssprünge
- Coverage-Metriken
**Abnahme:** Keine ungeklärten Pflichtverweise und keine Abhängigkeitszyklen.

### GF-080 · Claude Übergabeprotokoll (Immer)
- Versionsfixierung für Engine/Plugins
- Zip Manifest und Dateihashes
- Absolute Schritte zum Entpacken
- Runbook
- Erstprüfung
- Fortschrittszustände
- Abnahme und Fortsetzung nach Session-Ende
**Abnahme:** Ein neuer Claude-Chat kann ab gespeichertem Status ohne Annahmen fortfahren.

