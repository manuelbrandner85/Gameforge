---
name: film-projekt
description: Filme, Trailer, Kurzfilme und Cinematics planen und produzieren – neuer Film, Logline, Treatment, Drehbuch, Shotliste, Storyboard, Twinmotion-Vorvisualisierung, Unreal Sequencer / Movie Render Queue, Schnitt, Ton. In jedem Ordner; für eigenständige Filmprojekte (z. B. GENESIS Kinotrailer) gelten deren eigene Regeln.
---

# Film-Projekt

Werkzeug: `gf.cmd` (Pfad siehe Skill `gameforge-studio`).

1. **Projekt klären**: `gf.cmd erkennen`. Eigenständiges Filmprojekt mit eigener `CLAUDE.md` (z. B. GENESIS Kinotrailer): dessen Regeln, Kanon-Sperren, Freigaben und Status-Begriffe (PLANNED/BUILT/RENDERED/TESTED/APPROVED) haben Vorrang – dort keine GAMEFORGE-Struktur anlegen.
2. **Neuer Film** (im in Claude geöffneten Ordner bzw. mit `--ordner "<Pfad>"`; ist es ein allgemeiner Ordner wie Desktop, per Ja/Nein-Vorschlag klären – nie das Gespräch blockieren, keine Ordner von sich aus anlegen): `gf.cmd neu --typ film --titel "<Titel>" --idee "<…>" --laenge "<z. B. 90 Sekunden>" --stil "<…>" [--basis "<Spiel, falls Adaption>"]`. Nichts dazuerfinden; Basiert der Film auf einem Spiel, gilt dessen Kanon (nur lesen).
3. **Planung** in `FILM.md` wie Skill `spielbibel` (Vorher/Nachher, Zustimmung): Logline → Treatment → Drehbuch → Shotliste → Storyboard.
4. **Storyboard / Look**: Skill `referenzbilder` mit Art `environment` oder `character`, Ablage im Filmordner.
5. **Kulissen und Figuren**: Skill `blender-asset`, dann `unreal-import` (Sequencer, CineCamera).
5a. **Twinmotion (Vorvisualisierung / Look)**: für schnelle Stimmungs- und Kamera-Proben von Landschaften, Gebäuden, Wetter, Tageszeit, Jahreszeit und Vegetation – bevor in Unreal final gebaut wird.
   - Ablauf: Blender-Export (`.fbx` oder `.glb` aus `export/`) → in Twinmotion importieren → Bilder/Probefahrten nach `twinmotion/` bzw. `storyboard/` exportieren → nach Zustimmung im Storyboard verwenden.
   - **Steuerung**: Twinmotion hat keine Skript-Schnittstelle; ein lokales MCP gibt es nicht (die bekannten Twinmotion-MCPs sind fremde Cloud-Dienste mit API-Schlüssel – nicht verwenden). Claude bedient Twinmotion per **Computersteuerung** (Zugriff anfragen mit dem Programmpfad `C:\Program Files\Epic Games\Twinmotion2026.2\Twinmotion\Binaries\Win64\TwinmotionCookedEditor-Win64-Shipping.exe`; starten per PowerShell `Start-Process`). Getestet am 25.10.2026: neue Szene, FBX-Import (Import → + → Dateiname eintippen), Himmel, Bild anlegen (Media → +) funktionieren. Bild-Export getestet und bestanden (1920×1080 PNG): Export → Image „+“ → Bild anklicken → blaue Zahl rechts bestätigt → ganz nach unten scrollen → „Start export“ → im Ordner-Dialog **per Doppelklick** zum Ordner `twinmotion/<Asset>/export` navigieren (Tippen ist dort gesperrt) → „Ordner auswählen“ → danach `gf.cmd twinmotion pruefen`. Noch NICHT bestätigt: Neu-Import über das ⟳-Symbol (zeigte keine Wirkung – sicherer: neue Szene und neu importieren) und Video-Export.
   - **Python-Brücke `gf.cmd twinmotion …`** (alles außerhalb der Twinmotion-Oberfläche):
     `status` (installiert, läuft, Grafikspeicher, Warnung bei offenem Unreal) · `start` (nur nach GPU-Prüfung) ·
     `vorbereiten "<Projekt>" --asset "<Name>" [--datei <fbx/glb>] [--sekunden 5]` (legt `twinmotion/<Asset>/` mit Import-Datei unter festem Namen, Shots, Looks und Klickweg in `TWINMOTION_AUFTRAG.json` an) ·
     `pruefen "<Projekt>" --asset "<Name>"` (prüft exportierte Bilder/Videos echt per Dateikopf/ffprobe, schreibt `PRUEFUNG.json`).
     Änderungen am Modell: in Blender (MCP/Skript) ändern, neu exportieren, `vorbereiten` erneut → gleiche Datei, in Twinmotion neu einlesen.
   - **Vorher**: Unreal Editor speichern und schließen lassen (vom Nutzer), sonst holt Unreal sich den Vordergrund und beide zusammen überlasten 12 GB VRAM. `gf.cmd gpu` prüfen. Klappt die Bedienung nicht, Schritt-für-Schritt-Anleitung für den Nutzer geben.
   - Nie behaupten, etwas sei in Twinmotion passiert, ohne die exportierte Datei geprüft zu haben.
   - **Twinmotion ist kein Final-Renderer** (Entscheidung des Nutzers, 25.10.2026). Final bleibt Unreal (Sequencer + Movie Render Queue). Ein Weg Twinmotion → Unreal ist nicht eingerichtet; gebaut wird aus den Blender-Dateien.
   - Twinmotion belegt viel Grafikspeicher: der GPU-Wächter (`gf.cmd gpu`) erkennt es als offenes Programm, schließt es nie, und lässt Schwerjobs warten, solange der Speicher nicht reicht.
   - Lizenz: kostenlos nur bei unter 1 Mio. US-$ Jahresumsatz; Content aus der Twinmotion-Bibliothek nur nach Lizenzprüfung in finale Renders übernehmen.
6. **Rendern**: nur nach Zustimmung (lange GPU-Last; ComfyUI vorher mit `gf.cmd comfy stop` beenden). Ergebnis nach `renders/`, Status erst „gerendert“, wenn die Datei existiert und mit ffprobe geprüft ist.
7. **Schnitt und Ton**: Werkzeuge vorher mit `gf.cmd system` bzw. `where ffmpeg` prüfen; Fassungen nach `export/`. Nie Erfolg ohne geprüfte Datei melden.
8. Agenten: `gameforge:cinematic-director`, `gameforge:story-narrative`, `gameforge:sound-dialogue`, `gameforge:materials-visual`, `gameforge:quality-testing`.
