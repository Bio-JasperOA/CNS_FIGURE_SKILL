# Research Logic Layer

This directory upgrades the Skill from a plotting-only assistant to a **research-design assistant** for single-cell, spatial, developmental/embryo and biological foundation-model studies.

The core idea is simple: **do not start from methods or figures; start from the biological gap, build a claim–evidence graph, and only then choose analyses and figures.**

## Files

- `SKILL.md` — operational rules for Codex/agents.
- `CNS_ANCHORS.md` — compact Cell / Nature / Science anchor reading set.
- `PAPER_LOGIC_LIBRARY.md` — paper-by-paper research logic distilled from representative top-tier studies and reviews.
- `ANALYSIS_STRATEGY_LIBRARY.md` — common scRNA-seq and spatial transcriptomics analysis routes, with question, inference unit, outputs, limitations and validation logic.
- `ANALYSIS_STRATEGY_CATALOG.json` — machine-readable analysis-family catalog for Codex routing.
- `RESEARCH_PLAN_SCHEMA.json` — machine-readable research-plan contract.
- `templates/research_plan.example.json` — example project specification.
- `validate_research_plan.py` — structural and semantic validator for research plans.

## Research-first flow

```text
Biological gap
    ↓
One answerable biological question
    ↓
Central claim
    ↓
3–5 subclaims
    ↓
Claim-specific evidence
    ↓
Analysis strategy selection
    ↓
Diagnostics + validation
    ↓
Failure modes and alternative explanations
    ↓
Figure story
```

The analysis layer is **question-driven**. QC, integration, annotation, differential abundance, DE, pathway/regulon analysis, trajectory, velocity, communication, deconvolution, spatial domains, SVGs, niches, gradients, multi-section integration and histology integration are not a mandatory checklist. They are selected only when they provide evidence for a claim.

The plotting pipeline remains downstream. A figure is generated only after the result is linked to a claim and the claim is linked to a biological question.

## Quick use

Validate a durable research plan:

```bash
python research_logic/validate_research_plan.py \
  research_logic/templates/research_plan.example.json
```

For a new project, copy the example JSON and replace the example content with the real biological question, data, claims, validation strategy and figure story.

When deciding what analysis to add, inspect:

```text
ANALYSIS_STRATEGY_LIBRARY.md
ANALYSIS_STRATEGY_CATALOG.json
```

and ask whether the analysis adds evidence beyond a simpler alternative.

## Scope

Designed for:

- single-cell atlases and cohort studies;
- spatial transcriptomics and tissue ecology;
- developmental and embryo biology;
- cross-modal reference mapping;
- perturbation biology;
- biological foundation models and virtual cell / virtual embryo studies.

Not intended to certify that a project is publishable in any journal. It enforces research logic and evidence structure; scientific judgment remains human.
