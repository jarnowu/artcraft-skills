---
name: effectcraft
description: Operates EffectCraft (ArtCraft's open-source After Effects-style motion graphics app) through effectcraft-cli, its After Effects-style scripting, or its MCP server, headless or live in the running app - comps, text and shape layers, keyframes, expressions, effects, alpha renders. Use whenever a task involves EffectCraft, .ecproj projects, effectcraft-cli, or EffectCraft MCP tools, including titles, lower thirds and motion graphics made with it.
---

# EffectCraft

EffectCraft is an open-source clone of Adobe After Effects: comps, layers, property groups, keyframes, expressions, effects and a render queue work as they do there, so plan the work as you would in After Effects. Its scripting engine runs the After Effects object model (`app.project`, `addComp`, `layers.addText`, `TextDocument`, `setValueAtTime`, `KeyframeEase`, `ADBE` match names, expressions such as `wiggle`) in JavaScript, so a normal After Effects script is usually the fastest way to build something. Section 4 lists where the clone behaves differently.

Version: check `effectcraft-cli --version`; section 4 was verified on 0.16.0 (Windows). The repo changes quickly: trust the installed app's command list (`effectcraft-cli commands --filter WORD`) over docs on the main branch.

Docs: [agents.md](https://github.com/storytold/effectcraft/blob/main/docs/agents.md) (MCP, CLI, property paths), [scripting-parity.md](https://github.com/storytold/effectcraft/blob/main/docs/scripting-parity.md), [gaps.md](https://github.com/storytold/effectcraft/blob/main/docs/gaps.md) and [target-app-parity.md](https://github.com/storytold/effectcraft/blob/main/docs/target-app-parity.md) (what is missing compared with After Effects), [issues](https://github.com/storytold/effectcraft/issues).

## 1. Connect

CLI: `C:/Program Files/EffectCraft/effectcraft-cli.exe` on Windows (not on PATH).

| Situation | Use |
|---|---|
| Build or change a project file | CLI: `script build.jsx`, `exec`, `set`, `get`, `props`, `render`, `render-frame`, each with `--project F.ecproj` (or `--empty`) and `--save` / `--save-as F` |
| Several steps with feedback in one conversation | MCP headless: `effectcraft-cli mcp` (add `--autosave` to checkpoint unsaved work) |
| The project open on the user's screen | The app must have been launched with `effectcraft --control PORT`. CLI: add `--bridge PORT` to any command. MCP: `effectcraft-cli mcp --bridge PORT` |

If the MCP tools are not loaded in this session, call them from the shell with this skill's `scripts/mcp_call.py`:

```bash
python scripts/mcp_call.py --out-dir shots -- "C:/Program Files/EffectCraft/effectcraft-cli.exe" mcp --bridge 9881 :: get_comp '{}' :: render_frame '{"time":1}'
```

Calls in one invocation share a session; images are saved as files. `--list` prints the server's tools.

## 2. Safety

- With `--bridge`, every command changes the user's open project at once. Say what you will change, and do not save unless asked.
- Save new work with `--save-as` to a new file; never overwrite the user's project or footage.
- Do not run `help.*` commands: they open web pages or windows on the user's desktop.
- A script that throws keeps the edits it already made. Wrap scripts in `app.beginUndoGroup()` / `app.endUndoGroup()` so one undo reverts them.

## 3. Working loop

1. **Inspect.** `info --json` (project, comps, layers), `props COMP LAYER --flat` (every property path, such as `transform/position` or `effects/#1/blurriness`), `get COMP LAYER PATH --time S --json` (returns `value` and, with expressions, `evaluated` and `expressionError`).
2. **Find, don't guess.** `commands --filter WORD` lists command ids with their parameters. Effects are not commands: list them with `exec effect.list --params '{"filter":"glow"}'`; fonts with `exec text.fonts --params '{"query":"Inter"}'`. Unknown parameter keys are rejected with the accepted list.
3. **Act.** Build comps, layers, keyframes and expressions in one script (`script build.jsx --empty --save-as out.ecproj`). Use `exec` / `set` for single changes. Name layers on creation so later steps can refer to them by name.
4. **Verify.** Render frames and look at them: `render-frame --comp C --time S --out f.png` (add `--transparent` to see alpha). Check renders with ffprobe if it is installed; the render summary does not state codec or alpha.
5. **Save** with `--save` / `--save-as`; in MCP with `save_project {path}`.

## 4. Traps (verified on EffectCraft 0.16.0)

- `exec`, `run`, `get`, `set` and `info` without `--project` or `--empty` open EffectCraft's demo project ("EffectCraft Intro", 1920x1080, 29.97 fps) and act on it.
- Each CLI call is a fresh session: nothing persists without `--save` / `--save-as`.
- The last rendered frame is at `duration - frameDuration` (4.958 s in a 5 s, 24 fps comp). A key at exactly `duration` is never reached, so end fades one frame early.
- `keys.info` takes `{"keys":[{"layer": <numeric layer id>, "prop": <numeric property uid>, "time": S}]}`. With a layer name or property path it silently returns `[]`. The uid is in `props COMP LAYER --json` (the `uid` of each node).
- Text fill, size and font cannot be read with `get` (it returns only the text). Read them in a script: `layer.property("Source Text").value.fillColor`. Set them with `exec layer.setText --params '{"layer":"Headline","fill":"#FF8C1A"}'` or in a script.
- `commands --filter glow` finds only the layer styles (Outer/Inner Glow). The Glow effect is `ec.stylize.glow` in `effect.list`; apply it with `exec effect.apply --params '{"effect":"ec.stylize.glow","layers":[2]}'`.
- `render-frame` composites over the comp background colour, so a dark semi-transparent element can be invisible in a preview. Use `--transparent`.
- Alpha: `render --format prores --prores 4444 --channels rgba --audio off --out x.mov` gives ProRes 4444 with alpha (`yuva444p12le`). H.264 has no alpha.
- Scripts can read files only inside the saved project's folder and cannot write files unless the user enables Preferences > Scripting & Expressions > Allow Scripts to Write Files. Render and export with the CLI, not from a script.
- There is no Dynamic Link to FilmCraft. Hand motion graphics over as a ProRes 4444 or PNG sequence render; after re-rendering to the same path, FilmCraft's `media.refreshChanged` picks up the new file.

## 5. Recipes

[references/recipes.md](references/recipes.md): a scripted title with slide-in, ease and fade; a lower third rendered with alpha and checked; a live edit (colour and glow) through the bridge.
