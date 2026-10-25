# GAMEFORGE – Erweiterung für Spiel- und Filmproduktion (Architektur & Integrationsplan)

**Status:** Entwurf Phase 0 · Arbeitszweig `gameforge-film/phase0` · nichts an `main`, GENESIS oder dem Trailer-Projekt geändert.

## 1. Grundsatz: anschließen statt neu bauen

Es gibt bereits drei funktionierende Teile. Der Kern verbindet sie, er ersetzt keinen davon.

| Bestand | Ort | Rolle im Kern |
|---|---|---|
| GAMEFORGE 2.0/3.0 (App, SQLite, 20 Agenten, Plugin, Referenz-Engine, Projektscanner, Papierkorb) | `Desktop/GAMEFORGE_GODMODE_v2_0` | **Kern**: ProjectRegistry, JobOrchestrator, ApprovalCenter, Dashboard |
| GENESIS-Spiel (UE 5.8, Branch `v4/neustart`, 24 Agenten, 36 Skills, Canon-Hooks, ScriptLock, C00-Set) | `Desktop/Genesis-Games` | Projekt `GENESIS` · Bereich `GENESIS_GAME_CANON` + `GENESIS_CINEMATICS` |
| GENESIS-Kinotrailer (eigenes UE-Projekt, MRQ-CLI, Chatterbox, Audio-/Farb-QA, C00-Pilot v5) | `Desktop/GENESIS_CINEMA_TRAILER` | Projekt `GENESIS` · Bereich `GENESIS_FILM_ADAPTATION` |

Die Daten bleiben in ihren Ordnern. Der Kern speichert nur Verweise mit Hash und Herkunft.

## 2. Kernmodule → Umsetzung

| Modul | Umsetzung |
|---|---|
| ProjectRegistry | bestehende GAMEFORGE-Projekttabelle + Feld `kind` (game/film/trailer) und `canon_version` |
| CanonGuard | GENESIS-Hooks (`claude_pretool_guard.py`, `free_ai_pretool_guard.py`) + SHA-256-Baseline (`audit/claude-health-baseline.json`) + Prüfung „Canon-Hashes unverändert“ in jedem QA-Lauf |
| JobOrchestrator | GAMEFORGE-Auftragsliste (Fehler anzeigen/erneut versuchen) + Jobdateien `task.json`, `stdout/stderr.log`, `artifacts.json`, `validation.json` |
| ToolRegistry | `gameforge_core/doctor.py` (Erkennung) + je Werkzeug ein Adapter mit `detect/version/smoke_test/license` (Vorlage: `smoke_cpu.py`) |
| AssetRegistry | GENESIS `ASSET`-/Lizenzregister (`WARDROBE_REGISTER.json`, FAB-Plan, Install-Plans) verlinken, nicht kopieren |
| ShotRegistry | GENESIS `SCENE_MATRIX_C00_C21.json` + Trailer `TRAILER_SHOTLIST.md`; künftig OTIO-Datei je Szene |
| RenderFarmLocal | **neu**: Lock-Dateien GPU/Blender/Unreal unter `GAMEFORGE_DATA/locks`, VRAM-Prüfung vor GPU-Jobs (Fund H-04) |
| QAOrchestrator | GENESIS-QA-Skills + Trailer-QA (ffprobe, ebur128, Farbsprung, Whisper) als gemeinsame Prüfbausteine |
| ApprovalCenter | bestehende GENESIS-Freigaben (`DIRECTOR_DECISIONS.md`, `.genesis_approvals/`) + einfache Ja/Nein-Fragen im Dashboard |

## 3. Agenten

Die 20 GAMEFORGE- und 24 GENESIS-Agenten bleiben unverändert. Die 16 Filmrollen aus dem Masterprompt werden auf vorhandene Agenten abgebildet. Neue Agentendateien entstehen nur dort, wo es noch keine passende Rolle gibt:

| Filmrolle | vorhandener Agent | neu nötig |
|---|---|---|
| FilmDirector, CinematicSequencer | `cinematic-director`, `genesis-cinematic-director` | – |
| ScreenwriterContinuity | `story-narrative`, `genesis-script-guardian` | – |
| StoryboardArtist | `reference-director`, `genesis-reference-director` | – |
| DirectorOfPhotography, LightingLookdev | `materials-visual`, `genesis-pbr-specialist` | **DoP-Lookdev** (Kamera/Licht/Belichtung) |
| CharacterPerformance, AnimationDirector | `animation-rigging`, `genesis-motion-specialist`, `genesis-face-voice-sync` | – |
| SoundDesigner, Composer, DialogueVoiceDirector | `sound-dialogue`, `genesis-audio-director` | – |
| VFXCompositor | – | **VFX-Compositor** (Natron/Blender-Compositor) |
| FilmEditor, ColorAndMastering | – | **Film-Editor** (OTIO/MLT/FFmpeg, Lautheit, Farbe) |
| CinematicQA | `quality-testing`, `genesis-qa-release` | – |
| LicensingSupervisor | `genesis-asset-licensing` | – |

## 4. Werkzeugketten (getestet bzw. offen)

- **Film:** Drehbuch/Shotliste → UE Sequencer → MRQ (CLI, headless) → FFmpeg (ProRes-Master, H.264-Vorschau) → MLT-Timeline → Ton: Piper/Chatterbox → Whisper-Prüfung → FFmpeg-Mix/Lautheit. Offen: OTIO, Natron.
- **Spiel:** Blender (CLI/MCP) → FBX/GLB → UE-Import (Python) → Level → PIE → Build. Belegt in GENESIS (`docs/production-status/G2…G7`).
- **Bild:** ComfyUI + FLUX.2 klein 4B (lokal, 127.0.0.1).

## 5. Piloten (Phase 2)

1. **Film:** Der C00-Trailer-Pilot v5 besteht bereits (24 s, gemessen). Statt eines zweiten Piloten wird er an den Kern angeschlossen: Jobdateien, OTIO-Schnittplan, MLT-Timeline als editierbare Quelle, Natron-Testkomposition. Dazu kommt die In-Game-Fassung von 00-B aus dem Spielprojekt.
2. **Spiel:** Minimales spielbares GENESIS-Level (vorhandenes Flussdorf aus G6/G7) mit einer Interaktion, die eine kurze Sequencer-Zwischensequenz startet und danach die Steuerung zurückgibt (Kamerabesitz, Skip, Untertitel).

## 6. Schutz von GENESIS

- Keine Story-/Canon-Änderung: Canon-Hashes vor und nach jedem Job vergleichen (Baseline vom 25.10.2026, 42 Dateien).
- Keine Datei-Migration: GENESIS und Trailer bleiben, wo sie sind.
- Spielprojekt nur auf seinem Branch `v4/neustart`; der Kern schreibt nur in `GAMEFORGE_GODMODE_v2_0` (Zweig `gameforge-film/phase0`).
