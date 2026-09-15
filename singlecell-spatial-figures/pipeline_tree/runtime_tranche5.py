"""Final executable tranche for pipeline modules not covered by earlier runtimes.

All functions consume upstream-reviewed result tables only. They never fit models,
choose biological thresholds, infer lineage, reconstruct segmentation, or invent
uncertainty. Every figure obeys the repository-wide no-subtitle rule.
"""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from scipy.stats import gaussian_kde

INK="#263641";MUTED="#65757F";GRID="#E6EBEE"


def _clean_axes(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(axis="y",color=GRID,lw=.5,zorder=0)


def _categorical_embedding(d,field,title,config,api):
    def maker():
        fig,ax=plt.subplots(figsize=(6.7,5.4),facecolor="white")
        levels=list(dict.fromkeys(d[field].astype(str)))
        pal=api["style_palette"](levels,{"categorical_preset":config.get("categorical_preset","C19"),"palette_order":levels})
        for g in levels:
            p=d[d[field].astype(str)==g]
            ax.scatter(p.x,p.y,s=config.get("point_area",7),c=pal[g],lw=0,alpha=.84,rasterized=True,label=g)
        ax.set_aspect("equal");ax.set_xticks([]);ax.set_yticks([])
        ax.set_xlabel(config.get("x_label","Embedding 1"));ax.set_ylabel(config.get("y_label","Embedding 2"))
        ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK)
        ax.legend(frameon=False,bbox_to_anchor=(1.02,1),loc="upper left",fontsize=7)
        return fig
    return maker


def _continuous_embedding(d,field,title,label,config,api,signed=False):
    def maker():
        fig,ax=plt.subplots(figsize=(6.7,5.4),facecolor="white")
        v=pd.to_numeric(d[field],errors="raise").to_numpy(float);finite=v[np.isfinite(v)]
        if not len(finite):raise ValueError(f"{field}: no finite values")
        if signed:
            mx=max(abs(float(finite.min())),abs(float(finite.max())),1e-9);norm=plt.Normalize(-mx,mx);cm=plt.get_cmap("coolwarm")
        else:
            lo=float(finite.min());hi=float(finite.max()) if finite.max()>finite.min() else lo+1;norm=plt.Normalize(lo,hi);cm=plt.get_cmap("viridis")
        im=ax.scatter(d.x,d.y,c=v,s=config.get("point_area",7),cmap=cm,norm=norm,lw=0,alpha=.88,rasterized=True)
        ax.set_aspect("equal");ax.set_xticks([]);ax.set_yticks([])
        ax.set_xlabel(config.get("x_label","Embedding 1"));ax.set_ylabel(config.get("y_label","Embedding 2"))
        ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK)
        cb=fig.colorbar(im,ax=ax,fraction=.05,pad=.03);cb.set_label(label);return fig
    return maker


def _scatter_xy(x,y,title,xlabel,ylabel,config=None,identity=False):
    def maker():
        fig,ax=plt.subplots(figsize=(5.8,5.1),facecolor="white");ax.scatter(x,y,s=18,c="#5E8795",alpha=.72,lw=0)
        if identity:
            lo=min(float(np.nanmin(x)),float(np.nanmin(y)));hi=max(float(np.nanmax(x)),float(np.nanmax(y)));ax.plot([lo,hi],[lo,hi],c=MUTED,lw=.8,ls="--")
        ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK);_clean_axes(ax);return fig
    return maker


def _scree(pca):
    def maker():
        p=pca.sort_values("component");fig,ax=plt.subplots(figsize=(6.2,4.6),facecolor="white")
        ax.bar(p.component.astype(str),p.variance_ratio*100,color="#668E9C",width=.74);ax.plot(np.arange(len(p)),p.variance_ratio.to_numpy()*100,color=INK,lw=1,marker="o",ms=3)
        ax.set_ylabel("Explained variance (%)");ax.set_xlabel("Principal component");ax.set_title("PCA variance structure",loc="left",fontsize=11.5,fontweight="bold",color=INK);_clean_axes(ax);return fig
    return maker


def render_normalization_hvg(inputs,config,out,api):
    f=inputs["features"].copy();dist=inputs["distribution"].copy();api["_validate_contract"](f,"feature_variability");api["_validate_contract"](dist,"sample_value")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(dist.group.astype(str)))
    dd=dist[["id","group","value"]+(["condition"] if "condition" in dist else [])].copy();dc=dict(base,title="Normalized expression distribution",group_order=groups,value_label=config.get("value_label","Normalized value"))
    records.append(api["_render_style"]("normalized_distribution","distribution",dd,dc,"minimal",out))
    def mv():
        fig,ax=plt.subplots(figsize=(5.8,5.0),facecolor="white");sel=f.selected.astype(bool)
        ax.scatter(f.loc[~sel,"mean"],f.loc[~sel,"variance"],s=10,c="#C8D1D5",lw=0,alpha=.65,label="Not selected");ax.scatter(f.loc[sel,"mean"],f.loc[sel,"variance"],s=13,c="#4D8598",lw=0,alpha=.85,label="Selected")
        ax.set_xlabel("Mean");ax.set_ylabel("Variance");ax.set_title("Feature variability selection",loc="left",fontsize=11.5,fontweight="bold",color=INK);ax.legend(frameon=False);_clean_axes(ax);return fig
    records.append(api["_custom_figure"]("hvg_mean_variance",mv,out));rank=f.copy()
    if "rank" not in rank:rank["rank"]=rank["variance"].rank(method="first",ascending=False)
    rr=rank.sort_values("rank").head(int(config.get("top_hvg",30)));records.append(api["_custom_figure"]("hvg_rank",api["_rank_bar"](rr.feature,-rr["rank"],"Highly variable feature ranking","Higher rank → right"),out))
    if "condition" in dist:
        tmp=dist[["id","condition","value"]].rename(columns={"condition":"group"});cc=dict(base,title="Normalization before/after comparison",group_order=list(dict.fromkeys(tmp.group.astype(str))),value_label=config.get("value_label","Normalized value"));records.append(api["_render_style"]("normalization_before_after","distribution",tmp,cc,"advanced",out))
    else:skipped.append({"target":"normalization_before_after","reason":"distribution.condition (e.g. before/after) not supplied."})
    def annotated_rank():
        fig,ax=plt.subplots(figsize=(7.0,4.8),facecolor="white");p=rank.sort_values("rank").head(int(config.get("annotate_hvg",25))).copy();x=np.arange(len(p));ax.bar(x,p.variance,color=["#4D8598" if bool(v) else "#C8D1D5" for v in p.selected]);ax.set_xticks(x,p.feature.astype(str),rotation=55,ha="right",fontsize=7);ax.set_ylabel("Variance");ax.set_title("Top variable features",loc="left",fontsize=11.5,fontweight="bold",color=INK);_clean_axes(ax);return fig
    records.append(api["_custom_figure"]("hvg_rank_annotated",annotated_rank,out))
    if "batch" in f:
        u=f[f.selected.astype(bool)][["feature","batch"]].drop_duplicates().rename(columns={"feature":"item","batch":"set"})
        if len(u):
            uc=dict(base,title="Selected-feature overlap across batches",set_order=list(dict.fromkeys(u["set"].astype(str))),allow_top_k=True,max_intersections=20);records.append(api["_render_style"]("hvg_overlap_by_batch","upset",u,uc,"advanced",out))
        else:skipped.append({"target":"hvg_overlap_by_batch","reason":"No selected features in batch-resolved input."})
    else:skipped.append({"target":"hvg_overlap_by_batch","reason":"feature_variability.batch not supplied."})
    return records,skipped


def render_integration(inputs,config,out,api):
    pca=inputs["pca"].copy();pre=inputs["pre"].copy();post=inputs["post"].copy();api["_validate_contract"](pca,"pca_component");api["_validate_contract"](pre,"embedding");api["_validate_contract"](post,"embedding")
    records=[];skipped=[];records.append(api["_custom_figure"]("pca_scree",_scree(pca),out));prefield="group" if "group" in pre else "sample" if "sample" in pre else None
    if prefield is None:raise ValueError("integration pre embedding needs group or sample labels")
    records.append(api["_custom_figure"]("pca_embedding",_categorical_embedding(pre,prefield,"Pre-integration PCA / embedding",config,api),out))
    for field,target,title in [("sample","embedding_by_sample","Integrated embedding by sample"),("batch","embedding_by_batch","Integrated embedding by batch"),("condition","embedding_by_condition","Integrated embedding by condition")]:
        if field in post:records.append(api["_custom_figure"](target,_categorical_embedding(post,field,title,config,api),out))
        else:skipped.append({"target":target,"reason":f"post.{field} not supplied."})
    if "batch" in pre and "batch" in post:
        r1=api["_custom_figure"]("integration_pre_batch",_categorical_embedding(pre,"batch","Before integration",config,api),out);records.append(r1);r2=api["_custom_figure"]("integration_post_batch",_categorical_embedding(post,"batch","After integration",config,api),out);records.append(r2);p=api["_contact_sheet"]("integration_before_after",[r1,r2],out,2);records.append(p) if p else None
    else:skipped.append({"target":"integration_before_after","reason":"batch labels required in pre and post embeddings."})
    if "confidence" in post:records.append(api["_custom_figure"]("batch_mixing_diagnostic",_continuous_embedding(post,"confidence","Supplied integration mixing diagnostic",config.get("mixing_label","Supplied mixing/quality score"),config,api),out))
    else:skipped.append({"target":"batch_mixing_diagnostic","reason":"No upstream mixing/quality score supplied as post.confidence."})
    if "group" in pre and "group" in post:
        r1=api["_custom_figure"]("celltype_preservation_pre",_categorical_embedding(pre,"group","Identity before integration",config,api),out);records.append(r1);r2=api["_custom_figure"]("celltype_preservation_post",_categorical_embedding(post,"group","Identity after integration",config,api),out);records.append(r2);p=api["_contact_sheet"]("celltype_preservation",[r1,r2],out,2);records.append(p) if p else None
    else:skipped.append({"target":"celltype_preservation","reason":"group labels required in pre and post embeddings."})
    p=api["_contact_sheet"]("latent_space_qc_panel",[r for r in records if r["target"] in {"integration_before_after","batch_mixing_diagnostic","celltype_preservation"}],out,2);records.append(p) if p else None
    return records,skipped


def render_clustering(inputs,config,out,api):
    d=inputs["main"].copy();res=inputs["resolution"].copy();api["_validate_contract"](d,"embedding");api["_validate_contract"](res,"model_metric")
    if "group" not in d:raise ValueError("clustering embedding requires group")
    records=[];skipped=[];base=api["_base_cfg"](config);groups=list(dict.fromkeys(d.group.astype(str)));ec=dict(base,title="Cluster embedding",group_order=groups,categorical_preset=config.get("categorical_preset","C19"),label_groups=groups)
    records.append(api["_render_style"]("cluster_embedding","embedding",d[["id","x","y","group"]],ec,"minimal",out));counts=d.group.astype(str).value_counts().reindex(groups);records.append(api["_custom_figure"]("cluster_size",api["_rank_bar"](counts.index,counts.values,"Cluster sizes","Cells / observations"),out))
    metric=config.get("resolution_metric",str(res.metric.iloc[0]));rr=res[res.metric.astype(str)==metric].copy();
    if rr.empty:raise ValueError("resolution_metric absent from resolution table")
    rr=rr.groupby(["dataset","method"],as_index=False).value.mean().rename(columns={"value":"score"});bc=dict(base,title=f"Resolution comparison · {metric}",dataset_order=list(dict.fromkeys(rr.dataset.astype(str))),method_order=list(dict.fromkeys(rr.method.astype(str))),value_label=metric,baseline_method=config.get("baseline_resolution",str(rr.method.iloc[0])));records.append(api["_render_style"]("resolution_comparison","benchmark",rr,bc,"advanced",out));records.append(api["_render_style"]("cluster_centroid_labels","embedding",d[["id","x","y","group"]],dict(ec,title="Cluster identities",label_groups=groups),"advanced",out))
    def density():
        fig,ax=plt.subplots(figsize=(6.7,5.4),facecolor="white");pal=api["style_palette"](groups,{"categorical_preset":config.get("categorical_preset","C19"),"palette_order":groups})
        for g in groups:
            p=d[d.group.astype(str)==g];ax.scatter(p.x,p.y,s=4,c=pal[g],alpha=.22,lw=0,rasterized=True)
            if len(p)>10 and np.std(p.x)>0 and np.std(p.y)>0:
                xy=np.vstack([p.x,p.y]);k=gaussian_kde(xy);xx,yy=np.mgrid[p.x.min():p.x.max():40j,p.y.min():p.y.max():40j];zz=k(np.vstack([xx.ravel(),yy.ravel()])).reshape(xx.shape);ax.contour(xx,yy,zz,levels=3,colors=[pal[g]],linewidths=.8,alpha=.9)
        ax.set_aspect("equal");ax.set_xticks([]);ax.set_yticks([]);ax.set_title("Cluster density contours",loc="left",fontsize=11.5,fontweight="bold",color=INK);return fig
    records.append(api["_custom_figure"]("cluster_density_contours",density,out))
    if "parent" in d:
        def hierarchy():
            pairs=d[["group","parent"]].drop_duplicates();parents=list(dict.fromkeys(pairs.parent.astype(str)));children=list(dict.fromkeys(pairs.group.astype(str)));fig,ax=plt.subplots(figsize=(7.2,max(4,.35*len(children)+1.5)),facecolor="white");py={p:i for i,p in enumerate(parents)};cy={c:i for i,c in enumerate(children)}
            for row in pairs.itertuples():ax.add_patch(FancyArrowPatch((0,py[str(row.parent)]),(1,cy[str(row.group)]),arrowstyle="-",lw=1,color="#91A4AD",alpha=.65))
            for p,y in py.items():ax.text(-.05,y,p,ha="right",va="center",weight="bold",color=INK)
            for c,y in cy.items():ax.text(1.05,y,c,ha="left",va="center",color=INK)
            ax.set_xlim(-.5,1.5);ax.set_ylim(-.7,max(len(parents),len(children))-.3);ax.axis("off");ax.set_title("Supplied cluster hierarchy",loc="left",fontsize=11.5,fontweight="bold",color=INK);return fig
        records.append(api["_custom_figure"]("cluster_hierarchy",hierarchy,out))
    else:skipped.append({"target":"cluster_hierarchy","reason":"No supplied parent hierarchy."})
    if "sample" in d:
        tab=d.groupby(["sample","group"]).size().rename("n").reset_index();tab["fraction"]=tab.n/tab.groupby("sample").n.transform("sum");cc=dict(base,title="Cluster composition by sample",sample_order=list(dict.fromkeys(tab["sample"].astype(str))),group_order=groups,categorical_preset=config.get("categorical_preset","C19"));records.append(api["_render_style"]("cluster_sample_composition","composition",tab[["sample","group","fraction"]],cc,"advanced",out))
    else:skipped.append({"target":"cluster_sample_composition","reason":"sample identity not supplied."})
    return records,skipped


def render_velocity_fate(inputs,config,out,api):
    v=inputs["velocity"].copy();f=inputs["fate"].copy();drivers=inputs["drivers"].copy();api["_validate_contract"](v,"velocity_point");api["_validate_contract"](f,"fate_probability");api["_validate_contract"](drivers,"group_feature")
    records=[];skipped=[];base=api["_base_cfg"](config)
    def quiver(title,dense=False):
        def maker():
            fig,ax=plt.subplots(figsize=(6.7,5.5),facecolor="white");step=max(1,int(len(v)/(450 if dense else 220)));q=v.iloc[::step];ax.scatter(v.x,v.y,s=3,c="#CBD4D8",lw=0,alpha=.45,rasterized=True);ax.quiver(q.x,q.y,q.vx,q.vy,angles="xy",scale_units="xy",scale=config.get("velocity_scale",8),width=.0022,color="#4E7F90",alpha=.72);ax.set_aspect("equal");ax.set_xticks([]);ax.set_yticks([]);ax.set_title(title,loc="left",fontsize=11.5,fontweight="bold",color=INK);return fig
        return maker
    records.append(api["_custom_figure"]("velocity_embedding",quiver("RNA velocity field",False),out));records.append(api["_custom_figure"]("velocity_stream",quiver("Velocity direction field",True),out))
    if "latent_time" in v:records.append(api["_custom_figure"]("latent_time",_continuous_embedding(v,"latent_time","Latent time",config.get("latent_time_label","Supplied latent time"),config,api),out))
    else:skipped.append({"target":"latent_time","reason":"velocity.latent_time not supplied."})
    states=list(dict.fromkeys(f.state.astype(str)));sel=str(config.get("fate_state",states[0]));pf=f[f.state.astype(str)==sel][["id","probability"]].merge(v[["id","x","y"]],on="id",how="inner")
    if len(pf):records.append(api["_custom_figure"]("fate_probability",_continuous_embedding(pf,"probability",f"Fate probability · {sel}","Supplied fate probability",config,api),out))
    else:skipped.append({"target":"fate_probability","reason":"No matching fate rows for selected fate_state."})
    wide=f.pivot_table(index="id",columns="state",values="probability",aggfunc="first");term=wide.idxmax(axis=1).rename("terminal").reset_index().merge(v[["id","x","y"]],on="id",how="inner");records.append(api["_custom_figure"]("terminal_states",_categorical_embedding(term,"terminal","Most probable supplied fate",config,api),out));records.append(api["_custom_figure"]("terminal_fate_map",_categorical_embedding(term,"terminal","Terminal fate map",config,api),out))
    if "group" in f:
        mat=f.groupby(["group","state"],as_index=False).probability.mean().rename(columns={"state":"feature","probability":"value"});hc=dict(base,title="Mean fate probabilities by supplied group",group_order=list(dict.fromkeys(mat.group.astype(str))),feature_order=states,value_label="Mean supplied probability",continuous_preset="M02",limits=[0,1],norm="linear");records.append(api["_render_style"]("fate_matrix","heatmap",mat,hc,"advanced",out))
    else:skipped.append({"target":"fate_matrix","reason":"fate.group not supplied."})
    hc=dict(base,title="Lineage driver programmes",group_order=list(dict.fromkeys(drivers.group.astype(str))),feature_order=list(dict.fromkeys(drivers.feature.astype(str))),value_label=config.get("driver_label","Driver score"),continuous_preset="D03");records.append(api["_render_style"]("lineage_driver_heatmap","heatmap",drivers[["group","feature","value"]],hc,"advanced",out));p=api["_contact_sheet"]("velocity_fate_panel",[r for r in records if r["target"] in {"velocity_embedding","latent_time","fate_probability","lineage_driver_heatmap"}],out,2);records.append(p) if p else None
    return records,skipped


def render_perturbation_prediction(inputs,config,out,api):
    pred=inputs["prediction"].copy();eff=inputs["effect"].copy();emb=inputs["embedding"].copy();api["_validate_contract"](pred,"prediction");api["_validate_contract"](eff,"effect");api["_validate_contract"](emb,"embedding")
    records=[];skipped=[];base=api["_base_cfg"](config);field="condition" if "condition" in emb else "group" if "group" in emb else None
    if field:records.append(api["_custom_figure"]("response_embedding",_categorical_embedding(emb,field,"Perturbation response embedding",config,api),out))
    else:skipped.append({"target":"response_embedding","reason":"embedding condition/group label not supplied."})
    if {"lower","upper"}<=set(eff):
        ff=eff.dropna(subset=["lower","upper"]).copy();ff["term"]=ff.feature;fc=dict(base,title="Perturbation effects",term_order=list(dict.fromkeys(ff.term.astype(str))),effect_label=config.get("effect_label","Effect"),interval_label=config.get("interval_label","Supplied interval"));records.append(api["_render_style"]("perturbation_effect","forest",ff[["term","effect","lower","upper"]].rename(columns={"effect":"estimate"}),fc,"advanced",out))
    else:records.append(api["_custom_figure"]("perturbation_effect",api["_rank_bar"](eff.feature,eff.effect,"Perturbation effects",config.get("effect_label","Effect")),out))
    records.append(api["_custom_figure"]("observed_predicted",_scatter_xy(pred.observed,pred.predicted,"Observed versus predicted","Observed","Predicted",config,True),out));res=pred["residual"] if "residual" in pred else pred.observed-pred.predicted;records.append(api["_custom_figure"]("residual",_scatter_xy(pred.predicted,res,"Prediction residuals","Predicted",config.get("residual_label","Observed − predicted"),config,False),out));p=api["_contact_sheet"]("perturbation_landscape",[r for r in records if r["target"] in {"response_embedding","perturbation_effect","observed_predicted","residual"}],out,2);records.append(p) if p else None
    if {"group","feature"}<=set(pred):
        hm=pred.assign(_residual=res).groupby(["group","feature"],as_index=False)._residual.mean().rename(columns={"_residual":"value"});mx=max(abs(hm.value.min()),abs(hm.value.max()),1e-9);hc=dict(base,title="Residual structure by group and feature",group_order=list(dict.fromkeys(hm.group.astype(str))),feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label=config.get("residual_label","Observed − predicted"),continuous_preset="D03",limits=[-mx,mx],norm="two_slope");records.append(api["_render_style"]("residual_heatmap","heatmap",hm,hc,"advanced",out))
    else:skipped.append({"target":"residual_heatmap","reason":"prediction group/feature fields not supplied."})
    if config.get("prediction_type")=="probability":
        bins=pd.cut(pred.predicted,np.linspace(0,1,11),include_lowest=True,duplicates="drop");cal=pred.assign(_bin=bins).groupby("_bin",observed=True).agg(predicted=("predicted","mean"),observed=("observed","mean"),n=("id","count")).reset_index(drop=True);cal["model"]=config.get("model_name","Model");cal["bin"]=np.arange(len(cal));records.append(api["_render_style"]("prediction_calibration","calibration",cal[["model","bin","predicted","observed","n"]],dict(base,title="Perturbation prediction calibration"),"advanced",out))
    else:skipped.append({"target":"prediction_calibration","reason":"Set prediction_type='probability' for calibration."})
    p=api["_contact_sheet"]("perturbation_response_panel",[r for r in records if r["target"] in {"response_embedding","perturbation_effect","residual_heatmap","prediction_calibration"}],out,2);records.append(p) if p else None;return records,skipped


def render_spatial_normalization_embedding(inputs,config,out,api):
    sp=inputs["spatial"].copy();feat=inputs["features"].copy();emb=inputs["embedding"].copy();api["_validate_contract"](sp,"spatial_point");api["_validate_contract"](feat,"feature_variability");api["_validate_contract"](emb,"embedding")
    if "value" not in sp:raise ValueError("spatial normalization runtime requires spatial.value")
    records=[];skipped=[];base=api["_base_cfg"](config);dd=sp[["id","section","value"]].rename(columns={"section":"group"});groups=list(dict.fromkeys(dd.group.astype(str)));dc=dict(base,title="Normalized spatial values by section",group_order=groups,value_label=config.get("value_label","Normalized value"));records.append(api["_render_style"]("spatial_normalized_distribution","distribution",dd,dc,"advanced",out))
    def scatter():
        fig,ax=plt.subplots(figsize=(5.8,5.0),facecolor="white");sel=feat.selected.astype(bool);ax.scatter(feat.loc[~sel,"mean"],feat.loc[~sel,"variance"],s=10,c="#CCD5D9",lw=0,alpha=.6);ax.scatter(feat.loc[sel,"mean"],feat.loc[sel,"variance"],s=14,c="#4D8598",lw=0,alpha=.85);ax.set_xlabel("Mean");ax.set_ylabel("Variance");ax.set_title("Spatial variable-feature selection",loc="left",fontsize=11.5,fontweight="bold",color=INK);_clean_axes(ax);return fig
    records.append(api["_custom_figure"]("spatial_hvg_svg_scatter",scatter,out));field="section" if "section" in emb else "group" if "group" in emb else None
    if field:records.append(api["_custom_figure"]("section_embedding",_categorical_embedding(emb,field,"Spatial latent embedding by section",config,api),out))
    else:skipped.append({"target":"section_embedding","reason":"embedding section/group labels not supplied."})
    records.append(api["_render_style"]("section_normalization_diagnostic","distribution",dd,dict(dc,title="Section normalization diagnostic"),"advanced",out))
    if "confidence" in emb:records.append(api["_custom_figure"]("latent_spatial_consistency",_continuous_embedding(emb,"confidence","Supplied latent–spatial consistency",config.get("consistency_label","Supplied consistency score"),config,api),out))
    else:skipped.append({"target":"latent_spatial_consistency","reason":"No upstream consistency score supplied as embedding.confidence."})
    return records,skipped


def render_multisection(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"spatial_point")
    if "value" not in d:raise ValueError("multisection requires spatial.value")
    records=[];skipped=[];base=api["_base_cfg"](config);sections=list(dict.fromkeys(d.section.astype(str)));gene=config.get("gene");use=d
    if "gene" in d:
        genes=list(dict.fromkeys(d.gene.astype(str)));gene=str(gene or genes[0]);use=d[d.gene.astype(str)==gene]
    maps=[]
    for sec,g in use.groupby("section",sort=False):
        p=g[["id","section","x","y","value"]].copy();c=dict(base,title=f"{gene+' · ' if gene else ''}{sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label=config.get("value_label","Spatial value"),continuous_preset=config.get("continuous_preset","M02"),invert_y=bool(config.get("invert_y",False)));r=api["_render_style"]("section__"+api["_slug"](sec),"spatial",p,c,"advanced",out);maps.append(r);records.append(r)
    for target in ["section_small_multiples","aligned_feature_maps","aligned_atlas_panel"]:
        p=api["_contact_sheet"](target,maps,out,min(3,max(1,len(maps))));records.append(p) if p else None
    if "group" in use:
        hm=use.groupby(["section","group"],as_index=False).value.mean().rename(columns={"section":"group","group":"feature"});hc=dict(base,title="Region comparison across sections",group_order=sections,feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label=config.get("value_label","Mean spatial value"),continuous_preset="M02");records.append(api["_render_style"]("region_comparison_heatmap","heatmap",hm,hc,"advanced",out))
    else:skipped.append({"target":"region_comparison_heatmap","reason":"No supplied region/group labels."})
    def variability():
        s=use.groupby("section").value.agg(["mean","std"]).reindex(sections);fig,ax=plt.subplots(figsize=(6.5,4.6),facecolor="white");x=np.arange(len(s));ax.errorbar(x,s["mean"],yerr=s["std"].fillna(0),fmt="o",c="#4D8598",ecolor="#8199A3",capsize=3);ax.set_xticks(x,s.index,rotation=45,ha="right");ax.set_ylabel(config.get("value_label","Spatial value"));ax.set_title("Section-to-section variability",loc="left",fontsize=11.5,fontweight="bold",color=INK);_clean_axes(ax);return fig
    records.append(api["_custom_figure"]("section_variability_panel",variability,out))
    if "group" in use:
        p=api["_contact_sheet"]("cross_sample_summary",[r for r in records if r["target"] in {"region_comparison_heatmap","section_variability_panel"}],out,2);records.append(p) if p else None
    else:skipped.append({"target":"cross_sample_summary","reason":"No supplied region/group labels."})
    return records,skipped


def render_histology_morphology(inputs,config,out,api):
    d=inputs["main"].copy();img=inputs["image"].copy();api["_validate_contract"](d,"morphology_point");api["_validate_contract"](img,"image_pixel");records=[];skipped=[]
    def image_overlay():
        fig,ax=plt.subplots(figsize=(6.8,5.5),facecolor="white");ax.scatter(img.x,img.y,c=img.intensity,s=config.get("image_pixel_area",12),cmap="gray",lw=0,rasterized=True);ax.scatter(d.x,d.y,c=d.transcript_value,s=14,cmap="viridis",lw=0,alpha=.72,rasterized=True);ax.set_aspect("equal");ax.set_title("Supplied histology/image intensity with transcript overlay",loc="left",fontsize=11.5,fontweight="bold",color=INK)
        if config.get("invert_y"):ax.invert_yaxis()
        return fig
    records.append(api["_custom_figure"]("histology_overlay",image_overlay,out))
    if "vertices" in d:
        temp=d[["id","section","x","y","transcript_value","vertices"]].rename(columns={"transcript_value":"value"});c=dict(api["_base_cfg"](config),title="Supplied segmentation map",coordinate_unit=config.get("coordinate_unit","µm"),value_label="Transcript value",continuous_preset="M02");records.append(api["_render_style"]("segmentation_map","spatial",temp,c,"advanced",out))
    else:skipped.append({"target":"segmentation_map","reason":"Supplied segmentation vertices not present."})
    temp=d[["id","section","x","y","morphology_value"]].rename(columns={"morphology_value":"value"});c=dict(api["_base_cfg"](config),title="Morphology feature map",coordinate_unit=config.get("coordinate_unit","µm"),value_label=config.get("morphology_label","Morphology feature"),continuous_preset="M02");records.append(api["_render_style"]("morphology_feature_map","spatial",temp,c,"advanced",out));records.append(api["_custom_figure"]("transcript_image_scatter",_scatter_xy(d.morphology_value,d.transcript_value,"Morphology–transcript association",config.get("morphology_label","Morphology feature"),config.get("transcript_label","Transcript value"),config,False),out))
    for target,sel,cols in [("image_segmentation_expression_composite",{"histology_overlay","segmentation_map","morphology_feature_map"},3),("morphology_transcript_panel",{"morphology_feature_map","transcript_image_scatter"},2)]:
        p=api["_contact_sheet"](target,[r for r in records if r["target"] in sel],out,cols);records.append(p) if p else None
    if config.get("zoom_box"):
        box=list(map(float,config["zoom_box"]));
        if len(box)!=4:raise ValueError("zoom_box must be [xmin,xmax,ymin,ymax]")
        def zoom():
            fig=image_overlay();ax=fig.axes[0];ax.set_xlim(box[0],box[1]);ax.set_ylim(box[2],box[3]);ax.set_title("Declared region zoom",loc="left",fontsize=11.5,fontweight="bold",color=INK);return fig
        records.append(api["_custom_figure"]("region_zoom_evidence",zoom,out))
    else:skipped.append({"target":"region_zoom_evidence","reason":"No explicit zoom_box supplied."})
    return records,skipped


def render_niche_validation(inputs,config,out,api):
    sp=inputs["spatial"].copy();act=inputs["activity"].copy();api["_validate_contract"](sp,"spatial_point");api["_validate_contract"](act,"group_feature")
    if "niche" not in sp or "group" not in sp:raise ValueError("niche validation requires spatial.niche and spatial.group")
    records=[];skipped=[];base=api["_base_cfg"](config);records.append(api["_custom_figure"]("niche_map",api["_categorical_spatial"](sp,"niche",config,"Spatial niche assignment"),out))
    if "state_abundance" in sp:
        temp=sp[["id","section","x","y","state_abundance"]].rename(columns={"state_abundance":"value"});c=dict(base,title="Mapped state abundance",coordinate_unit=config.get("coordinate_unit","µm"),value_label=config.get("state_abundance_label","Supplied state abundance"),continuous_preset="M02");records.append(api["_render_style"]("state_abundance_map","spatial",temp,c,"advanced",out))
    else:records.append(api["_custom_figure"]("state_abundance_map",api["_categorical_spatial"](sp,"group",config,"Mapped cell state identity"),out))
    if not config.get("rows_are_cells",False):skipped.append({"target":"state_niche_heatmap","reason":"Set rows_are_cells=true only when each spatial row is an individual cell/observation suitable for composition counting."})
    else:
        tab=sp.groupby(["niche","group"]).size().rename("n").reset_index();tab["value"]=tab.n/tab.groupby("niche").n.transform("sum");hm=tab.rename(columns={"niche":"group","group":"feature"})[["group","feature","value"]];hc=dict(base,title="Observed cell-state composition within niches",group_order=list(dict.fromkeys(hm.group.astype(str))),feature_order=list(dict.fromkeys(hm.feature.astype(str))),value_label="Observed row fraction",continuous_preset="M02",limits=[0,1],norm="linear");records.append(api["_render_style"]("state_niche_heatmap","heatmap",hm,hc,"advanced",out))
    p=api["_contact_sheet"]("niche_state_panel",[r for r in records if r["target"] in {"niche_map","state_abundance_map","state_niche_heatmap"}],out,2);records.append(p) if p else None
    if len(act):
        hc=dict(base,title="Local pathway / programme support",group_order=list(dict.fromkeys(act.group.astype(str))),feature_order=list(dict.fromkeys(act.feature.astype(str))),value_label=config.get("activity_label","Activity score"),continuous_preset="D03");records.append(api["_render_style"]("local_pathway_support","heatmap",act[["group","feature","value"]],hc,"advanced",out))
    else:skipped.append({"target":"local_pathway_support","reason":"No activity rows supplied."})
    return records,skipped


def render_communication_validation(inputs,config,out,api):
    comm=inputs["communication"].copy();sp=inputs["spatial"].copy();con=inputs["concordance"].copy();api["_validate_contract"](comm,"interaction");api["_validate_contract"](sp,"spatial_point");api["_validate_contract"](con,"concordance_pair")
    records=[];skipped=[];base=api["_base_cfg"](config);nn=comm.groupby(["source","target"],as_index=False).score.mean().rename(columns={"score":"weight"});nc=dict(base,title="scRNA communication network",edge_unit=config.get("edge_unit","Interaction score"),categorical_preset=config.get("categorical_preset","C19"));records.append(api["_render_style"]("scrna_communication_network","network",nn,nc,"advanced",out));selected=None
    if {"ligand","receptor"}<=set(comm):
        row=comm.sort_values("score",ascending=False).iloc[0];selected=(str(row.ligand),str(row.receptor))
    if selected and {"gene","value"}<=set(sp):
        maps=[]
        for gene in selected:
            p=sp[sp.gene.astype(str)==gene][["id","section","x","y","value"]]
            for sec,g in p.groupby("section",sort=False):
                c=dict(base,title=f"{gene} · {sec}",coordinate_unit=config.get("coordinate_unit","µm"),value_label="Spatial expression",continuous_preset="M02");r=api["_render_style"]("spatial_localization__"+api["_slug"](gene)+"__"+api["_slug"](sec),"spatial",g,c,"advanced",out);records.append(r);maps.append(r)
        p=api["_contact_sheet"]("spatial_localization",maps,out,2);records.append(p) if p else None
    else:skipped.append({"target":"spatial_localization","reason":"Communication ligand/receptor and spatial gene/value rows are required."})
    records.append(api["_custom_figure"]("lr_concordance",_scatter_xy(con.scrna_score,con.spatial_score,"Cross-modal LR concordance","scRNA score","Spatial score",config,True),out));p=api["_contact_sheet"]("communication_triangulation",[r for r in records if r["target"] in {"scrna_communication_network","spatial_localization","lr_concordance"}],out,2);records.append(p) if p else None
    if "pathway" in comm and selected:
        p=api["_contact_sheet"]("pathway_localization_panel",[r for r in records if r["target"] in {"scrna_communication_network","spatial_localization"}],out,2);records.append(p) if p else None
    else:skipped.append({"target":"pathway_localization_panel","reason":"Pathway annotation or localized LR pair unavailable."})
    return records,skipped
