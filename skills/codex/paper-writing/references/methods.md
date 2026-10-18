# Methods

A specialist can understand the method, reproduce every reported number and judge every comparison as fair, without wading through details that serve none of these. The reader should be able to see where the care went.

## Triage every detail

Ask in order and stop at the first yes.

1. **Is it introduced by this paper?** → *novel.* Specify it completely across the paper's materials. The main Methods holds the definitions, the new objective or procedure and, where the inputs give one, a one-sentence motivation for each choice that is not obvious (never a motivation the inputs do not state; reasoning that follows from the formulation is explanation, below); long derivations, proofs and pseudocode go where they clarify most, in the appendix if long.
2. **Does a reader need it to understand the contribution, reproduce a reported number or judge whether a comparison is fair?** → *critical.* Main Methods (for ml-conference, the main-text method or experimental setup), with exact values. Typical critical items:
   - data source, how splits were made (random, temporal, by entity) and filtering that removes data;
   - the evaluation protocol and the exact definition and direction of each metric;
   - the selection rule for checkpoints and hyperparameters, and which data informed it;
   - how baselines were obtained (published numbers or reproduced), configured and tuned, and with what budget;
   - hyperparameters the results are sensitive to;
   - numerical precision, solver tolerances or convergence criteria when they affect the result;
   - repeats and uncertainty (below);
   - the compute budget when methods are compared at matched compute.
3. **Is it a standard, nameable choice?** → *routine.* A clause with a citation in the main text ("trained with AdamW [CITE]"); full values in the setup table or the appendix hyperparameter table.
4. **Otherwise** → *environment.* Software versions, hardware and numerical settings that do not affect the result go to a Supplementary table or an archived environment file with a clear reference; incidental logging, file formats and directory layout are omitted.

A routine detail moves up to critical when the inputs show that the results are sensitive to it; state what the inputs show, with their values ("validation error rises from 7.9% to 9.4% when the dropout rate doubles").

## Definitions first, then build up

- Open the method with definitions: the quantities, their domains or dimensions, and the notation ("Let $x_t \in \mathbb{R}^d$ denote …"), before any equation that uses them. Define what the reader needs to read the next equation, not a glossary of every later symbol.
- Build the model in the order a reader can follow: the simplest form first, then each addition in its own short subsection, ordered by dependency (for example "Rigid-body model" → "Joint friction" → "Contact" → "Parameter estimation"), then how the result is used. Each subsection opens by saying what it adds to the previous one.
- For ml-conference, benchmark and computational papers, set up the problem before the components: inputs, outputs, available supervision, the relevant distributions, the objective, the controls and the assumptions. Then show how each component implements the key idea, and distinguish training from inference. For a theoretical contribution, state the result and its assumptions in the main text and give the proof in a referenced appendix. Include only the formulation this paper needs.
- Methods are often read on their own: spell out each acronym again at its first use in Methods.

## Explain each step

A Methods section that lists equations and settings can be reproduced but not followed. For each novel or critical step, say in a sentence what it does or implies whenever this follows from the equations or from facts in the inputs, before, within or after the related equations, wherever the reader needs it; there is no quota per equation: what a term computes or penalizes, what a parameter controls, what a constraint enforces, which alternative explanation a matched setting removes, what would change without the step. Write that sentence in this paper's quantities; a sentence that would fit any method ("this ensures stability", "this improves efficiency") is padding and goes. Name the object each property belongs to, and keep the quantity defined by the formulation apart from its implemented approximation. Write it as what the step does, never as why the authors chose it: such reasoning is derivation, not invented motivation, and it is often what lets a reader outside the subfield trust the method. A routine step keeps its clause and citation and gets an explanation only when a novel step depends on it. A design motivation, the cause of an empirical effect, a claim about alternatives that were tried, the range over which an approximation holds (unless the inputs or their formulas give it) and any benefit the experiments did not test still need the inputs.

When results are read against a control, floor or reference (a trivial baseline, an oracle, a reference measurement), define it in the problem setup, before data and models, with its value and what it rules out.

## Repeats, uncertainty and fair comparison

- State the number of independent runs, what varies between them (seed, data split, sample), how results are aggregated and exactly what each error bar or interval represents. Report single runs as single runs.
- Where a statistical test is used, name it and say whether observations are paired. Never add runs, intervals or tests the inputs do not report.
- Wherever methods are compared, state what was matched (data, compute, tuning budget, inference access) and disclose any material mismatch beside the comparison it affects. Matching one factor rules out a difference in that factor; it does not isolate a mechanism.

## Experimental setup tables

When several models, baselines or settings are compared, a table is easier to check than prose. Give the configuration values that differ between them (for example model size, depth and training budget) as columns, and the settings they share in the caption, which also says what was matched. A table earns its place when its rows carry values a reader would otherwise have to collect from prose, such as sizes, depths, budgets or resolutions. A column with the same value in every row belongs in the caption; a column that only sorts the rows into two or three groups is better written as one sentence per group; a table made only of such columns is not a table. The prose around a table does not repeat what the table lists. Use only values the inputs give, with the basis of every quantity in its header or caption; a missing cell is marked as such, never filled by inference. For ml-conference, place the table in the main-text experimental setup; for nature-family, in Methods or as an Extended Data table. The full hyperparameter list goes to the appendix or Supplementary. Prose around the table states what the reader needs to judge fairness and replaces, rather than repeats, the configuration prose.

## Writing the main Methods

- Organize by component or by pipeline stage under short descriptive subheadings ("Decoder architecture", "Training data", "Evaluation"), never chronologically by what was tried. Do not split a section into subsections of two or three sentences: parallel short items such as metrics or benchmarks read better as one paragraph each under a single heading, opened by a short bold label in ml-conference papers.
- Describe the final procedure. Attempts, failed variants and debugging do not appear; a rejected alternative appears only as an ablation result or as a one-clause motivation the inputs give ("we use X rather than Y because Y diverges when …").
- **Equations.** Say in prose what the equation computes, display it, and define in a following "where" clause only the symbols it introduces; quantities that recur across equations belong to the opening definitions. Display an equation when later text refers to it or when it carries the method; a one-line definition reads better inline. Number the equations that are referenced later.
- **Missing definitions and values.** Define an undefined symbol only when the supplied formulation admits a single consistent reading (the wave number $k$ in $e^{ikx}$), and list each such definition in Notes to author. Familiar notation alone does not establish what an experimental quantity, estimator or implementation choice is. When the inputs fix a setting by a rule rather than a number, state the rule, which is reproducible, and list the missing number in Notes to author. List every missing value or definition in Notes to author. An inline `[AUTHOR: what is needed]` appears only where a required sentence cannot be written without it, which is rare; a sentence that stands without the missing detail carries no marker. Never guess.
- **Settings of the reported run.** Describe a method's settings (ranges, stages, schedules) only from the retained config of the reported run; an analysis's aggregation window is not the method's scope.
- Tense: present for the definition and properties of the method ("The encoder maps …"), past for what was done in the experiments ("We trained each model for 200 epochs").
- Precision follows importance: novel and critical items get exact values and, where the inputs give it, a motivation; routine items get a name and a citation.
- **Pointers.** Point to the rest ("Supplementary Table S1 lists all hyperparameters") when the item can be built from values in the inputs, and list each new pointer in Notes to author so the author can create it. Never point to a figure, table or ablation whose data the inputs lack. Add code and data availability statements as the venue requires.

## What goes where

| Tier | Main text | Supplementary, Extended Data or appendix |
|---|---|---|
| novel | definitions, objective or procedure, motivation from the inputs | extended derivations, proofs, long pseudocode |
| critical | exact values and protocol; setup table when models are compared | sensitivity analyses |
| routine | name and citation | table of full values |
| environment | nothing | versions, hardware, environment file |

## Example (synthetic; the system and numbers are invented)

Notes, mixed together:

> AdamW lr 3e-4, beta는 기본값 / 학습 데이터 960시간 낭독 음성, 잡음 섞어서 SNR 0–20 dB 증강 / train·dev·test는 화자 겹치지 않게 나눔 / loss = CTC + λ·consistency, λ=0.3 (λ 0.1/0.3/1.0에서 평균 WER 9.6/8.4/10.2) / PyTorch 2.3, GPU 4장 / wandb로 로깅 / seed 3개 평균 / consistency는 원음과 잡음 버전의 frame posterior KL

Main Methods:

> We trained on 960 h of read speech and augmented each utterance with additive noise at signal-to-noise ratios between 0 and 20 dB. Development and test sets are speaker-disjoint from the training set and from each other. The training objective adds a consistency term to the connectionist temporal classification (CTC) loss,
>
> $$\mathcal{L} = \mathcal{L}_{\mathrm{CTC}} + \lambda\, \mathcal{L}_{\mathrm{cons}}, \tag{1}$$
>
> where $\mathcal{L}_{\mathrm{cons}}$ is the Kullback–Leibler divergence between the frame-level posteriors of the clean and noise-augmented versions of an utterance, and $\lambda = 0.3$. The consistency term vanishes when the two versions receive the same posteriors, so it penalizes only predictions that change with the added noise, and it needs no transcript. Recognition accuracy depends on $\lambda$: the average word error rate is 9.6%, 8.4% and 10.2% at $\lambda = 0.1$, 0.3 and 1.0 (Supplementary Fig. S2). Models were optimized with AdamW [CITE]; all reported error rates are means over three training runs with different random seeds. Supplementary Table S1 lists all hyperparameters and the software and hardware used.

The sentence after the "where" clause is derived from the definition of the term, not taken from the notes; it explains what the term does without claiming why it was chosen. Where the rest went: the learning rate and betas, PyTorch version and GPU count to Supplementary Table S1; the logging tool nowhere. Notes to author lists Supplementary Fig. S2 (built from the λ values in the notes) and Table S1 as new pointers. With several models compared, a setup table in the main text would hold their sizes and training budgets.
