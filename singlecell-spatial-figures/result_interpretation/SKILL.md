---
name: singlecell-spatial-result-interpretation
description: "Interpret actual single-cell, spatial, developmental, perturbation and wet-lab results; build source-linked biological explanations, adjudicate alternatives and write calibrated Results/Discussion narratives. Use after analysis diagnostics or directly on supplied results."
---

# Result Interpretation Skill · v3-compatible

## Purpose and entry

Repository task mode: `results-interpret`. This is an agent interpretation workflow, not a command that automatically discovers mechanisms. `review_results.py` checks evidence records and produces a review packet; it does not replace reading experiments or evaluating biology. Keep the existing plotting implementation, palette policy and major version unchanged.

Read this file, then the applicable sections of `ASSAY_PLAYBOOK.md`, `NARRATIVE_PLAYBOOK.md` and `LITERATURE_LOGIC.md`. Use `RESULT_BUNDLE_SCHEMA.json` only when a durable machine-readable interpretation is useful. A focused figure does not require an entire paper plan.

Position in the project:

```text
research question → data adaptation → analysis → diagnostics
→ result interpretation ↔ targeted reanalysis / discriminating validation
→ reviewed result-to-figure handoff → Results / Discussion → human review
```

Diagnostic plots may precede interpretation. Existing figures can be interpreted without rerunning the pipeline. Read available `profile.json`, `adaptive_plan.json`, result manifests and analysis logs, but do not require the optional data-adaptation module to be installed. Reuse sufficient context; do not restart project planning.

## 1. Establish what has actually been observed

Start by reading the actual supplied files, not prior assistant summaries. For every result establish:

- assay/modality and what it measures; organism, tissue, state and time window;
- observation, experimental allocation and independent biological units;
- test group, reference group, effect scale, sign, normalization and denominator;
- number of independent specimens separately from cells, fields, wells or technical repeats;
- effect and uncertainty, test, multiplicity correction, diagnostics and exclusions;
- source file, table/row or figure/panel, actual read scope and upstream processing.

Use the upstream adaptive profile to select the right reader: R/Seurat, Python/AnnData, matrix, tidy table, image or model summary are not interchangeable. Do not infer raw counts from `X`, assume image pixels are micrometres, or treat a file extension as an assay. Keep sparse data sparse and original files immutable. Do not run new statistical tests merely to complete an interpretation unless requested.

Images alone permit visual descriptions, not invented exact effects, sample sizes, p-values, replicates or statistical conclusions. Read legends and available source data. Record unread/partially read sources. An absent assay feature is not a negative measurement. A previous interpretation is not a new independent experiment.

## 2. Decode each result in five layers

For each result write, in this order:

1. **Observation:** a neutral, source-linked statement of the actual contrast, magnitude, direction, uncertainty and heterogeneity.
2. **Biological meaning:** what process or state this measurement informs, and why that process matters to the question.
3. **Explanation:** the leading candidate explanation and the particular observations it explains.
4. **Alternatives:** the strongest plausible competing explanation(s), with their distinguishing predictions.
5. **Claim boundary:** the strongest defensible sentence now, the tempting but unsupported extension, and the next discriminating test.

Do not substitute a list of enriched pathways for an explanation. Connect the specific genes, cell types, spatial compartment, temporal window, molecular readout and phenotype. Separate a programme change within a state from changes in the number of cells carrying that programme. Inspect coherence, leading-edge contributors, direction and upstream measurement limitations before naming a process.

Be decisive when the evidence warrants it. Do not weaken a well-supported finding with a generic caveat catalogue. Conversely, familiar biology or publication prestige cannot fill a missing experimental link. All mechanistic proposals remain hypotheses until the relevant experiment or design supports them.

## 3. Integrate experiments as an evidence graph, not an analysis list

Use result IDs for observations and claim IDs for provisional conclusions. A useful chain might be:

```text
reproducible phenotype / cell-state change
→ candidate cellular source and molecular programme
→ localization or temporal ordering
→ perturbation of a candidate component
→ molecular response and/or functional consequence
→ specificity, rescue, epistasis or external replication when relevant
```

Do not require this chain for every paper. Atlas, descriptive, methodological and negative-result contributions can be complete within their stated scope.

Every cross-result connection must be classified as `supports`, `contradicts`, `complements`, `not_comparable` or `unresolved`. Explain whether the results share an estimand, system, time, scale and denominator. For each connection specify whether it is same-data consistency, an orthogonal assay on the same specimens, independent-specimen evidence, or unknown. DE, GSEA, GSVA and a regulon from one expression matrix do not become four independent confirmations.

Orthogonality and independent replication are separate axes. An orthogonal assay on the same donor can strengthen measurement validity without adding donors. Literature supplies context, not replication of the user's experiment. A perturbation affecting a molecular programme does not by itself establish mediation of an organismal phenotype.

## 4. Calibrate claims by design and evidence

Keep claim **type** separate from claim **status**. Types include descriptive, comparative, predictive, mechanistic, causal, generalization and equivalence. They are not a single ladder of paper quality. Status is `supported`, `provisional`, `contradicted` or `unresolved`.

- An association or model prediction may nominate a mechanism without establishing it.
- A controlled perturbation can support an effect within the manipulated system, subject to allocation, specificity, measurement and confounding checks. Neither randomization alone nor a string saying “experimental validation” certifies a mechanism.
- Necessity, sufficiency, direct binding, mediation and pathway order require different contrasts. A single rescue experiment is not universal proof of all five.
- Generalization requires an explicitly independent holdout or external context appropriate to the claim; repeated model seeds are not independent biological cohorts.
- No detected difference is not evidence of equivalence. Use precision, justified practical margins and the actual equivalence/non-inferiority procedure when available. Do not infer post-hoc power from p-values.
- “Significant in A but not B” is not a tested A-versus-B difference; inspect an interaction or difference-of-effects contrast.
- A low q-value is not an effect size, probability of mechanism truth, or assurance of biological importance.

For all supported claims identify the exact results that carry them, important qualifications, and material contrary evidence. For unresolved claims specify exactly what remains uncertain. Never discard a contradictory result solely because it spoils the proposed story.

## 5. Reconcile negative, mixed and contradictory results

First check identity, test/reference orientation, assay scale, normalization, sampling, timepoint, exposure, composition and technical quality. Then distinguish:

- imprecision versus evidence against a practically meaningful effect;
- failed target engagement versus a successful perturbation with no downstream response;
- RNA/protein/activity disagreement versus a contradiction on the same endpoint;
- common response with subgroup heterogeneity versus opposite biological mechanisms;
- failure to reject a null versus successful equivalence testing;
- exploratory subgroup finding versus independently replicated effect.

Do not invent compensation, feedback, redundancy or dose thresholds to explain disagreement. List them as candidate explanations with predictions and tests, unless measured. Keep a contradiction ledger with competing interpretations, current resolution and the most informative next experiment.

## 6. Build an honest scientific narrative

Organize Results by questions and findings, not software order:

```text
Question → comparison that addresses it → principal observation
→ corroborating / challenging evidence → bounded conclusion → next question
```

Use a finding-led heading only after the result warrants it. Every quantitative sentence must be traceable to result IDs and files. Avoid pretending that exploratory analyses were prespecified. Logical presentation order need not match chronological laboratory order, but neither chronology nor preregistration may be invented.

In **Results**, prioritize actual observations and short local interpretations. In **Discussion**, distinguish the integrated model, literature context, novelty, limitations and testable predictions. Do not import unperformed validation into either section. Mark missing numbers rather than manufacture them. Cite actual papers for external claims, and source files for the user's results.

CNS-derived patterns are examples of disciplined argument, not a mandatory six-figure formula or a guarantee of journal acceptance. The goal is the strongest coherent story that survives the evidence, not the most dramatic story.

## 7. Choose the next analysis or experiment adaptively

Prioritize by the uncertainty each step resolves, not by how advanced the tool looks. For a leading and competing explanation, state their distinct predicted outcomes and choose a feasible test that separates them. Identify indispensable versus optional validation. Link requested reanalysis back to `analysis-plan` / `analysis-code`, with the required input, unit, control and failure condition.

Examples: composition versus within-state activation → compare state-specific effects with specimen-aware abundance; proximity versus density artifact → an anatomy-aware spatial null; failed perturbation versus pathway dispensability → target-engagement assessment; prediction versus mean-response memorization → matched simple baselines and held-out perturbations.

Do not reclassify a failed experiment as a successful negative-control experiment after seeing its result. Do not propose more omics merely to increase the number of panels.

## 8. Required deliverables

Default `interpretation_depth: full`, `response_language: zh`. Respect the user's language.

- `quick`: main finding, evidence supporting it, one decisive limitation/alternative, next step.
- `full`: result inventory, per-result interpretation, integrated evidence graph, claim ledger, contradiction/negative-result ledger, ranked validation plan and figure-to-claim map.
- `manuscript`: all full-depth outputs plus a Results draft and a separate Discussion draft; neither is marked accepted automatically.

For a durable run save `result_bundle.json`, `interpretation.md`, `claim_evidence.json`, `contradictions.md`, `next_steps.md` and `review.json` as appropriate. These are agent deliverables; the helper CLI only validates the bundle and writes a structured `review_packet.md` plus `audit.json`.

No actual results available → return an input-gap list and an interpretation template, not a biological conclusion. Synthetic examples must remain labelled synthetic in every report and never be combined silently with real evidence.

## 9. Review and handoff

Before delivery verify all main statements against source content, numerical direction and units; check all material contrary evidence, uncertain labels, literature access depth and cell/specimen independence. A validator pass establishes structural/declared-evidence consistency only. It does not establish truth, novelty, image integrity or publishability. Human review remains pending.

Use the current plotting registry for figure handoffs; do not invent renderer IDs. Preserve existing no-subtitle, aligned-legend and no-grey-explanatory-microcopy policies. Interpretive paragraphs belong in the manuscript/caption/report, not on the plotting canvas. This module never modifies plot aesthetics or raw data.
