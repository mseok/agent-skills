#!/usr/bin/env python3
"""check_layout_quality.py flags node labels with non-zero side insets (Apple's renderer shifts centred text right by the inset)."""
import json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'check_layout_quality.py'
EMU = 12700


def sp(name, lins):
    return ('<p:sp><p:nvSpPr><p:cNvPr id="1" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="ellipse"/><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></p:spPr>'
            '<p:txBody><a:bodyPr lIns="%d" rIns="%d"/><a:p><a:r><a:rPr sz="3000"/><a:t>GSK3B</a:t></a:r></a:p></p:txBody></p:sp>') % (name, 400 * EMU, 400 * EMU, 400 * EMU, 200 * EMU, lins * EMU, lins * EMU)


def run(lins):
    ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
    slide = '<p:sld %s><p:cSld><p:spTree>%s</p:spTree></p:cSld></p:sld>' % (ns, sp('node-label:GSK3B', lins))
    pres = '<p:presentation %s><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="%d" cy="%d"/></p:presentation>' % (ns, 1920 * EMU, 1080 * EMU)
    rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/></Relationships>'
    with tempfile.TemporaryDirectory() as td:
        pp = Path(td, 'a.pptx')
        with zipfile.ZipFile(pp, 'w') as z:
            z.writestr('ppt/presentation.xml', pres); z.writestr('ppt/_rels/presentation.xml.rels', rels); z.writestr('ppt/slides/slide1.xml', slide)
        from PIL import Image
        Image.new('RGB', (192, 108), 'white').save(Path(td, 'slide-01.png'))
        out = subprocess.run([sys.executable, str(SCRIPT), str(pp), '--renders', td], capture_output=True, text=True)
        return [f['code'] for f in json.loads(out.stdout)['findings']]


class NodeInsetTests(unittest.TestCase):
    def test_nonzero_inset_flagged(self):
        self.assertIn('node-inset', run(20))

    def test_zero_inset_clean(self):
        self.assertNotIn('node-inset', run(0))


if __name__ == '__main__':
    unittest.main()
