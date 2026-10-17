---
name: neues-spiel
description: Ein neues Videospiel-Projekt in GAMEFORGE anlegen, wenn der Nutzer eine neue Spielidee hat („neues Spiel“, „ich möchte ein Spiel mit …“). Legt automatisch den Spieleordner mit Spielbibel, Stilprofil und Aufgaben an.
---

# Neues Spiel anlegen

1. Aus der Nachricht des Nutzers so viel wie möglich übernehmen. Höchstens **eine** Rückfrage mit Ja/Nein-Vorschlägen (AskUserQuestion), z. B. Grafikstil (Pixel-Art / Cartoon / Stilisiert / Realistisch / AAA+ fotorealistisch), Perspektive, Plattform. Fehlt nur der Name, schlage zwei Namen vor.
2. Anlegen mit dem Werkzeug (Pfad siehe Skill `gameforge-studio`):
   `gf.cmd neu --titel "<Name>" --idee "<Idee in Worten des Nutzers>" --genre "<…>" --stil "<…>" --perspektive "<…>" --plattform "<…>" --wuensche "<…>"`
3. **Nichts erfinden**: Die Spielbibel enthält nur, was der Nutzer gesagt hat. Weitere Inhalte nur als Vorschläge anbieten, die er bestätigt.
4. Ergebnis kurz melden: Ordner, erkannter Grafikstil, nächster sinnvoller Schritt (meist: Story/Spielregeln besprechen oder erste Referenzbilder).
