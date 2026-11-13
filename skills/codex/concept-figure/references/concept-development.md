# Finding the concept

Use this when there is a result and a method but no picture yet. The drawing is the easy part; deciding what the reader should see is the work. Do it with the user, in thumbnails, before any polished figure.

## Procedure

1. **Write the claim in one line**: "[our thing] does [what] by [how], where [the usual way] does [what instead]". Take it from the abstract and the last paragraph of the introduction, or ask the user for three sentences: the problem, the insight, the consequence. If the line will not come out, the paper's message is not settled yet; say so instead of drawing.
2. **Name the one contrast** the figure must make visible: prior versus ours, before versus after, naive versus insight, many steps versus one, separate versus unified, frozen versus trained, slow versus fast.
3. **Take inventory**: actors (nouns that can be drawn: data objects, modules, agents), actions (verbs, which become arrows), quantities (anything with more or less, which becomes size, count, position or a colour scale), and the one concrete example that will run through the figure.
4. **Pick three candidate patterns** from the catalogue below that differ in kind, not three variations of one.
5. **Draw thumbnails**: one low-fidelity sketch per candidate, side by side, gray boxes with one accent colour, real labels, no polish (`assets/examples/thumbnails.html` is the starting point). Under each write the sentence a reader would say after five seconds.
6. **Show the user the thumbnails** and ask which sentence is the paper's. Their choice, in their words, goes into the figure folder's notes; then build the chosen one with the archetype it maps to.

A concept is settled when the first sentence of the caption can be written and is the claim from step 1.

## Pattern catalogue

| Pattern | Use it when the claim is | It reads as | Reference figures | Build with |
|---|---|---|---|---|
| Same skeleton, one difference | "ours changes one thing" | spot the difference | MoCo Fig. 2, I-JEPA Fig. 2, ConvNeXt Fig. 4 | comparison |
| One example's journey | "this is what happens to an input" | follow the object | MAE Fig. 1, CLIP Fig. 1, SAM Fig. 4, Genie Fig. 3 | pipeline |
| Overview and zoom | "a known frame with one new part" | whole, then the part | ViT Fig. 1, DiT Fig. 3 | architecture |
| Two routes, same endpoints | "we reach the same place more directly" | long way versus shortcut | Consistency Models Fig. 1 | concept |
| Grid of the design space | "ours fills the empty cell" or "ours unifies two axes" | rows and columns | Diffusion Forcing Fig. 2, KAN Fig. 0.1 | comparison with rows |
| One source, several projections | "different views of one underlying thing" | common origin | Platonic Representation Hypothesis Fig. 1 | concept |
| Loop | "the system improves by iterating" | cycle with named steps | 3D Gaussian Splatting Fig. 2, Voyager Fig. 2 | agent system |
| Failure, then fix | "the usual way breaks here; ours does not" | wrong beside right, same example | ReAct Fig. 1, Tree of Thoughts Fig. 1 | comparison or cards |
| Triptych of what is new | "the contribution has three parts" | three small scenes | SAM Fig. 1 | panels |
| Lanes | "two processes run side by side and meet" | parallel tracks | BYOL Fig. 2 | comparison with lanes |
| Cost made visible | "ours is cheaper, smaller, fewer" | size or count of objects | Prefix-tuning Fig. 1, ControlNet Fig. 3 | comparison |
| One object transformed | "a gradual change is the mechanism" | strip of states | DDPM Fig. 2, Consistency Models Fig. 1 | concept |

Reference figures are identified in [archetypes.md](archetypes.md).

Patterns combine as frame and inset: one pattern gives the page its skeleton, and a second may sit inside the one box the figure is about. `contrast.html` is "same skeleton, one difference" with the geometry of the difference drawn inside the differing step. A second inset is a second idea.

## Questions that unlock a concept

Ask only what the material does not answer, one at a time:

- 이 그림을 5초 본 사람이 한 문장으로 뭐라고 말하면 성공인가요?
- 기존 방식과 딱 하나 다른 점을 고르면 무엇인가요?
- 예시 하나로 보여 준다면 어떤 입력과 어떤 출력인가요?
- 독자가 가장 흔히 오해하는 부분은 어디인가요?
- 이 그림이 맡지 않아도 되는 내용은 무엇인가요? (방법 전체, 결과 수치 등)

## Tests on a thumbnail

- Five seconds: someone who has not read the claim says the sentence.
- Labels covered: the contrast is still visible from structure, size and colour alone.
- One accent: the single coloured thing is the contribution.
- Whiteboard: could the author redraw it from memory in a minute? If not, it holds more than one idea.

## Usual ways a concept goes wrong

- The method is drawn as a pipeline when the claim is a contrast with prior work.
- Everything in the method is shown, so nothing is the point.
- A metaphor that needs its own explanation.
- Ours and the baseline are drawn on different skeletons, so the difference cannot be seen.
- No example: boxes with names, and the reader cannot tell what goes in or comes out.
- The new step is a named box like every other box, so the figure could belong to any paper. Draw what that step does.
- Two ideas in one figure; split them into Fig. 1 and the method figure.

## Why these steps

- B. Tversky, "Visualizing thought", Topics in Cognitive Science 3 (2011) 499-535, doi:10.1111/j.1756-8765.2010.01113.x: the page itself carries meaning (centre versus periphery, left to right, up and down) and so do the marks; she summarises the conventions as dots for entities, lines for relations, arrows for asymmetric relations and boxes for collections. A concept is a choice of which relation gets the page's main axis.
- R. E. Mayer, "Using multimedia for e-learning", Journal of Computer Assisted Learning 33 (2017) 403-423: leaving out extraneous material (coherence, d = 0.70), highlighting the essential (signalling, d = 0.46) and putting words next to the pictures they describe (spatial contiguity, d = 0.79) each improve learning in his review. Thumbnails with one accent are these three rules applied before polish.
- M. Rolandi, K. Cheng, S. Pérez-Kriz, "A brief guide to designing effective figures for the scientific paper", Advanced Materials 23 (2011) 4343-4346: a designer's and a scientist's step-by-step figure guide.
- V. Deschaintre's SIGGRAPH guide (see design-rules.md): one idea per figure, and the teaser's job is to make the reader curious.
