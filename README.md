# ArtCraft skills for Claude Code

Skills that let Claude Code operate the open-source ArtCraft apps from storytold through their command-line tools and MCP servers.

Unofficial. Not affiliated with storytold or the ArtCraft projects.

| Skill | App | Modelled on | Verified on |
|---|---|---|---|
| [filmcraft](skills/filmcraft/SKILL.md) | [FilmCraft](https://github.com/storytold/filmcraft) video editor | Premiere Pro | 0.12.0, Windows |
| [effectcraft](skills/effectcraft/SKILL.md) | [EffectCraft](https://github.com/storytold/effectcraft) motion graphics | After Effects | 0.16.0, Windows |
| [figcraft](skills/figcraft/SKILL.md) | [FigCraft](https://github.com/storytold/figcraft) interface design | Figma | 0.10.0, Windows |
| [soundcraft](skills/soundcraft/SKILL.md) | [SoundCraft](https://github.com/storytold/soundcraft) audio workstation | Pro Tools | 0.12.1, Windows |

Each skill has Claude work as it would in the original app and spells out only where the clone differs, plus how to reach the app headless or live in its open window. Only a skill's short description sits in context; the instructions load when a task involves that app. Linux and macOS paths in the skills come from the upstream docs and are untested.

## Install

Clone the collection once, then copy the skills you want into your personal skills folder:

```bash
git clone https://github.com/jarnowu/artcraft-skills ~/artcraft-skills
```

```bash
cp -r ~/artcraft-skills/skills/filmcraft ~/.claude/skills/
```

To update, `git pull` in `~/artcraft-skills` and copy again. To use a skill in one project only, copy it into that project's `.claude/skills/` instead.

## Requirements

The app, with its command-line tool (bundled with the Windows installers in `C:\Program Files\<App>\<app>-cli.exe`). Python 3 for the skills' `scripts/mcp_call.py`, which calls an app's MCP server from the shell when its tools are not set up in Claude Code.

## Optional: the apps' MCP servers

The skills work with the CLIs alone. To give Claude an app's MCP tools as well (Windows paths shown):

| App | Headless | Live in the open app (start the app with `--control PORT` first) |
|---|---|---|
| FilmCraft | `claude mcp add filmcraft --scope user -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" mcp` | `... filmcraft-cli.exe --bridge 127.0.0.1:PORT mcp` |
| EffectCraft | `claude mcp add effectcraft --scope user -- "C:\Program Files\EffectCraft\effectcraft-cli.exe" mcp` | `... effectcraft-cli.exe mcp --bridge PORT` |
| FigCraft | `claude mcp add figcraft --scope user -- "C:\Program Files\FigCraft\figcraft-cli.exe" mcp` | `... figcraft-cli.exe mcp --attach PORT` |
| SoundCraft | `claude mcp add soundcraft --scope user -- "C:\Program Files\SoundCraft\soundcraft-cli.exe" mcp` | `... soundcraft-cli.exe mcp --connect PORT` |

## Tests

Each skill has test cases in `skills/<app>/evals/`, in the format `claude plugin eval` reads. They use the apps' built-in demo content or small bundled project files, so no media is needed. Cases tagged `needs-live-app` need the app running with the control port their `case.yaml` names.

## Maintaining

See [MAINTAINING.md](MAINTAINING.md): how the skills are laid out, what to re-check when an app releases a new version, and how the shared helper script is kept in sync.

## License

MIT
