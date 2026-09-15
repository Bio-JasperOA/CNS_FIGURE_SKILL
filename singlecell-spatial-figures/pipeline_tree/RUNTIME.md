# Executable pipeline runtime · tranche 1

This directory contains the pipeline-first registry plus the first executable module runtime. The roadmap is broader than the implementation.

## Runtime v1 modules

The following modules have executable plotting adapters:

- `scrna.qc`
- `scrna.composition_da`
- `scrna.communication`
- `spatial.expression`
- `spatial.mapping_deconvolution`
- `fm.reconstruction_prediction`
- `fm.benchmark`
- `development.stage_composition`

Each invocation consumes canonical tables, writes standalone PNG/PDF/SVG figures, and writes `manifest.json`. Review contact sheets are intentionally raster review artifacts; the standalone PDF/SVG outputs remain the publication candidates.

Modules not listed in `IMPLEMENTED_MODULES.json` remain roadmap-only.

## CLI

```bash
python pipeline_tree/runtime.py \
  --module scrna.qc \
  --input main=results/qc.csv \
  --config project/qc_plot.json \
  --out build/qc
```

All figures inherit the global no-subtitle rule. Real data must carry provenance. The runtime never reruns upstream analysis or invents p-values, intervals, trajectories, segmentation boundaries, mapping confidence, or uncertainty.

## Conditional outputs

Some advanced plots require optional upstream fields. For example, `da_forest` requires supplied effect intervals, LR bubbles require ligand/receptor columns, and segmentation overlays require supplied segmentation vertices. Missing optional evidence is recorded in `manifest.json` under `skipped`; it is never synthesized.
