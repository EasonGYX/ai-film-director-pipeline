# SKILL: Director-level AI Short-Film Pipeline (model- and platform-agnostic)

> Derived from one real 100-second AI short (cloud generation + CapCut finishing).
> For: 90–125s AI shorts on a limited budget, aiming to be clearly better than typical output.
> Not for: live action, films over 3 minutes, projects needing professional voice actors.

## Rule tags
- 【Principle】: holds across subjects and platforms
- 【Project experience】: from this production; a reference, not a law
- 【External · suggestion】: paraphrased from Eian's public post (license unverified)
- 【Tool operation】: depends on a specific platform UI
- 【Style example】: sample style lock, replace with your subject

## 0. Startup prompt (paste into any model)
```
You are the director of this short film; I only talk to you. Follow the SKILL pipeline:
1) Ask me: subject, length, aspect, total budget, delivery format, reference film (optional).
2) Produce six artefacts (script / storyboard / VO+subtitles / character+palette / prompts / ledger), one at a time for my approval.
3) Before every paid generation, report prompt + parameters + unit price; wait for my go.
4) Submit serially, validate every clip, stop on failure; keep >=20% budget reserve.
5) Post-production with ffmpeg + NLE; subtitles/VO/music per templates.
Start with the script.
```

## 1. Roles
- Director (AI): script, storyboard, prompts, review, post scripts, ledger. Single point of contact.
- Human: direction, visual approval, listening, BGM, final export.
- Platform: only turns first frames/prompts into clips. Swappable.

## 2. Six stages (each with a gate)
1. **Requirements & benchmark** (free): ask subject/length/aspect/budget/deliverables; pick a reference film, measure framing; write a one-sentence premise.
2. **Script** (free; gate): episodic structure by default — shots may be generated independently, but the story stays continuous (identity, costume, props, space, causality); five checks (logic / one-sentence premise / hook in 5s / believable bystander reactions / AI-feasible). Have a fresh "reviewer view" with no context flag problems.
3. **Storyboard** (free; gate): per shot — on-screen time / generate seconds / shot size / camera / movement / subject direction / expression beat / motion (camera or subject; if intentionally still, state the narrative reason) / first frame / last frame / transition / weakness avoidance. Camera grammar: rarely the same angle twice; 38%/62% composition is a heuristic, not a rule 【External · suggestion】.
4. **Character & palette lock** (planning free; reference image generation may cost credits): turnaround sheet (front/side/back), fixed costume colours in hex (a reference, not a guarantee — still verify each shot), fixed prop positions, per-scene palette, B&W contrast check ≥30%. Text/anachronism rules: no readable text inside generated frames; add period typography in post.
5. **Generation** (main paid stage): read unit prices first, build a budget table, get approval; images: turnaround → key frame → last frame then derive first frame (for push-ins, last frame = centre crop of first); video: first frame + seven-part prompt; **serial**, validate every clip, download immediately (many tools keep only the latest result).
6. **Post-production** (local processing free; NLE subscription, premium TTS or stock assets may cost money): normalise to 1080p/30fps, unified grade + grain, concat, cards; subtitles via SRT; **read the VO script for TTS, not the bilingual subtitles**; BGM and export in the NLE.

## 3. Prompt engineering
- **Style lock** (every prompt): e.g. `cinematic, natural light, film grain, muted earthy palette, sharp focus, no text, no watermark` 【Style example】
- **Character lock**: age/face/hair/costume hex/prop positions, copied verbatim.
- **Seven-part video prompt**: style / shot (size·angle·movement) / composition & palette / characters (fixed) / second-by-second action / sound / constraints (no dialogue, single take, no text).
- **Nine model weaknesses**: crossing characters, hands with small objects, text, mirrors, left-right asymmetry, lighting change within a shot, three actions in one shot, overhead shots hiding faces, too many extras.
- Prefer positive constraints ("only these two people are in frame") over "don't do X".
- Suspect the prompt before the model; change prompt or image before re-rolling.

## 4. Money rules
| Rule | Why |
|---|---|
| Read prices, report budget, wait for approval | Prices differ per model/resolution |
| Probe with one shot first, then at most 2 in parallel (each result downloaded and validated independently) | 7 parallel jobs → 6 silent failures in practice |
| Validate every clip, download at once | Nodes keep only the latest result |
| Stop on failure, check price/params/quota, keep evidence | Failed jobs are often still charged |
| Log every spend; reconcile balance after each batch | Silent deductions happen |
| Keep ≥20% reserve | Rework is real |
| Use "clean" nodes only | Duplicated nodes can inherit broken config |
| Re-open the parameter menu for each selection | Menus close after one pick; durations silently reset |

## 5. QC
- Image: prompt↔image alignment / camera consistency / palette / nine weaknesses / motif line / text & anachronism / costume.
- Clip: action chain / face warping / colour jumps / vanishing props / synchronised crowds / garbled text.
- Final: 90–125s / subtitle overlap / card-to-shot transitions / VO vs music balance.
- Failure detection: record src → submit → poll every 5–10s → success = src changed; failure = no loading, no change, past normal duration → screenshot, check price/quota, fix, retry once.

## 6. Post recipes
```bat
:: normalise a clip
ffmpeg -y -t 8 -i in.mp4 -vf "scale=1920:1080:flags=lanczos,fps=30,eq=saturation=0.92:contrast=1.06,colorbalance=rs=-0.04:bs=0.06:rh=0.03:bh=-0.02,unsharp=5:5:0.4,noise=alls=5:allf=t,format=yuv420p" -an -c:v libx264 -crf 18 -preset veryfast out.mp4
:: static card segment (no audio, to keep stream layout consistent)
ffmpeg -y -loop 1 -t 3 -i card.png -vf "fps=30,noise=alls=4:allf=t,format=yuv420p" -an -c:v libx264 -crf 18 seg.mp4
:: concat
ffmpeg -y -f concat -safe 0 -i list.txt -c copy final.mp4
:: compact delivery
ffmpeg -y -i final.mp4 -c:v libx264 -crf 21 -preset veryfast -r 30 -pix_fmt yuv420p out.mp4
```
- **Sound hand-off**: Python outputs a silent intermediate; VO, subtitle calibration, BGM and final export happen in the NLE. **Read the VO script (one language) for TTS — never the bilingual subtitles**, or both languages get spoken.
- **Shot list**: `post_make.py`'s `SEGS` is an example list; edit it with your own file names, durations and order. The script does not auto-scan the clips folder.
- Subtitle timing: fix the edit first, derive per-segment in/out points, one subtitle per segment, ≤24 CJK chars / ≤45 Latin chars per line, ≥2.5s per cue, calibrate against the VO waveform.
- Output canvas is fixed 1920×1080 (16:9). Non-16:9 input is letterboxed, not stretched; for a 9:16 deliverable, change the target canvas in the filter. 【Tool operation】
- Windows: avoid `powershell -File` with non-ASCII paths (GBK corruption); use `pwsh` or Python.

## 7. New-platform checklist
- [ ] Image/video prices and duration options
- [ ] Generation modes (text/image/first-last/multi-reference) and how references attach
- [ ] Silent-failure signature (no error, no output, still charged)
- [ ] Concurrency limit and queue time
- [ ] Does it keep only the latest result (then download immediately)
- [ ] Free-tier limits

## 8. Retrospective (real incidents)
1. Assumed ffmpeg was missing → downloaded twice → **search the workspace first**.
2. First batch: 7 parallel → 6 silent failures → serial/two-shot probes fixed it.
3. Duplicated nodes inherited broken config → only use clean nodes.
4. Parameter menus close on each pick → durations silently reset → re-open per item.
5. Nodes keep only the latest result → screenshots hit placeholders → download immediately.
6. Silent failures still charged → filed a refund with evidence.
7. Cost baseline for a 100s film: ~18 reference images, 10–11 clips (mixed 480p/720p), spend roughly 500–1300 credits depending on platform pricing; failed/reworked work was ~40% before the rules above.

## 9. Cost & schedule baseline (100s film)
| Item | Baseline |
|---|---|
| Images | 18 × unit price |
| Video | 10–11 clips, mixed resolution |
| Reserve | ≥20% |
| Duration | 2–3 evenings including approvals |
| Deliverables | final 1080p + SRT + cover + script/storyboard/prompts/ledger |
