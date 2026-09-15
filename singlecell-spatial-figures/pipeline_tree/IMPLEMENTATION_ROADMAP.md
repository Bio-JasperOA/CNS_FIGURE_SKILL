# Implementation roadmap · runtime complete

The original implementation roadmap is now complete for the registered pipeline tree. The Skill remains major version **3** and FigureSpec remains **3.0**.

## Completion status

| Phase | Scope | Status |
|---|---|---|
| Priority 1 | core scRNA/ST/development/model pipeline | complete |
| Priority 2 | common advanced analyses | complete |
| Priority 3 | perturbation and histology/morphology extensions | complete |
| Cross-modal | reference mapping, marker, niche and communication validation | complete |
| Synthetic gallery | all registered executable modules | complete |

Current implementation boundary: **36/36 pipeline modules executable**.

## Implemented domains

### scRNA-seq · 13/13

- `scrna.qc`
- `scrna.normalization_hvg`
- `scrna.integration`
- `scrna.clustering`
- `scrna.annotation`
- `scrna.markers_de`
- `scrna.composition_da`
- `scrna.pathway_activity`
- `scrna.trajectory`
- `scrna.velocity_fate`
- `scrna.communication`
- `scrna.regulon_module`
- `scrna.perturbation_prediction`

### Spatial transcriptomics · 11/11

- `spatial.qc`
- `spatial.normalization_embedding`
- `spatial.domains`
- `spatial.expression`
- `spatial.mapping_deconvolution`
- `spatial.svg_autocorrelation`
- `spatial.neighborhood_niche`
- `spatial.communication`
- `spatial.gradient_trajectory`
- `spatial.multisection`
- `spatial.histology_morphology`

### Cross-modal · 4/4

- `cross_modal.reference_mapping`
- `cross_modal.marker_validation`
- `cross_modal.niche_validation`
- `cross_modal.communication_validation`

### Development / embryo · 4/4

- `development.stage_composition`
- `development.lineage_progression`
- `development.spatial_gradient`
- `development.virtual_embryo_prediction`

### Foundation-model evaluation · 4/4

- `fm.latent_embedding`
- `fm.reconstruction_prediction`
- `fm.benchmark`
- `fm.ablation_scaling`

## Completion criterion used

A module is considered executable only when:

- its reviewed result-table contract exists;
- it is listed in `IMPLEMENTED_MODULES.json`;
- `run_pipeline.py` routes it to executable code;
- it produces at least one required and one advanced scientific view for the deterministic fixture;
- all declared targets are either generated or explicitly skipped for a documented missing upstream field;
- figure exports are checked as actual files;
- no subtitle is rendered;
- regression tests pass;
- the full synthetic gallery can render the module in the same CI run.

## Latest validation

GitHub Actions complete run:

- architecture: 36 modules / 23 contracts;
- required assignments: 141;
- advanced assignments: 107;
- unique targets: 240;
- tests: **60 passed**;
- complete gallery: **36 modules / 286 generated figure records**.

## Architecture after completion

The implementation intentionally keeps a shared runtime rather than creating 36 isolated plotting packages:

```text
reviewed analysis output
        │
        ▼
RESULT_CONTRACTS.json
        │
        ▼
run_pipeline.py
        │
        ├── reusable style_gallery primitives
        ├── pipeline-specific adapters
        ├── minimal scientific views
        ├── advanced scientific views
        └── publication/review panels
        │
        ▼
PNG / PDF / SVG + manifest.json
```

This design keeps figure semantics centralized and prevents copies of near-identical UMAP, heatmap, network and spatial renderers from drifting apart.

## Maintenance roadmap

Development now shifts from breadth to quality and real-project validation:

1. connect real Seurat/Scanpy/CellChat/CellRank/Squidpy/cell2location outputs through thin adapters;
2. add real-data stress fixtures without committing sensitive or unpublished data;
3. benchmark large-category legends, dense matrices and multi-section layouts;
4. add native R parity only when an R backend is actually executed and tested;
5. expand paper-reference evidence for each advanced target;
6. promote review-only panel compositions to vector-native panel layouts where scientifically useful;
7. keep palette identity and numerical normalization stable across multi-panel manuscripts.

## Scientific boundary

“36/36 executable” means every registered analysis node has a runnable visualization route. It does not mean the repository performs the upstream biological/statistical analysis. P-values, confidence intervals, clustering, cell annotations, trajectories, communication inference, deconvolution, neighborhood definitions, image segmentation and prediction uncertainty remain upstream reviewed inputs.

Advanced figures must continue to add real scientific structure—comparison, uncertainty, pairing, hierarchy, spatial context, trajectory, transition, multimodal evidence or prediction error—not decoration.
