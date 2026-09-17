---
name: singlecell-spatial-analysis-strategy
scope: scRNA-seq, snRNA-seq, spatial transcriptomics, developmental and cross-modal analysis planning
---

# Single-cell & Spatial Analysis Strategy Skill

Use this Skill **after** the biological gap and claim–evidence graph are defined, and **before** selecting software or figures.

Read:

1. `ANALYSIS_STRATEGY_LIBRARY.md`
2. `ANALYSIS_STRATEGY_CATALOG.json`
3. `SKILL.md` for the parent research-logic rules.

## 1. Mandatory routing rule

For each proposed analysis step, state:

- biological question;
- claim(s) supported;
- minimum required input;
- biological replicate / independence unit;
- analysis family;
- expected output;
- diagnostic check;
- what the result can support;
- what it cannot support;
- validation or orthogonal evidence.

Do not output a bare software list.

## 2. Backbone versus optional modules

### Backbone

Most studies need some version of:

```text
QC
→ representation / normalization
→ annotation
→ sample/specimen-aware comparison
→ claim-specific downstream analysis
→ validation
```

### Optional modules

Add only when required by the biological question:

- integration / batch correction;
- differential abundance;
- donor-aware DE;
- pathway / programme analysis;
- regulon / TF activity;
- trajectory / pseudotime;
- RNA velocity / fate;
- cell–cell communication;
- perturbation response;
- spatial mapping / deconvolution;
- spatial domains;
- SVG / autocorrelation;
- neighborhood / niche analysis;
- spatial gradients;
- spatial communication;
- multi-section integration;
- histology / morphology integration.

## 3. Default single-cell route

For a conventional multi-sample scRNA-seq study:

```text
QC / doublet / contamination
→ sample-aware normalization / representation
→ integration only if needed
→ broad annotation
→ subtype/state refinement
→ sample-level composition
→ cell-type-specific donor-aware DE
→ coherent programmes / regulators
→ trajectory / communication only if they answer a defined claim
→ independent or orthogonal validation
```

## 4. Default spatial route

For a conventional spatial transcriptomics study:

```text
spatial QC / tissue integrity
→ cell typing or deconvolution
→ domains / architecture
→ spatially patterned genes/programmes
→ neighborhoods / niches
→ gradients or communication only when anatomically motivated
→ multi-section / specimen validation
→ scRNA, histology or perturbation cross-validation
```

## 5. Default scRNA + spatial route

Prefer an integrated biological story:

```text
scRNA defines molecular states
→ spatial data localize states
→ identify disease/stage-specific niche or axis
→ dissect niche-associated programmes in scRNA
→ nominate regulator / communication mechanism
→ return to spatial data for localization / proximity validation
→ external / histology / perturbation validation
```

Do not run the two modalities as independent parallel analyses unless the study question requires it.

## 6. Statistics and independence rules

- Cells are usually not independent biological replicates for donor/condition claims.
- Use donor/sample/embryo/specimen-level inference for population-level comparisons.
- Pseudobulk or other specimen-aware models are preferred for many condition-level DE questions.
- Adjacent serial sections are not automatically independent biological replicates.
- Random cell splits are weak evidence for donor, embryo, tissue or spatial generalization.

## 7. Interpretation boundaries

- clustering ≠ new cell type;
- UMAP distance ≠ biological distance;
- pseudotime ≠ lineage;
- RNA velocity ≠ ground-truth fate;
- ligand–receptor score ≠ demonstrated signaling;
- spatial deconvolution ≠ exact cell contact;
- spatial clustering ≠ anatomy without supporting evidence;
- enrichment ≠ mechanism;
- multimodal UMAP overlap ≠ successful biological integration.

## 8. Required planning output

When asked for a bioinformatics analysis plan, return:

1. **Scientific objective**
2. **Minimal backbone**
3. **Question-driven optional modules**
4. **Per-step input → method family → output → supported claim**
5. **Replicate / independence unit**
6. **Critical diagnostics**
7. **Validation plan**
8. **Analyses explicitly not recommended and why**
9. **Minimal publishable workflow**
10. **Ambitious extension**

The goal is a coherent evidence chain, not maximal pipeline complexity.
