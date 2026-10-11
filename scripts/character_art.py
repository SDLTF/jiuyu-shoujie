"""Prepare complete, uncropped character illustrations and battle wallpapers."""
from pathlib import Path
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets"

def character_art_entries(row):
    yield "portrait", "人设图-2", row["portrait"]
    yield "battle", "战斗壁纸", row["battle"]
    for art in row.get("battle_variants", []):
        yield "battle", art.get("label", "战斗壁纸"), art

def prepare_character_art():
    manifest_path = ROOT / "content/character-art.json"
    if not manifest_path.exists():
        return {}
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))["characters"]
    by_id = {}
    for row in rows:
        ident = row["id"]
        if ident in by_id:
            raise ValueError(f"Duplicate character artwork: {ident}")
        stems = set()
        for kind, label, art in character_art_entries(row):
            variant = art.get("variant", "")
            if variant and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", variant):
                raise ValueError(f"Invalid artwork variant: {variant}")
            stem = f"{ident}-{variant}" if variant else ident
            source = ROOT / art["original"]
            directory = "character-scenes" if kind == "portrait" else "character-battles"
            if (directory, stem) in stems:
                raise ValueError(f"Duplicate artwork variant: {ident}, {stem}")
            stems.add((directory, stem))
            target_dir = OUT / directory
            target_dir.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as picture:
                if picture.size != (art["width"], art["height"]):
                    raise ValueError(f"Incorrect artwork dimensions: {source}")
                if kind == "battle" and (picture.width <= picture.height or abs(picture.width / picture.height - 16 / 9) > .04):
                    raise ValueError(f"Battle artwork must be landscape 16:9: {source}")
                for suffix, width, quality in (("", None, 92), ("-960", 960, 88), ("-480", 480, 86)):
                    target = target_dir / f"{stem}{suffix}.webp"
                    if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                        image = picture.convert("RGB")
                        if width and image.width > width:
                            image.thumbnail((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
                        image.save(target, "WEBP", quality=quality, method=6)
            art["web_directory"] = directory
            art["web_stem"] = stem
        by_id[ident] = row
    return by_id
