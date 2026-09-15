"""Deterministic synthetic fixtures for pipeline-runtime regression tests.

These tables exercise rendering contracts only. They are not biological data.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260915)


def scrna_qc():
    rows=[]
    for sample,shift in [("S1",0),("S2",350),("S3",-250)]:
        for i in range(80):
            counts=max(500,RNG.normal(4200+shift,1100))
            genes=max(250,RNG.normal(1650+shift/6,330))
            mito=np.clip(RNG.normal(6.5+(sample=="S3")*2.3,3.0),.2,22)
            rows.append((f"{sample}_{i}",sample,counts,genes,mito,mito<14 and genes>500,
                         "Case" if sample=="S3" else "Control"))
    d=pd.DataFrame(rows,columns=["cell_id","sample","n_counts","n_features","pct_mito","keep","condition"])
    cfg={"demo":True,"thresholds":{"pct_mito_max":14},"style":{"categorical_preset":"C03"}}
    return d,cfg


def composition():
    groups=["T","B","Myeloid","Stromal"]
    stages=["Control","Disease"]
    rows=[]
    for si in range(8):
        condition=stages[si//4]
        raw=np.array([.40,.22,.25,.13])+RNG.normal(0,.025,4)
        if condition=="Disease": raw+=np.array([-.08,.01,.10,-.03])
        raw=np.clip(raw,.02,None);raw=raw/raw.sum()
        subject=f"P{si%4+1}"
        for g,f in zip(groups,raw):
            effect={"T":-.32,"B":.08,"Myeloid":.46,"Stromal":-.18}[g]
            rows.append((f"S{si+1}",g,float(f),condition,subject,int(round(f*2000)),
                         effect,effect-.15,effect+.15,.01 if abs(effect)>.2 else .12))
    d=pd.DataFrame(rows,columns=["sample","group","fraction","condition","subject","count","effect","lower","upper","q"])
    cfg={"demo":True,"effect_label":"log odds ratio","interval_label":"Supplied interval","categorical_preset":"C19"}
    return d,cfg


def communication():
    sources=["Myeloid","T","Stromal"];targets=["T","B","Stromal"]
    lrs=[("CCL5","CCR5","Chemokine"),("TGFB1","TGFBR1","TGFb"),("CXCL12","CXCR4","Chemokine"),
         ("SPP1","CD44","Matrix")]
    rows=[]
    for s in sources:
        for t in targets:
            for lig,rec,path in lrs:
                score=float(RNG.uniform(.05,1.2)*(1.5 if s=="Myeloid" and t=="T" else 1))
                rows.append((s,t,score,lig,rec,path,float(RNG.uniform(.001,.12)),
                             "Inflammation" if path=="Chemokine" else "Remodeling"))
    d=pd.DataFrame(rows,columns=["source","target","score","ligand","receptor","pathway","q","target_program"])
    cfg={"demo":True,"edge_unit":"interaction score","score_label":"Interaction score","categorical_preset":"C19"}
    return d,cfg


def spatial_expression():
    rows=[]
    for section,offset in [("SecA",0),("SecB",1.2)]:
        for gene in ["SOX2","MKI67"]:
            for iy in range(12):
                for ix in range(14):
                    x=ix*40; y=iy*40
                    center=np.exp(-((ix-(5+offset))**2+(iy-5.5)**2)/22)
                    val=float(center*(2.2 if gene=="SOX2" else 1.4)+RNG.normal(0,.08))
                    rows.append((f"{section}_{gene}_{ix}_{iy}",section,x,y,val,gene))
    d=pd.DataFrame(rows,columns=["id","section","x","y","value","gene"])
    cfg={"demo":True,"coordinate_unit":"µm","value_label":"Normalized expression","scale_bar":200,
         "max_genes":4,"continuous_preset":"M02"}
    return d,cfg


def spatial_mapping():
    groups=["Epithelial","Mesenchymal","Immune","Endothelial"]
    rows=[]
    for iy in range(10):
        for ix in range(12):
            x=ix*45;y=iy*45
            base=np.array([
                1.3*np.exp(-((ix-3)**2+(iy-4)**2)/18)+.1,
                1.1*np.exp(-((ix-8)**2+(iy-5)**2)/22)+.1,
                .45+.15*np.sin(ix/2),
                .25+.08*iy
            ])
            base=np.clip(base,0.02,None); frac=base/base.sum()
            conf=float(.65+.3*np.max(frac))
            sid=f"spot_{ix}_{iy}"
            for g,f in zip(groups,frac):
                rows.append((sid,"SecA",x,y,g,float(f),conf))
    d=pd.DataFrame(rows,columns=["id","section","x","y","group","fraction","confidence"])
    cfg={"demo":True,"coordinate_unit":"µm","categorical_preset":"C19","continuous_preset":"M02","top_k":3}
    return d,cfg


def prediction():
    rows=[]
    feats=["GeneA","GeneB","GeneC"]; groups=["State1","State2"]
    for i in range(360):
        obs=float(RNG.beta(2.5,2.0))
        pred=float(np.clip(obs*.82+.09+RNG.normal(0,.10),0,1))
        group=groups[i%2]; feat=feats[i%3]
        rows.append((f"p{i}",obs,pred,obs-pred,float(RNG.uniform(.02,.12)),feat,group))
    d=pd.DataFrame(rows,columns=["id","observed","predicted","residual","uncertainty","feature","group"])
    cfg={"demo":True,"prediction_type":"probability","model_name":"VirtualModel"}
    return d,cfg


def benchmark():
    methods=["ModelA","ModelB","ModelC","Baseline"]; datasets=[f"D{i}" for i in range(1,9)]
    rows=[]
    for ds_i,ds in enumerate(datasets):
        for m_i,m in enumerate(methods):
            for seed in range(3):
                val=.66+.035*m_i*(-1)+.025*np.sin(ds_i)+RNG.normal(0,.012)
                if m=="ModelA": val+=.10
                elif m=="ModelB": val+=.06
                elif m=="ModelC": val+=.03
                rows.append((ds,m,"Pearson r",float(np.clip(val,0,1)),seed))
    d=pd.DataFrame(rows,columns=["dataset","method","metric","value","seed"])
    cfg={"demo":True,"metric":"Pearson r","baseline_method":"Baseline","categorical_preset":"C03"}
    return d,cfg


def stage_composition():
    groups=["Epiblast","Mesoderm","Endoderm","Ectoderm"]
    stages=["E6.5","E7.0","E7.5","E8.0"]
    rows=[]
    for st_i,stage in enumerate(stages):
        for rep in range(3):
            raw=np.array([.50-.10*st_i,.12+.08*st_i,.15+.03*st_i,.23-.01*st_i])+RNG.normal(0,.018,4)
            raw=np.clip(raw,.02,None);raw=raw/raw.sum()
            for g,f in zip(groups,raw):
                rows.append((f"{stage}_R{rep+1}",g,float(f),stage))
    d=pd.DataFrame(rows,columns=["sample","group","fraction","condition"])
    cfg={"demo":True,"stage_order":stages,"categorical_preset":"C19"}
    return d,cfg


FIXTURES={
    "scrna.qc":scrna_qc,
    "scrna.composition_da":composition,
    "scrna.communication":communication,
    "spatial.expression":spatial_expression,
    "spatial.mapping_deconvolution":spatial_mapping,
    "fm.reconstruction_prediction":prediction,
    "fm.benchmark":benchmark,
    "development.stage_composition":stage_composition,
}
