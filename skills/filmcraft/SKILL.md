---
name: filmcraft
description: Operates FilmCraft (ArtCraft's open-source Premiere Pro-style video editor) through filmcraft-cli or its MCP server, headless or live in the running app - cutting, assembling, titles, captions, audio levels, color, frames and export. Use whenever a task involves FilmCraft, .fcproj projects, filmcraft-cli, or FilmCraft MCP tools (command_run, sequence_inspect, ui_*), even if the user only says "edit this video in FilmCraft".
---

# FilmCraft

FilmCraft is an open-source clone of Adobe Premiere Pro: projects, bins, sequences, tracks, Lift/Extract, Ripple Delete, Mark In/Out, Lumetri Color, Essential Sound and Essential Graphics work as they do there, so plan the work and search for commands in Premiere terms. Every edit is an undoable engine command. Section 4 lists where it behaves differently.

Version: check `filmcraft-cli --version`; section 4 was verified on 0.12.0 (Windows). The repo changes quickly: trust the installed app's `filmcraft-cli commands WORD` and `describe ID` over docs on the main branch.

Docs: [agents.md](https://github.com/storytold/filmcraft/blob/main/docs/agents.md) (MCP, CLI), [gaps.md](https://github.com/storytold/filmcraft/blob/main/docs/gaps.md) and [target-app-parity.md](https://github.com/storytold/filmcraft/blob/main/docs/target-app-parity.md) (what is missing compared with Premiere), [file-format-parity.md](https://github.com/storytold/filmcraft/blob/main/docs/file-format-parity.md) (XML, FCPXML, OTIO, AAF fidelity), [issues](https://github.com/storytold/filmcraft/issues).

## 1. Connect

CLI: `C:/Program Files/FilmCraft/filmcraft-cli.exe` on Windows (not on PATH).

| Situation | Use |
|---|---|
| Change a project file or export | CLI: `filmcraft-cli [--project p.fcproj] [--save / --save-as F] run script.jsonl` (one `{"id","params"}` per line), `exec ID '{json}'`, `inspect`, `render`, `export`, `probe` |
| Several edits with feedback in one conversation | MCP headless: `filmcraft-cli mcp`; open a file with `command_run file.open {"path":...}` |
| The project open on the user's screen | The app must have been launched with `filmcraft --control PORT`; nothing turns it on later. CLI: add `--bridge 127.0.0.1:PORT`. MCP: `filmcraft-cli --bridge 127.0.0.1:PORT mcp` |

If the MCP tools are not loaded in this session, call them from the shell with this skill's `scripts/mcp_call.py`:

```bash
python scripts/mcp_call.py --out-dir shots -- "C:/Program Files/FilmCraft/filmcraft-cli.exe" --bridge 127.0.0.1:9876 mcp :: sequence_inspect '{}' :: ui_screenshot '{"panel":"Timeline"}'
```

## 2. Safety

- With `--bridge`, every command changes the user's open project at once. Say what you will change, and do not save unless asked.
- Save new work with `--save-as` to a new file. Export to new filenames, never to a source clip's own path (an export there destroys the footage, open issue #2793).
- `edit.undo` reverts the last edit; `history.list` shows what was done.

## 3. Working loop

1. **Inspect.** `inspect project` gives bins and item ids; `inspect sequence` gives tracks and clips with ids, `start`/`end`, `sourceIn`/`sourceOut` in ticks (254016000000 per second) and `link` (the audio/video partner). Bins, items, tracks and clips share one id counter.
2. **Find, don't guess.** `commands WORD` matches ids and labels only, so search with Premiere words ("caption" not "subtitle", "loud" not "lufs", "extract" not "delete range"), then `describe ID`. Effects and their parameter ranges: `exec effects.list '{"kind":"Video","detail":true}'`; Lumetri looks: `lumetri.presets`; export presets: `export --list-presets`.
3. **Act, naming the targets** with `items`, `clips` or `clip` ids and track names like `"V1"`, `"A1"`, `"C1"`. Times also take `seconds`, `frame` or `timecode`.
4. **Verify.** Re-inspect after commands that return `null`, and look at frames: headless `render --seconds S --out f.png`; live see section 4.
5. **Save** only when the user wants the change kept.

## 4. Traps (verified on FilmCraft 0.12.0)

- Each CLI call is a fresh session. `--save` / `--save-as` take effect with `run`, `exec` and `import`; `inspect` ignores them.
- If any line of a `run` script fails, nothing is saved, earlier lines included. A script cannot use ids it creates unless you can predict them: run the creating step with `exec ... --save`, read the id, continue.
- Commands that act on a selection fail headless ("select a clip in the Project panel") unless given ids. `describe` shows every command disabled when no project is loaded; that is not an error.
- `file.newSequence` defaults to 1920x1080, 23.976 fps, 3+3 tracks; `file.newSequenceFromClip {"items":[id]}` matches the media.
- Out points are inclusive. To remove 0:30 to 0:40 at 24 fps, mark Out at `frame: 959`, not `seconds: 40`.
- `render --seconds S` truncates to the frame containing S; for frame N pass (N + 0.5) / fps.
- `effects.apply` returns `null` and inserts the new effect at index 0, shifting the others. Read the order from `inspect sequence` before `effects.setParam`.
- `inspect sequence` omits caption tracks (use `captions.list`) and shows only keyframe counts.
- Live: `render` refuses to run, and MCP `render_frame` returns a Program-monitor screenshot with player controls. For a clean frame: `playhead.set {"seconds":S}`, then `file.exportFrame {"path":"f.png","format":"png","target":"program"}`.
- Export defaults without a preset: H.264 VBR 20 Mbps at any resolution, AAC 320 kbps. H.265 has no CRF mode. Normalize a delivery mix with `loudnessLufs` in `file.exportMedia`.
- Shell: use forward slashes in JSON paths (Git Bash rejects `\\` with "invalid escape"); in PowerShell 7 put JSON in plain single quotes.
- No Dynamic Link to EffectCraft: import its ProRes 4444 render as footage, and after a re-render to the same path run `media.refreshChanged`.

## 5. Recipes

[references/recipes.md](references/recipes.md): assembling and removing ranges, titles and fades, captions with burn-in, loudness, Lumetri color, export settings by destination, and stills for checking.
