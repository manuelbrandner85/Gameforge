---
name: referenzbilder
description: Referenzbilder und Konzeptbilder für ein GAMEFORGE-Spiel erzeugen, prüfen und freigeben (Charaktere, Bosse, Kreaturen, Waffen, Gebäude, Umgebungen, UI). Erzeugt lokal auf der Grafikkarte mit ComfyUI + FLUX.2 klein – ohne Cloud und ohne Kosten.
---

# Referenzbilder

Werkzeug: `gf.cmd` (Pfad siehe Skill `gameforge-studio`).

## Erzeugen
1. Spiel, Objekt, Art und gewünschte Ansichten klären. Arten: character, boss, npc, creature, weapon, building, vehicle, environment, prop, ui. Ohne Angabe nimmt `gf` die Standardansichten der Art.
2. Verbindliche Designdetails aus `SPIEL.md` übernehmen (z. B. Rüstung, Farben, Größe) und als `--details` mitgeben. Nichts dem Kanon Widersprechendes erfinden.
3. Aufruf (läuft mehrere Minuten, beim ersten Mal lädt das Modell länger – Bash mit langem Timeout oder im Hintergrund):
   `gf.cmd bild "<Spiel>" --asset "<Name>" --art boss --ansichten front,side,back --details "<…>" --qualitaet AUTO`
   - Qualität: AUTO (aus Stilprofil), DRAFT (schnell), STANDARD, HIGH (2 Varianten), CINEMATIC_MASTER (höchste Auflösung **im Spielstil**).
   - Bereits freigegebene Ansichten werden wiederverwendet; `--neu` erzeugt bewusst eine neue Variante.
4. Jedes erzeugte Bild mit dem Read-Werkzeug ansehen und dem Nutzer zeigen. Ehrlich beurteilen: Anatomie, Proportionen, Design-Treue zwischen den Ansichten, Stil. Probleme klar benennen.

## Freigeben
- Nur nach Ja des Nutzers: `gf.cmd freigeben "<Spiel>" "referenzen/entwuerfe/<Asset>/<ansicht>_v<n>.png"`
- Frühere Freigaben bleiben unter `_frueher/` erhalten.

## Wenn etwas fehlt
- ComfyUI nicht installiert / Fehler: Skill `system-check`. Alternative ohne lokale KI: `gf.cmd prompt "<Spiel>" --asset … --art … --ansicht front` liefert einen kopierbaren Prompt für ChatGPT; das Bild legt der Nutzer dann in `referenzen/entwuerfe/<Asset>/` ab.
- Ein Referenzbild ist **kein 3D-Modell**. Für das Modell: Skill `blender-asset`.
