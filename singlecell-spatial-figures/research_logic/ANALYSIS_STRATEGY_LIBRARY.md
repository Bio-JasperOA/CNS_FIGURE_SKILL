# Single-cell & Spatial Transcriptomics Analysis Strategy Library

This file is the **analysis reasoning layer** between a biological question and a concrete software command.

The goal is not to maximize the number of analyses. The goal is to choose the **smallest defensible set of analyses that can test the claim–evidence graph**.

Use together with `SKILL.md` and `PAPER_LOGIC_LIBRARY.md`.

---

## 1. Core rule: analysis is selected by question

Use this order:

```text
biological question
→ claim
→ evidence needed
→ statistical / computational analysis family
→ diagnostic checks
→ validation
→ figure
```

Do not use this order:

```text
available software
→ many analyses
→ interesting plots
→ retrospective story
```

For every analysis ask four questions:

1. What biological question does this answer?
2. What is the correct independent replicate?
3. What alternative explanation could produce the same result?
4. What additional evidence would strengthen the interpretation?

---

# Part I. scRNA-seq analysis backbone

## SC-01. Quality control and contamination control

**Question:** Are the observed transcriptional states credible biological cells/nuclei rather than technical artifacts?

Typical components:

- library size / detected feature QC;
- mitochondrial / ribosomal / stress metrics where biologically appropriate;
- doublet detection;
- ambient RNA / soup assessment when relevant;
- sample-level QC and outlier detection;
- optional cell-cycle or dissociation-stress diagnostics.

**Unit of inference:** cell for technical QC; sample/donor for deciding whether an entire specimen is problematic.

**Main outputs:** retained cells, excluded cells, QC metrics, sample-level diagnostic summary.

**Supports:** data-quality statements.

**Does not support:** biological differences between conditions.

**Important rule:** do not choose thresholds only because they make the UMAP look cleaner. Thresholds should be justified by assay properties, distributions, sample consistency and biological context.

---

## SC-02. Normalization, feature selection and representation

**Question:** What representation preserves meaningful biological variation while reducing sampling noise and nuisance variation?

Typical components:

- count normalization or model-based normalization;
- highly variable feature selection when appropriate;
- PCA / latent representation;
- optional variance partitioning and nuisance-factor diagnostics.

**Main outputs:** normalized assay, feature set, latent representation.

**Supports:** downstream representation.

**Does not support:** removal of batch effects by itself.

**Diagnostic:** ensure major biological programs are not removed as “technical”.

---

## SC-03. Multi-sample integration / batch handling

**Question:** Can cells from different batches, donors or datasets be compared without erasing real biological differences?

Use only when there is a real integration problem.

Evaluate both:

- removal of unwanted batch structure;
- preservation of cell-type, condition, stage and rare-state structure.

**Unit of concern:** donor / sample / experiment / platform, not individual cell.

**Main outputs:** integrated latent space or corrected representation.

**Supports:** joint visualization and cross-sample state comparison.

**Does not support:** differential expression on corrected values unless the method explicitly provides an appropriate inferential model.

**Failure mode:** over-integration that mixes biologically distinct states.

---

## SC-04. Clustering and state discovery

**Question:** Are there recurrent transcriptional states not explained by existing annotations?

Typical components:

- graph construction;
- multi-resolution clustering;
- stability / robustness checks;
- hierarchical relationships between broad types and fine states.

**Main outputs:** candidate clusters/states.

**Supports:** state discovery.

**Does not support:** a new biological cell type merely because a cluster exists.

**Validation:** marker programs, reference mapping, recurrence across donors, spatial support, perturbation or orthogonal markers.

---

## SC-05. Cell-type and cell-state annotation

**Question:** What biological identity best explains each cluster/cell state?

Prefer convergent evidence:

```text
canonical markers
+ marker programme
+ reference mapping
+ tissue/developmental context
+ orthogonal modality when available
```

Avoid one-marker annotation.

For novel states distinguish:

- established cell type;
- subtype;
- transient state;
- activation program;
- technical or stress state.

**Main outputs:** identity labels, confidence/evidence record, hierarchical annotation.

---

## SC-06. Composition and differential abundance

**Question:** Does the abundance of a cell type/state change across conditions, stages or phenotypes?

Use sample-level inference.

Preferred conceptual structure:

```text
cell counts/fractions
→ donor/sample-level abundance
→ model condition while accounting for design/covariates
→ effect size + uncertainty
```

**Biological replicate:** donor/sample/embryo, not cell.

**Supports:** differential abundance.

**Does not support:** direct mechanism of the abundance change.

**Common error:** testing thousands of cells as independent replicates.

---

## SC-07. Differential expression and state-specific response

**Question:** Within a defined cell type/state, which transcriptional responses differ between biological groups?

When the scientific contrast is across donors/conditions, prefer donor-aware or pseudobulk-style inference rather than treating cells as independent biological replicates.

Consider separately:

- cell-type-specific DE;
- state-specific DE;
- interaction effects such as condition × cell type;
- stage / time trends;
- perturbation effects.

**Main outputs:** effect size, uncertainty, adjusted evidence, ranked genes.

**Supports:** transcriptional association / response.

**Does not support:** pathway mechanism by itself.

---

## SC-08. Gene programmes, pathway activity and functional interpretation

**Question:** Can many gene-level differences be summarized as coherent biological programmes?

Possible families:

- gene-set enrichment;
- pathway activity scoring;
- module / topic modelling;
- transcription-factor activity;
- leading-edge analysis.

Use pathway analysis to compress evidence, not to decorate every gene list.

**Strong use:** a pathway explains multiple independent observations and links to perturbation or regulatory evidence.

**Weak use:** reporting broad GO terms after every DE table.

---

## SC-09. Regulatory network / regulon analysis

**Question:** Which regulators could explain the observed state transition or transcriptional programme?

Evidence can include:

- TF-target association;
- motif/chromatin support;
- regulon activity;
- perturbation response;
- temporal precedence;
- cross-dataset recurrence.

**Supports:** candidate regulatory mechanism.

**Does not support:** causality from co-expression alone.

---

## SC-10. Trajectory and pseudotime

**Question:** Are observed states consistent with an ordered biological transition?

Use only when biology implies progression, differentiation, response, recovery or continuous state change.

Required reasoning:

```text
starting state
→ candidate intermediate states
→ endpoint / branch
→ ordered gene programmes
→ external support for direction or lineage
```

**Supports:** inferred ordering / transition hypothesis.

**Does not support:** physical lineage solely from UMAP geometry.

Validation options:

- known chronological stage;
- lineage tracing;
- clonal information;
- RNA velocity;
- perturbation;
- spatial ordering;
- molecular recorder.

---

## SC-11. RNA velocity / fate probability

**Question:** Is there evidence about local transcriptional direction or future-state propensity that strengthens a transition model?

Treat RNA velocity as a model with assumptions, not as ground truth.

Check:

- model applicability;
- gene-wise fit;
- uncertainty;
- preprocessing sensitivity;
- agreement with known biology / stage labels.

**Supports:** directional evidence under model assumptions.

**Does not support:** definitive lineage or actual cell migration.

---

## SC-12. Cell–cell communication

**Question:** Which sender–receiver relationships could plausibly explain a receiver-cell programme?

Evidence ladder:

```text
ligand in sender
→ receptor in receiver
→ condition-specific interaction
→ downstream target programme
→ spatial co-localization when tissue context matters
→ perturbation / orthogonal validation
```

Ligand–receptor scores alone are hypothesis generation.

Prefer interaction hypotheses that are:

- recurrent across donors;
- condition/stage specific;
- supported by downstream response;
- spatially plausible where applicable.

---

## SC-13. Perturbation and response modelling

**Question:** Does modifying a regulator or environmental input change the predicted biological state?

Typical logic:

```text
candidate regulator
→ perturbation signature
→ response state
→ downstream programme
→ recovery / rescue / resistance
```

When prediction models are used, validate on held-out perturbations or perturbation families rather than random cells.

---

# Part II. Spatial transcriptomics analysis backbone

Spatial data are not simply scRNA-seq plus coordinates. Platform resolution, molecular diffusion, segmentation, capture geometry and histology can materially change interpretation.

---

## ST-01. Spatial QC and tissue integrity

**Question:** Are spatial measurements technically reliable and anatomically plausible?

Check:

- counts/features by location;
- tissue coverage;
- segmentation quality for cell-resolved assays;
- image registration where relevant;
- section-specific artifacts;
- edge effects;
- molecular diffusion / effective resolution concerns;
- cross-section consistency.

**Main output:** trusted locations/cells and tissue geometry.

---

## ST-02. Spatial normalization and representation

**Question:** What expression/latent representation preserves both molecular and spatial information relevant to the biological question?

Do not force spatial smoothing when sharp biological boundaries are expected.

Compare spatial and non-spatial representations when the claim depends on spatial information.

---

## ST-03. Cell-type mapping / deconvolution

**Question:** Which cell types or states occupy each spatial location?

Two cases:

### Cell-resolved spatial assay

Perform cell typing / reference mapping, ideally with confidence and marker support.

### Multi-cell spot / voxel

Estimate cell-type fractions or abundance rather than assigning a single identity by convenience.

**Reference dependency:** evaluate whether the scRNA reference contains the relevant states.

**Validation:** spatial markers, histology, known anatomical regions, independent references.

**Does not support:** precise cell-cell contact when the assay resolution is substantially multicellular.

---

## ST-04. Spatial domains / tissue architecture

**Question:** Are there reproducible regions defined by molecular state and spatial organization?

Use spatially aware domain detection when appropriate, but test robustness across:

- algorithm / parameter choice;
- sections;
- biological samples;
- known anatomy / histology;
- marker programmes.

**Supports:** tissue-domain structure.

**Does not support:** a biological compartment solely from one clustering output.

---

## ST-05. Spatially variable genes and spatial autocorrelation

**Question:** Which genes/programmes show non-random spatial organization?

Possible evidence:

- spatial autocorrelation;
- hotspot / coldspot structure;
- domain-associated expression;
- gradients;
- local spatial variance.

Control for obvious confounding such as library size, cell-type composition and domain boundaries when needed.

---

## ST-06. Neighborhood and niche analysis

**Question:** Which local cellular communities recur in tissue and associate with specific cell states or phenotypes?

Logic:

```text
local neighbourhood definition
→ cell-type / state composition
→ recurrent niche
→ niche-specific programmes
→ condition / stage enrichment
→ reproducibility across sections/specimens
```

Strong niche evidence is specimen-recurrent and biologically interpretable.

A niche is not validated merely because clustering produces a niche label.

---

## ST-07. Spatial gradients and axes

**Question:** Does a molecular/cellular programme change continuously along an anatomical or developmental axis?

Prefer measured or anatomically defined axes.

Examples:

- proximal–distal;
- dorsal–ventral;
- crypt–villus;
- tumor core–margin;
- embryo developmental axis.

**Supports:** spatial ordering / gradient.

**Does not support:** developmental time unless independently linked to time.

---

## ST-08. Spatial cell–cell communication

**Question:** Are candidate ligand–receptor interactions anatomically plausible and linked to local receiver programmes?

Stronger spatial communication evidence requires:

```text
sender ligand
+ receiver receptor
+ physical / neighborhood proximity
+ local target programme
+ condition or stage specificity
+ independent / perturbational support
```

This is stronger than applying a dissociated-scRNA communication method to spatially labelled cell types without proximity constraints.

---

## ST-09. Multi-section / multi-sample spatial integration

**Question:** Which spatial structures are reproducible rather than section-specific?

Key tasks:

- section alignment only when justified;
- shared domain/state identification;
- variability across specimens;
- conserved vs specimen-specific niches;
- registration of comparable anatomy;
- cross-platform validation where possible.

Do not treat adjacent serial sections as independent biological replicates.

---

## ST-10. Histology / morphology integration

**Question:** Do transcriptional states correspond to measurable tissue morphology?

Possible evidence:

- H&E / IF / imaging features;
- segmentation morphology;
- gland / vessel / tumor boundary;
- ECM architecture;
- cell shape / density.

Image features should add orthogonal evidence rather than serve as decorative backgrounds.

---

# Part III. Cross-modal analysis patterns

## CM-01. scRNA reference → spatial mapping

Use when scRNA has deeper molecular coverage and spatial data provide location.

Logic:

```text
validated scRNA identities
→ map/deconvolve spatial data
→ inspect mapping confidence
→ validate marker localization
→ identify spatially structured states
```

---

## CM-02. Spatial finding → scRNA molecular dissection

Use when a spatial niche/domain is discovered first.

Logic:

```text
spatial niche
→ identify enriched cell types/states
→ dissect transcriptomic programme in scRNA
→ nominate regulators / interactions
→ return to spatial data for localization validation
```

---

## CM-03. Multi-omic regulatory chain

For RNA + chromatin/protein/etc.:

```text
state-specific RNA programme
→ candidate regulator
→ chromatin / motif / protein support
→ target genes
→ perturbation or external validation
```

Do not call modalities “integrated” merely because they share a UMAP.

---

# Part IV. Common end-to-end study routes

## Route A — Disease cohort scRNA-seq

```text
QC
→ annotation
→ sample-level composition
→ cell-type-specific DE
→ pathway/regulatory programmes
→ disease-associated state
→ communication or trajectory only if biologically motivated
→ external cohort / orthogonal validation
```

Core question: **which cell types/states change, how do they change, and what mechanism plausibly explains the change?**

---

## Route B — Developmental scRNA-seq

```text
QC
→ hierarchical annotation
→ stage composition
→ transition / trajectory model
→ dynamic genes/programmes
→ regulator/fate analysis
→ spatial localization
→ lineage / stage / perturbation validation
```

Core question: **how does state change through developmental time, and what constrains fate?**

---

## Route C — Spatial tissue atlas

```text
spatial QC
→ cell-type mapping/deconvolution
→ tissue domains
→ SVG/programmes
→ niches/neighbourhoods
→ spatial gradients
→ communication hypotheses
→ multi-section/specimen validation
```

Core question: **how does tissue organization explain molecular/cellular function?**

---

## Route D — Disease scRNA + spatial

```text
scRNA defines high-resolution states
→ spatial mapping localizes them
→ disease-enriched niche
→ niche-specific state programme
→ local communication hypothesis
→ receiver target programme
→ external / histology / perturbation validation
```

This is often stronger than running scRNA and spatial analyses independently.

---

## Route E — Virtual embryo / developmental foundation model

```text
stage-resolved reference atlas
→ spatial / lineage ground truth where available
→ model learns developmental representation
→ held-out embryo/stage/species evaluation
→ predict state / fate / space / perturbation
→ compare with classical developmental models
→ biological utility test
→ orthogonal or experimental validation
```

Avoid random-cell train/test splits across the same embryo or specimen.

---

# Part V. Decision gates

Before adding an analysis, ask:

### Gate 1 — Does it support a claim?

If no, do not add it.

### Gate 2 — Is the required information actually measured?

Examples:

- no spatial coordinates → no spatial niche claim;
- no lineage evidence → no definitive lineage claim;
- no perturbation → no direct causal claim;
- no donor-level replication → weak population-level inference.

### Gate 3 — Is the independence unit correct?

For condition/disease inference, cells usually are observations nested inside biological specimens, not independent biological replicates.

### Gate 4 — Does the method add information beyond a simpler analysis?

If a complex model does not improve biological inference, robustness, generalization or interpretability, prefer the simpler analysis.

### Gate 5 — What would falsify the interpretation?

Every advanced analysis should have a failure rule.

---

# Part VI. Common analysis anti-patterns

Avoid:

- clustering at many resolutions until a preferred biology appears;
- annotation from one marker;
- cell-level p-values for donor-level questions;
- DE followed by generic pathway enrichment with no mechanistic follow-up;
- CellChat/CellPhoneDB-like output treated as demonstrated communication;
- pseudotime treated as lineage;
- velocity arrows treated as ground-truth fate;
- spatial clustering treated as anatomy without histology/marker support;
- deconvolution results used without checking reference coverage and uncertainty;
- defining niches on one section only and calling them tissue architecture;
- integrating modalities only for visual overlap;
- running every available method because it is available.

---

# Part VII. Reference principles used for this library

This strategy library is consistent with recurring guidance from recent methodological reviews and benchmarks, including:

- Trapnell, **Revealing gene function with statistical inference at single-cell resolution**, Nature Reviews Genetics, 2024;
- Gulati et al., **Profiling cell identity and tissue architecture with single-cell and spatial transcriptomics**, Nature Reviews Molecular Cell Biology, 2025;
- Armingol et al., **The diversification of methods for studying cell–cell interactions and communication**, Nature Reviews Genetics, 2024;
- Bunne et al., **Optimal transport for single-cell and spatial omics**, Nature Reviews Methods Primers, 2024;
- Carstens et al., **Spatial multiplexing and omics**, Nature Reviews Methods Primers, 2024;
- Yuan et al., **Benchmarking spatial clustering methods with spatially resolved transcriptomics data**, Nature Methods, 2024;
- You et al., **Systematic comparison of sequencing-based spatial transcriptomic methods**, Nature Methods, 2024;
- Gaspard-Boulinc et al., **Cell-type deconvolution methods for spatial transcriptomics**, Nature Reviews Genetics, 2025;
- the community-maintained **Single-cell Best Practices** resource.

These sources motivate principles and decision structure; they do not define a mandatory software stack.
