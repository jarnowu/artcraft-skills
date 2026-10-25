# ArtCraft skills for Claude Code

Skills that let Claude Code operate the ArtCraft apps from storytold through their command-line tools and MCP servers.

Unofficial. Not affiliated with storytold or the ArtCraft projects.

| Skill | App | Verified on |
|---|---|---|
| [filmcraft](skills/filmcraft/SKILL.md) | [FilmCraft](https://github.com/storytold/filmcraft), the Premiere Pro-style video editor | FilmCraft 0.12.0, Windows |

Each skill is self-contained. Only its short description sits in context; the instructions load when a task involves that app.

## Install

Clone the collection once, then copy the skills you want into your personal skills folder:

```bash
git clone https://github.com/jarnowu/artcraft-skills ~/artcraft-skills
```

```bash
cp -r ~/artcraft-skills/skills/filmcraft ~/.claude/skills/
```

To update, `git pull` in `~/artcraft-skills` and copy again. To use a skill in one project only, copy it into that project's `.claude/skills/` instead.

## FilmCraft

Covers connecting headless or live to the running app, a verified working loop (inspect, find the command, act on explicit ids, verify, save deliberately), frame-exact cuts, titles and fades, captions with burn-in, loudness targets, Lumetri color, export settings by destination, and clean stills for checking.

Requires FilmCraft with `filmcraft-cli` (bundled with the Windows installer at `C:\Program Files\FilmCraft\filmcraft-cli.exe`). Linux and macOS paths in the skill come from the upstream docs and are untested.

The skill works with the CLI alone. To also give Claude FilmCraft's MCP tools (Windows paths shown):

```bash
claude mcp add filmcraft --scope user -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" mcp
```

For live editing in the open app, start FilmCraft with `filmcraft.exe --control 9876`, then:

```bash
claude mcp add filmcraft-live --scope user -- "C:\Program Files\FilmCraft\filmcraft-cli.exe" --bridge 127.0.0.1:9876 mcp
```

Tests are in `skills/filmcraft/evals/`, in the format `claude plugin eval` reads. They use FilmCraft's built-in demo footage, so no media is needed. The `remove-section-live` case needs FilmCraft running with `--control 9877` and its `two-shots.fcproj` open.

## License

MIT
