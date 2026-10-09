"""Build a complete static website for GitHub Pages from local content."""
from pathlib import Path
import html
import json
import hashlib
import re
import markdown
from PIL import Image
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

def avatar(person, prefix="../", loading='loading="lazy"'):
    crop = person.get("avatar", {"width": 315, "left": -108, "top": 0})
    style = f'--portrait-width:{crop["width"]}%;--portrait-left:{crop["left"]}%;--portrait-top:{crop["top"]}%'
    return f'<span class="avatar-window" style="{style}"><img src="{prefix}assets/thumbs/{person["id"]}.webp" alt="{escape(person["name"])}头像" width="960" height="480" {loading}></span>'

def image_viewer():
    return '''<dialog id="image-viewer" aria-labelledby="viewer-name"><div class="viewer-toolbar"><h2 id="viewer-name">人物展示卡</h2><div><button id="viewer-zoom" type="button" aria-pressed="false">放大细节</button><button id="viewer-close" type="button" aria-label="关闭图片">关闭 <span aria-hidden="true">×</span></button></div></div><div class="viewer-image-wrap"><img id="viewer-image" alt=""></div><div class="viewer-bottom"><p class="viewer-tip">放大后可滑动查看图片细节</p><a id="viewer-original" target="_blank" rel="noopener">查看原始 PNG</a></div></dialog>'''

def frame(title, body, prefix="", active="", noindex=False, route=""):
    links = "".join(
        f'<a href="{prefix}{href}"' + (' aria-current="page"' if name == active else '') + f'>{label}</a>'
        for name, href, label in [("gallery", "gallery/", "人物图集"), ("world", "world/", "世界观"), ("chapters", "chapters/", "正文阅读")]
    )
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    page_kind = 'home' if not route else ('character' if route.startswith('gallery/') and route.endswith('.html') else ('gallery' if route == 'gallery/' else ('world' if route == 'world/' else 'reader')))
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · 九域守界</title>
<meta name="description" content="九域守界的官方故事档案：人物设定图集与小说正文。">
<meta name="theme-color" content="#101b25">{robots}
<link rel="canonical" href="{SITE_URL}{route}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/fonts/fonts.css?v={asset_version('fonts/fonts.css')}">
<link rel="stylesheet" href="{prefix}assets/site.css?v={asset_version('site.css')}">
<script src="{prefix}assets/site.js?v={asset_version('site.js')}" defer></script>
</head><body class="page-{page_kind}">
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

def build():
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
        for slot, person in enumerate(ordered[index:index + 3]):
            loading = 'fetchpriority="high"' if index == 0 and slot == 0 else 'loading="lazy"'
            figures.append(f'<figure class="portrait portrait-{["one", "two", "three"][slot]}"><a href="gallery/{person["id"]}.html" aria-label="查看{escape(person["name"])}人物资料"><img src="assets/images/{person["id"]}.webp" alt="{escape(person["name"])}的人物设定" {loading}></a><figcaption><span>{person["id"]}</span>{escape(person["name"])}</figcaption></figure>')
        hidden = ' hidden' if index else ''
        slides.append(f'<div class="hero-slide" role="group" aria-roledescription="幻灯片" aria-label="第{index//3+1}组，共{(len(ordered)+2)//3}组"{hidden}>{"".join(figures)}</div>')
    carousel = f'''<div class="hero-art" id="hero-carousel" role="region" aria-roledescription="轮播" aria-label="人物设定预览"><div class="hero-slides">{''.join(slides)}</div><div class="carousel-controls"><span class="art-caption">人物档案 / CHARACTER ARCHIVE</span><div class="carousel-buttons"><button id="carousel-prev" type="button" aria-label="上一组人物" aria-controls="hero-carousel">←</button><span id="carousel-status" aria-live="polite" aria-atomic="true">01 / {(len(ordered)+2)//3:02}</span><button id="carousel-next" type="button" aria-label="下一组人物" aria-controls="hero-carousel">→</button></div></div></div>'''
    home = '''<div class="home-shell">
<section class="hero" aria-labelledby="hero-title">
<div class="hero-copy"><p class="eyebrow">九域守界 · 故事档案</p><h1 id="hero-title">九域<span>守界</span></h1>
<p class="hero-intro">从灰桥的一次救援出发，<br>走入九域交错的世界。</p>
<p class="hero-note">在这里认识同行者，翻阅他们的设定，等待故事展开。</p>
<div class="hero-actions"><a class="button primary" href="gallery/">翻阅人物图集</a><a class="button secondary" href="chapters/">正文阅读</a></div>
<p class="hero-meta"><span class="line" aria-hidden="true"></span>27 位角色 · 人物设定图集已收录</p></div>
<!-- CHARACTER_CAROUSEL -->
</section>
<a class="world-entry" href="world/"><span class="eyebrow">WORLD & LEXICON / 世界观与术语</span><span class="world-entry-title">九域之间</span><span class="world-entry-copy">从地脉到梦路，认识这个世界里的名字与规则。</span><span class="world-entry-action">打开世界档案 ↗</span></a>
<section class="entry-grid" aria-label="阅读入口">
<a class="entry" href="gallery/"><div class="entry-top"><span class="eyebrow">01 / 人物</span><span class="entry-status">27 份设定</span></div><h2>人物设定图集</h2><p>从头像认识角色，翻阅展示卡与个人资料。</p><span class="entry-action">打开图集 <span aria-hidden="true">↗</span></span></a>
<a class="entry" href="chapters/"><div class="entry-top"><span class="eyebrow">02 / 故事</span><span class="entry-status">正文尚未发布</span></div><h2>小说正文</h2><p>章节发布后，将在这里按顺序收录。</p><span class="entry-action">前往阅读目录 <span aria-hidden="true">↗</span></span></a>
</section></div>'''
    home = home.replace('<!-- CHARACTER_CAROUSEL -->', carousel)
    chapters = sorted((ROOT / "content/chapters").glob("*.md"))
    if chapters:
        home = home.replace("正文尚未发布", f"已收录 {len(chapters)} 章").replace("章节发布后，将在这里按顺序收录。", "按章节顺序，继续九域守界的故事。")
    save(OUT / "index.html", frame("故事与人物档案", home))

    build_world(characters)

    cards = []
    for i, person in enumerate(characters):
        name, real, ident = escape(person["name"]), escape(person.get("real", "")), person["id"]
        loading = 'fetchpriority="high"' if i < 4 else 'loading="lazy"'
        cards.append(f'''<article class="character-card character-tile" data-search="{name} {real}"><a class="tile-link" href="{ident}.html" aria-label="查看{name}的展示卡和个人资料"><span class="tile-number">{ident}</span>{avatar(person, loading=loading)}<h2>{name}</h2><span class="tile-caption">查看人物资料</span></a></article>''')
    gallery = f'''<div class="page-shell gallery-shell"><a class="gallery-world-link" href="../world/">← 返回世界观</a><div class="page-heading"><p class="eyebrow">CHARACTER ARCHIVE / 人物档案</p><h1>人物设定图集</h1><p>九域之间的同行者。选择头像，查看人物展示卡与个人资料。</p></div>
<div class="gallery-tools"><label class="search-field"><span aria-hidden="true">⌕</span><input id="character-search" type="search" placeholder="搜索角色名或原名" aria-label="搜索角色名或原名" autocomplete="off"></label><span class="gallery-count" aria-live="polite"><strong id="character-count">{len(characters)}</strong> / {len(characters)} 位角色</span></div>
<div class="avatar-grid">{''.join(cards)}</div><p id="no-results" class="empty-results" hidden>没有找到对应角色，换个名字试试。</p></div>'''
    save(OUT / "gallery/index.html", frame("人物设定图集", gallery, "../", "gallery", route="gallery/"))

    for index, person in enumerate(characters):
        ident, name = person["id"], escape(person["name"])
        profile = person["profile"]
        image = f"../assets/images/{ident}.webp"
        raw = escape(RAW_URL + person["original"])
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
        body = f'''<div class="page-shell character-profile"><nav class="breadcrumbs" aria-label="位置"><a href="./">人物图集</a><span aria-hidden="true">/</span><span>{name}</span></nav>
<header class="profile-heading"><div class="profile-avatar">{avatar(person, loading='fetchpriority="high"')}</div><div class="profile-heading-copy"><p class="eyebrow">九域守界 / 人物档案 {ident}</p><h1>{name}</h1><p class="profile-name-line">{escape(profile['name_line'])}</p><div class="profile-basic">{basic}</div></div></header>{quote}
<div class="profile-layout"><section class="dossier-section" aria-labelledby="dossier-title"><h2 id="dossier-title">人物展示卡</h2><button type="button" class="image-open dossier-image" data-image="{image}" data-name="{name}" data-original="{raw}" aria-label="放大{name}人物展示卡"><img src="{image}" alt="{name}完整人物展示卡" width="1774" height="887"><span class="image-hint">点击放大</span></button><div class="dossier-actions"><a class="button secondary" href="{image}" target="_blank" rel="noopener">打开完整图片</a><a class="button secondary" href="{raw}" target="_blank" rel="noopener">查看原始 PNG</a></div></section><section class="profile-info" aria-labelledby="profile-info-title"><h2 id="profile-info-title">个人资料</h2>{''.join(sections)}</section></div>
<nav class="profile-pagination" aria-label="人物导航"><a href="{previous['id']}.html"><span>上一位</span>{escape(previous['name'])}</a><a class="back-to-gallery" href="./">全部人物</a><a href="{following['id']}.html"><span>下一位</span>{escape(following['name'])}</a></nav></div>{image_viewer()}'''
        save(OUT / f'gallery/{ident}.html', frame(f'{person["name"]} · 人物资料', body, '../', 'gallery', route=f'gallery/{ident}.html'))

    outline_title, outline_body, toc = md_content((ROOT / "content/outline.md").read_text(encoding="utf-8"))
    outline = f'''<div class="page-shell"><div class="page-heading"><p class="eyebrow">AUTHOR'S NOTES / 创作资料</p><h1>故事大纲</h1><p>此页包含完整剧情走向、人物选择与结局。</p></div>
<div id="outline-content"><div class="reading-layout"><aside class="reading-toc"><p class="eyebrow">大纲目录</p>{toc}</aside><div class="reading-column"><details class="mobile-toc"><summary>展开大纲目录</summary>{toc}</details><article class="prose">{outline_body}</article><div class="reading-end">创作大纲 · 九域守界 <a href="{REPO_URL}/blob/main/content/outline.md" target="_blank" rel="noopener">查看 Markdown 源文件</a></div></div></div></div></div>'''
    save(OUT / "outline/index.html", frame("故事大纲（含剧透）", outline, "../", noindex=True, route="outline/"))

    chapter_entries = []
    for i, source in enumerate(chapters):
        title, body, toc = md_content(source.read_text(encoding="utf-8"))
        title = title or source.stem
        chapter_entries.append(f'<a class="chapter-item" href="{escape(source.stem)}.html"><span>{i+1:02}</span><h2>{escape(title)}</h2><span aria-hidden="true">↗</span></a>')
        previous = f'<a href="{escape(chapters[i-1].stem)}.html">上一章</a>' if i else '<span></span>'
        following = f'<a href="{escape(chapters[i+1].stem)}.html">下一章</a>' if i + 1 < len(chapters) else '<span></span>'
        chapter = f'<div class="page-shell chapter-reading"><p class="eyebrow">九域守界 / 正文</p><h1>{escape(title)}</h1><article class="prose">{body}</article><nav class="chapter-pagination" aria-label="章节导航">{previous}<a href="./">章节目录</a>{following}</nav></div>'
        save(OUT / f"chapters/{source.stem}.html", frame(title, chapter, "../", "chapters", route=f"chapters/{source.stem}.html"))
    chapter_body = '<div class="chapter-list">' + ''.join(chapter_entries) + '</div>' if chapters else '''<section class="chapters-empty"><span class="empty-symbol" aria-hidden="true">卷</span><p class="eyebrow">故事正在准备中</p><h2>正文尚未发布</h2><p>章节发布后，这里会按顺序收录。<br>现在可以先认识故事中的人物。</p><a class="button primary" href="../gallery/">翻阅人物图集</a></section>'''
    chapter_index = f'<div class="page-shell"><div class="page-heading"><p class="eyebrow">THE STORY / 正文阅读</p><h1>小说正文</h1><p>九域守界的故事，从这里展开。</p></div>{chapter_body}</div>'
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
