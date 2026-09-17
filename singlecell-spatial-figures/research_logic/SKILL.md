---
name: research-logic
scope: single-cell, spatial, developmental, embryo, cross-modal and biological foundation-model studies
---

# Research Logic Skill

## 1. Research-first rule

When the user asks to design, critique, extend or prioritize a study, **do not begin with a list of methods, software or plots**. Begin with:

1. the unresolved biological gap;
2. one answerable biological question;
3. the central claim the study would need to support;
4. 3–5 subordinate claims;
5. the evidence required for each claim;
6. only then the analysis, model, experiment and figure plan.

A long analysis list is not a research strategy. Every analysis must answer a question or discriminate between competing explanations.

## 2. Claim–evidence graph

Every project must be expressible as:

```text
Question
  └─ Central claim
      ├─ Claim C1 → evidence E1/E2 → validation V1
      ├─ Claim C2 → evidence E3/E4 → validation V2
      ├─ Claim C3 → evidence E5/E6 → validation V3
      └─ Boundary claim → failure / negative result / scope limit
```

For each claim record:

- exact statement;
- evidence level;
- data source;
- analysis or experiment;
- expected observation;
- alternative explanation;
- validation strategy;
- failure rule: what result would make the claim unsupported.

Do not write a conclusion first and then search for supporting analyses.

## 3. Evidence ladder

Use the weakest wording supported by the strongest available evidence.

### Level 1 — Descriptive

Answers: **what exists?**

Examples: cell type, state, spatial domain, gene program, latent factor, developmental stage.

Allowed claims: presence, abundance, localization, association, recurrence.

Not enough for mechanism or causality.

### Level 2 — Comparative

Answers: **what differs?**

Requires appropriate biological replicate unit and a meaningful contrast.

Examples: condition-specific abundance, stage-specific program, spatial niche enrichment, model-vs-baseline difference.

### Level 3 — Predictive

Answers: **can information in X predict Y?**

Requires held-out evaluation at the correct independence unit and leakage control.

Prediction alone does not establish mechanism.

### Level 4 — Mechanistic

Answers: **what biological process plausibly explains the observation?**

Requires convergent evidence such as regulatory networks, perturbation response, receptor–ligand–target consistency, chromatin support, temporal ordering or orthogonal modality support.

### Level 5 — Causal / perturbational

Answers: **does changing X change Y in the predicted direction?**

Requires perturbation, intervention, genetic manipulation or a design with a defensible causal interpretation.

### Level 6 — Generalization

Answers: **does the claim survive outside the discovery setting?**

Examples: external cohort, unseen donor, unseen tissue, unseen species, unseen platform, unseen developmental stage.

### Level 7 — Translational / actionable

Answers: **does the mechanism or prediction enable a meaningful intervention, stratification or decision?**

Requires stronger validation than benchmark performance alone.

## 4. Top-paper logic patterns

Choose the study pattern before choosing tools.

### Pattern A — Atlas → biological discovery

Use when the main novelty is a new biological state space across cells, tissues, stages or disease contexts.

Logic:

```text
Missing biological map
→ build sufficiently broad atlas
→ establish robust identities/states
→ map time / space / condition
→ discover recurrent program or transition
→ nominate regulator / interaction / mechanism
→ validate with orthogonal data, species comparison or experiment
```

Fatal weakness: ending at UMAP + marker genes + pathway enrichment.

### Pattern B — Development / embryo: time × space × lineage

Logic:

```text
Developmental question
→ stage-resolved cell-state atlas
→ lineage / transition structure
→ spatial localization
→ regulatory program
→ cross-stage / cross-species / experimental validation
```

Rules:

- UMAP geometry is not developmental time.
- pseudotime is not lineage without lineage-supporting evidence.
- spatial gradients require measured spatial coordinates.
- a developmental mechanism should connect temporal order, spatial position and regulatory change.

### Pattern C — Spatial tissue ecology

Logic:

```text
Dissociated data lose context
→ define tissue architecture
→ identify niches / domains / gradients
→ test which cell states depend on local context
→ connect local interactions to target programs
→ validate across section, sample, modality or perturbation
```

A spatial claim requires spatial evidence. CellChat-like interaction inference without spatial co-localization is not spatial mechanism.

### Pattern D — Foundation model → biological utility

Logic:

```text
Specific information bottleneck
→ pretraining corpus designed to contain the missing information
→ representation learning
→ task-specific evaluation
→ baseline + ablation + OOD tests
→ show representation contains biologically meaningful information
→ demonstrate a scientific use case not obtainable from benchmark tables alone
→ experimental or orthogonal validation when making mechanistic claims
```

The scientific question must precede the architecture. “We trained a larger transformer” is not a biological gap.

### Pattern E — Perturbation / causal cell biology

Logic:

```text
Observed association
→ candidate regulator / program
→ perturbation prediction
→ direct perturbation
→ molecular / phenotypic response
→ network consequence
→ rescue / reversal / external confirmation
```

Preferred loop:

```text
experiment → model → hypothesis → experiment
```

not:

```text
model → more model → more model
```

### Pattern F — Multimodal bridge

Logic:

```text
one modality observes A, another observes B
→ define shared biological unit
→ align modalities
→ quantify what each adds beyond the other
→ transfer or predict missing context
→ validate on paired or orthogonal measurements
```

Concordance is not causality. A multimodal model must demonstrate that the added modality contributes information, not merely additional parameters.

## 5. How to design the study

### Step 1 — Write the gap

Use this form:

> Existing work can describe **X**, but cannot resolve **Y**, because **Z information or design element is missing**.

Good gap: loss of spatial context prevents testing whether a transcriptional state is niche-dependent.

Weak gap: no one has applied algorithm X to dataset Y.

### Step 2 — Write one biological question

Good:

> Which early embryonic cell states acquire lineage restriction only after entering a specific spatial niche?

Weak:

> Can we use scRNA-seq, spatial transcriptomics, CellChat, trajectory analysis and AI to study development?

### Step 3 — Write the central claim

The central claim should be one sentence that would still be scientifically interesting if the named software were removed.

### Step 4 — Decompose into 3–5 claims

A common structure:

- C1: the phenomenon exists;
- C2: it is structured by time / space / condition;
- C3: a specific program or regulator explains it;
- C4: the mechanism or model generalizes;
- C5: perturbation or orthogonal evidence supports the interpretation.

### Step 5 — Assign evidence

Each analysis must support at least one claim. If an analysis supports no claim, remove it.

### Step 6 — Design validation before discovery analysis

Specify validation before running the analysis:

- independent donor / cohort;
- held-out stage;
- held-out tissue;
- held-out species;
- alternate spatial platform;
- paired modality;
- perturbation;
- experimental assay;
- negative control.

## 6. Rules for biological foundation-model studies

### 6.1 Biological gap first

State what biological information is currently inaccessible, sparse or fragmented.

Examples:

- spatial context is lost in dissociated scRNA-seq;
- perturbation space is too large to measure exhaustively;
- rare developmental states have insufficient labelled data;
- paired image–omics data are sparse;
- transcriptional regulation must generalize across cell types.

### 6.2 Corpus must match the intended claim

If the model claims spatial knowledge, pretraining must contain spatial information or the paper must explicitly test whether spatial knowledge can emerge without it.

If the model claims developmental generalization, training/test splits must not leak stage identity, donor or near-duplicate datasets.

### 6.3 Baseline hierarchy

Benchmark against:

1. trivial/statistical baseline;
2. strong task-specific method;
3. classical latent model;
4. contemporary foundation models;
5. same architecture without the proposed biological information;
6. smaller-data or smaller-model ablations when scale is part of the claim.

### 6.4 Independence unit

Split at the unit relevant to the scientific claim:

- donor, not cell, for patient generalization;
- tissue, not cell, for cross-tissue generalization;
- embryo or stage, not cell, for developmental generalization;
- experiment or perturbation family for perturbation generalization;
- section / specimen for spatial generalization.

Random cell split is usually too weak when cells from the same specimen occur in both train and test.

### 6.5 OOD axes

At least one relevant out-of-distribution axis should be explicit:

- unseen donor;
- unseen tissue;
- unseen disease;
- unseen developmental stage;
- unseen perturbation;
- unseen species;
- unseen platform.

### 6.6 Biological utility

A top-tier model paper should do more than win metrics. It should show at least one of:

- new regulatory relationship;
- candidate therapeutic target;
- spatial context recovery;
- mechanistic hypothesis;
- perturbation prediction verified experimentally;
- a previously inaccessible biological mapping task.

## 7. Rules for single-cell and spatial studies

### Identity

Cell annotation should be supported by multiple marker programs, reference mapping and/or orthogonal evidence. Avoid claiming new cell types from clustering resolution alone.

### Composition

Use sample-level inference. Cell count is not the biological replicate.

### Differential expression

Prefer donor/sample-aware models when the scientific claim concerns individuals or conditions.

### Trajectory

Trajectory analysis should answer a biological transition question. A trajectory plot with no transition claim is decorative.

### Communication

Ligand–receptor score alone is hypothesis generation. Stronger evidence connects sender ligand, receiver receptor, spatial proximity, downstream target program and perturbation/validation.

### Spatial niches

A niche should have reproducible composition or program structure and should be validated across sections/samples. Do not define a niche only because a clustering algorithm produced a label.

## 8. Figure-story logic

Figures follow claims, not methods.

Typical high-impact order:

```text
Fig. 1  Problem + resource / cohort + principal biological structure
Fig. 2  Core discovery
Fig. 3  Time / space / regulatory explanation
Fig. 4  Mechanism or perturbation
Fig. 5  Generalization / orthogonal validation
Fig. 6  Integrated model or biological implication
```

This is a pattern, not a mandatory six-figure template.

A figure should answer one main question. Panels are evidence components of that question.

## 9. Anti-patterns

Reject or redesign projects dominated by:

- analysis stacking: QC → UMAP → DE → enrichment → CellChat → trajectory with no unifying claim;
- benchmark stacking with no biological use case;
- UMAP-as-evidence for mechanism;
- pseudoreplication at cell level;
- training/test leakage through donor, stage, tissue or dataset;
- circular validation using the same marker set or label source used to construct the result;
- spatial claims from dissociated data alone;
- causal language from observational association;
- “novel method applied to public dataset” as the only novelty;
- adding a foundation model after the biological story is already complete without showing added information.

## 10. Required output when planning a project

Return these sections in order:

1. **Biological gap** — one paragraph.
2. **Core question** — one sentence.
3. **Central claim** — one sentence.
4. **Claim–evidence graph** — 3–5 claims.
5. **Data design** — samples, modalities, biological replicate, time/space/perturbation axes.
6. **Analysis chain** — each step with purpose and output.
7. **Validation ladder** — internal, external, orthogonal, perturbational/experimental.
8. **Failure modes** — what could falsify or weaken each claim.
9. **Figure story** — figures mapped to claims.
10. **Minimal publishable version vs. ambitious version** — separate the core paper from optional complexity.

If the user provides an existing plan, critique it against this structure rather than adding more methods automatically.

## 11. Literature-derived anchor principles

The current rules were distilled from recurring logic in recent high-impact work, including:

- Geneformer / transfer learning for network biology — Nature 2023;
- scGPT — Nature Methods 2024;
- scFoundation — Nature Methods 2024;
- Nicheformer — Nature Methods 2025;
- OmiCLIP — Nature Methods 2025;
- Human Cell Atlas → unified foundation model perspective — Nature 2024;
- Perturbation Cell and Tissue Atlas perspective — Cell 2024;
- human embryonic limb spatiotemporal atlas — Nature 2023;
- multi-omic human embryonic skeletal atlas — Nature 2024;
- intact human gastrulation spatial transcriptomics — Nature Cell Biology 2024;
- Spateo 3D spatiotemporal embryo modelling — Cell 2024;
- reviews on statistical inference at single-cell resolution and integrated single-cell/spatial tissue architecture — Nature Reviews Genetics / Nature Reviews Molecular Cell Biology 2024–2025.

See `PAPER_LOGIC_LIBRARY.md` for the paper-by-paper abstraction. The Skill uses these studies as examples of reasoning patterns, not as templates to imitate mechanically.