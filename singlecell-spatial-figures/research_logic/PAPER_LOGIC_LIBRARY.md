# Paper Logic Library

This file abstracts **research logic**, not paper prose. Each entry asks: what was the gap, how was the evidence chain built, and what reusable design principle follows?

## 1. Geneformer — Nature 2023

**Paper:** Theodoris et al. *Transfer learning enables predictions in network biology.* Nature 618, 616–624 (2023). DOI: 10.1038/s41586-023-06139-9

**Gap**

Network biology often has limited task-specific data, especially in rare disease or inaccessible tissues.

**Logic chain**

```text
large general single-cell corpus
→ self-supervised pretraining
→ limited-data downstream tasks
→ show context-aware network information is encoded
→ in silico gene deletion / treatment
→ disease-state reversal hypothesis
→ experimental validation in cardiac models
```

**Why the story is strong**

The model is not the endpoint. The endpoint is a biologically testable hypothesis and therapeutic-target prediction.

**Reusable rule**

If a model claims mechanistic utility, finish with a biological consequence that can be independently tested.

---

## 2. scGPT — Nature Methods 2024

**Paper:** Cui et al. *scGPT: toward building a foundation model for single-cell multi-omics using generative AI.* Nature Methods 21, 1470–1480 (2024). DOI: 10.1038/s41592-024-02201-0

**Gap**

Single-cell data are large and heterogeneous, but many analytical tasks are trained independently.

**Logic chain**

```text
large heterogeneous single-cell corpus
→ generative pretraining
→ common cell / gene representation
→ multiple downstream tasks
→ multi-batch and multi-omic integration
→ perturbation prediction
→ inspect gene embeddings / attention for biological structure
```

**Reusable rule**

A foundation model paper needs evidence at both the task level and representation level. Benchmark performance alone does not demonstrate that the learned representation contains useful biology.

---

## 3. scFoundation — Nature Methods 2024

**Paper:** Hao et al. *Large-scale foundation model on single-cell transcriptomics.* Nature Methods (2024). DOI: 10.1038/s41592-024-02305-7

**Gap**

Existing single-cell models were limited by model capacity, gene dimensionality or training scale.

**Logic chain**

```text
scale model + gene vocabulary + corpus
→ task-specific pretraining design
→ cell and gene context representations
→ expression enhancement
→ drug-response prediction
→ perturbation prediction
→ annotation / gene-module inference
```

**Reusable rule**

When scale is part of the novelty, include scale ablations and show what additional scientific capability appears because of scale, not only that metrics improve.

---

## 4. Nicheformer — Nature Methods 2025

**Paper:** Tejada-Lapuerta et al. *Nicheformer: a foundation model for single-cell and spatial omics.* Nature Methods 22, 2525–2538 (2025). DOI: 10.1038/s41592-025-02814-z

**Gap**

Dissociated scRNA-seq loses spatial microenvironment information.

**Logic chain**

```text
information loss is explicitly defined
→ build mixed dissociated + spatial corpus
→ pretrain joint representation
→ create spatially specific downstream tasks
→ compare with non-spatial foundation models
→ ablate spatial training data
→ show spatial context can be transferred back to dissociated cells
```

**Why the story is strong**

The evaluation task directly matches the missing information that motivated the model.

**Reusable rule**

Design downstream tasks from the scientific gap. Do not benchmark only on standard tasks that are unrelated to the model’s claimed new information.

---

## 5. OmiCLIP / Loki — Nature Methods 2025

**Paper:** Chen et al. *A visual–omics foundation model to bridge histopathology with spatial transcriptomics.* Nature Methods 22, 1568–1582 (2025). DOI: 10.1038/s41592-025-02707-1

**Gap**

Histology and transcriptomics are complementary but typically modeled separately.

**Logic chain**

```text
paired image–omics corpus
→ joint representation learning
→ retrieval / alignment
→ annotation and decomposition
→ image-to-expression prediction
→ evaluate across simulations, public cohorts and in-house datasets
```

**Reusable rule**

For multimodal work, demonstrate what the second modality adds and evaluate transfer on independent data. Simply concatenating modalities is not a scientific contribution.

---

## 6. Human Cell Atlas → foundation model — Nature 2024 perspective

**Paper:** Rozenblatt-Rosen, Stubbington, Regev et al. *The Human Cell Atlas from a cell census to a unified foundation model.* Nature (2024). DOI: 10.1038/s41586-024-08338-4

**Conceptual progression**

```text
cell census
→ 3D tissue map
→ genotype-to-phenotype map
→ 4D developmental map
→ integrated biological foundation model
```

**Reusable rule**

A mature atlas evolves from cataloguing entities to explaining relationships across space, time, perturbation and phenotype.

---

## 7. Perturbation Cell and Tissue Atlas — Cell 2024 perspective

**Paper:** Rood, Hupalowska & Regev. *Toward a foundation model of causal cell and tissue biology with a Perturbation Cell and Tissue Atlas.* Cell 187, 4520–4545 (2024). DOI: 10.1016/j.cell.2024.07.035

**Core logic**

```text
large perturbational experiments
→ learn causal response structure
→ model predicts unmeasured perturbations
→ model selects informative next experiments
→ new experiments refine model
→ iterative causal atlas
```

**Reusable rule**

The strongest AI-for-biology loop is closed-loop experimentation. Prediction should change which experiment is done next.

---

## 8. Human embryonic limb atlas — Nature 2023

**Paper:** *A human embryonic limb cell atlas resolved in space and time.* Nature (2023). DOI: 10.1038/s41586-023-06806-x

**Gap**

Cell-state diversification during human limb development lacked integrated time and spatial context.

**Logic chain**

```text
multiple developmental timepoints
→ single-cell state atlas
→ identify lineage diversification and novel populations
→ map states spatially
→ connect programs to anatomical patterning
→ nominate regulatory factor(s)
→ cross-species comparison
```

**Reusable rule**

Developmental papers become mechanistic when they connect **state + time + space + regulator** rather than presenting separate atlases.

---

## 9. Human embryonic skeletal multi-omics — Nature 2024

**Paper:** *A multi-omic atlas of human embryonic skeletal development.* Nature 635, 657–667 (2024). DOI: 10.1038/s41586-024-08189-z

**Gap**

Lineage commitment in human embryonic skeletal tissues required joint transcriptional, epigenetic and spatial explanation.

**Logic chain**

```text
paired transcriptome + chromatin data
→ developmental states and trajectories
→ region-specific progenitors
→ regulatory network inference
→ spatial localization
→ distinguish alternative ossification programs
```

**Reusable rule**

Use multimodal data to answer a specific regulatory question. The modalities should converge on the same claim, not exist as parallel analyses.

---

## 10. Intact human gastrulation spatial atlas — Nature Cell Biology 2024

**Paper:** *Spatial transcriptomic characterization of a Carnegie stage 7 human embryo.* Nature Cell Biology (2024). DOI: 10.1038/s41556-024-01597-3

**Gap**

Early human gastrulation is difficult to study because intact tissue is rare and dissociation destroys geometry.

**Logic chain**

```text
serial spatial sections
→ single-cell-resolution reconstruction
→ 3D embryo model
→ localize lineage specification
→ identify unexpected cell positions / developmental events
→ independent immunofluorescence validation
```

**Reusable rule**

When sample number is intrinsically limited, strengthen the paper through spatial completeness, internal consistency and orthogonal validation rather than pretending statistical replication is larger than it is.

---

## 11. Spateo — Cell 2024

**Paper:** *Spatiotemporal modeling of molecular holograms.* Cell (2024). DOI: 10.1016/j.cell.2024.10.011

**Gap**

Embryogenesis is a 3D dynamic process, but most analyses reduce it to isolated slices or static cell states.

**Logic chain**

```text
whole-embryo spatial data
→ 3D alignment / reconstruction
→ tissue geometry
→ molecular gradients
→ signaling landscapes
→ morphometric vector fields
→ connect tissue-scale morphogenesis with molecular programs
```

**Reusable rule**

A computational framework becomes biologically compelling when each new mathematical object corresponds to a biological question that cannot be answered by a simpler representation.

---

## 12. Statistical inference at single-cell resolution — Nature Reviews Genetics 2024

**Paper:** Trapnell. *Revealing gene function with statistical inference at single-cell resolution.* Nature Reviews Genetics 25, 623–638 (2024). DOI: 10.1038/s41576-024-00750-w

**Conceptual shift**

Single-cell biology is moving from cataloguing heterogeneity toward designed perturbation, cohort-level inference and mechanistic questions.

**Reusable rule**

The sample, not the cell, is usually the independent replicate for condition-level claims. Use single-cell resolution to increase biological resolution, not to inflate sample size.

---

## 13. Cell identity + tissue architecture review — Nature Reviews Molecular Cell Biology 2025

**Paper:** Gulati, D’Silva, Liu, Wang, Newman et al. *Profiling cell identity and tissue architecture with single-cell and spatial transcriptomics.* Nature Reviews Molecular Cell Biology 26, 11–31 (2025). DOI: 10.1038/s41580-024-00768-2

**Conceptual progression**

```text
cell identity
→ multicellular neighborhood
→ recurrent tissue ecotype
→ spatial organization
→ disease or developmental consequence
```

**Reusable rule**

Cell-state discovery and tissue architecture are different evidence layers. A state can recur across locations; a niche additionally requires reproducible spatial organization and neighborhood structure.

---

# Cross-paper synthesis

Across these papers, the recurring structure is:

```text
1. Define information that current studies cannot observe or generalize.
2. Acquire or construct data that contain that missing information.
3. Establish a reliable representation / atlas before making novel claims.
4. Design analyses that directly test the central claim.
5. Use an orthogonal axis — space, time, modality, perturbation, species or cohort — to challenge the claim.
6. Add mechanistic or causal evidence only when supported.
7. End with a biological capability, not a software feature.
```

The most important distinction is between **technical novelty** and **scientific novelty**:

- technical novelty: a new architecture, loss, integration scheme or plotting method;
- scientific novelty: new biological information, mechanism, generalization or experimentally useful prediction.

Strong studies make the technical contribution serve the scientific one.