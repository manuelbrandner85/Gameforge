---
name: dlc
description: DLC / Erweiterung für ein GAMEFORGE-Spiel anlegen und planen (neue Regionen, Story, Figuren, Missionen), immer eindeutig einem Basisspiel zugeordnet.
---

# DLC

1. Basisspiel klären. Anlegen: `gf.cmd dlc "<Spiel>" --titel "<DLC-Name>" --idee "<Idee>" --basisversion "<Version>"`.
2. Planung in `dlc/<Name>/DLC.md` – wie Skill `spielbibel` (Vorher/Nachher, Zustimmung). Der Kanon des Basisspiels gilt.
3. Referenzen, Blender und Exporte des DLC liegen in `dlc/<Name>/referenzen|blender|export` – nie mit dem Basisspiel vermischen.
4. Kompatibilität (Basisversion, Savegames) im Abschnitt „Integration“ festhalten; Agent `gameforge:dlc-release`.
