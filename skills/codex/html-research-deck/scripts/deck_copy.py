#!/usr/bin/env python3
"""Dump the visible copy of an HTML deck slide by slide as JSON (and optionally a readable text file).

usage: deck_copy.py /abs/deck/index.html --json /abs/deck/qa/copy.json [--text /abs/deck/qa/copy.txt] [--notes 400]

Per slide: data-title, data-section, kicker, h2, lane headers (SVG text at 24px/650 — the builder's lane()), every other
visible text run in DOM order (SVG <text>, HTML blocks), the closing line (.takeaway) with its bold phrases, the cite line and
the speaker notes. Used by score_message.py (measured items) and judge_message.py (what the independent judge reads).
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser

BLOCK = {'h1', 'h2', 'h3', 'h4', 'p', 'li', 'div', 'figcaption', 'blockquote', 'td', 'th', 'text', 'svg', 'g', 'ul', 'ol', 'table', 'tr', 'dt', 'dd', 'pre', 'foreignObject'}


class Deck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides, self.cur, self.stack, self.buf, self.meta, self.skip = [], None, [], [], None, 0

    def flush(self):
        if self.cur is not None and self.buf:
            text = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
            if text:
                self.cur['_lines'].append((self.meta or {'tag': '?', 'cls': '', 'style': '', 'path': []}, text))
        self.buf, self.meta = [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'section' and 'slide' in (a.get('class') or ''):
            self.flush()
            self.cur = {'n': len(self.slides) + 1, 'title': a.get('data-title', ''), 'section': a.get('data-section', ''), 'cls': a.get('class', ''), '_lines': []}
            self.slides.append(self.cur)
            self.stack = []
            return
        if self.cur is None:
            return
        cls = a.get('class', '') or ''
        if tag in BLOCK:
            self.flush()
            self.meta = {'tag': tag, 'cls': cls, 'style': a.get('style', '') or '', 'path': [c for _, c in self.stack if c]}
        elif tag in ('b', 'strong'):
            self.buf.append('**')
        elif tag in ('em', 'i'):
            self.buf.append('*')
        elif tag == 'br':
            self.buf.append(' / ')
        self.stack.append((tag, cls))

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1
        if self.cur is None:
            return
        if tag == 'section':
            self.flush(); self.cur = None; self.stack = []
            return
        while self.stack:
            t, c = self.stack.pop()
            if t == tag:
                if tag in ('b', 'strong'):
                    self.buf.append('**')
                elif tag in ('em', 'i'):
                    self.buf.append('*')
                elif tag in BLOCK:
                    self.flush()
                break

    def handle_data(self, data):
        if self.cur is not None and not self.skip:
            self.buf.append(data)


def classify(slide):
    out = {'n': slide['n'], 'title': slide['title'], 'section': slide['section'], 'cls': slide['cls'], 'kicker': '', 'h2': '', 'h1': '',
           'lanes': [], 'visible': [], 'closing': '', 'closing_bold': [], 'cite': '', 'notes': ''}
    in_notes = False
    for meta, text in slide['_lines']:
        tag, cls, style, path = meta['tag'], meta['cls'], meta['style'], meta['path']
        if tag == 'aside' or 'notes' in cls or any('notes' in p for p in path):
            in_notes = True
        if in_notes:
            out['notes'] += (' ' if out['notes'] else '') + text
            continue
        if 'kicker' in cls:
            out['kicker'] = text
        elif tag == 'h2':
            out['h2'] = text
        elif tag == 'h1':
            out['h1'] = text
        elif 'takeaway' in cls or any('takeaway' in p for p in path):
            out['closing'] = text.replace('**', '').strip()
            out['closing_bold'] = re.findall(r'\*\*(.+?)\*\*', text)
        elif 'cite' in cls or any('cite' in p for p in path):
            out['cite'] = text
        elif tag == 'text' and 'font-size:24px;font-weight:650' in style.replace(' ', ''):
            out['lanes'].append(text)
        else:
            out['visible'].append(text)
    return out


def dump(index):
    html = open(index, encoding='utf-8').read()
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    d = Deck()
    d.feed(html)
    return {'index': index, 'n': len(d.slides), 'slides': [classify(s) for s in d.slides]}


def render_text(doc, notes_chars=400):
    lines = []
    for s in doc['slides']:
        lines.append(f"\n===== slide {s['n']:02d} [{s['section']}] {s['title']}")
        if s['kicker']:
            lines.append(f"  kicker : {s['kicker']}")
        if s['h1']:
            lines.append(f"  h1     : {s['h1']}")
        if s['h2']:
            lines.append(f"  h2     : {s['h2']}")
        for l in s['lanes']:
            lines.append(f"  lane   : {l}")
        if s['visible']:
            lines.append('  text   : ' + ' | '.join(s['visible']))
        if s['closing']:
            lines.append(f"  closing: {s['closing']}")
        if s['cite']:
            lines.append(f"  cite   : {s['cite']}")
        if s['notes'] and notes_chars:
            lines.append(f"  notes  : {s['notes'][:notes_chars]}{'…' if len(s['notes']) > notes_chars else ''}")
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index'); ap.add_argument('--json'); ap.add_argument('--text'); ap.add_argument('--notes', type=int, default=400)
    a = ap.parse_args()
    doc = dump(a.index)
    if a.json:
        open(a.json, 'w', encoding='utf-8').write(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    if a.text:
        open(a.text, 'w', encoding='utf-8').write(render_text(doc, a.notes))
    if not a.json and not a.text:
        sys.stdout.write(render_text(doc, a.notes))
    print(f"{doc['n']} slides", file=sys.stderr)


if __name__ == '__main__':
    main()
