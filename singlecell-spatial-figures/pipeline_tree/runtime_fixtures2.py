"""Deterministic multi-input fixtures for executable pipeline tranche 2."""
from __future__ import annotations
import numpy as np
import pandas as pd
RNG=np.random.default_rng(260915)


def annotation():
    groups=["Progenitor","Epithelial","Mesenchymal","Immune"]
    genes=["SOX2","KRT8","EPCAM","COL1A1","VIM","PTPRC","LST1","MKI67"]
    modules={g:("Identity" if g!="Progenitor" else "Proliferation") for g in genes};modules["MKI67"]="Proliferation"
    rows=[]
    preferred={"Progenitor":{"SOX2","MKI67"},"Epithelial":{"KRT8","EPCAM"},"Mesenchymal":{"COL1A1","VIM"},"Immune":{"PTPRC","LST1"}}
    for g in groups:
        for gene in genes:
            on=gene in preferred[g];rows.append((g,gene,float(RNG.normal(2.2 if on else .25,.12)),float(np.clip(RNG.normal(.78 if on else .12,.05),.01,.98)),modules[gene]))
    markers=pd.DataFrame(rows,columns=["group","feature","value","fraction","module"])
    centers={"Progenitor":(-2,1),"Epithelial":(1.7,1.2),"Mesenchymal":(-.3,-1.8),"Immune":(2.6,-1.5)};er=[]
    for g in groups:
        for i in range(90):
            cx,cy=centers[g];er.append((f"{g}_{i}",RNG.normal(cx,.55),RNG.normal(cy,.45),g,float(RNG.uniform(.72,.99)),"Developmental" if g!="Immune" else "Immune"))
    emb=pd.DataFrame(er,columns=["id","x","y","group","confidence","parent"])
    return {"markers":markers,"embedding":emb},{"demo":True,"categorical_preset":"C19","continuous_preset":"M02"}


def markers_de():
    ins,cfg=annotation();features=[f"Gene{i:02d}" for i in range(1,41)];eff=RNG.normal(0,.7,len(features));eff[:5]+=1.4;eff[-5:]-=1.2
    q=np.clip(np.exp(-np.abs(eff)*5)*.08,1e-5,.2);mean=np.exp(RNG.normal(1.2,.7,len(features)))
    de=pd.DataFrame({"feature":features,"effect":eff,"q":q,"mean":mean,"lower":eff-.25,"upper":eff+.25})
    return {"markers":ins["markers"],"de":de},{"demo":True,"effect_label":"log2 fold change","interval_label":"Supplied interval","label_n":8}


def trajectory():
    rows=[];times=np.linspace(0,1,18);features=["SOX2","T","GATA6","MKI67"]
    for lineage in ["A","B"]:
        for ti,t in enumerate(times):
            state="Root" if t<.28 else lineage
            prob=.5+.45*t if lineage=="A" else .5+.35*t
            for f_i,f in enumerate(features):
                val=np.sin((t+f_i*.12)*np.pi)*(1 if lineage=="A" else .75)+f_i*.15
                mean=val;rows.append((state,float(t),lineage,mean,mean-.12,mean+.12,float(np.clip(prob,0,1)),None,np.nan,f,float(val)))
    # Explicit transition edges are supplied, not inferred from the embedding.
    rows += [("Root",.3,"A",np.nan,np.nan,np.nan,np.nan,"A",60,None,np.nan),("Root",.3,"B",np.nan,np.nan,np.nan,np.nan,"B",40,None,np.nan)]
    main=pd.DataFrame(rows,columns=["state","time","lineage","mean","lower","upper","probability","transition_to","mass","feature","value"])
    er=[]
    for g,cx,cy in [("Root",0,0),("A",2.5,1.4),("B",2.3,-1.5)]:
        for i in range(100):
            t=(i/99)*(.3 if g=="Root" else .7)+(.0 if g=="Root" else .3)
            er.append((f"{g}_{i}",RNG.normal(cx*t if g!="Root" else 0,.28),RNG.normal(cy*t if g!="Root" else 0,.26),g,float(t)))
    emb=pd.DataFrame(er,columns=["id","x","y","group","value"])
    cfg={"demo":True,"time_label":"Pseudotime","value_label":"Programme score","interval_label":"Supplied interval","mass_label":"Transition mass","abstract_edges":[{"source":"Root","target":"A","weight":.6,"directed":True},{"source":"Root","target":"B","weight":.4,"directed":True}],"edge_definition":"Supplied lineage edges"}
    return {"main":main,"embedding":emb},cfg


def spatial_qc():
    rows=[]
    for iy in range(13):
        for ix in range(15):
            dist=((ix-7)/7)**2+((iy-6)/6)**2;inside=dist<1
            counts=max(100,RNG.normal(4300*(1-.35*dist),550));features=max(80,RNG.normal(1800*(1-.25*dist),220));mito=float(np.clip(RNG.normal(5+4*dist,1.6),.2,24))
            rows.append((f"s{ix}_{iy}","SecA",ix*45,iy*45,counts,features,mito,inside))
    d=pd.DataFrame(rows,columns=["id","section","x","y","n_counts","n_features","pct_mito","in_tissue"])
    return {"main":d},{"demo":True,"coordinate_unit":"µm","continuous_preset":"M02"}


def spatial_domains():
    rows=[];domains=["D1","D2","D3"]
    for iy in range(12):
        for ix in range(15):
            domain="D1" if ix<5 else "D2" if iy<6 else "D3";rows.append((f"p{ix}_{iy}","SecA",ix*40,iy*40,domain,float(RNG.uniform(.7,.99))))
    spatial=pd.DataFrame(rows,columns=["id","section","x","y","domain","confidence"])
    genes=["KRT8","SOX2","COL1A1","VIM","PTPRC","LST1"];mr=[]
    for d in domains:
        for i,g in enumerate(genes):mr.append((d,g,float((i//2)==domains.index(d))*1.7+float(RNG.uniform(.05,.45)),"Identity"))
    markers=pd.DataFrame(mr,columns=["group","feature","value","module"])
    return {"main":spatial,"markers":markers},{"demo":True,"coordinate_unit":"µm","categorical_preset":"C19"}


def spatial_niche():
    rows=[];niches=["Niche-A","Niche-B","Niche-C"];celltypes=["Epithelial","Immune","Stromal"]
    for iy in range(12):
        for ix in range(15):
            n=niches[0] if ix<5 else niches[1] if iy<6 else niches[2];ct=celltypes[(ix+iy)%3];cond="Late" if iy>5 else "Early";rows.append((f"p{ix}_{iy}","SecA",ix*40,iy*40,ct,n,cond))
    spatial=pd.DataFrame(rows,columns=["id","section","x","y","group","niche","condition"])
    ir=[]
    for a in niches:
        for b in niches:
            score=float(RNG.uniform(.05,1.0)*(1.5 if a==b else 1));ir.append((a,b,score,"Matrix" if a==b else "Chemokine"))
    inter=pd.DataFrame(ir,columns=["source","target","score","pathway"])
    return {"spatial":spatial,"interaction":inter},{"demo":True,"coordinate_unit":"µm","categorical_preset":"C19","score_label":"Neighborhood association"}

FIXTURES={"scrna.annotation":annotation,"scrna.markers_de":markers_de,"scrna.trajectory":trajectory,"spatial.qc":spatial_qc,"spatial.domains":spatial_domains,"spatial.neighborhood_niche":spatial_niche}
