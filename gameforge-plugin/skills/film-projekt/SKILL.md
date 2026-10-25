---
name: film-projekt
description: Filme, Trailer, Kurzfilme und Cinematics planen und produzieren – neuer Film, Logline, Treatment, Drehbuch, Shotliste, Storyboard, Unreal Sequencer / Movie Render Queue, Schnitt, Ton. In jedem Ordner; für eigenständige Filmprojekte (z. B. GENESIS Kinotrailer) gelten deren eigene Regeln.
---

# Film-Projekt

Werkzeug: `gf.cmd` (Pfad siehe Skill `gameforge-studio`).

1. **Projekt klären**: `gf.cmd erkennen`. Eigenständiges Filmprojekt mit eigener `CLAUDE.md` (z. B. GENESIS Kinotrailer): dessen Regeln, Kanon-Sperren, Freigaben und Status-Begriffe (PLANNED/BUILT/RENDERED/TESTED/APPROVED) haben Vorrang – dort keine GAMEFORGE-Struktur anlegen.
2. **Neuer Film**: `gf.cmd neu --typ film --titel "<Titel>" --idee "<…>" --laenge "<z. B. 90 Sekunden>" --stil "<…>" [--basis "<Spiel, falls Adaption>"]`. Nichts dazuerfinden; Basiert der Film auf einem Spiel, gilt dessen Kanon (nur lesen).
3. **Planung** in `FILM.md` wie Skill `spielbibel` (Vorher/Nachher, Zustimmung): Logline → Treatment → Drehbuch → Shotliste → Storyboard.
4. **Storyboard / Look**: Skill `referenzbilder` mit Art `environment` oder `character`, Ablage im Filmordner.
5. **Kulissen und Figuren**: Skill `blender-asset`, dann `unreal-import` (Sequencer, CineCamera).
6. **Rendern**: nur nach Zustimmung (lange GPU-Last; ComfyUI vorher mit `gf.cmd comfy stop` beenden). Ergebnis nach `renders/`, Status erst „gerendert“, wenn die Datei existiert und mit ffprobe geprüft ist.
7. **Schnitt und Ton**: Werkzeuge vorher mit `gf.cmd system` bzw. `where ffmpeg` prüfen; Fassungen nach `export/`. Nie Erfolg ohne geprüfte Datei melden.
8. Agenten: `gameforge:cinematic-director`, `gameforge:story-narrative`, `gameforge:sound-dialogue`, `gameforge:materials-visual`, `gameforge:quality-testing`.
