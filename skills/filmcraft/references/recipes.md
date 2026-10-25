# FilmCraft task recipes

Tested on FilmCraft 0.12.0. Ids below (item 1, clips 6/7, clip 9) are what a fresh project produced in testing; always use the ids your own commands return or `inspect` shows.

## Contents
- Start a project from media
- Assemble a cut from source ranges
- Remove a range and close the gap
- Split and delete clips
- Title over video, with a fade
- Captions and lyrics from an SRT
- Audio loudness to a target
- Color: Lumetri looks and manual grading
- Export
- Stills for checking

## Start a project from media

```jsonl
{"id":"file.import","params":{"paths":["C:/media/clip.mp4"]}}
{"id":"file.newSequenceFromClip","params":{"items":[1]}}
```

`filmcraft-cli --save-as C:/media/clip.fcproj run start.jsonl`. The sequence matches the media's size, rate and audio; the result names the video and audio clip ids (`"clips":[6,7]`). Media is referenced in place, not copied.

## Assemble a cut from source ranges

`timeline.place` puts a range of a project item on the timeline in one step, video and linked audio together. Example: keep 0:10–0:25 and 1:00–1:15 back to back on a new 720p24 sequence (ticks: 10 s = 2540160000000, 15 s = 3810240000000, 60 s = 15240960000000):

```jsonl
{"id":"file.newSequence","params":{"name":"Short","width":1280,"height":720,"fps":24}}
{"id":"timeline.place","params":{"item":1,"track":"V1","seconds":0,"sourceIn":2540160000000,"duration":3810240000000}}
{"id":"timeline.place","params":{"item":1,"track":"V1","seconds":15,"sourceIn":15240960000000,"duration":3810240000000}}
```

`seconds` is the timeline position; `sourceIn` and `duration` are ticks. Give `file.newSequence` the source's width, height and fps, or it uses 1920x1080 at 23.976.

## Remove a range and close the gap

Premiere's Extract: mark In and Out on the program, then `sequence.extract`. It cuts every track, keeps audio and video linked, closes the gap, clears the marks and leaves the playhead on the new edit.

```jsonl
{"id":"markers.markIn","params":{"seconds":30}}
{"id":"markers.markOut","params":{"frame":959}}
{"id":"sequence.extract","params":{}}
```

The Out point is inclusive: to remove exactly 0:30–0:40 at 24 fps, Out is frame 959, not 40 s. `sequence.lift` removes the range but leaves a gap. Check the result: the clip after the cut should have `start` at 30 s and `sourceIn` at 40 s.

## Split and delete clips

- `timeline.razor {"seconds":S}` cuts all tracks at S (video and audio both, so it reports 2 cuts for one A/V clip). Add `"track":"V1"` to cut one track.
- `edit.rippleDelete {"clips":[id]}` removes clips and closes the gap; `edit.clear` leaves the gap.
- `timeline.trim {"clip":id,"edge":"in|out","mode":"regular|ripple","delta":ticks}` trims an edge.

## Title over video, with a fade

```text
graphics.newText   {"text":"MY TITLE","seconds":3,"time":0}         -> {"clip":9,"layer":0}
graphics.set       {"clip":9,"layer":0,"props":{"align":"center"}}
graphics.align     {"clip":9,"layers":[0],"align":"hcenter"}
graphics.align     {"clip":9,"layers":[0],"align":"vcenter"}
effects.setParam   {"clip":9,"effect":"opacity","param":"opacity","value":100,"time":<fade start ticks>,"keyframe":true}
effects.setParam   {"clip":9,"effect":"opacity","param":"opacity","value":0,"time":<last frame ticks>,"keyframe":true}
```

- `graphics.newText` creates a graphic clip on the first free video track above the footage and returns its clip id; run it on its own (`exec … --save`) to learn the id before the next steps.
- New text is left-aligned with its anchor at the frame centre, so it runs off to the right until you set `align` and use `graphics.align`. Default size is 100 px and the fill is white. `graphics.list {"clip":id}` shows each layer's position and on-screen `quad`, to check placement without rendering. Other styling (font, size, `fill_color`, stroke, shadow, background) goes in `graphics.set` props; fonts come from `fonts.list`.
- There is no fade command; fades are opacity keyframes as above. Keyframe times are sequence ticks.

## Captions and lyrics from an SRT

```text
captions.import  {"path":"C:/media/lyrics.srt"}     -> {"captions":4,"track":11,...}
captions.list    {}                                 (shows text and in/out per caption)
captions.setStyle {"track":"C1","size":…,"color":"#ffffff","anchor":"bottom",…}
```

- `captions.import` takes `path` (one string), unlike `file.import`'s `paths` list. It creates the caption track itself; SRT times land on exact frames.
- `inspect sequence` does not show caption tracks; use `captions.list`.
- Burn-in is an export setting, not a command: `"burnCaptions": true` in `file.exportMedia` params or in `export --settings`. `"captionSidecar": "srt"|"vtt"` writes a separate file instead.
- Transcribing speech to captions exists (`transcript.generate`, then `transcript.createCaptions`) but needs a speech model (`transcript.models`, `transcript.downloadModel`); not covered by these tests.

## Audio loudness to a target

**For the finished mix** (a delivery spec such as -14 LUFS for YouTube), normalize at export: add `"loudnessLufs": -14` to `file.exportMedia` params (or `export.resolve` to preview it). It measures the whole mix and applies a -2 dBTP true-peak limit by default; on the demo project it took -24.7 LUFS to -14.1. The project itself is unchanged.

**For one clip's level inside the edit** (balancing music against dialogue), use Essential Sound:

```jsonl
{"id":"essentialSound.setType","params":{"clips":[7],"type":"music"}}
{"id":"essentialSound.autoMatch","params":{"clips":[7],"target":-14}}
```

- `autoMatch` only works on clips that have an audio type (dialogue, music, sfx, ambience). Without `setType` first it fails with "no clips with an audio type and audible audio in the selection".
- It measures that clip's integrated loudness, sets static clip gain and returns `measuredLufs` and `gainDb`. With other audio in the sequence, the mix will not land on the target; use export normalization for that. FilmCraft has no separate loudness meter; to check an export, use ffmpeg `ebur128=peak=true` if it is installed.
- Use the audio clip id (the second of `newSequenceFromClip`'s `clips`, or the clip on an `A` track in `inspect sequence`).

## Color: Lumetri looks and manual grading

Color tools are effects, so `commands color` does not find them.

- **Ready-made looks:** `lumetri.presets` lists them by folder (Cinematic: Teal Shadows Warm Skin, Golden Dusk, Hard Sun, Steel Blue, Night Exterior; Film Emulation; Monochrome; Technical). Apply with `lumetri.applyPreset {"name":"Golden Dusk","clips":[6]}`. Each apply adds a new Lumetri effect, so applying to a clip that already has one stacks a second instance.
- **Manual:** `effects.apply {"clips":[6],"effect":"lumetri"}` returns `null` and inserts Lumetri at index 0, ahead of motion, opacity and time_remap, which shifts their indexes. Read the order from `inspect sequence`, then `effects.setParam {"clip":6,"effect":0,"param":"temperature","value":20}`.
- Parameter ids, ranges and defaults: `effects.list {"kind":"Video","detail":true}`, the `lumetri` entry's `paramInfo` (60 parameters). Temperature, tint and exposure are offsets from 0; `shadow_tint` and `highlight_tint` are colours whose neutral is mid grey (0.5, 0.5, 0.5), so a dark tint colour also darkens.
- A preset is a starting point, not an answer. Render the same moment before and after and look: on footage that is already strongly coloured, a warm preset can push it too far, and a manual grade (or a preset plus adjustments) is the better result.

## Export

Pick settings for where the file goes, then preview them: `export.resolve` takes the same params as `file.exportMedia` and returns a `summary` with codec, bitrate and `estimated_size`.

- **Upload to YouTube, Vimeo or similar:** the platform re-encodes, so give it quality, not a small file. A "Match Source – Adaptive" preset keeps the source frame size; the YouTube/Vimeo presets force 1920x1080 or 4K.
- **Preview or review copy:** small is fine: `"format":"h264","bitrateMode":"crf","crf":23`.
- **Hosting the file yourself on a website:** CRF as above, plus faststart (below).
- **Handing to another editor:** ProRes/DNxHR presets, or interchange (`file.exportFcpxml`, `file.exportOtio`, `file.exportEdl`, `file.exportAaf`).

Defaults and traps:
- With no preset or settings, H.264 is VBR at a 20 Mbps target at any resolution and audio is AAC 320 kbps, more than most sources carry. `"settings":{"audio":{"bitrate_kbps":192}}` (or the source's bitrate) fixes the audio; `settings` objects merge over the defaults.
- H.265 has no CRF mode ("choose CBR or VBR, 1 pass") and uses the hardware encoder; give `bitrateMode` and `bitrateKbps`.
- Test a short range first: `export out.mp4 --start 0 --end 5 …` (seconds).
- FilmCraft writes the MP4 index at the end. Only for files streamed from your own web server does that matter; then remux with ffmpeg (`-c copy -map 0 -movflags +faststart`) into a new file and tell the user it was done outside FilmCraft. Skip it for uploads and local files.
- MCP `command_run file.exportMedia` needs `"wait": true` to return after the file is written; `run` scripts and the `export` subcommand wait by themselves.

## Stills for checking

- Headless: `render --seconds S --out f.png`, with S inside the frame you want ((N + 0.5) / fps for frame N).
- Bridge: `playhead.set {"seconds":S}` then `file.exportFrame {"path":"…/f.png","format":"png","target":"program"}`.
- A PNG `file.exportMedia` writes numbered files (`f000.png`, `f001.png`, …) even for one frame; prefer `render` or `file.exportFrame` for single stills.
- For an edit point, show both sides: the last frame before and the first frame after.
