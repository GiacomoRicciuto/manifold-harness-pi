#!/usr/bin/env python3
"""
Market Research PDF Designer
Transforms a raw markdown manifold brief into a McKinsey-level PDF document.
v3 — typography: 9.5pt body, 1.52 line-height (McKinsey/BCG enterprise standard)
"""

import sys
import re
import os
import subprocess
from pathlib import Path
from datetime import datetime

# ── THEME ENGINE ──────────────────────────────────────────────────────────────

THEMES = {
    "saas_tech": {
        "name": "SaaS / Tech / AI",
        "keywords": ["saas", "ai", "software", "app", "digital", "tech", "api", "platform",
                     "cloud", "vocal", "voce", "agente", "automatiz", "chatbot", "crm"],
        "primary": "#1A1F36", "accent": "#4F46E5", "accent2": "#818CF8",
        "accent3": "#C7D2FE", "text": "#1E293B", "light_bg": "#F1F5FF",
        "gradient_start": "#1A1F36", "gradient_end": "#312E81",
        "chapter_bg": "#0F172A", "font_display": "Space Grotesk",
        "font_body": "Inter", "deco_shape": "circuit", "stat_color": "#4F46E5",
    },
    "healthcare": {
        "name": "Healthcare / Medicina",
        "keywords": ["medic", "clinic", "salut", "pazient", "ospedale", "dottore", "dentist",
                     "odontoiatri", "farmac", "terapia", "diagnosi", "studio medico"],
        "primary": "#0F4C81", "accent": "#0EA5E9", "accent2": "#38BDF8",
        "accent3": "#BAE6FD", "text": "#1E293B", "light_bg": "#F0F9FF",
        "gradient_start": "#0F4C81", "gradient_end": "#0369A1",
        "chapter_bg": "#082F49", "font_display": "Playfair Display",
        "font_body": "Source Serif 4", "deco_shape": "cross", "stat_color": "#0EA5E9",
    },
    "real_estate": {
        "name": "Real Estate / Immobiliare",
        "keywords": ["immobil", "real estate", "agenzia immobiliare", "affitto", "vendita casa",
                     "mutuo", "appartamento", "terreno", "investimento immobiliare"],
        "primary": "#1C3A2E", "accent": "#10B981", "accent2": "#34D399",
        "accent3": "#A7F3D0", "text": "#1E293B", "light_bg": "#F0FDF4",
        "gradient_start": "#1C3A2E", "gradient_end": "#065F46",
        "chapter_bg": "#052E16", "font_display": "Cormorant Garamond",
        "font_body": "Lora", "deco_shape": "arch", "stat_color": "#10B981",
    },
    "legal": {
        "name": "Legal / Studi Legali",
        "keywords": ["legale", "avvocato", "studio legale", "notaio", "contratto", "giuridic",
                     "sentenza", "causa", "consulenza legale", "diritto"],
        "primary": "#2D2010", "accent": "#B45309", "accent2": "#D97706",
        "accent3": "#FDE68A", "text": "#1C1917", "light_bg": "#FFFBEB",
        "gradient_start": "#2D2010", "gradient_end": "#78350F",
        "chapter_bg": "#1C1107", "font_display": "Cormorant Garamond",
        "font_body": "EB Garamond", "deco_shape": "scale", "stat_color": "#B45309",
    },
    "beauty_wellness": {
        "name": "Beauty / Wellness / Estetica",
        "keywords": ["estetica", "beauty", "wellness", "parrucchiere", "spa", "centro estetico",
                     "massaggio", "trattamento", "bellezza", "cura del corpo"],
        "primary": "#4A1942", "accent": "#C026D3", "accent2": "#E879F9",
        "accent3": "#F5D0FE", "text": "#1E1B2E", "light_bg": "#FDF4FF",
        "gradient_start": "#4A1942", "gradient_end": "#86198F",
        "chapter_bg": "#2E1065", "font_display": "Playfair Display",
        "font_body": "Raleway", "deco_shape": "flower", "stat_color": "#C026D3",
    },
    "finance": {
        "name": "Finance / Consulenza Finanziaria",
        "keywords": ["finanza", "investimento", "consulente finanziario", "banca", "assicurazione",
                     "portafoglio", "rendimento", "risparmio", "fiscale", "commercialista"],
        "primary": "#0A2540", "accent": "#1570EF", "accent2": "#53B1FD",
        "accent3": "#B2DDFF", "text": "#101828", "light_bg": "#EFF8FF",
        "gradient_start": "#0A2540", "gradient_end": "#1D4ED8",
        "chapter_bg": "#020617", "font_display": "Libre Baskerville",
        "font_body": "IBM Plex Sans", "deco_shape": "chart", "stat_color": "#1570EF",
    },
    "restaurant_food": {
        "name": "Ristorazione / Food",
        "keywords": ["ristorante", "ristorazione", "catering", "food", "cucina", "chef",
                     "pizzeria", "bar", "osteria", "trattoria", "gastronomia"],
        "primary": "#3B0A00", "accent": "#DC2626", "accent2": "#F87171",
        "accent3": "#FEE2E2", "text": "#1C0A00", "light_bg": "#FFF5F5",
        "gradient_start": "#3B0A00", "gradient_end": "#991B1B",
        "chapter_bg": "#1C0A00", "font_display": "Playfair Display",
        "font_body": "Merriweather", "deco_shape": "leaf", "stat_color": "#DC2626",
    },
    "construction": {
        "name": "Edilizia / Costruzioni",
        "keywords": ["edilizia", "costruzione", "impresa edile", "geometra", "architetto",
                     "cantiere", "ristrutturazione", "idraulico", "elettricista", "muratore"],
        "primary": "#1C1917", "accent": "#EA580C", "accent2": "#FB923C",
        "accent3": "#FED7AA", "text": "#1C1917", "light_bg": "#FFF7ED",
        "gradient_start": "#1C1917", "gradient_end": "#7C2D12",
        "chapter_bg": "#0C0A09", "font_display": "Barlow",
        "font_body": "Barlow", "deco_shape": "grid", "stat_color": "#EA580C",
    },
    "default": {
        "name": "Business / PMI",
        "keywords": [],
        "primary": "#1E293B", "accent": "#3B82F6", "accent2": "#60A5FA",
        "accent3": "#BFDBFE", "text": "#1E293B", "light_bg": "#F8FAFC",
        "gradient_start": "#1E293B", "gradient_end": "#1D4ED8",
        "chapter_bg": "#0F172A", "font_display": "Inter",
        "font_body": "Inter", "deco_shape": "dots", "stat_color": "#3B82F6",
    }
}

ASCII_BOX_CHARS = set('┌┐└┘├┤┬┴┼─│╔╗╚╝╠╣╦╩╬═║▼▲►◄→←↑↓')


def detect_theme(content: str) -> dict:
    content_lower = content.lower()
    scores = {}
    for theme_key, theme in THEMES.items():
        if theme_key == "default":
            continue
        score = sum(1 for kw in theme["keywords"] if kw in content_lower)
        if score > 0:
            scores[theme_key] = score
    if not scores:
        return THEMES["default"]
    return THEMES[max(scores, key=scores.get)]


# ── MARKDOWN PARSER ───────────────────────────────────────────────────────────

def parse_markdown(content: str) -> dict:
    lines = content.split('\n')
    doc_title = ""
    doc_subtitle = ""
    doc_market = ""
    doc_date = datetime.now().strftime("%B %Y")

    for line in lines[:20]:
        if line.startswith('# ') and not re.match(r'^#\s+CAPITOLO', line) and not doc_title:
            doc_title = line[2:].strip()
        if ('— ' in line or '– ' in line) and not doc_subtitle:
            doc_subtitle = line.strip().lstrip('#').strip()
        if 'Mercato' in line and not doc_market:
            doc_market = line.strip().lstrip('#').strip()

    chapters = []
    current_chapter = None
    current_content = []

    for line in lines:
        chap_match = re.match(r'^#\s+CAPITOLO\s+(\d+)\s*[—–-]\s*(.+)', line)
        if chap_match:
            if current_chapter is not None:
                current_chapter['content'] = '\n'.join(current_content)
                chapters.append(current_chapter)
            num = chap_match.group(1).zfill(2)
            title = chap_match.group(2).strip()
            # Strip trailing metadata like "# FINE CAPITOLO ..."
            if re.match(r'FINE\s+CAPITOLO', title, re.IGNORECASE):
                current_chapter = None
                current_content = []
                continue
            current_chapter = {'number': num, 'title': title, 'content': ''}
            current_content = []
        else:
            # Skip "# FINE CAPITOLO" lines
            if re.match(r'^#\s+FINE\s+CAPITOLO', line):
                continue
            if current_chapter is not None:
                current_content.append(line)

    if current_chapter is not None:
        current_chapter['content'] = '\n'.join(current_content)
        chapters.append(current_chapter)

    return {
        'title': doc_title or "Market Research Brief",
        'subtitle': doc_subtitle or "",
        'market': doc_market or "",
        'date': doc_date,
        'chapters': chapters,
        'raw': content,
    }


# ── CONTENT FORMATTER ─────────────────────────────────────────────────────────

# Sentinel for protected blocks
_BLOCK_SENTINEL = "XXXXXXPROTECTEDBLOCKXXXXXX"


def is_ascii_diagram(text: str) -> bool:
    """Check if a code block contains ASCII box-drawing art."""
    return any(c in ASCII_BOX_CHARS for c in text)


def render_ascii_map(text: str, theme: dict) -> str:
    """Render ASCII/box-drawing diagram as a styled visual card."""
    a = theme["accent"]
    a3 = theme["accent3"]
    p = theme["primary"]
    lbg = theme["light_bg"]
    fb = theme["font_body"]

    # Detect a title from the first non-empty line if it looks like a label
    lines = text.strip().split('\n')
    # Replace HTML special chars
    safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return f'''<div class="diagram-card">
    <div class="diagram-body"><pre class="diagram-pre">{safe}</pre></div>
</div>'''


def extract_code_blocks(text: str, theme: dict):
    """
    Extract ``` blocks, replace with sentinels, return (modified_text, replacements_dict).
    ASCII diagrams get special HTML rendering; code blocks get plain code styling.
    """
    replacements = {}
    counter = [0]

    def replacer(m):
        lang = m.group(1).strip()
        body = m.group(2)
        idx = counter[0]
        counter[0] += 1
        key = f"{_BLOCK_SENTINEL}{idx}{_BLOCK_SENTINEL}"

        if is_ascii_diagram(body):
            replacements[key] = render_ascii_map(body, theme)
        else:
            safe = body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            replacements[key] = f'<div class="code-block"><pre><code>{safe}</code></pre></div>'

        return key

    modified = re.sub(r'```([^\n]*)\n([\s\S]*?)```', replacer, text)
    return modified, replacements


def convert_tables(text: str, theme: dict) -> str:
    """Convert markdown tables to styled HTML. Applied BEFORE inline markdown processing."""
    p = theme["primary"]
    a3 = theme["accent3"]
    gstart = theme["gradient_start"]
    gend = theme["gradient_end"]

    table_pattern = re.compile(
        r'(?:^|\n)(\|.+\|[ \t]*\n\|[-| :\t]+\|[ \t]*\n(?:\|.+\|[ \t]*\n?)+)',
        re.MULTILINE
    )

    def table_replacer(match):
        raw = match.group(1) if match.lastindex else match.group(0)
        rows = [r.strip() for r in raw.strip().split('\n')]
        if len(rows) < 2:
            return match.group(0)

        header_cells = [c.strip() for c in rows[0].strip('|').split('|')]
        # rows[1] is separator — skip
        data_rows = rows[2:]

        thead = '<thead><tr>' + ''.join(
            f'<th>{apply_inline_md(c)}</th>' for c in header_cells
        ) + '</tr></thead>'

        tbody_rows = []
        for row in data_rows:
            row = row.strip()
            if not row or not row.startswith('|'):
                continue
            cells = [c.strip() for c in row.strip('|').split('|')]
            tbody_rows.append(
                '<tr>' + ''.join(f'<td>{apply_inline_md(c)}</td>' for c in cells) + '</tr>'
            )
        tbody = '<tbody>' + ''.join(tbody_rows) + '</tbody>'

        return f'\n<div class="table-wrapper"><table>{thead}{tbody}</table></div>\n'

    return table_pattern.sub(table_replacer, text)


def apply_inline_md(text: str) -> str:
    """Apply bold and italic only — safe to call on table cells."""
    # Bold
    text = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', text)
    return text


def format_content_to_html(md_text: str, theme: dict) -> str:
    """
    Convert markdown body to styled HTML.
    Order matters:
      1. Extract code/diagram blocks → sentinels
      2. Convert markdown tables → HTML (BEFORE inline regex touches cell content)
      3. Apply headings
      4. Apply blockquote/stat-quote regex (now safe: tables already HTML)
      5. Apply bold/italic
      6. Convert lists
      7. Paragraphs
      8. Restore sentinels
    """
    html, code_replacements = extract_code_blocks(md_text, theme)

    # Step 2: Tables (before inline processing)
    html = convert_tables(html, theme)

    # Step 3: Headings
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

    # Step 4: Stat quotes — "text" — source (only in non-table, non-sentinel text)
    html = re.sub(
        r'"([^"\n]{10,})"[ \t]*([—–-][ \t]*[^\n\r]+)',
        lambda m: (
            f'<blockquote class="stat-quote">'
            f'<span class="quote-text">&#8220;{m.group(1)}&#8221;</span>'
            f'<cite>{m.group(2).strip(" —–-").strip()}</cite>'
            f'</blockquote>'
        ),
        html
    )

    # Step 5: Bold / Italic
    html = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', html)

    # Step 5b: Horizontal rules
    html = re.sub(r'^---+$', r'<hr class="section-divider">', html, flags=re.MULTILINE)

    # Step 6: Unordered lists
    html = convert_ul(html)
    # Ordered lists
    html = convert_ol(html)

    # Step 7: Paragraphs
    paragraphs = re.split(r'\n\n+', html)
    formatted = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Block elements — don't wrap
        if para.startswith(('<h', '<ul', '<ol', '<blockquote', '<hr', '<table',
                            '<div', _BLOCK_SENTINEL)):
            formatted.append(para)
        elif re.match(r'^' + re.escape(_BLOCK_SENTINEL), para):
            formatted.append(para)
        else:
            # Stat callout: short lines with key figures
            stripped = re.sub(r'<[^>]+>', '', para)
            if re.search(r'(\d+[%€]|\€\s*\d+|\d+\s*euro)', stripped) and len(stripped) < 300:
                formatted.append(f'<p class="stat-callout">{para}</p>')
            else:
                formatted.append(f'<p>{para}</p>')

    result = '\n'.join(formatted)

    # Step 8: Restore sentinels
    for key, replacement in code_replacements.items():
        result = result.replace(key, replacement)

    return result


def convert_ul(html: str) -> str:
    lines = html.split('\n')
    result = []
    in_list = False
    for line in lines:
        if re.match(r'^[-*•]\s+', line):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*•]\s+', '', line)
            result.append(f'<li>{apply_inline_md(item)}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ul>')
    return '\n'.join(result)


def convert_ol(html: str) -> str:
    lines = html.split('\n')
    result = []
    in_list = False
    for line in lines:
        if re.match(r'^\d+\.\s+', line):
            if not in_list:
                result.append('<ol>')
                in_list = True
            item = re.sub(r'^\d+\.\s+', '', line)
            result.append(f'<li>{apply_inline_md(item)}</li>')
        else:
            if in_list:
                result.append('</ol>')
                in_list = False
            result.append(line)
    if in_list:
        result.append('</ol>')
    return '\n'.join(result)


# ── SVG DECORATIONS ───────────────────────────────────────────────────────────

def get_deco_svg(shape: str, color: str, opacity: float = 0.15) -> str:
    svgs = {
        "circuit": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g stroke="{color}" stroke-width="1.5" fill="none" opacity="{opacity}">
                <circle cx="200" cy="200" r="150"/><circle cx="200" cy="200" r="100"/>
                <circle cx="200" cy="200" r="50"/>
                <line x1="50" y1="200" x2="350" y2="200"/>
                <line x1="200" y1="50" x2="200" y2="350"/>
                <line x1="94" y1="94" x2="306" y2="306"/>
                <line x1="306" y1="94" x2="94" y2="306"/>
                <circle cx="200" cy="50" r="8" fill="{color}"/>
                <circle cx="350" cy="200" r="8" fill="{color}"/>
                <circle cx="200" cy="350" r="8" fill="{color}"/>
                <circle cx="50" cy="200" r="8" fill="{color}"/>
                <rect x="185" y="185" width="30" height="30" fill="{color}" opacity="0.4"/>
            </g></svg>''',
        "dots": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g fill="{color}" opacity="{opacity}">
                {''.join(f'<circle cx="{x*40+20}" cy="{y*40+20}" r="3"/>'
                         for x in range(10) for y in range(10))}
            </g></svg>''',
        "arch": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g stroke="{color}" stroke-width="2" fill="none" opacity="{opacity}">
                <path d="M50,350 Q200,50 350,350"/>
                <path d="M80,350 Q200,100 320,350"/>
                <path d="M110,350 Q200,150 290,350"/>
                <line x1="50" y1="350" x2="350" y2="350"/>
            </g></svg>''',
        "scale": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g stroke="{color}" stroke-width="2" fill="none" opacity="{opacity}">
                <line x1="200" y1="50" x2="200" y2="250"/>
                <line x1="80" y1="150" x2="320" y2="150"/>
                <circle cx="80" cy="250" r="60"/><circle cx="320" cy="250" r="60"/>
                <line x1="80" y1="150" x2="80" y2="250"/>
                <line x1="320" y1="150" x2="320" y2="250"/>
            </g></svg>''',
        "flower": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g fill="{color}" opacity="{opacity}">
                <circle cx="200" cy="130" r="50"/><circle cx="270" cy="165" r="50"/>
                <circle cx="270" cy="235" r="50"/><circle cx="200" cy="270" r="50"/>
                <circle cx="130" cy="235" r="50"/><circle cx="130" cy="165" r="50"/>
                <circle cx="200" cy="200" r="40" fill="white" opacity="0.5"/>
            </g></svg>''',
        "cross": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g fill="{color}" opacity="{opacity}">
                <rect x="160" y="60" width="80" height="280" rx="10"/>
                <rect x="60" y="160" width="280" height="80" rx="10"/>
                <circle cx="200" cy="200" r="40" fill="white" opacity="0.3"/>
            </g></svg>''',
        "chart": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g fill="{color}" opacity="{opacity}">
                <rect x="60" y="280" width="40" height="70"/>
                <rect x="120" y="220" width="40" height="130"/>
                <rect x="180" y="160" width="40" height="190"/>
                <rect x="240" y="100" width="40" height="250"/>
                <rect x="300" y="60" width="40" height="290"/>
                <line x1="50" y1="350" x2="360" y2="350" stroke="{color}" stroke-width="3" fill="none"/>
                <line x1="50" y1="50" x2="50" y2="360" stroke="{color}" stroke-width="3" fill="none"/>
            </g></svg>''',
        "grid": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g stroke="{color}" stroke-width="1" opacity="{opacity}">
                {''.join(f'<line x1="{x*40}" y1="0" x2="{x*40}" y2="400"/>' for x in range(11))}
                {''.join(f'<line x1="0" y1="{y*40}" x2="400" y2="{y*40}"/>' for y in range(11))}
            </g>
            <g fill="{color}" opacity="{opacity * 2}">
                <rect x="160" y="160" width="80" height="80" rx="4"/>
            </g></svg>''',
        "leaf": f'''<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" class="deco-svg">
            <g fill="{color}" opacity="{opacity}">
                <path d="M200,50 Q350,200 200,350 Q50,200 200,50 Z"/>
                <path d="M200,50 Q200,200 200,350" stroke="white" stroke-width="2" fill="none" opacity="0.5"/>
                <path d="M120,180 Q200,200 280,180" stroke="white" stroke-width="1.5" fill="none" opacity="0.4"/>
                <path d="M100,230 Q200,250 300,230" stroke="white" stroke-width="1.5" fill="none" opacity="0.4"/>
            </g></svg>''',
    }
    return svgs.get(shape, svgs["dots"])


# ── HTML GENERATOR ────────────────────────────────────────────────────────────

def generate_html(doc: dict, theme: dict) -> str:
    p = theme["primary"]
    a = theme["accent"]
    a2 = theme["accent2"]
    a3 = theme["accent3"]
    txt = theme["text"]
    lbg = theme["light_bg"]
    gstart = theme["gradient_start"]
    gend = theme["gradient_end"]
    cbg = theme["chapter_bg"]
    fd = theme["font_display"]
    fb = theme["font_body"]
    stat_color = theme["stat_color"]
    deco_shape = theme["deco_shape"]

    font_import = (
        f"https://fonts.googleapis.com/css2?"
        f"family={fd.replace(' ', '+')}:wght@400;600;700;900"
        f"&family={fb.replace(' ', '+')}:wght@300;400;500;600"
        f"&display=swap"
    )

    # Build chapters HTML
    chapters_html = ""
    for chap in doc['chapters']:
        body_html = format_content_to_html(chap['content'], theme)
        deco = get_deco_svg(deco_shape, "#FFFFFF", 0.08)
        deco_content = get_deco_svg(deco_shape, a, 0.07)

        chapters_html += f'''
<!-- CHAPTER COVER {chap["number"]} -->
<div class="chapter-cover" style="background:linear-gradient(135deg,{cbg} 0%,{gstart} 60%,{gend} 100%);">
  <div class="chapter-cover-deco">{deco}</div>
  <div class="chapter-cover-inner">
    <div class="chapter-label">CAPITOLO {chap["number"]}</div>
    <h1 class="chapter-title">{chap["title"]}</h1>
    <div class="chapter-accent-line"></div>
  </div>
  <div class="chapter-number-bg">{chap["number"]}</div>
</div>

<!-- CHAPTER CONTENT {chap["number"]} -->
<div class="chapter-content">
  <div class="chapter-content-deco">{deco_content}</div>
  <div class="chapter-header-band" style="background:linear-gradient(90deg,{a} 0%,transparent 100%);">
    <span class="chapter-header-label">CAP. {chap["number"]} — {chap["title"]}</span>
  </div>
  <div class="chapter-body">
    {body_html}
  </div>
</div>

<!-- CHAPTER END {chap["number"]} -->
<div class="chapter-end" style="background:linear-gradient(180deg,{lbg} 0%,{a3} 100%);">
  <div class="chapter-end-inner">
    <div class="chapter-end-line" style="background:{a};"></div>
    <span class="chapter-end-label" style="color:{a};">Fine Capitolo {chap["number"]}</span>
    <div class="chapter-end-line" style="background:{a};"></div>
  </div>
  <div class="chapter-end-deco">{get_deco_svg(deco_shape, a, 0.12)}</div>
</div>
'''

    # TOC
    toc_items = ""
    for chap in doc['chapters']:
        toc_items += f'''
<div class="toc-item">
  <span class="toc-num" style="color:{a};">{chap["number"]}</span>
  <span class="toc-title">{chap["title"]}</span>
</div>'''

    cover_deco = get_deco_svg(deco_shape, "#FFFFFF", 0.06)

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>{doc["title"]}</title>
<link href="{font_import}" rel="stylesheet">
<style>
/* ── RESET ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── PAGE SETUP with proper margins ── */
@page {{
  size: A4;
  margin: 18mm 20mm 20mm 20mm;
}}

/* Full-bleed pages (covers) override margin */
@page cover {{
  margin: 0;
}}

@page chapter-cover-page {{
  margin: 0;
}}

body {{
  font-family: '{fb}', 'Helvetica Neue', sans-serif;
  font-size: 9.5pt;
  line-height: 1.52;
  color: {txt};
  background: white;
}}

/* ── FULL-BLEED COVER PAGES ── */
.main-cover,
.chapter-cover,
.chapter-end {{
  /* Bleed to compensate for page margin */
  margin: -18mm -20mm -20mm -20mm;
  padding: 18mm 20mm 20mm 20mm;
  page-break-before: always;
  page-break-after: always;
  page-break-inside: avoid;
  position: relative;
  overflow: hidden;
}}

/* ── MAIN COVER ── */
.main-cover {{
  min-height: 297mm;
  background: linear-gradient(150deg, {gstart} 0%, {p} 40%, {gend} 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 50mm 22mm 22mm 22mm;
}}

.main-cover-deco {{
  position: absolute; top: -40mm; right: -40mm;
  width: 140mm; height: 140mm;
}}
.main-cover-deco2 {{
  position: absolute; bottom: -20mm; left: -30mm;
  width: 100mm; height: 100mm;
}}

.cover-top-bar {{
  width: 20mm; height: 2px;
  background: {a2}; margin-bottom: 8mm;
}}
.cover-market-label {{
  font-family: '{fb}', sans-serif;
  font-size: 8pt; font-weight: 500;
  letter-spacing: 3px; text-transform: uppercase;
  color: {a2}; margin-bottom: 6mm;
}}
.cover-title {{
  font-family: '{fd}', Georgia, serif;
  font-size: 26pt; font-weight: 700;
  color: #FFFFFF; line-height: 1.2;
  margin-bottom: 6mm; max-width: 150mm;
}}
.cover-subtitle {{
  font-family: '{fb}', sans-serif;
  font-size: 10pt; font-weight: 300;
  color: rgba(255,255,255,0.75); line-height: 1.5;
  max-width: 130mm; margin-bottom: 15mm;
}}
.cover-accent-bar {{
  width: 30mm; height: 3px;
  background: linear-gradient(90deg, {a}, transparent);
  margin-bottom: 15mm;
}}
.cover-meta {{ display: flex; flex-direction: column; gap: 2mm; }}
.cover-meta-item {{
  font-size: 8pt; color: rgba(255,255,255,0.55);
  letter-spacing: 1px; text-transform: uppercase;
}}
.cover-bottom {{ display: flex; justify-content: space-between; align-items: flex-end; }}
.cover-badge {{
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  padding: 2mm 5mm; border-radius: 2mm;
  font-size: 7pt; color: rgba(255,255,255,0.7);
  letter-spacing: 1.5px; text-transform: uppercase;
}}

/* ── TABLE OF CONTENTS ── */
.toc-page {{
  page-break-before: always;
  page-break-after: always;
}}
.toc-header {{
  margin-bottom: 10mm; padding-bottom: 4mm;
  border-bottom: 2px solid {a3};
}}
.toc-label {{
  font-size: 7pt; letter-spacing: 4px;
  text-transform: uppercase; color: {a}; margin-bottom: 2mm;
}}
.toc-title-main {{
  font-family: '{fd}', Georgia, serif;
  font-size: 20pt; font-weight: 700; color: {p};
}}
.toc-item {{
  display: flex; align-items: baseline;
  padding: 3.5mm 0; border-bottom: 1px solid {a3}; gap: 4mm;
}}
.toc-num {{
  font-family: '{fd}', monospace;
  font-size: 9pt; font-weight: 700; min-width: 10mm; color: {a};
}}
.toc-title {{
  font-family: '{fb}', sans-serif;
  font-size: 9.5pt; color: {txt}; font-weight: 500; flex: 1;
}}

/* ── CHAPTER COVER ── */
.chapter-cover {{
  min-height: 297mm;
  display: flex; flex-direction: column;
  justify-content: center; align-items: flex-start;
  padding: 40mm 24mm;
}}
.chapter-cover-deco {{
  position: absolute; top: 0; right: 0;
  width: 120mm; height: 120mm;
}}
.chapter-cover-inner {{ position: relative; z-index: 2; max-width: 145mm; }}
.chapter-label {{
  font-family: '{fb}', sans-serif;
  font-size: 8pt; font-weight: 600; letter-spacing: 5px;
  text-transform: uppercase; color: {a2}; margin-bottom: 6mm;
}}
.chapter-title {{
  font-family: '{fd}', Georgia, serif;
  font-size: 28pt; font-weight: 700;
  color: #FFFFFF; line-height: 1.15; margin-bottom: 8mm;
}}
.chapter-accent-line {{
  width: 25mm; height: 3px;
  background: linear-gradient(90deg, {a}, transparent);
}}
.chapter-number-bg {{
  position: absolute; bottom: -10mm; right: 5mm;
  font-family: '{fd}', Georgia, serif;
  font-size: 180pt; font-weight: 900;
  color: rgba(255,255,255,0.04); line-height: 1;
  user-select: none; z-index: 1;
}}

/* ── CHAPTER CONTENT ── */
.chapter-content {{
  page-break-before: avoid;
}}
.chapter-content-deco {{
  position: absolute; top: 0; right: 0;
  width: 55mm; height: 55mm;
  pointer-events: none; opacity: 0.5;
}}
.chapter-header-band {{
  height: 7mm; margin-bottom: 7mm;
  display: flex; align-items: center;
  padding-left: 4mm;
  margin-left: -20mm; margin-right: -20mm;
  margin-top: -18mm;
  padding-left: 20mm;
}}
.chapter-header-label {{
  font-family: '{fb}', sans-serif;
  font-size: 7pt; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  color: rgba(255,255,255,0.9);
}}
.chapter-body {{ position: relative; z-index: 2; }}

/* ── TYPOGRAPHY ── */
h2 {{
  font-family: '{fd}', Georgia, serif;
  font-size: 13pt; font-weight: 700; color: {p};
  margin: 7mm 0 3mm 0;
  padding-bottom: 1.5mm; border-bottom: 2px solid {a3};
  page-break-after: avoid;
}}
h3 {{
  font-family: '{fd}', Georgia, serif;
  font-size: 10.5pt; font-weight: 600; color: {a};
  margin: 5mm 0 2mm 0; page-break-after: avoid;
}}
h4 {{
  font-family: '{fb}', sans-serif;
  font-size: 8.5pt; font-weight: 700; color: {txt};
  margin: 4mm 0 1.5mm 0;
  text-transform: uppercase; letter-spacing: 1px;
  page-break-after: avoid;
}}
p {{ margin-bottom: 2.5mm; text-align: justify; hyphens: auto; }}
strong {{ font-weight: 700; color: {p}; }}
em {{ font-style: italic; color: #555; }}

/* ── STAT CALLOUT ── */
p.stat-callout {{
  background: {lbg}; border-left: 4px solid {a};
  padding: 2mm 4mm; border-radius: 0 2mm 2mm 0;
  font-weight: 500; color: {p}; font-size: 9pt;
  margin: 4mm 0;
}}

/* ── BLOCKQUOTE / STAT QUOTE ── */
blockquote.stat-quote {{
  margin: 4mm 0; padding: 3mm 5mm 3mm 9mm;
  background: {lbg}; border-radius: 0 2mm 2mm 0;
  border-left: 4px solid {stat_color};
  position: relative; page-break-inside: avoid;
}}
blockquote.stat-quote::before {{
  content: '\\201C';
  font-family: '{fd}', Georgia, serif;
  font-size: 30pt; color: {a3};
  position: absolute; top: -2mm; left: 2mm;
  line-height: 1;
}}
.quote-text {{
  display: block; font-style: italic;
  color: {p}; font-size: 9pt; font-weight: 500;
  margin-bottom: 1.5mm;
}}
cite {{
  display: block; font-size: 7pt; color: {a};
  text-align: right; font-style: normal;
  font-weight: 600; letter-spacing: 0.5px;
}}

/* ── LISTS ── */
ul, ol {{ margin: 2mm 0 4mm 5mm; padding-left: 4mm; }}
li {{ margin-bottom: 1.5mm; line-height: 1.5; }}
ul li::marker {{ color: {a}; font-size: 11pt; }}
ol li::marker {{ color: {a}; font-weight: 700; }}

/* ── TABLES ── */
.table-wrapper {{
  margin: 6mm 0; overflow: hidden;
  border-radius: 3mm;
  box-shadow: 0 2px 10px rgba(0,0,0,0.10);
  page-break-inside: auto;   /* allow multi-page split */
}}
table {{
  width: 100%; border-collapse: collapse; font-size: 8pt;
}}
thead {{
  background: linear-gradient(135deg, {p}, {gend});
  display: table-header-group;
}}
thead th {{
  color: white; font-family: '{fb}', sans-serif;
  font-weight: 600; padding: 2mm 3.5mm;
  text-align: left; letter-spacing: 0.4px;
  font-size: 7.5pt; vertical-align: top;
}}
tbody tr {{ page-break-inside: avoid; }}
tbody tr:nth-child(even) {{ background: {lbg}; }}
tbody tr:nth-child(odd) {{ background: white; }}
tbody td {{
  padding: 2mm 3.5mm;
  border-bottom: 1px solid {a3};
  line-height: 1.45; vertical-align: top;
}}
tbody td:first-child {{ font-weight: 600; color: {p}; }}

/* ── ASCII DIAGRAM CARD ── */
.diagram-card {{
  margin: 7mm 0;
  background: {lbg};
  border: 1px solid {a3};
  border-left: 5px solid {a};
  border-radius: 0 4mm 4mm 0;
  padding: 5mm 6mm;
  page-break-inside: avoid;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}}
.diagram-pre {{
  font-family: 'Courier New', 'Lucida Console', monospace;
  font-size: 8pt; line-height: 1.4;
  color: {p}; white-space: pre;
  overflow-x: hidden; word-wrap: break-word;
}}

/* ── CODE BLOCK ── */
.code-block {{
  margin: 5mm 0;
  background: #1E293B;
  border-radius: 3mm; padding: 4mm 5mm;
  page-break-inside: avoid;
}}
.code-block pre {{ margin: 0; }}
.code-block code {{
  font-family: 'Courier New', monospace;
  font-size: 8pt; color: #E2E8F0; line-height: 1.55;
}}

/* ── SECTION DIVIDER ── */
hr.section-divider {{
  border: none; height: 1px;
  background: linear-gradient(90deg, transparent, {a2}, transparent);
  margin: 7mm 0;
}}

/* ── CHAPTER END ── */
.chapter-end {{
  min-height: 60mm;
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
}}
.chapter-end-inner {{
  display: flex; align-items: center;
  gap: 5mm; z-index: 2; position: relative;
}}
.chapter-end-line {{ width: 30mm; height: 1px; }}
.chapter-end-label {{
  font-family: '{fb}', sans-serif;
  font-size: 8pt; letter-spacing: 3px; text-transform: uppercase;
}}
.chapter-end-deco {{
  position: absolute; bottom: -15mm; right: -15mm;
  width: 70mm; height: 70mm; pointer-events: none;
}}

.deco-svg {{ width: 100%; height: 100%; }}

/* ── PAGE NUMBERS ── */
@page {{
  @bottom-center {{
    content: counter(page);
    font-family: '{fb}', sans-serif;
    font-size: 8pt; color: {a};
  }}
  @bottom-right {{
    content: "{doc["title"][:40]}";
    font-family: '{fb}', sans-serif;
    font-size: 7pt; color: {a3};
    letter-spacing: 0.5px;
  }}
}}
</style>
</head>
<body>

<!-- ═══ MAIN COVER ═══ -->
<div class="main-cover">
  <div class="main-cover-deco">{get_deco_svg(deco_shape, "#FFFFFF", 0.04)}</div>
  <div class="main-cover-deco2">{get_deco_svg(deco_shape, a2, 0.04)}</div>
  <div>
    <div class="cover-top-bar"></div>
    <div class="cover-market-label">{doc["market"] or "Market Research Brief"}</div>
    <h1 class="cover-title">{doc["title"]}</h1>
    <div class="cover-subtitle">{doc["subtitle"]}</div>
    <div class="cover-accent-bar"></div>
    <div class="cover-meta">
      <span class="cover-meta-item">Documento Riservato · {doc["date"]}</span>
      <span class="cover-meta-item">Ricerca di Mercato Professionale · {len(doc["chapters"])} Capitoli</span>
    </div>
  </div>
  <div class="cover-bottom">
    <div class="cover-badge">Confidential Research Report</div>
    <div class="cover-badge">&copy; {datetime.now().year} — All Rights Reserved</div>
  </div>
</div>

<!-- ═══ TABLE OF CONTENTS ═══ -->
<div class="toc-page">
  <div class="toc-header">
    <div class="toc-label">Indice dei Capitoli</div>
    <div class="toc-title-main">Sommario</div>
  </div>
  {toc_items}
</div>

<!-- ═══ CHAPTERS ═══ -->
{chapters_html}

</body>
</html>'''
    return html


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py <input.md> [output.pdf]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = (
        Path(sys.argv[2]) if len(sys.argv) > 2
        else input_path.with_name(input_path.stem + "_professional.pdf")
    )

    print(f"📖 Reading: {input_path}")
    content = input_path.read_text(encoding='utf-8')

    print("🎨 Detecting market theme...")
    theme = detect_theme(content)
    print(f"   Theme: {theme['name']}")

    print("📐 Parsing document structure...")
    doc = parse_markdown(content)
    print(f"   Title: {doc['title']}")
    print(f"   Chapters: {len(doc['chapters'])}")

    print("🖌  Generating themed HTML...")
    html = generate_html(doc, theme)

    html_path = output_path.with_suffix('.html')
    html_path.write_text(html, encoding='utf-8')
    print(f"   HTML saved: {html_path}")

    try:
        import weasyprint
        print("📄 Converting to PDF with WeasyPrint...")
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(output_path))
        html_path.unlink()
        print(f"\n✅ PDF created: {output_path}")
        return
    except ImportError:
        print("   WeasyPrint not found, trying alternatives...")
    except Exception as e:
        print(f"   WeasyPrint error: {e}")

    # Fallback: wkhtmltopdf
    try:
        result = subprocess.run(
            ['wkhtmltopdf', '--page-size', 'A4',
             '--margin-top', '18mm', '--margin-bottom', '20mm',
             '--margin-left', '20mm', '--margin-right', '20mm',
             '--enable-local-file-access', '--print-media-type',
             '--footer-center', '[page]', '--footer-font-size', '8',
             str(html_path), str(output_path)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            html_path.unlink()
            print(f"\n✅ PDF created: {output_path}")
            return
        print(f"   wkhtmltopdf error: {result.stderr[:300]}")
    except FileNotFoundError:
        pass

    print(f"\n⚠️  Delivered as HTML: {html_path}")
    print("Install WeasyPrint:  pip install weasyprint && brew install pango")


if __name__ == '__main__':
    main()
