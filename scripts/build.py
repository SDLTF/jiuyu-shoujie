"""Build a complete static website for GitHub Pages from local content."""
from pathlib import Path
import html
import json
import hashlib
import re
import markdown
from PIL import Image

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
        for name, href, label in [("gallery", "gallery/", "人物图集"), ("chapters", "chapters/", "正文阅读")]
    )
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · 九域守界</title>
<meta name="description" content="九域守界的官方故事档案：人物设定图集与小说正文。">
<meta name="theme-color" content="#101b25">{robots}
<link rel="canonical" href="{SITE_URL}{route}">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/site.css?v={asset_version('site.css')}">
<script src="{prefix}assets/site.js?v={asset_version('site.js')}" defer></script>
</head><body>
<a class="skip-link" href="#main">跳到正文</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="{prefix or './'}" aria-label="九域守界首页"><span class="brand-mark" aria-hidden="true">九</span><span>九域守界</span></a>
<nav aria-label="主导航">{links}<a class="repo-link" href="{REPO_URL}" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a></nav>
</div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div><a class="footer-title" href="{prefix or './'}">九域守界</a><span>故事与人物档案 · SDLTF</span></div>
<a href="{prefix}outline/" class="spoiler-link">创作大纲 <span>含剧透</span></a></footer>
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

    home = '''<div class="home-shell">
<section class="hero" aria-labelledby="hero-title">
<div class="hero-copy"><p class="eyebrow">九域守界 · 故事档案</p><h1 id="hero-title">九域<span>守界</span></h1>
<p class="hero-intro">从灰桥的一次救援出发，<br>走入九域交错的世界。</p>
<p class="hero-note">在这里认识同行者，翻阅他们的设定，等待故事展开。</p>
<div class="hero-actions"><a class="button primary" href="gallery/">翻阅人物图集</a><a class="button secondary" href="chapters/">正文阅读</a></div>
<p class="hero-meta"><span class="line" aria-hidden="true"></span>27 位角色 · 人物设定图集已收录</p></div>
<div class="hero-art" aria-label="人物设定预览">
<figure class="portrait portrait-one"><img src="assets/images/01.webp" alt="三岛的人物设定" fetchpriority="high"><figcaption><span>01</span>三岛</figcaption></figure>
<figure class="portrait portrait-two"><img src="assets/images/10.webp" alt="林清翊的人物设定"><figcaption><span>10</span>林清翊</figcaption></figure>
<figure class="portrait portrait-three"><img src="assets/images/06.webp" alt="吴语的人物设定"><figcaption><span>06</span>吴语</figcaption></figure>
<span class="art-caption">人物档案 / CHARACTER ARCHIVE</span></div>
</section>
<section class="entry-grid" aria-label="阅读入口">
<a class="entry" href="gallery/"><div class="entry-top"><span class="eyebrow">01 / 人物</span><span class="entry-status">27 份设定</span></div><h2>人物设定图集</h2><p>从头像认识角色，翻阅展示卡与个人资料。</p><span class="entry-action">打开图集 <span aria-hidden="true">↗</span></span></a>
<a class="entry" href="chapters/"><div class="entry-top"><span class="eyebrow">02 / 故事</span><span class="entry-status">正文尚未发布</span></div><h2>小说正文</h2><p>章节发布后，将在这里按顺序收录。</p><span class="entry-action">前往阅读目录 <span aria-hidden="true">↗</span></span></a>
</section></div>'''
    chapters = sorted((ROOT / "content/chapters").glob("*.md"))
    if chapters:
        home = home.replace("正文尚未发布", f"已收录 {len(chapters)} 章").replace("章节发布后，将在这里按顺序收录。", "按章节顺序，继续九域守界的故事。")
    save(OUT / "index.html", frame("故事与人物档案", home))

    cards = []
    for i, person in enumerate(characters):
        name, real, ident = escape(person["name"]), escape(person.get("real", "")), person["id"]
        loading = 'fetchpriority="high"' if i < 4 else 'loading="lazy"'
        cards.append(f'''<article class="character-card character-tile" data-search="{name} {real}"><a class="tile-link" href="{ident}.html" aria-label="查看{name}的展示卡和个人资料"><span class="tile-number">{ident}</span>{avatar(person, loading=loading)}<h2>{name}</h2><span class="tile-caption">查看人物资料</span></a></article>''')
    gallery = f'''<div class="page-shell gallery-shell"><div class="page-heading"><p class="eyebrow">CHARACTER ARCHIVE / 人物档案</p><h1>人物设定图集</h1><p>九域之间的同行者。选择头像，查看人物展示卡与个人资料。</p></div>
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
<section id="spoiler-notice" class="spoiler-notice" aria-labelledby="spoiler-title"><span class="warning-label">含剧透</span><h2 id="spoiler-title">在翻阅之前</h2><p>如果你希望随正文逐步探索故事，请先返回正文目录。<br>确认后，可以查看完整的创作大纲。</p><div class="notice-actions"><button id="reveal-outline" class="button primary" type="button">我已知晓，查看大纲</button><a class="button secondary" href="../chapters/">返回正文目录</a></div><noscript><p>请启用 JavaScript 后查看大纲，或在 GitHub 阅读 <a href="{REPO_URL}/blob/main/content/outline.md">大纲源文件（含剧透）</a>。</p></noscript></section>
<div id="outline-content" hidden><div class="reading-layout"><aside class="reading-toc"><p class="eyebrow">大纲目录</p>{toc}</aside><div class="reading-column"><details class="mobile-toc"><summary>展开大纲目录</summary>{toc}</details><article class="prose">{outline_body}</article><div class="reading-end">创作大纲 · 九域守界 <a href="{REPO_URL}/blob/main/content/outline.md" target="_blank" rel="noopener">查看 Markdown 源文件</a></div></div></div></div></div>'''
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

if __name__ == "__main__":
    build()
