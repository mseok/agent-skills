# Archetypes and their reference figures

Pick the archetype from the figure's job, then open the worked example (`assets/examples/<name>.html`, rendered in `assets/examples/renders/<name>.png`) and the reference figures named here. The references were read from the arXiv PDFs on 2026-11-13; a venue is given only where the PDF's first page states it. Borrow the structure and the encoding, never the artwork: draw with the kit.

| The figure must show | Archetype | Worked example |
|---|---|---|
| what the model is made of | architecture | `architecture.html` |
| how data moves through the method | pipeline | `pipeline.html` |
| how the proposal differs from prior approaches | paradigm comparison | `comparison.html` (panels side by side), `contrast.html` (two rows, the differing step drawn as what it does) |
| why the idea works, as one picture | concept | `concept.html` |
| a system of components around an LLM or agent | agent system | `agent-loop.html` |

When the concept itself is not settled, start with [concept-development.md](concept-development.md) and `thumbnails.html`. A paper's Fig. 1 is usually a concept or comparison figure; the architecture or pipeline figure opens the method section. Two jobs mean two figures or two panels with a rule between them, not one crowded drawing.

## Architecture

Recipe: main path in one direction (bottom-to-top for a layer stack, left-to-right for stages); one tint per module type; a container with "×N" around the repeated unit; the repeated block zoomed in a second panel, joined by zoom lines or separated by a dashed rule; tensor shapes or symbols on the arrows; a real input and output at the two ends.

- Transformer, arXiv 1706.03762 (NIPS 2017), Fig. 1: one pastel fill per module type, gray container with "N×", residual loops with rounded corners.
- ViT, 2010.11929 (ICLR 2021), Fig. 1: overview left, zoomed encoder block right of a dashed rule, real image patches as the input.
- Swin Transformer, 2103.14030, Fig. 3: outline boxes in black and white, dashed stage groups, tensor shapes above the arrows, colour only in the zoomed block.
- DETR, 2005.12872, Fig. 2: four dashed groups titled on top; colour only for the object queries, carried through to the boxes on the output photo.
- Latent Diffusion, 2112.10752, Fig. 3: tinted regions for the spaces (pixel, latent, conditioning), trapezoid encoder and decoder, a key row for the small symbols.
- Perceiver IO, 2107.14795 (ICLR 2022), Fig. 2: arrays as rows of cells, one colour per array; dashed groups whose stroke and label share a colour; an inset with the attention detail.
- Flamingo, 2204.14198 (NeurIPS 2022), Fig. 3: two colours, both semantic (blue with a snowflake = frozen, lilac = trained), key in a corner.
- SAM, 2304.02643, Fig. 4: the heavy image encoder drawn large and the light decoder small, tint fill with a darker edge of the same hue, a real photo in and out.
- DiT, 2212.09748, Fig. 3: borderless tints, zoom lines from the block to its detail, the two rejected variants drawn faded beside the adopted one.
- ControlNet, 2302.05543, Fig. 3: gray with a lock = frozen, blue = trainable copy, box width following resolution, a dotted boundary around the added network.
- Genie, 2402.15391, Fig. 3: each module's output tokens in the module's colour; stacked frames with a brace.
- Density counter-example: SD3, 2403.03206, Fig. 2, about 110 words and a caption that says "best viewed zoomed in". Split such a figure.

## Pipeline

Recipe: left to right, three to six stages; each stage's output drawn as a concrete object (tokens, a matrix, an image, a stack of samples) rather than a second box; one colour per stage or modality, continuing into what that stage produces; numbered or lettered stages when the figure spans training and use; inputs and outputs are examples.

- CLIP, 2103.00020, Fig. 1: three numbered stages; purple = text, green = image, blue = matched pairs; trapezoid encoders, stacked cards for a batch, a similarity matrix with the diagonal tinted.
- MAE, 2111.06377, Fig. 1: gray encoder and decoder, token squares in three colours, the image at both ends, four words in the whole figure.
- unCLIP, 2204.06125, Fig. 2: a dotted line separates training (above) from generation (below); embeddings as cell strips.
- NeRF, 2003.08934, Fig. 2: scene renders and small plots along the path, (a) to (d) under the stages, one arrow colour for computation and another for rays.
- 3D Gaussian Splatting, 2308.04079 (ACM Trans. Graph. 42), Fig. 2: gray boxes = operations, white = data; two arrow colours with a key (operation flow, gradient flow).
- SAM, 2304.02643, Fig. 1: Task / Model / Data as three panels with "(a) **Task**: …" under each.

## Paradigm comparison

Recipe: two to four panels on one skeleton, drawn at the same size and position so that only the difference catches the eye; colour only on what differs; the proposal last, optionally after a dashed rule, its name in bold; a two-entry key when colour means trained versus frozen or kept versus pruned. Rows can add a second axis (training, sampling). With one earlier method, stack two rows instead (`contrast.html`): the earlier method above as `.context`, the proposal below as `.strong`, columns and lanes shared, and the one step that differs drawn as a picture of what it does.

- MoCo, 1911.05722, Fig. 2: three mechanisms on one skeleton, only the differing component changes colour; borderless tints, gray arrows, about 45 words.
- I-JEPA, 2301.08243, Fig. 2: three architectures on one skeleton in slate, a red outline on the energy and the latent.
- BYOL, 2006.07733, Fig. 2: two tinted lanes (online, target) crossing stage columns, a dashed arrow for the loss, "//" for stop-gradient.
- Diffusion Forcing, 2407.01392 (NeurIPS 2024), Fig. 2: methods in columns with the proposal first, training and sampling in rows; node tint encodes noise level with a colour bar.
- Tree of Thoughts, 2305.10601 (NeurIPS 2023), Fig. 1: four schematics, the proposal last after a dashed rule and in bold; green = kept path, pink = pruned.
- Prefix-tuning, 2101.00190, Fig. 1: top and bottom contrast; red = tuned, gray = frozen; stacked copies show the storage cost.
- ConvNeXt, 2201.03545, Fig. 4: three block designs side by side in black and white with operations written on the edges.
- KAN, 2404.19756, Fig. 0.1: the comparison laid out as a table (rows: theorem, formula, model; columns: the two networks).

## Concept

Recipe: one picture of the idea on one concrete example, two colours at most, each colour one named thing that the caption can print in the same colour; computed stand-ins (a noise series, a density) instead of hand-drawn blobs; almost no boxes.

- Consistency Models, 2303.01469 (ICML 2023), Fig. 1: a strip of real images from data to noise; olive = the ODE, red = the learned map, drawn as arcs back to the origin; the caption prints both terms in those colours.
- Score SDE, 2011.13456 (ICLR 2021), Fig. 2: a computed density with sample paths, equations on the arrows, marginals at both ends.
- DDPM, 2006.11239 (NeurIPS 2020), Fig. 2: a graphical model (circles, arrows, a dashed reverse arrow) with image thumbnails under the nodes.
- SimCLR, 2002.05709 (ICML 2020), Fig. 2: symbols and arrows only, functions written on the arrows, symmetric.
- Platonic Representation Hypothesis, 2405.07987 (ICML 2024), Fig. 1: one metaphor drawing with math labels only.

## Agent system

Recipe: the model in the centre, components around it, one colour per component with arrow labels in the component's colour; a transcript or code card showing one concrete episode in the same colours; marks for right and wrong when outcomes are compared.

- ReAct, 2210.03629 (ICLR 2023), Fig. 1: transcript cards with tab titles in monospace, highlighted spans (red wrong, green right, blue thought), a cross or check per card.
- RAG, 2005.11401, Fig. 1: two rounded containers with coloured titles; task examples enter on the left and leave on the right in matching highlight colours; a dashed arrow on top for back-propagation.
- Voyager, 2305.16291, Fig. 2: three components under coloured header bars, arrow labels in the component colour, a code card in the centre.
- Decision Transformer, 2106.01345, Fig. 1: one colour per token type, with a concrete example under the tokens.
