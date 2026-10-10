# VIDEO_BRIEF.md — paste this whole file to Devin (with the assets below)

> **For the friend running Devin:** clone
> `https://github.com/FaridMahmudlu/neathack-agent.git` (public), drop the
> received assets into `demo_assets/`, then paste this file + the "Context"
> line below as your Devin prompt. No API keys needed — everything the video
> shows is in the repo and the recordings.

---

## Mission

Produce a **75–100 second, 1920×1080, 24–30fps** product demo video for
**Autopsy**, a hackathon project. Build it with **Remotion** (React-based
programmatic video) — hybrid style: real screen recordings embedded inside
motion-graphic scenes, like a top-tier dev-tool launch video (think
Vercel/Linear/Supabase product videos).

## Context (keep in the prompt)

Autopsy is a debugger for AI-agent mistakes: it takes a failing agent run,
reads the neatlogs trace, walks Entire checkpoints (which coding-agent
session wrote which commit), and outputs an evidence-backed diagnosis +
fix. The demo: a research agent's search was silently flipped to ascending
order in commit `dece484` (checkpoint `01M4K1P5A9NYJJNRY2D9XKJ08P`), the
agent started missing the right document, Autopsy named the exact line
(`reverse=False`, app.py:51) and the culprit checkpoint. Real IDs and links
are in `SUBMISSION.md` — use the REAL values in the video, never lorem ipsum.

## Assets (drop into `demo_assets/` before running)

| Path | What |
|---|---|
| `recordings/run_bugged.mp4` | terminal: demo agent giving incomplete answer |
| `recordings/neatlogs_trace.mp4` | neatlogs dashboard, span list of the failing trace |
| `recordings/debugger_run.mp4` | terminal: Autopsy investigating + printing diagnosis |
| `recordings/entire_commit.mp4` | entire.io commit page with 4 sessions |
| `recordings/run_fixed.mp4` | terminal: same question, full correct answer |
| `voiceover/*.mp3` | one narration file per scene (real voice or AI) |
| `voiceover/script.txt` | exact narration text per scene (for subtitles/timing) |

If a recording is missing, generate the motion-graphic scene anyway and
leave a labeled placeholder `<Sequence>` so it can be swapped.

## Storyboard (durations are targets — sync cuts to the voiceover)

1. **Cold open (0–7s).** Black → monospace text types itself:
   "Your agent gave a wrong answer. *Why?*" Then the Autopsy wordmark
   glitches in. Beat of silence before VO starts.
2. **The failure (7–18s).** `run_bugged.mp4` inside a mock terminal window
   (rounded, drop-shadow, subtle scale-in). Red underline sweeps under the
   incomplete answer text. Caption chip: "trace 98330b2d… captured by
   neatlogs".
3. **The trace (18–28s).** `neatlogs_trace.mp4`; overlay an animated span
   waterfall diagram — 4 `search_docs` tool spans highlight one-by-one in
   amber, each stamping "SAME 3 PAGES" — a subtle "something is off" pulse.
4. **Autopsy works (28–50s).** `debugger_run.mp4` (speed-ramp through the
   thinking, slow down when the diagnosis prints). Side panel animates the
   method: three source icons (trace / checkpoint / code) connect into one
   node labeled "diagnosis".
5. **The smoking gun (50–62s).** Split screen: left = code block of
   `search_docs` zooming onto `reverse=False` (line highlight + red box
   draw-on); right = the Entire checkpoint card sliding in — commit
   `dece484`, checkpoint `01M4K1P5…`, "the session that broke it". A line
   literally *connects* the code line to the checkpoint card.
6. **Verify (62–72s).** `run_fixed.mp4`; green check draws itself over the
   correct answer ("tricolour… crescent… eight-pointed star"). Small
   caption: "verified — new trace ead5a98e…".
7. **Close (72–80s).** Three logos/text fades: "neatlogs — runtime truth" /
   "Entire — development truth" / "Autopsy — the diagnosis between them".
   End card: repo URL + "Team Last Commit · neatHack 2026".

## Style guide

- Dark theme `#0d1117`-ish; accent `#f0ab00` (amber) for evidence,
  `#ff4d4d` for the bug, `#3fb950` for verified. Monospace: JetBrains Mono
  or IBM Plex Mono for code/IDs; Inter for prose.
- Motion: spring-based, `spring({ damping: 200 })` feel — snappy, no
  linear tweens; 4–8 frame anticipation on big reveals; every element
  enters with purpose (draw-on lines, clip-path reveals, type-on for code).
- Real IDs on screen look great small — don't enlarge them until the beat
  that names them (`reverse=False` zoom is THE money shot of scene 5).
- Subtle grain/vignette on terminal footage so it sits inside the motion
  world; 24px safe margins.
- Background music: low, dark, pulsing — duck −12dB under VO (license-free
  is fine; leave a `music.mp3` slot if absent).
- Burned-in subtitles matching `script.txt`, mono font, bottom-center,
  90% opacity — hackathon judges watch muted.

## Engineering requirements

- `npx create-video` Remotion project inside `video/` at repo root
  (do NOT commit node_modules; add `video/` to .gitignore except
  `video/README.md` describing how to render).
- One `<Composition>` per scene + a `Main` composition sequencing them;
  read durations from the actual mp3/mp4 files (`getAudioDurationInSeconds`,
  `getVideoMetadata`) so re-cutting VO doesn't break timing.
- `<OffthreadVideo>` for recordings, `<Audio>` for VO; all file paths via
  `staticFile()`.
- Render: `npx remotion render Main out/autopsy-demo.mp4 --codec=h264
  --crf=18`. Deliverable = that file, 1080p, <200MB.
- Verify: the final mp4 plays start-to-finish, audio and subtitles sync,
  no placeholder text visible.

## Do NOT

- invent fake traces/checkpoint IDs (use SUBMISSION.md values)
- narrate over silent gaps faster than ~160wpm
- show `.env` contents anywhere
- spend effort on 3D — this is a flat, typographic, dev-tool aesthetic
