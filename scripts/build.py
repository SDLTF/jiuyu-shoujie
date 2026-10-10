"""Build a complete static website for GitHub Pages from local content."""
from pathlib import Path
import html
import json
import hashlib
import re
import shutil
import markdown
from PIL import Image, ImageOps
from design_assets import prepare_design_assets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
OWNER = "SDLTF"
REPO = "jiuyu-shoujie"
REPO_URL = f"https://github.com/{OWNER}/{REPO}"
RAW_URL = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/"
SITE_URL = "https://sdltf.github.io/jiuyu-shoujie/"

def escape(value):
    return html.escape(str(value), quote=True)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")

def asset_version(name):
    return hashlib.sha256((OUT / "assets" / name).read_bytes()).hexdigest()[:10]

def avatar_url(ident, suffix="", style="original"):
    directory = 'chibi-avatars' if style == 'chibi' else 'avatars'
    name = f'{directory}/{ident}{suffix}.webp'
    return name, asset_version(name)

def avatar_sources(ident, prefix="../", style="original"):
    small, small_version = avatar_url(ident, "-256", style)
    medium, medium_version = avatar_url(ident, "-512", style)
    src = f'{prefix}assets/{medium}?v={medium_version}'
    srcset = f'{prefix}assets/{small}?v={small_version} 256w, {src} 512w'
    return src, srcset

def avatar_switch():
    return '''<div class="avatar-switch" role="group" aria-label="头像风格" hidden><span class="avatar-switch-label">头像风格</span><div class="avatar-switch-options"><button type="button" data-avatar-choice="original" aria-pressed="true">原版</button><button type="button" data-avatar-choice="chibi" aria-pressed="false">Q版</button></div></div>'''

def avatar(person, prefix="../", loading='loading="lazy"', sizes='(max-width: 640px) 40vw, (max-width: 1100px) 25vw, 220px'):
    ident = person["id"]
    original, original_set = avatar_sources(ident, prefix)
    chibi, chibi_set = avatar_sources(ident, prefix, 'chibi')
    return f'<span class="avatar-window" data-avatar-style="original"><img data-avatar data-avatar-name="{escape(person["name"])}" data-original-src="{original}" data-original-srcset="{original_set}" data-chibi-src="{chibi}" data-chibi-srcset="{chibi_set}" src="{original}" srcset="{original_set}" sizes="{sizes}" alt="{escape(person["name"])}头像" width="512" height="512" {loading} decoding="async"></span>'

def image_viewer(title="人物展示卡", navigation=False, original_label="查看原始 PNG"):
    controls = '<div class="viewer-navigation" aria-label="图片切换"><button id="viewer-prev" type="button">← 上一幅</button><span id="viewer-position" aria-live="polite"></span><button id="viewer-next" type="button">下一幅 →</button></div>' if navigation else ''
    return '''<dialog id="image-viewer" aria-labelledby="viewer-name"><div class="viewer-toolbar"><h2 id="viewer-name">VIEWER_TITLE</h2><div><button id="viewer-zoom" type="button" aria-pressed="false">放大细节</button><button id="viewer-close" type="button" aria-label="关闭图片">关闭 <span aria-hidden="true">×</span></button></div></div>VIEWER_NAV<div class="viewer-image-wrap"><img id="viewer-image" alt=""></div><div class="viewer-bottom"><p class="viewer-tip">放大后可滑动查看图片细节</p><a id="viewer-original" target="_blank" rel="noopener">ORIGINAL_LABEL</a></div></dialog>'''.replace('VIEWER_TITLE', escape(title)).replace('VIEWER_NAV', controls).replace('ORIGINAL_LABEL', escape(original_label))

def frame(title, body, prefix="", active="", noindex=False, route="", background=""):
    links = "".join(
        f'<a href="{prefix}{href}"' + (' aria-current="page"' if name == active else '') + f'>{label}</a>'
        for name, href, label in [("gallery", "gallery/", "人物图集"), ("world", "world/", "世界观"), ("chapters", "chapters/", "正文阅读"), ("art", "art/", "印象画廊"), ("fanworks", "fanworks/", "二创")]
    )
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    if not route:
        page_kind = 'home'
    elif route.startswith('gallery/') and route.endswith('.html'):
        page_kind = 'character'
    else:
        page_kind = {'gallery/': 'gallery', 'world/': 'world', 'art/': 'art', 'fanworks/': 'fanworks'}.get(route, 'reader')
    description = '九域守界的粉丝二创：图片与文字作品，收录创作者署名和作品描述。' if active == 'fanworks' else '九域守界的官方故事档案：人物设定图集、小说正文与章节印象图。'
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · 九域守界</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#101b25">{robots}
<link rel="canonical" href="{SITE_URL}{route}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/fonts/fonts.css?v={asset_version('fonts/fonts.css')}">
<link rel="stylesheet" href="{prefix}assets/site.css?v={asset_version('site.css')}">
<script src="{prefix}assets/site.js?v={asset_version('site.js')}" defer></script>
</head><body class="page-{page_kind}"{f' style="--character-background:url({escape(background)})"' if background else ''}>
<a class="skip-link" href="#main">跳到正文</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="{prefix or './'}" aria-label="九域守界首页"><span class="brand-mark" aria-hidden="true">九</span><span>九域守界</span></a>
<nav aria-label="主导航">{links}<a class="repo-link" href="{REPO_URL}" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a></nav>
</div></header>
<main id="main"><div class="page-backdrop" aria-hidden="true"></div>{body}</main>
<footer class="site-footer"><div><a class="footer-title" href="{prefix or './'}">九域守界</a><span>故事与人物档案 · SDLTF</span></div>
<a href="{prefix}world/" class="footer-world-link">世界观与术语 ↗</a></footer>
</body></html>'''

def md_content(text):
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)
    lines = text.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), "")
    if title:
        text = re.sub(r"^# .*?\n", "", text, count=1, flags=re.M)
    parser = markdown.Markdown(extensions=["tables", "fenced_code", "toc"], extension_configs={"toc": {"toc_depth": "2-3"}})
    body = parser.convert(text)
    body = re.sub(r"(<table>.*?</table>)", r'<div class="table-scroll" tabindex="0">\1</div>', body, flags=re.S)
    return title, body, parser.toc

def chapter_art_url(art, suffix=""):
    name = f'chapter-art/{art["id"]}{suffix}.webp'
    return f'../assets/{name}?v={asset_version(name)}'

def chapter_art_original_url(art):
    return f"{RAW_URL}{art['original']}?v={art['sha256'][:10]}"

def chapter_art_figure(art):
    full = chapter_art_url(art)
    medium = chapter_art_url(art, '-960')
    small = chapter_art_url(art, '-480')
    caption = escape(art['caption'])
    original = escape(chapter_art_original_url(art))
    return f'''<figure class="chapter-illustration" id="illustration-{art['id']}"><button type="button" class="image-open chapter-art-open" data-image="{full}" data-name="{caption}" data-kind="章节印象图" data-original="{original}" aria-label="放大{caption}"><img src="{full}" srcset="{small} 480w, {medium} 960w, {full} {art['width']}w" sizes="(max-width: 1000px) 90vw, 900px" alt="{escape(art['alt'])}" width="{art['width']}" height="{art['height']}" loading="lazy" decoding="async"></button><figcaption><span>{caption}</span><span aria-hidden="true">点击放大 ↗</span></figcaption></figure>'''

def illustrated_chapter(text, artwork):
    # Anchors keep artwork beside its scene without modifying the manuscript.
    # A changed or duplicate paragraph must be reviewed before rebuilding.
    text = '\n\n' + text.strip() + '\n\n'
    for art in artwork:
        anchor = '\n\n' + art['after'] + '\n\n'
        if text.count(anchor) != 1:
            raise ValueError(f'Chapter artwork {art["id"]}: expected one matching paragraph')
        text = text.replace(anchor, anchor + chapter_art_figure(art) + '\n\n', 1)
    return md_content(text.strip() + '\n')

def build_art_gallery(chapters, artwork):
    titles = {source.stem: md_content(source.read_text(encoding='utf-8'))[0] for source in chapters}
    artwork = sorted(artwork, key=lambda art: tuple(int(part) for part in art['id'].split('-')))
    illustrated = sorted({art['chapter'] for art in artwork})
    filters = ['<button type="button" class="art-filter" data-chapter="all" aria-pressed="true">全部</button>']
    for chapter in illustrated:
        label = titles[chapter].split(' ', 1)[0]
        count = sum(art['chapter'] == chapter for art in artwork)
        filters.append(f'<button type="button" class="art-filter" data-chapter="{chapter}" aria-pressed="false">{escape(label)}<span>{count}</span></button>')
    cards = []
    for index, art in enumerate(artwork):
        ident, chapter, caption = escape(art['id']), art['chapter'], escape(art['caption'])
        full, medium, small = (chapter_art_url(art, suffix) for suffix in ('', '-960', '-480'))
        loading = 'loading="eager"' if index < 2 else 'loading="lazy"'
        cards.append(f'''<article class="art-card" id="art-{ident}" data-chapter="{chapter}"><button type="button" class="image-open art-image" data-image="{full}" data-name="{ident} · {caption}" data-kind="章节印象图" data-original="{escape(chapter_art_original_url(art))}" aria-label="放大{ident} {caption}"><img src="{medium}" srcset="{small} 480w, {medium} 960w, {full} {art['width']}w" sizes="(max-width: 640px) 90vw, (max-width: 1400px) 44vw, 600px" alt="{escape(art['alt'])}" width="{art['width']}" height="{art['height']}" {loading} decoding="async"><span class="art-image-hint" aria-hidden="true">放大查看 ↗</span></button><div class="art-card-copy"><p class="art-card-chapter">{escape(titles[chapter])}<span>{ident}</span></p><h2>{caption}</h2><a href="../chapters/{chapter}.html#illustration-{ident}" aria-label="阅读{escape(titles[chapter])}中{caption}的场景">阅读这一幕 →</a></div></article>''')
    gallery = f'''<div class="page-shell art-gallery"><div class="page-heading"><p class="eyebrow">SCENES FROM THE STORY / 故事里的场景</p><h1>印象图画廊</h1><p>收藏旅途中的片刻。点击图片看细节，或回到它出现的正文。</p></div><div class="art-gallery-tools"><p class="art-gallery-count" role="status"><strong id="art-count">{len(artwork)}</strong> / {len(artwork)} 幅印象图<span>来自 {len(illustrated)} 个章节</span></p><div class="art-filters" role="group" aria-label="按章节筛选">{''.join(filters)}</div></div><div class="art-grid">{''.join(cards)}</div></div>{image_viewer('章节印象图', navigation=True)}'''
    save(OUT / 'art/index.html', frame('印象图画廊', gallery, '../', 'art', route='art/'))

def load_fanworks():
    works = json.loads((ROOT / 'content/fanworks.json').read_text(encoding='utf-8'))['works']
    if not isinstance(works, list):
        raise ValueError('Fanworks: works must be a list')
    seen = set()
    for work in works:
        ident = work.get('id', '')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError(f'Fanwork: invalid or duplicate id {ident!r}')
        seen.add(ident)
        kind = work.get('type')
        if kind not in ('image', 'text'):
            raise ValueError(f'Fanwork {ident}: type must be image or text')
        for field in ('creator', 'description', kind):
            if not isinstance(work.get(field), str) or not work[field].strip():
                raise ValueError(f'Fanwork {ident}: {field} is required')
        if 'title' in work and not isinstance(work['title'], str):
            raise ValueError(f'Fanwork {ident}: title must be text')
        if kind == 'image':
            source = (ROOT / work['image']).resolve()
            if not source.is_relative_to((ROOT / 'assets/fanworks').resolve()) or not source.is_file():
                raise ValueError(f'Fanwork {ident}: image must exist inside assets/fanworks/')
            if source.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
                raise ValueError(f'Fanwork {ident}: unsupported image format')
    return works

def fanwork_image(work):
    source = ROOT / work['image']
    directory = OUT / 'assets/fanworks'
    directory.mkdir(parents=True, exist_ok=True)
    original_name = f"fanworks/{work['id']}-original{source.suffix.lower()}"
    original = OUT / 'assets' / original_name
    if not original.exists() or original.read_bytes() != source.read_bytes():
        shutil.copyfile(source, original)
    original_url = f'../assets/{original_name}?v={asset_version(original_name)}'
    with Image.open(source) as picture:
        image = ImageOps.exif_transpose(picture).convert('RGBA')
        width, height = image.size
        # Keep animated submissions intact; static images get uncut responsive previews.
        if getattr(picture, 'is_animated', False):
            return original_url, '', width, height, original_url
        variants = []
        for suffix, limit in (('', 2000), ('-960', 960), ('-480', 480)):
            name = f"fanworks/{work['id']}{suffix}.webp"
            target = OUT / 'assets' / name
            if not target.exists() or target.stat().st_mtime < original.stat().st_mtime:
                preview = image.copy()
                preview.thumbnail((limit, limit), Image.Resampling.LANCZOS)
                preview.save(target, 'WEBP', quality=90, method=6)
            with Image.open(target) as preview:
                variants.append((f'../assets/{name}?v={asset_version(name)}', preview.width))
    # Portrait images can share widths; keep the largest matching candidate only.
    by_width = {size: url for url, size in reversed(variants)}
    srcset = ', '.join(f'{url} {size}w' for size, url in sorted(by_width.items()))
    return variants[0][0], srcset, width, height, original_url

def build_fanworks(works):
    labels = {'image': '图片二创', 'text': '文字二创'}
    filters = []
    for kind, label in (('all', '全部作品'), *labels.items()):
        count = len(works) if kind == 'all' else sum(work['type'] == kind for work in works)
        filters.append(f'<button type="button" class="fanwork-filter" data-type="{kind}" aria-pressed="{str(kind == "all").lower()}">{label}<span>{count}</span></button>')
    cards = []
    for index, work in enumerate(works):
        ident, kind = work['id'], work['type']
        creator, description = escape(work['creator']), escape(work['description'])
        title = escape(work.get('title') or f"{work['creator']}的二创")
        if kind == 'image':
            full, srcset, width, height, original = fanwork_image(work)
            responsive = f' srcset="{srcset}" sizes="(max-width: 640px) 90vw, (max-width: 1400px) 44vw, 600px"' if srcset else ''
            content = f'<button type="button" class="image-open fanwork-image" data-image="{full}" data-name="{title}" data-kind="图片二创" data-alt="{description}" data-original="{original}" aria-label="放大{title}"><img src="{full}"{responsive} alt="{description}" width="{width}" height="{height}" loading="lazy" decoding="async"><span class="art-image-hint" aria-hidden="true">放大查看 ↗</span></button>'
        else:
            text = work['text'].replace('\r\n', '\n').replace('\r', '\n')
            body = f'<div class="fanwork-text">{escape(text)}</div>'
            if len(text) > 220:
                content = f'<details class="fanwork-reading"><summary>展开全文 · {len(text)} 字</summary>{body}</details><p class="fanwork-excerpt">{escape(text[:220].rstrip())}…</p>'
            else:
                content = body
            content = f'<div class="fanwork-writing">{content}</div>'
        search = escape(' '.join([work['creator'], work['description'], work.get('title', ''), work.get('text', '')]))
        cards.append(f'<article class="fanwork-card" id="work-{ident}" data-type="{kind}" data-search="{search}"><header class="fanwork-card-heading"><p>{labels[kind]}<a href="#work-{ident}" aria-label="{title}的直接链接">#{index + 1:02}</a></p><h2>{title}</h2><p class="fanwork-creator">创作者 <strong>{creator}</strong></p></header>{content}<div class="fanwork-description"><h3>作品描述</h3><p>{description}</p></div></article>')
    empty = '''<section class="fanworks-empty" aria-labelledby="fanworks-empty-title"><span class="empty-symbol" aria-hidden="true">创</span><p class="eyebrow">等待第一份来自你的创作</p><h2 id="fanworks-empty-title">这里，为新的故事留一盏灯</h2><p>目前还没有收录二创作品。<br>一幅画、一段文字，都可以让九域的故事继续生长。</p></section>''' if not works else ''
    viewer = image_viewer('图片二创', navigation=True, original_label='查看原图') if any(work['type'] == 'image' for work in works) else ''
    body = f'''<div class="page-shell fanworks-shell"><div class="page-heading"><p class="eyebrow">FAN CREATIONS / 来自读者的创作</p><h1>二创</h1><p>把你眼中的九域，留在这里。收藏读者笔下的图画与文字，也记住每一位创作者。</p></div>
<p class="fanworks-note">图片与文字作品由站主收集后更新。投稿时，请附上创作者署名与作品描述。</p>
<div class="fanworks-tools"><div class="fanwork-filters" role="group" aria-label="按二创类型筛选">{''.join(filters)}</div><label class="search-field"><span aria-hidden="true">⌕</span><input id="fanwork-search" type="search" placeholder="搜索创作者或作品" aria-label="搜索二创的创作者、描述或文字" autocomplete="off"></label></div><p class="fanworks-count" role="status">显示 <strong id="fanwork-count">{len(works)}</strong> / {len(works)} 件作品</p>
{empty}<div class="fanworks-grid">{''.join(cards)}</div><p id="fanwork-no-results" class="empty-results" hidden>没有找到匹配的作品，试试其他分类或关键词。</p></div>{viewer}'''
    save(OUT / 'fanworks/index.html', frame('二创', body, '../', 'fanworks', route='fanworks/'))

def build():
    fanworks = load_fanworks()
    prepare_design_assets()
    characters = json.loads((ROOT / "content/characters.json").read_text(encoding="utf-8"))
    image_dir = OUT / "assets/images"
    image_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_dir = OUT / "assets/thumbs"
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    for person in characters:
        source = ROOT / person["original"]
        target = image_dir / f'{person["id"]}.webp'
        if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
            with Image.open(source) as picture:
                picture.convert("RGB").save(target, "WEBP", quality=92, method=6)
        thumbnail = thumbnail_dir / f'{person["id"]}.webp'
        if not thumbnail.exists() or thumbnail.stat().st_mtime < source.stat().st_mtime:
            with Image.open(source) as picture:
                preview = picture.convert("RGB")
                preview.thumbnail((960, 480), Image.Resampling.LANCZOS)
                preview.save(thumbnail, "WEBP", quality=82, method=6)

    featured = [characters[0], characters[9], characters[5]]
    featured_ids = {person['id'] for person in featured}
    ordered = featured + [person for person in characters if person['id'] not in featured_ids]
    slides = []
    for index in range(0, len(ordered), 3):
        figures = []
        group = ordered[index:index + 3]
        # Keep the three-panel composition when a new character leaves a partial group.
        if len(group) < 3:
            group = group + ordered[:3 - len(group)]
        for slot, person in enumerate(group):
            loading = 'fetchpriority="high"' if index == 0 and slot == 0 else 'loading="lazy"'
            framing = person['hero_framing']
            # At the narrowest viewport, cap scaling so the entire head has 10% breathing room.
            face_scale = round(887 / framing['head_width'] * .9, 4)
            style = f'--hero-focus-x:{framing["x"]}%;--hero-face-scale:{face_scale};--hero-portrait-src:url(assets/images/{person["id"]}.webp)'
            figures.append(f'<figure class="portrait portrait-{["one", "two", "three"][slot]}" style="{style}"><a href="gallery/{person["id"]}.html" aria-label="查看{escape(person["name"])}人物资料"><img src="assets/images/{person["id"]}.webp" alt="{escape(person["name"])}的人物设定" {loading}></a><figcaption><span>{person["id"]}</span>{escape(person["name"])}</figcaption></figure>')
        hidden = ' hidden' if index else ''
        slides.append(f'<div class="hero-slide" role="group" aria-roledescription="幻灯片" aria-label="第{index//3+1}组，共{(len(ordered)+2)//3}组"{hidden}>{"".join(figures)}</div>')
    carousel = f'''<div class="hero-art" id="hero-carousel" role="region" aria-roledescription="轮播" aria-label="人物设定预览"><div class="hero-slides">{''.join(slides)}</div><div class="carousel-controls"><span class="art-caption">人物档案 / CHARACTER ARCHIVE</span><div class="carousel-buttons"><button id="carousel-prev" type="button" aria-label="上一组人物" aria-controls="hero-carousel">←</button><span id="carousel-status" aria-live="polite" aria-atomic="true">01 / {(len(ordered)+2)//3:02}</span><button id="carousel-next" type="button" aria-label="下一组人物" aria-controls="hero-carousel">→</button></div></div></div>'''
    home = '''<div class="home-shell">
<section class="hero" aria-labelledby="hero-title">
<div class="hero-copy"><p class="eyebrow">九域守界 · 故事档案</p><h1 id="hero-title">九域<span>守界</span></h1>
<p class="hero-intro">从灰桥的一次救援出发，<br>走入九域交错的世界。</p>
<p class="hero-note">在这里认识同行者，翻阅他们的设定，等待故事展开。</p>
<div class="hero-actions"><a class="button primary" href="gallery/">翻阅人物图集</a><a class="button secondary" href="chapters/">正文阅读</a><a class="button secondary" href="art/">印象画廊</a></div>
<p class="hero-meta"><span class="line" aria-hidden="true"></span>CHARACTER_COUNT 位角色 · 人物设定图集已收录</p></div>
<!-- CHARACTER_CAROUSEL -->
</section>
<a class="world-entry" href="world/"><span class="eyebrow">WORLD & LEXICON / 世界观与术语</span><span class="world-entry-title">九域之间</span><span class="world-entry-copy">从地脉到梦路，认识这个世界里的名字与规则。</span><span class="world-entry-action">打开世界档案 ↗</span></a>
<section class="entry-grid" aria-label="阅读入口">
<a class="entry" href="gallery/"><div class="entry-top"><span class="eyebrow">01 / 人物</span><span class="entry-status">CHARACTER_COUNT 份设定</span></div><h2>人物设定图集</h2><p>从头像认识角色，翻阅展示卡与个人资料。</p><span class="entry-action">打开图集 <span aria-hidden="true">↗</span></span></a>
<a class="entry" href="chapters/"><div class="entry-top"><span class="eyebrow">02 / 故事</span><span class="entry-status">正文尚未发布</span></div><h2>小说正文</h2><p>章节发布后，将在这里按顺序收录。</p><span class="entry-action">前往阅读目录 <span aria-hidden="true">↗</span></span></a>
</section></div>'''
    home = home.replace('</section></div>', '''</section><a class="fanworks-entry" href="fanworks/"><span class="eyebrow">FAN CREATIONS / 读者二创</span><span class="fanworks-entry-title">你眼中的九域</span><span class="fanworks-entry-copy">收藏读者的图画与文字，让每一份热爱都有署名。</span><span class="fanworks-entry-action">浏览二创 →</span></a></div>''')
    home = home.replace('<!-- CHARACTER_CAROUSEL -->', carousel)
    home = home.replace("CHARACTER_COUNT", str(len(characters)))
    chapters = sorted((ROOT / "content/chapters").glob("*.md"))
    if chapters:
        home = home.replace("正文尚未发布", f"已收录 {len(chapters)} 章").replace("章节发布后，将在这里按顺序收录。", "按章节顺序，继续九域守界的故事。")
    save(OUT / "index.html", frame("故事与人物档案", home))

    build_world(characters)
    build_fanworks(fanworks)

    cards = []
    for i, person in enumerate(characters):
        name, real, ident = escape(person["name"]), escape(person.get("real", "")), person["id"]
        loading = 'fetchpriority="high"' if i < 4 else 'loading="lazy"'
        cards.append(f'''<article class="character-card character-tile" data-search="{name} {real}"><a class="tile-link" href="{ident}.html" aria-label="查看{name}的展示卡和个人资料"><span class="tile-number">{ident}</span>{avatar(person, loading=loading)}<h2>{name}</h2><span class="tile-caption">查看人物资料</span></a></article>''')
    gallery = f'''<div class="page-shell gallery-shell"><a class="gallery-world-link" href="../world/">← 返回世界观</a><div class="page-heading"><p class="eyebrow">CHARACTER ARCHIVE / 人物档案</p><h1>人物设定图集</h1><p>从头像认识同行者，进入档案查看展示卡、专属背景与个人资料。</p></div>
<div class="gallery-tools"><label class="search-field"><span aria-hidden="true">⌕</span><input id="character-search" type="search" placeholder="搜索角色名或原名" aria-label="搜索角色名或原名" autocomplete="off"></label>{avatar_switch()}<span class="gallery-count" aria-live="polite"><strong id="character-count">{len(characters)}</strong> / {len(characters)} 位角色</span></div>
<div class="avatar-grid">{''.join(cards)}</div><p id="no-results" class="empty-results" hidden>没有找到对应角色，换个名字试试。</p></div>'''
    save(OUT / "gallery/index.html", frame("人物设定图集", gallery, "../", "gallery", route="gallery/"))

    for index, person in enumerate(characters):
        ident, name = person["id"], escape(person["name"])
        profile = person["profile"]
        image = f"../assets/images/{ident}.webp"
        raw = escape(RAW_URL + person["original"])
        art_name = f'character-backgrounds/{ident}.webp'
        art = f'../assets/{art_name}?v={asset_version(art_name)}'
        art_mobile_name = f'character-backgrounds/{ident}-mobile.webp'
        art_mobile = f'../assets/{art_mobile_name}?v={asset_version(art_mobile_name)}'
        art_raw = escape(RAW_URL + f'assets/character-backgrounds/{ident}.png')
        avatar_name, avatar_version = avatar_url(ident)
        avatar_full = f'../assets/{avatar_name}?v={avatar_version}'
        avatar_raw = escape(RAW_URL + person['avatar']['original'])
        chibi_name, chibi_version = avatar_url(ident, style='chibi')
        chibi_full = f'../assets/{chibi_name}?v={chibi_version}'
        chibi_raw = escape(RAW_URL + person['avatar']['chibi'])

        with Image.open(ROOT / f'assets/character-backgrounds/{ident}.png') as picture:
            art_width, art_height = picture.size
        basic = ''.join(f'<span>{escape(part.strip())}</span>' for part in profile['basic'].split('｜'))
        sections = []
        for section in profile['sections']:
            text = ''.join(f'<p>{escape(line)}</p>' for line in section['lines'])
            if section['title'] == '隐秘':
                sections.append(f'<details class="profile-secret"><summary>隐秘设定 <span>含剧透</span></summary><div>{text}</div></details>')
            else:
                sections.append(f'<section class="profile-section"><h3>{escape(section["title"])}</h3>{text}</section>')
        quote = f'<blockquote class="profile-quote">{escape(profile["quote"])}</blockquote>' if profile['quote'] else ''
        previous, following = characters[(index - 1) % len(characters)], characters[(index + 1) % len(characters)]
        body = f'''<section class="character-scene" aria-label="{name}专属场景"><picture class="character-scene-art"><source media="(max-width: 640px)" srcset="{art_mobile}"><img src="{art}" alt="{name}专属场景插画" width="{art_width}" height="{art_height}" fetchpriority="high"></picture><div class="scene-shade" aria-hidden="true"></div><div class="page-shell scene-content"><nav class="breadcrumbs" aria-label="位置"><a href="./">人物图集</a><span aria-hidden="true">/</span><span>{name}</span></nav>
<header class="profile-heading"><div class="profile-avatar">{avatar(person, loading='fetchpriority="high"', sizes='94px')}</div><div class="profile-heading-copy"><p class="eyebrow">九域守界 / 人物档案 {ident}</p><h1>{name}</h1><p class="profile-name-line">{escape(profile['name_line'])}</p><div class="profile-basic">{basic}</div></div></header>{avatar_switch()}{quote}
<div class="scene-actions"><div class="scene-action-group"><button type="button" class="button secondary image-open" data-image="{art}" data-name="{name} · 专属场景" data-kind="专属场景插画" data-original="{art_raw}">查看专属大图 ↗</button><a href="{art_raw}" target="_blank" rel="noopener" class="scene-original">背景原图</a></div><div class="scene-action-group"><button type="button" class="button secondary image-open avatar-open" data-avatar-viewer data-avatar-name="{name}" data-original-image="{avatar_full}" data-chibi-image="{chibi_full}" data-original-source="{avatar_raw}" data-chibi-source="{chibi_raw}" data-image="{avatar_full}" data-name="{name} · 人物头像" data-kind="人物头像" data-original="{avatar_raw}">查看人物头像 ↗</button><a data-avatar-download data-original-source="{avatar_raw}" data-chibi-source="{chibi_raw}" href="{avatar_raw}" target="_blank" rel="noopener" class="scene-original">头像原图</a></div></div></div></section><div class="page-shell character-profile">
<div class="profile-layout"><section class="dossier-section" aria-labelledby="dossier-title"><h2 id="dossier-title">人物展示卡</h2><button type="button" class="image-open dossier-image" data-image="{image}" data-name="{name}" data-original="{raw}" aria-label="放大{name}人物展示卡"><img src="{image}" alt="{name}完整人物展示卡" width="1774" height="887"><span class="image-hint">点击放大</span></button><div class="dossier-actions"><a class="button secondary" href="{image}" target="_blank" rel="noopener">打开完整图片</a><a class="button secondary" href="{raw}" target="_blank" rel="noopener">查看原始 PNG</a></div></section><section class="profile-info" aria-labelledby="profile-info-title"><h2 id="profile-info-title">个人资料</h2>{''.join(sections)}</section></div>
<nav class="profile-pagination" aria-label="人物导航"><a href="{previous['id']}.html"><span>上一位</span>{escape(previous['name'])}</a><a class="back-to-gallery" href="./">全部人物</a><a href="{following['id']}.html"><span>下一位</span>{escape(following['name'])}</a></nav></div>{image_viewer('人物档案', navigation=True)}'''
        save(OUT / f'gallery/{ident}.html', frame(f'{person["name"]} · 人物资料', body, '../', 'gallery', route=f'gallery/{ident}.html', background=art))

    outline_title, outline_body, toc = md_content((ROOT / "content/outline.md").read_text(encoding="utf-8"))
    outline = f'''<div class="page-shell"><div class="page-heading"><p class="eyebrow">AUTHOR'S NOTES / 创作资料</p><h1>故事大纲</h1><p>此页包含完整剧情走向、人物选择与结局。</p></div>
<div id="outline-content"><div class="reading-layout"><aside class="reading-toc"><p class="eyebrow">大纲目录</p>{toc}</aside><div class="reading-column"><details class="mobile-toc"><summary>展开大纲目录</summary>{toc}</details><article class="prose">{outline_body}</article><div class="reading-end">创作大纲 · 九域守界 <a href="{REPO_URL}/blob/main/content/outline.md" target="_blank" rel="noopener">查看 Markdown 源文件</a></div></div></div></div></div>'''
    save(OUT / "outline/index.html", frame("故事大纲（含剧透）", outline, "../", noindex=True, route="outline/"))

    chapter_art_path = ROOT / 'content/chapter-art.json'
    chapter_art = json.loads(chapter_art_path.read_text(encoding='utf-8'))['images'] if chapter_art_path.exists() else []
    build_art_gallery(chapters, chapter_art)
    chapter_entries = []
    for i, source in enumerate(chapters):
        artwork = [art for art in chapter_art if art['chapter'] == source.stem]
        title, body, toc = illustrated_chapter(source.read_text(encoding="utf-8"), artwork)
        title = title or source.stem
        thumbnail = f'<img class="chapter-thumbnail" src="{chapter_art_url(artwork[0], "-480")}" alt="{escape(title)}印象图" width="{artwork[0]["width"]}" height="{artwork[0]["height"]}" loading="lazy">' if artwork else ''
        chapter_entries.append(f'<a class="chapter-item{" has-art" if artwork else ""}" href="{escape(source.stem)}.html"><span>{i+1:02}</span>{thumbnail}<h2>{escape(title)}</h2><span aria-hidden="true">↗</span></a>')
        previous = f'<a href="{escape(chapters[i-1].stem)}.html">上一章</a>' if i else '<span></span>'
        following = f'<a href="{escape(chapters[i+1].stem)}.html">下一章</a>' if i + 1 < len(chapters) else '<span></span>'
        art_link = f'<a class="chapter-gallery-link" href="../art/?chapter={source.stem}">浏览本章印象图 →</a>' if artwork else ''
        chapter = f'<div class="page-shell chapter-reading"><p class="eyebrow">九域守界 / 正文</p><h1>{escape(title)}</h1><article class="prose">{body}</article><nav class="chapter-pagination" aria-label="章节导航">{previous}<a href="./">章节目录</a>{following}</nav>{art_link}</div>' + (image_viewer("章节印象图") if artwork else '')
        save(OUT / f"chapters/{source.stem}.html", frame(title, chapter, "../", "chapters", route=f"chapters/{source.stem}.html"))
    chapter_body = '<div class="chapter-list">' + ''.join(chapter_entries) + '</div>' if chapters else '''<section class="chapters-empty"><span class="empty-symbol" aria-hidden="true">卷</span><p class="eyebrow">故事正在准备中</p><h2>正文尚未发布</h2><p>章节发布后，这里会按顺序收录。<br>现在可以先认识故事中的人物。</p><a class="button primary" href="../gallery/">翻阅人物图集</a></section>'''
    chapter_index = f'<div class="page-shell"><div class="page-heading"><p class="eyebrow">THE STORY / 正文阅读</p><h1>小说正文</h1><p>九域守界的故事，从这里展开。</p></div><a class="chapter-gallery-link chapter-gallery-directory" href="../art/">浏览全部 {len(chapter_art)} 幅印象图 →</a>{chapter_body}</div>'
    save(OUT / "chapters/index.html", frame("正文阅读", chapter_index, "../", "chapters", route="chapters/"))
    save(OUT / "404.html", frame("页面未找到", '<div class="page-shell error-page"><p class="eyebrow">404</p><h1>这页档案还未收录</h1><p>可以回到首页，继续翻阅故事与人物。</p><a class="button primary" href="/jiuyu-shoujie/">返回首页</a></div>', "/jiuyu-shoujie/", noindex=True))
    save(OUT / ".nojekyll", "")
    save(OUT / "robots.txt", "User-agent: *\nAllow: /\nDisallow: /jiuyu-shoujie/outline/\n")
    print(f"Built {len(characters)} character cards, complete outline, {len(chapters)} published chapters.")

def build_world(characters):
    world = json.loads((ROOT / 'content/world.json').read_text(encoding='utf-8'))
    people = {person['id']: person['name'] for person in characters}
    terms = {term['id']: term for term in world['terms']}
    categories = {category['id']: category['name'] for category in world['categories']}
    def term_link(ident):
        term = terms[ident]
        marker = ' <span class="link-spoiler">剧透</span>' if term['spoiler'] else ''
        return f'<a href="#term-{ident}" class="term-link" data-term-link="{ident}">{escape(term["name"])}{marker}</a>'
    overview = ''.join(f'<article class="world-overview-card"><span class="overview-number">0{index+1}</span><h2>{escape(item["title"])}</h2><p>{escape(item["text"])}</p><div class="related-terms">{"".join(term_link(ident) for ident in item["links"])}</div></article>' for index, item in enumerate(world['overview']))
    entries = []
    for term in world['terms']:
        searchable = ' '.join([term['name'], *term['aliases'], term['summary'], *term['detail']])
        related = f'<div class="term-related"><span>相关词条</span><div class="related-terms">{"".join(term_link(ident) for ident in term["related"])}</div></div>' if term['related'] else ''
        characters_html = f'<div class="term-people"><span>相关人物</span>{"".join(f"<a href=\"../gallery/{ident}.html\">{escape(people[ident])} ↗</a>" for ident in term["people"])}</div>' if term['people'] else ''
        aliases = f'<p class="term-aliases">亦作：{escape("、".join(term["aliases"]))}</p>' if term['aliases'] else ''
        content = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in term['detail'])
        entry = f'''<article id="term-{term['id']}" class="wiki-term" data-category="{term['category']}" data-spoiler="{str(term['spoiler']).lower()}" data-search="{escape(searchable)}" tabindex="-1"><div class="term-title-row"><span class="term-category">{escape(categories[term['category']])}</span><a class="term-permalink" href="#term-{term['id']}" aria-label="{escape(term['name'])}的直接链接">#</a></div><h3>{escape(term['name'])}</h3>{aliases}<p class="term-summary">{escape(term['summary'])}</p><div class="term-description">{content}</div>{related}{characters_html}<p class="term-source">资料依据：{escape(term['source'])}</p></article>'''
        entries.append((term['spoiler'], entry))
    basic = ''.join(entry for spoiler, entry in entries if not spoiler)
    advanced = ''.join(entry for spoiler, entry in entries if spoiler)
    filters = '<button type="button" data-wiki-category="all" aria-pressed="true">全部词条</button>' + ''.join(f'<button type="button" data-wiki-category="{ident}" aria-pressed="false">{escape(name)}</button>' for ident, name in categories.items())
    basic_count = sum(not term['spoiler'] for term in world['terms'])
    body = f'''<div class="page-shell world-shell"><div class="page-heading world-heading"><p class="eyebrow">WORLD & LEXICON / 世界档案</p><h1>{escape(world['title'])}</h1><p>{escape(world['intro'])}</p><div class="world-jump-links"><a href="#world-overview">世界速览 ↓</a><a href="#wiki">术语索引 ↓</a></div></div>
<section id="world-overview" class="world-overview" aria-label="世界速览">{overview}</section>
<section id="wiki" class="wiki-section" aria-labelledby="wiki-title"><div class="wiki-section-heading"><div><p class="eyebrow">THE LEXICON / 术语索引</p><h2 id="wiki-title">把每一个名字说清楚</h2></div><p><strong>{len(terms)}</strong> 条档案 · 默认浏览基础设定</p></div><p class="wiki-editorial">{escape(world['editorial_note'])}</p>
<div class="wiki-tools"><label class="search-field"><span aria-hidden="true">⌕</span><input id="wiki-search" type="search" placeholder="搜索术语、别名或解释" aria-label="搜索世界观术语" autocomplete="off"></label><span id="wiki-count" class="wiki-count" aria-live="polite">{basic_count} 条基础词条</span><button id="wiki-clear" class="wiki-clear" type="button" hidden>清除筛选</button></div><div class="wiki-filters" role="group" aria-label="词条分类">{filters}</div>
<div id="wiki-basic" class="wiki-grid">{basic}</div><p id="wiki-no-results" class="empty-results" hidden>没有匹配的词条，试试别名或清除分类筛选。</p>
<section id="wiki-spoiler-notice" class="wiki-spoiler-notice" aria-labelledby="wiki-spoiler-title"><span class="warning-label">进阶档案 · 含剧透</span><h2 id="wiki-spoiler-title">翻到故事更深处</h2><p>另有 {len(terms)-basic_count} 条词条涉及后续机制、人物秘密与结局。主动展开后，它们才会进入列表和搜索结果。</p><button id="wiki-reveal" class="button secondary" type="button" aria-controls="wiki-advanced" aria-expanded="false">我已知晓，展开进阶词条</button></section><div id="wiki-advanced" hidden><div class="advanced-heading"><h2>进阶档案</h2><span class="warning-label">含剧透</span><button id="wiki-hide" type="button" class="wiki-clear">收起进阶词条</button></div><div class="wiki-grid">{advanced}</div></div>
</section><a class="world-back" href="#wiki">返回术语索引 ↑</a></div>'''
    save(OUT / 'world/index.html', frame('世界观与术语', body, '../', 'world', route='world/'))

if __name__ == "__main__":
    build()
