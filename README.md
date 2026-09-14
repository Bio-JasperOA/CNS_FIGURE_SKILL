# CNS Figure Skill · v3

**Render reviewed single-cell/spatial results, make visual decisions explicit, and audit the final artifact.** This is not an automated scientific-analysis or “CNS-approved design” system.

Start with [`singlecell-spatial-figures/SKILL.md`](singlecell-spatial-figures/SKILL.md). Preserve that complete directory.

## What changed

The v3 pipeline adds six explicit scalar mappings, measured labels and independent guides, lightness/contrast/CVD screening, text and PDF geometry checks, actual final-PDF placement verification, artifact-bound human review, repair escalation, and dependency-aware re-review. Unsupported renderer names fail preflight instead of being advertised as working features.

Python has four connected v3 renderers: embedding, spatial scalar map, marker dotplot, and annotated heatmap. The R bridge consumes the same compiled geometry and colors but **has not been executed in the authoring environment**. Shared post-export PDF checks do not prove Python/R pixel parity. Legacy v1/v2 numerical helpers and tests are retained separately.

## Read only what is needed

- [Skill entry](singlecell-spatial-figures/SKILL.md): decisions, commands and stop conditions.
- [Capability registry](singlecell-spatial-figures/CAPABILITIES.json): current implementation/test/manual boundaries, including all 17 reported issues.
- [Operational playbook](singlecell-spatial-figures/references/v3_playbook.md): visual hierarchy, density, guide design, concrete failure criteria and version migration.
- [Current QA record](singlecell-spatial-figures/QA_REPORT.md): actual tests and limitations, not historical claims.
- [Run a clearly artificial example](singlecell-spatial-figures/examples/v3_software_qa/README.md).

```bash
cd singlecell-spatial-figures
# Use an isolated environment; review pins before changing an existing research project.
python -m pip install -r requirements-v3.txt
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml   --root examples/v3_software_qa --out build/software_qa
python -m pytest -q
```

A successful render produces **a draft**, not an approved scientific figure. Complete `review.json` against the actual output; a later input/config/code/export change makes that review stale. Use `render_v3.py --help` and the playbook for final placement and native-R audits.

No fonts, user experiments, paper PDFs or author model weights are distributed. The paper/code audit is inherited; v3 does not claim additional paper reproduction. Journal dimensions and contrast thresholds are project defaults, not universal publication rules. No new license is assigned by this update.
