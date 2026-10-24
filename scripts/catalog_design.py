"""Presentation for the main chapter directory; reading pages stay unchanged."""
import html
import json
import re
from pathlib import Path


def text(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value)).strip()


def esc(value):
    return html.escape(str(value), quote=True)


def title_parts(value):
    match = re.match(r'^(第[^\s章]+章)\s*(.+)$', value)
    return match.groups() if match else ('', value)


def directory(body, route):
    if route != 'chapters/':
        return body
    entries = re.findall(r'<a class="chapter-item[^\"]*" href="([^\"]+)">(.*?)</a>', body, re.S)
    if not entries:
        return body
    heading = re.search(r'<h1>(.*?)</h1>', body, re.S)
    title = text(heading[1]) if heading else '小说正文'
    latest = text(re.search(r'<h2>(.*?)</h2>', entries[-1][1], re.S)[1])
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'content/volumes.json').read_text(encoding='utf-8'))['volumes']
    last_end = 0
    seen = set()
    for volume in manifest:
        if not re.fullmatch(r'[a-z0-9-]+', volume['id']) or volume['id'] in seen:
            raise ValueError('Invalid or duplicate volume ID')
        if not isinstance(volume['start'], int) or not isinstance(volume['end'], int) or volume['start'] != last_end + 1 or volume['end'] < volume['start']:
            raise ValueError('Volumes must cover consecutive, non-overlapping chapter ranges')
        seen.add(volume['id'])
        last_end = volume['end']
    cards, published = [], []
    for index, (href, entry) in enumerate(entries):
        number_match = re.fullmatch(r'([0-9]{3})\.html', href)
        if not number_match:
            raise ValueError('Chapter picker requires three-digit chapter links')
        number = int(number_match[1])
        volume = next((v for v in manifest if v['start'] <= number <= v['end']), None)
        if volume is None:
            raise ValueError(f'Chapter {number} needs an entry in content/volumes.json')
        full_title = text(re.search(r'<h2>(.*?)</h2>', entry, re.S)[1])
        chapter, name = title_parts(full_title)
        image = re.search(r'<img\b[^>]+>', entry)
        image_url = re.search(r'\bsrc="([^\"]+)"', image[0])[1] if image else ''
        published.append({'volume': volume['id'], 'number': number, 'href': href, 'title': full_title, 'chapter': chapter, 'name': name, 'image': html.unescape(image_url)})
        image = image[0] if image else '<span class="catalog-no-art" aria-hidden="true">卷</span>'
        cards.append(f'''<a class="chapter-item catalog-card" href="{esc(href)}" data-chapter-title="{esc(full_title)}" data-chapter-number="{number}" data-volume="{esc(volume['id'])}" data-chapter-label="{esc(chapter)}" data-chapter-name="{esc(name)}" data-chapter-image="{esc(html.unescape(image_url))}"><span class="catalog-number">{number:02}</span><div class="catalog-art">{image}</div><div class="catalog-copy"><span>{esc(chapter or '正文')}</span><h2>{esc(name)}</h2><span class="catalog-card-action">翻开这一章 <span aria-hidden="true">↗</span></span></div></a>''')
    volumes = [v for v in manifest if any(item['volume'] == v['id'] for item in published)]
    volume_buttons = []
    for index, volume in enumerate(volumes):
        chapters = [item for item in published if item['volume'] == volume['id']]
        volume_buttons.append(f'''<button type="button" class="picker-volume" role="option" aria-selected="{'true' if index == 0 else 'false'}" data-picker-volume="{esc(volume['id'])}" data-volume-label="{esc(volume['label'])}" data-volume-name="{esc(volume['title'])}"><span>{esc(volume['label'])}</span><strong>{esc(volume['title'])}</strong><small>{chapters[0]['number']:02}–{chapters[-1]['number']:02} 章 · {'已完结' if chapters[-1]['number'] == volume['end'] else '连载中'}</small></button>''')
    first, first_volume = published[0], volumes[0]
    picker = f'''<section class="catalog-picker" data-catalog-picker hidden aria-labelledby="picker-title"><div class="picker-heading"><div><p class="eyebrow">FIND YOUR CHAPTER / 翻卷选章</p><h2 id="picker-title">选一卷，翻一章</h2></div><p id="picker-help"><span>↑↓ 选卷</span><span>←→ 选章</span></p></div><div class="picker-frame" data-picker-frame tabindex="0" role="region" aria-label="滑动选章" aria-describedby="picker-help"><aside class="picker-volume-rail" aria-label="选择卷"><button class="picker-volume-step" type="button" data-picker-volume-step="-1" aria-label="上一卷">↑</button><div class="picker-volumes" role="listbox" aria-label="卷目录">{''.join(volume_buttons)}</div><button class="picker-volume-step" type="button" data-picker-volume-step="1" aria-label="下一卷">↓</button><p>上下滑动选卷</p></aside><div class="picker-stage"><div class="picker-stage-top"><p data-picker-volume-title>{esc(first_volume['label'])} · {esc(first_volume['title'])}</p><span data-picker-position>01 / {sum(item['volume'] == first_volume['id'] for item in published):02}</span></div><div class="picker-scene" data-picker-scene><div class="picker-illustration"><img data-picker-image src="{esc(first['image'])}" alt="{esc(first['title'])}章节插画" draggable="false"><span class="picker-art-shade" aria-hidden="true"></span><span class="picker-chapter-number" data-picker-number aria-hidden="true">{first['number']:02}</span><span class="picker-art-label" data-picker-art-label>CHAPTER / 章节印象</span></div><div class="picker-chapter-copy"><p data-picker-chapter-label>{esc(first['chapter'])}</p><h3 data-picker-chapter-name>{esc(first['name'])}</h3><p class="picker-swipe-note">左右滑动，翻到想读的那一章</p></div></div><div class="picker-chapter-track" data-picker-track role="group" aria-label="本卷章节"></div><div class="picker-actions"><button type="button" class="picker-chapter-step" data-picker-chapter-step="-1" aria-label="上一章">←</button><a class="picker-read" data-picker-read href="{esc(first['href'])}">阅读这一章 <span aria-hidden="true">→</span></a><button type="button" class="picker-chapter-step" data-picker-chapter-step="1" aria-label="下一章">→</button></div></div></div><p class="picker-announcement" data-picker-announcement aria-live="polite" aria-atomic="true"></p></section>'''
    art_link = re.search(r'<a class="chapter-gallery-link[^\"]*".*?</a>', body, re.S)
    return f'''<div class="page-shell catalog-shell"><nav class="catalog-breadcrumb" aria-label="位置"><a href="../">← 返回首页</a><span>九域守界 / 正文阅读</span></nav><header class="catalog-hero catalog-hero-compact"><div class="catalog-intro"><p class="eyebrow">THE STORY ARCHIVE <span>/ 故事长卷</span></p><h1>{esc(title)}</h1><p class="catalog-description">一页一程，走进九域的故事。</p></div><div class="catalog-header-actions"><div class="catalog-stats"><span><strong>{len(volumes):02}</strong> 卷</span><span class="catalog-stats-line"></span><span><strong>{len(entries):02}</strong> 章已收录</span></div><a class="catalog-latest" href="{esc(entries[-1][0])}">最新 · {esc(latest)} <span aria-hidden="true">↗</span></a></div></header><a class="catalog-resume" data-resume-reader hidden><span>接着上次的旅途</span><strong data-resume-title></strong><span>继续阅读 →</span></a><section class="catalog-directory" aria-label="章节选择"><div class="catalog-tools" data-catalog-controls hidden><label class="catalog-search"><span aria-hidden="true">⌕</span><input type="search" data-chapter-search placeholder="搜索章节名或序号" aria-label="搜索章节名或序号"></label><div class="catalog-tools-right"><span data-chapter-count aria-live="polite">共 {len(entries)} 章</span><button type="button" data-chapter-sort aria-pressed="false">↑ 正序</button><button type="button" data-catalog-view aria-expanded="false">全部目录</button></div></div>{picker}<div class="chapter-list catalog-grid">{''.join(cards)}</div><p class="catalog-empty" data-chapter-empty hidden>没有找到这一章，试试其他章节名或序号。</p><div class="catalog-gallery-footer">{art_link[0] if art_link else ''}<span>也可以使用方向键选卷、选章</span></div></section><p class="catalog-colophon"><span aria-hidden="true">✦</span> 九域守界 · 每一个名字，都有自己的故事。</p></div>'''


def enhance(body, route):
    updated = directory(body, route)
    return (updated, 'library') if updated != body else (body, '')
