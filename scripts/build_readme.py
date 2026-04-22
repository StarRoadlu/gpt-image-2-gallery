from pathlib import Path
import json
import html
from collections import Counter, defaultdict

base = Path(__file__).resolve().parent.parent
items = json.loads((base / 'data' / 'items.json').read_text(encoding='utf-8'))

cat_names = {
    'poster': '海报 / Poster',
    'ui': 'UI / 界面',
    'infographic': '信息图 / Infographic',
    'game': '游戏 / Character / Scene',
    'product': '产品 / Product',
    'portrait': '人物 / Portrait',
    'other': '其他 / Other',
}
order = ['poster', 'ui', 'infographic', 'game', 'product', 'portrait', 'other']

cats = defaultdict(list)
for item in items:
    cats[item['category']].append(item)

repo_counter = Counter(item.get('repo_source', 'Unknown') for item in items)
featured = items[:6]
recent_pick = items[6:12]


def esc(value: str) -> str:
    return html.escape(value or '')


def short_prompt(text: str, limit: int = 900) -> str:
    text = (text or '').strip()
    if len(text) <= limit:
        return text
    return text[:limit] + '...'


def meta_line(item: dict, compact: bool = False) -> str:
    parts = []
    if item.get('repo_source') and not compact:
        parts.append(f'来源仓库：`{item["repo_source"]}`')
    if item.get('author'):
        if item.get('author_url'):
            parts.append(f'作者：[{item["author"]}]({item["author_url"]})')
        else:
            parts.append(f'作者：{item["author"]}')
    if item.get('source_url'):
        parts.append(f'[原链接]({item["source_url"]})')
    return ' · '.join(parts)


def card_cell(item: dict) -> str:
    title = esc(item['title'])
    img = esc(item['local_image'])
    meta = meta_line(item, compact=True)
    lines = [
        '<td width="50%" valign="top">',
        f'<a href="{img}"><img src="{img}" alt="{title}" width="100%"></a>',
        f'<b>{title}</b><br>',
    ]
    if meta:
        lines.append(f'<sub>{meta}</sub>')
    lines.append('</td>')
    return '\n'.join(lines)


parts = []
parts.append('# GPT-Image-2 Gallery')
parts.append('')
parts.append('<p align="center">')
parts.append('  <img src="images/other/gpt-image-2-prompts-cover-en.png" width="100%" alt="GPT-Image-2 Gallery Cover">')
parts.append('</p>')
parts.append('')
parts.append('一个直接看图、顺手抄 prompt、还能回跳原始来源的 GPT-Image-2 展示仓库。')
parts.append('')
parts.append('这里不讲复杂方法论，重点就是三件事：')
parts.append('- 看现成案例')
parts.append('- 找可复用 prompt')
parts.append('- 快速回到原始链接继续深挖')
parts.append('')
parts.append('## 快速概览')
parts.append('')
parts.append(f'- 案例总数：**{len(items)}**')
parts.append(f'- 分类数量：**{len(cats)}**')
parts.append(f'- 主要来源：**{len(repo_counter)}** 类')
parts.append('- 当前更偏展示型仓库：首页直接预览，分类往下翻，原链接都保留')
parts.append('')
parts.append('### 来源分布')
parts.append('')
for repo, count in repo_counter.most_common():
    parts.append(f'- `{repo}` · **{count}** 条')
parts.append('')
parts.append('### 分类导航')
parts.append('')
for cat in order:
    if cat in cats:
        parts.append(f'- [{cat_names.get(cat, cat)}](#{cat}) · **{len(cats[cat])}** 条')
parts.append('')
parts.append('## 首页精选')
parts.append('')
parts.append('<table>')
for i in range(0, len(featured), 2):
    row = featured[i:i+2]
    parts.append('<tr>')
    for item in row:
        parts.append(card_cell(item))
    if len(row) == 1:
        parts.append('<td width="50%"></td>')
    parts.append('</tr>')
parts.append('</table>')
parts.append('')
parts.append('## 再看 6 条')
parts.append('')
parts.append('<table>')
for i in range(0, len(recent_pick), 2):
    row = recent_pick[i:i+2]
    parts.append('<tr>')
    for item in row:
        parts.append(card_cell(item))
    if len(row) == 1:
        parts.append('<td width="50%"></td>')
    parts.append('</tr>')
parts.append('</table>')
parts.append('')
parts.append('---')
parts.append('')

for cat in order:
    if cat not in cats:
        continue
    parts.append(f'## {cat_names.get(cat, cat)}')
    parts.append(f'<a id="{cat}"></a>')
    parts.append('')
    parts.append(f'> 当前分类共 **{len(cats[cat])}** 条')
    parts.append('')
    for item in cats[cat]:
        title = esc(item['title'])
        img = esc(item['local_image'])
        parts.append(f'### {title}')
        parts.append(f'<p><img src="{img}" width="760" alt="{title}"></p>')
        meta = meta_line(item, compact=False)
        if meta:
            for seg in meta.split(' · '):
                parts.append(f'- {seg}')
            parts.append('')
        prompt = short_prompt(item.get('prompt', ''))
        if prompt:
            parts.append('**Prompt**')
            parts.append('```text')
            parts.append(prompt)
            parts.append('```')
            parts.append('')
    parts.append('---')
    parts.append('')

(base / 'README.md').write_text('\n'.join(parts).strip() + '\n', encoding='utf-8')
print(f'generated README with {len(items)} items')
