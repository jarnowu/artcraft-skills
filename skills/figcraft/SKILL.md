---
name: figcraft
description: Operates FigCraft (ArtCraft's open-source Figma-style design app) through figcraft-cli scripts or its MCP server, headless or attached to the running app - frames, text, auto layout, components, templates, and PNG/SVG/PDF export. Use whenever a task involves FigCraft, .figcraft files, figcraft-cli, or FigCraft MCP tools, including social posts, thumbnails and UI mockups made with it.
---

# FigCraft

FigCraft is an open-source clone of Figma: pages, frames, groups, auto layout, components and instances, styles and variables work as they do there, so design as you would in Figma. It has no `figma.*` plugin API; everything is a FigCraft command (`node.create`, `node.set`, `text.set`, `align.*`, `file.export`, ...). Section 4 lists where it behaves differently.

Version: check `figcraft-cli --version`; section 4 was verified on 0.10.0 (Windows). The docs on the main branch can describe features the installed version lacks: trust `figcraft-cli commands --filter WORD`.

Docs: [mcp.md](https://github.com/storytold/figcraft/blob/main/docs/mcp.md) (conventions, tools, `$step` references), [cli.md](https://github.com/storytold/figcraft/blob/main/docs/cli.md), [file-format-parity.md](https://github.com/storytold/figcraft/blob/main/docs/file-format-parity.md) (.fig, SVG, PDF fidelity), [gaps.md](https://github.com/storytold/figcraft/blob/main/docs/gaps.md), [issues](https://github.com/storytold/figcraft/issues).

## 1. Connect

CLI: `C:/Program Files/FigCraft/figcraft-cli.exe` on Windows (not on PATH).

| Situation | Use |
|---|---|
| Build or change a file | CLI: `run script.json [--in in.figcraft] [--out out.figcraft]`, plus `info`, `render`, `export`, `convert` |
| Several steps with feedback in one conversation | MCP headless: `figcraft-cli mcp` |
| The file open on the user's screen | The app must have been launched with `figcraft --control PORT`. Only the MCP server reaches it: `figcraft-cli mcp --attach PORT`. The CLI has no other route to a running app. |

If the MCP tools are not loaded in this session, call them from the shell with this skill's `scripts/mcp_call.py`:

```bash
python scripts/mcp_call.py --out-dir shots -- "C:/Program Files/FigCraft/figcraft-cli.exe" mcp --attach 7981 :: inspect_document '{"depth":3}' :: screenshot '{}'
```

Calls in one invocation share a session; screenshots are saved as files. `--list` prints the tools.

## 2. Safety

- Attached, every command changes the user's open file at once. Say what you will change, and do not save unless asked.
- `run --in a.figcraft --out b.figcraft` never touches `a`; write results to a new file.
- Never run `collab.share` or other `collab.*` commands unless asked: they publish the document to a public server.

## 3. Working loop

1. **Inspect.** `info FILE` gives a summary. For the tree, `node.get {"id":N}` in a script (direct children only) or MCP `inspect_document {"depth":N}` / `get_node {"id":N,"depth":N}`.
2. **Find, don't guess.** `commands --filter WORD` lists ids with parameters. The `node.set` entry lists every layer property (fills, strokes, layout, text, constraints). `template.list` lists starter templates.
3. **Act.** A `run` script is a JSON array of `{"command","params"}`. Refer to ids created earlier in the same script with `{"$step": n}` (zero-based step index). Attached or in MCP, use `batch` the same way.
4. **Verify.** Export or render a PNG and look at it, and check its pixel size. `text.missingFonts` lists fonts that fell back to a substitute.
5. **Save** with `--out` (CLI) or `file.saveAs {path}` / `save_file {path}`.

## 4. Traps (verified on FigCraft 0.10.0)

- `run` is all-or-nothing: if any step fails, nothing is written (`--out` too) and it exits 1. Results print after the whole script.
- Ids are assigned in order in a new document (page 1, first layer 2). Prefer `{"$step": n}` to hard-coded ids; `parent` and `ids` accept it.
- A layer created without `parent` lands on the page, not in the frame you just made. `x`/`y` are relative to the parent.
- New text is black (`#000000`) unless a `fill` is given.
- Export size is what the layers paint: a frame with an outside stroke exports larger (a 1920x1080 frame with a 4 px outside stroke exports 1928x1088). For an exact size, remove outside strokes or effects that spill, and export with `size {"by":"width","value":1280}`.
- `align.hcenter` / `align.vcenter` on a single layer centre it in its parent frame.
- Built-in templates: `mobile-app`, `landing-page`, `dashboard`, `design-system`, `wireframe-kit`, `social-posts`, `slides`, `icon-set`. There is no thumbnail template; `slides` is the 16:9 one (1920x1080).
- Fonts: installed system fonts are used. For renders that match on every machine, add `--no-system-fonts`.
- Attached, the open document can differ from the file on disk: the app may have reopened a recovery copy with unsaved changes from an earlier session. Read the live state (`inspect_document`) before editing, and mention any difference from the saved file to the user.

## 5. Recipes

[references/recipes.md](references/recipes.md): a social post built with one script; a template turned into an exact-size thumbnail; a live edit of the open file through `mcp --attach`.
