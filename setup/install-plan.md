# Installationsplan (gebündelte Freigabe, Masterprompt V1.2 B1.2)

Grundlage: `setup/tool-inventory.json`, `setup/hardware.json` (RTX 5070 12 GB, 32 GB RAM, C: 183 GB frei).
**Nichts davon ist installiert.** Größen werden beim Download gemessen und protokolliert, nicht geschätzt.

## Empfohlen jetzt

| # | Werkzeug | Wozu | Quelle | Lizenz | Admin | Weg |
|---|---|---|---|---|---|---|
| I-1 | **OpenTimelineIO** | Schnittplan/Shotliste als Datei, Austausch mit Kdenlive/MLT | PyPI `opentimelineio` (Academy Software Foundation) | Apache-2.0 | nein | eigene venv `C:\Users\manue\AI-Tools\GAMEFORGE\otio`, kein System-pip |
| I-2 | **Natron 2.5.0** | Compositing/VFX headless (`NatronRenderer`) | WinGet `Natron.Natron` (Herausgeber „The Natron developers“, Inno-Installer) | GPL-2.0 | wahrscheinlich ja (UAC-Dialog bestätigst du selbst) | `winget install --id Natron.Natron --exact` |

## Optional, nur bei Bedarf

| # | Werkzeug | Wozu | Quelle | Lizenz | Hinweis |
|---|---|---|---|---|---|
| I-3 | Material Maker 1.7 | prozedurale PBR-Texturen | WinGet `RodZill4.MaterialMaker` | MIT (App; Community-Materialien einzeln prüfen) | Blender-Shader reichen bisher |
| I-4 | Rhubarb Lip Sync | einfache 2D-Mundbewegung | GitHub-Release (kein WinGet-Paket) | MIT | für MetaHumans nicht nötig (MetaHuman Audio-Driven ist getestet) |

## Bewusst nicht

| Werkzeug | Grund |
|---|---|
| FreeMoCap | braucht mehrere echte Kameras und Kalibrierung – keine vorhanden |
| DaVinci Resolve Free | ab 21.1 keine Skript-Automatisierung in der Free-Version; höchstens manuell |
| Mixamo, Cloud-KI (Higgsfield, HeyGen …) | keine freie API bzw. Cloud/kostenpflichtig – Regel 1 |
| Twinmotion | keine Automatisierung; Blender→UE ist getestet |

## Bereits vorhanden und getestet (keine Installation nötig)

Blender 5.2.3, Unreal 5.8.4 (+ Python, Sequencer, MRQ, MetaHuman, Control Rig, PCG, Niagara), FFmpeg 9.0.2, Kdenlive/MLT 7.43, Krita 5.3.4, Piper 1.8 (deutsche Stimmen), faster-whisper 1.2.1, ACE-Step 1.5, ComfyUI + FLUX.2 klein 4B, Chatterbox (Trailer). Audacity 4.0.1 nur manuell.

## Vorher zu lösende Reparaturen

H-01 bis H-03 aus `audit/CLAUDE_REPARATURPLAN.md`.
