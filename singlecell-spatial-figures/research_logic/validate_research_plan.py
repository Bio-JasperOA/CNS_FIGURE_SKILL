#!/usr/bin/env python3
"""Validate a research-first project plan against schema and evidence-logic rules."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "RESEARCH_PLAN_SCHEMA.json").read_text(encoding="utf-8"))

METHOD_WORDS = re.compile(
    r"\b(Seurat|Scanpy|CellChat|LIANA|Milo|scCODA|Harmony|UMAP|t[- ]?SNE|"
    r"scGPT|Geneformer|scFoundation|Nicheformer|transformer|VAE|GNN)\b",
    re.I,
)


def _nonempty(value) -> bool:
    return value is not None and str(value).strip() not in {"", "none", "na", "n/a"}


def validate(plan: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    validator = Draft202012Validator(SCHEMA)
    for err in sorted(validator.iter_errors(plan), key=lambda e: list(e.absolute_path)):
        path = ".".join(map(str, err.absolute_path)) or "<root>"
        errors.append(f"schema:{path}: {err.message}")

    if errors:
        return errors, warnings

    claims = plan["claims"]
    claim_ids = [c["id"] for c in claims]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("semantic: claim IDs must be unique")
    claim_set = set(claim_ids)

    question = plan["project"]["biological_question"]
    central = plan["project"]["central_claim"]
    if METHOD_WORDS.search(question):
        warnings.append("question: biological question contains a method/model name; rewrite it so the biology survives method substitution")
    if METHOD_WORDS.search(central):
        warnings.append("central_claim: central claim contains a method/model name; prefer a biological statement")

    steps = plan["analysis_chain"]
    step_ids = [s["step"] for s in steps]
    if step_ids != list(range(1, len(step_ids) + 1)):
        errors.append("analysis_chain: step numbers must be consecutive starting at 1")

    supported = set()
    for step in steps:
        for cid in step["supports_claims"]:
            if cid not in claim_set:
                errors.append(f"analysis_chain step {step['step']}: unknown claim {cid}")
            supported.add(cid)
    for cid in claim_ids:
        if cid not in supported:
            errors.append(f"claim {cid}: no analysis-chain step supports this claim")

    figure_claims = set()
    for fig in plan["figure_story"]:
        cid = fig["claim"]
        if cid not in claim_set:
            errors.append(f"figure_story {fig['figure']}: claim must reference an existing claim ID, got {cid!r}")
        figure_claims.add(cid)
    for cid in claim_ids:
        if cid not in figure_claims:
            warnings.append(f"claim {cid}: no primary figure is assigned to this claim")

    pattern = plan["project"]["study_pattern"]
    data = plan["data_design"]
    val = plan["validation_ladder"]

    if pattern in {"development_embryo", "hybrid"} and not _nonempty(data.get("time_axis")):
        warnings.append("development: no explicit time_axis; developmental claims need stage/time information")
    if pattern in {"spatial_ecology", "development_embryo", "hybrid"} and not _nonempty(data.get("space_axis")):
        warnings.append("spatial: no explicit space_axis; spatial claims require measured spatial information")
    if pattern in {"perturbation_causal", "hybrid"} and not _nonempty(data.get("perturbation_axis")):
        warnings.append("causal: no perturbation_axis is declared")

    high_level = {c["level"] for c in claims}
    if not high_level.intersection({"mechanistic", "causal", "generalization", "translational"}):
        warnings.append("evidence ladder: project ends at descriptive/comparative/predictive evidence; consider whether a stronger validation layer is needed")

    for c in claims:
        level = c["level"]
        validations = " ".join(e["validation"] for e in c["evidence"])
        if level == "causal" and not any(_nonempty(x) for x in [val.get("perturbational"), val.get("experimental")]):
            errors.append(f"claim {c['id']}: causal claim requires perturbational or experimental validation")
        if level == "mechanistic" and not (_nonempty(val.get("orthogonal")) or _nonempty(validations)):
            warnings.append(f"claim {c['id']}: mechanistic claim lacks an orthogonal validation route")
        if level == "generalization" and not _nonempty(val.get("external_or_ood")):
            errors.append(f"claim {c['id']}: generalization claim requires external_or_ood validation")

    if pattern in {"foundation_model", "hybrid"}:
        model = plan.get("model_evaluation")
        if not model:
            errors.append("foundation_model: model_evaluation block is required")
        else:
            if len(model.get("baselines", [])) < 3:
                warnings.append("foundation_model: use at least trivial/statistical, strong task-specific and contemporary representation/model baselines")
            for key in ["split_strategy", "leakage_audit", "biological_utility_test"]:
                if not _nonempty(model.get(key)):
                    errors.append(f"foundation_model: model_evaluation.{key} is required")
            if not model.get("ood_axes"):
                warnings.append("foundation_model: no OOD axis declared")
            if not model.get("ablations"):
                warnings.append("foundation_model: no ablation is declared; cannot attribute gains to the proposed information/model component")

    replicate = data["biological_replicate_unit"].lower()
    split = str(plan.get("model_evaluation", {}).get("split_strategy", "")).lower()
    if any(x in replicate for x in ["donor", "patient", "embryo", "sample", "animal"]) and "random cell" in split:
        errors.append("leakage: random cell split conflicts with the declared biological replicate unit")

    if not data.get("leakage_barriers"):
        errors.append("data_design: at least one leakage barrier is required")

    for fm in plan["failure_modes"]:
        if len(fm["diagnostic"].strip()) < 5 or len(fm["response"].strip()) < 5:
            errors.append(f"failure_modes: risk {fm['risk']!r} lacks an actionable diagnostic/response")

    return errors, warnings


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan", type=Path)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    errors, warnings = validate(plan)
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: research plan is structurally valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
