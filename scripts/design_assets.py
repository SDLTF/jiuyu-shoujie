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

def chibi_preview(picture):
    """Remove empty quadrant padding while retaining the whole pose and true alpha."""
    image = picture.convert('RGBA')
    bounds = image.getchannel('A').point(lambda a: 255 if a > 24 else 0).getbbox()
    if not bounds:
        raise ValueError('Empty chibi pose')
    left, top, right, bottom = bounds
    side = max(right-left, bottom-top) + 32
    x = (left+right-side)//2
    y = (top+bottom-side)//2
    return image.crop((x,y,x+side,y+side))

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

    # Keep both avatar styles; preserve the transparent chibi PNG backgrounds.
    for directory in ('avatars', 'chibi-avatars'):
        avatar_manifest = ROOT / f'assets/{directory}/generation-prompts.json'
        if not avatar_manifest.exists():
            continue
        avatar_dir = OUT / directory
        avatar_dir.mkdir(parents=True, exist_ok=True)
        for art in json.loads(avatar_manifest.read_text(encoding='utf-8'))['images']:
            source = ROOT / art['original']
            for suffix, width, quality in (('', 1024, 92), ('-512', 512, 90), ('-256', 256, 87)):
                target = avatar_dir / f'{art["id"]}{suffix}.webp'
                if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                    with Image.open(source) as picture:
                        if picture.width != picture.height:
                            raise ValueError(f'Avatar must be square: {source}')
                        image = chibi_preview(picture) if directory == 'chibi-avatars' else picture.convert('RGB')
                        image.thumbnail((width, width), Image.Resampling.LANCZOS)
                        image.save(target, 'WEBP', quality=quality, method=6)

    sticker_manifest = ROOT / 'content/chibi-stickers.json'
    if sticker_manifest.exists():
        for person in json.loads(sticker_manifest.read_text(encoding='utf-8'))['characters']:
            ident = f'{person["id"]:02}'
            directory = OUT / 'chibi-stickers' / ident
            directory.mkdir(parents=True, exist_ok=True)
            for pose in person['images']:
                source = ROOT / pose['file']
                native = directory / f'{pose["index"]:02}.png'
                if not native.exists() or native.read_bytes() != source.read_bytes():
                    shutil.copyfile(source,native)
                for suffix, width, quality in (('', 627, 92), ('-256', 256, 87)):
                    target = directory / f'{pose["index"]:02}{suffix}.webp'
                    if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                        with Image.open(source) as picture:
                            image = chibi_preview(picture)
                            image.thumbnail((width,width), Image.Resampling.LANCZOS)
                            image.save(target,'WEBP',quality=quality,method=4)

    # Preserve complete chapter compositions, including on small screens.
    chapter_manifest = ROOT / 'content/chapter-art.json'
    if chapter_manifest.exists():
        art_dir = OUT / 'chapter-art'
        art_dir.mkdir(parents=True, exist_ok=True)
        for art in json.loads(chapter_manifest.read_text(encoding='utf-8'))['images']:
            source = ROOT / art['original']
            for suffix, width, quality in (('', 1920, 90), ('-960', 960, 88), ('-480', 480, 85)):
                target = art_dir / f'{art["id"]}{suffix}.webp'
                if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
                    with Image.open(source) as picture:
                        image = picture.convert('RGB')
                        image.thumbnail((width, width), Image.Resampling.LANCZOS)
                        image.save(target, 'WEBP', quality=quality, method=6)

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
