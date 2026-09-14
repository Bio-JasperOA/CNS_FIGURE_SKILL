# SOFTWARE QA ONLY

These CSVs are deterministic artificial software fixtures, not biological observations or a reproduction of any paper.
The example exercises a shared two-slope scale, out-of-range colors, missing values, spatial geometry, an annotated heatmap and measured guide placement. Warnings about information density and the lead panel are deliberately retained for review.

From the Skill directory:

```bash
python scripts/render_v3.py render examples/v3_software_qa/figure.yaml --root examples/v3_software_qa --out build/software_qa
```

A successful render is a draft. `review.json` intentionally remains pending. Do not present these panels as research results.
