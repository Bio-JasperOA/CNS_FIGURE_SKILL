# Repository agent routing

## Start with the requested task

Read the root `README.md` Invocation section and `STRATEGY_ROUTES.json`. The JSON file defines repository-local `task_mode` values, entry documents, prerequisites, deliverables and analysis-to-plot handoffs. These are agent routing labels, not shell commands or automatically installed slash commands. All paths in that registry are repository-root relative.

| Task mode | Instruction |
|---|---|
| `research-design` | Read `singlecell-spatial-figures/research_logic/SKILL.md`; design or critique the question, provisional claims and evidence chain. |
| `analysis-plan` | Read `singlecell-spatial-figures/research_logic/ANALYSIS_SKILL.md`; choose question-driven analysis families and diagnostics. |
| `analysis-code` | Read `singlecell-spatial-figures/research_logic/ANALYSIS_EXECUTION.md`; author project-specific R/Python scripts from a reviewed plan. |
| `results-interpret` | Read `singlecell-spatial-figures/result_interpretation/SKILL.md`; interpret source-linked actual results before manuscript-level conclusions. |
| `plot-single` | Read `singlecell-spatial-figures/style_gallery/README.md`; render one reviewed table with an existing gallery kind. |
| `plot-pipeline` | Read `singlecell-spatial-figures/pipeline_tree/README.md`; render the reviewed inputs of one registered module. |
| `figure-audit` | Read `singlecell-spatial-figures/SKILL.md`; select strict FigureSpec rendering, PDF inspection, carrier checking or artifact-bound review. |
| `end-to-end` | Follow the staged chain below; do not recursively reload this document. |

Honor an explicit task mode. Without one, select the smallest route that answers the user's task and state the selected route briefly. A request to redraw an existing result does not require a new research plan. A request for an analysis plan does not authorize data processing or figure regeneration. Do not invent route IDs, module IDs, CLI flags, missing data or claimed capabilities.

`language: R|Python|mixed` is an analysis implementation preference, not renderer parity. `execution: plan_only` means no analysis execution, `write_code` means source deliverables, and `run_approved` means the user has explicitly requested execution of the named scope. Respect scientific prerequisites and actual data access. An explicit, sufficiently specified execution request does not need redundant confirmation. Never report an unexecuted script as a completed analysis.

## Research design and scientific strategy

For research questions, study critique, literature-derived logic or prioritization, read:

1. `singlecell-spatial-figures/research_logic/SKILL.md`
2. `singlecell-spatial-figures/research_logic/CNS_ANCHORS.md`
3. `singlecell-spatial-figures/research_logic/PAPER_LOGIC_LIBRARY.md`
4. `singlecell-spatial-figures/research_logic/RESEARCH_PLAN_SCHEMA.json` when authoring a full machine-readable research plan.

Start from the biological gap, answerable question, provisional central claim, alternatives and claim-evidence graph, not software or attractive plots. Treat the literature library as a navigation aid: verify specific literature claims in the actual source and distinguish verified facts from hypotheses. A valid JSON plan is not a scientific certification.

For biological foundation-model projects, address biological utility, appropriate baselines, OOD axes, specimen-level independence and leakage. For development/embryo and spatial studies, distinguish measured time and space from inferred geometry. Do not infer a true lineage from pseudotime or a spatial mechanism from dissociated data alone.

## Analysis strategy and code authoring

After the scientific objective is sufficiently defined, read:

1. `singlecell-spatial-figures/research_logic/ANALYSIS_SKILL.md`
2. `singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_LIBRARY.md`
3. `singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_CATALOG.json`
4. `singlecell-spatial-figures/research_logic/ANALYSIS_EXECUTION.md` only when authoring or running project code.

Choose the smallest defensible analysis chain. Each step needs a question or technical quality objective, actual input, independence unit, method-selection reason, output, diagnostic, limitation, validation and figure handoff or justified skip. Do not add communication, trajectory, velocity, regulons, niches or deconvolution simply because they are available.

Use `STRATEGY_ROUTES.json` `analysis_to_plot` only for candidate downstream figures. For example, analysis `sc.de` and plotting `scrna.markers_de` are not interchangeable IDs. The latter currently requires separate `markers` and `de` tables. Check all current named inputs and conditions; mappings do not manufacture missing outputs or run analysis algorithms.

When a relevant analysis is absent from the catalog, describe its scientific and implementation requirements. Add a reviewed definition, handoff and validation when repository extension is requested. Until then, label it a project-specific or unregistered analysis rather than invoking a fictional built-in module.

## Figure generation and audit

For reviewed results, use the selected plotting entry and also read:

- `singlecell-spatial-figures/SKILL.md`
- `singlecell-spatial-figures/pipeline_tree/IMPLEMENTED_MODULES.json` for module inputs and conditional capabilities
- `singlecell-spatial-figures/pipeline_tree/RESULT_CONTRACTS.json` for result-table fields
- the relevant style-gallery design and example documentation.

Do not refit biological/statistical models while plotting. Do not create missing intervals, significance, boundaries, trajectories, probabilities or conclusions. `plot-single` supports `minimal` and `advanced`, not a generic `panel` mode. Pipeline module figures and strict FigureSpec panels are distinct execution paths. Check manifest-generated records and skipped reasons instead of claiming all mapped targets were produced.

Keep the established palette policy, no subtitles, aligned legends and no explanatory microcopy on the canvas. Retain essential data labels and synthetic-data identification; put interpretation in captions/provenance. Current R bridges are not native equivalents of the full Python gallery/runtime.

## Combined task

```text
research-design
→ analysis-plan
→ analysis-code
→ actual analysis execution when requested and feasible
→ result diagnostics
→ results-interpret
→ plot-single or plot-pipeline
→ figure-audit when required
```

`end-to-end` defaults to planning. Respect the requested execution stage, reuse adequate prior work, and stop only the branches whose prerequisites fail. Keep status for each step separate: planned, code written, executed, checked, or skipped. Never reverse this order by retrofitting a scientific story to attractive figures.

<!-- RESULT_INTERPRETATION:START -->
## Source-linked result interpretation

Use `results-interpret` after analysis diagnostics or directly on supplied results. Read `singlecell-spatial-figures/result_interpretation/SKILL.md` and its assay/narrative playbooks. Reuse available data-adaptation profiles and experiment metadata; do not require a complete project restart.

For each result separate observation, biological meaning, explanation, alternatives and claim boundary. Integrate same-data consistency, orthogonal assays, interventions and independent validation without treating them as interchangeable. Preserve material negative and contrary evidence. Cite the actual source table/panel for experimental statements and verified literature only for external context.

`interpretation_depth` is quick, full or manuscript; `response_language` controls prose. This agent-only route uses plan_only for read-only interpretation, not for rerunning analyses. The optional `review_results.py` helper checks declared evidence and source bindings; it does not establish biological truth. Keep review pending and return targeted reanalysis to analysis-plan/analysis-code only when requested.

For combined tasks: question → data adaptation when available → analysis/diagnostics → results-interpret ↔ discriminating validation → plotting/manuscript handoff. Diagnostic plots may come earlier. Do not redesign palettes or renderers while adding interpretation.
<!-- RESULT_INTERPRETATION:END -->

## Maintenance

When modifying task modes, named entry files or handoffs, update `STRATEGY_ROUTES.json`, the root README and these instructions together, then run:

```bash
python .github/scripts/validate_strategy_routes.py --self-test
```

Do not change figure renderers, palettes or generated images during documentation-only work. Keep Skill major version 3 and FigureSpec 3.0 unless the user explicitly requests otherwise.
