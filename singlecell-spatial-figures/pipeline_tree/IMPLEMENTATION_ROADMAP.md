# Implementation roadmap

The registry is a coverage contract, not a claim that every target plot already has a dedicated renderer. Implementation proceeds in phases while keeping major version 3 and FigureSpec 3.0.

## Priority 1 — core paper pipeline

These modules should be implemented first because together they cover the dominant figure flow of most scRNA-seq and spatial-transcriptomics studies.

1. `scrna.qc`
2. `scrna.normalization_hvg`
3. `scrna.integration`
4. `scrna.clustering`
5. `scrna.annotation`
6. `scrna.markers_de`
7. `scrna.composition_da`
8. `scrna.trajectory`
9. `scrna.communication`
10. `spatial.qc`
11. `spatial.normalization_embedding`
12. `spatial.domains`
13. `spatial.expression`
14. `spatial.mapping_deconvolution`
15. `spatial.neighborhood_niche`
16. `spatial.communication`
17. `spatial.gradient_trajectory`
18. `cross_modal.reference_mapping`
19. `development.stage_composition`
20. `development.lineage_progression`
21. `development.spatial_gradient`
22. `development.virtual_embryo_prediction`
23. `fm.reconstruction_prediction`
24. `fm.benchmark`

### Priority-1 completion criterion

A module becomes `implemented` only when all of the following exist:

- validated result-table adapter/contract;
- every `required_plots` target has runnable code;
- every `advanced_plots` target has runnable code or a documented composite that calls implemented primitives;
- minimal and advanced synthetic fixtures;
- PNG/PDF/SVG output checks;
- stable palette identity when categorical biology is shared across panels;
- explicit uncertainty/denominator/unit semantics when applicable;
- no subtitle output;
- regression tests;
- a panel example when the module is used in a standard publication figure.

## Priority 2 — common advanced analyses

- `scrna.pathway_activity`
- `scrna.velocity_fate`
- `scrna.regulon_module`
- `spatial.svg_autocorrelation`
- `spatial.multisection`
- `cross_modal.marker_validation`
- `cross_modal.niche_validation`
- `cross_modal.communication_validation`
- `fm.latent_embedding`
- `fm.ablation_scaling`

These modules should reuse existing primitives wherever scientifically valid, but receive dedicated renderers where the semantics differ. For example, fate probability is not generic continuous expression, and Moran's I is not a generic effect size.

## Priority 3 — specialized extensions

- `scrna.perturbation_prediction`
- `spatial.histology_morphology`

These require additional input types, image/segmentation handling or experiment-specific semantics and should not block the core single-cell/spatial pipeline.

## Implementation pattern

Each module should evolve toward:

```text
plots/<domain>/<module>/
├─ adapter.py          # reviewed upstream result -> canonical table
├─ minimal.py          # smallest scientifically complete view
├─ advanced.py         # real additional information layer
├─ panel.py            # multi-plot publication composition
├─ schema.json         # module-specific constraints extending RESULT_CONTRACTS
├─ fixtures/
│  ├─ example.csv
│  └─ config.json
├─ tests/
│  └─ test_module.py
└─ references.md       # paper/code design evidence and evidence grade
```

The existing `style_gallery` is the reusable primitive layer during migration. New module code should call those primitives when their semantics match instead of cloning plotting code.

## Advanced-figure design rule

An advanced plot must add at least one of:

- real comparison;
- uncertainty;
- paired/matched structure;
- hierarchy;
- spatial context or boundary;
- temporal/lineage structure;
- transition mass/probability;
- multi-modal validation;
- prediction error/uncertainty;
- evidence linking a summary to underlying observations.

It must not qualify as advanced solely because it has more colors, annotations, borders, labels, shadows or decorative insets.

## Panel implementation order

After Priority-1 primitives are stable, build panels in this order:

1. single-cell atlas;
2. trajectory/development;
3. spatial atlas;
4. cell-cell communication;
5. scRNA + spatial integration;
6. foundation-model / virtual-embryo evaluation.

Panels may compose existing plots but must not silently rescale, reorder identities, recompute statistics, or change denominators.