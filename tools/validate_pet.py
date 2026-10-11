#!/usr/bin/env python3
"""Validate every Codex v2 pet package in this repository.

Checks the pet manifest, atlas geometry, per-row frame counts, cell occupancy,
unused-cell transparency, and transparent-pixel RGB residue.

Usage: python tools/validate_pet.py [pets-dir]
Exit code is non-zero when any pet fails.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ATLAS_WIDTH = CELL_WIDTH * COLUMNS
ATLAS_HEIGHT = CELL_HEIGHT * 11
SPRITE_VERSION = 2
USED_CELLS_PER_ROW = {
    0: 6,   # idle (column 6 additionally holds the v2 neutral/rest frame
    1: 8,   # running-right
    2: 8,   # running-left
    3: 4,   # waving
    4: 5,   # jumping
    5: 8,   # failed
    6: 6,   # waiting
    7: 6,   # running
    8: 6,   # review
    9: 8,   # look directions 000-157.5
    10: 8,  # look directions 180-337.5
}
ALPHA_CUTOFF = 16
# In a v2 (11-row) atlas, row 0 column 6 is reserved for the neutral/rest frame
# that the look-direction pointer falls back to, so it is a used cell even though the
# idle row itself only spans columns 0-5.
NEUTRAL_LOOK_FRAME = (0, 6)


def validate_cell(image: Image.Image, row: int, column: int, used: bool) -> list[str]:
    cell = image.crop(
        (column * CELL_WIDTH, row * CELL_HEIGHT, (column + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT)
    )
    alpha = cell.getchannel("A")
    visible = [value > ALPHA_CUTOFF for value in alpha.getdata()]
    visible_count = sum(visible)
    problems: list[str] = []
    label = "row %d column %d" % (row, column)
    if used and visible_count == 0:
        problems.append("%s is a required cell but is completely empty" % label)
    if not used and visible_count > 0:
        problems.append("%s must stay unused but has %d visible pixels" % (label, visible_count))
    if used:
        rgba = cell.load()
        residue = 0
        for y in range(CELL_HEIGHT):
            for x in range(CELL_WIDTH):
                red, green, blue, cell_alpha = rgba[x, y]
                if cell_alpha == 0 and (red or green or blue):
                    residue += 1
        if residue:
            problems.append("%s keeps RGB data under fully transparent pixels (%d px)" % (label, residue))
    return problems


def validate_pet(pet_dir: Path) -> list[str]:
    manifest_path = pet_dir / "pet.json"
    if not manifest_path.is_file():
        return ["missing pet.json"]
    problems: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return ["pet.json is not readable JSON: %s" % error]

    if manifest.get("id") != pet_dir.name:
        problems.append('id "%s" does not match folder name "%s"' % (manifest.get("id"), pet_dir.name))
    for field in ("displayName", "description"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append("%s must be a non-empty string" % field)
    if manifest.get("spriteVersionNumber") != SPRITE_VERSION:
        problems.append("spriteVersionNumber must be %d" % SPRITE_VERSION)
    sprite_value = manifest.get("spritesheetPath")
    if not isinstance(sprite_value, str) or not sprite_value:
        problems.append("spritesheetPath must be set")
        return problems
    sprite_path = pet_dir / sprite_value
    if not sprite_path.is_file():
        problems.append("spritesheet not found: %s" % sprite_value)
        return problems
    if Path(sprite_value).is_absolute() or ".." in Path(sprite_value).parts:
        problems.append("spritesheetPath must stay inside the pet folder")
        return problems

    with Image.open(sprite_path) as handle:
        if handle.mode != "RGBA":
            problems.append("spritesheet must be RGBA, got %s" % handle.mode)
        if handle.size != (ATLAS_WIDTH, ATLAS_HEIGHT):
            problems.append(
                "spritesheet must be %dx%d, got %dx%d"
                % (ATLAS_WIDTH, ATLAS_HEIGHT, handle.width, handle.height)
            )
            return problems
        image = handle.convert("RGBA")
        for row, used in USED_CELLS_PER_ROW.items():
            if used > COLUMNS:
                problems.append("row %d declares more cells than the atlas has columns" % row)
                continue
            for column in range(COLUMNS):
                is_used = column < used or (row, column) == NEUTRAL_LOOK_FRAME
                problems.extend(validate_cell(image, row, column, is_used))
    return problems


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "pets"
    if not root.is_dir():
        print("pets directory not found: %s" % root, file=sys.stderr)
        return 2
    pet_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not pet_dirs:
        print("no pets found in %s" % root, file=sys.stderr)
        return 1
    failures = 0
    for pet_dir in pet_dirs:
        problems = validate_pet(pet_dir)
        if problems:
            failures += 1
            print("FAIL %s" % pet_dir.name)
            for problem in problems[:12]:
                print("     - %s" % problem)
            if len(problems) > 12:
                print("     - ... %d more" % (len(problems) - 12))
        else:
            print("OK   %s" % pet_dir.name)
    print("%d/%d pets valid" % (len(pet_dirs) - failures, len(pet_dirs)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())