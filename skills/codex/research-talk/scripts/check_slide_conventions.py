#!/usr/bin/env python3
"""Read-only exported PPTX check: numeric citations and diagram-label alignment.

Checks editable shapes, not raster labels or optical font alignment. Group-local
coordinates are compared only within the same group. No automatic mutation.
"""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from check_korean_slide_copy import NS, relationships, paragraph_text

MARKER = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')

def numbers(text):
    return [int(n) for group in MARKER.findall(text) for n in group.split(',')]

def rect(shape):
    x = shape.find('p:spPr/a:xfrm', NS)
    if x is None:
        return None
    off, ext = x.find('a:off', NS), x.find('a:ext', NS)
    if off is None or ext is None or x.get('rot', '0') != '0':
        return None
    return tuple(int(off.get(k)) for k in ('x', 'y')) + tuple(int(ext.get(k)) for k in ('cx', 'cy'))

def contained(inner, outer):
    x,y,w,h=inner; a,b,c,d=outer
    return x>=a and y>=b and x+w<=a+c and y+h<=b+d

def audit(path):
    findings=[]; summaries=[]; seen=set(); checked=0; chart_parts={}
    def add(slide, code, obj, detail):
        findings.append(dict(slide=slide,code=code,object_id=obj.get('id'),object_name=obj.get('name'),text=obj.get('text',''),detail=detail))
    with zipfile.ZipFile(path) as z:
        presentation=ET.fromstring(z.read('ppt/presentation.xml'))
        slide_height=int(presentation.find('p:sldSz',NS).get('cy'))
        links=relationships(z,'ppt/presentation.xml')
        for index, entry in enumerate(presentation.findall('p:sldIdLst/p:sldId',NS),1):
            slide_part=links[entry.get('{'+NS['r']+'}id')]
            tree=ET.fromstring(z.read(slide_part))
            for rid,target in relationships(z,slide_part).items():
                chart_parts[(index,rid)]=target
            if tree.get('show')=='0':
                continue
            body=[];foot=[];footer_objects=[];marker_items=[]
            for parent in tree.iter():
                if parent.tag not in ('{'+NS['p']+'}spTree','{'+NS['p']+'}grpSp'):
                    continue
                objects=[]
                for shape in parent.findall('p:sp',NS):
                    identity=shape.find('p:nvSpPr/p:cNvPr',NS)
                    if identity is None or identity.get('hidden')=='1':
                        continue
                    paras=shape.findall('p:txBody/a:p',NS)
                    text='\n'.join(paragraph_text(p) for p in paras).strip()
                    bounds=rect(shape); name=identity.get('name','')
                    pr=shape.find('p:spPr',NS)
                    filled=pr is not None and (pr.find('a:solidFill',NS) is not None or pr.find('a:gradFill',NS) is not None)
                    item=dict(id=identity.get('id'),name=name,text=text,bounds=bounds,filled=filled,shape=shape,paras=paras)
                    objects.append(item)
                    # Prefix is the authoring contract; legacy footer heuristic enables regression checks.
                    legacy=bool(bounds and bounds[1]>=slide_height*0.85 and re.search(r'et al\.|BindingDB|ChEMBL|PubChem|& He',text))
                    is_footer=name.startswith('reference-footer:') or legacy
                    if is_footer:
                        footer_objects.append(item)
                    else:
                        body.extend(numbers(text))
                        if bounds and numbers(text):
                            marker_items.append((bounds,numbers(text)))
                    node=name.startswith('node-label:') or (filled and 0<len(text)<=80 and len(paras)<=3 and not name.startswith(('prose:','figure-label:')))
                    if node:
                        checked+=1
                        bp=shape.find('p:txBody/a:bodyPr',NS)
                        if bp is None or bp.get('anchor')!='ctr':
                            add(index,'node_vertical_alignment',item,'Require explicit native middle anchor (anchor=ctr).')
                        for pi,p in enumerate(paras):
                            if not paragraph_text(p).strip():
                                continue
                            pp=p.find('a:pPr',NS)
                            if pp is None or pp.get('algn')!='ctr':
                                add(index,'node_horizontal_alignment',item,'Every node-label paragraph requires explicit center alignment.')
                            if pp is not None:
                                size=next((int(r.get('sz')) for r in p.iter('{'+NS['a']+'}rPr') if r.get('sz')),4000)
                                for tag in ('spcBef','spcAft'):
                                    sp=pp.find('a:'+tag,NS)
                                    if sp is None:
                                        continue
                                    for v in sp:
                                        val=int(v.get('val','0'))
                                        # Later lines may carry up to 0.3 em before them (the 1.2x look without a line-spacing multiplier).
                                        allowed=int(0.3*size) if (tag=='spcBef' and pi>0 and v.tag.endswith('spcPts')) else 0
                                        if val>allowed:
                                            add(index,'node_paragraph_spacing',item,'Node labels allow zero paragraph spacing, except up to 0.3 em before later lines.')
                        if bp is not None:
                            # OOXML defaults: left/right0.1in, top/bottom0.05in.
                            vals={k:int(bp.get(k,str(default))) for k,default in [('lIns',91440),('rIns',91440),('tIns',45720),('bIns',45720)]}
                            optical=re.search(r'\|optical-y=(-?\d+(?:\.\d+)?)$',name)
                            expected_delta=2*float(optical.group(1))*12700 if optical else 0
                            if vals['lIns']!=vals['rIns'] or abs(vals['tIns']-vals['bIns']-expected_delta)>2:
                                add(index,'node_asymmetric_insets',item,'Use balanced insets, or a declared measured optical-y offset consistent with the native insets. Optical offsets also require rendered QA.')
                # Blank container + separate short textbox reproduces the GSK3B misalignment failure.
                for outer in objects:
                    if not outer['filled'] or outer['text'] or not outer['bounds'] or outer['name'].startswith('prose:'):
                        continue
                    for inner in objects:
                        if inner['filled'] or not (0<len(inner['text'])<=80) or not inner['bounds']:
                            continue
                        if contained(inner['bounds'],outer['bounds']):
                            add(index,'separate_node_label_overlay',inner,'Short label is a separate textbox inside blank filled shape '+outer['id']+'. Use the container native text body.')
            for frame in tree.iter('{'+NS['p']+'}graphicFrame'):
                body.extend(numbers(' '.join(t.text or '' for t in frame.iter('{'+NS['a']+'}t'))))
                # Native charts: markers inside category names, series names and titles count as point-of-use markers.
                for ch in frame.iter('{http://schemas.openxmlformats.org/drawingml/2006/chart}chart'):
                    rid=ch.get('{'+NS['r']+'}id')
                    chart_part=chart_parts.get((index,rid))
                    if chart_part and chart_part in z.namelist():
                        croot=ET.fromstring(z.read(chart_part))
                        ctext=' '.join((e.text or '') for e in croot.iter() if e.tag.endswith('}v') or e.tag.endswith('}t'))
                        body.extend(numbers(ctext))
            for obj in sorted(footer_objects,key=lambda o:(o['bounds'][1],o['bounds'][0]) if o['bounds'] else (0,0)):
                foot.extend(numbers(obj['text']))
            if foot != sorted(set(foot)):
                add(index,'footer_order',{},'Footer references must appear once in ascending numeric order: '+str(foot))
            if set(body)!=set(foot):
                add(index,'citation_links',{},'Body-only '+str(sorted(set(body)-set(foot)))+'; footer-only '+str(sorted(set(foot)-set(body))))
            new=sorted(set(foot)-seen)
            expected=list(range(len(seen)+1,len(seen)+1+len(new)))
            if new!=expected:
                add(index,'citation_first_use',{},'New references must continue consecutively from1: expected '+str(expected)+'; found '+str(new))
            # New references must also be introduced in reading order within the slide (row-major or column-major).
            if len(new)>1 and marker_items:
                slide_w=int(presentation.find('p:sldSz',NS).get('cx'))
                def first_seq(key):
                    order=[];
                    for b,nums in sorted(marker_items,key=lambda it:key(it[0])):
                        for n in nums:
                            if n in new and n not in order:
                                order.append(n)
                    return order
                row=first_seq(lambda b:(round(b[1]/(slide_height/12)),b[0]))
                col=first_seq(lambda b:(round(b[0]/(slide_w/6)),b[1]))
                if row!=sorted(row) and col!=sorted(col):
                    add(index,'citation_reading_order',{},'New markers are introduced out of reading order (row-major '+str(row)+', column-major '+str(col)+'); renumber so they ascend as the slide is read.')
            seen.update(foot)
            summaries.append(dict(slide=index,body_markers=sorted(set(body)),footer_markers=foot,new_markers=new))
    return dict(input=str(path),sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),status='fail' if findings else 'pass',checked_node_labels=checked,slides=summaries,findings=findings,scope='Native editable slide shapes; explicit alignment and same-group geometry, not optical centering. Verify reading order and source semantics visually. Charts/tables/raster citations need separate source-map review.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pptx',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    result=audit(a.pptx);s=json.dumps(result,ensure_ascii=False,indent=2)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(s+'\n')
    print(s);return int(result['status']!='pass')

if __name__=='__main__':
    raise SystemExit(main())
