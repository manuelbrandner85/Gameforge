---
name: spielbibel
description: Spielinhalte eines GAMEFORGE-Spiels besprechen und ändern – Story, Prolog, Missionen, Charaktere, Bosse, Welt, Kampfsystem, Steuerung, Menüs, Enden. Für Ideen und Änderungswünsche wie „mach AION düsterer“ oder „erstelle einen Boss mit drei Phasen“.
---

# Spielbibel bearbeiten

Die Spielbibel ist `SPIEL.md` im Spieleordner (Abschnitte mit `## `). „(offen)“ = noch nicht ausgearbeitet.

1. `SPIEL.md` und `art-direction.json` des richtigen Spiels lesen. Bei DLC: `dlc/<Name>/DLC.md`.
2. Antwort gliedern: **Verstanden** · **Vorschlag** · **Auswirkungen** (welche Abschnitte, Missionen, Assets betroffen) · **Nächster Schritt**.
3. Vor dem Schreiben: Vorher/Nachher zeigen und per Ja/Nein fragen. Änderungen am Abschnitt „Story-Kanon (verbindlich)“ nur nach ausdrücklichem Ja.
4. Vor dem Schreiben eine Kopie ablegen: `versionen/SPIEL_<JJJJMMTT_HHMM>.md`.
5. Nur die betroffenen Abschnitte ändern (Edit-Werkzeug), Rest unverändert lassen.
6. Am Ende sagen, was **nur geplant** ist (Text) und was noch **gebaut** werden muss (Referenzen, Blender, Unreal) – mit Angebot für den nächsten Schritt.

Für umfangreiche Ausarbeitung (ganze Questlinie, Bossdesign) die Agenten `gameforge:story-narrative`, `gameforge:mission-quest` oder `gameforge:character-boss` einsetzen.
