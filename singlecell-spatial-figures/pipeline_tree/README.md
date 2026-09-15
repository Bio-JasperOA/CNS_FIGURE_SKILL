# Pipeline-first figure architecture

This directory is the executable pipeline-aware plotting layer for scRNA-seq, spatial transcriptomics, cross-modal analysis, development/embryo studies, and biological foundation-model evaluation.

The governing rule is:

> every analysis process must produce at least one required figure, and every advanced analysis must map to at least one advanced figure.

The plotting layer does **not** rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram, scVI, segmentation, enrichment statistics or model fitting. It consumes reviewed result tables from those tools and renders them through stable contracts.

## Current executable status

- 36/36 registered pipeline modules are executable.
- 23 canonical result contracts are validated.
- 141 required-figure assignments and 107 advanced-figure assignments are registered.
- 240 unique figure targets are covered by runnable code, composites, or explicit evidence-dependent skip rules.
- GitHub Actions regression suite: **60 passed**.
- Complete deterministic synthetic gallery: **36 modules / 286 generated figure records**.
- Skill major version remains **v3**; FigureSpec remains `3.0`.
- Subtitle policy remains **forbidden**.

A target that depends on optional upstream evidence is not fabricated when that evidence is missing. Its manifest entry is recorded under `skipped` with a reason.

## Files

- `PIPELINE_TREE.md` — human-readable analysis → figure tree.
- `MODULE_REGISTRY.json` — machine-readable 36-module coverage registry.
- `RESULT_CONTRACTS.json` — 23 reusable result-table contracts.
- `IMPLEMENTED_MODULES.json` — executable implementation boundary.
- `run_pipeline.py` — canonical router for all 36 modules.
- `runtime*.py` — executable renderers/adapters.
- `runtime_fixtures*.py` — deterministic synthetic validation fixtures.
- `build_gallery.py` — renders the complete 36-module synthetic gallery.
- `RUNTIME.md` — runtime semantics, CLI and current validation record.
- `IMPLEMENTATION_ROADMAP.md` — completed development phases and maintenance rules.
- `validate_registry.py` — fails if an analysis node has no figure mapping, an unknown contract, duplicate IDs or subtitle-oriented output.
- `tests/` — registry, routing, rendering and file-output regression tests.

## Rendering levels

The pipeline exposes three conceptual levels:

1. `minimal` — the smallest scientifically complete view.
2. `advanced` — minimal plus a real scientific dimension such as comparison, uncertainty, hierarchy, paired structure, spatial context, transition structure, prediction error or multi-modal evidence.
3. `panel` — a publication-oriented composition of validated views without changing numerical meaning.

`advanced` never means more decoration, borders or colors by itself.

## Global figure rules

- No subtitle renderer. Legacy `subtitle` keys are ignored rather than moved elsewhere.
- Cell identities should keep a stable named color mapping across embedding, composition, communication and spatial panels.
- Palette choice and numeric normalization remain separate.
- Missing uncertainty, lineage, boundary, transition, neighborhood, morphology or model-error inputs are never invented for visual completeness.
- Multi-section scalar maps are rendered section-by-section using a common scale before review composition.
- Standalone PDF/SVG files are publication candidates; raster contact sheets are navigation/review composites.
- Synthetic fixtures are software tests, never biological evidence.

## Commands

Validate architecture and runtime:

```bash
python pipeline_tree/validate_registry.py validate
python -m pytest pipeline_tree/tests -q
```

Render all synthetic module examples:

```bash
python pipeline_tree/build_gallery.py --out build/pipeline_gallery
```

Render one real reviewed analysis result:

```bash
python pipeline_tree/run_pipeline.py \
  --module spatial.communication \
  --input spatial=results/spatial.csv \
  --input interaction=results/interaction.csv \
  --config project/spatial_communication.json \
  --out build/spatial_communication
```

See `RUNTIME.md` and `RESULT_CONTRACTS.json` before connecting real project outputs.
