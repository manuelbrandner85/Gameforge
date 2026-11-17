# Fremde Inhalte in GAMEFORGE

## UltraGameStudio (MIT)
Quelle: https://github.com/wellingfeng/UltraGameStudio (Stand 31.10.2026, gelesen am 07.11.2026).
Übernommen und ins Deutsche übertragen bzw. angepasst – kein Programmcode aus UltraGameStudio wird ausgeführt:
- `skills/gameforge-studio/EXPERTEN.md` – 52 Spielentwicklungs-Rollen (aus `app/src/lib/gameExperts.ts`)
- `scripts/gflib/genres.py` – 30 Genre-Vorlagen (aus `app/src/lib/gameTemplateProfiles.ts`)
- Arbeitsstrategien im Agent `agents/studio-director.md` (Idee aus `app/src/runtime/dynamicHarness.ts`, `/studio`)
- Hinweise auf freie Animationsquellen (Mesh2Motion, CMU Motion Capture) aus `app/src/lib/threeDGeneration.ts`

```
MIT License

Copyright (c) 2026 wellingfeng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Bewusst NICHT übernommen (Begründung)
- **Die Desktop-App selbst** (Tauri/React, eigener Agent um Claude Code/Codex/Gemini) – wäre ein zweites Agentensystem neben Claude Code.
- **„Free-Model-Routing“** über fremde Gratis-Clouds (u. a. schlüssellose Wege wie LLM7/Kilo) – Code, Spielbibeln und Kanon würden an unbekannte Dienste gehen; doppelt zu Claude Code.
- **Generator-Anbindungen** für Bild, 3D, Musik, Sprache, Video, Rigging (Meshy, Tripo, Rodin, ElevenLabs, Suno, Stability, OpenAI, fal.ai …) – kostenpflichtige Cloud-Dienste mit API-Schlüssel.
- **Lokale 3D-Generatoren** (TRELLIS, Stable Fast 3D, Hunyuan3D) – in UltraGameStudio nur leere Anschlüsse für einen selbst betriebenen Server; nichts davon wird mitgeliefert. Hunyuan3D bleibt ausgeschlossen (Lizenz gilt nicht in der EU), Stable Fast 3D/SPAR3D ebenfalls (Stability Community License).

## Bild → 3D (`gf 3d`, eingerichtet am 07.11.2026)
Läuft nativ in ComfyUI (Knoten `comfy_extras/nodes_trellis2.py`, GPL-3.0 wie ComfyUI, nicht in GAMEFORGE kopiert). GAMEFORGE baut nur den API-Workflow nach dem TRELLIS.2-Zweig der offiziellen Vorlage „Pixal3D & TRELLIS.2: Image to Model“. Modelle liegen nur lokal unter `engines/` (nicht im Repo), SHA256-geprüft:
- TRELLIS.2 (Microsoft) – `trellis_2_int8_convrot`, Form- und Textur-VAE, aus Hugging Face `Comfy-Org/TRELLIS.2` – **MIT**
- BiRefNet (Freistellen) – `Comfy-Org/BiRefNet` – **MIT**
- DINOv3 ViT-L (Bild-Encoder, Meta) – `Comfy-Org/TRELLIS.2/clip_vision` – **DINOv3 License** (kommerzielle Nutzung erlaubt; keine Nutzung für Militär, Waffen-/ITAR-Zwecke; bei Weitergabe des Modells Lizenz beilegen). Erzeugte 3D-Modelle sind Ausgaben und fallen nicht unter die Weitergabepflicht.
