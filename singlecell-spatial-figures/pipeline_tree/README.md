# Pipeline-first figure architecture

This directory turns the figure Skill into a pipeline-aware plotting layer for scRNA-seq, spatial transcriptomics, cross-modal analysis, development/embryo studies, and biological foundation-model evaluation.

The governing rule is:

> every analysis process must produce at least one required figure, and every advanced analysis must map to at least one advanced figure.

The plotting layer does **not** rerun Seurat, Scanpy, CellRank, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, Tangram, scVI or other analysis methods. It consumes reviewed result tables from those tools and renders them through stable contracts.

## Files

- `PIPELINE_TREE.md` — human-readable analysis → figure tree.
- `MODULE_REGISTRY.json` — machine-readable module/plot coverage registry.
- `RESULT_CONTRACTS.json` — reusable result-table contracts shared by modules.
- `IMPLEMENTATION_ROADMAP.md` — implementation order and completion criteria.
- `validate_registry.py` — fails if any analysis node has no required plot, no advanced plot, an unknown contract, duplicate IDs, or subtitle-oriented output.
- `tests/test_registry.py` — regression tests for the architecture.

## Rendering levels

Every reusable plot family should eventually expose three levels:

1. `minimal` — the smallest scientifically complete view.
2. `advanced` — the minimal view plus a real scientific dimension such as comparison, uncertainty, hierarchy, paired structure, spatial context, transition structure, or multi-modal evidence.
3. `panel` — a publication-ready composition that joins several validated plots without changing their numerical meaning.

`advanced` never means more decoration, more borders, or more colors by itself.

## Global figure rules

- No subtitle renderer. Legacy `subtitle` keys are ignored rather than moved elsewhere.
- Cell identities keep a stable named color mapping across embedding, composition, communication and spatial panels.
- Palette choice and numeric normalization remain separate.
- Missing uncertainty, lineage, boundary, transition, neighborhood, morphology, or model-error inputs are never invented for visual completeness.
- Synthetic fixtures are always labelled as synthetic examples.
- A process can be marked complete only when its required plots, advanced plots, result contract, tests and at least one example are present.

## Commands

```bash
python pipeline_tree/validate_registry.py validate
python pipeline_tree/validate_registry.py tree
python -m pytest pipeline_tree/tests -q
```

The registry intentionally contains both currently reusable `style_gallery` backends and future plot targets. A plot named in the registry is a required capability target, not automatically a claim that the renderer already exists.