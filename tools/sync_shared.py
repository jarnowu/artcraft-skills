#!/usr/bin/env python3
"""Copy the files in shared/ into every skill's scripts/ folder, or check that the copies match.

Each skill must work when installed on its own, so it carries its own copy of the shared helpers.
Edit the file in shared/, then run this script; never edit a skill's copy directly.

usage:
  python tools/sync_shared.py          copy shared/* into skills/*/scripts/
  python tools/sync_shared.py --check  exit 1 if any copy differs from shared/
"""
import filecmp
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent.parent
shared = sorted(p for p in (root / "shared").iterdir() if p.is_file())
skills = sorted(p for p in (root / "skills").iterdir() if (p / "SKILL.md").is_file())
check = "--check" in sys.argv[1:]

stale = []
for skill in skills:
    for src in shared:
        dst = skill / "scripts" / src.name
        if dst.is_file() and filecmp.cmp(src, dst, shallow=False):
            continue
        if check:
            stale.append(dst.relative_to(root))
        else:
            dst.parent.mkdir(exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"updated {dst.relative_to(root)}")

if check:
    for path in stale:
        print(f"out of date: {path}")
    sys.exit(1 if stale else 0)
