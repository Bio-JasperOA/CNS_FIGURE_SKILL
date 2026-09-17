# Analysis-code execution contract

This file defines the repository-local `analysis-code` route. It is an agent instruction, not a bundled end-to-end Seurat/Scanpy executable. Select methods using `ANALYSIS_SKILL.md` and the actual project design; then author reproducible project-specific code. The plotting engine remains downstream.

## Invocation and prerequisites

Read `../../STRATEGY_ROUTES.json` from this directory's parent Skill root via the repository root: the canonical file is `/STRATEGY_ROUTES.json` in the checkout. All request paths are relative to the repository working directory unless explicitly absolute.

A request should contain `task_mode: analysis-code`, `language: R|Python|mixed`, `execution: write_code|run_approved`, the reviewed plan, input paths, sample metadata, output directory and compute constraints. These fields are a documented agent convention, not command-line flags.

`write_code` is the default: write scripts and tests without claiming the analysis was run. `run_approved` authorizes only the named analysis in the specified environment; it does not authorize overwriting raw inputs, publishing data, uploading private files, or installing arbitrary infrastructure. An explicitly requested and sufficiently specified run does not need another confirmation. `plan_only` requests design only and must not execute analysis.

Do not restart research planning when an adequate approved plan already exists. Do not require all optional methods. For a focused task, consume the approved contrast and relevant inputs rather than imposing a full atlas workflow.

## Preflight before analysis

Inspect actual files and metadata before selecting an assay, matrix layer, contrast or tool. Record modality, observation unit, feature identifiers, dimensions, sparsity, counts versus transformed values, sample/donor/embryo identifiers, condition, pairing, batch and spatial units when relevant. Check key uniqueness and joins, missing levels, complete confounding and the estimability of the requested contrast.

Missing raw counts, biological replication, spliced/unspliced data, registered images, segmentation or spatial coordinates must remain explicit limitations. Do not reconstruct missing measurements from normalized values or plot geometry. Halt only the affected branch, preserve diagnostics, and describe the supported descriptive alternative. QC and other technical prerequisites may support a data-quality objective rather than a biological subclaim.

Separate immutable input data, working intermediates and outputs. Keep sparse matrices sparse; inspect the environment and workload before choosing memory-intensive or GPU-dependent code. Use project-local environments and record package versions actually resolved. Never present an untested package combination as validated.

## Code deliverables

Create a project directory such as:

```text
project/
├── analysis_plan.md
├── config/analysis.yaml
├── scripts/01_preflight.R or 01_preflight.py
├── scripts/02_<approved_step>.R or .py
├── scripts/export_plot_contracts.R or .py
├── tests/
├── environment/                 # dependency declaration / resolved versions
├── results/                     # created only by actual execution
├── logs/                        # created only by actual execution
└── RUN.md                       # exact commands and verified execution status
```

Use numbered steps only where they express a real dependency. Paths and thresholds belong in configuration rather than repeated hard-coded values. Include deterministic seeds when applicable, shape/type checks, explicit errors, checkpoints and sample-level diagnostic summaries. Pin a tested environment only after it was tested; otherwise label the environment declaration unverified.

Provide native R or Python analysis code according to the request and method availability. `language: R` does not mean every method must be reimplemented in R, or that the figure runtime has native R parity. For mixed-language steps, document the handoff format, identifiers, matrix orientation, assay/layer, units and version boundaries.

## Execution and reporting

The execution order is preflight → approved analysis → diagnostics → interpretation review → export of reviewed results → requested figures. Record each step as `not_run`, `passed`, `failed` or `skipped`, with the command, exit code and actual output paths. Report scientific limitations separately from software status. Passing tests does not validate the biological claim.

Do not remove samples, change contrasts, lower statistical thresholds or choose additional methods merely to obtain the desired result. Preserve negative findings and sensitivity checks. No automatic causal certification or journal-readiness label is permitted.

## Figure handoff

Use `/STRATEGY_ROUTES.json` `analysis_to_plot` to identify candidate plotting modules. Before exporting, inspect `../pipeline_tree/IMPLEMENTED_MODULES.json` and `../pipeline_tree/RESULT_CONTRACTS.json` relative to this directory. Use all required named input tables of the selected module; a mapping is not an automatic conversion.

For example, `sc.de` routes toward `scrna.markers_de`, whose current renderer needs separate `markers` and `de` inputs. A DE table alone does not become a marker table. With only one reviewed effect table, select an appropriate single chart instead of fabricating the missing input.

Export explicit IDs, sample scope, units, denominator, transformation, effect definition and interval definition. Keep statistics and fitted quantities from their actual upstream models. Missing optional confidence intervals, gene-level measurements, trajectories or boundaries must not be generated for visual completeness.

Record a figure or an explicit skip/failure reason for every executed analysis step. The visual requirements remain no subtitles, the existing palette policy, aligned legends and no explanatory microcopy on the canvas. Retain interpretation details in captions/provenance; do not hide information necessary to understand the statistical comparison.

## Completion criterion

The route is complete when the requested deliverable exists at the requested stage: a checked plan for `plan_only`, source code plus run instructions for `write_code`, or recorded execution outputs and diagnostics for `run_approved`. Distinguish a completed code-writing task from a completed biological analysis.

<!-- RESULT_INTERPRETATION:START -->
## Interpretation handoff

After diagnostics, invoke `results-interpret` for source-linked biological interpretation before manuscript claims. Read `../result_interpretation/SKILL.md`. Preserve assay/layer, contrast, biological units, normalization, intervals, limitations and negative results. No completed analysis is assumed merely because its script exists.
<!-- RESULT_INTERPRETATION:END -->
