# Executable pipeline runtime · v2.0

The pipeline-first runtime now covers all **36/36 registered analysis nodes** while the Skill remains major version **v3** and FigureSpec remains `3.0`.

The runtime is a plotting/output layer only. It consumes reviewed upstream results, validates canonical result contracts, writes reusable standalone figures and records explicit skips when optional upstream evidence is absent. It does **not** rerun Seurat, Scanpy, CellRank, scVelo, CellChat, LIANA, Milo, scCODA, Squidpy, cell2location, image segmentation, enrichment statistics, model fitting or biological inference.

## Coverage

- scRNA-seq: 13/13 modules
- spatial transcriptomics: 11/11 modules
- cross-modal scRNA + spatial: 4/4 modules
- development / embryo: 4/4 modules
- foundation-model evaluation: 4/4 modules
- total: **36/36 modules**

The roadmap contains 141 required-figure assignments and 107 advanced-figure assignments across 240 unique target names. A module is considered executable only when it is listed in `IMPLEMENTED_MODULES.json`, routed by `run_pipeline.py`, has a deterministic fixture, and passes real PNG/PDF/SVG export tests.

## Canonical CLI

```bash
python pipeline_tree/run_pipeline.py \
  --module scrna.trajectory \
  --input main=results/trajectory.csv \
  --input embedding=results/embedding.csv \
  --config project/trajectory_plot.json \
  --out build/trajectory
```

For each invocation, `manifest.json` records:

- module ID and runtime version;
- canonical contract for every named input;
- input hashes and row counts;
- generated targets and file paths;
- explicitly skipped targets and reasons;
- scientific-boundary statement.

All standalone renderers follow the global **no-subtitle** policy. Legacy `subtitle` config is removed before dispatch.

## Required versus conditional outputs

Every pipeline process has required and advanced figure targets in `MODULE_REGISTRY.json`. Some targets require optional upstream evidence. Examples include supplied confidence, intervals, segmentation vertices, ligand/receptor identity, pathway labels, fate probabilities, section alignment, image features or model uncertainty.

If the necessary evidence is absent, the runtime records the target under `skipped` with a concrete reason. It never fabricates the missing value merely to make a panel look complete.

Multi-section spatial scalar maps are rendered section-by-section with a shared scale and then assembled into a review contact sheet. The individual PDF/SVG files remain the vector publication candidates; contact-sheet panels are review/navigation artifacts.

## Full synthetic validation

GitHub Actions workflow `Validate pipeline figure tree` validates the registry, runs the runtime regression tests and then executes:

```bash
python pipeline_tree/build_gallery.py --out /tmp/cns_pipeline_gallery
```

Latest complete validation for runtime v2.0:

- registry: 36 modules, 23 canonical contracts;
- tests: **60 passed**;
- full gallery: **36 modules rendered**;
- generated figure records: **286**;
- subtitle policy: forbidden.

All bundled fixtures are deterministic synthetic style fixtures. These results prove software execution and output coverage, not biological validity on a real dataset.

## Implementation files

- `run_pipeline.py` — canonical router
- `runtime.py` — base runtime and first renderer tranche
- `runtime_tranche2.py` — annotation / DE / trajectory / spatial-domain tranche
- `runtime_tranche3.py` — spatial communication / cross-modal / lineage / model tranche
- `runtime_tranche4.py` — pathway / regulon / SVG / gradient / virtual-embryo tranche
- `runtime_tranche5.py` — normalization / integration / clustering / velocity / remaining spatial and cross-modal tranche
- `runtime_final_fixes.py` — multi-section spatial and dense-overlap layout adapters
- `runtime_fixtures*.py` — deterministic synthetic fixtures
- `RESULT_CONTRACTS.json` — canonical input contracts
- `IMPLEMENTED_MODULES.json` — executable capability registry
- `MODULE_REGISTRY.json` — full pipeline-to-figure tree
- `build_gallery.py` — complete executable gallery builder

## Remaining boundaries

36/36 means every registered pipeline node has an executable visualization route. It does **not** mean every upstream scientific method is implemented by this repository. Statistical testing, clustering, annotation, trajectories, communication inference, deconvolution, spatial neighborhoods, segmentation and model uncertainty remain upstream analyses.

Native R parity is also not claimed. The current executable pipeline runtime is Python-first; final carrier review and the older v3 FigureSpec audit rules remain separate safeguards.
