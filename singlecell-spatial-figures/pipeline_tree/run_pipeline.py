#!/usr/bin/env python3
"""Canonical pipeline-first CLI for all 36 executable figure modules.

The router only dispatches reviewed upstream results to plotting runtimes. It does
not rerun biological or statistical analyses. All figures obey the no-subtitle rule.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
STYLE=HERE.parent/"style_gallery"
if str(STYLE) not in sys.path:sys.path.insert(0,str(STYLE))
import runtime as base
import runtime_tranche2 as t2
import runtime_tranche3 as t3
import runtime_tranche4 as t4
import runtime_tranche5 as t5
import runtime_final_fixes as fixes
import runtime_foundation as fmrt
from modern_palettes import palette as editorial_palette,cmap as editorial_cmap

# Pipeline rendering follows the same low-saturation editorial defaults as the style
# gallery. Explicit user maps are preserved; palette_lock/palette_policy=legacy opts out.
base.style_palette=editorial_palette
base.style_cmap=editorial_cmap

EXTRA={
 "scrna.normalization_hvg":fixes.render_normalization_hvg,
 "scrna.integration":t5.render_integration,
 "scrna.clustering":t5.render_clustering,
 "scrna.annotation":t2.render_annotation,
 "scrna.markers_de":t2.render_markers_de,
 "scrna.pathway_activity":t4.render_pathway_activity,
 "scrna.trajectory":t2.render_trajectory,
 "scrna.velocity_fate":t5.render_velocity_fate,
 "scrna.regulon_module":t4.render_regulon_module,
 "scrna.perturbation_prediction":t5.render_perturbation_prediction,
 "spatial.normalization_embedding":t5.render_spatial_normalization_embedding,
 "spatial.qc":t2.render_spatial_qc,
 "spatial.domains":t2.render_spatial_domains,
 "spatial.svg_autocorrelation":t4.render_svg_autocorrelation,
 "spatial.neighborhood_niche":t2.render_spatial_niche,
 "spatial.communication":t3.render_spatial_communication,
 "spatial.gradient_trajectory":fixes.render_spatial_gradient_trajectory,
 "spatial.multisection":t5.render_multisection,
 "spatial.histology_morphology":t5.render_histology_morphology,
 "cross_modal.reference_mapping":t3.render_reference_mapping,
 "cross_modal.marker_validation":t3.render_marker_validation,
 "cross_modal.niche_validation":t5.render_niche_validation,
 "cross_modal.communication_validation":t5.render_communication_validation,
 "development.lineage_progression":t3.render_lineage_progression,
 "development.spatial_gradient":fixes.render_development_spatial_gradient,
 "development.virtual_embryo_prediction":t4.render_virtual_embryo_prediction,
 "fm.latent_embedding":fmrt.render_latent_embedding,
 "fm.ablation_scaling":t3.render_ablation_scaling,
}
DISPATCH=dict(base.DISPATCH);DISPATCH.update(EXTRA)
IMPLEMENTED=json.loads((HERE/"IMPLEMENTED_MODULES.json").read_text(encoding="utf-8"))


def api_namespace():
    ns=vars(base).copy();ns["style_palette"]=editorial_palette;ns["style_cmap"]=editorial_cmap;return ns


def _semantic_adapters(module_id,inputs,cfg):
    adapted={k:v.copy() for k,v in inputs.items()}
    if module_id=="scrna.trajectory":
        d=adapted["main"];interval={"lineage","time","mean","lower","upper"}
        if interval<=set(d):
            finite=d[["mean","lower","upper"]].notna().all(axis=1);duplicate=d.loc[finite].duplicated(["lineage","time"]).any()
            if duplicate:
                chosen=cfg.get("trend_feature")
                if chosen is not None:
                    if "feature" not in d:raise ValueError("trend_feature was declared but trajectory table has no feature field")
                    if str(chosen) not in set(d.feature.dropna().astype(str)):raise ValueError("trend_feature is absent from trajectory input")
                    keep=d.feature.astype(str)==str(chosen);d.loc[~keep,["mean","lower","upper"]]=np.nan
                else:d.loc[:,["mean","lower","upper"]]=np.nan
        adapted["main"]=d
    return adapted


def render_module(module_id:str,inputs:dict[str,pd.DataFrame],config:dict,out:Path)->dict:
    spec=IMPLEMENTED["modules"].get(module_id)
    if spec is None:raise NotImplementedError(f"{module_id} is not a registered executable module")
    if module_id not in DISPATCH:raise RuntimeError(f"{module_id} is declared executable without a dispatcher")
    out=base._mkdir(Path(out));cfg=dict(config);cfg.pop("subtitle",None);cfg.setdefault("palette_policy","modern_editorial")
    for name,contract in spec["inputs"].items():
        if name not in inputs:raise ValueError(f"{module_id}: missing named input {name!r}")
        base._validate_contract(inputs[name],contract)
    inputs=_semantic_adapters(module_id,inputs,cfg)
    if module_id in base.DISPATCH:
        manifest=base.render_module(module_id,inputs,cfg,out);manifest["runtime_version"]=IMPLEMENTED["runtime_version"];manifest["palette_policy"]=cfg["palette_policy"]
        (out/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");return manifest
    records,skipped=EXTRA[module_id](inputs,cfg,out,api_namespace())
    manifest={"module_id":module_id,"runtime_version":IMPLEMENTED["runtime_version"],"skill_major_version":3,"subtitle_policy":"forbidden","palette_policy":cfg["palette_policy"],"inputs":{k:{"contract":spec["inputs"].get(k),"sha256":base._sha_frame(v),"rows":len(v)} for k,v in inputs.items()},"generated":records,"skipped":skipped,"vector_rule":"Standalone PDF/SVG outputs are publication candidates; contact-sheet panels are review-only raster assemblies.","scientific_boundary":"No upstream analysis, significance, interval, lineage, segmentation, niche, posterior uncertainty or latent metric is inferred by this runtime."}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");return manifest


def load_inputs(items):
    result={}
    for item in items:
        if "=" not in item:raise ValueError("--input must be NAME=path.csv")
        name,path=item.split("=",1);result[name]=pd.read_csv(path)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--module",required=True,choices=sorted(IMPLEMENTED["modules"]));p.add_argument("--input",action="append",required=True,help="NAME=path.csv; repeat for multi-input modules");p.add_argument("--config",required=True);p.add_argument("--out",required=True);a=p.parse_args();cfg=json.loads(Path(a.config).read_text(encoding="utf-8"));m=render_module(a.module,load_inputs(a.input),cfg,Path(a.out));print(json.dumps({"module":a.module,"generated":len(m["generated"]),"skipped":len(m["skipped"]),"palette_policy":m.get("palette_policy")},indent=2));return 0

if __name__=="__main__":raise SystemExit(main())
