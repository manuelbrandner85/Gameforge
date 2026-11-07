---
name: neues-spiel
description: Ein neues Videospiel-Projekt in GAMEFORGE anlegen, wenn der Nutzer eine neue Spielidee hat („neues Spiel“, „ich möchte ein Spiel mit …“). Richtet das Spiel im in Claude geöffneten Ordner ein (Spielbibel, Stilprofil, Aufgaben) – legt selbst keine Ordner an.
---

# Neues Spiel anlegen

1. Aus der Nachricht des Nutzers so viel wie möglich übernehmen. Höchstens **eine** Rückfrage mit Ja/Nein-Vorschlägen (AskUserQuestion), z. B. Grafikstil (Pixel-Art / Cartoon / Stilisiert / Realistisch / AAA+ fotorealistisch), Perspektive, Plattform, **Engine** (Unreal = Standard; Godot bei 2D/Pixel-Art/stilisiert/klein/Web/Mobile oder auf Wunsch – siehe Skill `godot-projekt`). Fehlt nur der Name, schlage zwei Namen vor.
2. **Ordner klären** (blockiert nie das Gespräch – Ideen und Spielbibel-Entwurf gehen sofort): Normalerweise ist der in Claude geöffnete Ordner der Projektordner. Ist es ein allgemeiner Ordner (z. B. Desktop) oder liegt dort schon ein Projekt, als Ja/Nein-Vorschlag fragen, welcher vorhandene Ordner gelten soll, und mit `--ordner "<Pfad>"` einrichten. Keine Ordner von sich aus anlegen.
   Einrichten mit dem Werkzeug (Pfad siehe Skill `gameforge-studio`), im geöffneten Ordner:
   `gf.cmd neu --titel "<Name>" --idee "<Idee in Worten des Nutzers>" --genre "<…>" --stil "<…>" --perspektive "<…>" --plattform "<…>" --wuensche "<…>" [--engine unreal|godot]`
   **Genre-Vorlage** vorschlagen, wenn das Genre passt (`gf.cmd genres [--engine godot]`, Details `gf.cmd genres <id>`): mit `--genre-vorlage <id>` entstehen `GENRE_VORLAGE.md` (Kernschleife, Kernsysteme, Abnahme – nur Vorschlag, nicht in der Spielbibel) und Kernsystem-Aufgaben.
   Bei `--engine godot` danach `gf.cmd godot projekt "<Name>" --profil 3d|2d|pixel|web` (Skill `godot-projekt`).
3. **Nichts erfinden**: Die Spielbibel enthält nur, was der Nutzer gesagt hat. Weitere Inhalte nur als Vorschläge anbieten, die er bestätigt.
4. Ergebnis kurz melden: Projektordner, erkannter Grafikstil, nächster sinnvoller Schritt (meist: Story/Spielregeln besprechen oder erste Referenzbilder).
