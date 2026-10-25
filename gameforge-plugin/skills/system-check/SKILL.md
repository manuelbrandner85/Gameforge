---
name: system-check
description: Prüfen, ob die Werkzeuge für Spiel- und Filmproduktion funktionieren – Claude-Anmeldung, Blender- und Unreal-Verbindung (MCP), lokale Bild-KI (ComfyUI), Grafikkarte. Bei „geht Blender?“, „ist Unreal verbunden?“, Fehlern der Produktion.
---

# System-Check

1. `gf.cmd system` ausführen und Ergebnis einfach erklären (grün = geprüft ok, sonst der eine nötige Schritt).
2. Typische Lösungen:
   - **Blender nicht erreichbar (Port 9876)**: Blender öffnen → Bearbeiten → Einstellungen → Add-ons → „MCP“ → Server starten; „Autostart“ anhaken, dann klappt es künftig von selbst.
   - **Unreal**: wird über Python-Fernsteuerung bzw. Kommandozeile (UnrealEditor-Cmd) angesprochen, nicht über eine eigene MCP-Verbindung. Unreal-Projekt im Editor öffnen, Plugin „Python Editor Script“ aktiv.
   - **MCP in Claude Code fehlt**: Die Verbindung `blender` ist für alle Ordner eingetragen; Blender muss offen sein und das Add-on den Server gestartet haben.
   - **Claude nicht angemeldet**: `claude auth login` in einer Eingabeaufforderung.
   - **ComfyUI**: `gf.cmd comfy start` / `stop` (stop gibt den Grafikspeicher frei – sinnvoll vor großen Unreal-Arbeiten).
3. Blender ohne MCP testen: `gf.cmd blender-test` (läuft über den GPU-Wächter).
4. **Grafikkarte / Smart GPU Commander**: `gf.cmd gpu` zeigt VRAM, Last, Temperatur, wer das GPU-Token hält und welche GPU-Programme offen sind.
   - Es läuft immer nur **ein** GPU-Schwerjob (Bild-KI, Blender-Render, Unreal-Render). Weitere warten automatisch („WARTET – …“).
   - Offene Editoren (Unreal, Blender, ComfyUI) zählen als belegt und werden **nie** von GAMEFORGE geschlossen. Reicht der Speicher nicht, sag dem Nutzer, welches Programm ihn belegt; er entscheidet, ob er speichert und schließt.
   - Die Qualität wird **nie** automatisch gesenkt. Grafikspeicher voll → Status BLOCKIERT, kein stiller Ersatz.
   - Warteschlange: `gf.cmd jobs` (Liste), `gf.cmd jobs arbeiten`, `gf.cmd jobs abbrechen <Nr>`, `gf.cmd jobs erneut <Nr>`.
