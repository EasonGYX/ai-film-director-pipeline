# Director Pipeline Skill (AI Short Films)

A complete, model- and platform-agnostic workflow for turning an idea into a 90–125 second AI short film: six stages with gates, prompt engineering, budget control, and post-production recipes.
Everything is Markdown + Python. **Switch models or platforms without changing the process.**

## Who it is for / not for
- For: 90–125s AI shorts (assignments, promos, client work) on a limited budget, where the goal is "clearly better than typical AI output"
- Not for: live-action footage, films over 3 minutes, projects requiring professional voice actors

## Demo stills
Frames from a 100-second historical AI short produced with this pipeline (practice project, no personal information):

![Candlelit translation](examples/screenshots/01_translation.jpg)
![Desert crossing](examples/screenshots/02_t12.jpg)
![Gaochang](examples/screenshots/03_t47.jpg)
![Snow ridge](examples/screenshots/04_t58.jpg)
![Nalanda](examples/screenshots/05_t74.jpg)

## Quick start (5 minutes)
1. Read section 0 of `SKILL_EN.md` (or `SKILL.md` for the authoritative Chinese version) and paste the startup prompt into any AI assistant
2. Copy `templates/01`–`06` into your project folder and fill them in order
3. Check `SKILL_EN.md` section 7 (or `SKILL.md` §7) for the platform checklist (pricing, modes, failure behavior)
4. Run `scripts/post_make.py` for post-production (verify your environment with `examples/smoke_test/README.md` first)

> ⚠ **Read before use**: the `SEGS` list at the top of `scripts/post_make.py` is an **example shot list** (clip01 / 卡1 / clip02 / 卡B).
> The script does **not** auto-scan `生成/`; edit `SEGS` with your own file names, durations and order, or only those four example segments will be concatenated.

## Requirements
- Python 3.9+, `pip install -r requirements.txt` (Pillow only)
- ffmpeg / ffprobe (external binaries; set `FFMPEG` env var if not on PATH)
- Chinese fonts: defaults to `C:/Windows/Fonts/` (KaiTi/SimSun); on other OS set `FONT_DIR`

## Layout
```
README.md           this file
README_EN.md        English README (this file)
SKILL.md            main workflow: six stages, prompts, budget rules, QC, post recipes, platform checklist, retrospective
SKILL_EN.md         English version of the workflow (condensed)
LICENSE             MIT (copyright holder: EasonGYX)
requirements.txt    Python dependencies
templates/          six templates: script / storyboard / VO+subtitles / character+palette / prompts / ledger
scripts/            four scripts: contact_sheet / make_cards / make_cover / post_make
examples/           smoke test (2 clips x 3s + 4 cards + 2 test images + 1 cover)
```

## Script inputs and outputs
| Script | Input | Output | Env vars |
|---|---|---|---|
| `contact_sheet.py` | several images | one contact sheet (aspect-preserving letterbox) | — |
| `make_cards.py` | none (edit constants: chapters/quotes/source) | chapter cards + quote card PNGs | `CARDS_DIR`, `FONT_DIR` |
| `make_cover.py` | optional background image | cover JPG/PNG | `COVER_TITLE`, `BYLINE`, `SCHOOL`, `COVER_EN`, `COVER_BG`, `FONT_DIR` |
| `post_make.py` | clips in `生成/` + cards in `后期/` | `成片_无音轨中间片.mp4` (silent) | `PROJECT_DIR`, `FFMPEG` |

## Sound hand-off (important)
Python produces a **silent video intermediate**. Voice-over, subtitle timing, BGM and the final export happen in CapCut (or any NLE): import the intermediate → import the SRT → **use the separate voice-over script for TTS, not the bilingual subtitle file** → add BGM → export.
(`post_make.py` keeps every segment without audio so mixed streams are never silently dropped; the smoke test asserts this.)

## Method sources
- The seven-part video prompt, the nine model weaknesses, and the 38%/62% composition heuristic are adapted from a public long-form post by **Eian (@EianLu)** on X (Nov 2026): https://x.com/EianLu/status/2118317430665613741 . This project paraphrases the method and does not copy the text. Those items are tagged 【External · suggestion】. The six templates are currently Chinese-only.
- Everything else (six stage gates, serial validation, stop-on-failure, ledger rules, card/cover/concat scripts) comes from this project's own production and rework retrospective, tagged 【Project experience】.

## Known limitations
- Platform pricing, concurrency limits and failure rates change; no prices are hard-coded
- The "Tang-dynasty realism" style lock in templates is only an example — replace it with your own subject
- Subtitle timing must be calibrated against the final edit (see `templates/03`)

## License
MIT, copyright holder EasonGYX (see LICENSE).
Scope: MIT covers this project's own content only. Eian's original article and other third-party content are not covered and remain under their authors' terms.
