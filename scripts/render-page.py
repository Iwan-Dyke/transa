"""Render a page from the modern cPages notebook format for capture experiments."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

import cairosvg


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("archive", type=Path)
parser.add_argument("page", type=int, help="one-based page number")
args = parser.parse_args()
output = Path(".local/render-test")
output.mkdir(parents=True, exist_ok=True)
stem = output / f"page-{args.page:02}"

with zipfile.ZipFile(args.archive) as archive:
    content_name = next(n for n in archive.namelist() if n.endswith(".content"))
    content = json.loads(archive.read(content_name))
    pages = sorted(content["cPages"]["pages"], key=lambda p: p["idx"]["value"])
    if not 1 <= args.page <= len(pages):
        parser.error(f"page must be between 1 and {len(pages)}")
    page = pages[args.page - 1]
    document_id = content_name.removesuffix(".content")
    member = f"{document_id}/{page['id']}.rm"
    stem.with_suffix(".rm").write_bytes(archive.read(member))

renderer = Path(sys.executable).parent / "rmc"
with stem.with_suffix(".warnings.log").open("w") as warnings:
    subprocess.run(
        [str(renderer), "-t", "svg", str(stem.with_suffix(".rm")),
         "-o", str(stem.with_suffix(".svg"))],
        check=True, stderr=warnings,
    )
svg = stem.with_suffix(".svg").read_text()
# The exporter writes byte alpha (0–255); SVG requires a fractional opacity.
svg = re.sub(
    r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)",
    lambda m: f"rgb({m[1]},{m[2]},{m[3]}); stroke-opacity:{int(m[4]) / 255:.6f}",
    svg,
)
stem.with_name(stem.name + "-normalised.svg").write_text(svg)
cairosvg.svg2png(
    bytestring=svg.encode(), write_to=str(stem.with_suffix(".png")),
    scale=2, background_color="white",
)
stem.with_name(stem.name + "-source.json").write_text(json.dumps({
    "archive": str(args.archive.resolve()), "notebook_id": document_id,
    "page_id": page["id"], "page_number": args.page, "source_member": member,
    "page_modified_raw": page.get("modifed"),
    "renderer_warnings": stem.with_suffix(".warnings.log").read_text(),
}, indent=2) + "\n")
print(stem.with_suffix(".png"))
