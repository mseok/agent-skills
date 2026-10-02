import { Presentation } from '@oai/artifact-tool';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

// Source coordinates are Keynote points on a 1920 x 1080 canvas.
// Artifact Tool uses CSS pixels. Keep the source's physical size, not just ratio.
export const S = 4 / 3;
export const C = { ink:'#000000', muted:'#666666', light:'#DDDDDD', pale:'#F7F7F7', accent:'#1F77B4', green:'#66A34A', orange:'#C9993F', purple:'#9977AA',
  // Sampled from the dissertation deck: emphasis red, category blue/green/orange, thin gray arrows/outlines. Fills in the dissertation PPTX are white and neutral grays (#EBEBEB #DDDDDD #CCCCCC #F7F7F7); colour lives in text and outlines.
  red:'#E02000', sky:'#00A0F0', green2:'#10B000', orange2:'#F07000', brown:'#B05000', purple2:'#9966CC', arrow:'#7A7A7A', edge:'#C8C8C8' };
// Vertical budget in source points (1080 high): header to y≈263, evidence band, closing line, reference footer (≤ 2 rows), page number.
export const BAND = { x:95, y:285, w:1730, h:555 };   // evidence incl. captions ends at y 840
export const TAKEAWAY = { x:140, y:872, w:1640, h:90 };   // one centered line; ≥ 40 pt clear below the band
export let FAMILY = 'Pretendard';   // default for every deck (Hangul + Latin + Greek in one face; installed on Mac, copy on Windows: assets/fonts, scripts/ensure_font.py)
// Vertical optical correction (source pt) for single-family decks whose line box sits low in a middle-anchored shape (measured in Artifact Tool; Pretendard +2 to +4 pt low).
const FAMILY_OPTICAL={Pretendard:-2};
export const LINE_SPACING = 1.2;
export let REFERENCE_PT = 20;
// One family for the whole deck, Korean or English: Pretendard (default; 20 pt references, x-height slightly above Helvetica Neue's). Opt-in alternatives: setFamily('Helvetica Neue') (20 pt, Mac only look) or 'Apple SD Gothic Neo' (20.5 pt).
export function setFamily(name){FAMILY=name;REFERENCE_PT=name==='Apple SD Gothic Neo'?20.5:20;}
export const kinds = ['cover','section','question','figure','comparison','method','equation','benchmark','table-case','paper','conclusion','appendix'];
export const labels = ['Cover','Section divider','Research question','Large figure','Two-way comparison','Method and pipeline','Equation and algorithm','Benchmark','Table and case study','Paper introduction','Conclusion and next steps','Appendix'];
export const frame = (x,y,w,h) => ({left:x*S,top:y*S,width:w*S,height:h*S});

export function text(slide, value, x,y,w,h,size=40, options={}) {
  const {name, ...styleOptions} = options;
  const shape = slide.shapes.add({name,geometry:'textbox',position:frame(x,y,w,h),fill:'none',line:{fill:'none',width:0}});
  shape.text = value;
  shape.text.style = {typeface:FAMILY,fontSize:size*S,lineSpacing:LINE_SPACING,color:C.ink,autoFit:'none',wrap:'square',insets:{left:0,right:0,top:0,bottom:0},...styleOptions};
  return shape;
}
export function box(slide,value,x,y,w,h,options={}) {
  // options: geometry, borderRadius ('rounded-full' = capsule, 'rounded-2xl' = soft rect; flowChartTerminator renders nothing), fill, line, lineWidth, size, bold, color, lineSpacing, insetX (default 0: Apple's renderer shifts centered text right by the left inset, so symmetric non-zero insets drift 15–20 pt there; keep ≥ 16 pt of free width on each side of the longest line instead), opticalOffsetY.
  // Optical offsets are measured from the final renderer, in source PPT points.
  const opticalY=options.opticalOffsetY??FAMILY_OPTICAL[FAMILY]??0;
  const paddingY=Math.max(Math.min(8,h*0.08),Math.abs(opticalY)+2);
  const name=(options.name??`node-label:${String(value).replace(/\[\[\w+\|/g,'').replace(/\]\](?!\])/g,'').replace(/\s+/g,' ').slice(0,50)}`)+(opticalY?`|optical-y=${opticalY}`:'');
  const shape=slide.shapes.add({name,geometry:options.geometry??'rect',position:frame(x,y,w,h),fill:options.fill??'#FFFFFF',line:{fill:options.line??C.light,width:(options.lineWidth??1)*S},...(options.borderRadius?{borderRadius:options.borderRadius}:{})});
  // Multiline labels: line spacing 1.0 plus 0.2 em before every later line. A 1.2x multiplier shifts the block 3-8 pt low in PowerPoint-like renderers
  // (and high in Keynote); paragraph spacing renders identically in both, keeps the 1.2x look and keeps the block centered.
  if(options.insetX)console.warn(`box(): insetX ignored (label "${String(value).slice(0,24)}"): symmetric side insets shift centred text right by the inset in Apple's renderer, so side insets are always 0`);
  const markup=String(value).includes('[[');   // `[[ref|[3]]]`/`[[red|…]]` inside a node label: runs carry size and colour (shape-level values would override them)
  const plainOf=l=>l.replace(/\[\[\w+\|/g,'').replace(/\]\](?!\])/g,'');
  const widest=Math.max(...String(value).split('\n').map(l=>textWidth(plainOf(l),options.size??40,options.bold)));
  const usable=(options.geometry==='ellipse'?0.72*w:w)-32;   // an ellipse holds text only in ~72 % of its width
  if(widest>usable)console.warn(`box(): label "${String(value).slice(0,30)}" (~${Math.round(widest)} pt) needs a wider ${options.geometry==='ellipse'?'ellipse (text fits in ~72 % of its width)':'box'} than ${w} pt (keep 16 pt free on each side)`);
  const lines=String(value).split("\n"),gapHundredths=Math.round(0.2*(options.size??40)*100);
  shape.text=lines.map((line,i)=>({runs:markup?runsFrom(line,{color:options.color??C.ink,size:options.size??40}).map(r=>options.bold?{...r,textStyle:{...r.textStyle,bold:true}}:r):[line],bulletCharacter:"",spaceBefore:i>0&&options.lineSpacing===undefined?gapHundredths:0,spaceAfter:0}));
  shape.text.style={typeface:FAMILY,...(markup?{}:{fontSize:(options.size??40)*S,color:options.color??C.ink}),lineSpacing:options.lineSpacing??1,alignment:'center',verticalAlignment:'middle',autoFit:'none',insets:{left:0,right:0,top:(paddingY+opticalY)*S,bottom:(paddingY-opticalY)*S},bold:options.bold??false};
  return shape;
}
export function line(slide,x,y,w,color=C.light){return slide.shapes.add({geometry:'rect',position:frame(x,y,w,1),fill:color,line:{fill:'none',width:0}});}
export function slot(slide,label,x,y,w,h){return box(slide,label,x,y,w,h,{color:C.muted,size:36});}
export function connect(slide,a,b){return slide.shapes.connect(a,b,{kind:'straight',fromSide:'right',toSide:'left',line:{fill:C.ink,width:2*S},tail:{type:'triangle',width:'med',length:'med'}});}
// A single native PowerPoint arrow, not a rectangle/triangle assembly.
export function arrow(slide,x,y,w,h,{geometry='rightArrow',color=C.arrow}={}) {
  return slide.shapes.add({geometry,position:frame(x,y,w,h),fill:color,line:{fill:'none',width:0}});
}
// Coordinates and font sizes are source PPT points; reserve footer space as needed.
export function reference(slide,value,x=650,y=1000,w=1175,h=60,options={}) {
  return text(slide,value,x,y,w,h,REFERENCE_PT,{name:'reference-footer:'+value.slice(0,40),alignment:'right',color:C.muted,...options});
}
// Pretendard is not preinstalled on Mac or Windows: createDeck() runs scripts/ensure_font.py once per process, which installs the bundled copy into the user's font folder when it is missing.
let FONT_CHECKED=false;
export function ensureFont(){
  if(FONT_CHECKED||FAMILY!=='Pretendard')return;
  FONT_CHECKED=true;
  try{
    const here=path.dirname(fileURLToPath(import.meta.url));
    const root=[process.env.RESEARCH_TALK_SKILL,path.resolve(here,'..'),'/Users/mseok/.codex/skills/research-talk'].filter(Boolean).find(r=>fs.existsSync(path.join(r,'scripts/ensure_font.py')));
    if(!root){console.warn('ensureFont(): scripts/ensure_font.py not found; make sure Pretendard is installed');return;}
    const r=spawnSync('python3',[path.join(root,'scripts/ensure_font.py')],{encoding:'utf8'});
    const msg=(r.stdout||'').trim();
    if(r.status!==0)console.warn('ensureFont(): '+(msg||r.stderr||'failed')+' (renders fall back to another font until Pretendard is installed)');
    else if(!/: installed$/.test(msg))console.log('ensureFont(): '+msg);
  }catch(e){console.warn('ensureFont(): '+e.message);}
}
export function createDeck({language}={}){
  ensureFont();
  // `language` is kept for old callers; the family no longer depends on it (Pretendard covers both).
  const p=Presentation.create({slideSize:{width:2560,height:1440}});
  // Theme colours = the deck palette, so any chart element left at its default (Artifact Tool draws scatter markers in accent1) is the accent blue or a gray, never Office teal.
  p.theme.colorScheme={name:'Research plain',themeColors:{accent1:C.accent,accent2:'#7A7A7A',accent3:'#B4B4B4',accent4:C.red,accent5:'#666666',accent6:'#DDDDDD',bg1:'#FFFFFF',bg2:'#F7F7F7',tx1:'#000000',tx2:'#666666',dk1:'#000000',dk2:'#333333',lt1:'#FFFFFF',lt2:'#F7F7F7',hlink:C.accent,folHlink:'#666666'}};
  const master=p.masters.add('Seokhyun research white');master.background.fill='#FFFFFF';
  for(let i=0;i<kinds.length;i++){
    const layout=p.layouts.add(`${String(i+1).padStart(2,'0')} ${labels[i]}`);layout.setParentLayoutId(master.id);
    const center=['cover','section','appendix'].includes(kinds[i]);
    const title=layout.placeholders.add({type:'title',index:0,geometry:'textbox',position:frame(center?150:95,center?450:85,center?1620:1730,center?185:113),text:''});
    title.text.style={typeface:FAMILY,fontSize:(center?78:80)*S,lineSpacing:1,bold:true,color:center?C.accent:C.ink,insets:{left:0,right:0,top:0,bottom:0},alignment:center?'center':'left',autoFit:'none'};
    if(!center){
      const sub=layout.placeholders.add({type:'subtitle',index:1,geometry:'textbox',position:frame(95,189,1730,74),text:''});
      sub.text.style={typeface:FAMILY,fontSize:40*S,lineSpacing:1,color:C.muted,insets:{left:0,right:0,top:0,bottom:0},autoFit:'none'};
    }
  }
  return p;
}
// Title size in points: 80 by default, shrinking to at most 66 so a one-line title fits the 1730 pt measure; throws when it still cannot.
export function titleSize(title){
  // Per-character width in em for bold Latin text (narrow/wide classes) and Hangul/CJK 1.0; throws when a one-line title cannot fit at >= 66 pt.
  const w=c=>c.charCodeAt(0)>0x2e80?1.0:' '.includes(c)?0.28:'iljtfr.,:;|!()\'-'.includes(c)?0.32:/[A-Z]/.test(c)?0.70:/[0-9]/.test(c)?0.58:/[mwMW]/.test(c)?0.85:0.57;
  const k=[...String(title)].reduce((a,c)=>a+w(c),0);const sz=Math.min(80,Math.floor(1730/k));
  if(sz<66)throw new Error(`Title too long for one line at ≥ 66 pt (${String(title).length} chars): shorten it`);return sz;}
export function slide(p,kind,{title='',subtitle='',section='',takeaway='',notes='',titlePt,credit:creditText}={}){
  const index=kinds.indexOf(kind);
  const name=`${String(index+1).padStart(2,'0')} ${labels[index]}`;
  const s=p.slides.add();s.setLayout(p.layouts.items.find(l=>l.name===name));s.background.fill='#FFFFFF';
  const centered=['cover','section','appendix'].includes(kind);
  const titleShape=s.placeholders.getItem('title');titleShape.text=title;
  titleShape.position=frame(centered?150:95,centered?450:85,centered?1620:1730,centered?185:113);
  const tsz=centered?78:(titlePt??titleSize(title));titleShape.text.style={typeface:FAMILY,fontSize:tsz*S,lineSpacing:1,bold:true,color:centered?C.accent:C.ink,insets:{left:0,right:0,top:0,bottom:0},alignment:centered?'center':'left',autoFit:'none'};
  if(!['cover','section','appendix'].includes(kind)){
    // The subtitle accepts rich markup; `[[ref|[1]]]` puts a small gray reference marker inside it. Sizes sit on the runs (a shape-level fontSize set afterwards would override them).
    const sub=s.placeholders.getItem('subtitle');
    sub.text=[{runs:runsFrom(subtitle,{color:C.muted,size:40}).map(r=>({...r,textStyle:{bold:false,...r.textStyle,fontSize:r.textStyle.fontSize??'40pt'}})),bulletCharacter:'',marginLeft:0,indent:0}];sub.position=frame(95,189,1730,74);
    sub.text.style={typeface:FAMILY,lineSpacing:1,insets:{left:0,right:0,top:0,bottom:0},autoFit:'none'};
    text(s,section,95,49,1000,44,30,{color:C.muted,lineSpacing:1});
    if(creditText)credit(s,creditText);
    if(takeaway)closing(s,takeaway);
  }
  text(s,String(p.slides.items.length),920,1044,80,28,20,{alignment:'center',color:C.muted,lineSpacing:1});
  s.speakerNotes.textFrame.setText(notes);
  return s;
}
// Dissertation table: header row bold gray, thin gray rule under every row, no vertical lines, no fills. Per-cell borders (table.borders.assign is not
// available in this runtime). widths: column widths in source points.
export function table(s,values,x,y,w,h,widths,{size=34,headerColor=C.muted,headerAnchor='middle'}={}){
  // Cells containing "[[tone|text]]" markup or newlines become paragraph arrays with per-run colors (cell.text is read-only after creation).
  const rich=(v,r)=>{const t=String(v);return (t.includes('[[')||t.includes('\n'))?t.split('\n').map((line,li)=>({runs:runsFrom(line,{color:r===0?headerColor:C.ink,size}).map(x=>r===0&&li===0&&!x.textStyle.bold?{...x,textStyle:{...x.textStyle,bold:true}}:x),bulletCharacter:'',spaceBefore:0,spaceAfter:0})):v;};  // header: first line bold, later lines regular
  const vals=values.map((row,r)=>row.map(v=>rich(v,r)));
  const t=s.tables.add({rows:values.length,columns:values[0].length,left:x*S,top:y*S,width:w*S,height:h*S,values:vals,columnWidths:widths?.map(n=>n*S)});
  for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.anchor=r===0?headerAnchor:'middle';
    const markup=Array.isArray(vals[r][c]);
    cell.text.style={typeface:FAMILY,...(markup?{}:{fontSize:size*S,color:r===0?headerColor:C.ink}),lineSpacing:LINE_SPACING,...(r===0&&!markup?{bold:true}:{}),autoFit:'none'};   // markup cells: sizes live on the runs
    cell.borders={top:{style:'none'},left:{style:'none'},right:{style:'none'},bottom:{style:'solid',width:1*S,fill:C.edge}};
  }
  return t;
}
// ---------------------------------------------------------------------------------------------
// Dissertation vocabulary helpers (2026-10-01). Same units as above: source points on 1920 x 1080.
// ---------------------------------------------------------------------------------------------
const TONES={ref:C.muted,dim:C.muted,b:null,red:C.red,navy:C.accent,gray:C.muted};
// Plain colour rule (user, 2026-10-01): text is black/gray; emphasis is red (one key phrase) or bold. No blue/sky/green/orange/brown/purple tones: they made r09 and r16 decks read as multicoloured (a lavender takeaway cost a design point).
const REMOVED_TONES=new Set(['blue','sky','green','orange','brown','purple']);
// Markup: [[red|key phrase]] -> bold in that tone; [[b|word]] -> bold in the base color; [[dim|sub-label]] -> regular gray; [[ref|[3]]] -> inline reference marker (regular gray at 0.75 × the text size, never below 24 pt). One run per piece; every run carries its own color
// (a base `color` in text.style would overwrite run colors in Artifact Tool).
export function runsFrom(markup,{color=C.ink,size}={}){
  // With `size` (pt) every run carries its own fontSize; `[[ref|[3]]]` markers are 0.75 x size (never below 24 pt).
  const out=[];const re=/\[\[(\w+)\|((?:[^\[\]]|\[[^\]]*\])+)\]\]/g;let i=0,m;
  const fs=n=>size?{fontSize:n+'pt'}:{};
  while((m=re.exec(markup))){
    if(m.index>i)out.push({run:markup.slice(i,m.index),textStyle:{color,...fs(size)}});
    if(!(m[1] in TONES))throw new Error(REMOVED_TONES.has(m[1])?`rich(): tone "${m[1]}" is not allowed (plain colour rule); use red for one key phrase, b for bold, navy for the accent`:`rich(): unknown tone "${m[1]}" (use ${Object.keys(TONES).join('|')})`);
    out.push({run:m[2],textStyle:{bold:m[1]!=='dim'&&m[1]!=='ref',color:TONES[m[1]]??color,...fs(m[1]==='ref'?Math.max(24,Math.round((size??0)*0.75)):size)}});
    i=re.lastIndex;}
  if(i<markup.length)out.push({run:markup.slice(i),textStyle:{color,...fs(size)}});
  return out.length?out:[{run:'',textStyle:{color,...fs(size)}}];
}
export function rich(slide,markup,x,y,w,h,size=40,options={}){
  const {name,color=C.ink,alignment='left',verticalAlignment='top',bold,italic,lineSpacing=LINE_SPACING}=options;
  const shape=slide.shapes.add({name,geometry:'textbox',position:frame(x,y,w,h),fill:'none',line:{fill:'none',width:0}});
  shape.text=String(markup).split('\n').map(line=>({runs:runsFrom(line,{color,size}),bulletCharacter:'',spaceBefore:0,spaceAfter:0}));
  // Sizes live on the runs (runsFrom adds fontSize to every run): a shape-level fontSize set after the text overrides run sizes, which made `[[ref|…]]` markers full size.
  shape.text.style={typeface:FAMILY,lineSpacing,autoFit:'none',wrap:'square',alignment,verticalAlignment,insets:{left:0,right:0,top:0,bottom:0},...(bold?{bold:true}:{}),...(italic?{italic:true}:{})};
  return shape;
}
// The one-line (max two-line) closing interpretation: black, ~40 pt, centered, accent/bold on one or two key phrases only.
// One line holds ~80 mixed Latin characters or ~47 Hangul at 40 pt across 1640 pt (Pretendard). A two-line closing (the maximum) moves up to y 852 / h 96 automatically so the 40 pt gap above the footer survives;
// break it by meaning with '\n' (two balanced phrases), not by width.
export function closing(slide,markup,{y,h,lines}={}){
  const n=lines??Math.min(2,estimateLines(markup,40,TAKEAWAY.w,false));
  return rich(slide,markup,TAKEAWAY.x,y??(n>=2?852:TAKEAWAY.y),TAKEAWAY.w,h??(n>=2?96:TAKEAWAY.h),40,{name:'closing-interpretation',alignment:'center',verticalAlignment:'middle'});}
// Process/step box in the dissertation's vocabulary: white, thin gray outline, gray text; active = thick black outline, black text.
export function stage(slide,value,x,y,w,h,{active=false,size=34,bold=false,color,geometry='rect',borderRadius}={}){
  // geometry: 'rect' for data/steps, 'ellipse' for enzymes/models, borderRadius 'rounded-full' for small molecules (capsule) — meaning-bearing shapes, not decoration.
  return box(slide,value,x,y,w,h,{geometry,borderRadius,fill:'#FFFFFF',line:active?C.ink:C.edge,lineWidth:active?3:1.5,color:color??(active?C.ink:C.muted),size,bold:bold||active});
}
// Small native arrow between steps: gray, slim; centered on (cx, cy).
export function thinArrow(slide,cx,cy,{w=40,h=24,color=C.arrow,geometry='rightArrow'}={}){return arrow(slide,cx-w/2,cy-h/2,w,h,{geometry,color});}
// Blocked flow: a red × on the stub of an arrow (native `plus` rotated 45°; `mathMultiply` is not drawn by Apple's renderer). Attach the label to it; name 'inhibition-x'.
export function inhibitX(slide,cx,cy,{d=54,color=C.red}={}){return slide.shapes.add({name:'inhibition-x',geometry:'plus',position:{...frame(cx-d/2,cy-d/2,d,d),rotation:45},fill:color,line:{fill:'none',width:0}});}
// Status pill under a stage card: 'done' black outline, 'active' accent outline, 'planned' gray outline. Text 24 pt+.
export function statusPill(slide,value,cx,y,{state='planned',w=170,h=52}={}){
  const col=state==='active'?C.accent:state==='done'?C.ink:C.muted,line=state==='planned'?C.edge:col;
  return box(slide,value,cx-w/2,y,w,h,{geometry:'roundRect',borderRadius:'rounded-full',line,lineWidth:state==='planned'?1.5:2.5,color:col,size:26,bold:state!=='planned',name:'status-pill:'+value});
}
// Flow connectors. Thin native connectors attached to the nodes (they follow when a node is moved), with a small triangle head. Prefer these to block arrows in flow charts;
// thinArrow() stays for the dissertation's pipeline rows. Routed (elbow/curved) connectors are NOT used: Artifact Tool draws them but Apple's renderer collapses them to a straight line.
export function link(slide,a,b,{fromSide='right',toSide='left',color=C.ink,width=3,dash=false,head='triangle',headSize='lg'}={}){
  return slide.shapes.connect(a,b,{kind:'straight',fromSide,toSide,line:{style:dash?'dashed':'solid',fill:color,width:width*S},...(head?{tail:{type:head,width:headSize,length:headSize}}:{})});
}
// Small gray label centred on a link (24 pt minimum). Put it above a horizontal link, or beside a vertical one.
export function linkLabel(slide,value,cx,cy,{w=170,size=24,color=C.muted,bold=false}={}){
  return text(slide,value,cx-w/2,cy-Math.ceil(size*0.6),w,Math.ceil(size*1.3),size,{name:'link-label:'+value.slice(0,24),alignment:'center',color,bold,lineSpacing:1});
}
// Return path from the bottom of node a, down by `drop`, left/right to under node b, up into b (head on the last segment). Three straight connectors through two invisible waypoints,
// so it renders the same everywhere. boxA/boxB = [x,y,w,h] in source points.
export function loopBack(slide,a,b,boxA,boxB,{drop=70,color=C.accent,width=3.5,headSize='lg'}={}){
  const yb=Math.max(boxA[1]+boxA[3],boxB[1]+boxB[3])+drop,xa=boxA[0]+boxA[2]/2,xb=boxB[0]+boxB[2]/2;
  const wp=(x)=>slide.shapes.add({name:'waypoint',geometry:'rect',position:frame(x-1,yb-1,2,2),fill:'none',line:{fill:'none',width:0}});
  const w1=wp(xa),w2=wp(xb);
  const ln=(f,t,fs,ts,head)=>slide.shapes.connect(f,t,{kind:'straight',fromSide:fs,toSide:ts,line:{style:'solid',fill:color,width:width*S},...(head?{tail:{type:'triangle',width:headSize,length:headSize}}:{})});
  return [ln(a,w1,'bottom','top',false),ln(w1,w2,xb<xa?'left':'right',xb<xa?'right':'left',false),ln(w2,b,'top','bottom',true)];
}
// Numbered conclusion/finding list (dissertation p.49): colored number + colored label, bold statement with red key phrase, gray support line.
// items: [{label, text, support}]; one accent for every numeral (tone 'navy' default, 'red' allowed). Two-line statements fit up to 3 items.
// Width estimate in pt. Pretendard advances measured from the bundled font files (em fractions, Regular/Bold): Hangul 0.864, digits 0.58/0.62, capitals 0.64/0.67,
// lowercase 0.51/0.54, space 0.25/0.23, punctuation 0.36/0.40, Greek 0.56/0.59. Other families keep the old rough values (Hangul 1.0, Latin 0.55/0.60).
const PRETENDARD_W=(c,b)=>{const k=c.codePointAt(0);
  if((k>=0xac00&&k<=0xd7a3)||(k>=0x3131&&k<=0x318e))return 0.864;
  if(k>0x2e80)return 1.0;
  if(c===' ')return b?0.23:0.25;
  if(k>=48&&k<=57)return b?0.62:0.58;
  if(k>=65&&k<=90)return b?0.67:0.64;
  if(k>=97&&k<=122)return b?0.54:0.51;
  if(k>=0x370&&k<=0x3ff)return b?0.59:0.56;
  return b?0.40:0.36;};
export const textWidth=(t,size,bold=false)=>[...t].reduce((a,c)=>a+(FAMILY==='Pretendard'?PRETENDARD_W(c,bold):(c.charCodeAt(0)>0x2e80?1.0:(bold?0.6:0.55)))*size,0);
export function estimateLines(markup,size,w,bold=false){const plain=String(markup).replace(/\[\[\w+\|/g,'').replace(/\]\](?!\])/g,'');return plain.split('\n').reduce((n,l)=>n+Math.max(1,Math.ceil(textWidth(l,size,bold)/w)),0);}
export function findings(slide,items,{x=BAND.x,y=BAND.y,w=BAND.w,maxGap=80,tone='navy'}={}){
  // Plain style: ONE accent for every numeral (title blue), gray bold labels, black bold statements with at most one [[red|key phrase]] each.
  // Per-item colors (it.tone) are available but the user finds three category colors on a conclusion slide pointless; leave them off.
  const tw=w-110,rows=items.map(it=>({it,lines:estimateLines(it.text,40,tw,true)}));
  const block=r=>46+r.lines*48+(r.it.support?48:0);
  const total=rows.reduce((a,r)=>a+block(r),0),gap=Math.min(maxGap,Math.max(52,(BAND.h-total)/Math.max(1,rows.length-1)));   // item gap always larger than label→statement (46) so labels group with their own statement
  let yy=y;
  rows.forEach(({it,lines},i)=>{
    const col=['navy','red'].includes(it.tone??tone)?TONES[it.tone??tone]:C.accent;
    text(slide,String(i+1),x,yy+10,70,80,64,{bold:true,color:col,name:'finding-number:'+(i+1)});
    text(slide,it.label,x+110,yy,tw,44,30,{bold:true,color:C.muted});
    rich(slide,it.text,x+110,yy+46,tw,lines*48+4,40,{bold:true,name:'prose:finding-'+(i+1)});
    if(it.support)text(slide,it.support,x+110,yy+46+lines*48+6,tw,40,30,{color:C.muted});
    yy+=block({it,lines})+gap;
  });
}
// callout()/blockquote boxes are intentionally absent: the user never wants quote-style boxes (cream panel + colored side bar, shaded text panels). State a message as plain text with [[red|…]] emphasis or in closing().
export function callout(){throw new Error('callout() was removed: no blockquote/callout/side-bar/shaded text panels in this user\'s decks. Use plain text with [[red|…]] emphasis, rich(), or closing().');}
// Gray italic caption under a figure.
export function caption(slide,value,x,y,w,{size=28,alignment='center'}={}){return text(slide,value,x,y,w,Math.ceil(size*1.5),size,{name:'caption:'+String(value).slice(0,30),color:C.muted,alignment});}
// Aspect-fit rectangle of an image inside a frame, so labels/leaders can be placed on the visible picture.
export function containRect(iw,ih,x,y,w,h){const k=Math.min(w/iw,h/ih);return {x:x+(w-iw*k)/2,y:y+(h-ih*k)/2,w:iw*k,h:ih*k,scale:k};}
// Reference footer in the lower right: right-aligned rows of REFERENCE_PT text ending at y 1020, above the page number (y 1044), at most 2 rows (x 420–1825 holds ~6 short references; abbreviate journal names).
// items: ['[1] Lowry et al., Genes Dev. 2005', ...] already sorted ascending by number.
export function references(slide,items,{xLeft=420,xRight=1825,bottom=1020,maxRows=2}={}){
  const em=REFERENCE_PT,cap=(xRight-xLeft);const wid=t=>textWidth(t,em,false);
  const rows=[];let cur='';
  for(const it of items){const cand=cur?cur+'     '+it:it;if(cur&&wid(cand)>cap){rows.push(cur);cur=it;}else cur=cand;}
  if(cur)rows.push(cur);
  if(rows.length>maxRows)throw new Error(`references(): ${rows.length} rows > ${maxRows}. Put markers at the point of use and cite fewer sources in the footer, or split the slide; do not shrink the footer.`);
  const h=rows.length*em*LINE_SPACING*1.08+6;
  return reference(slide,rows.join('\n'),xLeft,bottom-h,cap,h);
}
// Intentional label on a figure (residue, ligand, chain). The `figure-label:` name exempts it from the text-over-picture check.
// halo (default off): a white box behind the label hid a hinge strand and an atom label in earlier decks; use it only on a verified blank-ribbon area and check the crop at full size.
export function figureLabel(slide,value,x,y,{size=30,color='#9E40B3',w,halo=false}={}){const sh=text(slide,value,x,y,w??Math.ceil(textWidth(value,size,true))+10,Math.ceil(size*1.2),size,{name:'figure-label:'+value,bold:true,color});if(halo)sh.fill='#FFFFFF';return sh;}
// Short leader from a label to a point on the picture (source points); same color as the highlighted site. Written as a bounding box + flipV (never a rotated zero-height line, which Apple's renderer mirrors).
export function leader(slide,x1,y1,x2,y2,{color='#9E40B3',width=1.6}={}){
  // Plain bounding box + flip, the way PowerPoint writes a line (a default line runs top-left to bottom-right; up-right/down-left needs flipV).
  const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.abs(x2-x1),h=Math.abs(y2-y1);
  const sh=slide.shapes.add({name:'figure-leader',geometry:'line',position:{...frame(x,y,w,h),...((x2-x1)*(y2-y1)<0?{verticalFlip:true}:{})},line:{fill:color,width:width*S}});
  return sh;}
// Native bar chart in the dissertation's benchmark style (p.25): gray bars, the proposed/main bar in the accent blue, one-decimal value labels,
// no gridlines. Text sizes are source points (>= 24). highlight: indices to color. direction 'column' or 'bar' (horizontal bars list the first
// category at the bottom, so this helper reverses the data to read top-to-bottom). The renderer does not draw value-axis titles on horizontal
// bar charts: put the unit in a gray line above the panel (text()) as well as in axisTitle.
export function barChart(slide,{categories,values,name='value',x,y,w,h,highlight=[],direction='column',min=0,max,major,format='0.0',axisFormat='#,##0',axisTitle,size=24,gray='#B4B4B4',accent=C.accent,gap=45}){
  const ts={typeface:FAMILY,fontSize:size*S,fill:'#333333'},horiz=direction==='bar';
  const cats=horiz?[...categories].reverse():categories,vals=horiz?[...values].reverse():values;
  const idx=highlight.map(i=>horiz?categories.length-1-i:i);
  // One series holding only the real data (the embedded workbook stays honest and editable); the highlighted bar is a per-point fill (standard c:dPt).
  // Apple's QuickLook ignores per-point fills (the bar stays gray there); a second padded series would fix that but leaves fake zero cells in the workbook, which is worse.
  return slide.charts.add('bar',{position:frame(x,y,w,h),categories:cats,
    series:[{name,values:vals,valuesFormatCode:format,fill:gray,points:idx.map(i=>({idx:i,fill:accent}))}],hasLegend:false,
    barOptions:{direction,grouping:'clustered',gapWidth:gap},chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},
    xAxis:{textStyle:ts,line:{style:'solid',fill:'#9A9A9A',width:1.5}},
    yAxis:{min,...(max!==undefined?{max}:{}),...(major?{majorUnit:major}:{}),numberFormatCode:axisFormat,...(axisTitle?{title:{text:axisTitle,textStyle:{...ts,bold:false}}}:{}),textStyle:ts,majorGridlines:null,line:{style:'solid',fill:'#9A9A9A',width:1}},
    dataLabels:{showValue:true,position:'outEnd',textStyle:{typeface:FAMILY,fontSize:(size+2)*S,bold:true,fill:'#000000'}}});
}
// Native scatter chart with explicit marker fill (Keynote drops markers whose fill is only on the series). Plot only real data.
// Excel cannot keep more than 15 significant digits of a literal chart value (finalize.mjs fails, without naming the chart): round to 12.
const r12=v=>(typeof v==='number'&&Number.isFinite(v))?Number(v.toPrecision(12)):v;
export function scatterChart(slide,{xs,ys,name='data',x,y,w,h,xAxis,yAxis,size=24,color=C.accent}){
  const ts={typeface:FAMILY,fontSize:size*S,fill:'#333333'};
  const ax=(a)=>({min:a.min,max:a.max,majorUnit:a.major,title:{text:a.title,textStyle:ts},textStyle:ts,majorGridlines:{style:'solid',fill:'#EEEEEE',width:1},line:{style:'solid',fill:C.light,width:1}});
  return slide.charts.add('scatter',{position:frame(x,y,w,h),series:[{name,xValues:xs.map(r12),values:ys.map(r12),marker:{symbol:'circle',size:9,fill:color},line:{fill:'none',width:0}}],scatterOptions:{style:'marker'},hasLegend:false,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},xAxis:ax(xAxis),yAxis:ax(yAxis)});
}

// Credit/collaborator slot in the top-right corner (dissertation p.44 puts a photo + name there); never inline between body and closing line.
export function credit(slide,value,{size=28}={}){return text(slide,value,1100,49,725,44,size,{name:'credit',color:C.muted,alignment:'right',lineSpacing:1});}

// Process card in the dissertation's pipeline style (p.45): gray small-caps kicker, bold name, one detail line, all centered in one native text body.
// Fill the box with information instead of a one-word box in empty space; size it to its text (≤ ~2.5× the text area).
// state: 'done' (light-gray fill, black outline), 'active' (white, black outline), 'planned' (white, thin gray outline, muted text); `active:true` is the old spelling of 'active'.
// Pair with statusPill() under each card for a pipeline whose stages are at different stages of completion.
export function stageCard(slide,{kicker='',name,detail=''},x,y,w,h,{active=false,state,color,geometry='rect',borderRadius}={}){
  const st=state??(active?'active':'planned'),on=st!=='planned';
  const ink=on?C.ink:C.muted,pt=n=>n+'pt';
  const paras=[];
  if(kicker)paras.push({runs:[{run:kicker.toUpperCase(),textStyle:{color:C.muted,fontSize:pt(24)}}],bulletCharacter:'',spaceBefore:0,spaceAfter:0});
  paras.push({runs:[{run:name,textStyle:{color:color??ink,bold:true,fontSize:pt(38)}}],bulletCharacter:'',spaceBefore:kicker?400:0,spaceAfter:0});
  if(detail)detail.split('\n').forEach((ln,i)=>paras.push({runs:[{run:ln,textStyle:{color:C.muted,fontSize:pt(28)}}],bulletCharacter:'',spaceBefore:i?0:300,spaceAfter:0}));   // '\n' in detail = line break; keep each line under ~24 characters in a 380 pt card
  const shape=slide.shapes.add({name:'node-label:'+name,geometry,position:frame(x,y,w,h),fill:st==='done'?'#F5F5F5':'#FFFFFF',line:{fill:on?C.ink:C.edge,width:(on?3:1.5)*S},...(borderRadius?{borderRadius}:{})});
  shape.text=paras;
  shape.text.style={typeface:FAMILY,lineSpacing:1,alignment:'center',verticalAlignment:'middle',autoFit:'none',insets:{left:0,right:0,top:8*S,bottom:8*S}};
  return shape;
}
