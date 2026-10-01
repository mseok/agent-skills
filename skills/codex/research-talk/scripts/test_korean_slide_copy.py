"""Behavior checks for the Korean copy gate; synthetic OOXML, no user edits."""
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from check_korean_slide_copy import NS, check, declarative_endings


def fixture(path, nominal=False):
    a, p, r, c = (NS[k] for k in ('a', 'p', 'r', 'c'))
    ns = f'xmlns:a="{a}" xmlns:p="{p}" xmlns:r="{r}" xmlns:c="{c}"'
    subtitle = 'CHEK1 구조 기반 결합 가설' if nominal else 'CHEK1 구조는 결합 가설과 선택성 검증을 연결'
    suffix = '' if nominal else '한다 [15]'
    table = '활성 증가' if nominal else '활성이 증가한다'
    chart = '농도 차이' if nominal else '농도가 다르다'
    parts = {
        'ppt/presentation.xml': f'<p:presentation {ns}><p:sldIdLst><p:sldId id="257" r:id="B"/><p:sldId id="256" r:id="A"/></p:sldIdLst></p:presentation>',
        'ppt/_rels/presentation.xml.rels': f'<Relationships xmlns="{NS["rel"]}"><Relationship Id="A" Target="slides/slide1.xml"/><Relationship Id="B" Target="slides/slide2.xml"/></Relationships>',
        'ppt/slides/slide1.xml': f'<p:sld {ns}><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="noun"/></p:nvSpPr><p:txBody><a:p><a:r><a:t>캐나다·람다·바다 연구</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>',
        'ppt/slides/slide2.xml': f'<p:sld {ns}><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="subtitle"/></p:nvSpPr><p:txBody><a:p><a:r><a:t>{subtitle}</a:t></a:r><a:r><a:t>{suffix}</a:t></a:r></a:p></p:txBody></p:sp><p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="3" name="table"/></p:nvGraphicFramePr><a:graphic><a:graphicData><a:tbl><a:tr><a:tc><a:txBody><a:p><a:r><a:t>{table}</a:t></a:r></a:p></a:txBody></a:tc></a:tr></a:tbl></a:graphicData></a:graphic></p:graphicFrame><p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="4" name="chart"/></p:nvGraphicFramePr><a:graphic><a:graphicData><c:chart r:id="chart"/></a:graphicData></a:graphic></p:graphicFrame></p:spTree></p:cSld></p:sld>',
        'ppt/slides/_rels/slide2.xml.rels': f'<Relationships xmlns="{NS["rel"]}"><Relationship Id="chart" Target="charts/custom.xml"/></Relationships>',
        'ppt/slides/charts/custom.xml': f'<c:chartSpace {ns}><c:chart><c:title><c:tx><c:rich><a:p><a:r><a:t>{chart}</a:t></a:r></a:p></c:rich></c:tx></c:title></c:chart></c:chartSpace>',
        'ppt/notesSlides/notesSlide2.xml': f'<p:notes {ns}><a:p><a:r><a:t>발표 대본은 설명한다</a:t></a:r></a:p></p:notes>',
    }
    with zipfile.ZipFile(path, 'w') as archive:
        for name, content in parts.items():
            archive.writestr(name, content)


class KoreanCopyTests(unittest.TestCase):
    def test_sentence_variants_and_nominal_copy(self):
        for text in ['검증한다 [1, 2].', '실험 결과가 있다 / 후속 검증', '결합하지 않는다',
                     '농도를 높인다', '구조가 바뀐다', '실험을 수행했습니다.', '활성은 미확인이다']:
            with self.subTest(text=text):
                self.assertTrue(declarative_endings(text))
        for text in ['결합 가설과 선택성 검증', '수소결합 수용 가능성', '세포 반응: 미검증',
                     '캐나다·람다·바다', 'Lowry et al., 2005', '결합한다는 가설']:
            with self.subTest(text=text):
                self.assertEqual(declarative_endings(text), [])

    def test_package_order_split_runs_table_chart_and_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.pptx'
            fixture(path)
            before = path.read_bytes()
            result = check(path)
            self.assertEqual(result['unresolved'], 3)
            self.assertEqual({x['slide'] for x in result['findings']}, {1})
            self.assertEqual({x['object_name'] for x in result['findings']}, {'subtitle', 'table', 'chart'})
            self.assertIn('연결한다 [15]', result['findings'][0]['text'])
            self.assertEqual(path.read_bytes(), before)

    def test_exact_exception_keeps_other_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.pptx'
            fixture(path)
            finding = check(path)['findings'][0]
            exception = {key: finding[key] for key in ('part', 'object_id', 'paragraph', 'text')}
            exception['reason'] = 'Synthetic literal-source exception test only'
            result = check(path, [exception])
            self.assertEqual(result['unresolved'], 2)
            self.assertEqual(len(result['findings']), 3)
            with self.assertRaises(ValueError):
                check(path, [{'reason': 'broad bypass'}])

    def test_cli_fails_bad_copy_and_passes_nominal_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.pptx'
            report = Path(directory) / 'qa' / 'report.json'
            script = Path(__file__).with_name('check_korean_slide_copy.py')
            for nominal, code in [(False, 1), (True, 0)]:
                fixture(path, nominal)
                process = subprocess.run([sys.executable, str(script), str(path), '--report', str(report)], capture_output=True, text=True)
                self.assertEqual(process.returncode, code, process.stderr)
                self.assertEqual(json.loads(report.read_text())['status'], 'pass' if nominal else 'fail')


if __name__ == '__main__':
    unittest.main()
