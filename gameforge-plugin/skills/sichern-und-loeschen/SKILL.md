---
name: sichern-und-loeschen
description: GAMEFORGE-Spiele und -Filme sichern, Versionen anlegen, ein Projekt löschen (Papierkorb) oder wiederherstellen.
---

# Sichern, Löschen, Wiederherstellen

- **Sichern**: `gf.cmd sichern "<Spiel>"` → geprüftes ZIP in GAMEFORGEs Datenordner (`GAMEFORGE_DATA\sicherungen\`), der Projektordner bleibt unverändert.
- **Löschen** (nur nach ausdrücklicher Bestätigung mit Spielnamen): erst sagen, was alles betroffen ist, dann `gf.cmd loeschen "<Spiel>" --bestaetigen "<exakter Ordnername>"`. Das Projekt landet geprüft als ZIP in `GAMEFORGE_DATA\papierkorb\` – wiederherstellbar.
- **Wiederherstellen**: `gf.cmd wiederherstellen "<Dateiname.zip>"` (aus Papierkorb oder Sicherungen) – zurück an den ursprünglichen Ort, sonst `--ziel "<vorhandener Ordner>"`. Überschreibt nie etwas und legt keine Ordner an.
- Endgültig löschen (ZIP im Papierkorb entfernen) nur nach ausdrücklicher Bitte des Nutzers – das ist unwiderruflich.
