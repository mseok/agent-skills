#!/usr/bin/env python3
"""Measure visible dark label ink against native node centers in matching PNG renders.

Requires Pillow and numpy. Read-only; no image/deck edits. Use final native-PDF
renders. Supports unrotated top-level nodes with dark text on light backgrounds.
Colored/white text, nested groups, overlaps and unusual borders need manual QA.
A small residual is a review tolerance, not proof of optical perfection.
"""
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import numpy as np
from PIL import Image
from check_slide_conventions import NS, relationships, paragraph_text, rect


def ink_bounds(rgb):
    mask=(rgb.max(axis=2)<110) & ((rgb.max(axis=2).astype(int)-rgb.min(axis=2))<55)
    ys,xs=np.where(mask)
    if len(ys)<5:
        return None
    return int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())


def audit(path,pattern,tolerance=0.08):
    rows=[];manual=[]
    with zipfile.ZipFile(path) as z:
        p=ET.fromstring(z.read('ppt/presentation.xml'));sz=p.find('p:sldSz',NS)
        sw,sh=int(sz.get('cx')),int(sz.get('cy'));links=relationships(z,'ppt/presentation.xml')
        for index,e in enumerate(p.findall('p:sldIdLst/p:sldId',NS),1):
            root=ET.fromstring(z.read(links[e.get('{'+NS['r']+'}id')]))
            if root.get('show')=='0':continue
            im=Image.open(pattern.format(slide=index)).convert('RGB');pixels=np.array(im)
            for parent in root.iter():
                if parent.tag not in ('{'+NS['p']+'}spTree','{'+NS['p']+'}grpSp'):continue
                for s in parent.findall('p:sp',NS):
                    ident=s.find('p:nvSpPr/p:cNvPr',NS)
                    if ident is None or not ident.get('name','').startswith('node-label:') or ident.get('hidden')=='1':continue
                    text='\n'.join(paragraph_text(v) for v in s.findall('p:txBody/a:p',NS))
                    item={'slide':index,'object_id':ident.get('id'),'name':ident.get('name'),'text':text}
                    bounds=rect(s)
                    if bounds is None or parent.tag.endswith('grpSp'):
                        manual.append({**item,'reason':'Grouped/rotated coordinates require manual review'});continue
                    sizes=[int(v.get('sz'))/100 for v in s.findall('.//a:rPr',NS)+s.findall('.//a:defRPr',NS) if v.get('sz')]
                    if not sizes:
                        manual.append({**item,'reason':'Inherited font size requires manual review'});continue
                    x,y,w,h=bounds;xf,yf=im.width/sw,im.height/sh
                    x0,y0,x1,y1=round(x*xf),round(y*yf),round((x+w)*xf),round((y+h)*yf)
                    pad=max(2,round(min(x1-x0,y1-y0)*0.05))
                    crop=pixels[y0+pad:y1-pad,x0+pad:x1-pad]
                    ink=ink_bounds(crop)
                    if ink is None:
                        manual.append({**item,'reason':'No isolated dark label ink detected'});continue
                    a,b,c,d=ink
                    # Pixel centers, measured in original slide physical points.
                    dx=((a+c+1)/2+x0+pad-(x+w/2)*xf)/xf/12700
                    dy=((b+d+1)/2+y0+pad-(y+h/2)*yf)/yf/12700
                    limit=max(1.0,max(sizes)*tolerance)
                    edge=a==0 or b==0 or c==crop.shape[1]-1 or d==crop.shape[0]-1
                    if edge:
                        manual.append({**item,'reason':'Ink touches crop edge; inspect border, clipping or overlap'});continue
                    rows.append({**item,'offset_x_pt':round(dx,3),'offset_y_pt':round(dy,3),'suggested_optical_y_correction_pt':round(-dy,3),'tolerance_pt':round(limit,3),'status':'review' if abs(dx)>limit or abs(dy)>limit else 'pass'})
    findings=[r for r in rows if r['status']=='review']
    return {'input':str(path),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'render_pattern':pattern,'status':'review' if findings or manual else 'pass','checked':len(rows),'findings':findings,'manual_review':manual,'nodes':rows,'scope':__doc__}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pptx',type=Path);p.add_argument('--renders',required=True,help='PNG path pattern with {slide}');p.add_argument('--report',type=Path,required=True);p.add_argument('--tolerance-em',type=float,default=.08);a=p.parse_args()
    result=audit(a.pptx,a.renders,a.tolerance_em);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','checked','findings','manual_review')},ensure_ascii=False,indent=2));raise SystemExit(result['status']!='pass')
