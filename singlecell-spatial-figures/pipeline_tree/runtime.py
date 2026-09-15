#!/usr/bin/env python3
"""Pipeline-first figure runtime for implemented v3 modules.

This layer consumes canonical result tables declared in RESULT_CONTRACTS.json and
emits standalone vector figures plus review contact sheets. It never reruns the
scientific analysis and never fabricates significance, intervals, trajectories,
spatial boundaries or uncertainty.

All figures follow the repository-wide no-subtitle rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageDraw

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
STYLE = SKILL / "style_gallery"
if str(STYLE) not in sys.path:
    sys.path.insert(0, str(STYLE))

import render as style_render
from chart_core import palette as style_palette, cmap as style_cmap

IMPLEMENTED = json.loads((HERE / "IMPLEMENTED_MODULES.json").read_text(encoding="utf-8"))
CONTRACTS = json.loads((HERE / "RESULT_CONTRACTS.json").read_text(encoding="utf-8"))["contracts"]

INK = "#263641"
MUTED = "#65757F"
GRID = "#E6EBEE"


def _slug(x: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(x)).strip("_")


def _sha_frame(df: pd.DataFrame) -> str:
    return hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()


def _mkdir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_custom(fig, base: Path) -> dict:
    _mkdir(base.parent)
    outputs = {}
    for ext in ("png", "pdf", "svg"):
        path = base.with_suffix("." + ext)
        fig.savefig(path, dpi=300 if ext == "png" else None, bbox_inches="tight", facecolor="white")
        outputs[ext] = str(path)
    plt.close(fig)
    return outputs


def _render_style(target: str, kind: str, df: pd.DataFrame, cfg: dict, mode: str, out: Path,
                  post: Callable | None = None) -> dict:
    cfg = dict(cfg)
    cfg.pop("subtitle", None)
    fig = style_render.render(kind, df, cfg, mode)
    if post is not None:
        post(fig)
        fig.canvas.draw()
    base = out / target
    report = style_render.export(fig, base)
    outputs = {ext: str(base.with_suffix("." + ext)) for ext in ("png", "pdf", "svg")}
    return {"target": target, "engine": "style_gallery", "kind": kind, "mode": mode,
            "outputs": outputs, "sha256": report["outputs"],
            "semantic_layers": report["semantic_layers"]}


def _custom_figure(target: str, maker: Callable, out: Path) -> dict:
    fig = maker()
    outputs = _save_custom(fig, out / target)
    return {"target": target, "engine": "pipeline_runtime", "kind": target,
            "mode": "advanced", "outputs": outputs, "semantic_layers": [target]}


def _contact_sheet(target: str, plot_records: list[dict], out: Path, columns: int = 2) -> dict | None:
    pngs = [Path(r["outputs"]["png"]) for r in plot_records if r.get("outputs", {}).get("png")]
    if not pngs:
        return None
    ims = [Image.open(p).convert("RGB") for p in pngs]
    try:
        tile_w, tile_h, gap = 900, 660, 28
        rows = math.ceil(len(ims) / columns)
        canvas = Image.new("RGB", (columns * tile_w + (columns + 1) * gap,
                                   rows * tile_h + (rows + 1) * gap), "white")
        draw = ImageDraw.Draw(canvas)
        for i, (im, rec) in enumerate(zip(ims, plot_records)):
            scaled = ImageOps.contain(im, (tile_w - 18, tile_h - 55))
            x = gap + (i % columns) * (tile_w + gap)
            y = gap + (i // columns) * (tile_h + gap)
            canvas.paste(scaled, (x + (tile_w - scaled.width)//2, y + 35))
            draw.text((x + 8, y + 8), rec["target"], fill=INK)
        path = out / f"{target}.png"
        canvas.save(path, dpi=(200, 200))
        pdf = out / f"{target}.pdf"
        canvas.save(pdf, "PDF", resolution=200.0)
        return {"target": target, "engine": "pipeline_runtime", "kind": "review_contact_sheet",
                "mode": "advanced", "outputs": {"png": str(path), "pdf": str(pdf)},
                "semantic_layers": ["review contact sheet"],
                "note": "Raster review panel; standalone PDFs/SVGs are the vector publication outputs."}
    finally:
        for im in ims:
            im.close()


def _validate_contract(df: pd.DataFrame, contract: str) -> None:
    req = CONTRACTS[contract]["required"]
    missing = [x for x in req if x not in df.columns]
    if missing:
        raise ValueError(f"{contract}: missing canonical fields {missing}")


def _zscore(v: pd.Series) -> pd.Series:
    sd = float(v.std(ddof=0))
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.zeros(len(v)), index=v.index)
    return (v - float(v.mean())) / sd


def _base_cfg(config: dict, title: str | None = None) -> dict:
    c = dict(config.get("style", {}))
    c["demo"] = bool(config.get("demo", False))
    if not c["demo"]:
        if not config.get("provenance"):
            raise ValueError("Real-data pipeline rendering requires provenance")
        c["provenance"] = config["provenance"]
    c["font_family"] = c.get("font_family", "DejaVu Sans")
    c.pop("subtitle", None)
    if title is not None:
        c["title"] = title
    return c


def _categorical_spatial(df: pd.DataFrame, group_col: str, config: dict, title: str):
    def maker():
        fig, ax = plt.subplots(figsize=(6.8, 5.6), facecolor="white")
        levels = list(dict.fromkeys(df[group_col].astype(str)))
        pal = style_palette(levels, {"categorical_preset": config.get("categorical_preset", "C19"),
                                     "palette_order": levels})
        for g in levels:
            p = df[df[group_col].astype(str) == g]
            ax.scatter(p.x, p.y, s=config.get("point_area", 14), c=pal[g], lw=0, label=g, rasterized=True)
        ax.set_aspect("equal")
        if config.get("invert_y"):
            ax.invert_yaxis()
        ax.set_xlabel(f"x ({config.get('coordinate_unit','coordinate')})")
        ax.set_ylabel(f"y ({config.get('coordinate_unit','coordinate')})")
        ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", color=INK)
        ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        return fig
    return maker


def _rank_bar(labels, values, title, xlabel, color="#5E8795"):
    labels = list(map(str, labels))
    values = np.asarray(values, float)
    order = np.argsort(values)
    labels = [labels[i] for i in order]
    values = values[order]
    def maker():
        h = max(3.2, .28 * len(labels) + 1.3)
        fig, ax = plt.subplots(figsize=(6.8, h), facecolor="white")
        y = np.arange(len(labels))
        ax.barh(y, values, color=color, edgecolor="none")
        ax.set_yticks(y, labels)
        ax.set_xlabel(xlabel)
        ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", color=INK)
        ax.axvline(0, color=MUTED, lw=.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", color=GRID, lw=.6, zorder=0)
        return fig
    return maker


def render_scrna_qc(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "cell_qc")
    records, skipped = [], []
    samples = list(dict.fromkeys(d["sample"].astype(str)))
    base = _base_cfg(config)

    counts = pd.DataFrame({"id": d.cell_id, "group": d["sample"].astype(str), "value": d.n_counts})
    c = dict(base, title="Library size across cells", group_order=samples, value_label="RNA counts")
    records.append(_render_style("qc_violin", "distribution", counts, c, "minimal", out))

    hg = pd.DataFrame({"id": d.cell_id, "x": d.n_counts, "y": d.n_features})
    c = dict(base, title="Detected genes versus library size", x_label="RNA counts", y_label="Detected genes")
    records.append(_render_style("qc_counts_vs_genes", "hexbin", hg, c, "advanced", out))

    mito = pd.DataFrame({"id": d.cell_id, "group": d["sample"].astype(str), "value": d.pct_mito})
    c = dict(base, title="Mitochondrial fraction across cells", group_order=samples,
             value_label="Mitochondrial fraction (%)")
    records.append(_render_style("qc_mito_distribution", "distribution", mito, c, "minimal", out))

    med = d.groupby("sample", sort=False)[["n_counts", "n_features", "pct_mito"]].median()
    z = med.apply(_zscore, axis=0)
    hm = z.rename_axis("group").reset_index().melt("group", var_name="feature", value_name="value")
    c = dict(base, title="Sample-level QC summary", group_order=samples,
             feature_order=["n_counts", "n_features", "pct_mito"], value_label="Median metric z-score",
             continuous_preset="D03", limits=[-2.5, 2.5], norm="two_slope")
    records.append(_render_style("qc_sample_summary", "heatmap", hm, c, "advanced", out))

    thresholds = config.get("thresholds", {})
    mito_max = thresholds.get("pct_mito_max")
    if mito_max is not None:
        c = dict(base, title="QC density with declared threshold", group_order=samples,
                 value_label="Mitochondrial fraction (%)")
        def post(fig):
            fig.axes[0].axhline(float(mito_max), color="#A94949", ls="--", lw=1.0)
        records.append(_render_style("qc_density_thresholds", "distribution", mito, c, "advanced", out, post=post))
    else:
        skipped.append({"target": "qc_density_thresholds", "reason": "No pct_mito_max threshold supplied."})

    if "keep" in d:
        tmp = d.copy()
        tmp["condition"] = np.where(tmp["keep"].astype(bool), "Kept", "Filtered")
        both = tmp.groupby("sample").condition.nunique()
        ok = both[both == 2].index
        tmp = tmp[tmp["sample"].isin(ok)]
        if len(tmp):
            ba = pd.DataFrame({"id": tmp.cell_id, "group": tmp["sample"].astype(str),
                               "condition": tmp.condition, "value": tmp.pct_mito})
            c = dict(base, title="Filtering effect on mitochondrial fraction",
                     group_order=[str(x) for x in ok], condition_order=["Kept", "Filtered"],
                     value_label="Mitochondrial fraction (%)")
            records.append(_render_style("qc_before_after_filtering", "distribution", ba, c, "advanced", out))
        else:
            skipped.append({"target": "qc_before_after_filtering", "reason": "No sample contains both kept and filtered cells."})
    else:
        skipped.append({"target": "qc_before_after_filtering", "reason": "No keep column supplied."})

    records.append(_render_style("qc_sample_heatmap", "heatmap", hm, dict(
        base, title="QC metric heatmap by sample", group_order=samples,
        feature_order=["n_counts", "n_features", "pct_mito"], value_label="Median metric z-score",
        continuous_preset="D03", limits=[-2.5, 2.5], norm="two_slope"), "advanced", out))

    panel = _contact_sheet("qc_dashboard", records[:4], out, columns=2)
    if panel: records.append(panel)
    return records, skipped


def render_composition_da(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "composition_effect")
    records, skipped = [], []
    groups = list(dict.fromkeys(d.group.astype(str)))
    samples = list(dict.fromkeys(d["sample"].astype(str)))
    base = _base_cfg(config)

    comp = d.copy()
    comp["sample"] = comp["sample"].astype(str); comp["group"] = comp["group"].astype(str)
    c = dict(base, title="Cell composition across samples", sample_order=samples, group_order=groups,
             categorical_preset=config.get("categorical_preset", "C19"))
    records.append(_render_style("composition_stacked", "composition", comp, c, "minimal", out))
    records.append(_render_style("composition_heatmap", "composition", comp, dict(c, title="Sample-level cell composition"), "advanced", out))

    dist = pd.DataFrame({"id": comp["sample"] + "::" + comp["group"], "group": comp.group, "value": comp.fraction})
    if "condition" in comp:
        dist["condition"] = comp.condition.astype(str)
    dc = dict(base, title="Cell-type fractions across biological samples", group_order=groups,
              value_label="Within-sample fraction")
    if "condition" in dist:
        dc["condition_order"] = list(dict.fromkeys(dist.condition))
    records.append(_render_style("fraction_distribution", "distribution", dist, dc, "advanced", out))

    effect_cols = {"effect", "lower", "upper"}
    if effect_cols <= set(comp):
        eff = comp[["group", "effect", "lower", "upper"]].drop_duplicates()
        if eff.groupby("group").size().max() != 1:
            skipped.append({"target": "da_forest", "reason": "Effect/interval is not unique per group."})
        else:
            f = eff.rename(columns={"group":"term","effect":"estimate"})
            fc = dict(base, title="Differential abundance effect sizes",
                      effect_label=config.get("effect_label", "Effect estimate"),
                      interval_label=config.get("interval_label", "Supplied interval"),
                      term_order=groups)
            records.append(_render_style("da_forest", "forest", f, fc, "advanced", out))
    else:
        skipped.append({"target":"da_forest","reason":"effect/lower/upper were not supplied."})

    if {"effect", "q"} <= set(comp):
        eff = comp.groupby("group", sort=False).agg(effect=("effect","first"), q=("q","first")).reset_index()
        records.append(_custom_figure("da_lollipop",
            _rank_bar(eff.group, eff.effect, "Differential abundance ranking", config.get("effect_label","Effect estimate")),
            out))
    else:
        skipped.append({"target":"da_lollipop","reason":"effect and q were not both supplied."})

    if {"subject", "condition"} <= set(comp):
        conds = list(dict.fromkeys(comp.condition.astype(str)))
        paired_records = []
        if len(conds) == 2:
            for g in groups[:min(len(groups), int(config.get("max_paired_groups", 6)))]:
                p = comp[comp.group == g][["subject","condition","fraction"]].copy()
                if p.groupby("subject").condition.nunique().eq(2).all():
                    p = p.rename(columns={"subject":"sample","fraction":"value"})
                    pc = dict(base, title=f"Matched abundance: {g}", condition_order=conds, value_label="Within-sample fraction")
                    paired_records.append(_render_style("paired_composition__"+_slug(g), "paired", p, pc, "advanced", out))
            if paired_records:
                records.extend(paired_records)
                panel = _contact_sheet("paired_composition", paired_records, out, columns=2)
                if panel: records.append(panel)
            else:
                skipped.append({"target":"paired_composition","reason":"No complete two-condition subjects."})
        else:
            skipped.append({"target":"paired_composition","reason":"Paired view requires exactly two conditions."})
    else:
        skipped.append({"target":"paired_composition","reason":"subject/condition not supplied."})

    panel = _contact_sheet("composition_da_panel", [r for r in records if r["target"] in {"composition_stacked","composition_heatmap","fraction_distribution","da_forest","da_lollipop"}], out, columns=2)
    if panel: records.append(panel)
    skipped += [
        {"target":"neighborhood_da_map","reason":"Requires neighborhood coordinates/effects from Milo-like upstream output."},
        {"target":"composition_effect_matrix","reason":"Requires condition-specific effect estimates rather than one effect per cell type."}
    ]
    return records, skipped


def render_communication(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "interaction")
    records, skipped = [], []
    base = _base_cfg(config)
    sources = list(dict.fromkeys(d.source.astype(str))); targets = list(dict.fromkeys(d.target.astype(str)))

    h = d.groupby(["source","target"], sort=False).score.sum().reset_index()
    hm = h.rename(columns={"source":"feature","target":"group","score":"value"})
    hc = dict(base, title="Sender–receiver interaction matrix", group_order=targets, feature_order=sources,
              value_label=config.get("score_label","Interaction score"), continuous_preset=config.get("continuous_preset","M02"))
    records.append(_render_style("interaction_heatmap", "heatmap", hm, hc, "advanced", out))

    net = h.rename(columns={"score":"weight"})
    nc = dict(base, title="Candidate sender–receiver communication", edge_unit=config.get("edge_unit","interaction score"),
              categorical_preset=config.get("categorical_preset","C19"))
    records.append(_render_style("communication_network", "network", net, nc, "minimal", out))
    records.append(_render_style("communication_chord", "network", net, dict(nc, title="Mass-allocated communication chord"), "advanced", out))
    records.append(_render_style("pathway_network", "network", net, dict(nc, title="Communication topology"), "advanced", out))

    if {"ligand","receptor"} <= set(d):
        lr = d.copy()
        lr["pair"] = lr.ligand.astype(str) + "–" + lr.receptor.astype(str)
        lr["edge"] = lr.source.astype(str) + " → " + lr.target.astype(str)
        top = lr.nlargest(int(config.get("max_lr_pairs", 28)), "score")
        def bubble():
            edges = list(dict.fromkeys(top.edge)); pairs = list(dict.fromkeys(top.pair))
            fig, ax = plt.subplots(figsize=(max(7, .32*len(pairs)+3), max(4, .34*len(edges)+2)), facecolor="white")
            x = [pairs.index(v) for v in top.pair]; y = [edges.index(v) for v in top.edge]
            size = np.full(len(top), 55.0)
            size_label = "Fixed point area"
            if "q" in top and top.q.notna().all() and (top.q > 0).all():
                evid = np.clip(-np.log10(top.q.to_numpy(float)), 0, 8)
                size = 18 + 32 * evid
                size_label = "Point area ∝ -log10(q)"
            sc = ax.scatter(x, y, c=top.score, s=size, cmap=style_cmap({"continuous_preset":config.get("continuous_preset","M02")}), lw=.3, edgecolor="white")
            ax.set_xticks(range(len(pairs)), pairs, rotation=45, ha="right")
            ax.set_yticks(range(len(edges)), edges)
            ax.set_title("Ligand–receptor evidence", loc="left", fontsize=11.5, fontweight="bold", color=INK)
            ax.text(1, -.22, size_label, transform=ax.transAxes, ha="right", fontsize=7, color=MUTED)
            fig.colorbar(sc, ax=ax, label=config.get("score_label","Interaction score"), fraction=.04, pad=.03)
            ax.spines[["top","right"]].set_visible(False)
            return fig
        records.append(_custom_figure("lr_bubble", bubble, out))
        records.append(_custom_figure("lr_evidence_bubble", bubble, out))
    else:
        skipped += [{"target":"lr_bubble","reason":"ligand/receptor columns not supplied."},
                    {"target":"lr_evidence_bubble","reason":"ligand/receptor columns not supplied."}]

    if "pathway" in d:
        p = d.groupby("pathway", sort=False).score.sum().sort_values(ascending=False)
        records.append(_custom_figure("pathway_ranking",
            _rank_bar(p.index[:20], p.values[:20], "Communication pathway ranking", config.get("score_label","Summed interaction score")),
            out))
    else:
        skipped.append({"target":"pathway_ranking","reason":"pathway column not supplied."})

    panel = _contact_sheet("sender_receiver_panel", [r for r in records if r["target"] in {"interaction_heatmap","communication_network","communication_chord","lr_bubble","pathway_ranking"}], out, columns=2)
    if panel: records.append(panel)

    if "target_program" in d:
        t = d.groupby("target_program", sort=False).score.sum().sort_values(ascending=False)
        prog = _custom_figure("communication_target_program",
            _rank_bar(t.index[:20], t.values[:20], "Downstream target-program support", config.get("score_label","Summed interaction score")),
            out)
        records.append(prog)
        panel2 = _contact_sheet("communication_target_program_panel", [records[0], records[2], prog], out, columns=2)
        if panel2: records.append(panel2)
    else:
        skipped.append({"target":"communication_target_program_panel","reason":"target_program column not supplied."})
    return records, skipped


def render_spatial_expression(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "spatial_point")
    if "value" not in d:
        raise ValueError("spatial.expression requires canonical optional field 'value'")
    records, skipped = [], []
    base = _base_cfg(config)
    sections = list(dict.fromkeys(d.section.astype(str)))
    genes = list(dict.fromkeys(d.gene.astype(str))) if "gene" in d else ["feature"]
    standalone = []

    for section in sections:
        for gene in genes[:int(config.get("max_genes", 6))]:
            p = d[d.section.astype(str) == section].copy()
            if "gene" in p:
                p = p[p.gene.astype(str) == gene]
            sd = p[["id","x","y","value","section"]].copy()
            if "vertices" in p: sd["vertices"] = p["vertices"]
            c = dict(base, title=f"{gene} · {section}" if "gene" in d else f"Spatial feature · {section}",
                     coordinate_unit=config.get("coordinate_unit","µm"),
                     value_label=config.get("value_label","Expression / score"),
                     continuous_preset=config.get("continuous_preset","M02"),
                     invert_y=bool(config.get("invert_y", False)))
            if config.get("scale_bar") is not None: c["scale_bar"] = config["scale_bar"]
            if config.get("rois"): c["rois"] = config["rois"]
            name = f"spatial_feature__{_slug(section)}__{_slug(gene)}"
            rec = _render_style(name, "spatial", sd, c, "advanced", out)
            records.append(rec); standalone.append(rec)

    if standalone:
        first = standalone[0]
        records.append({"target":"spatial_feature","engine":"alias","kind":"spatial","mode":"advanced",
                        "outputs":first["outputs"],"semantic_layers":first["semantic_layers"]})
    if len(sections) > 1:
        panel = _contact_sheet("spatial_multisection_feature", standalone[:min(8,len(standalone))], out, columns=min(3,len(sections)))
        if panel: records.append(panel)
    else:
        skipped.append({"target":"spatial_multisection_feature","reason":"Only one section supplied."})
    if len(genes) > 1:
        panel = _contact_sheet("spatial_multigene_panel", standalone[:min(8,len(standalone))], out, columns=2)
        if panel: records.append(panel)
    else:
        skipped.append({"target":"spatial_multigene_panel","reason":"Only one gene/feature supplied."})

    p0 = d[d.section.astype(str)==sections[0]].copy()
    if "gene" in p0: p0 = p0[p0.gene.astype(str)==genes[0]]
    if len(p0) >= 20 and np.isfinite(p0.value).sum() >= 20:
        def contour():
            fig, ax = plt.subplots(figsize=(6.8,5.6), facecolor="white")
            sc = ax.scatter(p0.x,p0.y,c=p0.value,s=config.get("point_area",12),cmap=style_cmap({"continuous_preset":config.get("continuous_preset","M02")}),lw=0)
            try:
                ax.tricontour(p0.x,p0.y,p0.value,levels=6,colors=INK,linewidths=.5,alpha=.65)
            except Exception:
                pass
            ax.set_aspect("equal")
            if config.get("invert_y"): ax.invert_yaxis()
            ax.set_title("Spatial field with scalar contours",loc="left",fontsize=11.5,fontweight="bold",color=INK)
            ax.set_xlabel(f"x ({config.get('coordinate_unit','µm')})"); ax.set_ylabel(f"y ({config.get('coordinate_unit','µm')})")
            fig.colorbar(sc,ax=ax,label=config.get("value_label","Expression / score"))
            ax.spines[["top","right"]].set_visible(False)
            return fig
        records.append(_custom_figure("spatial_contour_hotspot", contour, out))
    else:
        skipped.append({"target":"spatial_contour_hotspot","reason":"Too few finite points for a stable contour display."})

    if "vertices" in d:
        records.append({"target":"segmentation_overlay","engine":"alias","kind":"spatial","mode":"advanced",
                        "outputs":standalone[0]["outputs"],"semantic_layers":standalone[0]["semantic_layers"]})
    else:
        skipped.append({"target":"segmentation_overlay","reason":"No supplied segmentation vertices."})

    if config.get("rois"):
        skipped.append({"target":"region_zoom","reason":"ROI overlay is rendered, but dedicated zoom panels are not yet implemented in runtime v1."})
    else:
        skipped.append({"target":"region_zoom","reason":"No ROI supplied."})
    skipped.append({"target":"feature_image_composite","reason":"Requires an explicit histology/image asset; runtime v1 never invents a background image."})
    return records, skipped


def render_spatial_mapping(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "spatial_composition")
    records, skipped = [], []
    base = _base_cfg(config)
    groups = list(dict.fromkeys(d.group.astype(str)))
    sections = list(dict.fromkeys(d.section.astype(str)))
    if len(sections) != 1:
        raise ValueError("runtime v1 spatial mapping expects one section per invocation")
    c = dict(base, title="Spatial cell-type composition", coordinate_unit=config.get("coordinate_unit","µm"),
             categorical_preset=config.get("categorical_preset","C19"),
             group_order=groups, invert_y=bool(config.get("invert_y",False)))
    records.append(_render_style("spatial_composition", "spatial_composition", d, c, "minimal", out))
    records.append(_render_style("spatial_pie", "spatial_composition", d, dict(c,title="Local cell-type mixtures"), "advanced", out))

    wide = d.pivot(index=["id","section","x","y"], columns="group", values="fraction")
    dom = wide.idxmax(axis=1).rename("dominant").reset_index()
    records.append(_custom_figure("mapped_celltype",
        _categorical_spatial(dom, "dominant", dict(config, coordinate_unit=config.get("coordinate_unit","µm")), "Dominant mapped cell type"),
        out))

    maxp = wide.max(axis=1).rename("value").reset_index()
    mc = dict(base, title="Maximum mapping probability", coordinate_unit=config.get("coordinate_unit","µm"),
              value_label="Maximum cell-type fraction", continuous_preset=config.get("continuous_preset","M02"),
              limits=[0,1], norm="linear", invert_y=bool(config.get("invert_y",False)))
    records.append(_render_style("mapping_probability", "spatial", maxp, mc, "advanced", out))

    if "confidence" in d:
        conf = d.groupby(["id","section","x","y"],sort=False).confidence.first().rename("value").reset_index()
        records.append(_render_style("mapping_confidence","spatial",conf,dict(mc,title="Mapping confidence",value_label="Confidence"),"advanced",out))
    else:
        skipped.append({"target":"mapping_confidence","reason":"No confidence field supplied."})

    k = int(config.get("top_k", min(6,len(groups))))
    means = d.groupby("group").fraction.mean().sort_values(ascending=False)
    top = list(means.index[:k])
    td = d[d.group.isin(top)].copy()
    missing = 1 - td.groupby("id").fraction.sum()
    if (missing > 1e-9).any():
        geom = d.drop_duplicates("id").set_index("id")[["section","x","y"]]
        other = pd.DataFrame({"id":missing.index,"fraction":missing.values,"group":"Other"}).join(geom,on="id")
        td = pd.concat([td,other],ignore_index=True,sort=False)
    top_groups = top + (["Other"] if "Other" in set(td.group) else [])
    tc = dict(c, title=f"Top-{k} composition plus Other", group_order=top_groups)
    records.append(_render_style("topk_composition_map","spatial_composition",td,tc,"advanced",out))

    atlas = []
    for g in top:
        p = d[d.group==g][["id","section","x","y","fraction"]].rename(columns={"fraction":"value"})
        rec = _render_style("abundance__"+_slug(g),"spatial",p,dict(mc,title=f"{g} abundance",value_label="Local fraction"),"advanced",out)
        atlas.append(rec);records.append(rec)
    panel = _contact_sheet("celltype_abundance_atlas", atlas, out, columns=2)
    if panel: records.append(panel)
    panel2 = _contact_sheet("mapping_confidence_panel", [r for r in records if r["target"] in {"mapped_celltype","mapping_probability","mapping_confidence","spatial_pie"}], out, columns=2)
    if panel2: records.append(panel2)
    skipped.append({"target":"region_composition_heatmap","reason":"No region/domain label exists in the spatial_composition contract."})
    return records, skipped


def render_prediction(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "prediction")
    records, skipped = [], []
    base = _base_cfg(config)
    residual = d["residual"] if "residual" in d else d["observed"] - d["predicted"]

    hp = pd.DataFrame({"id":d.id,"x":d.observed,"y":d.predicted})
    hc = dict(base, title="Observed versus predicted", x_label="Observed", y_label="Predicted")
    records.append(_render_style("observed_predicted","hexbin",hp,hc,"advanced",out))

    grp = d["group"].astype(str) if "group" in d else pd.Series(["All"]*len(d))
    rd = pd.DataFrame({"id":d.id,"group":grp,"value":residual})
    rc = dict(base,title="Prediction residual distribution",group_order=list(dict.fromkeys(grp)),value_label=config.get("residual_label","Observed − predicted"))
    records.append(_render_style("prediction_residual","distribution",rd,rc,"advanced",out))

    if {"group","feature"} <= set(d):
        err = d.assign(_abs=np.abs(residual)).groupby(["group","feature"],sort=False)._abs.mean().rename("value").reset_index()
        hc2 = dict(base,title="Mean absolute prediction error",group_order=list(dict.fromkeys(err.group.astype(str))),
                   feature_order=list(dict.fromkeys(err.feature.astype(str))),value_label="Mean absolute error",
                   continuous_preset=config.get("continuous_preset","M02"))
        records.append(_render_style("prediction_error_heatmap","heatmap",err,hc2,"advanced",out))
    else:
        skipped.append({"target":"prediction_error_heatmap","reason":"group and feature fields are needed for a meaningful error matrix."})

    if config.get("prediction_type") == "probability":
        if ((d.observed<0)|(d.observed>1)|(d.predicted<0)|(d.predicted>1)).any():
            raise ValueError("Probability calibration requires observed/predicted in [0,1]")
        bins = pd.qcut(d.predicted, q=min(10,max(2,len(d)//20)), duplicates="drop")
        cal = d.assign(_bin=bins).groupby("_bin", observed=True).agg(predicted=("predicted","mean"),observed=("observed","mean"),n=("id","size")).reset_index()
        cal["model"] = config.get("model_name","Model"); cal["bin"] = np.arange(len(cal))
        cc = dict(base,title="Prediction calibration",model_order=[config.get("model_name","Model")])
        records.append(_render_style("prediction_calibration","calibration",cal[["model","bin","predicted","observed","n"]],cc,"advanced",out))
    else:
        skipped.append({"target":"prediction_calibration","reason":"Set prediction_type='probability' for probability calibration."})

    if "uncertainty" in d and {"section","x","y"} <= set(d):
        p = d[["id","section","x","y","uncertainty"]].rename(columns={"uncertainty":"value"})
        uc = dict(base,title="Prediction uncertainty",coordinate_unit=config.get("coordinate_unit","µm"),
                  value_label=config.get("uncertainty_label","Uncertainty"),continuous_preset=config.get("continuous_preset","M02"))
        records.append(_render_style("prediction_uncertainty","spatial",p,uc,"advanced",out))

    panel = _contact_sheet("truth_prediction_error_uncertainty_panel", records[:4], out, columns=2)
    if panel: records.append(panel)
    return records, skipped


def render_benchmark(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d = inputs["main"].copy()
    _validate_contract(d, "model_metric")
    metric = config.get("metric", str(d.metric.iloc[0]))
    p = d[d.metric.astype(str)==str(metric)].copy()
    if p.empty: raise ValueError(f"No rows for metric={metric}")
    agg = p.groupby(["dataset","method"],sort=False).value.mean().rename("score").reset_index()
    datasets = list(dict.fromkeys(agg.dataset.astype(str))); methods=list(dict.fromkeys(agg.method.astype(str)))
    base=_base_cfg(config)
    bc=dict(base,title=f"Benchmark: {metric}",dataset_order=datasets,method_order=methods,value_label=str(metric),
            baseline_method=config.get("baseline_method",methods[0]))
    records=[_render_style("benchmark_scores","benchmark",agg,bc,"minimal",out),
             _render_style("paired_benchmark","benchmark",agg,dict(bc,title=f"Paired benchmark differences: {metric}"),"advanced",out)]
    skipped=[]

    wide=agg.pivot(index="dataset",columns="method",values="score").reindex(index=datasets,columns=methods)
    wins=np.zeros((len(methods),len(methods)))
    for i,a in enumerate(methods):
        for j,b in enumerate(methods):
            wins[i,j]=float((wide[a]>wide[b]).mean()) if i!=j else .5
    wh=pd.DataFrame(wins,index=methods,columns=methods).rename_axis("feature").reset_index().melt("feature",var_name="group",value_name="value")
    hc=dict(base,title="Pairwise method win rate",group_order=methods,feature_order=methods,value_label="Win rate",
            continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
    records.append(_render_style("winrate_heatmap","heatmap",wh,hc,"advanced",out))

    ranks=wide.rank(axis=1,ascending=False,method="average").mean(axis=0).sort_values(ascending=False)
    records.append(_custom_figure("method_rank",_rank_bar(ranks.index,ranks.values,"Mean method rank across datasets","Mean rank (lower is better)"),out))
    panel=_contact_sheet("benchmark_evidence_panel",records, out, columns=2)
    if panel:records.append(panel)
    return records,skipped


def render_stage_composition(inputs: dict[str, pd.DataFrame], config: dict, out: Path):
    d=inputs["main"].copy()
    _validate_contract(d,"composition_effect")
    if "condition" not in d: raise ValueError("development.stage_composition requires condition as developmental stage")
    stages=config.get("stage_order",list(dict.fromkeys(d.condition.astype(str))))
    groups=list(dict.fromkeys(d.group.astype(str)));samples=list(dict.fromkeys(d["sample"].astype(str)))
    base=_base_cfg(config);records=[];skipped=[]

    agg=d.groupby(["condition","group"],sort=False).fraction.mean().rename("value").reset_index()
    hm=agg.rename(columns={"condition":"group","group":"feature"})
    hc=dict(base,title="Cell-type abundance across developmental stages",group_order=stages,feature_order=groups,
            value_label="Mean within-sample fraction",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
    records.append(_render_style("stage_celltype_heatmap","heatmap",hm,hc,"advanced",out))

    comp=d.copy();comp["sample"]=comp["sample"].astype(str);comp["group"]=comp.group.astype(str)
    cc=dict(base,title="Developmental composition by sample",sample_order=samples,group_order=groups,
            categorical_preset=config.get("categorical_preset","C19"))
    records.append(_render_style("stage_composition","composition",comp,cc,"minimal",out))

    stage_index={str(s):i for i,s in enumerate(stages)}
    def trend():
        fig,ax=plt.subplots(figsize=(7.6,5.4),facecolor="white")
        pal=style_palette(groups,{"categorical_preset":config.get("categorical_preset","C19"),"palette_order":groups})
        for g in groups:
            gg=d[d.group.astype(str)==g].copy()
            gg["_stage"]=gg.condition.astype(str).map(stage_index)
            for sample,ss in gg.groupby("sample",sort=False):
                ax.plot(ss._stage,ss.fraction,color=pal[g],alpha=.12,lw=.7)
            sm=gg.groupby("_stage").fraction.agg(["mean","count","std"]).reindex(range(len(stages)))
            ax.plot(range(len(stages)),sm["mean"],marker="o",ms=4,lw=1.8,color=pal[g],label=g)
        ax.set_xticks(range(len(stages)),stages,rotation=0)
        ax.set_ylabel("Within-sample fraction")
        ax.set_xlabel("Developmental stage")
        ax.set_title("Cell-type abundance trajectories",loc="left",fontsize=11.5,fontweight="bold",color=INK)
        ax.legend(frameon=False,bbox_to_anchor=(1.02,1),loc="upper left",fontsize=7)
        ax.spines[["top","right"]].set_visible(False);ax.grid(axis="y",color=GRID,lw=.6)
        return fig
    records.append(_custom_figure("abundance_trends",trend,out))
    panel=_contact_sheet("developmental_atlas_panel",records,out,columns=2)
    if panel:records.append(panel)
    return records,skipped


DISPATCH = {
    "scrna.qc": render_scrna_qc,
    "scrna.composition_da": render_composition_da,
    "scrna.communication": render_communication,
    "spatial.expression": render_spatial_expression,
    "spatial.mapping_deconvolution": render_spatial_mapping,
    "fm.reconstruction_prediction": render_prediction,
    "fm.benchmark": render_benchmark,
    "development.stage_composition": render_stage_composition,
}


def render_module(module_id: str, inputs: dict[str, pd.DataFrame], config: dict, out: Path) -> dict:
    spec = IMPLEMENTED["modules"].get(module_id)
    if spec is None:
        raise NotImplementedError(f"{module_id} is registered in the roadmap but has no runtime-v1 implementation")
    if module_id not in DISPATCH:
        raise RuntimeError(f"IMPLEMENTED_MODULES declares {module_id} without a dispatcher")
    if config.get("subtitle"):
        config = dict(config); config.pop("subtitle", None)
    out = _mkdir(Path(out))
    for name, contract in spec["inputs"].items():
        if name not in inputs:
            if name in spec.get("optional_inputs", []):
                continue
            raise ValueError(f"{module_id}: missing named input '{name}'")
        _validate_contract(inputs[name], contract)
    records, skipped = DISPATCH[module_id](inputs, config, out)
    manifest = {
        "module_id": module_id,
        "runtime_version": "1.0.0",
        "skill_major_version": 3,
        "subtitle_policy": "forbidden",
        "inputs": {k: {"contract": spec["inputs"].get(k), "sha256": _sha_frame(v), "rows": len(v)}
                   for k,v in inputs.items()},
        "generated": records,
        "skipped": skipped,
        "vector_rule": "Standalone PDF/SVG outputs are publication candidates; contact-sheet panels are review-only raster assemblies.",
        "scientific_boundary": "No upstream analysis, significance, interval, trajectory, segmentation or uncertainty is inferred by this runtime."
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return manifest


def _load_named_inputs(items: list[str]) -> dict[str,pd.DataFrame]:
    result={}
    for item in items:
        if "=" not in item: raise ValueError("--input must be NAME=path.csv")
        name,path=item.split("=",1)
        result[name]=pd.read_csv(path)
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--module",required=True,choices=sorted(IMPLEMENTED["modules"]))
    p.add_argument("--input",action="append",required=True,help="NAME=path.csv; repeat for multi-input modules")
    p.add_argument("--config",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    cfg=json.loads(Path(a.config).read_text(encoding="utf-8"))
    manifest=render_module(a.module,_load_named_inputs(a.input),cfg,Path(a.out))
    print(json.dumps({"module":a.module,"generated":len(manifest["generated"]),"skipped":len(manifest["skipped"])},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
