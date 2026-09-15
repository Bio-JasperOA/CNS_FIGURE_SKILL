"""Deterministic fixtures for executable runtime tranche 4."""
from __future__ import annotations
import numpy as np
import pandas as pd
RNG=np.random.default_rng(3152615)


def pathway_activity():
    groups=["Progenitor","Epithelial","Mesenchymal"];features=["WNT","TGFb","MYC","p53"];rows=[]
    for gi,g in enumerate(groups):
        for fi,f in enumerate(features):rows.append((g,f,float(np.sin(gi+fi*.6)),"Signaling" if f in {"WNT","TGFb"} else "Regulatory"))
    activity=pd.DataFrame(rows,columns=["group","feature","value","module"])
    enrichment=pd.DataFrame({"term":["WNT signaling","TGF-beta response","Cell cycle","Stress response"],"effect":[1.4,.9,-.8,.55],"q":[.002,.01,.03,.08],"count":[18,14,11,9]})
    rank=np.arange(1,81);metric=np.linspace(2,-2,80);run=np.sin(np.linspace(0,np.pi,80))*.9-.15;hits=np.zeros(80,int);hits[[4,9,16,28,45,63]]=1
    gsea=pd.DataFrame({"rank":rank,"running_score":run,"hit":hits,"rank_metric":metric,"term":"WNT signaling","feature":[f"G{i}" for i in rank],"leading_edge":[i<30 and h==1 for i,h in enumerate(hits)]})
    return {"activity":activity,"enrichment":enrichment,"gsea":gsea},{"demo":True,"gsea_term":"WNT signaling","activity_label":"Activity score"}


def regulon_module():
    groups=["Prog","Epi","Mes"];regs=["SOX2","GATA6","TEAD4","MYC"];rows=[]
    for gi,g in enumerate(groups):
        for ri,r in enumerate(regs):rows.append((g,r,float(np.cos(gi*.8+ri*.45)),"Lineage" if r!="MYC" else "Growth",float(np.sin(gi+ri*.3))))
    activity=pd.DataFrame(rows,columns=["group","feature","value","module","effect"]);er=[];centers={"Prog":(-1.5,0),"Epi":(1.2,1.2),"Mes":(1.4,-1.2)}
    for g,(cx,cy) in centers.items():
        for i in range(70):er.append((f"{g}_{i}",RNG.normal(cx,.45),RNG.normal(cy,.4),g,float(RNG.normal({"Prog":.8,"Epi":.3,"Mes":-.25}[g],.08)),"E8.5" if i<35 else "E9.5"))
    emb=pd.DataFrame(er,columns=["id","x","y","group","value","stage"]);loading=pd.DataFrame({"feature":[f"Gene{i}" for i in range(12)],"effect":np.linspace(-1.1,1.5,12)})
    net=pd.DataFrame({"source":["SOX2","SOX2","GATA6","TEAD4","MYC"],"target":["Gene10","Gene11","Gene3","Gene8","Gene6"],"score":[.9,.72,.81,.66,.58]})
    return {"activity":activity,"embedding":emb,"loading":loading,"network":net},{"demo":True,"categorical_preset":"C19","embedding_value_label":"Module score"}


def svg_autocorrelation():
    feats=["GeneA","GeneB","GeneC","GeneD","GeneE","GeneF"];effects=pd.DataFrame({"feature":feats,"effect":[.4,.7,.2,.9,.35,.6],"moran_i":[.22,.48,.12,.61,.28,.4],"geary_c":[.88,.65,.95,.51,.79,.68],"module":["M1","M1","M2","M2","M3","M3"]});mr=[]
    for feat,coef in zip(feats,effects.moran_i):
        for i in range(80):
            v=RNG.normal();mr.append((f"{feat}_{i}",feat,float(v),float(coef*v+RNG.normal(0,.5))))
    moran=pd.DataFrame(mr,columns=["id","feature","value","spatial_lag"]);sr=[]
    for feat_i,feat in enumerate(feats):
        for iy in range(8):
            for ix in range(10):sr.append((f"{feat}_{ix}_{iy}","SecA",ix*40,iy*40,float(np.sin((ix+feat_i)/3)+np.cos((iy-feat_i)/4)+RNG.normal(0,.08)),feat))
    spatial=pd.DataFrame(sr,columns=["id","section","x","y","value","gene"])
    return {"effects":effects,"moran":moran,"spatial":spatial},{"demo":True,"coordinate_unit":"µm","top_n_maps":4,"moran_feature":"GeneD"}


def spatial_gradient():
    sr=[]
    for sec,shift in [("A",0),("B",.15)]:
        for iy in range(8):
            for ix in range(11):
                t=(ix/10+shift)%1;sr.append((f"{sec}_{ix}_{iy}",sec,ix*45,iy*45,float(t),float(np.clip(t+RNG.normal(0,.03),0,1)),"Anterior" if t<.5 else "Posterior"))
    spatial=pd.DataFrame(sr,columns=["id","section","x","y","gradient_value","pseudotime","group"]);tr=[]
    for gene_i,gene in enumerate(["SOX2","T","GATA6"]):
        for t in np.linspace(0,1,30):tr.append(("state",float(t),gene,float(np.sin((t+gene_i*.18)*np.pi)),float(np.clip(.2+.7*t,0,1))))
    trajectory=pd.DataFrame(tr,columns=["state","time","feature","value","probability"])
    return {"spatial":spatial,"trajectory":trajectory},{"demo":True,"coordinate_unit":"µm","axis_label":"Anterior → posterior"}


def development_spatial_gradient():
    inputs,cfg=spatial_gradient();sp=inputs["spatial"].copy();sp["cell_state"]=np.where(sp.gradient_value<.34,"Early",np.where(sp.gradient_value<.67,"Intermediate","Late"));inputs["spatial"]=sp;return inputs,cfg


def virtual_embryo_prediction():
    rows=[]
    for iy in range(10):
        for ix in range(12):
            obs=.5+.35*np.sin(ix/3)+.18*np.cos(iy/2);pred=obs+RNG.normal(0,.07);rows.append((f"p{ix}_{iy}",float(obs),float(pred),float(abs(RNG.normal(.08,.02))),"SecA",ix*40,iy*40))
    d=pd.DataFrame(rows,columns=["id","observed","predicted","uncertainty","section","x","y"]);d["residual"]=d.observed-d.predicted
    return {"main":d},{"demo":True,"coordinate_unit":"µm","residual_label":"Observed − predicted"}

FIXTURES={"scrna.pathway_activity":pathway_activity,"scrna.regulon_module":regulon_module,"spatial.svg_autocorrelation":svg_autocorrelation,"spatial.gradient_trajectory":spatial_gradient,"development.spatial_gradient":development_spatial_gradient,"development.virtual_embryo_prediction":virtual_embryo_prediction}
