#!/usr/bin/env python3
"""Behavior tests of exported-file conventions, including the reported failures."""
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape
from check_slide_conventions import audit

A='http://schemas.openxmlformats.org/drawingml/2006/main'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'

def shape(i,text,name='',filled=False,x=100,y=100,w=1000,h=400,center=True):
    fill='<a:solidFill><a:srgbClr val="EEEEEE"/></a:solidFill>' if filled else '<a:noFill/>'
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{escape(name)}"/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"/>{fill}</p:spPr><p:txBody><a:bodyPr anchor="{"ctr" if center else "t"}" lIns="10" rIns="10" tIns="10" bIns="10"/><a:p><a:pPr algn="{"ctr" if center else "l"}"/><a:r><a:t>{escape(text)}</a:t></a:r></a:p></p:txBody></p:sp>'

def deck(path,slides):
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('ppt/presentation.xml',f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst>'+''.join(f'<p:sldId id="{i+256}" r:id="r{i}"/>' for i in range(len(slides)))+'</p:sldIdLst><p:sldSz cx="20000" cy="12000"/></p:presentation>')
        z.writestr('ppt/_rels/presentation.xml.rels',f'<Relationships xmlns="{REL}">'+''.join(f'<Relationship Id="r{i}" Target="slides/slide{i+1}.xml" Type="{R}/slide"/>' for i in range(len(slides)))+'</Relationships>')
        for i,s in enumerate(slides,1):
            z.writestr(f'ppt/slides/slide{i}.xml',f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>{s}</p:spTree></p:cSld></p:sld>')

def refs(body,foot):
    return shape(1,body)+shape(2,foot,'reference-footer:test',y=10000,w=18000)

class ConventionTests(unittest.TestCase):
    def run_audit(self,slides):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'case.pptx';deck(p,slides);return audit(p)
    def test_consecutive_reused_sources_and_centered_nodes(self):
        r=self.run_audit([refs('Claim[1] and[2]','[1] A [2] B')+shape(3,'GSK3B','node-label:GSK3B',True,y=1000),refs('Repeat[1], new[3]','[1] A [3] C')])
        self.assertEqual(r['status'],'pass');self.assertEqual(r['checked_node_labels'],1)
    def test_late_added_opening_source_and_unsorted_footer(self):
        r=self.run_audit([refs('Structure[20], claim[1]','[20] Structure [1] Claim')])
        self.assertEqual({v['code'] for v in r['findings']},{'footer_order','citation_first_use','citation_reading_order'})
    def test_new_markers_must_ascend_in_reading_order(self):
        ok=refs('First[1] then[2] then[3]','[1] A [2] B [3] C')
        self.assertEqual(self.run_audit([ok])['status'],'pass')
        bad=shape(1,'Early[2]',y=100)+shape(2,'Later[1]',y=5000)+shape(3,'Last[3]',y=9000)+shape(4,'[1] A [2] B [3] C','reference-footer:t',y=10000,w=18000)
        self.assertIn('citation_reading_order',[v['code'] for v in self.run_audit([bad])['findings']])
    def test_overlay_and_noncentered_native_text(self):
        s=shape(1,'',filled=True,x=100,y=100,w=1000,h=600)+shape(2,'GSK3B',x=150,y=150,w=600,h=150,center=False)+shape(3,'ATP',filled=True,x=2000,center=False)
        codes={v['code'] for v in self.run_audit([s])['findings']}
        self.assertTrue({'separate_node_label_overlay','node_horizontal_alignment','node_vertical_alignment'}<=codes)
    def test_unmatched_marker_and_intentional_prose(self):
        r=self.run_audit([refs('Only[1]','[1] A [2] B')+shape(3,'Prose paragraph','prose:explanation',True,y=500,center=False)])
        self.assertEqual(r['checked_node_labels'],0);self.assertIn('citation_links',[v['code'] for v in r['findings']])
    def test_declared_optical_correction_matches_native_insets(self):
        s=shape(1,'GSK3B','node-label:GSK3B|optical-y=4',True).replace('tIns="10" bIns="10"','tIns="152400" bIns="50800"')
        self.assertEqual(self.run_audit([s])['status'],'pass')
        wrong=s.replace('optical-y=4','optical-y=2')
        self.assertIn('node_asymmetric_insets',[v['code'] for v in self.run_audit([wrong])['findings']])

if __name__=='__main__':unittest.main()
