# CNS Anchor Set

This compact reading set keeps the Research Logic Skill anchored to representative **Cell / Nature / Science** studies rather than to one journal family.

## Nature anchors

### Geneformer — Nature 2023

Theodoris et al. *Transfer learning enables predictions in network biology.* DOI: 10.1038/s41586-023-06139-9

**Logic:** large general corpus → transfer to limited-data biology → network interpretation → in silico perturbation → experimental validation.

### Human embryonic limb — Nature 2023

*A human embryonic limb cell atlas resolved in space and time.* DOI: 10.1038/s41586-023-06806-x

**Logic:** stage-resolved atlas → spatial mapping → lineage diversification → regulatory factor → cross-species comparison.

### Human embryonic skeletal multi-omics — Nature 2024

*A multi-omic atlas of human embryonic skeletal development.* DOI: 10.1038/s41586-024-08189-z

**Logic:** transcriptome + chromatin → region-specific trajectories → regulatory networks → spatial confirmation.

### Human Cell Atlas perspective — Nature 2024

*The Human Cell Atlas from a cell census to a unified foundation model.* DOI: 10.1038/s41586-024-08338-4

**Logic:** census → 3D map → causal genotype-to-phenotype map → 4D development → integrated foundation model.

## Cell anchors

### Perturbation Cell and Tissue Atlas — Cell 2024

Rood, Hupalowska & Regev. *Toward a foundation model of causal cell and tissue biology with a Perturbation Cell and Tissue Atlas.* DOI: 10.1016/j.cell.2024.07.035

**Logic:** perturbation experiment → causal response model → predict unmeasured interventions → choose next experiment → iterative causal atlas.

### Spateo — Cell 2024

*Spatiotemporal modeling of molecular holograms.* DOI: 10.1016/j.cell.2024.10.011

**Logic:** 3D reconstruction → tissue geometry → gradients → signaling → morphometric vector fields → molecular explanation of morphogenesis.

### Spatiotemporal developing human brain atlas — Cell 2023

*Spatiotemporal transcriptome atlas reveals the regional specification of the developing human brain.* Cell 186 (2023).

**Logic:** broad developmental atlas → regional specification → spatially organized programs → temporal and anatomical interpretation.

## Science anchors

### sci-Space — Science 2021

Srivatsan et al. *Embryo-scale, single cell spatial transcriptomics.* Science 373, 111–117 (2021). DOI: 10.1126/science.abb9536

**Gap:** available approaches traded off large field of view against cellular resolution.

**Logic:** new spatial measurement → whole-embryo application → integrate with existing non-spatial atlases → identify spatially patterned genes and cell states → relate developmental pseudotime to anatomical migration patterns.

**Reusable rule:** a technology paper is strongest when the measurement capability unlocks a biological question that prior data could not resolve.

### Whole-embryo spatial transcriptomics — Science 2026

Wan et al. *Whole-embryo spatial transcriptomics at subcellular resolution from gastrulation to organogenesis.* Science 391, eadt3439 (2026). DOI: 10.1126/science.adt3439

**Gap:** systematic whole-embryo gene-expression patterning across development remained difficult to measure at subcellular resolution.

**Logic:** whole-embryo high-resolution imaging → spatial atlas across development → integrate with large-scale single-cell multi-omics → expand from measured gene panel toward genome-wide regulatory interpretation.

**Reusable rule:** when the novelty is measurement scale/resolution, demonstrate how the new scale changes biological inference, not only how many cells or genes were measured.

## Review / synthesis anchors

### Nature Reviews Genetics 2024

Trapnell. *Revealing gene function with statistical inference at single-cell resolution.* DOI: 10.1038/s41576-024-00750-w

**Key lesson:** move from cell catalogues to statistically defensible, perturbation-aware and cohort-aware inference.

### Nature Reviews Molecular Cell Biology 2025

Gulati, D’Silva, Liu, Wang, Newman et al. *Profiling cell identity and tissue architecture with single-cell and spatial transcriptomics.* DOI: 10.1038/s41580-024-00768-2

**Key lesson:** cell identity, neighborhood structure and tissue ecotype are distinct evidence layers and should not be conflated.

### Cell 2024 causal-atlas perspective

Rood et al. DOI: 10.1016/j.cell.2024.07.035

**Key lesson:** causal biological foundation models should emerge from iterative experiment–model–experiment loops.

# What Codex should learn from the set

The journal-specific styles differ, but the shared research grammar is stable:

```text
important missing biological information
→ data or experiment designed to capture it
→ reliable representation / atlas
→ focused discovery
→ mechanistic or predictive explanation
→ orthogonal challenge
→ generalization or perturbation
→ biological conclusion
```

The Skill should imitate this **logic**, not the surface methods or figure count of any paper.