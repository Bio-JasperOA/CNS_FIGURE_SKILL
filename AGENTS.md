# Repository agent routing

This repository has two complementary execution layers.

## Research design / scientific strategy

If the task asks to design, critique, prioritize, extend or interpret a study, **read first**:

1. `singlecell-spatial-figures/research_logic/SKILL.md`
2. `singlecell-spatial-figures/research_logic/CNS_ANCHORS.md`
3. `singlecell-spatial-figures/research_logic/PAPER_LOGIC_LIBRARY.md`
4. `singlecell-spatial-figures/research_logic/ANALYSIS_SKILL.md` for operational scRNA-seq / spatial analysis planning.
5. `singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_LIBRARY.md`
6. `singlecell-spatial-figures/research_logic/ANALYSIS_STRATEGY_CATALOG.json` when selecting concrete analysis families.
7. `singlecell-spatial-figures/research_logic/RESEARCH_PLAN_SCHEMA.json` when producing a durable project plan.

Do not begin a research-design task with software, analysis methods or figures. Start from the biological gap, core question, central claim and claim–evidence graph.

Once the claims are defined, choose the **smallest defensible analysis chain** from the analysis-strategy library. Every analysis step must support at least one claim and must specify its biological question, independence unit, expected output, limitation and validation. Do not add CellChat, trajectory, velocity, regulons, spatial niches, deconvolution or other advanced modules only because they are available.

For biological foundation-model projects, explicitly address biological utility, baseline hierarchy, OOD evaluation, specimen-level independence and leakage.

For developmental/embryo or spatial projects, distinguish measured time/space from inferred geometry. UMAP is not developmental time; pseudotime is not lineage by itself; a spatial claim requires measured spatial information.

## Figure generation / result presentation

If the task is to render reviewed upstream results, read:

- `singlecell-spatial-figures/SKILL.md`
- `singlecell-spatial-figures/pipeline_tree/README.md`
- the relevant style-gallery documentation.

The plotting layer must not invent missing statistics, boundaries, trajectories, significance, uncertainty or biological conclusions.

## Combined task

When a task includes both research design and figures:

```text
research question
→ claim–evidence graph
→ data design
→ analysis strategy selection
→ validation design
→ reviewed result contracts
→ figure pipeline
```

Never reverse this order by selecting attractive figures first and retrofitting a scientific story afterward.
