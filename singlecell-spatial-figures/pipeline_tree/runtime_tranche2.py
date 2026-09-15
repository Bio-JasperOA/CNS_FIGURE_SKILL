"""Second executable pipeline tranche: annotation, DE, trajectory and spatial context.

Functions receive the parent runtime namespace as ``api`` so output/audit semantics
stay centralized without circular imports. No upstream biological inference occurs here.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

INK="#263641";MUTED="#65757F";GRID="#E6EBEE"


def _continuous_embedding(d,value,title,label,config,api):
    def maker():
        fig,ax=plt.subplots(figsize=(6.8,5.5),facecolor="white")
        sc=ax.scatter(d.x,d.y,c=d[value],s=config.get("point_area",5),cmap=api["style_cmap"]({"continuous_preset":config.get("continuous_preset","M02")}),lw=0,rasterized=True)
        ax.set_aspect("equal");ax.set_xticks([]);ax.set_yticks([]);ax.set_xlabel("Embedding 1");ax.set_ylabel("Embedding 2")
        ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK)
        fig.colorbar(sc,ax=ax,label=label,fraction=.04,pad=.03)
        ax.spines[["top","right"]].set_visible(False)
        return fig
    return maker


def _categorical_spatial(d,col,title,config,api):
    return api["_categorical_spatial"](d,col,config,title)


def render_annotation(inputs,config,out,api):
    markers=inputs["markers"].copy();emb=inputs["embedding"].copy();records=[];skipped=[]
    api["_validate_contract"](markers,"group_feature");api["_validate_contract"](emb,"embedding")
    if "group" not in emb: raise ValueError("scrna.annotation embedding input requires group")
    groups=list(dict.fromkeys(emb.group.astype(str)));features=list(dict.fromkeys(markers.feature.astype(str)))
    base=api["_base_cfg"](config)
    ec=dict(base,title="Annotated cell-state embedding",group_order=groups,categorical_preset=config.get("categorical_preset","C19"),label_groups=groups[:14])
    e=emb[["id","x","y","group"]+(["parent"] if "parent" in emb else [])].copy();e["group"]=e.group.astype(str)
    records.append(api["_render_style"]("annotated_embedding","embedding",e,ec,"advanced",out))
    if "fraction" in markers:
        dot=markers[["group","feature","value","fraction"]+(["module"] if "module" in markers else [])].rename(columns={"value":"mean"})
        dc=dict(base,title="Canonical marker evidence",group_order=groups,feature_order=features,value_label=config.get("value_label","Mean expression"),categorical_preset=config.get("categorical_preset","C19"))
        records.append(api["_render_style"]("marker_dotplot","dotplot",dot,dc,"advanced",out))
    else: skipped.append({"target":"marker_dotplot","reason":"fraction field not supplied; dot area cannot be encoded honestly."})
    hm=markers[["group","feature","value"]+(["module"] if "module" in markers else [])].copy()
    hc=dict(base,title="Marker programme matrix",group_order=groups,feature_order=features,value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("continuous_preset","D03"))
    records.append(api["_render_style"]("marker_heatmap","heatmap",hm,hc,"advanced",out))
    records.append(api["_render_style"]("grouped_marker_heatmap","heatmap",hm,dict(hc,title="Grouped marker programmes"),"advanced",out))
    if "confidence" in emb:
        records.append(api["_custom_figure"]("annotation_confidence",_continuous_embedding(emb,"confidence","Annotation confidence","Confidence",config,api),out))
        records.append(api["_custom_figure"]("annotation_confidence_embedding",_continuous_embedding(emb,"confidence","Annotation confidence on embedding","Confidence",config,api),out))
    else:
        skipped += [{"target":"annotation_confidence","reason":"No confidence supplied."},{"target":"annotation_confidence_embedding","reason":"No confidence supplied."}]
    if "parent" in emb:
        records.append(api["_render_style"]("celltype_hierarchy_markers","embedding",e,dict(ec,title="Declared cell-type hierarchy"),"advanced",out))
    else: skipped.append({"target":"celltype_hierarchy_markers","reason":"No upstream parent hierarchy supplied."})
    panel=api["_contact_sheet"]("annotation_evidence_panel",[r for r in records if r["target"] in {"annotated_embedding","marker_dotplot","marker_heatmap","annotation_confidence"}],out,2)
    if panel:records.append(panel)
    return records,skipped


def render_markers_de(inputs,config,out,api):
    markers=inputs["markers"].copy();de=inputs["de"].copy();records=[];skipped=[]
    api["_validate_contract"](markers,"group_feature");api["_validate_contract"](de,"effect")
    groups=list(dict.fromkeys(markers.group.astype(str)));features=list(dict.fromkeys(markers.feature.astype(str)));base=api["_base_cfg"](config)
    if "fraction" in markers:
        dot=markers[["group","feature","value","fraction"]+(["module"] if "module" in markers else [])].rename(columns={"value":"mean"})
        records.append(api["_render_style"]("marker_dotplot","dotplot",dot,dict(base,title="Marker expression and detection",group_order=groups,feature_order=features,value_label=config.get("value_label","Mean expression")),"advanced",out))
    else:skipped.append({"target":"marker_dotplot","reason":"fraction not supplied."})
    hm=markers[["group","feature","value"]+(["module"] if "module" in markers else [])]
    hc=dict(base,title="Differential marker matrix",group_order=groups,feature_order=features,value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("continuous_preset","D03"))
    records.append(api["_render_style"]("de_heatmap","heatmap",hm,hc,"advanced",out));records.append(api["_render_style"]("grouped_marker_matrix","heatmap",hm,dict(hc,title="Grouped differential marker matrix"),"advanced",out))
    if "q" in de:
        vol=de[["feature","effect","q"]].dropna().copy()
        vc=dict(base,title="Differential expression",effect_label=config.get("effect_label","Effect"),q_label="q",label_n=int(config.get("label_n",8)))
        records.append(api["_render_style"]("volcano","volcano",vol,vc,"minimal",out));records.append(api["_render_style"]("annotated_volcano","volcano",vol,dict(vc,title="Differential expression with selected labels"),"advanced",out))
    else: skipped += [{"target":"volcano","reason":"q not supplied."},{"target":"annotated_volcano","reason":"q not supplied."}]
    if "mean" in de:
        def ma():
            fig,ax=plt.subplots(figsize=(6.7,5.0),facecolor="white");ax.scatter(de["mean"],de.effect,s=12,c="#628A98",alpha=.65,lw=0,rasterized=True);ax.axhline(0,c=MUTED,lw=.8)
            ax.set_xlabel("Mean expression");ax.set_ylabel(config.get("effect_label","Effect"));ax.set_title("MA-style differential expression",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
        records.append(api["_custom_figure"]("ma_plot",ma,out))
    else:skipped.append({"target":"ma_plot","reason":"mean expression not supplied."})
    rank=de.sort_values("effect");records.append(api["_custom_figure"]("ranked_effect",api["_rank_bar"](rank.feature,rank.effect,"Ranked differential effects",config.get("effect_label","Effect")),out))
    if {"lower","upper"}<=set(de):
        f=de[["feature","effect","lower","upper"]].dropna().sort_values("effect",key=abs,ascending=False).head(int(config.get("forest_n",15))).rename(columns={"feature":"term","effect":"estimate"})
        fc=dict(base,title="Top differential effect intervals",term_order=list(f.term),effect_label=config.get("effect_label","Effect"),interval_label=config.get("interval_label","Supplied interval"))
        records.append(api["_render_style"]("de_forest","forest",f,fc,"advanced",out))
    else:skipped.append({"target":"de_forest","reason":"lower/upper not supplied."})
    skipped.append({"target":"top_gene_distribution","reason":"Raw sample/cell expression is not present in effect or group_feature contracts; runtime will not reconstruct it."})
    panel=api["_contact_sheet"]("de_evidence_panel",[r for r in records if r["target"] in {"marker_dotplot","de_heatmap","annotated_volcano","de_forest","ranked_effect"}],out,2)
    if panel:records.append(panel)
    return records,skipped


def render_trajectory(inputs,config,out,api):
    d=inputs["main"].copy();emb=inputs["embedding"].copy();records=[];skipped=[]
    api["_validate_contract"](d,"trajectory");api["_validate_contract"](emb,"embedding");base=api["_base_cfg"](config)
    if "value" not in emb: raise ValueError("scrna.trajectory embedding input requires value=pseudotime or reviewed continuous ordering")
    records.append(api["_custom_figure"]("pseudotime_embedding",_continuous_embedding(emb,"value","Pseudotime embedding",config.get("time_label","Pseudotime"),config,api),out))
    if "group" in emb and config.get("abstract_edges"):
        e=emb[["id","x","y","group"]].copy();ec=dict(base,title="Supplied lineage graph",group_order=list(dict.fromkeys(e.group.astype(str))),abstract_edges=config["abstract_edges"],edge_definition=config.get("edge_definition","Upstream lineage graph"),categorical_preset=config.get("categorical_preset","C19"))
        records.append(api["_render_style"]("lineage_graph","embedding",e,ec,"advanced",out))
    else:skipped.append({"target":"lineage_graph","reason":"Requires embedding group plus supplied abstract_edges; 2-D geometry is never used to infer lineage."})
    if {"feature","value"}<=set(d):
        def trend():
            fig,ax=plt.subplots(figsize=(7.2,5.0),facecolor="white");keys=["feature"]+(["lineage"] if "lineage" in d else [])
            for name,g in d.dropna(subset=["feature","value"]).groupby(keys,sort=False):
                g=g.sort_values("time");lab=" / ".join(map(str,name if isinstance(name,tuple) else (name,)));ax.plot(g.time,g.value,lw=1.6,label=lab)
            ax.set_xlabel(config.get("time_label","Pseudotime"));ax.set_ylabel(config.get("value_label","Expression / score"));ax.set_title("Gene programmes along trajectory",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.legend(frameon=False,bbox_to_anchor=(1.02,1),loc="upper left",fontsize=7);ax.spines[["top","right"]].set_visible(False);return fig
        records.append(api["_custom_figure"]("gene_trend",trend,out))
        th=d.dropna(subset=["feature","value"])[["feature","time","value"]].rename(columns={"feature":"gene"})
        # Aggregate only when multiple lineages/states supply the same gene/time point.
        th=th.groupby(["gene","time"],sort=False).value.mean().reset_index()
        tc=dict(base,title="Temporal gene programme heatmap",gene_order=list(dict.fromkeys(th.gene.astype(str))),value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("continuous_preset","D03"))
        records.append(api["_render_style"]("trajectory_heatmap","trajectory_heatmap",th,tc,"advanced",out))
        records.append(api["_render_style"]("branch_program_heatmap","trajectory_heatmap",th,dict(tc,title="Branch-associated gene programmes"),"advanced",out))
        records.append(api["_render_style"]("branch_expression","trajectory_heatmap",th,dict(tc,title="Branch expression programmes"),"advanced",out))
    else:
        skipped += [{"target":x,"reason":"feature/value trajectory rows not supplied."} for x in ["gene_trend","trajectory_heatmap","branch_program_heatmap","branch_expression"]]
    if {"lineage","mean","lower","upper"}<=set(d):
        tr=d.dropna(subset=["lineage","mean","lower","upper"])[["lineage","time","mean","lower","upper"]]
        if len(tr):
            tc=dict(base,title="Lineage trends with supplied interval",lineage_order=list(dict.fromkeys(tr.lineage.astype(str))),interval_label=config.get("interval_label","Supplied interval"),value_label=config.get("value_label","Programme score"))
            records.append(api["_render_style"]("trend_with_interval","trajectory",tr,tc,"advanced",out))
        else: skipped.append({"target":"trend_with_interval","reason":"No finite interval rows."})
    else:skipped.append({"target":"trend_with_interval","reason":"lineage/mean/lower/upper not supplied."})
    if "probability" in d:
        p=d.dropna(subset=["probability"]);order=p.groupby("state").probability.mean().sort_values()
        records.append(api["_custom_figure"]("lineage_probability",api["_rank_bar"](order.index,order.values,"Lineage / fate probabilities","Mean supplied probability"),out))
    else:skipped.append({"target":"lineage_probability","reason":"probability not supplied."})
    if {"transition_to","mass"}<=set(d):
        t=d.dropna(subset=["transition_to","mass"]);hm=t.groupby(["state","transition_to"],sort=False).mass.sum().rename("value").reset_index().rename(columns={"state":"feature","transition_to":"group"})
        hc=dict(base,title="State-transition mass matrix",group_order=list(dict.fromkeys(hm.group.astype(str))),feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label=config.get("mass_label","Transition mass"),continuous_preset=config.get("continuous_preset","M02"))
        records.append(api["_render_style"]("transition_matrix","heatmap",hm,hc,"advanced",out))
    else:skipped.append({"target":"transition_matrix","reason":"transition_to/mass not supplied."})
    panel=api["_contact_sheet"]("developmental_panel",[r for r in records if r["target"] in {"pseudotime_embedding","lineage_graph","gene_trend","trajectory_heatmap","trend_with_interval","transition_matrix"}],out,2)
    if panel:records.append(panel)
    return records,skipped


def render_spatial_qc(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"spatial_point");records=[];skipped=[];base=api["_base_cfg"](config)
    metrics=[m for m in ["n_counts","n_features","pct_mito"] if m in d]
    if not metrics: raise ValueError("spatial.qc requires at least one of n_counts/n_features/pct_mito")
    for m in metrics:
        p=d[["id","section","x","y",m]].rename(columns={m:"value"});c=dict(base,title=f"Spatial QC · {m}",coordinate_unit=config.get("coordinate_unit","µm"),value_label=m,continuous_preset=config.get("continuous_preset","M02"),invert_y=bool(config.get("invert_y",False)))
        records.append(api["_render_style"]("spatial_"+m,"spatial",p,c,"advanced",out))
    if "n_counts" in d: records.append({"target":"spatial_counts","engine":"alias","kind":"spatial","mode":"advanced","outputs":next(r for r in records if r["target"]=="spatial_n_counts")["outputs"],"semantic_layers":["spatial counts"]})
    else:skipped.append({"target":"spatial_counts","reason":"n_counts not supplied."})
    if "n_features" in d: records.append({"target":"spatial_genes","engine":"alias","kind":"spatial","mode":"advanced","outputs":next(r for r in records if r["target"]=="spatial_n_features")["outputs"],"semantic_layers":["spatial genes"]})
    else:skipped.append({"target":"spatial_genes","reason":"n_features not supplied."})
    rows=[]
    for sec,g in d.groupby("section",sort=False):
        for m in metrics: rows.append((str(sec),m,float(g[m].median())))
    med=pd.DataFrame(rows,columns=["group","feature","raw"]);med["value"]=med.groupby("feature").raw.transform(lambda x:(x-x.mean())/(x.std(ddof=0) if x.std(ddof=0)>0 else 1))
    hc=dict(base,title="Section-level spatial QC summary",group_order=list(dict.fromkeys(med.group)),feature_order=metrics,value_label="Median metric z-score",continuous_preset="D03",limits=[-2.5,2.5],norm="two_slope")
    records.append(api["_render_style"]("section_qc_summary","heatmap",med[["group","feature","value"]],hc,"advanced",out));records.append(api["_render_style"]("section_qc_comparison","heatmap",med[["group","feature","value"]],dict(hc,title="Cross-section QC comparison"),"advanced",out))
    panel=api["_contact_sheet"]("multi_metric_spatial_qc",records[:min(5,len(records))],out,2)
    if panel:records.append(panel)
    panel2=api["_contact_sheet"]("spatial_qc_dashboard",records[:min(5,len(records))],out,2)
    if panel2:records.append(panel2)
    skipped.append({"target":"tissue_image","reason":"No image asset is part of spatial_point; runtime does not fabricate histology from coordinates."})
    return records,skipped


def render_spatial_domains(inputs,config,out,api):
    d=inputs["main"].copy();markers=inputs["markers"].copy();api["_validate_contract"](d,"spatial_point");api["_validate_contract"](markers,"group_feature");records=[];skipped=[]
    col="domain" if "domain" in d else "group" if "group" in d else None
    if col is None: raise ValueError("spatial.domains requires supplied domain or group labels")
    domains=list(dict.fromkeys(d[col].astype(str)));base=api["_base_cfg"](config)
    records.append(api["_custom_figure"]("spatial_domain_map",_categorical_spatial(d,col,"Spatial domains",config,api),out))
    size=d.groupby(col,sort=False).size();records.append(api["_custom_figure"]("domain_size",api["_rank_bar"](size.index,size.values,"Spatial-domain size","Spots / cells"),out))
    hm=markers[["group","feature","value"]+(["module"] if "module" in markers else [])].copy();hc=dict(base,title="Spatial-domain marker programmes",group_order=domains,feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("continuous_preset","D03"))
    records.append(api["_render_style"]("domain_marker_heatmap","heatmap",hm,hc,"advanced",out))
    if "confidence" in d:
        p=d[["id","section","x","y","confidence"]].rename(columns={"confidence":"value"});sc=dict(base,title="Domain assignment confidence",coordinate_unit=config.get("coordinate_unit","µm"),value_label="Confidence",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
        records.append(api["_render_style"]("domain_confidence_map","spatial",p,sc,"advanced",out))
    else:skipped.append({"target":"domain_confidence_map","reason":"confidence not supplied."})
    skipped.append({"target":"domain_boundary_overlay","reason":"Requires supplied segmentation/domain boundary geometry; labels alone are not converted into boundaries."})
    panel=api["_contact_sheet"]("domain_marker_panel",records,out,2)
    if panel:records.append(panel)
    return records,skipped


def render_spatial_niche(inputs,config,out,api):
    s=inputs["spatial"].copy();inter=inputs["interaction"].copy();api["_validate_contract"](s,"spatial_point");api["_validate_contract"](inter,"interaction");records=[];skipped=[];base=api["_base_cfg"](config)
    niche_col="niche" if "niche" in s else "domain" if "domain" in s else None
    if niche_col is None: raise ValueError("spatial.neighborhood_niche requires supplied niche/domain label")
    records.append(api["_custom_figure"]("neighborhood_map",_categorical_spatial(s,niche_col,"Spatial neighborhoods",config,api),out));records.append(api["_custom_figure"]("niche_map",_categorical_spatial(s,niche_col,"Spatial niches",config,api),out))
    h=inter.groupby(["source","target"],sort=False).score.sum().rename("value").reset_index().rename(columns={"source":"feature","target":"group"});hc=dict(base,title="Neighborhood co-occurrence / enrichment",group_order=list(dict.fromkeys(h.group.astype(str))),feature_order=list(dict.fromkeys(h.feature.astype(str))),value_label=config.get("score_label","Supplied association score"),continuous_preset=config.get("continuous_preset","M02"))
    records.append(api["_render_style"]("cooccurrence_heatmap","heatmap",h,hc,"advanced",out))
    rank=inter.assign(pair=inter.source.astype(str)+" → "+inter.target.astype(str)).groupby("pair").score.sum().sort_values();records.append(api["_custom_figure"]("pair_enrichment",api["_rank_bar"](rank.index,rank.values,"Neighborhood pair enrichment",config.get("score_label","Association score")),out))
    if "group" in s and niche_col!="group":
        tab=pd.crosstab(s["group"],s[niche_col],normalize="columns").rename_axis("feature").reset_index().melt("feature",var_name="group",value_name="value")
        cc=dict(base,title="Cell-state composition of niches",group_order=list(dict.fromkeys(s[niche_col].astype(str))),feature_order=list(dict.fromkeys(s["group"].astype(str))),value_label="Within-niche fraction",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
        records.append(api["_render_style"]("celltype_niche_heatmap","heatmap",tab,cc,"advanced",out))
    else:skipped.append({"target":"celltype_niche_heatmap","reason":"A separate group/cell-type label is required in addition to niche."})
    panel=api["_contact_sheet"]("niche_atlas",records,out,2)
    if panel:records.append(panel)
    if "condition" in s:
        counts=s.groupby(["condition",niche_col],sort=False).size().rename("value").reset_index().rename(columns={"condition":"group",niche_col:"feature"});counts["value"]=counts.groupby("group").value.transform(lambda x:x/x.sum())
        rc=dict(base,title="Niche composition across conditions",group_order=list(dict.fromkeys(counts.group.astype(str))),feature_order=list(dict.fromkeys(counts.feature.astype(str))),value_label="Within-condition fraction",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
        records.append(api["_render_style"]("regional_niche_comparison","heatmap",counts,rc,"advanced",out))
    else:skipped.append({"target":"regional_niche_comparison","reason":"condition not supplied."})
    if "pathway" in inter:
        p=inter.groupby("pathway").score.sum().sort_values();prog=api["_custom_figure"]("niche_pathway_support",api["_rank_bar"](p.index,p.values,"Niche-associated pathways",config.get("score_label","Association score")),out);records.append(prog);panel2=api["_contact_sheet"]("niche_marker_pathway_panel",[records[1],records[2],prog],out,2)
        if panel2:records.append(panel2)
    else:skipped.append({"target":"niche_marker_pathway_panel","reason":"pathway not supplied in interaction input."})
    return records,skipped
