# Result interpretation

Use `task_mode: results-interpret` to interpret actual single-cell, spatial, developmental, computational and wet-lab results. Start with [SKILL.md](SKILL.md), then select relevant [assay guidance](ASSAY_PLAYBOOK.md) and [narrative patterns](NARRATIVE_PLAYBOOK.md).

The agent reads results, constructs biological explanations, tests them against alternatives, and writes source-linked interpretations. The helper program only checks a declared evidence bundle and builds a review packet. It does not read arbitrary experiments, discover mechanisms, or approve manuscript conclusions automatically.

## Invocation

```text
task_mode: results-interpret
interpretation_depth: full
response_language: zh
execution: plan_only
inputs:
  question: project/research_question.md
  results: project/results/
  sample_metadata: project/samples.csv
  analysis_log: project/logs/
output_dir: project/interpretation
```

Replace project paths with actual files. `plan_only` here means read-only interpretation/reporting, not refusal to produce an interpretation. New computation belongs to an explicitly requested analysis route. `quick`, `full` and `manuscript` control interpretation depth; they do not change evidence standards.

The module works directly on available results; existing data-adaptation profiles and manifests are reused when available. It does not require the optional data-adaptation package or a new complete research plan. Existing plotting styles and raw data stay unchanged.

## Structured evidence check

Install the helper dependency with `python -m pip install 'jsonschema>=4.18,<5'`.

From the repository root:

```bash
python singlecell-spatial-figures/result_interpretation/review_results.py packet \
  singlecell-spatial-figures/result_interpretation/examples/synthetic_multimodal.json \
  --root singlecell-spatial-figures/result_interpretation/examples \
  --verify-files --out build/interpretation_demo

python -m unittest discover \
  -s singlecell-spatial-figures/result_interpretation/tests -v
```

The example is entirely synthetic. For a real project, record actual source IDs, project-root-relative file paths, read scope, effect scale, contrast, biological/inferential units, diagnostics, claim roles and contradictory evidence in `RESULT_BUNDLE_SCHEMA.json` format. File hashes detect stale inputs; explicit CSV/TSV numeric bindings verify that stated summary statistics match a uniquely selected source row. Other formats require a reviewed table export; this helper does not silently parse or convert them.

`validate` prints the audit, while `packet` additionally writes `audit.json` and `review_packet.md`. Existing output files are not overwritten unless `--overwrite` is supplied. Input evidence is protected even with that flag. A failed bundle does not produce a new endorsed-looking narrative packet. Use a new output directory per revision; an older packet is not evidence of a newer run's success.

## What gets checked, and what does not

Implemented checks include references, metadata consistency, effect/null/interval scale, duplicate keys, declared nesting, claimed independent evidence, heldout specimen overlap, unsupported causal/equivalence escalation, unaccounted results, obvious selective exclusions, source hashes and bound numeric values.

Unimplemented scientific judgments include automatic image quantification/integrity checks, arbitrary-format ingestion, proof of causal identification, verification of every sentence's meaning, literature novelty and a universal CNS-readiness score. A passing JSON record is not a proof that its declarations are true. Human review stays pending.

## Files

`SKILL.md` defines agent behavior; `ASSAY_PLAYBOOK.md` and `ASSAY_RULES.json` cover 20 interpretation families; `NARRATIVE_PLAYBOOK.md` covers six narrative patterns; `LITERATURE_LOGIC.md` and `SOURCES.json` document ten targeted references and actual read scope. The schema, executable checker, two synthetic worked examples and regression tests provide the software contract.

The referenced literature set includes primary Nature, Cell, Science and portfolio papers, two review navigation entries, and a statistical commentary. It is not an exhaustive or newest-paper survey. No paper PDFs, original figures, model weights or font files are distributed.
