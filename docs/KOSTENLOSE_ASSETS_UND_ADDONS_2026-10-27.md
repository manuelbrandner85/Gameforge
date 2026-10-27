# Kostenlose Assets und Blender-Add-ons – geprüft am 27.10.2026

Nichts davon ist geladen oder installiert. Alles wurde auf der jeweiligen Originalseite geprüft (Preis, Lizenz, KI-Klausel).

## Wichtig vorab
1. **Fab-Filter „Kostenlos“ täuscht:** Bei den meisten Megascans (Felsen, Böden) ist nur die Fortnite-Lizenz (UEFN, „nur als Referenz“) gratis. Für Unreal kosten sie **3,16 € (Privat, < 100.000 USD Umsatz)** bzw. 31,80 € (Professionell). Beispiel: „Mossy Rock Formation“.
2. **„NoAI“-Kennzeichen** (fast alle Fab-Inhalte, „Verwendung mit KI zulässig: Nein“): Laut Fab-EULA verboten ist die Nutzung (i) in Datensätzen für generative KI, (ii) bei der Entwicklung generativer KI, (iii) als Trainings-Input. Das Platzieren in Unreal/Blender ist davon nicht betroffen – aber diese Assets **nicht** als Vorlage in die Bild-KI (ComfyUI) geben. GAMEFORGE hält sich daran.
3. **CC0-Quellen (Poly Haven, ambientCG) haben keinerlei Einschränkung** – auch kommerziell, ohne Namensnennung, auch mit KI.

## A. Unreal (Fab) – wirklich kostenlos
| Inhalt | Anbieter | Preis für Unreal | Lizenz | KI-Klausel | Hinweis |
|---|---|---|---|---|---|
| Megaplants (Bäume/Sträucher: Norway Spruce, Baltic Pine, Silver Birch, English Oak, European Beech, Hornbeam, Hazel, Heather, Bilberry, Bulrush …) | Quixel/Epic | **kostenlos** („Zur Bibliothek hinzufügen“) | Fab-Standard | NoAI | braucht experimentelle Plugins „Procedural Vegetation Editor“ + „Nanite Foliage (Experimental)“; Epic empfiehlt Experimental-Funktionen nicht für fertige Produkte |
| M5 VFX Vol2 – Fire and Flames (Niagara) | M5VFX | **kostenlos** | Fab-Standard | NoAI | 194 Bewertungen (4,8), Niagara ab UE5, aktualisiert 27.11.2025 |
| Electric Dreams Env (PCG-Beispielprojekt) | Epic Games | **kostenlos** | Fab-Standard | NoAI | Dschungel, nicht europäischer Wald; großes Projekt; Lehrbeispiel für PCG |
| Medieval Village Megascans Sample | Epic Games | **kostenlos** | Fab-Standard | NoAI | Dorf mit Megascans-Böden/Felsen; aktualisiert 15.10.2026 |
| Forest ground soil pine – free (Fotoscan) | Einzelautor | **kostenlos** | **CC BY 4.0** (Namensnennung nötig) | **KI erlaubt** | Waldboden mit Zapfen/Nadeln, fbx/gltf |
| Starter Content (Feuer-Flipbooks, Böden, Felsen) | Epic, in der Engine | kostenlos | Epic-Engine-Inhalt | – | **bei dir nicht installiert** – über Epic Launcher → UE 5.8 → Optionen nachinstallierbar, ohne Fab |
| Megascans-Felsen/-Böden (z. B. Mossy Rock Formation, Forest Terrain) | Quixel | **3,16 €** je Asset (Privat) | Fab-Standard | NoAI | nicht kostenlos – nur zur Info |

## B. Asset-Quellen für Blender (und Unreal) – CC0, keine Einschränkung
| Quelle | Inhalt | Lizenz (geprüft) | Zugang |
|---|---|---|---|
| Poly Haven (polyhaven.com) | HDRIs, PBR-Texturen, 3D-Modelle (Felsen, Pflanzen, Möbel …) | CC0 – jede Nutzung, auch kommerziell und mit KI, ohne Namensnennung | Download ohne Konto |
| ambientCG (ambientcg.com) | > 2.000 PBR-Materialien (Waldboden, Gras, Rinde, Fels …), HDRIs | CC0 1.0 | Download ohne Konto; Blender-Importer verfügbar (siehe C) |

## C. Blender-Add-ons – offizieller Katalog extensions.blender.org, alle GPL (frei)
Bereits aktiv: Node Wrangler, Rigify, LoopTools, Extra Mesh Objects, IvyGen, Material Utilities, Shading Plus, Bake to Single Material, The Better Baker, MPFB (Menschen), FBX/glTF/BVH, Blender-MCP.

| Add-on | Zweck | Spiel | Film | Lizenz | Größe |
|---|---|---|---|---|---|
| Sapling Tree Gen | Bäume erzeugen | ✓ | ✓ | GPL-3 | 0,04 MB |
| A.N.T. Landscape | Gelände/Felsen erzeugen | ✓ | ✓ | GPL-2 | 0,06 MB |
| Bool Tool | Hard-Surface (Waffen, Gebäude) | ✓ | ✓ | GPL-3 | 0,17 MB |
| Cell Fracture | Zerstörung/Bruchstücke | ✓ | ✓ | GPL-3 | 0,01 MB |
| Archimesh | Architektur (Räume, Türen, Fenster) | ✓ | ✓ | GPL-2 | 0,32 MB |
| Edit Mesh Tools | Modellierwerkzeuge | ✓ | ✓ | GPL-2 | 0,07 MB |
| F2 | schnelles Flächenfüllen | ✓ | ✓ | GPL-3 | 0,01 MB |
| Snap Line Tool | präzises Zeichnen | ✓ | ✓ | GPL-3 | 0,03 MB |
| MeasureIt | Maße im Viewport (Standard: Maße in cm) | ✓ | ✓ | GPL-3 | 0,03 MB |
| Sun Position | echter Sonnenstand nach Ort/Zeit | ✓ | ✓ | GPL-3 | 0,03 MB |
| Curve Tools | Kurven/Kabel/Wege | ✓ | ✓ | GPL-2 | 0,06 MB |
| Auto Mirror | symmetrisch modellieren | ✓ | ✓ | GPL-2 | <0,01 MB |
| Copy Attributes Menu | Eigenschaften übertragen | ✓ | ✓ | GPL-3 | 0,01 MB |
| AmbientCG Material Importer | CC0-Materialien mit einem Klick | ✓ | ✓ | GPL-3 | – |
| PROTO Game Asset Tools | besserer Export für Unreal/Unity/Godot | ✓ | | GPL-3 | – |
| Game Asset Optimizer | Modelle für Unreal/Unity optimieren | ✓ | | GPL-3 | – |
| LODify / expLODe | LOD-Stufen automatisch | ✓ | | GPL-3 | – |
| Texel Density Checker | einheitliche Texturdichte | ✓ | | GPL-3 | – |
| Unreal PSK/PSA | Unreal-Formate (Skelett/Animation) | ✓ | | GPL-3 | – |
| PolyQuilt / Bsurfaces | Retopologie (Scans → spieltauglich) | ✓ | ✓ | GPL-3 | – |
| Bagapie / Scatter Objects / Place Helper | Streuen, Platzieren | ✓ | ✓ | GPL-3/2 | – |
| Add Camera Rigs | Kran/Dolly-Kamerarigs | | ✓ | GPL-3 | 0,02 MB |
| Camera Shakify | echtes Handkamera-Wackeln | | ✓ | GPL-3 | – |
| Storypencil / Storytools | Storyboards | | ✓ | GPL-3 | – |
| Stored Views | Kamerapositionen merken | | ✓ | GPL-3 | 0,02 MB |
| Amaranth | Render-/Szenenhelfer | | ✓ | GPL-3 | 0,05 MB |

Quellen: fab.com (Listings, EULA), quixel.com/license, polyhaven.com/license, ambientcg.com/license, extensions.blender.org API (Abfrage 27.10.2026).
