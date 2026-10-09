"""Prepare responsive scenery and self-hosted, content-subset web fonts."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/assets'

def prepare_design_assets():
    background_dir = OUT / 'backgrounds'
    background_dir.mkdir(parents=True, exist_ok=True)
    for name in ('greybridge-dusk', 'moonlit-archive'):
        source = ROOT / f'assets/backgrounds/{name}.png'
        for suffix, width in (('', 1920), ('-mobile', 960)):
            target = background_dir / f'{name}{suffix}.webp'
            if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                with Image.open(source) as image:
                    image = image.convert('RGB')
                    image.thumbnail((width, width), Image.Resampling.LANCZOS)
                    image.save(target, 'WEBP', quality=85, method=6)

    # Keep native PNG artwork; deliver lighter desktop and portrait mobile versions.
    manifest_path = ROOT / 'assets/character-backgrounds/generation-prompts.json'
    if manifest_path.exists():
        art_dir = OUT / 'character-backgrounds'
        art_dir.mkdir(parents=True, exist_ok=True)
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for art in manifest['images']:
            source = ROOT / art['original']
            for suffix in ('', '-mobile'):
                target = art_dir / f'{art["id"]}{suffix}.webp'
                if not target.exists() or source.stat().st_mtime > target.stat().st_mtime or manifest_path.stat().st_mtime > target.stat().st_mtime:
                    with Image.open(source) as picture:
                        image = picture.convert('RGB')
                        if suffix:
                            crop_width = min(image.width, round(image.height * 3 / 4))
                            center = image.width * art.get('focus_x', 68) / 100
                            left = max(0, min(image.width - crop_width, round(center - crop_width / 2)))
                            image = image.crop((left, 0, left + crop_width, image.height))
                            image.thumbnail((900, 1200), Image.Resampling.LANCZOS)
                        image.save(target, 'WEBP', quality=90, method=6)

    font_dir = OUT / 'fonts'
    font_dir.mkdir(parents=True, exist_ok=True)
    # Include all source content and UI strings, so future chapters remain covered.
    paths = list((ROOT / 'content').rglob('*.md')) + list((ROOT / 'content').rglob('*.json'))
    paths += [ROOT / 'scripts/build.py', ROOT / 'docs/assets/site.js']
    text = ''.join(path.read_text(encoding='utf-8') for path in paths)
    codepoints = sorted({ord(character) for character in text} | set(range(32, 127)))
    signature = hashlib.sha256(str(codepoints).encode()).hexdigest()
    stamp = font_dir / '.subset-signature'
    if not stamp.exists() or stamp.read_text() != signature:
        for source_name, target_name, family in (
            ('MaShanZheng-Regular.ttf', 'jiuyu-title.woff2', 'Jiuyu Script'),
            ('NotoSansSC-VF.ttf', 'jiuyu-text.woff2', 'Jiuyu Text'),
        ):
            font = TTFont(ROOT / 'assets/fonts' / source_name)
            options = subset.Options()
            options.flavor = 'woff2'
            options.recalc_timestamp = False
            options.name_IDs = ['*']
            options.name_legacy = True
            options.name_languages = ['*']
            subsetter = subset.Subsetter(options=options)
            subsetter.populate(unicodes=codepoints)
            subsetter.subset(font)
            for record in font['name'].names:
                if record.nameID in (1, 4, 6, 16):
                    value = family.replace(' ', '') if record.nameID == 6 else family
                    record.string = value.encode(record.getEncoding())
            font.flavor = 'woff2'
            font.save(font_dir / target_name)
            font.close()
        stamp.write_text(signature)
    for filename in ('MaShanZheng-OFL.txt', 'NotoSansSC-OFL.txt'):
        shutil.copyfile(ROOT / 'assets/fonts' / filename, font_dir / filename)
    faces = []
    for filename, family, weight in (
        ('jiuyu-title.woff2','Jiuyu Script','400'),
        ('jiuyu-text.woff2','Jiuyu Text','100 900'),
    ):
        digest = hashlib.sha256((font_dir / filename).read_bytes()).hexdigest()[:10]
        faces.append(f'@font-face{{font-family:"{family}";src:url("{filename}?v={digest}") format("woff2");font-weight:{weight};font-style:normal;font-display:swap}}')
    (font_dir / 'fonts.css').write_text('\n'.join(faces)+'\n',encoding='utf-8')
    print('Design assets:', ', '.join(f'{path.name} {path.stat().st_size//1024} KB' for path in font_dir.glob('*.woff2')))
