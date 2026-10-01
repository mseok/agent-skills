#!/usr/bin/env python3
"""Flag Korean declarative endings in editable PPTX slide/table/chart text."""
import argparse
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
ENDINGS = (
    '한다', '된다', '하다', '했다', '됐다', '였다', '었다', '았다',
    '있다', '없다', '이다', '아니다', '않다', '같다', '다르다',
    '높다', '낮다', '크다', '작다', '준다', '낸다', '는다',
    '습니다', '합니다', '됩니다', '입니다', '합니다만',
)
WORDS = re.compile(r'[가-힣]+')
LATIN_AUTHOR_DENG = re.compile(r'\b[A-Z][A-Za-z\-]+(?: & [A-Z][A-Za-z\-]+)?\s*등(?:은|이|의|을|를|과|와)?')
END_CONTEXT = re.compile(r'^(?:[ \t]*\[[0-9,; –—-]+\])*[ \t]*[”’"\')]*(?:[.!?。！？;…,:/|→]|$)')


def declarative_endings(text):
    """Conservative suffix check, not a full Korean morphological parser."""
    hits = []
    for line in text.splitlines():
        for match in WORDS.finditer(line):
            word = match.group()
            # Present-tense -ㄴ다, e.g. 정한다/높인다/바뀐다. 판다 is ambiguous.
            n_da = len(word) > 2 and word.endswith('다') and (ord(word[-2]) - 0xAC00) % 28 == 4
            if (word.endswith(ENDINGS) or n_da) and END_CONTEXT.match(line[match.end():]):
                hits.append(word)
    return hits


def target_part(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), target)) if not target.startswith('/') else target.lstrip('/')


def relationships(archive, part):
    name = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if name not in archive.namelist():
        return {}
    return {
        item.attrib['Id']: target_part(part, item.attrib['Target'])
        for item in ET.fromstring(archive.read(name))
        if item.get('TargetMode') != 'External'
    }


def paragraph_text(node):
    return ''.join('\n' if el.tag == '{' + NS['a'] + '}br' else (el.text or '')
                   for el in node.iter() if el.tag in ('{' + NS['a'] + '}t', '{' + NS['a'] + '}br'))


def paragraphs(tree, slide, part, object_id, object_name):
    for index, node in enumerate(tree.findall('.//a:p', NS), 1):
        text = paragraph_text(node)
        if text.strip():
            yield dict(slide=slide, part=part, object_id=object_id,
                       object_name=object_name, paragraph=index, text=text)


def text_records(path):
    with zipfile.ZipFile(path) as archive:
        presentation = 'ppt/presentation.xml'
        links = relationships(archive, presentation)
        root = ET.fromstring(archive.read(presentation))
        for slide, entry in enumerate(root.findall('p:sldIdLst/p:sldId', NS), 1):
            part = links[entry.attrib['{' + NS['r'] + '}id']]
            tree = ET.fromstring(archive.read(part))
            if tree.get('show') == '0':
                continue
            slide_links = relationships(archive, part)
            for obj in tree.iter():
                if obj.tag not in ('{' + NS['p'] + '}sp', '{' + NS['p'] + '}graphicFrame'):
                    continue
                identity = obj.find('.//p:cNvPr', NS)
                if identity is not None and identity.get('hidden') == '1':
                    continue
                oid = identity.get('id', '') if identity is not None else ''
                name = identity.get('name', '') if identity is not None else ''
                yield from paragraphs(obj, slide, part, oid, name)
                for chart in obj.findall('.//c:chart', NS):
                    chart_part = slide_links[chart.attrib['{' + NS['r'] + '}id']]
                    chart_tree = ET.fromstring(archive.read(chart_part))
                    yield from paragraphs(chart_tree, slide, chart_part, oid, name)
                    for index, val in enumerate(chart_tree.findall('.//c:strCache/c:pt/c:v', NS), 1):
                        yield dict(slide=slide, part=chart_part, object_id=oid,
                                   object_name=name, paragraph='cache-' + str(index), text=val.text or '')


def check(path, exceptions=()):
    records = list(text_records(path))
    findings = []
    identity_fields = ('part', 'object_id', 'paragraph', 'text')
    for item in exceptions:
        if not all(key in item for key in identity_fields) or not item.get('reason', '').strip():
            raise ValueError('Each literal-source exception needs part, object_id, paragraph, text and reason.')
    for record in records:
        hits = declarative_endings(record['text'])
        if hits:
            finding = dict(record, rule='ko-declarative-ending', matches=hits)
            exception = next((item for item in exceptions if all(item[key] == record[key] for key in identity_fields)), None)
            if exception:
                finding['exception_reason'] = exception['reason']
            findings.append(finding)
    # Author notation stays Latin ("Lowry et al."), on slides and in speaker notes.
    for record in records:
        hits = LATIN_AUTHOR_DENG.findall(record['text'])
        if hits:
            findings.append(dict(record, rule='latin-author-deng', matches=hits))
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', name):
                text = ' '.join(paragraph_text(p) for p in ET.fromstring(archive.read(name)).iter('{' + NS['a'] + '}p'))
                hits = LATIN_AUTHOR_DENG.findall(text)
                if hits:
                    findings.append({'part': name, 'object_id': None, 'paragraph': None, 'text': text[:80], 'rule': 'latin-author-deng-notes', 'matches': hits})
    unresolved = sum('exception_reason' not in finding for finding in findings)
    return {
        'input': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'status': 'fail' if unresolved else 'pass', 'unresolved': unresolved,
        'checked_paragraphs': len(records), 'findings': findings,
        'scope': 'Editable slide shapes, tables and linked chart text in presentation order (declarative endings); the Latin-author + 등 rule also scans speaker notes. Hidden slides, master-only text and raster image text excluded. Heuristic suffix detection, not full morphology. No automatic rewriting.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--exceptions', type=Path, help='Exact literal-source exceptions with reasons; never author-written prose.')
    args = parser.parse_args()
    exceptions = json.loads(args.exceptions.read_text()) if args.exceptions else []
    result = check(args.pptx, exceptions)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + '\n')
    print(output)
    raise SystemExit(1 if result['unresolved'] else 0)


if __name__ == '__main__':
    main()
