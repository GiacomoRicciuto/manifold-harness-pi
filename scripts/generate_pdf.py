#!/usr/bin/env python3
"""
Manifold PDF Designer v4
========================
Transforms avatar_manifold.txt into an exceptionally beautiful, colorful,
easy-to-read professional PDF document.

Designed for the specific manifold format with:
- CAPITOLO headers between ═══ decorative lines
- SEZIONE headers between ━━━ decorative lines
- ## Subsection headers
- > Blockquotes with — attribution
- → Arrow emotion/insight items
- **Bold** paragraph openers and inline emphasis
- DATI/DATO callout blocks
- Fonte: source citations
- ASCII box-drawing tables (┌│└ etc.)
- ✓ Checkmark lists
- [N.N] Numbered belief items
- ───── thin dividers
- CLUSTER/CATENA/PATTERN section labels
- A.01 — "Title" pattern entries
- FRASE ESATTA / FREQUENZA / ANALISI sub-labels
"""

import sys
import re
import html as html_mod
from pathlib import Path
from datetime import datetime

# ── THEME ENGINE ──────────────────────────────────────────────────────────────

THEMES = {
    "gaming_retro": {
        "name": "Gaming / Retro / Collezionismo",
        "keywords": ["videogioc", "retrogam", "gaming", "console", "nintendo", "playstation",
                     "snes", "nes", "game boy", "ps3", "vinted", "ebay", "collezion",
                     "cartuccia", "retro", "flipper", "giochi", "gioco"],
        "primary": "#1B1040",
        "accent": "#7C3AED",
        "accent2": "#A78BFA",
        "accent3": "#DDD6FE",
        "warm": "#F59E0B",
        "warm_light": "#FEF3C7",
        "danger": "#EF4444",
        "danger_light": "#FEE2E2",
        "success": "#10B981",
        "success_light": "#D1FAE5",
        "info": "#3B82F6",
        "info_light": "#DBEAFE",
        "text": "#1E293B",
        "text_light": "#64748B",
        "light_bg": "#F5F3FF",
        "light_bg2": "#FDF4FF",
        "gradient_start": "#1B1040",
        "gradient_mid": "#312E81",
        "gradient_end": "#5B21B6",
        "chapter_bg": "#0F0A2A",
        "font_display": "Space Grotesk",
        "font_body": "Inter",
        "stat_color": "#7C3AED",
    },
    "saas_tech": {
        "name": "SaaS / Tech / AI",
        "keywords": ["saas", "ai", "software", "app", "digital", "tech", "api", "platform",
                     "cloud", "vocal", "voce", "agente", "automatiz", "chatbot", "crm"],
        "primary": "#1A1F36", "accent": "#4F46E5", "accent2": "#818CF8",
        "accent3": "#C7D2FE", "warm": "#F59E0B", "warm_light": "#FEF3C7",
        "danger": "#EF4444", "danger_light": "#FEE2E2",
        "success": "#10B981", "success_light": "#D1FAE5",
        "info": "#3B82F6", "info_light": "#DBEAFE",
        "text": "#1E293B", "text_light": "#64748B",
        "light_bg": "#F1F5FF", "light_bg2": "#F8FAFC",
        "gradient_start": "#1A1F36", "gradient_mid": "#1E3A5F",
        "gradient_end": "#312E81",
        "chapter_bg": "#0F172A", "font_display": "Space Grotesk",
        "font_body": "Inter", "stat_color": "#4F46E5",
    },
    "default": {
        "name": "Business / PMI",
        "keywords": [],
        "primary": "#1E293B", "accent": "#3B82F6", "accent2": "#60A5FA",
        "accent3": "#BFDBFE", "warm": "#F59E0B", "warm_light": "#FEF3C7",
        "danger": "#EF4444", "danger_light": "#FEE2E2",
        "success": "#10B981", "success_light": "#D1FAE5",
        "info": "#3B82F6", "info_light": "#DBEAFE",
        "text": "#1E293B", "text_light": "#64748B",
        "light_bg": "#F8FAFC", "light_bg2": "#F1F5F9",
        "gradient_start": "#1E293B", "gradient_mid": "#1E3A5F",
        "gradient_end": "#1D4ED8",
        "chapter_bg": "#0F172A", "font_display": "Inter",
        "font_body": "Inter", "stat_color": "#3B82F6",
    }
}


def detect_theme(content: str) -> dict:
    content_lower = content.lower()
    scores = {}
    for key, theme in THEMES.items():
        if key == "default":
            continue
        score = sum(1 for kw in theme["keywords"] if kw in content_lower)
        if score > 0:
            scores[key] = score
    if not scores:
        return THEMES["default"]
    return THEMES[max(scores, key=scores.get)]


# ── DOCUMENT PARSER ───────────────────────────────────────────────────────────

def parse_document(content: str) -> dict:
    """Parse the manifold into structured chapters."""
    lines = content.split('\n')

    # Extract header info from first ~20 lines
    doc_title = ""
    doc_subtitle = ""
    doc_market = ""
    doc_date = datetime.now().strftime("%B %Y")

    for line in lines[:20]:
        stripped = line.strip().lstrip('#').strip()
        if line.startswith('# ') and not re.match(r'^#\s*CAPITOLO', line, re.I) and not doc_title:
            doc_title = line[2:].strip()
        if ('— ' in line or '– ' in line) and 'Ricerca' in line and not doc_subtitle:
            doc_subtitle = stripped
        if re.match(r'^#?\s*Mercato:', line, re.I) and not doc_market:
            doc_market = stripped.split(':', 1)[-1].strip() if ':' in stripped else stripped

    # Parse chapters
    chapters = []
    current_chapter = None
    current_lines = []
    chapter_re = re.compile(r'^#?\s*CAPITOLO\s+(\d+)\s*[—–-]\s*(.+)', re.I)
    sep_heavy = re.compile(r'^[═]{10,}$')

    for i, line in enumerate(lines):
        m = chapter_re.match(line.strip())
        if m:
            if current_chapter is not None:
                current_chapter['raw_lines'] = current_lines
                chapters.append(current_chapter)
            num = m.group(1).zfill(2)
            title = m.group(2).strip()
            # Read the subtitle line (next non-separator, non-empty line)
            subtitle = ""
            for j in range(i+1, min(i+5, len(lines))):
                lj = lines[j].strip()
                if lj and not sep_heavy.match(lj) and not chapter_re.match(lj):
                    subtitle = lj
                    break
            current_chapter = {'number': num, 'title': title, 'subtitle': subtitle, 'raw_lines': []}
            current_lines = []
        else:
            # Skip heavy separators at chapter boundaries
            if sep_heavy.match(line.strip()) and current_chapter is not None and len(current_lines) < 8:
                continue
            if current_chapter is not None:
                current_lines.append(line)

    if current_chapter is not None:
        current_chapter['raw_lines'] = current_lines
        chapters.append(current_chapter)

    return {
        'title': doc_title or "AI Manifold Brief",
        'subtitle': doc_subtitle or "",
        'market': doc_market or "",
        'date': doc_date,
        'chapters': chapters,
    }


# ── CONTENT TO HTML CONVERTER ─────────────────────────────────────────────────

def esc(text: str) -> str:
    """HTML-escape text."""
    return html_mod.escape(text)


def inline_md(text: str) -> str:
    """Apply inline markdown: bold, italic."""
    text = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', text)
    return text


def convert_chapter_content(raw_lines: list, theme: dict) -> str:
    """Convert raw chapter lines into beautiful HTML."""
    t = theme
    blocks = []
    i = 0
    lines = raw_lines

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # ── SECTION HEADER (━━━ ... SEZIONE N — Title ... ━━━) ──
        if re.match(r'^[━]{10,}$', stripped):
            # Collect section header block
            header_lines = []
            i += 1
            while i < len(lines) and not re.match(r'^[━]{10,}$', lines[i].strip()):
                if lines[i].strip():
                    header_lines.append(lines[i].strip())
                i += 1
            i += 1  # skip closing ━━━
            if header_lines:
                main_title = header_lines[0] if header_lines else ""
                sub_lines = header_lines[1:] if len(header_lines) > 1 else []
                subtitle_html = '<br>'.join(esc(s) for s in sub_lines) if sub_lines else ""
                blocks.append(f'''<div class="section-header">
                    <div class="section-header-line"></div>
                    <h2 class="section-title">{esc(main_title)}</h2>
                    {"<p class='section-subtitle'>" + subtitle_html + "</p>" if subtitle_html else ""}
                </div>''')
            continue

        # ── THIN DIVIDER (─────) ──
        if re.match(r'^[─]{10,}$', stripped):
            blocks.append('<hr class="thin-divider">')
            i += 1
            continue

        # ── HEAVY SEPARATOR (═══) — skip remnants ──
        if re.match(r'^[═]{10,}$', stripped):
            i += 1
            continue

        # ── H2 HEADING (## ...) ──
        m = re.match(r'^##\s+(.+)$', stripped)
        if m:
            blocks.append(f'<h2 class="subsection-heading">{inline_md(esc(m.group(1)))}</h2>')
            i += 1
            continue

        # ── H3 HEADING (### ...) ──
        m = re.match(r'^###\s+(.+)$', stripped)
        if m:
            blocks.append(f'<h3>{inline_md(esc(m.group(1)))}</h3>')
            i += 1
            continue

        # ── ASCII ART / BOX-DRAWING BLOCK ──
        # Detect lines containing box-drawing characters (even if indented)
        box_chars = set('┌┐└┘├┤┬┴┼│╔╗╚╝╠╣╦╩╬║┃')
        if any(c in box_chars for c in stripped):
            art_lines = [line]
            i += 1
            # Collect all consecutive lines that are part of the diagram
            # (contain box chars, or are empty lines between box-char lines, or are indented text within)
            empty_streak = 0
            while i < len(lines):
                tl = lines[i]
                ts = tl.strip()
                has_box = any(c in box_chars for c in ts)
                if has_box:
                    # Add any skipped empty lines back
                    for _ in range(empty_streak):
                        art_lines.append('')
                    empty_streak = 0
                    art_lines.append(tl)
                    i += 1
                elif not ts:
                    empty_streak += 1
                    if empty_streak > 2:
                        break
                    i += 1
                else:
                    break
            # Decide: simple table (has header row with │ cells) vs complex diagram
            is_simple_table = (art_lines[0].strip().startswith('┌') and
                               sum(1 for l in art_lines if '│' in l and l.strip().startswith('│')) > 2)
            if is_simple_table:
                blocks.append(render_ascii_table(art_lines, theme))
            else:
                # Complex diagram — render as a styled card preserving layout
                blocks.append(render_ascii_diagram(art_lines, theme))
            continue

        # ── BLOCKQUOTE (> "quote") ──
        if stripped.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            quote_text = ' '.join(quote_lines)
            # Check next line for attribution (— source)
            attribution = ""
            if i < len(lines) and re.match(r'^[—–-]\s*', lines[i].strip()):
                attribution = re.sub(r'^[—–-]\s*', '', lines[i].strip())
                i += 1
            blocks.append(render_blockquote(quote_text, attribution, theme))
            continue

        # ── ARROW EMOTION ITEMS (→ LABEL: "text") ──
        if stripped.startswith('→ '):
            arrow_items = []
            while i < len(lines) and lines[i].strip().startswith('→ '):
                item_text = lines[i].strip()[2:]
                # Collect continuation lines (indented)
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('→ ') \
                        and not re.match(r'^[━═─]', lines[i].strip()) \
                        and not lines[i].strip().startswith('> ') \
                        and not lines[i].strip().startswith('##') \
                        and not lines[i].strip().startswith('**') \
                        and (lines[i].startswith('  ') or lines[i].startswith('\t')):
                    item_text += ' ' + lines[i].strip()
                    i += 1
                arrow_items.append(item_text)
            blocks.append(render_arrow_block(arrow_items, theme))
            continue

        # ── CHECKMARK ITEMS (✓ ...) ──
        if stripped.startswith('✓ '):
            check_items = []
            while i < len(lines) and lines[i].strip().startswith('✓ '):
                item = lines[i].strip()[2:]
                i += 1
                # Continuation lines
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('✓ ') \
                        and not re.match(r'^[━═─\[>→#*]', lines[i].strip()) \
                        and (lines[i].startswith('  ') or lines[i].startswith('\t')):
                    item += ' ' + lines[i].strip()
                    i += 1
                check_items.append(item)
            blocks.append(render_checklist(check_items, theme))
            continue

        # ── NUMBERED BELIEF ITEMS ([N.N] "text") ──
        m = re.match(r'^\[(\d+\.\d+)\]\s*(.+)$', stripped)
        if m:
            belief_items = []
            while i < len(lines):
                bm = re.match(r'^\[(\d+\.\d+)\]\s*(.+)$', lines[i].strip())
                if bm:
                    belief_items.append((bm.group(1), bm.group(2)))
                    i += 1
                    # Continuation
                    while i < len(lines) and lines[i].strip() and \
                            not re.match(r'^\[\d+\.\d+\]', lines[i].strip()) and \
                            not re.match(r'^[━═─>→#]', lines[i].strip()):
                        belief_items[-1] = (belief_items[-1][0],
                                            belief_items[-1][1] + ' ' + lines[i].strip())
                        i += 1
                else:
                    break
            blocks.append(render_belief_items(belief_items, theme))
            continue

        # ── DATA CALLOUT (DATI...: / DATO...: / NOTA...:) ──
        if re.match(r'^(DATI?\s|DATO\s|NOTA\s|AVVERTIMENTO)', stripped, re.I):
            callout_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and \
                    not re.match(r'^[━═─>→#\[✓]', lines[i].strip()) and \
                    not re.match(r'^(DATI?\s|DATO\s)', lines[i].strip(), re.I) and \
                    not lines[i].strip().startswith('##') and \
                    not lines[i].strip().startswith('**'):
                callout_lines.append(lines[i].strip())
                i += 1
            blocks.append(render_data_callout(' '.join(callout_lines), theme))
            continue

        # ── SOURCE CITATION (Fonte: ...) ──
        if stripped.startswith('Fonte:') or stripped.startswith('Fonti:'):
            blocks.append(render_source(stripped, theme))
            i += 1
            continue

        # ── FREQUENCY/ANALYSIS LABELS ──
        if re.match(r'^(FRASE ESATTA|FREQUENZA|ANALISI|MECCANISMO|PERCHÉ|COME EVITARLO|'
                     r'PROVA EMPIRICA|VARIANTE|VARIANTI|SOUNDBITE|LA REGOLA|'
                     r'IMPLICAZIONE|STRUTTURA GRAMMATICALE|CONTESTO D\'USO|'
                     r'LOGICA DI COSTRUZIONE|RAGIONAMENTO|RISPOSTA|MAPPA)\s*:', stripped, re.I):
            label_match = re.match(r'^([^:]+):\s*(.*)', stripped)
            if label_match:
                label = label_match.group(1)
                rest = label_match.group(2)
                # Collect continuation
                i += 1
                while i < len(lines) and lines[i].strip() and \
                        not re.match(r'^(FRASE|FREQUENZA|ANALISI|MECCANISMO|PERCHÉ|COME|PROVA|'
                                     r'VARIANTE|SOUNDBITE|LA REGOLA|IMPLICAZIONE|STRUTTURA|'
                                     r'CONTESTO|LOGICA|RAGIONAMENTO|RISPOSTA|MAPPA)\s*:', lines[i].strip(), re.I) and \
                        not re.match(r'^[━═─>→#\[✓]', lines[i].strip()) and \
                        not lines[i].strip().startswith('##') and \
                        not re.match(r'^[A-Z]\.\d+\s*[—–-]', lines[i].strip()):
                    rest += ' ' + lines[i].strip()
                    i += 1
                blocks.append(render_analysis_label(label, rest, theme))
                continue

        # ── PATTERN ENTRY (A.01 — "Title") with ─── divider above ──
        m2 = re.match(r'^([A-Z]\.\d+)\s*[—–-]\s*(.+)$', stripped)
        if m2:
            blocks.append(f'<div class="pattern-entry-header">'
                          f'<span class="pattern-num">{esc(m2.group(1))}</span>'
                          f'<span class="pattern-title">{inline_md(esc(m2.group(2)))}</span>'
                          f'</div>')
            i += 1
            continue

        # ── BOLD PARAGRAPH OPENER (**text**) ──
        if stripped.startswith('**') and '**' in stripped[2:]:
            # It's a paragraph that starts with bold — render as a highlight paragraph
            para_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and \
                    not re.match(r'^[━═─>→#\[✓]', lines[i].strip()) and \
                    not lines[i].strip().startswith('**') and \
                    not re.match(r'^(DATI?|DATO|NOTA|Fonte)', lines[i].strip(), re.I) and \
                    not re.match(r'^[A-Z]\.\d+\s*[—–-]', lines[i].strip()):
                para_lines.append(lines[i].strip())
                i += 1
            text = ' '.join(para_lines)
            # Check if it's a short bold-only line (like a section intro statement)
            if re.match(r'^\*\*[^*]+\*\*$', text.strip()):
                blocks.append(f'<p class="bold-statement">{inline_md(esc(text))}</p>')
            else:
                blocks.append(f'<p class="highlight-para">{inline_md(esc(text))}</p>')
            continue

        # ── ATTRIBUTION LINE (— source) after a quote that wasn't caught ──
        if re.match(r'^[—–-]\s*.+', stripped) and not stripped.startswith('---'):
            attr = re.sub(r'^[—–-]\s*', '', stripped)
            blocks.append(f'<p class="attribution">— {inline_md(esc(attr))}</p>')
            i += 1
            continue

        # ── NUMBERED LIST (1. / 2. / etc.) ──
        if re.match(r'^\d+\.\s+', stripped):
            ol_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                i += 1
                while i < len(lines) and lines[i].strip() and \
                        not re.match(r'^\d+\.\s+', lines[i].strip()) and \
                        not re.match(r'^[━═─>→#\[✓*]', lines[i].strip()) and \
                        (lines[i].startswith('   ') or lines[i].startswith('\t')):
                    item += ' ' + lines[i].strip()
                    i += 1
                ol_items.append(item)
            items_html = ''.join(f'<li>{inline_md(esc(it))}</li>' for it in ol_items)
            blocks.append(f'<ol>{items_html}</ol>')
            continue

        # ── BULLET LIST (- or • or *) ──
        if re.match(r'^[-•*]\s+', stripped) and not stripped.startswith('**'):
            ul_items = []
            while i < len(lines) and re.match(r'^[-•*]\s+', lines[i].strip()):
                item = re.sub(r'^[-•*]\s+', '', lines[i].strip())
                i += 1
                while i < len(lines) and lines[i].strip() and \
                        not re.match(r'^[-•*]\s+', lines[i].strip()) and \
                        not re.match(r'^[━═─>→#\[✓]', lines[i].strip()) and \
                        (lines[i].startswith('  ') or lines[i].startswith('\t')):
                    item += ' ' + lines[i].strip()
                    i += 1
                ul_items.append(item)
            items_html = ''.join(f'<li>{inline_md(esc(it))}</li>' for it in ul_items)
            blocks.append(f'<ul>{items_html}</ul>')
            continue

        # ── REGULAR PARAGRAPH ──
        para_lines = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and \
                not re.match(r'^[━═─>→#\[✓]', lines[i].strip()) and \
                not lines[i].strip().startswith('##') and \
                not lines[i].strip().startswith('**') and \
                not re.match(r'^(DATI?|DATO|NOTA|Fonte|FRASE|FREQUENZA|ANALISI)', lines[i].strip(), re.I) and \
                not re.match(r'^[A-Z]\.\d+\s*[—–-]', lines[i].strip()) and \
                not re.match(r'^[—–]\s', lines[i].strip()) and \
                lines[i].strip()[0] not in '┌╔' and \
                not lines[i].strip().startswith('> '):
            para_lines.append(lines[i].strip())
            i += 1
        text = ' '.join(para_lines)
        # Stat callout: has numbers/percentages and is short
        clean = re.sub(r'<[^>]+>', '', text)
        if re.search(r'(\d+[%€]|€\s*\d+|\d+\s*euro)', clean) and len(clean) < 250:
            blocks.append(f'<p class="stat-callout">{inline_md(esc(text))}</p>')
        else:
            blocks.append(f'<p>{inline_md(esc(text))}</p>')

    return '\n'.join(blocks)


# ── SPECIAL ELEMENT RENDERERS ─────────────────────────────────────────────────

def render_blockquote(text: str, attribution: str, theme: dict) -> str:
    return f'''<blockquote class="quote-card">
        <div class="quote-mark">&ldquo;</div>
        <div class="quote-body">{inline_md(esc(text))}</div>
        {f'<cite class="quote-cite">— {inline_md(esc(attribution))}</cite>' if attribution else ''}
    </blockquote>'''


def render_arrow_block(items: list, theme: dict) -> str:
    """Render → items as emotion/insight cards."""
    cards = []
    for item in items:
        # Try to split LABEL: "rest"
        m = re.match(r'^([A-ZÀÈÉÌÒÙ\s]+(?:\s+[A-ZÀÈÉÌÒÙ]+)*):\s*(.+)', item)
        if m:
            label = m.group(1).strip()
            body = m.group(2).strip()
            cards.append(f'''<div class="arrow-card">
                <div class="arrow-icon">→</div>
                <div class="arrow-content">
                    <div class="arrow-label">{esc(label)}</div>
                    <div class="arrow-body">{inline_md(esc(body))}</div>
                </div>
            </div>''')
        else:
            cards.append(f'''<div class="arrow-card">
                <div class="arrow-icon">→</div>
                <div class="arrow-content">
                    <div class="arrow-body">{inline_md(esc(item))}</div>
                </div>
            </div>''')
    return f'<div class="arrow-block">{"".join(cards)}</div>'


def render_checklist(items: list, theme: dict) -> str:
    items_html = ''.join(
        f'<div class="check-item"><span class="check-icon">✓</span>'
        f'<span class="check-text">{inline_md(esc(it))}</span></div>'
        for it in items
    )
    return f'<div class="checklist-block">{items_html}</div>'


def render_belief_items(items: list, theme: dict) -> str:
    cards = []
    for num, text in items:
        cards.append(f'''<div class="belief-item">
            <span class="belief-num">[{esc(num)}]</span>
            <span class="belief-text">{inline_md(esc(text))}</span>
        </div>''')
    return f'<div class="belief-block">{"".join(cards)}</div>'


def render_data_callout(text: str, theme: dict) -> str:
    # Split label from content
    m = re.match(r'^([A-ZÀÈÉÌÒÙ\s]+(?:\s+[A-ZÀÈÉÌÒÙ]+)*):\s*(.*)', text, re.I)
    if m:
        label = m.group(1).strip()
        body = m.group(2).strip()
        return f'''<div class="data-callout">
            <div class="data-label">{esc(label)}</div>
            <div class="data-body">{inline_md(esc(body))}</div>
        </div>'''
    return f'<div class="data-callout"><div class="data-body">{inline_md(esc(text))}</div></div>'


def render_source(text: str, theme: dict) -> str:
    return f'<p class="source-citation">{inline_md(esc(text))}</p>'


def render_analysis_label(label: str, body: str, theme: dict) -> str:
    return f'''<div class="analysis-block">
        <div class="analysis-label">{esc(label)}:</div>
        <div class="analysis-body">{inline_md(esc(body))}</div>
    </div>'''


def render_ascii_diagram(art_lines: list, theme: dict) -> str:
    """Render complex ASCII art (diagrams, maps, visual figures) as a styled card
    preserving the exact original layout."""
    t = theme
    # Preserve original spacing/indentation exactly
    safe = esc('\n'.join(art_lines))
    return f'''<div class="ascii-diagram-card">
        <pre class="ascii-diagram-pre">{safe}</pre>
    </div>'''


def render_ascii_table(table_lines: list, theme: dict) -> str:
    """Convert ASCII box-drawing table into a beautiful HTML table."""
    # Parse the box-drawing table
    rows = []
    is_header = True
    for line in table_lines:
        stripped = line.strip()
        # Skip border lines
        if re.match(r'^[┌├└╔╠╚][─═┬┼┴╦╩╬]+[┐┤┘╗╣╝]$', stripped):
            if rows and is_header:
                is_header = False
            continue
        # Data row
        if stripped.startswith('│') or stripped.startswith('║') or stripped.startswith('┃'):
            cells = re.split(r'[│║┃]', stripped)
            cells = [c.strip() for c in cells if c.strip() != '']
            if cells:
                rows.append(('header' if is_header and not any(not is_header for _ in []) else 'data', cells))
                if is_header and len(rows) == 1:
                    is_header = False

    if not rows:
        # Fallback: render as preformatted
        safe = esc('\n'.join(table_lines))
        return f'<div class="diagram-card"><pre class="diagram-pre">{safe}</pre></div>'

    # Build HTML table
    html_parts = ['<div class="styled-table-wrapper"><table class="styled-table">']

    # First row as header
    if rows:
        html_parts.append('<thead><tr>')
        for cell in rows[0][1]:
            html_parts.append(f'<th>{inline_md(esc(cell))}</th>')
        html_parts.append('</tr></thead>')

    # Rest as body (handle multi-line cells by detecting continuation rows)
    html_parts.append('<tbody>')
    current_row_cells = None
    for row_type, cells in rows[1:]:
        if len(cells) >= len(rows[0][1]) if rows[0][1] else True:
            # Check if first cell is empty (continuation of previous row)
            if current_row_cells and cells[0] == '' and any(c for c in cells):
                # Merge into current row
                for j, c in enumerate(cells):
                    if j < len(current_row_cells) and c:
                        current_row_cells[j] += '<br>' + inline_md(esc(c))
            else:
                # Flush previous row
                if current_row_cells:
                    html_parts.append('<tr>' + ''.join(f'<td>{c}</td>' for c in current_row_cells) + '</tr>')
                current_row_cells = [inline_md(esc(c)) for c in cells]
        else:
            # Mismatched columns — try to merge
            if current_row_cells:
                merged = ' '.join(c for c in cells if c)
                if merged and current_row_cells:
                    current_row_cells[-1] += '<br>' + inline_md(esc(merged))

    if current_row_cells:
        html_parts.append('<tr>' + ''.join(f'<td>{c}</td>' for c in current_row_cells) + '</tr>')

    html_parts.append('</tbody></table></div>')
    return '\n'.join(html_parts)


# ── HTML DOCUMENT GENERATOR ──────────────────────────────────────────────────

def generate_full_html(doc: dict, theme: dict) -> str:
    t = theme

    font_import = (
        f"https://fonts.googleapis.com/css2?"
        f"family={t['font_display'].replace(' ', '+')}:wght@400;500;600;700;800;900"
        f"&family={t['font_body'].replace(' ', '+')}:wght@300;400;500;600;700"
        f"&display=swap"
    )

    # Build chapters HTML
    chapters_html = ""
    for chap in doc['chapters']:
        body_html = convert_chapter_content(chap['raw_lines'], theme)

        chapters_html += f'''
<!-- ═══ CHAPTER {chap["number"]} COVER ═══ -->
<div class="chapter-cover" style="background:linear-gradient(150deg,{t['chapter_bg']} 0%,{t['gradient_start']} 40%,{t['gradient_end']} 100%);">
  <div class="ch-cover-number">{chap["number"]}</div>
  <div class="ch-cover-inner">
    <div class="ch-cover-label">CAPITOLO {chap["number"]}</div>
    <h1 class="ch-cover-title">{esc(chap["title"])}</h1>
    <div class="ch-cover-accent"></div>
    <p class="ch-cover-subtitle">{esc(chap.get("subtitle", ""))}</p>
  </div>
</div>

<!-- ═══ CHAPTER {chap["number"]} CONTENT ═══ -->
<div class="chapter-content">
  <div class="ch-header-band">
    <span class="ch-header-num">CAP. {chap["number"]}</span>
    <span class="ch-header-title">{esc(chap["title"])}</span>
  </div>
  <div class="chapter-body">
    {body_html}
  </div>
</div>
'''

    # TOC
    toc_items = ""
    for chap in doc['chapters']:
        toc_items += f'''
<div class="toc-item">
  <div class="toc-num">{chap["number"]}</div>
  <div class="toc-text">
    <div class="toc-title">{esc(chap["title"])}</div>
    <div class="toc-subtitle">{esc(chap.get("subtitle", ""))}</div>
  </div>
</div>'''

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>{esc(doc["title"])}</title>
<link href="{font_import}" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════════════════
   MANIFOLD PDF — Professional Design System v4
   ═══════════════════════════════════════════════════════════════════ */

/* ── RESET ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── PAGE ── */
@page {{
  size: A4;
  margin: 18mm 20mm 22mm 20mm;
  @bottom-center {{
    content: counter(page);
    font-family: '{t["font_body"]}', sans-serif;
    font-size: 8pt;
    color: {t["accent"]};
  }}
  @bottom-right {{
    content: "{esc(doc['title'][:35])}";
    font-family: '{t["font_body"]}', sans-serif;
    font-size: 6.5pt;
    color: {t["accent3"]};
    letter-spacing: 0.5px;
  }}
}}

@page :first {{ margin: 0; }}
@page cover {{ margin: 0; }}
@page chapter-cover {{ margin: 0; }}

body {{
  font-family: '{t["font_body"]}', 'Helvetica Neue', Arial, sans-serif;
  font-size: 9.5pt;
  line-height: 1.58;
  color: {t["text"]};
  background: white;
}}

/* ═══════════════════════════════════════════════════════════════════
   COVER PAGE
   ═══════════════════════════════════════════════════════════════════ */
.main-cover {{
  page: cover;
  page-break-after: always;
  min-height: 297mm;
  margin: -18mm -20mm -22mm -20mm;
  padding: 0;
  background: linear-gradient(155deg, {t["chapter_bg"]} 0%, {t["gradient_start"]} 35%, {t["gradient_end"]} 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
.cover-deco-circle {{
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.06);
}}
.cover-deco-circle:nth-child(1) {{ width: 400mm; height: 400mm; top: -100mm; right: -150mm; }}
.cover-deco-circle:nth-child(2) {{ width: 300mm; height: 300mm; top: -50mm; right: -100mm; }}
.cover-deco-circle:nth-child(3) {{ width: 200mm; height: 200mm; bottom: -60mm; left: -80mm; }}
.cover-inner {{
  position: relative; z-index: 2;
  padding: 55mm 30mm 30mm 30mm;
}}
.cover-top-line {{
  width: 25mm; height: 3px;
  background: {t["accent2"]};
  margin-bottom: 10mm;
}}
.cover-market {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 8pt; font-weight: 600;
  letter-spacing: 4px; text-transform: uppercase;
  color: {t["accent2"]}; margin-bottom: 8mm;
}}
.cover-title {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 30pt; font-weight: 800;
  color: white; line-height: 1.15;
  margin-bottom: 6mm; max-width: 155mm;
}}
.cover-subtitle {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 10.5pt; font-weight: 300;
  color: rgba(255,255,255,0.65);
  line-height: 1.6; max-width: 140mm;
  margin-bottom: 18mm;
}}
.cover-accent-bar {{
  width: 40mm; height: 3px;
  background: linear-gradient(90deg, {t["accent"]}, {t["accent2"]}, transparent);
  margin-bottom: 18mm;
}}
.cover-meta {{
  display: flex; flex-direction: column; gap: 3mm;
}}
.cover-meta span {{
  font-size: 7.5pt; color: rgba(255,255,255,0.45);
  letter-spacing: 2px; text-transform: uppercase;
}}
.cover-bottom {{
  position: absolute; bottom: 25mm; left: 30mm; right: 30mm;
  display: flex; justify-content: space-between;
  z-index: 2;
}}
.cover-badge {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  padding: 2mm 6mm; border-radius: 3mm;
  font-size: 7pt; color: rgba(255,255,255,0.5);
  letter-spacing: 1.5px; text-transform: uppercase;
}}

/* ═══════════════════════════════════════════════════════════════════
   TABLE OF CONTENTS
   ═══════════════════════════════════════════════════════════════════ */
.toc-page {{
  page-break-before: always;
  page-break-after: always;
  padding-top: 5mm;
}}
.toc-header {{
  margin-bottom: 10mm;
  padding-bottom: 5mm;
  border-bottom: 3px solid {t["accent3"]};
}}
.toc-label {{
  font-size: 7pt; letter-spacing: 5px;
  text-transform: uppercase; color: {t["accent"]};
  margin-bottom: 2mm;
}}
.toc-title-main {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 22pt; font-weight: 800; color: {t["primary"]};
}}
.toc-item {{
  display: flex; align-items: flex-start;
  padding: 4mm 0;
  border-bottom: 1px solid {t["accent3"]};
  gap: 5mm;
}}
.toc-item:last-child {{ border-bottom: none; }}
.toc-num {{
  font-family: '{t["font_display"]}', monospace;
  font-size: 11pt; font-weight: 800;
  color: {t["accent"]}; min-width: 12mm;
  line-height: 1.2;
}}
.toc-text {{ flex: 1; }}
.toc-title {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 10pt; font-weight: 600;
  color: {t["text"]}; line-height: 1.3;
}}
.toc-subtitle {{
  font-size: 8pt; color: {t["text_light"]};
  margin-top: 1mm; line-height: 1.4;
}}

/* ═══════════════════════════════════════════════════════════════════
   CHAPTER COVER
   ═══════════════════════════════════════════════════════════════════ */
.chapter-cover {{
  page: chapter-cover;
  page-break-before: always;
  page-break-after: always;
  page-break-inside: avoid;
  min-height: 297mm;
  margin: -18mm -20mm -22mm -20mm;
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  position: relative;
  overflow: hidden;
}}
.ch-cover-number {{
  position: absolute;
  bottom: -15mm; right: -5mm;
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 220pt; font-weight: 900;
  color: rgba(255,255,255,0.03);
  line-height: 1;
}}
.ch-cover-inner {{
  position: relative; z-index: 2;
  padding: 0 35mm;
  max-width: 165mm;
}}
.ch-cover-label {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 8pt; font-weight: 700;
  letter-spacing: 6px; text-transform: uppercase;
  color: {t["accent2"]}; margin-bottom: 7mm;
}}
.ch-cover-title {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 30pt; font-weight: 800;
  color: white; line-height: 1.12;
  margin-bottom: 8mm;
}}
.ch-cover-accent {{
  width: 30mm; height: 3px;
  background: linear-gradient(90deg, {t["accent"]}, {t["accent2"]});
  margin-bottom: 10mm;
}}
.ch-cover-subtitle {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 9.5pt; font-weight: 300;
  color: rgba(255,255,255,0.55);
  line-height: 1.55;
}}

/* ═══════════════════════════════════════════════════════════════════
   CHAPTER CONTENT
   ═══════════════════════════════════════════════════════════════════ */
.chapter-content {{
  page-break-before: avoid;
}}
.ch-header-band {{
  background: linear-gradient(90deg, {t["accent"]} 0%, {t["accent2"]} 40%, transparent 100%);
  margin: -18mm -20mm 8mm -20mm;
  padding: 2mm 20mm;
  display: flex; align-items: center; gap: 3mm;
  height: 8mm;
}}
.ch-header-num {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 7pt; font-weight: 800;
  color: white; letter-spacing: 2px;
}}
.ch-header-title {{
  font-family: '{t["font_body"]}', sans-serif;
  font-size: 7pt; font-weight: 500;
  color: rgba(255,255,255,0.85);
  letter-spacing: 1px; text-transform: uppercase;
}}
.chapter-body {{
  position: relative;
  columns: 1;
}}

/* ═══════════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════════════════ */

/* Section headers (from ━━━ blocks) */
.section-header {{
  margin: 10mm 0 6mm 0;
  page-break-after: avoid;
  page-break-inside: avoid;
}}
.section-header-line {{
  width: 100%; height: 2px;
  background: linear-gradient(90deg, {t["accent"]}, {t["accent3"]}, transparent);
  margin-bottom: 4mm;
}}
.section-title {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 14pt; font-weight: 700;
  color: {t["primary"]};
  line-height: 1.25;
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}}
.section-subtitle {{
  font-size: 9pt; color: {t["text_light"]};
  margin-top: 2mm; line-height: 1.4;
  font-style: italic;
}}

/* Subsection heading (## ) */
h2.subsection-heading {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 12pt; font-weight: 700;
  color: {t["primary"]};
  margin: 8mm 0 3mm 0;
  padding-bottom: 2mm;
  border-bottom: 2px solid {t["accent3"]};
  page-break-after: avoid;
}}
h3 {{
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 10.5pt; font-weight: 600;
  color: {t["accent"]};
  margin: 6mm 0 2mm 0;
  page-break-after: avoid;
}}

/* Paragraphs */
p {{
  margin-bottom: 3mm;
  text-align: justify;
  hyphens: auto;
}}
p.bold-statement {{
  font-size: 11pt;
  font-weight: 600;
  color: {t["primary"]};
  line-height: 1.45;
  margin: 6mm 0 4mm 0;
  padding: 4mm 5mm;
  background: {t["light_bg"]};
  border-left: 4px solid {t["accent"]};
  border-radius: 0 3mm 3mm 0;
  text-align: left;
  page-break-inside: avoid;
}}
p.highlight-para {{
  margin-bottom: 3mm;
  text-align: justify;
}}
p.highlight-para strong:first-child {{
  color: {t["primary"]};
}}
p.stat-callout {{
  background: {t["light_bg"]};
  border-left: 4px solid {t["accent"]};
  padding: 3mm 5mm;
  border-radius: 0 2mm 2mm 0;
  font-weight: 500;
  color: {t["primary"]};
  font-size: 9pt;
  margin: 4mm 0;
  page-break-inside: avoid;
}}

strong {{ font-weight: 700; color: {t["primary"]}; }}
em {{ font-style: italic; color: #555; }}

/* ═══════════════════════════════════════════════════════════════════
   BLOCKQUOTES / QUOTE CARDS
   ═══════════════════════════════════════════════════════════════════ */
.quote-card {{
  margin: 5mm 0;
  padding: 5mm 6mm 4mm 14mm;
  background: linear-gradient(135deg, {t["light_bg"]} 0%, {t["light_bg2"]} 100%);
  border-left: 4px solid {t["accent"]};
  border-radius: 0 4mm 4mm 0;
  position: relative;
  page-break-inside: avoid;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}}
.quote-mark {{
  position: absolute;
  top: 1mm; left: 3mm;
  font-family: '{t["font_display"]}', Georgia, serif;
  font-size: 36pt;
  color: {t["accent3"]};
  line-height: 1;
}}
.quote-body {{
  font-style: italic;
  font-size: 9.5pt;
  color: {t["primary"]};
  line-height: 1.55;
  font-weight: 500;
}}
.quote-cite {{
  display: block;
  text-align: right;
  font-size: 7.5pt;
  font-style: normal;
  font-weight: 600;
  color: {t["accent"]};
  margin-top: 2mm;
  letter-spacing: 0.3px;
}}

/* ═══════════════════════════════════════════════════════════════════
   ARROW EMOTION CARDS
   ═══════════════════════════════════════════════════════════════════ */
.arrow-block {{
  margin: 4mm 0;
}}
.arrow-card {{
  display: flex;
  align-items: flex-start;
  gap: 3mm;
  padding: 3mm 4mm;
  margin-bottom: 2mm;
  background: {t["light_bg"]};
  border-radius: 3mm;
  border-left: 3px solid {t["accent2"]};
  page-break-inside: avoid;
}}
.arrow-icon {{
  font-size: 12pt;
  color: {t["accent"]};
  font-weight: 800;
  line-height: 1.3;
  min-width: 5mm;
}}
.arrow-content {{ flex: 1; }}
.arrow-label {{
  font-size: 8pt;
  font-weight: 700;
  color: {t["accent"]};
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 1mm;
}}
.arrow-body {{
  font-size: 9pt;
  color: {t["text"]};
  line-height: 1.5;
}}

/* ═══════════════════════════════════════════════════════════════════
   CHECKLIST
   ═══════════════════════════════════════════════════════════════════ */
.checklist-block {{
  margin: 4mm 0;
  padding: 4mm 5mm;
  background: {t["success_light"]};
  border-radius: 3mm;
  border: 1px solid {t["success"]};
}}
.check-item {{
  display: flex; align-items: flex-start;
  gap: 3mm; padding: 1.5mm 0;
}}
.check-icon {{
  color: {t["success"]};
  font-size: 11pt; font-weight: 800;
  line-height: 1.3; min-width: 5mm;
}}
.check-text {{
  font-size: 9pt; color: {t["text"]};
  line-height: 1.5;
}}

/* ═══════════════════════════════════════════════════════════════════
   BELIEF ITEMS [N.N]
   ═══════════════════════════════════════════════════════════════════ */
.belief-block {{
  margin: 4mm 0;
}}
.belief-item {{
  display: flex; align-items: flex-start;
  gap: 3mm; padding: 2mm 4mm;
  margin-bottom: 1.5mm;
  background: white;
  border: 1px solid {t["accent3"]};
  border-radius: 2mm;
  page-break-inside: avoid;
}}
.belief-num {{
  font-family: '{t["font_display"]}', monospace;
  font-size: 8pt; font-weight: 700;
  color: {t["accent"]};
  min-width: 10mm;
  line-height: 1.5;
}}
.belief-text {{
  font-size: 9pt; color: {t["text"]};
  line-height: 1.5; flex: 1;
}}

/* ═══════════════════════════════════════════════════════════════════
   DATA CALLOUTS
   ═══════════════════════════════════════════════════════════════════ */
.data-callout {{
  margin: 4mm 0;
  padding: 4mm 5mm;
  background: {t["info_light"]};
  border-left: 4px solid {t["info"]};
  border-radius: 0 3mm 3mm 0;
  page-break-inside: avoid;
}}
.data-label {{
  font-size: 7.5pt;
  font-weight: 700;
  color: {t["info"]};
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 2mm;
}}
.data-body {{
  font-size: 9pt;
  color: {t["text"]};
  line-height: 1.5;
}}

/* ═══════════════════════════════════════════════════════════════════
   SOURCE CITATIONS
   ═══════════════════════════════════════════════════════════════════ */
.source-citation {{
  font-size: 7.5pt;
  color: {t["text_light"]};
  font-style: italic;
  margin: 1mm 0 3mm 0;
  padding-left: 3mm;
  border-left: 2px solid {t["accent3"]};
}}

/* ═══════════════════════════════════════════════════════════════════
   ATTRIBUTION LINES
   ═══════════════════════════════════════════════════════════════════ */
.attribution {{
  font-size: 7.5pt;
  color: {t["accent"]};
  font-weight: 600;
  text-align: right;
  margin: -1mm 0 3mm 0;
  letter-spacing: 0.3px;
}}

/* ═══════════════════════════════════════════════════════════════════
   ANALYSIS / LABEL BLOCKS
   ═══════════════════════════════════════════════════════════════════ */
.analysis-block {{
  margin: 3mm 0;
  padding: 3mm 4mm;
  background: {t["light_bg"]};
  border-radius: 2mm;
  page-break-inside: avoid;
}}
.analysis-label {{
  font-size: 7.5pt;
  font-weight: 700;
  color: {t["accent"]};
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 1.5mm;
}}
.analysis-body {{
  font-size: 9pt;
  color: {t["text"]};
  line-height: 1.55;
}}

/* ═══════════════════════════════════════════════════════════════════
   PATTERN ENTRY HEADERS
   ═══════════════════════════════════════════════════════════════════ */
.pattern-entry-header {{
  margin: 6mm 0 3mm 0;
  padding: 3mm 5mm;
  background: linear-gradient(90deg, {t["primary"]} 0%, {t["gradient_end"]} 100%);
  border-radius: 3mm;
  page-break-after: avoid;
}}
.pattern-num {{
  font-family: '{t["font_display"]}', monospace;
  font-size: 9pt; font-weight: 800;
  color: {t["accent2"]};
  margin-right: 3mm;
}}
.pattern-title {{
  font-size: 10pt; font-weight: 600;
  color: white;
}}

/* ═══════════════════════════════════════════════════════════════════
   TABLES
   ═══════════════════════════════════════════════════════════════════ */
.styled-table-wrapper {{
  margin: 6mm 0;
  border-radius: 3mm;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  page-break-inside: auto;
}}
.styled-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 8pt;
}}
.styled-table thead {{
  background: linear-gradient(135deg, {t["primary"]}, {t["gradient_end"]});
  display: table-header-group;
}}
.styled-table thead th {{
  color: white;
  font-family: '{t["font_body"]}', sans-serif;
  font-weight: 700;
  padding: 3mm 4mm;
  text-align: left;
  font-size: 7.5pt;
  letter-spacing: 0.5px;
  vertical-align: top;
}}
.styled-table tbody tr {{
  page-break-inside: avoid;
}}
.styled-table tbody tr:nth-child(even) {{
  background: {t["light_bg"]};
}}
.styled-table tbody td {{
  padding: 3mm 4mm;
  border-bottom: 1px solid {t["accent3"]};
  line-height: 1.5;
  vertical-align: top;
}}
.styled-table tbody td:first-child {{
  font-weight: 600;
  color: {t["primary"]};
}}

/* ASCII DIAGRAM CARD — for complex visual figures */
.ascii-diagram-card {{
  margin: 8mm 0;
  background: linear-gradient(135deg, {t["light_bg"]} 0%, white 50%, {t["light_bg2"]} 100%);
  border: 2px solid {t["accent3"]};
  border-radius: 4mm;
  padding: 6mm 5mm;
  page-break-inside: avoid;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow-x: auto;
}}
.ascii-diagram-pre {{
  font-family: 'Courier New', 'Lucida Console', monospace;
  font-size: 7.5pt;
  line-height: 1.3;
  color: {t["primary"]};
  white-space: pre;
  margin: 0;
  text-align: center;
}}

/* DIAGRAM fallback */
.diagram-card {{
  margin: 5mm 0;
  background: {t["light_bg"]};
  border: 1px solid {t["accent3"]};
  border-left: 4px solid {t["accent"]};
  border-radius: 0 3mm 3mm 0;
  padding: 4mm 5mm;
  page-break-inside: avoid;
}}
.diagram-pre {{
  font-family: 'Courier New', monospace;
  font-size: 7pt; line-height: 1.35;
  color: {t["primary"]};
  white-space: pre-wrap;
  word-break: break-all;
}}

/* ═══════════════════════════════════════════════════════════════════
   LISTS
   ═══════════════════════════════════════════════════════════════════ */
ul, ol {{
  margin: 3mm 0 4mm 6mm;
  padding-left: 4mm;
}}
li {{
  margin-bottom: 2mm;
  line-height: 1.55;
}}
ul li::marker {{
  color: {t["accent"]};
  font-size: 11pt;
}}
ol li::marker {{
  color: {t["accent"]};
  font-weight: 700;
}}

/* ═══════════════════════════════════════════════════════════════════
   DIVIDERS
   ═══════════════════════════════════════════════════════════════════ */
hr.thin-divider {{
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, {t["accent3"]}, transparent);
  margin: 6mm 0;
}}

</style>
</head>
<body>

<!-- ═══════════════════════════════════════════════════════════════════
     MAIN COVER
     ═══════════════════════════════════════════════════════════════════ -->
<div class="main-cover">
  <div class="cover-deco-circle"></div>
  <div class="cover-deco-circle"></div>
  <div class="cover-deco-circle"></div>
  <div class="cover-inner">
    <div class="cover-top-line"></div>
    <div class="cover-market">{esc(doc["market"] or "Market Research Brief")}</div>
    <h1 class="cover-title">{esc(doc["title"])}</h1>
    <p class="cover-subtitle">{esc(doc["subtitle"])}</p>
    <div class="cover-accent-bar"></div>
    <div class="cover-meta">
      <span>Documento Riservato · {doc["date"]}</span>
      <span>AI Manifold Brief · {len(doc["chapters"])} Capitoli</span>
    </div>
  </div>
  <div class="cover-bottom">
    <div class="cover-badge">Confidential Research Report</div>
    <div class="cover-badge">&copy; {datetime.now().year}</div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     TABLE OF CONTENTS
     ═══════════════════════════════════════════════════════════════════ -->
<div class="toc-page">
  <div class="toc-header">
    <div class="toc-label">Indice dei Capitoli</div>
    <div class="toc-title-main">Sommario</div>
  </div>
  {toc_items}
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     CHAPTERS
     ═══════════════════════════════════════════════════════════════════ -->
{chapters_html}

</body>
</html>'''
    return html


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate professional PDF from manifold")
    parser.add_argument("input", help="Input text file")
    parser.add_argument("output", nargs="?", help="Output PDF file")
    parser.add_argument("--title", help="Override document title")
    parser.add_argument("--subtitle", help="Override document subtitle")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    output_path = (
        Path(args.output) if args.output
        else input_path.with_name(input_path.stem + "_professional.pdf")
    )

    print(f"📖 Reading: {input_path}")
    content = input_path.read_text(encoding='utf-8')

    print("🎨 Detecting market theme...")
    theme = detect_theme(content)
    print(f"   Theme: {theme['name']}")

    print("📐 Parsing document structure...")
    doc = parse_document(content)

    if args.title:
        doc['title'] = args.title
        if not doc['subtitle']:
            doc['subtitle'] = f"{args.title} — Ricerca di Mercato Professionale"
    if args.subtitle:
        doc['subtitle'] = args.subtitle
        if not doc['market']:
            doc['market'] = args.subtitle

    print(f"   Title: {doc['title']}")
    print(f"   Chapters: {len(doc['chapters'])}")
    for chap in doc['chapters']:
        print(f"     Cap. {chap['number']}: {chap['title']} ({len(chap['raw_lines'])} lines)")

    print("🖌  Generating HTML...")
    html = generate_full_html(doc, theme)

    html_path = output_path.with_suffix('.html')
    html_path.write_text(html, encoding='utf-8')
    print(f"   HTML saved: {html_path}")

    try:
        import weasyprint
        print("📄 Converting to PDF with WeasyPrint...")
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(output_path))
        html_path.unlink()
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ PDF created: {output_path}")
        print(f"   Size: {size_mb:.1f} MB")
        return
    except ImportError:
        print("   WeasyPrint not found, trying wkhtmltopdf...")
    except Exception as e:
        print(f"   WeasyPrint error: {e}")

    import subprocess
    try:
        result = subprocess.run(
            ['wkhtmltopdf', '--page-size', 'A4',
             '--margin-top', '18mm', '--margin-bottom', '22mm',
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
    print("Install WeasyPrint: pip install weasyprint")


if __name__ == '__main__':
    main()
