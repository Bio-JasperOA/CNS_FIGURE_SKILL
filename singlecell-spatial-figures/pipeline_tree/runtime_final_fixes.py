"""Compatibility fixes for fully executable pipeline runtime v2.

These wrappers preserve all scientific semantics while adapting multi-section spatial
results to the style-gallery one-section hard contract and replacing an overflowing
UpSet layout with an explicit feature-by-batch membership matrix.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import runtime_tranche4 as t4
import runtime_tranche5 as t5

INK="#263641";MUTED="#65757F";GRID="#E6EBEE"


def render_normalization_hvg(inputs,config,out,api):
    f=inputs["features"].copy();dist=inputs["distribution"].copy();api["_validate_contract"](f,"feature_variability");api["_validate_contract"](dist,"sample_value")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(dist.group.astype(str)))
    dd=dist[["id","group","value"]+(["condition"] if "condition" in dist else [])].copy();dc=dict(base,title="Normalized expression distribution",group_order=groups,value_label=config.get("value_label","Normalized value"))
    records.append(api["_render_style"]("normalized_distribution","distribution",dd,dc,"minimal",out))
    def mv():
        fig,ax=plt.subplots(figsize=(5.8,5.0),facecolor="white");sel=f.selected.astype(bool)
        ax.scatter(f.loc[~sel,"mean"],f.loc[~sel,"variance"],s=10,c="#C8D1D5",lw=0,alpha=.65,label="Not selected");ax.scatter(f.loc[sel,"mean"],f.loc[sel,"variance"],s=13,c="#4D8598",lw=0,alpha=.85,label="Selected")
        ax.set_xlabel("Mean");ax.set_ylabel("Variance");ax.set_title("Feature variability selection",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.legend(frameon=False);t5._clean_axes(ax);return fig
    records.append(api["_custom_figure"]("hvg_mean_variance",mv,out));rank=f.copy()
    if "rank" not in rank:rank["rank"]=rank["variance"].rank(method="first",ascending=False)
    rr=rank.sort_values("rank").head(int(config.get("top_hvg",30)));records.append(api["_custom_figure"]("hvg_rank",api["_rank_bar"](rr.feature,-rr["rank"],"Highly variable feature ranking","Higher rank → right"),out))
    if "condition" in dist:
        tmp=dist[["id","condition","value"]].rename(columns={"condition":"group"});cc=dict(base,title="Normalization before/after comparison",group_order=list(dict.fromkeys(tmp.group.astype(str))),value_label=config.get("value_label","Normalized value"));records.append(api["_render_style"]("normalization_before_after","distribution",tmp,cc,"advanced",out))
    else:skipped.append({"target":"normalization_before_after","reason":"distribution.condition (e.g. before/after) not supplied."})
    def annotated_rank():
        fig,ax=plt.subplots(figsize=(7.0,4.8),facecolor="white");p=rank.sort_values("rank").head(int(config.get("annotate_hvg",25))).copy();x=np.arange(len(p));ax.bar(x,p.variance,color=["#4D8598" if bool(v) else "#C8D1D5" for v in p.selected]);ax.set_xticks(x,p.feature.astype(str),rotation=55,ha="right",fontsize=7);ax.set_ylabel("Variance");ax.set_title("Top variable features",loc="left",fontsize=11.5,fontweight="bold",color=INK);t5._clean_axes(ax);return fig
    records.append(api["_custom_figure"]("hvg_rank_annotated",annotated_rank,out))
    if "batch" in f:
        u=f[f.selected.astype(bool)][["feature","batch"]].drop_duplicates()
        if len(u):
            batches=list(dict.fromkeys(u.batch.astype(str)));features=list(dict.fromkeys(u.feature.astype(str)))
            max_features=int(config.get("overlap_max_features",60));features=features[:max_features]
            mat=pd.crosstab(u.feature.astype(str),u.batch.astype(str)).reindex(index=features,columns=batches,fill_value=0).clip(upper=1)
            def membership():
                h=max(3.5,.22*len(features)+1.6);w=max(4.8,.65*len(batches)+3.2);fig,ax=plt.subplots(figsize=(w,h),facecolor="white")
                ax.imshow(mat.to_numpy(),aspect="auto",interpolation="nearest",cmap=plt.matplotlib.colors.ListedColormap(["#F0F3F4","#4D8598"]),vmin=0,vmax=1)
                ax.set_xticks(np.arange(len(batches)),batches);ax.set_yticks(np.arange(len(features)),features,fontsize=6.7);ax.set_xlabel("Batch");ax.set_ylabel("Selected feature");ax.set_title("Selected-feature membership across batches",loc="left",fontsize=11.5,fontweight="bold",color=INK)
                for x in np.arange(len(batches)+1)-.5:ax.axvline(x,c="white",lw=.7)
                for y in np.arange(len(features)+1)-.5:ax.axhline(y,c="white",lw=.45)
                return fig
            records.append(api["_custom_figure"]("hvg_overlap_by_batch",membership,out))
        else:skipped.append({"target":"hvg_overlap_by_batch","reason":"No selected features in batch-resolved input."})
    else:skipped.append({"target":"hvg_overlap_by_batch","reason":"feature_variability.batch not supplied."})
    return records,skipped


def _scalar_sections(sp,field,title,label,config,out,target,api,signed=False):
    p=sp[["id","section","x","y",field]].rename(columns={field:"value"}).dropna(subset=["value"])
    if p.empty:return [],None
    sections=list(dict.fromkeys(p.section.astype(str)));records=[]
    if len(sections)==1:
        c=dict(api["_base_cfg"](config),title=title,coordinate_unit=config.get("coordinate_unit","µm"),value_label=label,continuous_preset=config.get("signed_preset","D03") if signed else config.get("continuous_preset","M02"),invert_y=bool(config.get("invert_y",False)))
        if signed:
            mx=max(abs(float(p.value.min())),abs(float(p.value.max())),1e-9);c.update(limits=[-mx,mx],norm="two_slope")
        rec=api["_render_style"](target,"spatial",p,c,"advanced",out);return [rec],rec
    allv=p.value.to_numpy(float);common={}
    if signed:
        mx=max(abs(float(np.nanmin(allv))),abs(float(np.nanmax(allv))),1e-9);common={"limits":[-mx,mx],"norm":"two_slope"}
    else:
        lo=float(np.nanmin(allv));hi=float(np.nanmax(allv));common={"limits":[lo,hi if hi>lo else lo+1e-9],"norm":"linear"}
    for sec,g in p.groupby("section",sort=False):
        c=dict(api["_base_cfg"](config),title=f"{title} · {sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label=label,continuous_preset=config.get("signed_preset","D03") if signed else config.get("continuous_preset","M02"),invert_y=bool(config.get("invert_y",False)),**common)
        records.append(api["_render_style"](target+"__"+api["_slug"](sec),"spatial",g,c,"advanced",out))
    panel=api["_contact_sheet"](target,records,out,min(3,len(records)));return records,panel


def _categorical_sections(sp,field,title,config,out,target,api):
    sections=list(dict.fromkeys(sp.section.astype(str)));records=[]
    if len(sections)==1:
        rec=api["_custom_figure"](target,api["_categorical_spatial"](sp,field,config,title),out);return [rec],rec
    for sec,g in sp.groupby("section",sort=False):records.append(api["_custom_figure"](target+"__"+api["_slug"](sec),api["_categorical_spatial"](g,field,config,f"{title} · {sec}"),out))
    return records,api["_contact_sheet"](target,records,out,min(3,len(records)))


def render_spatial_gradient(inputs,config,out,api,target_prefix="spatial"):
    sp=inputs["spatial"].copy();tr=inputs["trajectory"].copy();api["_validate_contract"](sp,"spatial_point");api["_validate_contract"](tr,"trajectory")
    records=[];skipped=[];base=api["_base_cfg"](config);gradient_target="spatial_gradient" if target_prefix=="spatial" else "embryonic_axis_gradient"
    if "gradient_value" in sp:
        detail,main=_scalar_sections(sp,"gradient_value","Anatomical / spatial gradient",config.get("gradient_label","Supplied gradient coordinate"),config,out,gradient_target,api);records.extend(detail);records.append(main) if main and main not in detail else None
    else:skipped.append({"target":gradient_target,"reason":"gradient_value not supplied."})
    if target_prefix=="spatial":
        if "pseudotime" in sp:
            pseudo_detail,pseudo_main=_scalar_sections(sp,"pseudotime","Spatial pseudotime",config.get("pseudotime_label","Supplied pseudotime"),config,out,"spatial_pseudotime",api);records.extend(pseudo_detail);records.append(pseudo_main) if pseudo_main and pseudo_main not in pseudo_detail else None
        else:pseudo_detail=[];skipped.append({"target":"spatial_pseudotime","reason":"pseudotime not supplied."})
    else:
        group_col="cell_state" if "cell_state" in sp else "group" if "group" in sp else None
        if group_col:
            detail,main=_categorical_sections(sp,group_col,"Embryonic section / state map",config,out,"embryo_section",api);records.extend(detail);records.append(main) if main and main not in detail else None
        elif "gradient_value" in sp:
            detail,main=_scalar_sections(sp,"gradient_value","Embryonic section gradient",config.get("gradient_label","Gradient"),config,out,"embryo_section",api);records.extend(detail);records.append(main) if main and main not in detail else None
        else:skipped.append({"target":"embryo_section","reason":"No supplied state label or gradient field."})
    if {"feature","value"}<=set(tr):
        curve_target="gene_position_curve" if target_prefix=="spatial" else "development_gene_gradient";records.append(api["_custom_figure"](curve_target,t4._line_curves(tr,"Gene programmes along the supplied axis",config.get("axis_label","Axis / pseudotime"),config.get("value_label","Expression / score"),config,api,("feature",)),out))
        th=tr.dropna(subset=["feature","value"])[["feature","time","value"]].rename(columns={"feature":"gene"}).groupby(["gene","time"],sort=False).value.mean().reset_index();tc=dict(base,title="Spatial developmental programme heatmap",gene_order=list(dict.fromkeys(th.gene.astype(str))),value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("signed_preset","D03"))
        if target_prefix=="spatial":records.append(api["_render_style"]("spatial_trajectory_heatmap","trajectory_heatmap",th,tc,"advanced",out));records.append(api["_custom_figure"]("multi_gene_gradient",t4._line_curves(tr,"Multi-gene spatial gradient",config.get("axis_label","Axis / pseudotime"),config.get("value_label","Expression / score"),config,api,("feature",)),out))
    else:
        if target_prefix=="spatial":skipped += [{"target":x,"reason":"feature/value trajectory rows not supplied."} for x in ["gene_position_curve","spatial_trajectory_heatmap","multi_gene_gradient"]]
        else:skipped.append({"target":"development_gene_gradient","reason":"feature/value trajectory rows not supplied."})
    if {"probability","state"}<=set(tr):
        pr=tr.dropna(subset=["probability"]).groupby(["state","time"],sort=False).probability.mean().rename("value").reset_index().rename(columns={"state":"feature"});target="cellstate_probability_axis" if target_prefix=="spatial" else "cellstate_axis";records.append(api["_custom_figure"](target,t4._line_curves(pr,"Cell-state probability along the axis",config.get("axis_label","Axis / pseudotime"),"Mean supplied probability",config,api,("feature",)),out))
    else:skipped.append({"target":"cellstate_probability_axis" if target_prefix=="spatial" else "cellstate_axis","reason":"state/probability not supplied."})
    if target_prefix=="spatial":
        p=api["_contact_sheet"]("spatial_development_program",[r for r in records if r.get("target") not in {"spatial_development_program","aligned_section_trajectory"}],out,2);records.append(p) if p else None
        if "pseudotime" in sp and sp.section.nunique()>1 and pseudo_detail:
            p=api["_contact_sheet"]("aligned_section_trajectory",pseudo_detail,out,min(3,len(pseudo_detail)));records.append(p) if p else None
        else:skipped.append({"target":"aligned_section_trajectory","reason":"Requires multiple sections with supplied pseudotime."})
    else:
        p=api["_contact_sheet"]("embryo_gradient_panel",[r for r in records if r.get("target")!="embryo_gradient_panel"],out,2);records.append(p) if p else None
    return records,skipped


def render_spatial_gradient_trajectory(inputs,config,out,api):return render_spatial_gradient(inputs,config,out,api,"spatial")
def render_development_spatial_gradient(inputs,config,out,api):return render_spatial_gradient(inputs,config,out,api,"development")
