#!/usr/bin/env python3
"""
web_text.py — Clean text extraction from web pages.
Strips all HTML/CSS/JS and returns only readable text content.

Usage:
  python3 web_text.py "URL"                    # Fetch and extract text from URL
  python3 web_text.py --search "query terms"   # Search DuckDuckGo and return text results
  python3 web_text.py "URL" --max-lines 200    # Limit output lines
"""

import sys
import re
import urllib.request
import urllib.parse
import html


def strip_html(raw_html):
    """Remove all HTML tags, scripts, styles and return clean text."""
    # Remove script and style blocks entirely
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<noscript[^>]*>.*?</noscript>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Replace block elements with newlines
    text = re.sub(r'<(?:br|p|div|h[1-6]|li|tr|blockquote|hr)[^>]*/?>', '\n', text, flags=re.IGNORECASE)
    # Remove all remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace: collapse multiple spaces on each line, remove blank lines
    lines = []
    for line in text.split('\n'):
        line = ' '.join(line.split()).strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def fetch_url(url, max_lines=200):
    """Fetch a URL and return clean text."""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; ManifoldResearch/1.0)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            charset = resp.headers.get_content_charset() or 'utf-8'
            raw = resp.read().decode(charset, errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

    text = strip_html(raw)
    lines = text.split('\n')[:max_lines]
    return '\n'.join(lines)


def search_ddg(query, max_lines=100):
    """Search DuckDuckGo HTML and return clean text results."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    return fetch_url(url, max_lines)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    max_lines = 200
    if '--max-lines' in args:
        idx = args.index('--max-lines')
        max_lines = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if args[0] == '--search':
        query = ' '.join(args[1:])
        print(search_ddg(query, max_lines))
    else:
        url = args[0]
        print(fetch_url(url, max_lines))


if __name__ == '__main__':
    main()
