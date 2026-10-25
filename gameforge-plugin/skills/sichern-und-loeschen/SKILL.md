---
name: sichern-und-loeschen
description: GAMEFORGE-Spiele und -Filme sichern, Versionen anlegen, ein Projekt löschen (Papierkorb) oder wiederherstellen.
---

# Sichern, Löschen, Wiederherstellen

- **Sichern**: `gf.cmd sichern "<Spiel>"` → geprüftes ZIP unter `GAMEFORGE Spiele\_Sicherungen\`.
- **Löschen** (nur nach ausdrücklicher Bestätigung mit Spielnamen): erst sagen, was alles betroffen ist, dann `gf.cmd loeschen "<Spiel>" --bestaetigen "<exakter Ordnername>"`. Das Spiel landet geprüft als ZIP in `_Papierkorb\` – wiederherstellbar.
- **Wiederherstellen**: `gf.cmd wiederherstellen "<Dateiname.zip>"` (aus Papierkorb oder Sicherungen). Überschreibt nie ein vorhandenes Spiel.
- Endgültig löschen (ZIP im Papierkorb entfernen) nur nach ausdrücklicher Bitte des Nutzers – das ist unwiderruflich.
