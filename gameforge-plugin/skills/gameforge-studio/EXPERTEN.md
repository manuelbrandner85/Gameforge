# Experten-Rat – 52 Spielentwicklungs-Rollen

> Übernommen und ins Deutsche übertragen aus **UltraGameStudio** (wellingfeng, MIT-Lizenz, `app/src/lib/gameExperts.ts`, Stand 31.10.2026) – Lizenztext in `THIRD_PARTY_NOTICES.md`.
> Kein eigenes System: Die Rollen sind **Prüfblickwinkel**. Ausgeführt wird jede Arbeit von den GAMEFORGE-Agenten (Spalte „Agent“).

## So nutzt der Studio-Director den Rat
- Je Aufgabe **1–6 passende Rollen** wählen (einfach: 1–2 · normal: 3 · großes Feature/Architektur: „Rat“ mit bis zu 6). Nur Rollen der Engine des Projekts (`engine` in `spiel.json`: Unreal oder Godot); Unity/Web nur, wenn ein Projekt sie wirklich nutzt.
- Den Auftrag an den Agenten mit den **Leitlinien** der gewählten Rollen ergänzen; vor der Abnahme gegen deren **Grenzen** prüfen.
- Bei Widerspruch zwischen Rollen entscheidet die Kernerfahrung des Spiels (Spielbibel); bei Kanon/Story immer der Nutzer.

## Leitung
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Technical Director | Architektur, Risiko, Abwägung zwischen Systemen | Kernschleife und Systemgrenzen zuerst festlegen · lose gekoppelt, testbar, iterierbar · Entscheidungen markieren, die Spielstand, Netzwerk oder Performance betreffen | keine Abstraktion um ihrer selbst willen · keine großen Frameworks zu früh | studio-director |
| Creative Director | Vision, Grundton, kreative Abwägung zwischen Abteilungen | zurück zur Kernerfahrung und Zielgruppe · jede Abwägung dient der Identität des Spiels · umsetzbare kreative Grenzen statt Schlagworte | keine Feature-Anhäufung, die den Kern verwässert | game-design-director |
| Lead Programmer | Code-Architektur, Standards, Reviews, Umsetzungsgrenzen | zuerst Modulgrenzen und Datenfluss · riskante Änderungen in rücknehmbare Schritte teilen · Standards dienen Wartbarkeit, nicht Formalismus | nicht jedes Problem zur Neuarchitektur erklären | unreal-programming / godot-entwicklung |
| Producer | Meilensteine, Zeitplan, Risiko, Abhängigkeiten | in lieferbare Scheiben mit Abnahmekriterien teilen · Abhängigkeiten, Risiken, Verzugskosten offenlegen · Umfang begrenzen, um den Kern zu schützen | unbekannte Arbeit nie als sicheren Termin ausgeben | studio-director |

## Design
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Game Designer | Spielschleife, Regeln, Spielgefühl der Werte | Spielerverben, Ressourcen, Risiko und Belohnung klar benennen · einstellbare Parameter statt fest verdrahteter Erfahrung · kleinste spielbare Schleife zuerst prüfen | Grafik ersetzt keinen Spielbarkeitstest · keine Konzepte ohne konkrete Regeln | game-design-director |
| Systems Designer | Formeln, Zustände, Rezepte, Wechselwirkungen | Eingaben, Ausgaben, Formeln, Obergrenzen und Ausnahmen festlegen · komplexe Wechselwirkungen als Matrix mit Vorrang · alle Werte in Datentabellen/Konfiguration | keine Regeln, die nur im Code stehen | game-systems |
| Economy Designer | Ressourcen, Beute, Fortschrittskurven, Handel | Quellen, Senken, Obergrenzen und Inflationsrisiko festlegen · Beute- und Fortschrittskurven simulierbar · kurzfristige Belohnung und Langzeitziel in Schichten | keine unprüfbaren Bauchgefühl-Werte | game-systems |
| Level Designer | Raumaufbau, Begegnungen, Tempo, Erzählen durch Umgebung | Spielerziel, Weg, Sichtlinien und Risikotakt festlegen · Begegnungen schnell iterierbar · durch Raum führen statt durch Text | Level nicht nur per UI-Pfeil lenken | world-building |
| Live-Ops Designer | Saisons, Events, Battle Pass, Bindung | Ziel, Dauer, Belohnung, Auswertung jedes Events geschlossen planen · keine Ermüdung und keine Pflicht-Täglichaufgaben · Inhaltstakt passend zur Produktionskraft | keine ausbeuterische Bindungsmechanik | game-design-director |

## Programmierung
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Gameplay Programmer | Figuren, Fähigkeiten, Interaktion, Zustandsautomaten | Eingabe, Simulation und Darstellung trennen · Ereignisse/Daten statt gegenseitiger Skriptverweise · Grenzfälle und Fehlschläge abdecken | UI, Ton und Speicherlogik nicht in Kern-Spielklassen mischen | unreal-programming / godot-entwicklung |
| AI Programmer | NPCs, Verhaltensbäume, Wegfindung, Wahrnehmung | Wahrnehmung, Entscheidung und Ausführung trennen · Zustände sichtbar machen zum Debuggen · Rückfall bei Hängenbleiben, Zielverlust, Wegfehler | keine unpflegbaren langen If-Ketten | combat-enemy-ai |
| Network Programmer | Mehrspieler, Synchronisierung, Vorhersage, Rollback | zuerst Autorität und Synchronisierungsgranularität festlegen · deterministischen Zustand von Darstellungs-Interpolation trennen · Wiederverbinden, Cheats, Bandbreite bedenken | Einzelspieler-Zustand nicht 1:1 ins Netz übernehmen | netzwerk-multiplayer |
| Engine Programmer | Rendern, Physik, Speicher, Laden, Kernframework | Performance-Budget und Plattformgrenzen zuerst beziffern · Low-Level-Schnittstellen stabil, rücknehmbar, belastbar · Spielcode nicht an Engine-Interna binden | Kernframework nicht für ein einzelnes Feature aufbrechen | unreal-programming / godot-entwicklung |
| Tools Programmer | Editor-Werkzeuge, Import-Pipelines, Inhaltsproduktion | Inhaltsformate prüfbar und versionierbar · Fehlermeldungen für die Ersteller verständlich · Stapelverarbeitung mit klarem Rückweg | Einmal-Skripte nicht zur versteckten Produktionsabhängigkeit machen | unreal-programming / blender-3d |
| UI Programmer | HUD, Menüs, Inventar, Bedienzustände | Datenquelle, Anzeigezustand, Eingabe trennen · Fokus für Gamepad/Maus/Touch · Leer-, Gesperrt- und Ladezustand vorsehen | UI ändert nie direkt den Simulationszustand | ui-menu |
| Save Systems Engineer | Spielstände, Fortschritt, Migration | Laufzeit-, Einstellungs- und Dauerzustand trennen · Versionsnummer, Migration, Wiederherstellung bei Beschädigung · keine flüchtigen Darstellungszustände speichern | Objektverweise nie direkt als Speicherformat | game-systems |

## Engine – Unreal
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Unreal Specialist | Unreal, C++, Blueprint, GAS | Zugehörigkeit Actor/Component/Subsystem klären · Netzwerk: Autorität, Client, Replikation trennen · Blueprints zeigen nur, was Designer brauchen | nicht jedes Verhalten per Tick · Serverautorität nie ignorieren | unreal-programming |
| UE Blueprint Specialist | Blueprint-Architektur, C++-Grenze, BP-Optimierung | Komplexes in Funktionen, Komponenten oder C++ auslagern · nur nötige Designer-Stellschrauben · Tick, Schleifen und harte Verweise sparsam | kein Blueprint-Spaghetti | unreal-programming |
| UE GAS Specialist | Gameplay Ability System: Ability, Effect, Attribute, Tag | Zuständigkeiten von Ability/Effect/Attribute/Tag trennen · Vorhersage, Abklingzeit, Kosten und Abbruch einheitlich · Datenassets und C++/Blueprint-Grenze klar | kein paralleles Fähigkeitensystem neben GAS | unreal-programming / combat-enemy-ai |
| UE Replication Specialist | Replikation, RPC, Vorhersage, Relevanz, Bandbreite | Grenzen zwischen Zustandsreplikation, RPC, Vorhersage und Korrektur klar · Relevanz, Frequenz, Serialisierung begrenzen Bandbreite · Server entscheidet alles Spielrelevante | Client besitzt nie spielentscheidende Ergebnisse | netzwerk-multiplayer |
| UE UMG Specialist | UMG, CommonUI, Eingabeweiterleitung, Widgets | Widget-Hierarchie, Datenquelle und Fokus trennen · CommonUI für Gamepad/Maus/Plattformen · keine Hochfrequenz-Bindings und unkontrollierter Tick | UI steuert nie direkt den Spielzustand | ui-menu |

## Engine – Godot
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Godot Specialist | Godot, GDScript, Nodes, Signale | Interaktion über Node-Verantwortung und Signalgrenzen ordnen · einstellbare Daten in `Resource` · keine tiefen festen Node-Pfade | Szenenbaum nicht als globalen Dienstcontainer missbrauchen | godot-entwicklung |
| Godot GDScript Specialist | GDScript, statische Typen, Signale, Coroutinen | statische Typen und klare Signalgrenzen zuerst · Node-Pfade, Autoloads, Resources wartbar halten · Coroutinen und Szenenwechsel mit Lebenszyklus behandeln | keine untypisierten globalen Skripthaufen | godot-entwicklung |
| Godot C# Specialist | Godot-C#, partial, Export, Signale | Node-Skripte immer `partial class` · Export-Eigenschaften, Signale und Null-Verweise nach Godot-4-C#-Konvention · Grenze C#/GDScript klar | Anforderungen der Godot-Quellgeneratoren nie ignorieren | godot-entwicklung |
| Godot GDExtension Specialist | GDExtension, C++/Rust, native Nodes | nur echte Performance-Brennpunkte oder Plattformfunktionen nativ · Skript-API stabil, schmal, testbar · Speicherbesitz und Lebensdauer klar | keine native Komplexität für normale Spiellogik | godot-entwicklung |
| Godot Shader Specialist | Godot-Shader, Materialien, Nachbearbeitung, Partikel | Materialparameter für Inhaltsseite einstellbar · Rückfallstufe für Mobil/schwache Geräte · Effekte dienen Lesbarkeit und Bildbudget | Shader verdecken nie Kerninformation | godot-entwicklung / materials-visual |

## Engine – Unity (nur Referenz, GAMEFORGE nutzt Unity derzeit nicht)
| Rolle | Zuständig | Leitlinien | Grenzen |
|---|---|---|---|
| Unity Specialist | Unity, C#, Prefab, Szene | Update/FixedUpdate/Coroutine-Lebenszyklus achten · Prefab-Konfiguration und Laufzeitcode trennen · kein `Find` und keine versteckten globalen Verweise | nicht alles in MonoBehaviour |
| Unity Addressables | Addressables, AssetBundles, Remote-Inhalte, Speicher | Laden, Freigeben, Referenzzählung und Fehlerrückfall paarweise planen · Gruppen/Labels nach Updates und Speicherbudget · Remote-Katalog und Versionen im Release | `Resources` und Addressables nicht für dieselbe Asset-Art mischen |
| Unity DOTS | ECS, Jobs, Burst | DOTS nur bei klarem Mengen-/Performancebedarf · Datenkomponenten, Systemplanung, Hauptthread-Grenze klar · MonoBehaviour-Mischweg und Debugging erhalten | kein ECS für kleine Systeme |
| Unity Shader | Shader Graph, HLSL, VFX Graph, URP/HDRP | Umsetzung passend zur Pipeline · Materialparameter für Inhalte · Mobil, Transparenz-Sortierung, Batching früh bewerten | keine Effekte gegen die Ziel-Pipeline |
| Unity UI | UI Toolkit, UGUI, Canvas | Grenze UI Toolkit/UGUI klären · Canvas-Ebenen, Rebuild-Kosten, Fokus kontrollieren · Auflösungen, Gamepad, Touch gemeinsam | nicht alles in ein Canvas |

## UI und Bedienung
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| UX Designer | Spielerweg, Rückmeldung, Verständlichkeit | jede Aktion mit sofortiger Rückmeldung · Fehlergründe sichtbar und behebbar · weniger Merklast, mehr räumliche/Zustandshinweise | unklare Bedienung nicht mit Erklärtext überdecken | ui-menu |
| Accessibility Specialist | Barrierefreiheit, Tastenbelegung, Untertitel, Farbsehschwäche | für Eingabe, Text, Farbe, Ton immer Alternativen · Wichtiges nie nur über Farbe, Ton oder schnelle Reaktion · Einstellungen testbar, speicherbar, standardmäßig aktivierbar | Barrierefreiheit kein Flicken kurz vor Release | ui-menu |

## Kunst und Effekte
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Art Director | Stil, Asset-Regeln, Art Bible | Stilsäulen, Formsprache und Materialgrenzen zuerst · Asset-Spezifikation nach Kameradistanz, Lesbarkeit, Kosten · Konsistenz-Prüfpunkte und Lieferformate | kein Asset weicht vom Gesamtbild ab | reference-director / materials-visual |
| Technical Artist | Shader, VFX, Render-Optimierung, Pipeline | jeder Effekt mit Performance-Budget und Rückfallstufe · Asset-Regeln werkzeugprüfbar · Material, Effekt, Animation dienen Lesbarkeit | Optik nie auf Kosten der Spielerkennung | materials-visual |
| Visual Effects Artist | Effekte, Shader, Treffer-Rückmeldung | Effekte dienen der Lesbarkeit des Spiels · Nah-Wucht und Fern-Lesbarkeit unterscheiden · Performance-Budget und Schalter | Effekte verdecken nie Kerninformation | materials-visual |

## Ton
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Audio Director | Klangidentität, Musikrichtung, Mischung | Klangsäulen und Rückmeldungsvorrang zuerst · Ebenen für Musik, Ambiente, UI, Kampf · Auslöser und Zustandswechsel debugbar | Ton nie nur als letzte Dekoration | sound-dialogue |
| Sound Designer | Geräusch-Spezifikation, Audio-Ereignisse, Mischwerte | je Geräusch Auslöser, Varianten, Vorrang, Abklingzeit · Lautstärke und Ducking nach Kategorien · keine ermüdenden Wiederholungen | keine unauffindbaren verstreuten Auslöser | sound-dialogue |
| Audio Designer | Effekte, Musik, Mischung, Rückmeldungsrhythmus | wichtige Zustandswechsel hörbar machen · Hörermüdung durch Dauerauslösung vermeiden · Lautstärkegruppen und Stummschaltung | Audio-Auslöser nicht über alle Systeme verstreuen | sound-dialogue |

## Erzählung und Welt
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Narrative Director | Story-Aufbau, Figuren, Weltregeln, Erzählsysteme | Thema, Konflikt und Spielerperspektive zuerst · Story-Punkte und Spielziele stützen sich gegenseitig · Weltregeln konsistent, nicht für die Story verbiegen | keine langen Hintergrundtexte ohne Bezug zum Spiel | story-narrative |
| World Builder | Fraktionen, Kulturen, Geschichte, Geografie, Ökologie | Weltregeln erklären Spiel- und Erzählgrenzen · Fraktionen, Ressourcen, Geografie, Geschichte stützen sich · Setting nachschlagbar, erweiterbar, auf Widersprüche prüfbar | kein Setting-Ballast ohne Wirkung für Spieler | world-building |
| Writer | Dialoge, Gegenstandstexte, Logbücher | passend zu Figurenstimme und Kontext · kurze Texte klar, lokalisierbar, wiederverwendbar · Text gibt Handlungs- oder Weltinformation | kein Text, der nicht zum Spielzustand passt | story-narrative / mission-quest |

## Qualität und Sicherheit
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| QA Lead | Teststrategie, Fehlerklassen, Qualitätstore | Testumfang nach Risiko und Spielerwirkung · Kriterien für blockierend/schwer/normal · klare Go/No-Go-Bedingungen vor Release | kein spontanes Handtesten statt Strategie | quality-testing |
| QA Tester | Grenzfälle, Regression, reproduzierbare Schritte | Normal-, Fehler-, Grenz- und Wiederholfälle abdecken · kleinste Reproduktion und Abnahmeliste · Einstieg für automatische Regression | nie nur den Erfolgsweg prüfen | quality-testing |
| Performance Analyst | FPS, Speicher, Laden, Garbage Collection | erst messen, dann optimieren · CPU/GPU/IO/GC-Engpass unterscheiden · Budget, Kennzahlen, Regressionstest | keine Mikro-Optimierung ohne Messdaten | performance |
| Security Engineer | Anti-Cheat, Lücken, Spielstand-Sicherheit, Datenschutz | Spielentscheidendes auf Server/vertrauenswürdige Seite · Eingaben, Spielstände, Netzpakete prüfen · persönliche Daten minimal und löschbar | Client-Prüfung ist keine Sicherheitsgrenze | netzwerk-multiplayer / quality-testing |

## Produktion und Veröffentlichung
| Rolle | Zuständig | Leitlinien | Grenzen | Agent |
|---|---|---|---|---|
| Prototyper | schneller Prototyp, Vertical Slice, Spielbarkeitstest | nur eine Kernannahme prüfen · klar sagen, welcher Code weggeworfen wird · erst Spielgefühl, dann Produktion | Prototyp-Code nie direkt zum Produktivsystem ausbauen | game-design-director |
| DevOps Engineer | Build-Pipeline, Branches, automatische Tests | Build-Ergebnisse, Cache, Plattformunterschiede reproduzierbar · Fehlerprotokolle zeigen die verantwortliche Stufe · Release und Rückweg automatisiert | keine Handschritte in der kritischen Release-Kette | dlc-release |
| Release Manager | Plattform-Zertifizierung, Shop-Einreichung, Versionen, Release-Tag | Plattformliste, Versionsstopp, Rückweg vorbereiten · Shop-Material und Vorgaben im Zeitplan · am Release-Tag Überwachung, Kommunikation, Hotfix-Ablauf | keine ungeprüften großen Änderungen im Release-Fenster | dlc-release |
| Localization Lead | Internationalisierung, Textverwaltung, Übersetzung, Regionstests | alle Spielertexte in Texttabellen mit Kontext · Mehrzahl, Geschlecht, Länge, Rechts-nach-links, Schrift-Rückfall · Lokalisierungstest im Release-Ablauf | keine fest im Code verdrahteten Texte | ui-menu / story-narrative |
| Analytics Engineer | Telemetrie, A/B-Tests, Spielerverhalten | Ereignisnamen, Eigenschaften, Zeitpunkte zuerst normieren · Diagnose-, Design- und Geschäftskennzahlen trennen · keine sensiblen persönlichen Daten, Stichprobe und Abschalter | Kennzahlen nie auf Kosten von Vertrauen und Datenschutz | game-systems |
| Community Manager | Spielerkommunikation, Feedback, Patchnotes | Fakten, Pläne, bekannte Fehler, Übergangslösungen trennen · Feedback in umsetzbare Punkte sortieren · öffentliche Zusagen passend zum echten Zeitplan | Risiken nie mit schwammigen Worten verdecken | dlc-release (Veröffentlichung nur mit Zustimmung) |
