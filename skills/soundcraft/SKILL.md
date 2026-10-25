---
name: soundcraft
description: Operates SoundCraft (ArtCraft's open-source Pro Tools-style audio workstation) through soundcraft-cli or its MCP server, headless or live in the running app - importing and editing clips, fades, clip gain, inserts and plugins, automation, markers, loudness and bounces. Use whenever a task involves SoundCraft, .scraft sessions, soundcraft-cli, or SoundCraft MCP tools, including mixing or mastering a song with it.
---

# SoundCraft

SoundCraft is an open-source clone of Avid Pro Tools: sessions, tracks, clips (regions), playlists, inserts, sends, busses, automation modes, memory locations, edit modes and clip gain work as they do there, so plan the work as you would in Pro Tools. Section 4 lists where it behaves differently.

Version: check `soundcraft-cli --version`; section 4 was verified on 0.12.1 (Windows). The repo changes quickly: trust the installed app's `soundcraft-cli commands FILTER` and `describe ID` over docs on the main branch.

Docs: [mcp.md](https://github.com/storytold/soundcraft/blob/main/docs/mcp.md), [control-protocol.md](https://github.com/storytold/soundcraft/blob/main/docs/control-protocol.md) (live-app methods, positions), [gaps.md](https://github.com/storytold/soundcraft/blob/main/docs/gaps.md) and [target-app-parity.md](https://github.com/storytold/soundcraft/blob/main/docs/target-app-parity.md) (what is missing compared with Pro Tools), [plugin-parity.md](https://github.com/storytold/soundcraft/blob/main/docs/plugin-parity.md), [issues](https://github.com/storytold/soundcraft/issues).

## 1. Connect

CLI: `C:/Program Files/SoundCraft/soundcraft-cli.exe` on Windows (not on PATH).

| Situation | Use |
|---|---|
| Edit, bounce or save a session file | CLI: `run --in S.scraft --cmd 'ID={json}' ... [--bounce out.wav --start T --end T] [--save S2.scraft] [--inspect]`, or `script FILE` (one `ID JSON` per line) |
| Several steps with feedback in one conversation | MCP in-process: `soundcraft-cli mcp` |
| The session open on the user's screen | The app must have been launched with `soundcraft --control PORT`. CLI: `soundcraft-cli app --port PORT METHOD_OR_COMMAND_ID '{json}'`. MCP: `soundcraft-cli mcp --connect PORT` |

`app` accepts a command id directly (`app --port 7802 mix.mute '{"tracks":["Hats"],"value":true}'`) as well as control methods such as `session.inspect` and `ui.screenshot {"path":"shot.png"}`.

If the MCP tools are not loaded in this session, call them from the shell with this skill's `scripts/mcp_call.py`:

```bash
python scripts/mcp_call.py --out-dir shots -- "C:/Program Files/SoundCraft/soundcraft-cli.exe" mcp --connect 7802 :: inspect_session '{}' :: screenshot '{}'
```

## 2. Safety

- Live, every command changes the user's open session at once. Say what you will change, and do not save unless asked.
- `run --save` overwrites an existing file without asking, and saving to another folder copies every source into that folder's `Audio Files/`. Save to a new session name.
- A live request can time out and still run later. Re-read with `session.inspect` before retrying an edit.

## 3. Working loop

1. **Inspect.** `run --in S.scraft --inspect` (tracks, clips with ids, mixer, markers, selection). For insert parameters and automation, `session.inspect {"detail":"full"}`.
2. **Find, don't guess.** `commands FILTER` lists ids; `describe ID` shows parameters. Plugins: `plugins` lists ids (`eq_7band`, `compressor`, `maximizer`, ...); `run --demo --cmd engine.plugins` lists every parameter with its id, range and unit.
3. **Act, naming the targets.** Pass `track`/`tracks`, `clip`/`clips` and positions explicitly. Positions are samples, `{"seconds": x}`, or strings like `"bars_beats:9|1|000"`.
4. **Verify.** A bounce reports `lufs` and `peak`; check the result with `session.inspect` and, if ffmpeg is installed, `ebur128`. Listen-critical changes (EQ, compression) need a bounce to judge.
5. **Save** with `--save` to a new name, or MCP `save_session`.

## 4. Traps (verified on SoundCraft 0.12.1)

- Each `run` starts a fresh session from `--in`, `--demo`, or empty; nothing persists without `--save`.
- `describe` shows commands as disabled ("nothing is selected") in an empty session. They work when you pass the targets.
- Misspelled parameter names are ignored silently (`session.format_time {"samples":N}` answers bar 1; the parameter is `at`). Check names with `describe`.
- `mix.insert` into an occupied slot replaces that plugin without warning. Read the track's inserts first, and use a free slot.
- The fader range is -144 to +12 dB; larger values are clamped silently. Use `clip.gain` for bigger changes.
- Volume automation in Read mode overrides the fader, as in Pro Tools: `mix.volume` then succeeds but changes nothing audible. Edit the automation or set the mode with `mix.automation_mode`.
- There is no loudness-target command; `normalize` is peak only. Bounce, read `lufs`, apply the difference as gain, and bounce again. For a whole mix, a `gain` insert in front of the master's `maximizer` does it in one place (see recipes).
- The `maximizer` ceiling limits sample peaks only; true peaks land about 1 dB higher. For a true peak of -1 dBTP, set its `ceiling` to about -2 dB.
- A bounce stops at the end of the last clip, cutting reverb and delay tails. Pass `--start` and `--end` together (`--start 0 --end 60`); `--end` on its own is ignored.
- Bounces are WAV, AIFF or FLAC; there is no MP3 or AAC output.

## 5. Recipes

[references/recipes.md](references/recipes.md): master a song to a loudness target; EQ and compression on tracks; mute and a marker in the open session.
