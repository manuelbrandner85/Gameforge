---
name: system-check
description: Prüfen, ob die GAMEFORGE-Werkzeuge funktionieren – Claude-Anmeldung, Blender- und Unreal-Verbindung (MCP), lokale Bild-KI (ComfyUI), Grafikkarte. Bei „geht Blender?“, „ist Unreal verbunden?“, Fehlern der Produktion.
---

# System-Check

1. `gf.cmd system` ausführen und Ergebnis einfach erklären (grün = geprüft ok, sonst der eine nötige Schritt).
2. Typische Lösungen:
   - **Blender nicht erreichbar (Port 9876)**: Blender öffnen → Bearbeiten → Einstellungen → Add-ons → „MCP“ → Server starten; „Autostart“ anhaken, dann klappt es künftig von selbst.
   - **Unreal nicht erreichbar (Port 8000)**: Unreal-Projekt im Editor öffnen, MCP-Plugin aktiv.
   - **MCP in Claude Code fehlt**: Die Verbindungen `blender` und `unreal-mcp` sind nur im Ordner `GAMEFORGE Spiele` eingetragen – Chat in genau diesem Ordner öffnen.
   - **Claude nicht angemeldet**: `claude auth login` in einer Eingabeaufforderung.
   - **ComfyUI**: `gf.cmd comfy start` / `stop` (stop gibt den Grafikspeicher frei – sinnvoll vor großen Unreal-Arbeiten).
3. Blender ohne MCP testen: `gf.cmd blender-test`.
