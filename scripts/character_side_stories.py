"""Render explicitly associated side stories on character profile pages."""

from html import escape
import json
from pathlib import Path
import re


def profile_side_stories(character_id, root):
    manifest = Path(root) / 'content/character-side-stories.json'
    if not manifest.is_file():
        return ''

    stories = json.loads(manifest.read_text(encoding='utf-8'))['stories']
    seen = set()
    links = []
    for story in stories:
        ident = story['id']
        title = story['title']
        characters = story['character_ids']
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Side-story links require unique, valid story IDs')
        if not isinstance(title, str) or not title.strip():
            raise ValueError('Side-story links require a title')
        if not isinstance(characters, list) or not characters or any(
            not isinstance(value, str) or not re.fullmatch(r'[0-9]{2}', value) for value in characters
        ) or len(set(characters)) != len(characters):
            raise ValueError('Side-story links require unique two-digit character IDs')
        seen.add(ident)
        if str(character_id) not in characters:
            continue
        url = f'https://www.sdltf.club/side-stories/{ident}/'
        links.append(
            f'<p><a class="button secondary" href="{escape(url, quote=True)}">'
            f'阅读 {escape(title)} <span aria-hidden="true">→</span></a></p>'
        )

    if not links:
        return ''
    return (
        '<section id="character-side-stories" class="profile-section character-side-stories" '
        'aria-labelledby="character-side-stories-title">'
        '<h3 id="character-side-stories-title">相关支线</h3>'
        + ''.join(links) + '</section>'
    )
