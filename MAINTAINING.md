# Maintaining the skills

The ArtCraft apps are alpha and release often. The skills are written so that an app update usually needs no change, and when it does, the change is in one place.

## How each skill is laid out

Every `skills/<app>/SKILL.md` has the same five sections:

1. **Connect**: headless CLI, MCP, live app. Rarely changes.
2. **Safety**: rarely changes.
3. **Working loop**: how to inspect, find commands, act, verify and save. It teaches Claude to look up commands and parameters in the installed app instead of listing them, so it does not go stale.
4. **Traps (verified on <app> <version>)**: every version-specific fact lives here and only here.
5. **Recipes**: a pointer to `references/recipes.md`, short command sequences that were run on the stated version.

Each skill relies on the editing model of the app it was designed after for everything that works the same way, and documents only the differences.

## When an app releases a new version

1. Install it and note `<app>-cli --version`.
2. Run the skill's tests in `skills/<app>/evals/`. With Claude Code, from inside the skill folder: `claude plugin eval . --allow-tools Write,Edit,Bash` (add `--scaffold` when a case has input files). The live-app cases need the app running as their `case.yaml` says.
3. Re-check each line of the Traps section against the new version. Delete traps that were fixed upstream; add any new ones you hit, with the command that shows them.
4. Run the recipes in `references/recipes.md` as written and fix any that fail.
5. Update the version in the Traps heading and the "verified on" line, and the version column in the README.

Only write a fact into a skill after running it. Docs on the apps' main branches can describe features a released version does not have yet.

## Shared files

`shared/mcp_call.py` is copied into every skill's `scripts/` so each skill works when installed on its own. Edit only the copy in `shared/`, then:

```bash
python tools/sync_shared.py
```

`python tools/sync_shared.py --check` exits 1 if any copy differs; run it before committing.

## Adding a skill for another ArtCraft app

Copy the layout of an existing skill, run a few real tasks without the skill first to see where Claude struggles, and write only what fixes those failures. Add `scripts/` with `python tools/sync_shared.py`, add test cases under `evals/` (prefer the app's built-in demo content to bundled media), and add a row to the README table.
