// Living example of the dissertation vocabulary in style-kit.mjs. Copy beside style-kit.mjs and the runtime node_modules link, run with the
// Codex runtime node, then render with eval-cycle/tools/render_pptx.mjs (or the Presentations export) and compare with the dissertation pages.
// Slides: (1) step pipeline, (2) numbered findings, (3) plain statement + figure + caption + references, (4) benchmark charts. Replace the text with real content;
// a figure is an image you rendered (PyMOL/RDKit) placed with containRect() so labels can be anchored on the visible picture.
import fs from 'node:fs/promises';
import {PresentationFile} from '@oai/artifact-tool';
import {createDeck,slide,stage,stageCard,thinArrow,findings,rich,caption,references,containRect,frame,BAND,C,text,barChart} from './style-kit.mjs';
const p=createDeck();
{const s=slide(p,'method',{title:'Closed-loop pipeline',subtitle:'Three stages compose the screening loop',section:'Method',takeaway:'Most boxes are [[red|our own method]]; the remaining stage uses an [[b|external tool]].'});
 const xs=[95,405,715,1025,1335],lab=['Library\n460,605 structures','NESSO-1\naffinity','Ranking\ntop 1 %','Structural evidence\nPDB complexes','Candidate\nhypothesis'];
 xs.forEach((x,i)=>{stageCard(s,{kicker:['data','model','ranking','evidence','output'][i],name:lab[i].split('\n')[0],detail:lab[i].split('\n')[1]},x,430,270,190,{active:i===1||i===2});if(i<4)thinArrow(s,x+270+20,525);});
 text(s,'Stage 1',95,350,1000,60,44,{bold:true});
 references(s,['[1] Shenoy et al., bioRxiv 2026','[2] Sorokina et al., J. Cheminform. 2021','[3] Rutz et al., eLife 2022']);}
{const s=slide(p,'conclusion',{title:'Conclusion',subtitle:'Three findings',section:'',takeaway:''});
 findings(s,[{label:'Affinity ranking',text:'All three reference inhibitors are recovered in the top 1 %',support:'Supported by: NESSO-1 retrospective evaluation'},
  {label:'Structural evidence',text:'Experimental complexes share [[red|Val135 backbone contacts]]',support:'Supported by: 5HLN · 1UV5 · 1Q3W'},
  {label:'Next experiment',text:'Candidates 1 and 2 remain a binding hypothesis',support:'Supported by: structure-based comparison'}]);}
{const s=slide(p,'figure',{title:'Human GSK3B complexes',subtitle:'ATP-site hinge contacts',section:'NESSO-1 · GSK3B',takeaway:'All three complexes contact the [[red|Val135 backbone]].'});
 rich(s,'Experimental poses share [[red|hinge backbone contacts]] at Val135.',BAND.x,BAND.y,BAND.w,60,40);
 // const img=new Uint8Array(await fs.readFile('pocket.png')); const r=containRect(1200,1000,95,420,900,400);
 // s.images.add({blob:img,contentType:'image/png',fit:'contain',alt:'1UV5 pocket',position:frame(r.x,r.y,r.w,r.h)});
 caption(s,'1UV5 · ATP pocket',95,830,900);
 rich(s,'[[b|Val135]] N–H···O\nDistance 2.9 Å',1100,500,700,200,44);
 references(s,['[4] Meijer et al., Chem. Biol. 2003','[5] Wagner et al., ACS Chem. Biol. 2016']);}
{const s=slide(p,'benchmark',{title:'Benchmark',subtitle:'Three metrics, one benchmark [[gray|[2]]]'.replace(/\[\[gray\|(.*)\]\]/,'$1'),section:'Results',takeaway:'The proposed method is the [[red|best]] on every metric.'});
 const names=['Baseline A','Baseline B','Baseline C','Proposed'];
 [['Success (%, higher better)',[10.9,17.5,17.2,17.9],25],['Error (Å, lower better)',[19.0,14.4,15.3,12.2],22],['Distance (Å, lower better)',[17.9,12.9,13.9,10.8],22]].forEach(([t,v,mx],i)=>{const x=95+i*585;text(s,t,x,290,560,44,30,{bold:true,alignment:'center'});barChart(s,{categories:names,values:v,x,y:340,w:560,h:470,highlight:[3],max:mx,major:5});});
 references(s,['[2] Author et al., Journal 2024']);}
await (await PresentationFile.exportPptx(p)).save('kit-demo.pptx');
