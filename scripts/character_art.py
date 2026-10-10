"""Prepare complete, uncropped character illustrations and battle wallpapers."""
from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets"

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
        for kind in ("portrait", "battle"):
            art = row[kind]
            source = ROOT / art["original"]
            directory = "character-scenes" if kind == "portrait" else "character-battles"
            target_dir = OUT / directory
            target_dir.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as picture:
                if picture.size != (art["width"], art["height"]):
                    raise ValueError(f"Incorrect artwork dimensions: {source}")
                if kind == "battle" and (picture.width <= picture.height or abs(picture.width / picture.height - 16 / 9) > .04):
                    raise ValueError(f"Battle artwork must be landscape 16:9: {source}")
                for suffix, width, quality in (("", None, 92), ("-960", 960, 88), ("-480", 480, 86)):
                    target = target_dir / f"{ident}{suffix}.webp"
                    if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                        image = picture.convert("RGB")
                        if width and image.width > width:
                            image.thumbnail((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
                        image.save(target, "WEBP", quality=quality, method=6)
            art["web_directory"] = directory
        by_id[ident] = row
    return by_id
