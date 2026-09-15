"""Third executable tranche: cross-modal, lineage, foundation-model and spatial communication views."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

INK="#263641";MUTED="#65757F";GRID="#E6EBEE"


def render_reference_mapping(inputs,config,out,api):
    ref=inputs["reference"].copy();sp=inputs["spatial"].copy();api["_validate_contract"](ref,"embedding");api["_validate_contract"](sp,"spatial_composition")
    if "group" not in ref:raise ValueError("reference embedding requires group labels")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(ref.group.astype(str)))
    ec=dict(base,title="Reference single-cell embedding",group_order=groups,categorical_preset=config.get("categorical_preset","C19"),label_groups=groups[:14])
    records.append(api["_render_style"]("reference_embedding","embedding",ref[["id","x","y","group"]],ec,"advanced",out))
    wide=sp.pivot(index=["id","section","x","y"],columns="group",values="fraction").fillna(0)
    dom=wide.idxmax(axis=1).rename("dominant").reset_index();records.append(api["_custom_figure"]("mapped_spatial_identity",api["_categorical_spatial"](dom,"dominant",dict(config,coordinate_unit=config.get("coordinate_unit","µm")),"Mapped spatial identity"),out))
    maxp=wide.max(axis=1).rename("value").reset_index();mc=dict(base,title="Mapping confidence / maximum fraction",coordinate_unit=config.get("coordinate_unit","µm"),value_label="Maximum mapped fraction",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
    records.append(api["_render_style"]("mapping_confidence","spatial",maxp,mc,"advanced",out))
    ref_ab=ref.group.astype(str).value_counts(normalize=True);sp_ab=sp.groupby("group").fraction.mean();common=[g for g in groups if g in sp_ab.index]
    def concordance():
        fig,ax=plt.subplots(figsize=(5.5,5.1),facecolor="white");x=np.array([ref_ab.get(g,np.nan) for g in common]);y=np.array([sp_ab.get(g,np.nan) for g in common]);ax.scatter(x,y,s=42,c="#587F8E")
        lim=max(.05,float(np.nanmax(np.r_[x,y]))*1.08);ax.plot([0,lim],[0,lim],ls="--",lw=.8,c=MUTED)
        for a,b,g in zip(x,y,common):ax.text(a,b,g,fontsize=7,ha="left",va="bottom")
        ax.set_xlim(0,lim);ax.set_ylim(0,lim);ax.set_xlabel("Reference cell fraction");ax.set_ylabel("Mean spatial fraction");ax.set_title("Reference–space abundance concordance",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
    records.append(api["_custom_figure"]("abundance_concordance",concordance,out))
    mat=pd.DataFrame({"feature":common,"Reference":[ref_ab[g] for g in common],"Spatial":[sp_ab[g] for g in common]}).melt("feature",var_name="group",value_name="value")
    hc=dict(base,title="Reference versus spatial abundance",group_order=["Reference","Spatial"],feature_order=common,value_label="Fraction",continuous_preset=config.get("continuous_preset","M02"),limits=[0,max(.01,float(mat.value.max()))],norm="linear")
    records.append(api["_render_style"]("mapping_consistency_heatmap","heatmap",mat,hc,"advanced",out))
    entropy=-(wide.clip(lower=1e-12)*np.log(wide.clip(lower=1e-12))).sum(axis=1)/np.log(max(2,wide.shape[1]));ent=entropy.rename("value").reset_index()
    ecfg=dict(mc,title="Composition ambiguity (normalized entropy)",value_label="Normalized entropy",limits=[0,1])
    ent_rec=api["_render_style"]("mapping_composition_entropy","spatial",ent,ecfg,"advanced",out);records.append(ent_rec)
    panel=api["_contact_sheet"]("reference_to_space_panel",records[:4],out,2)
    if panel:records.append(panel)
    panel2=api["_contact_sheet"]("mapping_uncertainty_panel",[records[2],ent_rec],out,2)
    if panel2:records.append(panel2)
    return records,skipped


def render_marker_validation(inputs,config,out,api):
    markers=inputs["markers"].copy();sp=inputs["spatial"].copy();api["_validate_contract"](markers,"group_feature");api["_validate_contract"](sp,"spatial_point")
    if "fraction" not in markers:raise ValueError("cross-modal marker validation requires scRNA detection fraction")
    if not {"gene","value","group"}<=set(sp):raise ValueError("spatial marker input requires gene/value/group for regional validation")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(markers.group.astype(str)));features=list(dict.fromkeys(markers.feature.astype(str)))
    dot=markers[["group","feature","value","fraction"]].rename(columns={"value":"mean"});dc=dict(base,title="scRNA marker evidence",group_order=groups,feature_order=features,value_label=config.get("scrna_value_label","Mean expression"))
    records.append(api["_render_style"]("scrna_marker_dotplot","dotplot",dot,dc,"advanced",out))
    top=features[:int(config.get("max_spatial_markers",6))];maps=[]
    for gene in top:
        p=sp[sp.gene.astype(str)==str(gene)][["id","section","x","y","value"]].copy()
        if p.empty:continue
        for sec,g in p.groupby("section",sort=False):
            sc=dict(base,title=f"{gene} · {sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label=config.get("spatial_value_label","Spatial expression"),continuous_preset=config.get("continuous_preset","M02"))
            rec=api["_render_style"]("spatial_marker__"+api["_slug"](gene)+"__"+api["_slug"](sec),"spatial",g,sc,"advanced",out);maps.append(rec);records.append(rec)
    panel=api["_contact_sheet"]("spatial_marker_map",maps,out,2)
    if panel:records.append(panel)
    spatial_mean=sp.groupby(["group","gene"],sort=False).value.mean().rename("spatial").reset_index();scrna=markers.rename(columns={"feature":"gene","value":"scrna"})[["group","gene","scrna"]];joint=scrna.merge(spatial_mean,on=["group","gene"],how="inner")
    rhos=[]
    for gene,g in joint.groupby("gene",sort=False):
        if g.group.nunique()>=3 and g.scrna.std()>0 and g.spatial.std()>0:r=float(g[["scrna","spatial"]].corr(method="spearman").iloc[0,1])
        else:r=np.nan
        rhos.append((gene,r))
    rh=pd.DataFrame(rhos,columns=["feature","value"]).dropna();rh["group"]="Spearman rho"
    if len(rh):
        hc=dict(base,title="Cross-modal marker concordance",group_order=["Spearman rho"],feature_order=list(rh.feature),value_label="Spearman rho across shared groups",continuous_preset="D03",limits=[-1,1],norm="two_slope")
        records.append(api["_render_style"]("marker_concordance_heatmap","heatmap",rh[["group","feature","value"]],hc,"advanced",out))
    else:skipped.append({"target":"marker_concordance_heatmap","reason":"Fewer than three shared groups or zero variance for all marker genes."})
    p1=api["_contact_sheet"]("marker_validation_panel",[r for r in records if r["target"] in {"scrna_marker_dotplot","spatial_marker_map","marker_concordance_heatmap"}],out,2)
    if p1:records.append(p1)
    p2=api["_contact_sheet"]("cross_modal_evidence_panel",[r for r in records if r["target"] in {"scrna_marker_dotplot","marker_concordance_heatmap"}]+maps[:2],out,2)
    if p2:records.append(p2)
    return records,skipped


def render_lineage_progression(inputs,config,out,api):
    d=inputs["main"].copy();emb=inputs["embedding"].copy();api["_validate_contract"](d,"trajectory");api["_validate_contract"](emb,"embedding");records=[];skipped=[];base=api["_base_cfg"](config)
    if "group" not in emb:raise ValueError("development lineage embedding requires stage/state group")
    levels=list(dict.fromkeys(emb.group.astype(str)));ec=dict(base,title="Developmental states in embedding",group_order=levels,categorical_preset=config.get("categorical_preset","C19"),label_groups=levels[:14])
    records.append(api["_render_style"]("stage_embedding","embedding",emb[["id","x","y","group"]],ec,"advanced",out))
    if config.get("abstract_edges"):
        records.append(api["_render_style"]("lineage_tree","embedding",emb[["id","x","y","group"]],dict(ec,title="Declared developmental lineage",abstract_edges=config["abstract_edges"],edge_definition=config.get("edge_definition","Upstream lineage graph")),"advanced",out))
    else:skipped.append({"target":"lineage_tree","reason":"No supplied abstract_edges; lineage is never inferred from embedding geometry."})
    if {"feature","value"}<=set(d):
        th=d.dropna(subset=["feature","value"])[["feature","time","value"]].rename(columns={"feature":"gene"}).groupby(["gene","time"],sort=False).value.mean().reset_index()
        tc=dict(base,title="Developmental gene programmes",gene_order=list(dict.fromkeys(th.gene.astype(str))),value_label=config.get("value_label","Programme score"),continuous_preset=config.get("continuous_preset","D03"))
        records.append(api["_render_style"]("trajectory_heatmap","trajectory_heatmap",th,tc,"advanced",out))
    else:skipped.append({"target":"trajectory_heatmap","reason":"feature/value not supplied."})
    if {"state","lineage","probability"}<=set(d):
        fm=d.dropna(subset=["lineage","probability"]).groupby(["state","lineage"],sort=False).probability.mean().rename("value").reset_index().rename(columns={"state":"feature","lineage":"group"})
        hc=dict(base,title="State-to-lineage fate probability",group_order=list(dict.fromkeys(fm.group.astype(str))),feature_order=list(dict.fromkeys(fm.feature.astype(str))),value_label="Mean supplied probability",continuous_preset=config.get("continuous_preset","M02"),limits=[0,1],norm="linear")
        records.append(api["_render_style"]("fate_matrix","heatmap",fm,hc,"advanced",out))
    else:skipped.append({"target":"fate_matrix","reason":"lineage/probability not supplied."})
    panel=api["_contact_sheet"]("state_lineage_fate_gene_panel",records,out,2)
    if panel:records.append(panel)
    return records,skipped


def render_latent_embedding(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"embedding");records=[];skipped=[];base=api["_base_cfg"](config)
    if "group" not in d:raise ValueError("fm.latent_embedding requires group label")
    groups=list(dict.fromkeys(d.group.astype(str)));ec=dict(base,title="Foundation-model latent embedding",group_order=groups,categorical_preset=config.get("categorical_preset","C19"),label_groups=groups[:14])
    records.append(api["_render_style"]("latent_embedding","embedding",d[["id","x","y","group"]],ec,"minimal",out));records.append(api["_render_style"]("latent_by_label","embedding",d[["id","x","y","group"]],dict(ec,title="Latent space by biological label"),"advanced",out))
    if "batch" in d:
        b=d[["id","x","y","batch"]].rename(columns={"batch":"group"});bc=dict(base,title="Latent space by batch",group_order=list(dict.fromkeys(b.group.astype(str))),categorical_preset=config.get("batch_preset","C03"))
        records.append(api["_render_style"]("latent_by_batch","embedding",b,bc,"advanced",out))
    else:skipped.append({"target":"latent_by_batch","reason":"batch not supplied."})
    if "confidence" in d:
        records.append(api["_custom_figure"]("neighborhood_consistency",api["style_continuous_embedding"](d,"confidence","Neighborhood consistency","Supplied consistency score",config),out) if "style_continuous_embedding" in api else api["_custom_figure"])
    else:
        # Keep the target semantic explicit rather than inferring kNN purity inside a plotting layer.
        skipped.append({"target":"neighborhood_consistency","reason":"No upstream neighborhood-consistency/confidence score supplied."})
    panel=api["_contact_sheet"]("latent_structure_panel",records,out,2)
    if panel:records.append(panel)
    return records,skipped


def render_ablation_scaling(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"model_metric");records=[];skipped=[];base=api["_base_cfg"](config)
    metric=config.get("metric",str(d.metric.iloc[0]));p=d[d.metric.astype(str)==str(metric)].copy();methods=list(dict.fromkeys(p.method.astype(str)));datasets=list(dict.fromkeys(p.dataset.astype(str)))
    agg=p.groupby(["dataset","method"],sort=False).value.mean().rename("score").reset_index();bc=dict(base,title=f"Ablation comparison · {metric}",dataset_order=datasets,method_order=methods,baseline_method=config.get("baseline_method",methods[-1]),value_label=metric)
    records.append(api["_render_style"]("ablation_effect","benchmark",agg,bc,"advanced",out))
    if "compute" in p:
        def scaling():
            fig,ax=plt.subplots(figsize=(6.8,5.0),facecolor="white")
            for m,g in p.groupby("method",sort=False):
                q=g.groupby("compute").value.mean().sort_index();ax.plot(q.index,q.values,marker="o",lw=1.5,label=str(m))
            ax.set_xscale(config.get("compute_scale","log"));ax.set_xlabel(config.get("compute_label","Compute"));ax.set_ylabel(metric);ax.set_title("Scaling curve",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.legend(frameon=False);ax.spines[["top","right"]].set_visible(False);return fig
        records.append(api["_custom_figure"]("scaling_curve",scaling,out))
        def perf():
            fig,ax=plt.subplots(figsize=(6.6,5.0),facecolor="white");ax.scatter(p.compute,p.value,s=25,alpha=.65,c="#5E8795");ax.set_xscale(config.get("compute_scale","log"));ax.set_xlabel(config.get("compute_label","Compute"));ax.set_ylabel(metric);ax.set_title("Performance versus compute",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
        records.append(api["_custom_figure"]("performance_compute",perf,out))
    else:skipped += [{"target":"scaling_curve","reason":"compute not supplied."},{"target":"performance_compute","reason":"compute not supplied."}]
    cal_metric=config.get("calibration_metric")
    if cal_metric is not None and str(cal_metric) in set(d.metric.astype(str)):
        q=d[d.metric.astype(str)==str(cal_metric)].groupby("method").value.mean().sort_values()
        records.append(api["_custom_figure"]("calibration_shift",api["_rank_bar"](q.index,q.values,f"Calibration metric · {cal_metric}",str(cal_metric)),out))
    else:skipped.append({"target":"calibration_shift","reason":"Declare calibration_metric present in model_metric input."})
    panel=api["_contact_sheet"]("model_evaluation_panel",records,out,2)
    if panel:records.append(panel)
    return records,skipped


def render_spatial_communication(inputs,config,out,api):
    s=inputs["spatial"].copy();inter=inputs["interaction"].copy();api["_validate_contract"](s,"spatial_point");api["_validate_contract"](inter,"interaction");records=[];skipped=[];base=api["_base_cfg"](config)
    if "group" not in s:raise ValueError("spatial communication requires supplied cell/domain group labels")
    cent=s.drop_duplicates("id").groupby("group",sort=False)[["x","y"]].mean();h=inter.groupby(["source","target"],sort=False).score.sum().reset_index()
    def network():
        fig,ax=plt.subplots(figsize=(7,5.7),facecolor="white");levels=list(dict.fromkeys(s.group.astype(str)));pal=api["style_palette"](levels,{"categorical_preset":config.get("categorical_preset","C19"),"palette_order":levels});mx=max(h.score.max(),1e-12)
        for _,r in h.iterrows():
            if r.source not in cent.index or r.target not in cent.index:continue
            a=cent.loc[r.source];b=cent.loc[r.target];arrow=FancyArrowPatch((a.x,a.y),(b.x,b.y),arrowstyle="-|>",mutation_scale=8,lw=.5+3*r.score/mx,color=MUTED,alpha=.55);ax.add_patch(arrow)
        for g in levels:
            if g in cent.index:ax.scatter(cent.loc[g,"x"],cent.loc[g,"y"],s=85,c=pal[g],edgecolor="white",lw=.6,zorder=5);ax.text(cent.loc[g,"x"],cent.loc[g,"y"],g,fontsize=7,ha="center",va="bottom")
        ax.set_aspect("equal");ax.set_xlabel(f"x ({config.get('coordinate_unit','µm')})");ax.set_ylabel(f"y ({config.get('coordinate_unit','µm')})");ax.set_title("Spatially localized communication graph",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
    records.append(api["_custom_figure"]("spatial_network",network,out))
    hm=h.rename(columns={"source":"feature","target":"group","score":"value"});hc=dict(base,title="Spatial interaction matrix",group_order=list(dict.fromkeys(hm.group.astype(str))),feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label=config.get("score_label","Interaction score"),continuous_preset=config.get("continuous_preset","M02"))
    records.append(api["_render_style"]("spatial_interaction_heatmap","heatmap",hm,hc,"advanced",out))
    if "distance" in inter:
        def distplot():
            fig,ax=plt.subplots(figsize=(6.6,4.8),facecolor="white");ax.scatter(inter.distance,inter.score,s=20,c="#5E8795",alpha=.65);o=np.argsort(inter.distance.to_numpy());ax.plot(inter.distance.to_numpy()[o],pd.Series(inter.score.to_numpy()[o]).rolling(max(2,len(inter)//6),center=True,min_periods=1).mean(),c=INK,lw=1.2);ax.set_xlabel(config.get("distance_label","Distance"));ax.set_ylabel(config.get("score_label","Interaction score"));ax.set_title("Distance dependence of communication",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.spines[["top","right"]].set_visible(False);return fig
        records.append(api["_custom_figure"]("distance_response",distplot,out));records.append(api["_custom_figure"]("distance_dependence",distplot,out))
    else:skipped += [{"target":"distance_response","reason":"distance not supplied."},{"target":"distance_dependence","reason":"distance not supplied."}]
    lr_maps=[]
    if {"ligand","receptor"}<=set(inter) and {"gene","value"}<=set(s):
        top=inter.sort_values("score",ascending=False).iloc[0]
        for gene,label in [(top.ligand,"Ligand"),(top.receptor,"Receptor")]:
            p=s[s.gene.astype(str)==str(gene)][["id","section","x","y","value"]]
            if not p.empty:
                for sec,g in p.groupby("section",sort=False):
                    c=dict(base,title=f"{label}: {gene} · {sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label="Spatial expression",continuous_preset=config.get("continuous_preset","M02"));r=api["_render_style"]("spatial_lr__"+api["_slug"](label)+"__"+api["_slug"](sec),"spatial",g,c,"advanced",out);lr_maps.append(r);records.append(r)
        if lr_maps:
            p=api["_contact_sheet"]("spatial_lr_map",lr_maps,out,2);records.append(p) if p else None
            p=api["_contact_sheet"]("ligand_receptor_maps",lr_maps,out,2);records.append(p) if p else None
            p=api["_contact_sheet"]("spatial_lr_evidence",[records[0],records[1]]+lr_maps[:2],out,2);records.append(p) if p else None
    else:skipped += [{"target":"spatial_lr_map","reason":"ligand/receptor interaction fields and spatial gene/value rows are required."},{"target":"ligand_receptor_maps","reason":"Ligand/receptor localization unavailable."},{"target":"spatial_lr_evidence","reason":"Ligand/receptor localization unavailable."}]
    if "target_program" in inter:
        q=inter.groupby("target_program").score.sum().sort_values();prog=api["_custom_figure"]("spatial_target_program",api["_rank_bar"](q.index,q.values,"Spatial communication target programmes",config.get("score_label","Interaction score")),out);records.append(prog);p=api["_contact_sheet"]("spatial_target_program_panel",[records[0],records[1],prog],out,2);records.append(p) if p else None
    else:skipped.append({"target":"spatial_target_program_panel","reason":"target_program not supplied."})
    return records,skipped
