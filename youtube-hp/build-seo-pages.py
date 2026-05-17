from __future__ import annotations
import json
import re
from pathlib import Path

BASE = 'https://c-chan-dq-piano.chamberdeng.workers.dev'
ROOT = Path(__file__).resolve().parent

SERIES = [
    ('I', 'dq1', 'ドラゴンクエストI', 'Dragon Quest I', 'DQ1'),
    ('II', 'dq2', 'ドラゴンクエストII', 'Dragon Quest II', 'DQ2'),
    ('III', 'dq3', 'ドラゴンクエストIII', 'Dragon Quest III', 'DQ3'),
    ('IV', 'dq4', 'ドラゴンクエストIV', 'Dragon Quest IV', 'DQ4'),
    ('V', 'dq5', 'ドラゴンクエストV', 'Dragon Quest V', 'DQ5'),
    ('VI', 'dq6', 'ドラゴンクエストVI', 'Dragon Quest VI', 'DQ6'),
    ('VII', 'dq7', 'ドラゴンクエストVII', 'Dragon Quest VII', 'DQ7'),
    ('VIII', 'dq8', 'ドラゴンクエストVIII', 'Dragon Quest VIII', 'DQ8'),
    ('IX', 'dq9', 'ドラゴンクエストIX', 'Dragon Quest IX', 'DQ9'),
    ('X', 'dq10', 'ドラゴンクエストX', 'Dragon Quest X', 'DQ10'),
    ('XI', 'dq11', 'ドラゴンクエストXI', 'Dragon Quest XI', 'DQ11'),
]
SERIES_MAP = {k: {'slug': slug, 'ja': ja, 'en': en, 'code': code} for k, slug, ja, en, code in SERIES}
SERIES_ORDER = [key for key, *_ in SERIES]

CATS = {
    'opening': {'ja': '\u30aa\u30fc\u30d7\u30cb\u30f3\u30b0', 'en': 'Opening', 'match': ['\u30aa\u30fc\u30d7\u30cb\u30f3\u30b0']},
    'prologue': {'ja': '\u30d7\u30ed\u30ed\u30fc\u30b0', 'en': 'Prologue', 'match': ['\u30d7\u30ed\u30ed\u30fc\u30b0']},
    'interlude': {'ja': '\u5834\u9762\u8ee2\u63db', 'en': 'Interlude', 'match': ['\u5834\u9762\u8ee2\u63db']},
    'field': {'ja': '\u30d5\u30a3\u30fc\u30eb\u30c9', 'en': 'Field', 'match': ['\u30d5\u30a3\u30fc\u30eb\u30c9']},
    'sea': {'ja': '\u6d77', 'en': 'Sea', 'match': ['\u6d77']},
    'sky': {'ja': '\u7a7a', 'en': 'Sky', 'match': ['\u7a7a']},
    'town-village': {'ja': '\u8857\u30fb\u6751', 'en': 'Towns & Villages', 'match': ['\u8857\u30fb\u6751']},
    'castle': {'ja': '\u57ce', 'en': 'Castle', 'match': ['\u57ce']},
    'church-shrine': {'ja': '\u6559\u4f1a\u30fb\u307b\u3053\u3089', 'en': 'Churches & Shrines', 'match': ['\u6559\u4f1a\u30fb\u307b\u3053\u3089']},
    'casino': {'ja': '\u30ab\u30b8\u30ce', 'en': 'Casino', 'match': ['\u30ab\u30b8\u30ce']},
    'dungeon': {'ja': '\u30c0\u30f3\u30b8\u30e7\u30f3', 'en': 'Dungeon', 'match': ['\u30c0\u30f3\u30b8\u30e7\u30f3']},
    'tower': {'ja': '\u5854', 'en': 'Tower', 'match': ['\u5854']},
    'event': {'ja': '\u30a4\u30d9\u30f3\u30c8', 'en': 'Event', 'match': ['\u30a4\u30d9\u30f3\u30c8']},
    'character-theme': {'ja': '\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u30c6\u30fc\u30de', 'en': 'Character Theme', 'match': ['\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u30c6\u30fc\u30de']},
    'normal-battle': {'ja': '\u901a\u5e38\u6226\u95d8', 'en': 'Normal Battle', 'match': ['\u901a\u5e38\u6226\u95d8']},
    'boss-battle': {'ja': '\u30dc\u30b9\u6226\u95d8', 'en': 'Boss Battle', 'match': ['\u30dc\u30b9\u6226\u95d8']},
    'ending': {'ja': '\u30a8\u30f3\u30c7\u30a3\u30f3\u30b0', 'en': 'Ending', 'match': ['\u30a8\u30f3\u30c7\u30a3\u30f3\u30b0']},
    'game-over': {'ja': '\u5168\u6ec5', 'en': 'Game Over', 'match': ['\u5168\u6ec5']},
    'medley': {'ja': '\u30e1\u30c9\u30ec\u30fc', 'en': 'Medleys', 'match': []},
}

CAT_EN = {
    'イベント': 'Event',
    'エンディング': 'Ending',
    'オープニング': 'Opening',
    'カジノ': 'Casino',
    'キャラクターテーマ': 'Character Theme',
    'ダンジョン': 'Dungeon',
    'フィールド': 'Field',
    'プロローグ': 'Prologue',
    'ボス戦闘': 'Boss Battle',
    '全滅': 'Game Over',
    '城': 'Castle',
    '場面転換': 'Interlude',
    '塔': 'Tower',
    '教会・ほこら': 'Churches & Shrines',
    '海': 'Sea',
    '空': 'Sky',
    '街・村': 'Towns & Villages',
    '通常戦闘': 'Normal Battle',
}

DIFF_EN = {
    '初級': 'Beginner',
    '初中級': 'Beginner-Intermediate',
    '中級': 'Intermediate',
    '中上級': 'Upper-Intermediate',
    '上級': 'Advanced',
    '未設定': 'Not set',
}

LOCAL_PREVIEW = """<script>
(() => {
  if (location.protocol !== 'file:') return;
  const mapAsset = (value) => {
    if (!value || !value.startsWith('/') || value.startsWith('//')) return value;
    const clean = value.replace(/^\//, '');
    const root = location.href.replace(/[^/]*$/, '');
    if (!clean) return root;
    if (clean.endsWith('/')) return new URL(clean + 'index.html', root).href;
    return new URL(clean, root).href;
  };
  const rewrite = () => {
    document.querySelectorAll('a[href^="/"]').forEach((node) => {
      node.setAttribute('href', mapAsset(node.getAttribute('href')));
    });
    document.querySelectorAll('link[href^="/"]').forEach((node) => {
      node.setAttribute('href', mapAsset(node.getAttribute('href')));
    });
    document.querySelectorAll('img[src^="/"]').forEach((node) => {
      node.setAttribute('src', mapAsset(node.getAttribute('src')));
    });
  };
  rewrite();
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const raw = link.getAttribute('href');
    if (!raw || !raw.startsWith('/')) return;
    event.preventDefault();
    location.href = mapAsset(raw);
  }, true);
  new MutationObserver(rewrite).observe(document.documentElement, { childList: true, subtree: true });
})();
</script>"""


def load_js(filename: str, prefix: str):
    raw = (ROOT / filename).read_text(encoding='utf-8-sig')
    return json.loads(raw[len(prefix):].strip().rstrip(';'))


def load_titles():
    raw = (ROOT / 'song-title-translations.js').read_text(encoding='utf-8-sig')
    by_id_match = re.search(r'en:\s*\{\s*titlesById:\s*(\{.*?\})\s*,\s*titles:', raw, re.S)
    titles_match = re.search(r'en:\s*\{\s*titlesById:\s*\{.*?\}\s*,\s*titles:\s*(\{.*?\})\s*,\s*categories:', raw, re.S)
    return {
        'by_id': json.loads(by_id_match.group(1)) if by_id_match else {},
        'by_title': json.loads(titles_match.group(1)) if titles_match else {},
    }


def esc(value=''):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def infer_series(title: str) -> str:
    match = re.search(r'DRAGON QUEST\s*(XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\b', title.upper())
    return match.group(1) if match else ''


def is_medley(title: str) -> bool:
    lowered = title.lower()
    return 'medley' in lowered or 'メドレー' in title


def normalize_thumb(src: str | None) -> str:
    if not src:
        return ''
    return '/' + src.lstrip('./').lstrip('/')


def make_head(lang: str, title: str, desc: str, canon: str, ja_href: str, en_href: str, graph: list[dict]) -> str:
    locale = 'ja_JP' if lang == 'ja' else 'en_US'
    html_lang = 'ja' if lang == 'ja' else 'en'
    analytics_tag = (
        '<!-- Google tag (gtag.js) -->'
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-S51EBHNVZ3"></script>'
        '<script>'
        'window.dataLayer = window.dataLayer || [];'
        'function gtag(){dataLayer.push(arguments);}'
        "gtag('js', new Date());"
        "gtag('config', 'G-S51EBHNVZ3');"
        '</script>'
    )
    return (
        '<!DOCTYPE html>'
        f'<html lang="{html_lang}"><head>'
        f'{analytics_tag}'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc)}">'
        '<meta name="robots" content="index, follow">'
        f'<link rel="canonical" href="{canon}">'
        f'<link rel="alternate" hreflang="ja" href="{ja_href}">'
        f'<link rel="alternate" hreflang="en" href="{en_href}">'
        f'<link rel="alternate" hreflang="x-default" href="{ja_href}">'
        f'<meta property="og:title" content="{esc(title)}">'
        f'<meta property="og:description" content="{esc(desc)}">'
        '<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{locale}">'
        f'<meta property="og:url" content="{canon}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{esc(title)}">'
        f'<meta name="twitter:description" content="{esc(desc)}">'
        '<link rel="stylesheet" href="/styles.css">'
        f'{LOCAL_PREVIEW}'
        f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>'
        '</head>'
    )


def breadcrumbs(items: list[tuple[str, str]]) -> str:
    parts = []
    for i, (label, href) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{esc(label)}</span>')
        else:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + '<span> / </span>'.join(parts) + '</nav>'


def breadcrumb_json(items: list[tuple[str, str]]) -> dict:
    elements = []
    for i, (label, href) in enumerate(items, start=1):
        row = {'@type': 'ListItem', 'position': i, 'name': label}
        if i != len(items):
            row['item'] = BASE + href if href.startswith('/') else href
        elements.append(row)
    return {'@type': 'BreadcrumbList', 'itemListElement': elements}


def topbar(lang: str, current: str, alt: str) -> str:
    is_home = current in ('/', '/en.html')
    if lang == 'ja':
        home_link = '' if is_home else '<a class="topbar-home" href="/">ホーム</a>'
        return (
            '<nav class="topbar" aria-label="主要ナビゲーション">'
            f'{home_link}<a class="brand" href="/">しーちゃんピアノ</a>'
            '<div class="topbar-right"><div class="topbar-links">'
            '<a href="/series-index.html">作品別ページ</a>'
            '<a class="topbar-shortcut" href="/category-index.html">カテゴリ別ページ</a>'
            '<a class="topbar-cta" href="https://www.youtube.com/@chamberd_piano" target="_blank" rel="noreferrer">YouTubeチャンネルを見る</a>'
            '</div><div class="language-switch" aria-label="言語切り替え">'
            f'<a class="lang-pill is-active" href="{current}">日本語</a>'
            f'<a class="lang-pill" href="{alt}">English</a>'
            '</div></div></nav>'
        )
    home_link = '' if is_home else '<a class="topbar-home" href="/en.html">Home</a>'
    return (
        '<nav class="topbar" aria-label="Primary navigation">'
        f'{home_link}<a class="brand" href="/en.html">C-chan piano</a>'
        '<div class="topbar-right"><div class="topbar-links">'
        '<a href="/en/series-index.html">Browse by Series</a>'
        '<a class="topbar-shortcut" href="/en/category-index.html">Browse by Category</a>'
        '<a class="topbar-cta" href="https://www.youtube.com/@chamberd_piano" target="_blank" rel="noreferrer">Visit the YouTube channel</a>'
        '</div><div class="language-switch" aria-label="Language switch">'
        f'<a class="lang-pill" href="{alt}">日本語</a>'
        f'<a class="lang-pill is-active" href="{current}">English</a>'
        '</div></div></nav>'
    )


def metric(label: str, value: str) -> str:
    return f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'


def action(href: str, label: str, primary: bool = False, external: bool = False) -> str:
    cls = 'video-link page-action is-primary' if primary else 'video-link page-action'
    rel = ' rel="noreferrer"' if external else ''
    target = ' target="_blank"' if external else ''
    return f'<a class="{cls}" href="{href}"{target}{rel}>{esc(label)}</a>'


def entry_card(href: str, title: str, body: str, meta: str = '', thumb: str = '') -> str:
    extra = f'<span class="entry-card-meta">{esc(meta)}</span>' if meta else ''
    thumb_html = f'<img class="entry-card-thumb" src="{thumb}" alt="{esc(title)}" loading="lazy">' if thumb else ''
    return f'<a class="entry-card" href="{href}">{thumb_html}<span class="entry-card-title">{esc(title)}</span><span class="entry-card-body">{esc(body)}</span>{extra}</a>'


def entry_grid(cards: list[str]) -> str:
    return '<div class="entry-link-grid">' + ''.join(cards) + '</div>'


def playlist_cards(items: list[dict], lang: str, hero: bool = False) -> str:
    wrap = 'seo-card-grid seo-card-grid-hero' if hero else 'seo-card-grid'
    body = []
    for playlist in items:
        thumb = normalize_thumb(playlist.get('thumbnail'))
        thumb_html = f'<img class="playlist-thumb" src="{thumb}" alt="{esc(playlist["title"])}" loading="lazy">' if thumb else ''
        count = playlist.get('itemCountText') or ''
        desc = playlist.get('description') or ''
        link_label = 'プレイリストを開く' if lang == 'ja' else 'Open playlist'
        body.append(
            '<article class="video-card video-card-grid seo-card">'
            f'{thumb_html}'
            f'<p class="video-meta">{esc(count)}</p>'
            f'<h3>{esc(playlist["title"])}</h3>'
            f'{f"<p>{esc(desc)}</p>" if desc else ""}'
            f'<a class="video-link" href="{playlist["url"]}" target="_blank" rel="noreferrer">{link_label}</a>'
            '</article>'
        )
    return f'<div class="{wrap}">' + ''.join(body) + '</div>'


def medley_video_cards(items: list[dict], lang: str) -> str:
    body = []
    for item in items:
        thumb = normalize_thumb(item.get('thumbnail'))
        thumb_html = f'<img class="playlist-thumb" src="{thumb}" alt="{esc(item["title"])}" loading="lazy">' if thumb else ''
        link_label = '動画を開く' if lang == 'ja' else 'Open video'
        body.append(
            '<article class="video-card video-card-grid seo-card">'
            f'{thumb_html}'
            f'<p class="video-meta">{esc(item["playlistTitle"])}</p>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<a class="video-link" href="{item["url"]}" target="_blank" rel="noreferrer">{link_label}</a>'
            '</article>'
        )
    return '<div class="seo-card-grid">' + ''.join(body) + '</div>'


def hero_playlist_thumb(playlist: dict, lang: str) -> str:
    thumb = normalize_thumb(playlist.get('thumbnail'))
    if not thumb:
        return ''
    label = '\u4f5c\u54c1\u5225\u30dd\u30c3\u30c9\u30ad\u30e3\u30b9\u30c8' if lang == 'ja' else 'Series podcast'
    count = playlist.get('itemCountText') or ''
    title = playlist.get('title') or ''
    count_html = f'<p class="video-meta">{esc(count)}</p>' if count else ''
    title_html = f'<p class="hero-playlist-title">{esc(title)}</p>' if title else ''
    return (
        '<aside class="hero-playlist-thumb">'
        f'<p class="hero-playlist-kicker">{esc(label)}</p>'
        f'<a class="hero-playlist-image-link" href="{playlist["url"]}" target="_blank" rel="noreferrer">'
        f'<img class="hero-playlist-image" src="{thumb}" alt="{esc(title)}" loading="lazy">'
        '</a>'
        '<div class="hero-playlist-meta">'
        f'{count_html}'
        f'{title_html}'
        '</div>'
        '</aside>'
    )


def song_table(rows: list[dict], lang: str) -> str:
    headers = ('曲番号', '曲名', 'カテゴリ', '難易度') if lang == 'ja' else ('No.', 'Title', 'Category', 'Difficulty')
    body = []
    for row in rows:
        title = row['songTitle'] if lang == 'ja' else row['songTitleEn']
        category = row['category'] if lang == 'ja' else row['categoryEn']
        difficulty = (row.get('difficultyLabel') or '未設定') if lang == 'ja' else (row.get('difficultyEn') or 'Not set')
        difficulty_stars = row.get('difficultyStars')
        if row.get('videoUrl'):
            title_html = f'<a class="song-link" href="{row["videoUrl"]}" target="_blank" rel="noreferrer">{esc(title)}</a>'
            number_html = f'<a class="song-link song-number-link" href="{row["videoUrl"]}" target="_blank" rel="noreferrer">{esc(row["id"])}</a>'
        else:
            title_html = esc(title)
            number_html = esc(row['id'])
        body.append(
            '<tr>'
            f'<td>{number_html}</td>'
            f'<td>{title_html}</td>'
            f'<td>{esc(category)}</td>'
            f'<td>{render_difficulty_html(difficulty, difficulty_stars)}</td>'
            '</tr>'
        )
    return (
        '<div class="song-table-wrap seo-song-table-wrap"><div class="song-table-scroll">'
        '<table class="song-table"><thead><tr>'
        f'<th>{headers[0]}</th><th>{headers[1]}</th><th>{headers[2]}</th><th>{headers[3]}</th>'
        '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div></div>'
    )


def render_difficulty_html(label: str, stars: int | None) -> str:
    filled = max(0, min(5, stars)) if isinstance(stars, int) else 0
    empty = 5 - filled
    star_text = ('★' * filled) + ('☆' * empty)
    extra_class = ' is-empty' if filled == 0 else ''
    aria = f'{label} {filled}/5' if filled else label
    return (
        '<span class="difficulty-cell">'
        f'<span class="difficulty-text">{esc(label)}</span>'
        f'<span class="difficulty-stars{extra_class}" aria-label="{esc(aria)}">{star_text}</span>'
        '</span>'
    )


def section(kicker: str, title: str, inner: str, copy: str = '') -> str:
    copy_html = f'<p class="section-copy">{esc(copy)}</p>' if copy else ''
    return (
        '<section class="section">'
        '<div class="section-heading">'
        f'<p class="section-kicker">{esc(kicker)}</p>'
        f'<h2>{esc(title)}</h2>'
        f'{copy_html}'
        '</div>'
        f'{inner}'
        '</section>'
    )


def shell(lang: str, current: str, alt: str, crumb_html: str, title: str, lead: str, metrics_html: str, actions_html: str, feature_html: str, main: str) -> str:
    footer = '© しーちゃんピアノ' if lang == 'ja' else '© C-chan piano'
    feature_block = f'<div class="page-hero-feature">{feature_html}</div>' if feature_html else ''
    return (
        '<body><div class="site-bg" aria-hidden="true"></div>'
        f'<header class="hero hero-simple">{topbar(lang, current, alt)}'
        '<section class="page-hero seo-hero-panel">'
        '<div class="seo-hero-copy">'
        f'{crumb_html}'
        f'<p class="eyebrow">{"Dragon Quest Piano Library" if lang == "ja" else "Dragon Quest Piano Library"}</p>'
        f'<h1>{esc(title)}</h1>'
        f'<p class="lead">{esc(lead)}</p>'
        f'<dl class="hero-metrics page-hero-metrics">{metrics_html}</dl>'
        f'<div class="page-hero-actions">{actions_html}</div>'
        '</div>'
        f'{feature_block}'
        '</section></header>'
        f'<main class="page seo-page">{main}</main>'
        f'<footer class="seo-footer"><p>{footer}</p></footer></body></html>'
    )


def write(path: str | Path, content: str) -> None:
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding='utf-8')


def patch_home(path_str: str, lang: str, series_playlists: dict[str, dict]) -> None:
    path = ROOT / path_str
    text = path.read_text(encoding='utf-8')
    text = text.replace('https://chamberd-piano.github.io', BASE)
    series_cards = []
    for key, meta in SERIES_MAP.items():
        href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
        body = f'{meta["ja"]} \u306e\u66f2\u3092\u63a2\u3059' if lang == 'ja' else f'Browse {meta["en"]} songs'
        thumb = normalize_thumb(series_playlists.get(key, {}).get('thumbnail')) if series_playlists.get(key) else ''
        series_cards.append(entry_card(href, meta['code'], body, thumb=thumb))
    category_cards = []
    bgm_cards = []
    for slug, info in CATS.items():
        href = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
        if slug == 'medley':
            body = '\u4f5c\u696d\u7528BGM\u5411\u3051\u306e\u30e1\u30c9\u30ec\u30fc' if lang == 'ja' else 'Medleys for background listening'
            bgm_cards.append(entry_card(href, info['ja'] if lang == 'ja' else info['en'], body))
            continue
        body = '\u30c9\u30e9\u30b4\u30f3\u30af\u30a8\u30b9\u30c8 \u30d4\u30a2\u30ce\u306e\u5165\u53e3' if lang == 'ja' else 'Category page'
        category_cards.append(entry_card(href, info['ja'] if lang == 'ja' else info['en'], body))
    if lang == 'ja':
        heading = '\u4f5c\u54c1\u5225\u30fb\u30ab\u30c6\u30b4\u30ea\u5225\u306e\u7740\u5730\u30da\u30fc\u30b8'
        copy = '\u691c\u7d22\u7528\u9014\uff08\u4f8b\u3001DQ8\u3001\u6226\u95d8\u66f2 \u7b49\uff09\u306b\u5408\u308f\u305b\u3066\u3001\u30d4\u30a2\u30ce\u6f14\u594f\u52d5\u753b\u306e\u4f5c\u54c1\u5225\u30fb\u30ab\u30c6\u30b4\u30ea\u5225\u30da\u30fc\u30b8\u3078\u9032\u3081\u307e\u3059\u3002'
        s_title = '\u4f5c\u54c1\u5225\u30da\u30fc\u30b8'
        c_title = '\u30ab\u30c6\u30b4\u30ea\u5225\u30da\u30fc\u30b8'
        b_title = '\u4f5c\u696d\u7528BGM'
    else:
        heading = 'Series and category landing pages'
        copy = 'Jump to Dragon Quest piano landing pages by series and category.'
        s_title = 'Browse by Series'
        c_title = 'Browse by Category'
        b_title = 'Background Listening'
    hub = (
        '<section class="section seo-hub-links" id="seo-links">'
        '<div class="section-heading">'
        '<p class="section-kicker">SEO Landing Pages</p>'
        f'<h2>{esc(heading)}</h2>'
        f'<p class="section-copy">{esc(copy)}</p>'
        '</div>'
        f'<div class="seo-hub-block"><div class="section-heading compact-heading"><p class="section-kicker">Series</p><h3>{esc(s_title)}</h3></div>{entry_grid(series_cards)}</div>'
        f'<div class="seo-hub-block"><div class="section-heading compact-heading"><p class="section-kicker">Categories</p><h3>{esc(c_title)}</h3></div>{entry_grid(category_cards)}</div>'
        f'<div class="seo-hub-block"><div class="section-heading compact-heading"><p class="section-kicker">BGM</p><h3>{esc(b_title)}</h3></div>{entry_grid(bgm_cards)}</div>'
        '</section>'
    )
    import re
    if 'seo-hub-links' in text:
        text = re.sub(r'<section class="section seo-hub-links" id="seo-links">.*?</section>', hub, text, count=1, flags=re.S)
    else:
        text = text.replace('<main class="page">', '<main class="page">\n    ' + hub, 1)
    path.write_text(text, encoding='utf-8')


def series_feature_playlist(key: str, series_playlists: dict[str, dict]) -> list[dict]:
    playlist = series_playlists.get(key)
    return [playlist] if playlist else []


def related_category_cards(lang: str) -> str:
    cards = []
    for slug, info in CATS.items():
        href = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
        body = '関連カテゴリ' if lang == 'ja' else 'Related category'
        cards.append(entry_card(href, info['ja'] if lang == 'ja' else info['en'], body))
    return entry_grid(cards)


def build() -> None:
    songs = load_js('song-reference-data.js', 'window.songReferenceData = ')
    playlists = load_js('playlist-data.js', 'window.playlistData = ')
    en_titles = load_titles()

    all_rows = []
    by_series = {}
    for skey, rows in songs.items():
        cooked = []
        for row in rows:
            item = dict(row)
            item['seriesKey'] = skey
            item['songTitleEn'] = en_titles['by_id'].get(row['id']) or en_titles['by_title'].get(row['songTitle'], row['songTitle'])
            item['categoryEn'] = CAT_EN.get(row['category'], row['category'])
            item['difficultyEn'] = DIFF_EN.get(row.get('difficultyLabel', ''), row.get('difficultyLabel', ''))
            cooked.append(item)
            all_rows.append(item)
        by_series[skey] = cooked

    series_playlists = {}
    medley_playlists = []
    for playlist in playlists:
        playlist = dict(playlist)
        playlist['thumbnail'] = normalize_thumb(playlist.get('thumbnail'))
        key = infer_series(playlist['title'])
        if key and key not in series_playlists and not is_medley(playlist['title']):
            series_playlists[key] = playlist
        if is_medley(playlist['title']):
            medley_playlists.append(playlist)
    medley_tracks = []
    seen_medley_urls = set()
    for playlist in medley_playlists:
        for track in playlist.get('tracks', []):
            url = track.get('url')
            if not url or url in seen_medley_urls:
                continue
            seen_medley_urls.add(url)
            medley_tracks.append({
                'title': track.get('title') or track.get('rawTitle') or playlist['title'],
                'url': url,
                'playlistTitle': playlist['title'],
                'thumbnail': playlist.get('thumbnail', ''),
            })

    urls = [BASE + '/', BASE + '/en.html']

    for key, slug, ja_name, en_name, code in SERIES:
        rows = sorted(by_series[key], key=lambda row: row['sortNumber'])
        linked_count = sum(1 for row in rows if row.get('videoUrl'))
        playlist_items = series_feature_playlist(key, series_playlists)

        for lang in ('ja', 'en'):
            page = f'/{slug}/' if lang == 'ja' else f'/en/{slug}/'
            alt = f'/en/{slug}/' if lang == 'ja' else f'/{slug}/'
            title = f'{code} ピアノ | {ja_name} ピアノ演奏ライブラリー | しーちゃんピアノ' if lang == 'ja' else f'{code} Piano | {en_name} Piano Library | C-chan piano'
            desc = (
                f'{ja_name} の楽曲を作品別に探せるページです。ドラゴンクエスト ピアノ、{code} ピアノ、ゲーム音楽 ピアノの検索着地として、曲一覧とYouTube導線を整理しています。'
                if lang == 'ja' else
                f'Browse {en_name} piano performances with song links and YouTube playlist access.'
            )
            crumbs = [('ホーム', '/') if lang == 'ja' else ('Home', '/en.html'), (code, page)]
            graph = [
                breadcrumb_json(crumbs),
                {'@type': 'CollectionPage', 'name': title, 'description': desc, 'url': BASE + page, 'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US'},
                {'@type': 'ItemList', 'itemListElement': [
                    {'@type': 'ListItem', 'position': i + 1, 'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'], **({'url': row['videoUrl']} if row.get('videoUrl') else {})}
                    for i, row in enumerate(rows)
                ]},
            ]
            metrics = ''.join([
                metric('収録曲数' if lang == 'ja' else 'Songs', str(len(rows))),
                metric('動画リンク' if lang == 'ja' else 'Linked videos', str(linked_count)),
                metric('作品別プレイリスト' if lang == 'ja' else 'Playlists', '1' if playlist_items else '0'),
            ])
            actions = []
            if playlist_items:
                actions.append(action(playlist_items[0]['url'], 'YouTubeの作品別プレイリスト' if lang == 'ja' else 'Open playlist', primary=True, external=True))
            actions.append(action('/category-index.html' if lang == 'ja' else '/en/category-index.html', 'カテゴリ別に探す' if lang == 'ja' else 'Browse categories'))
            actions.append(action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る' if lang == 'ja' else 'Visit YouTube', external=True))
            feature = playlist_cards(playlist_items, lang, hero=True) if playlist_items else ''
            main = ''
            main += section('Songs', '収録曲一覧' if lang == 'ja' else 'Song List', song_table(rows, lang), '曲番号順でたどれる一覧です。' if lang == 'ja' else 'Song list ordered by catalog number.')
            main += section('Related', '関連カテゴリ' if lang == 'ja' else 'Related Categories', related_category_cards(lang), 'フィールド曲・戦闘曲・メドレーなど横断導線を用意しています。' if lang == 'ja' else 'Cross-link into field, battle, and medley pages.')
            html = make_head(lang, title, desc, BASE + page, BASE + f'/{slug}/', BASE + f'/en/{slug}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), f'{ja_name} ピアノ演奏ライブラリー' if lang == 'ja' else f'{en_name} Piano Library', desc, metrics, ''.join(actions), feature, main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/{slug}/', BASE + f'/en/{slug}/'])

    for slug, info in CATS.items():
        rows = [row for row in all_rows if row['category'] in info['match']]
        rows.sort(key=lambda row: (SERIES_ORDER.index(row['seriesKey']), row['sortNumber']))
        if slug == 'medley':
            featured = medley_playlists[:2]
        else:
            featured = []
        series_keys = sorted({row['seriesKey'] for row in rows}, key=lambda key: SERIES_ORDER.index(key))
        linked_count = sum(1 for row in rows if row.get('videoUrl'))

        for lang in ('ja', 'en'):
            page = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
            alt = f'/en/category/{slug}/' if lang == 'ja' else f'/category/{slug}/'
            title = f'{info["ja"]} ピアノ | ドラクエ ピアノ演奏ライブラリー | しーちゃんピアノ' if lang == 'ja' else f'{info["en"]} | Dragon Quest Piano Library | C-chan piano'
            desc = (
                f'{info["ja"]} を作品横断で探せるページです。ドラゴンクエスト ピアノ、ドラクエ ピアノ演奏、作業用BGMの入口として使いやすく整理しています。'
                if lang == 'ja' else
                f'Browse {info["en"]} across the Dragon Quest piano library.'
            )
            label = info['ja'] if lang == 'ja' else info['en']
            crumbs = [('ホーム', '/') if lang == 'ja' else ('Home', '/en.html'), (label, page)]
            if slug == 'medley':
                item_list = [
                    {'@type': 'ListItem', 'position': i + 1, 'name': track['title'], 'url': track['url']}
                    for i, track in enumerate(medley_tracks)
                ]
            else:
                item_list = [
                    {'@type': 'ListItem', 'position': i + 1, 'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'], **({'url': row['videoUrl']} if row.get('videoUrl') else {})}
                    for i, row in enumerate(rows)
                ]
            graph = [
                breadcrumb_json(crumbs),
                {'@type': 'CollectionPage', 'name': title, 'description': desc, 'url': BASE + page, 'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US'},
                {'@type': 'ItemList', 'itemListElement': item_list},
            ]
            metrics = ''.join([
                metric('対象曲数' if lang == 'ja' else 'Songs', str(len(rows) if slug != 'medley' else len(medley_tracks))),
                metric('関連シリーズ' if lang == 'ja' else 'Series', str(len(series_keys) if slug != 'medley' else len(SERIES_MAP))),
                metric('動画リンク' if lang == 'ja' else 'Linked videos', str(linked_count if slug != 'medley' else len(medley_tracks))),
            ])
            actions = [
                action('/category-index.html' if lang == 'ja' else '/en/category-index.html', 'カテゴリ一覧へ' if lang == 'ja' else 'Category index', primary=True),
                action('/series-index.html' if lang == 'ja' else '/en/series-index.html', '作品別ページへ' if lang == 'ja' else 'Browse series'),
                action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る' if lang == 'ja' else 'Visit YouTube', external=True),
            ]
            feature = playlist_cards(featured, lang, hero=True) if featured else ''
            if slug == 'medley':
                table_or_cards = (
                    medley_video_cards(medley_tracks, lang)
                    + section(
                        'Playlists',
                        'メドレープレイリスト' if lang == 'ja' else 'Medley Playlists',
                        playlist_cards(medley_playlists, lang),
                        'YouTube上のプレイリストへ進めます。' if lang == 'ja' else 'Open the full YouTube playlists.',
                    )
                )
                section_title = 'メドレー動画' if lang == 'ja' else 'Medley Videos'
                section_copy = '作業用BGMや場面別に聴けるメドレー動画をまとめています。' if lang == 'ja' else 'Medley videos for background listening and themed browsing.'
            else:
                table_or_cards = song_table(rows, lang)
                section_title = label
                section_copy = 'シリーズ横断で曲を一覧できるカテゴリページです。' if lang == 'ja' else 'A cross-series category page.'
            related_cards = []
            if slug == 'medley':
                for meta in SERIES_MAP.values():
                    href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
                    related_cards.append(entry_card(href, meta['code'], '作品別ページへ' if lang == 'ja' else 'Series page'))
            else:
                for key in series_keys[:8]:
                    meta = SERIES_MAP[key]
                    href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
                    related_cards.append(entry_card(href, meta['code'], '作品別ページへ' if lang == 'ja' else 'Series page'))
            main = section('Category', section_title, table_or_cards, section_copy)
            main += section('Related', '関連作品' if lang == 'ja' else 'Related Series', entry_grid(related_cards), '関連作品へ回遊しやすい導線です。' if lang == 'ja' else 'Jump into related series pages.')
            hero_title = f'{info["ja"]}を探す' if lang == 'ja' else f'Browse {info["en"]}'
            html = make_head(lang, title, desc, BASE + page, BASE + f'/category/{slug}/', BASE + f'/en/category/{slug}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), hero_title, desc, metrics, ''.join(actions), feature, main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/category/{slug}/', BASE + f'/en/category/{slug}/'])

    ja_series_cards = [entry_card(f'/{meta["slug"]}/', meta['code'], meta['ja'], thumb=normalize_thumb(series_playlists.get(key, {}).get('thumbnail')) if series_playlists.get(key) else '') for key, meta in SERIES_MAP.items()]
    en_series_cards = [entry_card(f'/en/{meta["slug"]}/', meta['code'], meta['en'], thumb=normalize_thumb(series_playlists.get(key, {}).get('thumbnail')) if series_playlists.get(key) else '') for key, meta in SERIES_MAP.items()]
    ja_cat_cards = [entry_card(f'/category/{slug}/', info['ja'], 'カテゴリ別ページ') for slug, info in CATS.items() if slug != 'medley']
    en_cat_cards = [entry_card(f'/en/category/{slug}/', info['en'], 'Category page') for slug, info in CATS.items() if slug != 'medley']
    ja_bgm_cards = [entry_card('/category/medley/', CATS['medley']['ja'], '作業用BGM向けメドレー')]
    en_bgm_cards = [entry_card('/en/category/medley/', CATS['medley']['en'], 'Medleys for background listening')]

    write('series-index.html', make_head('ja', '作品別ページ一覧 | しーちゃんピアノ', 'DQ1〜DQ11の作品別ページ一覧です。', BASE + '/series-index.html', BASE + '/series-index.html', BASE + '/en/series-index.html', [breadcrumb_json([('ホーム', '/'), ('作品別ページ一覧', '/series-index.html')]), {'@type': 'CollectionPage', 'name': '作品別ページ一覧', 'description': 'DQ1〜DQ11の作品別ページ一覧です。', 'url': BASE + '/series-index.html', 'inLanguage': 'ja-JP'}]) + shell('ja', '/series-index.html', '/en/series-index.html', breadcrumbs([('ホーム', '/'), ('作品別ページ一覧', '/series-index.html')]), '作品別ページ一覧', 'DQ1〜DQ11の作品別ページ一覧です。', metric('ページ数', '11') + metric('言語', '日本語 / English') + metric('目的', '作品名検索の入口'), action('/category-index.html', 'カテゴリ別も見る', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True), '', section('Series', 'DQ1〜DQ11', entry_grid(ja_series_cards), '各作品ページから曲一覧とYouTube導線に進めます。')))
    write('en/series-index.html', make_head('en', 'Browse by Series | C-chan piano', 'Series landing pages from DQ1 to DQ11.', BASE + '/en/series-index.html', BASE + '/series-index.html', BASE + '/en/series-index.html', [breadcrumb_json([('Home', '/en.html'), ('Browse by Series', '/en/series-index.html')]), {'@type': 'CollectionPage', 'name': 'Browse by Series', 'description': 'Series landing pages from DQ1 to DQ11.', 'url': BASE + '/en/series-index.html', 'inLanguage': 'en-US'}]) + shell('en', '/en/series-index.html', '/series-index.html', breadcrumbs([('Home', '/en.html'), ('Browse by Series', '/en/series-index.html')]), 'Browse by Series', 'Category pages from DQ1 to DQ11.', metric('Pages', '11') + metric('Language', 'English / Japanese') + metric('Purpose', 'Series search landing'), action('/en/category-index.html', 'Browse categories', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'Visit YouTube', external=True), '', section('Series', 'DQ1–DQ11', entry_grid(en_series_cards), 'Each page leads into song lists and the YouTube channel.')))
    write('category-index.html', make_head('ja', 'カテゴリ別ページ一覧 | しーちゃんピアノ', 'フィールド曲・戦闘曲・街村・エンディング・メドレーのカテゴリ別ページ一覧です。', BASE + '/category-index.html', BASE + '/category-index.html', BASE + '/en/category-index.html', [breadcrumb_json([('ホーム', '/'), ('カテゴリ別ページ一覧', '/category-index.html')]), {'@type': 'CollectionPage', 'name': 'カテゴリ別ページ一覧', 'description': 'カテゴリ別ページ一覧です。', 'url': BASE + '/category-index.html', 'inLanguage': 'ja-JP'}]) + shell('ja', '/category-index.html', '/en/category-index.html', breadcrumbs([('ホーム', '/'), ('カテゴリ別ページ一覧', '/category-index.html')]), 'カテゴリ別ページ一覧', 'フィールド曲・戦闘曲・街村・エンディング・メドレーをカテゴリ別にまとめています。', metric('カテゴリ数', str(len(CATS) - 1)) + metric('言語', '日本語 / English') + metric('目的', 'カテゴリ検索の入口'), action('/series-index.html', '作品別ページも見る', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True), playlist_cards(medley_playlists[:2], 'ja', hero=True), section('Categories', 'カテゴリ別ページ', entry_grid(ja_cat_cards), 'フィールド曲や戦闘曲などの探し方に対応しています。') + section('BGM', '作業用BGM', entry_grid(ja_bgm_cards), 'メドレーを作業用BGM向けにまとめています。')))
    write('en/category-index.html', make_head('en', 'Browse by Category | C-chan piano', 'Landing pages for opening themes, casino tracks, churches, battles, endings, and medleys.', BASE + '/en/category-index.html', BASE + '/category-index.html', BASE + '/en/category-index.html', [breadcrumb_json([('Home', '/en.html'), ('Browse by Category', '/en/category-index.html')]), {'@type': 'CollectionPage', 'name': 'Browse by Category', 'description': 'Category landing pages.', 'url': BASE + '/en/category-index.html', 'inLanguage': 'en-US'}]) + shell('en', '/en/category-index.html', '/category-index.html', breadcrumbs([('Home', '/en.html'), ('Browse by Category', '/en/category-index.html')]), 'Browse by Category', 'Opening themes, casino tracks, churches, battles, endings, and medleys.', metric('Categories', str(len(CATS) - 1)) + metric('Language', 'English / Japanese') + metric('Purpose', 'Search landing pages'), action('/en/series-index.html', 'Browse series', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'Visit YouTube', external=True), playlist_cards(medley_playlists[:2], 'en', hero=True), section('Categories', 'Category Pages', entry_grid(en_cat_cards), 'Built for clearer discovery across search intents.') + section('BGM', 'Background Listening', entry_grid(en_bgm_cards), 'Medley pages are grouped for background listening.')))

    urls.extend([BASE + '/series-index.html', BASE + '/en/series-index.html', BASE + '/category-index.html', BASE + '/en/category-index.html'])
    patch_home('index.html', 'ja', series_playlists)
    patch_home('en.html', 'en', series_playlists)
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>', encoding='utf-8')
    print('generated', len(urls), 'urls')


if __name__ == '__main__':
    build()
