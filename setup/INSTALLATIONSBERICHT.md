# Installationsbericht – Phase 0 (Bestand, keine Installation)

**Stand:** 25.10.2026 · Statuswerte nach Masterprompt V1.2 B1.5: `bereits_vorhanden`, `getestet`, `manueller_schritt`, `blockiert`, `nicht_unterstuetzt`, `fehlt`.
**Belege dieser Prüfung:** `audit/evidence/smoke_cpu_20261025_194840/validation.json` (alle Artefakte + Logs im selben Ordner).
**Fremde Belege von heute:** Trailer-Pilot `Desktop/GENESIS_CINEMA_TRAILER/QA_REPORT_PILOT.md`, GENESIS-Renders `Genesis-Games/docs/evidence/V42/`.

| Werkzeug | Version | Status | Beleg |
|---|---|---|---|
| Claude Code | 2.1.309 | getestet | `claude --version`, `claude mcp list` |
| Blender | 5.2.3 LTS | **getestet** | .blend 88 KB, GLB (Magic `glTF`), FBX, Render 320×180, Würfel 1,0 m |
| Blender-MCP | – | getestet | in dieser Sitzung Dutzende Aufrufe; `claude mcp list` ✔ |
| Unreal Engine | 5.8.4 CL58902052 | getestet (GENESIS + Trailer) | Python-Remote-Execution heute in der GENESIS-Sitzung; MRQ-Kommandozeilen-Render von 576 Frames im Trailer-Projekt. Eigener Smoke-Test „Level, Mesh, Sequence, 5 Frames, Packaging“ **ausstehend** (GPU war von zwei anderen Sitzungen belegt) |
| UE-Plugins | Python, Sequencer Scripting, MRQ, MetaHuman (Character, Animator, AnimationTools), Control Rig, PCG, Niagara, Remote Control | bereits_vorhanden | `*.uplugin` im Engine-Ordner |
| MetaHuman Audio-Driven | UE 5.8.4 | getestet (Trailer) | Lippen-/Mimikspur zur Dialogzeile bei 18,9 s im Trailer-Pilot |
| unreal-mcp | – | blockiert | ECONNREFUSED, kein Server-Plugin (H-03) |
| FFmpeg / FFprobe | 9.0.2 full | **getestet** | ProRes 422 HQ + PCM 24 bit, 2,000 s, Metadaten per ffprobe JSON |
| MLT (melt) | 7.43.0 | **getestet** | Timeline aus 2 Clips: 96 Frames / 4,01 s / 24 fps / 1280×720; Bild bei 1 s = Clip A, bei 3 s = Clip B |
| Kdenlive | (mit MLT 7.43) | bereits_vorhanden, manueller_schritt | GUI für Sichtkontrolle |
| Krita | 5.3.4.1 | **getestet** | CLI-Export PNG |
| Audacity | 4.0.1 | manueller_schritt | kein `mod-script-pipe`; Fallback FFmpeg |
| Audio-Bereinigung (FFmpeg) | – | **getestet** | Hochpass + Rauschminderung + Loudnorm: −22,8 LUFS (Ziel −23), Peak −4,8 dBFS |
| Piper TTS | 1.8.0, Stimme de_DE-thorsten-high | **getestet** | WAV 22,05 kHz, 4,0 s |
| faster-whisper | 1.2.1 small (CPU int8) | **getestet** | erkennt den Piper-Satz zurück |
| Chatterbox TTS | 0.1.7 | getestet (Trailer) | Dialog im Trailer-Pilot, Whisper-Konfidenz 0,94 |
| ACE-Step 1.5 | v0.1.8 | bereits_vorhanden | Rauchtest-Skript `Genesis-Games/tools/v4_1/ace_step_smoke.py`; neuer Lauf **ausstehend** (GPU belegt) |
| ComfyUI + FLUX.2 klein 4B | portable | getestet (GENESIS) | Familienfotos C00 heute erzeugt (`ArtSource/Reference/C00/PROPS_C00_FOTOS`); Wan 2.2 TI2V 5B liegt ebenfalls vor (ungetestet) |
| OpenTimelineIO | – | fehlt | Installationsplan I-1 |
| Natron | – | fehlt | Installationsplan I-2 (WinGet `Natron.Natron` 2.5.0) |
| Material Maker | – | fehlt (optional) | I-3 |
| Rhubarb Lip Sync | – | fehlt (optional) | I-4 |
| FreeMoCap | – | nicht_unterstuetzt | keine Mehrkamera-Hardware |
| DaVinci Resolve | – | nicht_unterstuetzt (Automatisierung) | Free-Version ohne Skripting |

**Nicht als „bereit“ gemeldet:** Unreal-Eigen-Smoke-Test, ACE-Step-Neulauf, Natron, OTIO.
