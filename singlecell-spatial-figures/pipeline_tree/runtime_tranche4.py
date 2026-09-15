"""Fourth executable tranche: pathway/regulon and spatial/developmental advanced views."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

INK="#263641";MUTED="#65757F";GRID="#E6EBEE"


def _spatial_scalar(d,field,title,label,config,out,target,api,signed=False):
    p=d[["id","section","x","y",field]].rename(columns={field:"value"}).dropna(subset=["value"])
    if p.empty:return None
    c=dict(api["_base_cfg"](config),title=title,coordinate_unit=config.get("coordinate_unit","µm"),value_label=label,
           continuous_preset=config.get("signed_preset","D03") if signed else config.get("continuous_preset","M02"),
           invert_y=bool(config.get("invert_y",False)))
    if signed:
        mx=max(abs(float(p.value.min())),abs(float(p.value.max())),1e-9);c.update(limits=[-mx,mx],norm="two_slope")
    return api["_render_style"](target,"spatial",p,c,"advanced",out)


def _line_curves(d,title,xlabel,ylabel,config,api,group_cols=("feature",)):
    def maker():
        fig,ax=plt.subplots(figsize=(7.2,5.1),facecolor="white")
        use=d.dropna(subset=["time","value"]).copy()
        for name,g in use.groupby(list(group_cols),sort=False):
            g=g.groupby("time",sort=True).value.mean().reset_index()
            label=" / ".join(map(str,name if isinstance(name,tuple) else (name,)))
            ax.plot(g.time,g.value,lw=1.6,label=label)
        ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK)
        if use.groupby(list(group_cols)).ngroups<=14:ax.legend(frameon=False,bbox_to_anchor=(1.02,1),loc="upper left",fontsize=7)
        ax.spines[["top","right"]].set_visible(False);ax.grid(axis="y",color=GRID,lw=.5)
        return fig
    return maker


def render_pathway_activity(inputs,config,out,api):
    activity=inputs["activity"].copy();enrich=inputs["enrichment"].copy();gsea=inputs["gsea"].copy()
    api["_validate_contract"](activity,"group_feature");api["_validate_contract"](enrich,"enrichment_result");api["_validate_contract"](gsea,"gsea_profile")
    records=[];skipped=[];base=api["_base_cfg"](config)
    terms=list(dict.fromkeys(enrich.term.astype(str)));groups=list(dict.fromkeys(activity.group.astype(str)));features=list(dict.fromkeys(activity.feature.astype(str)))
    ec=dict(base,title="Pathway enrichment effects",term_order=terms,effect_label=config.get("effect_label","Enrichment effect"),q_label="q",count_label=config.get("count_label","Supporting count"))
    records.append(api["_render_style"]("enrichment_dotplot","enrichment",enrich[["term","effect","q","count"]],ec,"minimal",out))
    records.append(api["_render_style"]("enrichment_lollipop","enrichment",enrich[["term","effect","q","count"]],dict(ec,title="Ranked pathway enrichment"),"advanced",out))
    records.append(api["_render_style"]("signed_enrichment","enrichment",enrich[["term","effect","q","count"]],dict(ec,title="Signed pathway enrichment"),"advanced",out))
    hc=dict(base,title="Pathway / regulator activity by cell state",group_order=groups,feature_order=features,value_label=config.get("activity_label","Activity score"),continuous_preset=config.get("signed_preset","D03"))
    records.append(api["_render_style"]("activity_heatmap","heatmap",activity[["group","feature","value"]+(["module"] if "module" in activity else [])],hc,"advanced",out))
    if "module" in activity:
        records.append(api["_render_style"]("tf_pathway_heatmap","heatmap",activity[["group","feature","value","module"]],dict(hc,title="TF and pathway activity modules"),"advanced",out))
    else:skipped.append({"target":"tf_pathway_heatmap","reason":"module/class annotation not supplied in activity input."})
    terms_g=list(dict.fromkeys(gsea.term.astype(str))) if "term" in gsea else []
    selected=config.get("gsea_term",terms_g[0] if len(terms_g)==1 else None)
    gg=gsea.copy()
    if terms_g:
        if selected is None:skipped.append({"target":"gsea_running_score","reason":"Multiple GSEA profiles supplied; set gsea_term explicitly."});gg=gg.iloc[0:0]
        else:
            if str(selected) not in set(gsea.term.astype(str)):raise ValueError("gsea_term is absent from supplied GSEA profiles")
            gg=gsea[gsea.term.astype(str)==str(selected)].copy()
    if len(gg):
        gc=dict(base,title=f"GSEA running profile{(' · '+str(selected)) if selected else ''}")
        records.append(api["_render_style"]("gsea_running_score","gsea",gg[["rank","running_score","hit","rank_metric"]],gc,"advanced",out))
    elif not any(x["target"]=="gsea_running_score" for x in skipped):skipped.append({"target":"gsea_running_score","reason":"No GSEA profile rows supplied."})
    atlas=api["_contact_sheet"]("pathway_activity_atlas",[r for r in records if r["target"] in {"activity_heatmap","signed_enrichment","gsea_running_score"}],out,2)
    if atlas:records.append(atlas)
    if len(gg) and "leading_edge" in gg and gg.leading_edge.astype(bool).any():
        le=gg[gg.leading_edge.astype(bool)].copy();le["abs_metric"]=le.rank_metric.abs();le=le.nlargest(int(config.get("leading_edge_n",15)),"abs_metric")
        labels=le["feature"].astype(str) if "feature" in le else le["rank"].astype(str)
        rankrec=api["_custom_figure"]("leading_edge_features",api["_rank_bar"](labels,le.rank_metric,"Leading-edge ranked features","Rank metric"),out);records.append(rankrec)
        panel=api["_contact_sheet"]("leading_edge_panel",[next(r for r in records if r["target"]=="gsea_running_score"),rankrec],out,2)
        if panel:records.append(panel)
    else:skipped.append({"target":"leading_edge_panel","reason":"No explicit leading_edge indicator supplied for the selected GSEA profile."})
    return records,skipped


def render_regulon_module(inputs,config,out,api):
    act=inputs["activity"].copy();emb=inputs["embedding"].copy();load=inputs["loading"].copy();net=inputs["network"].copy()
    api["_validate_contract"](act,"group_feature");api["_validate_contract"](emb,"embedding");api["_validate_contract"](load,"effect");api["_validate_contract"](net,"interaction")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(act.group.astype(str)));factors=list(dict.fromkeys(act.feature.astype(str)))
    hc=dict(base,title="Regulon / factor activity",group_order=groups,feature_order=factors,value_label=config.get("activity_label","Activity score"),continuous_preset=config.get("signed_preset","D03"))
    records.append(api["_render_style"]("regulon_heatmap","heatmap",act[["group","feature","value"]+(["module"] if "module" in act else [])],hc,"advanced",out))
    records.append(api["_render_style"]("factor_celltype_heatmap","heatmap",act[["group","feature","value"]+(["module"] if "module" in act else [])],dict(hc,title="Factor activity across cell states"),"advanced",out))
    if "value" in emb:
        from runtime_tranche2 import _continuous_embedding
        records.append(api["_custom_figure"]("module_embedding",_continuous_embedding(emb,"value","Selected module activity on embedding",config.get("embedding_value_label","Module score"),config,api),out))
    else:skipped.append({"target":"module_embedding","reason":"embedding.value module/regulon score not supplied."})
    order=load.sort_values("effect");records.append(api["_custom_figure"]("gene_loading",api["_rank_bar"](order.feature,order.effect,"Factor gene loadings",config.get("loading_label","Loading / effect")),out))
    if "effect" in act:
        sp=act[["group","feature","effect"]].rename(columns={"effect":"value"});sc=dict(hc,title="Supplied regulon specificity/effect",value_label=config.get("specificity_label","Supplied specificity / effect"))
        records.append(api["_render_style"]("regulon_specificity","heatmap",sp,sc,"advanced",out))
    else:skipped.append({"target":"regulon_specificity","reason":"No upstream specificity/effect field supplied; runtime does not compute a new specificity statistic."})
    if {"stage","value"}<=set(emb):
        td=pd.DataFrame({"id":emb.id,"group":emb.stage.astype(str),"value":emb.value})
        tc=dict(base,title="Module activity across developmental stages",group_order=list(dict.fromkeys(td.group)),value_label=config.get("embedding_value_label","Module score"))
        records.append(api["_render_style"]("module_lineage_activity","distribution",td,tc,"advanced",out))
    else:skipped.append({"target":"module_lineage_activity","reason":"stage and embedding.value are required."})
    nn=net.rename(columns={"score":"weight"})[["source","target","weight"]];nc=dict(base,title="TF / regulator target network",edge_unit=config.get("edge_unit","Supplied edge score"),categorical_preset=config.get("categorical_preset","C19"))
    records.append(api["_render_style"]("tf_target_network","network",nn,nc,"advanced",out))
    panel=api["_contact_sheet"]("factor_loading_activity_panel",[r for r in records if r["target"] in {"regulon_heatmap","module_embedding","gene_loading","tf_target_network"}],out,2)
    if panel:records.append(panel)
    return records,skipped


def render_svg_autocorrelation(inputs,config,out,api):
    eff=inputs["effects"].copy();moran=inputs["moran"].copy();sp=inputs["spatial"].copy()
    api["_validate_contract"](eff,"spatial_effect");api["_validate_contract"](moran,"moran_point");api["_validate_contract"](sp,"spatial_point")
    if not {"gene","value"}<=set(sp):raise ValueError("spatial.svg_autocorrelation spatial input requires gene/value for top feature maps")
    records=[];skipped=[];base=api["_base_cfg"](config);rank_field=config.get("rank_field","moran_i" if "moran_i" in eff else "effect")
    if rank_field not in eff:raise ValueError(f"rank_field {rank_field!r} is absent from spatial_effect input")
    rank=eff.dropna(subset=[rank_field]).sort_values(rank_field);records.append(api["_custom_figure"]("svg_rank",api["_rank_bar"](rank.feature,rank[rank_field],"Spatially variable feature ranking",rank_field),out));records.append(api["_custom_figure"]("autocorrelation_rank",api["_rank_bar"](rank.feature,rank[rank_field],"Spatial autocorrelation ranking",rank_field),out))
    feature=config.get("moran_feature",str(rank.iloc[-1].feature))
    mm=moran[moran.feature.astype(str)==str(feature)]
    if mm.empty:raise ValueError("moran_feature has no supplied Moran scatter points")
    def mscatter():
        fig,ax=plt.subplots(figsize=(5.5,5.2),facecolor="white");ax.scatter(mm.value,mm.spatial_lag,s=16,c="#5E8795",alpha=.65,lw=0);ax.axhline(0,c=MUTED,lw=.7);ax.axvline(0,c=MUTED,lw=.7);ax.set_xlabel("Supplied standardized value");ax.set_ylabel("Supplied spatial lag");ax.set_title(f"Moran scatter · {feature}",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
    records.append(api["_custom_figure"]("moran_scatter",mscatter,out))
    top=list(rank.tail(int(config.get("top_n_maps",6))).feature.astype(str));maps=[]
    for gene in top:
        p=sp[sp.gene.astype(str)==gene][["id","section","x","y","value"]]
        for sec,g in p.groupby("section",sort=False):
            c=dict(base,title=f"{gene} · {sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label=config.get("spatial_value_label","Spatial expression"),continuous_preset=config.get("continuous_preset","M02"));r=api["_render_style"]("svg_map__"+api["_slug"](gene)+"__"+api["_slug"](sec),"spatial",g,c,"advanced",out);maps.append(r);records.append(r)
    p=api["_contact_sheet"]("top_svg_maps",maps,out,2)
    if p:records.append(p)
    metrics=[x for x in ["effect","moran_i","geary_c"] if x in eff]
    standardized=[]
    for metric in metrics:
        s=eff[["feature",metric]].dropna().copy();sd=float(s[metric].std(ddof=0));s["value"]=(s[metric]-float(s[metric].mean()))/(sd if sd>0 else 1);s["group"]=metric;standardized.append(s[["group","feature","value"]])
    if standardized:
        hm=pd.concat(standardized,ignore_index=True);hc=dict(base,title="Spatial feature evidence matrix",group_order=metrics,feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label="Statistic z-score across features",continuous_preset="D03",limits=[-3,3],norm="two_slope")
        records.append(api["_render_style"]("svg_heatmap","heatmap",hm,hc,"advanced",out))
    else:skipped.append({"target":"svg_heatmap","reason":"No finite spatial statistics available."})
    panel=api["_contact_sheet"]("svg_evidence_panel",[r for r in records if r["target"] in {"svg_rank","moran_scatter","top_svg_maps","svg_heatmap"}],out,2)
    if panel:records.append(panel)
    if "module" in eff and maps:
        module_map=dict(zip(eff.feature.astype(str),eff.module.astype(str)));chosen=[]
        seen=set()
        for r in maps:
            parts=r["target"].split("__");gene=parts[1] if len(parts)>1 else ""
            mod=module_map.get(gene)
            if mod is not None and mod not in seen:chosen.append(r);seen.add(mod)
        p=api["_contact_sheet"]("svg_module_atlas",chosen or maps[:4],out,2)
        if p:records.append(p)
    else:skipped.append({"target":"svg_module_atlas","reason":"module annotation not supplied in spatial_effect."})
    return records,skipped


def render_spatial_gradient(inputs,config,out,api,target_prefix="spatial"):
    sp=inputs["spatial"].copy();tr=inputs["trajectory"].copy();api["_validate_contract"](sp,"spatial_point");api["_validate_contract"](tr,"trajectory")
    records=[];skipped=[];base=api["_base_cfg"](config)
    gradient_target="spatial_gradient" if target_prefix=="spatial" else "embryonic_axis_gradient"
    if "gradient_value" in sp:
        rec=_spatial_scalar(sp,"gradient_value","Anatomical / spatial gradient",config.get("gradient_label","Supplied gradient coordinate"),config,out,gradient_target,api);records.append(rec) if rec else None
    else:skipped.append({"target":gradient_target,"reason":"gradient_value not supplied."})
    pseudo_target="spatial_pseudotime" if target_prefix=="spatial" else "embryo_section"
    if target_prefix=="spatial":
        if "pseudotime" in sp:
            rec=_spatial_scalar(sp,"pseudotime","Spatial pseudotime",config.get("pseudotime_label","Supplied pseudotime"),config,out,pseudo_target,api);records.append(rec) if rec else None
        else:skipped.append({"target":pseudo_target,"reason":"pseudotime not supplied."})
    else:
        group_col="cell_state" if "cell_state" in sp else "group" if "group" in sp else None
        if group_col:records.append(api["_custom_figure"]("embryo_section",api["_categorical_spatial"](sp,group_col,config,"Embryonic section / state map"),out))
        elif "gradient_value" in sp:
            rec=_spatial_scalar(sp,"gradient_value","Embryonic section gradient",config.get("gradient_label","Gradient"),config,out,"embryo_section",api);records.append(rec) if rec else None
        else:skipped.append({"target":"embryo_section","reason":"No supplied state label or gradient field."})
    if {"feature","value"}<=set(tr):
        curve_target="gene_position_curve" if target_prefix=="spatial" else "development_gene_gradient"
        records.append(api["_custom_figure"](curve_target,_line_curves(tr,"Gene programmes along the supplied axis",config.get("axis_label","Axis / pseudotime"),config.get("value_label","Expression / score"),config,api,("feature",)),out))
        th=tr.dropna(subset=["feature","value"])[["feature","time","value"]].rename(columns={"feature":"gene"}).groupby(["gene","time"],sort=False).value.mean().reset_index();tc=dict(base,title="Spatial developmental programme heatmap",gene_order=list(dict.fromkeys(th.gene.astype(str))),value_label=config.get("value_label","Expression / score"),continuous_preset=config.get("signed_preset","D03"))
        if target_prefix=="spatial":records.append(api["_render_style"]("spatial_trajectory_heatmap","trajectory_heatmap",th,tc,"advanced",out))
        multi=api["_custom_figure"]("multi_gene_gradient",_line_curves(tr,"Multi-gene spatial gradient",config.get("axis_label","Axis / pseudotime"),config.get("value_label","Expression / score"),config,api,("feature",)),out) if target_prefix=="spatial" else None
        if multi:records.append(multi)
    else:
        if target_prefix=="spatial":skipped += [{"target":x,"reason":"feature/value trajectory rows not supplied."} for x in ["gene_position_curve","spatial_trajectory_heatmap","multi_gene_gradient"]]
        else:skipped.append({"target":"development_gene_gradient","reason":"feature/value trajectory rows not supplied."})
    if {"probability","state"}<=set(tr):
        pr=tr.dropna(subset=["probability"]).groupby(["state","time"],sort=False).probability.mean().rename("value").reset_index().rename(columns={"state":"feature"})
        target="cellstate_probability_axis" if target_prefix=="spatial" else "cellstate_axis"
        records.append(api["_custom_figure"](target,_line_curves(pr,"Cell-state probability along the axis",config.get("axis_label","Axis / pseudotime"),"Mean supplied probability",config,api,("feature",)),out))
    else:skipped.append({"target":"cellstate_probability_axis" if target_prefix=="spatial" else "cellstate_axis","reason":"state/probability not supplied."})
    if target_prefix=="spatial":
        p=api["_contact_sheet"]("spatial_development_program",records,out,2)
        if p:records.append(p)
        if "pseudotime" in sp and sp.section.nunique()>1:
            sec=[]
            for section,g in sp.groupby("section",sort=False):
                rec=_spatial_scalar(g,"pseudotime",f"Spatial pseudotime · {section}",config.get("pseudotime_label","Supplied pseudotime"),config,out,"aligned__"+api["_slug"](section),api);sec.append(rec);records.append(rec)
            p=api["_contact_sheet"]("aligned_section_trajectory",sec,out,min(3,len(sec)))
            if p:records.append(p)
        else:skipped.append({"target":"aligned_section_trajectory","reason":"Requires multiple sections with supplied pseudotime."})
    else:
        p=api["_contact_sheet"]("embryo_gradient_panel",records,out,2)
        if p:records.append(p)
    return records,skipped


def render_spatial_gradient_trajectory(inputs,config,out,api):return render_spatial_gradient(inputs,config,out,api,"spatial")
def render_development_spatial_gradient(inputs,config,out,api):return render_spatial_gradient(inputs,config,out,api,"development")


def render_virtual_embryo_prediction(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"prediction");records=[];skipped=[]
    if not {"section","x","y"}<=set(d):raise ValueError("virtual embryo spatial prediction requires section/x/y coordinates")
    for field,target,title,label,signed in [
        ("observed","prediction_truth","Observed embryo state","Observed",False),
        ("predicted","prediction_map","Predicted embryo state","Predicted",False)]:
        rec=_spatial_scalar(d,field,title,label,config,out,target,api,signed);records.append(rec) if rec else None
    dd=d.copy();dd["_residual"]=dd["residual"] if "residual" in dd else dd.observed-dd.predicted
    rec=_spatial_scalar(dd,"_residual","Prediction residual",config.get("residual_label","Observed − predicted"),config,out,"prediction_residual",api,True);records.append(rec) if rec else None
    if "uncertainty" in d:
        rec=_spatial_scalar(d,"uncertainty","Prediction uncertainty",config.get("uncertainty_label","Supplied uncertainty"),config,out,"prediction_uncertainty",api,False);records.append(rec) if rec else None
    else:skipped.append({"target":"prediction_uncertainty","reason":"uncertainty not supplied by prediction model."})
    p=api["_contact_sheet"]("virtual_embryo_prediction_panel",records,out,2)
    if p:records.append(p)
    return records,skipped
