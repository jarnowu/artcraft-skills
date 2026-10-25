---
name: filmcraft
description: Operates the FilmCraft video editor (ArtCraft's Premiere Pro-style NLE) through filmcraft-cli or its MCP server, headless or live in the running app - cutting, assembling, titles, captions, audio levels, color, frames and export. Use whenever a task involves FilmCraft, .fcproj projects, filmcraft-cli, or FilmCraft MCP tools (command_run, sequence_inspect, ui_*), even if the user only says "edit this video in FilmCraft".
---

# FilmCraft

FilmCraft is a non-linear editor modelled on Adobe Premiere Pro. Its commands, menus and behaviour follow Premiere (Lift/Extract, Ripple Delete, Mark In/Out, Lumetri Color, Essential Sound, Essential Graphics, Nest, Speed/Duration), so think in Premiere terms to find things. Every edit is an undoable engine command; menus, shortcuts and timeline gestures all map to the same command ids.

Verified on FilmCraft 0.12.0 (Windows). Check `filmcraft-cli --version`; on a newer version, confirm anything surprising with `describe <id>`.

CLI location: Windows `C:/Program Files/FilmCraft/filmcraft-cli.exe` (not on PATH); per the upstream guide (not tested here), Linux deb/rpm `/usr/bin/filmcraft-cli`, macOS a separate `filmcraft-cli-<version>-macos-<arch>.zip` release asset. Upstream agent guide: https://github.com/storytold/filmcraft/blob/main/docs/agents.md

## 1. Choose how to connect

| Situation | Use | Notes |
|---|---|---|
| Work on files; user is not watching the app | Headless CLI: `filmcraft-cli [--project p.fcproj] …` | Each CLI call is a fresh session (see section 4). |
| Several edits with feedback in one conversation | MCP server in headless mode (`filmcraft-cli mcp`) | One session for the whole conversation; ids stay valid between calls. Open a file with `command_run file.open {"path":…}`. |
| Edit the project open on the user's screen | Bridge: MCP server with `--bridge 127.0.0.1:PORT`, or CLI `--bridge 127.0.0.1:PORT exec …` | Only works if the app was launched with `filmcraft --control PORT` (or `FILMCRAFT_CONTROL_PORT`). No command or preference turns it on later, so the user must save, quit and relaunch with the flag. |

Check what is available before planning: are FilmCraft MCP tools in this session (their server names depend on how they were registered; `claude mcp list` shows them), and is anything listening on the bridge port? Do not start, restart or close the user's FilmCraft yourself.

## 2. Safety

- In bridge mode every command changes the user's open project immediately. Say what you will change before changing it, and do not save unless asked.
- Never overwrite source media or the user's project file. Headless: work on a copy or `--save-as` a new file. Exports go to new filenames.
- `edit.undo` reverts the last edit. `history.list` shows what was done.

## 3. The operating loop

1. **Inspect.** `inspect project` / `project_inspect` gives the bin tree with item ids. `inspect sequence` / `sequence_inspect` gives tracks and clips with ids, `start`/`end`, `sourceIn`/`sourceOut` (ticks) and `link` (the clip's audio/video partner). Bins, items, tracks and clips share one id counter, so an id from one kind is never valid for another.
2. **Find the command; never guess ids or names.** `filmcraft-cli commands <filter>` (or `command_list` with `filter`) matches command ids and labels only, so search with Premiere's words: "caption" not "subtitle", "loud" not "lufs", "extract" not "delete range". Then `describe <id>` for the parameter list. Things that are not commands have their own lists: effects and their parameters (ranges, defaults) via `effects.list {"kind":"Video","detail":true}`, Lumetri looks via `lumetri.presets`, export presets via `export --list-presets`, fonts via `fonts.list`. `describe` shows `"enabled": false` for everything when no project is loaded; that is not an error.
3. **Act, naming the targets.** Commands that act on a selection fail headless ("select a clip in the Project panel") unless you pass ids: `items`, `clips` or `clip`. Track parameters take names like `"V1"`, `"A1"`, `"C1"`.
4. **Verify with the right tool.** Many commands return `null` on success (`effects.apply`, `sequence.extract`, `markers.markIn`), so re-inspect. `inspect sequence` does not list caption tracks (`captions.list` does) and shows only keyframe counts (the `.fcproj` is JSON if you need values). Look at the picture: see section 6.
5. **Save deliberately.** Only when the user wants the change kept, and to a path they agreed to.

## 4. Headless CLI mechanics

- Each CLI invocation loads the project, runs, and exits. Nothing persists unless `--save` (write back to `--project`) or `--save-as <path>` is given, so a call without them is a free dry run. The save flags take effect with `run`, `exec` and `import`; `inspect` ignores them.
- Chain dependent steps in one `run script.jsonl` (one `{"id":…,"params":…}` per line). If any line fails, `run` stops and saves nothing, even with `--save-as`, so earlier lines are lost too. Fix and rerun the whole script.
- A script cannot use ids created earlier in the same script unless you can predict them. When a step creates something whose id you need (a sequence, a title clip, a caption track), run it with `exec … --save`, read the id from its output, then continue. Or use the MCP session, where returned ids stay usable.
- A fresh project: `file.import` returns item ids (the first is 1 in an empty project). `file.newSequenceFromClip {"items":[id]}` makes a sequence matching the media and returns `{"sequence":…, "clips":[video, audio]}`. `file.newSequence` defaults to 1920x1080, 23.976 fps, 3+3 tracks unless you pass width, height and fps.
- Exports and saves create a `FilmCraft Previews/` folder next to the project file.

## 5. Time and frames

- 254016000000 ticks per second. Most commands also take `seconds`, `frame` or `timecode`; `timeline.place` takes `sourceIn` and `duration` only in ticks.
- Out points are inclusive, as in Premiere. To remove 0:30 to 0:40 at 24 fps, mark In at `seconds: 30` and Out at `frame: 959` (40 × 24 − 1); marking Out at `seconds: 40` removes one frame too many.
- `render --seconds S` shows the frame that contains S, truncating. To show frame N, pass a time inside it, such as (N + 0.5) / fps.

## 6. Seeing the result

- Headless: `filmcraft-cli --project p.fcproj render --seconds S --out f.png` (reads the saved project), or MCP `render_frame {"seconds":S}`. Both give the clean program frame.
- Bridge: `render` refuses to run (exit 2, "render is headless"). MCP `render_frame` and `render_preview` return a screenshot of the Program monitor panel, with player controls, not a clean frame. For a clean full-size frame: `playhead.set {"seconds":S}`, then `file.exportFrame {"path":"…/f.png","format":"png","target":"program"}`. `ui_screenshot` shows the whole window or one panel.
- Read the image you produced before describing it to the user.

## 7. Task recipes

[references/recipes.md](references/recipes.md) has tested command sequences and their traps for: cutting and assembling, removing a range, titles and fades, captions and lyrics (including burn-in), loudness, color with Lumetri, and choosing export settings by destination. Read the section for the task at hand before starting it.

## 8. Shell quoting (Windows)

- Use forward slashes in every path inside JSON. In Git Bash, JSON containing `\\` paths fails with "invalid escape".
- PowerShell 7: put JSON in plain single quotes, `'{"seconds":3}'`; `\"`-escaped quotes break it.
- For more than one step, write a `.jsonl` file and use `run`.
