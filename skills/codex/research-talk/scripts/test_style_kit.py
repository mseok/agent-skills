#!/usr/bin/env python3
"""Smoke test for assets/style-kit.mjs: syntax check, then build assets/kit-demo.mjs into a temp dir and count slides.

Needs the Codex runtime node (it provides @oai/artifact-tool). Skips when the runtime is absent.
"""
import os, shutil, subprocess, tempfile, unittest, zipfile
from pathlib import Path

RUNTIME = Path('/Users/mseok/.cache/codex-runtimes/codex-primary-runtime/dependencies/node')
ASSETS = Path(__file__).resolve().parent.parent / 'assets'


@unittest.skipUnless((RUNTIME / 'bin/node').exists(), 'Codex runtime node not available')
class StyleKitTests(unittest.TestCase):
    def test_syntax_and_demo_build(self):
        node = str(RUNTIME / 'bin/node')
        subprocess.run([node, '--check', str(ASSETS / 'style-kit.mjs')], check=True)
        with tempfile.TemporaryDirectory() as td:
            for f in ('style-kit.mjs', 'kit-demo.mjs'):
                shutil.copy(ASSETS / f, td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            subprocess.run([node, 'kit-demo.mjs'], cwd=td, check=True, capture_output=True, timeout=180)
            with zipfile.ZipFile(Path(td) / 'kit-demo.pptx') as z:
                slides = [n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            self.assertEqual(len(slides), 4)

    def test_leader_is_flipped_bounding_box(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {PresentationFile} from '@oai/artifact-tool';"
                  "import {createDeck,slide,leader} from './style-kit.mjs';"
                  "const p=createDeck();const s=slide(p,'method',{title:'T',subtitle:'s',section:'x'});"
                  "leader(s,300,400,500,520);leader(s,300,800,500,680);"
                  "await (await PresentationFile.exportPptx(p)).save('l.pptx');")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180)
            with zipfile.ZipFile(Path(td) / 'l.pptx') as z:
                xml = z.read('ppt/slides/slide1.xml').decode()
            self.assertNotIn('rot=', xml.split('figure-leader', 1)[1])
            self.assertEqual(xml.count('flipV="1"'), 1)   # only the up-right leader is flipped

    def test_subtitle_marker_and_two_line_closing(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {PresentationFile} from '@oai/artifact-tool';"
                  "import {createDeck,slide} from './style-kit.mjs';"
                  "const p=createDeck();slide(p,'method',{title:'T',subtitle:'Apo state [[ref|[1]]]',section:'x',"
                  "takeaway:'A closing line that is long enough to need a second line when set at forty points across the whole band of the slide'});"
                  "await (await PresentationFile.exportPptx(p)).save('s.pptx');")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180)
            with zipfile.ZipFile(Path(td) / 's.pptx') as z:
                xml = z.read('ppt/slides/slide1.xml').decode()
        self.assertIn('sz="3000"', xml)              # the marker run: 0.75 x 40 pt
        self.assertIn('y="10820400"', xml)           # two-line closing at y 852

    def test_rich_marker_is_smaller_than_body(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {PresentationFile} from '@oai/artifact-tool';"
                  "import {createDeck,slide,rich,textWidth} from './style-kit.mjs';"
                  "const p=createDeck();const s=slide(p,'method',{title:'T',subtitle:'s',section:'x'});"
                  "rich(s,'Body text [[ref|[3]]] more',95,300,1000,60,40);"
                  "console.error('W',textWidth('가나다',40),textWidth('abc',40));"
                  "await (await PresentationFile.exportPptx(p)).save('s.pptx');")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            r = subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180, text=True)
            with zipfile.ZipFile(Path(td) / 's.pptx') as z:
                xml = z.read('ppt/slides/slide1.xml').decode()
        self.assertIn('sz="4000"', xml)
        self.assertIn('sz="3000"', xml)              # `[[ref|…]]` = 0.75 x 40 pt, not overridden by a shape-level size
        self.assertIn('W 103.68', r.stderr)           # Hangul 0.864 em x 3 x 40 pt

    def test_table_marker_cells_keep_run_sizes(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {PresentationFile} from '@oai/artifact-tool';"
                  "import {createDeck,slide,table} from './style-kit.mjs';"
                  "const p=createDeck();const s=slide(p,'table-case',{title:'T',subtitle:'s',section:'x'});"
                  "table(s,[['Model','Type'],['Boltz-2 [[ref|[7]]]','Euclidean']],95,300,1000,300,[500,500],{size:36,headerAnchor:'bottom'});"
                  "await (await PresentationFile.exportPptx(p)).save('s.pptx');")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180)
            with zipfile.ZipFile(Path(td) / 's.pptx') as z:
                xml = z.read('ppt/slides/slide1.xml').decode()
        self.assertIn('sz="3600"', xml)
        self.assertIn('sz="2700"', xml)              # `[[ref|…]]` = 0.75 x 36 pt in a table cell
        self.assertIn('anchor="b"', xml)             # header anchored to the bottom

    def test_box_markup_label_and_inhibit_x(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {PresentationFile} from '@oai/artifact-tool';"
                  "import {createDeck,slide,box,inhibitX} from './style-kit.mjs';"
                  "const p=createDeck();const s=slide(p,'method',{title:'T',subtitle:'s',section:'x'});"
                  "box(s,'GSK3B [[ref|[4]]]\\nkinase',300,400,400,160,{size:40,geometry:'ellipse'});inhibitX(s,900,480);"
                  "await (await PresentationFile.exportPptx(p)).save('s.pptx');")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180)
            with zipfile.ZipFile(Path(td) / 's.pptx') as z:
                xml = z.read('ppt/slides/slide1.xml').decode()
        self.assertIn('sz="3000"', xml)               # the marker inside a node label: 0.75 x 40 pt
        self.assertNotIn('lIns="254000"', xml)
        self.assertIn('name="inhibition-x"', xml)
        self.assertIn('prst="plus"', xml)

    def test_default_family_is_pretendard(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {FAMILY,REFERENCE_PT,setFamily} from './style-kit.mjs';"
                  "const a=[FAMILY,REFERENCE_PT];setFamily('Apple SD Gothic Neo');const b=[FAMILY,REFERENCE_PT];"
                  "console.log(JSON.stringify({a,b}));")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            out = subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180, text=True).stdout
        self.assertIn('"a":["Pretendard",20]', out)
        self.assertIn('"b":["Apple SD Gothic Neo",20.5]', out)

    def test_category_text_tones_are_rejected(self):
        node = str(RUNTIME / 'bin/node')
        script = ("import {runsFrom} from './style-kit.mjs';"
                  "let msg='';try{runsFrom('[[purple|x]]');}catch(e){msg=e.message;}"
                  "let ok=runsFrom('[[red|a]] [[b|b]] [[navy|c]]').length>=3;"
                  "console.log(JSON.stringify({msg,ok}));")
        with tempfile.TemporaryDirectory() as td:
            shutil.copy(ASSETS / 'style-kit.mjs', td)
            os.symlink(RUNTIME / 'node_modules', Path(td) / 'node_modules')
            Path(td, 't.mjs').write_text(script)
            out = subprocess.run([node, 't.mjs'], cwd=td, check=True, capture_output=True, timeout=180, text=True).stdout
        self.assertIn('not allowed', out)
        self.assertIn('"ok":true', out)


if __name__ == '__main__':
    unittest.main()
