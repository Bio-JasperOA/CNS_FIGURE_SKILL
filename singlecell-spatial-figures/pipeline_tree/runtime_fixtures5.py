"""Deterministic fixtures for the final executable pipeline tranche."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
RNG=np.random.default_rng(3152616)


def normalization_hvg():
    feats=[f"G{i:02d}" for i in range(36)];rows=[]
    for b in ["B1","B2"]:
        for i,g in enumerate(feats):
            mean=.15+i/25+RNG.normal(0,.03);var=mean*(1.1+(.7 if i%5==0 else .15))+RNG.normal(0,.04);rows.append((g,float(max(mean,.01)),float(max(var,.01)),bool(i%5==0 or i<5),i+1,b))
    features=pd.DataFrame(rows,columns=["feature","mean","variance","selected","rank","batch"]);dr=[]
    for cond,scale in [("Before",1.35),("After",1.0)]:
        for s in ["S1","S2","S3"]:
            for i in range(70):dr.append((f"{cond}_{s}_{i}",s,float(RNG.lognormal(.1,.45)*scale),cond))
    return {"features":features,"distribution":pd.DataFrame(dr,columns=["id","group","value","condition"])},{"demo":True,"top_hvg":24}


def integration():
    pca=pd.DataFrame({"component":np.arange(1,16),"variance_ratio":np.exp(-np.arange(15)/4)});pca["variance_ratio"]/=pca.variance_ratio.sum();pre=[];post=[];groups=["A","B","C"];centers={"A":(-2,0),"B":(1.5,1.4),"C":(1.6,-1.4)}
    for g in groups:
        for i in range(90):
            batch="B1" if i<45 else "B2";sample=f"S{1+i%3}";cond="Ctrl" if i%2==0 else "Treat";cx,cy=centers[g];shift=-.8 if batch=="B1" else .8;pre.append((f"{g}_{i}",RNG.normal(cx+shift,.45),RNG.normal(cy,.4),g,sample,batch,cond));post.append((f"{g}_{i}",RNG.normal(cx,.43),RNG.normal(cy,.39),g,sample,batch,cond,float(RNG.uniform(.72,.96))))
    return {"pca":pca,"pre":pd.DataFrame(pre,columns=["id","x","y","group","sample","batch","condition"]),"post":pd.DataFrame(post,columns=["id","x","y","group","sample","batch","condition","confidence"])},{"demo":True,"categorical_preset":"C19"}


def clustering():
    groups=["C0","C1","C2","C3"];parents={"C0":"Progenitor","C1":"Progenitor","C2":"Differentiated","C3":"Differentiated"};rows=[];centers=[(-2,0),(0,1.6),(2,.2),(0,-1.8)]
    for g,(cx,cy) in zip(groups,centers):
        for i in range(75):rows.append((f"{g}_{i}",RNG.normal(cx,.5),RNG.normal(cy,.42),g,f"S{1+i%4}",parents[g]))
    main=pd.DataFrame(rows,columns=["id","x","y","group","sample","parent"]);rr=[]
    for r in [".2",".4",".6",".8","1.0"]:
        for ds in ["silhouette","stability"]:rr.append((ds,r,"score",float(.55+.25*np.exp(-((float(r)-.65)**2)/.12)+RNG.normal(0,.015))))
    return {"main":main,"resolution":pd.DataFrame(rr,columns=["dataset","method","metric","value"])},{"demo":True,"resolution_metric":"score","categorical_preset":"C19"}


def velocity_fate():
    rows=[]
    for i in range(280):
        t=i/279;x=-2+4*t+RNG.normal(0,.15);y=np.sin(t*np.pi*1.7)+RNG.normal(0,.12);vx=.7;vy=.55*np.cos(t*np.pi*1.7);group="Root" if t<.35 else "FateA" if y>=0 else "FateB";rows.append((f"c{i}",x,y,vx,vy,t,group))
    vel=pd.DataFrame(rows,columns=["id","x","y","vx","vy","latent_time","group"]);fr=[]
    for r in vel.itertuples():
        pa=float(np.clip(.1+.85*r.latent_time*(1 if r.y>=0 else .35),.02,.98));pb=float(np.clip(.1+.85*r.latent_time*(1 if r.y<0 else .35),.02,.98));s=pa+pb;fr.append((r.id,"FateA",pa/s,r.group));fr.append((r.id,"FateB",pb/s,r.group))
    fate=pd.DataFrame(fr,columns=["id","state","probability","group"]);dr=[]
    for g in ["Root","FateA","FateB"]:
        for gene in ["SOX2","GATA6","T","MKI67"]:dr.append((g,gene,float(RNG.normal({"Root":.6,"FateA":.2,"FateB":-.2}[g],.35))))
    return {"velocity":vel,"fate":fate,"drivers":pd.DataFrame(dr,columns=["group","feature","value"])},{"demo":True,"fate_state":"FateA"}


def perturbation_prediction():
    n=260;obs=RNG.binomial(1,.5,n);pred=np.clip(.12+.72*obs+RNG.normal(0,.16,n),.01,.99);prediction=pd.DataFrame({"id":[f"p{i}" for i in range(n)],"observed":obs.astype(float),"predicted":pred,"group":np.where(np.arange(n)%2==0,"StateA","StateB"),"feature":np.where(np.arange(n)%3==0,"GeneA","GeneB")});prediction["residual"]=prediction.observed-prediction.predicted
    effect=pd.DataFrame({"feature":["PertA","PertB","PertC","PertD"],"effect":[.8,-.5,.35,-.2],"lower":[.55,-.72,.1,-.42],"upper":[1.05,-.28,.6,.02]});er=[]
    for cond,cx in [("Control",-1.2),("Perturbed",1.2)]:
        for i in range(120):er.append((f"{cond}_{i}",RNG.normal(cx,.6),RNG.normal(0,.75),cond,cond))
    return {"prediction":prediction,"effect":effect,"embedding":pd.DataFrame(er,columns=["id","x","y","group","condition"])},{"demo":True,"prediction_type":"probability","interval_label":"95% CI"}


def spatial_normalization_embedding():
    sr=[]
    for sec,shift in [("SecA",0),("SecB",.3)]:
        for iy in range(8):
            for ix in range(10):sr.append((f"{sec}_{ix}_{iy}",sec,ix*40,iy*40,float(RNG.lognormal(.1+shift,.3))))
    sp=pd.DataFrame(sr,columns=["id","section","x","y","value"]);feats=pd.DataFrame({"feature":[f"G{i}" for i in range(24)],"mean":np.linspace(.1,1.5,24),"variance":np.linspace(.2,2.2,24)+RNG.normal(0,.08,24),"selected":[i%4==0 for i in range(24)]});er=[]
    for sec,cx in [("SecA",-1.1),("SecB",1.1)]:
        for i in range(100):er.append((f"{sec}_{i}",RNG.normal(cx,.55),RNG.normal(0,.7),sec,float(RNG.uniform(.7,.98))))
    return {"spatial":sp,"features":feats,"embedding":pd.DataFrame(er,columns=["id","x","y","section","confidence"])},{"demo":True,"coordinate_unit":"µm"}


def multisection():
    rows=[];groups=["Region1","Region2"]
    for sec,offset in [("A",0),("B",.25),("C",-.15)]:
        for gene_i,gene in enumerate(["SOX2","T"]):
            for iy in range(7):
                for ix in range(9):rows.append((f"{sec}_{gene}_{ix}_{iy}",sec,ix*42,iy*42,float(np.sin(ix/3+gene_i)+np.cos(iy/3)+offset),gene,groups[0] if ix<4 else groups[1]))
    return {"main":pd.DataFrame(rows,columns=["id","section","x","y","value","gene","group"])},{"demo":True,"coordinate_unit":"µm","gene":"SOX2"}


def histology_morphology():
    image=pd.DataFrame([(ix*20,iy*20,float(.45+.35*np.sin(ix/3)*np.cos(iy/4))) for iy in range(12) for ix in range(14)],columns=["x","y","intensity"]);rows=[]
    for i in range(70):
        x=float(RNG.uniform(15,245));y=float(RNG.uniform(15,205));m=float(RNG.normal(.5+.002*x,.12));t=float(.7*m+RNG.normal(0,.12));v=[[x-5,y-5],[x+5,y-5],[x+5,y+5],[x-5,y+5]];rows.append((f"c{i}","SecA",x,y,m,t,json.dumps(v)))
    return {"main":pd.DataFrame(rows,columns=["id","section","x","y","morphology_value","transcript_value","vertices"]),"image":image},{"demo":True,"coordinate_unit":"µm","zoom_box":[40,150,40,150]}


def niche_validation():
    rows=[];niches=["N1","N2"];states=["Immune","Stromal","Epithelial"]
    for iy in range(12):
        for ix in range(14):
            niche=niches[0] if ix<7 else niches[1];state=states[(iy//4+(0 if niche=="N1" else 1))%3];rows.append((f"c{ix}_{iy}","SecA",ix*35,iy*35,state,niche,float(RNG.uniform(.2,.9))))
    sp=pd.DataFrame(rows,columns=["id","section","x","y","group","niche","state_abundance"]);ar=[]
    for niche in niches:
        for feat in ["IFN","TGFb","WNT","ECM"]:ar.append((niche,feat,float(RNG.normal(.5 if (niche=="N1")== (feat in {"IFN","WNT"}) else -.3,.2))))
    return {"spatial":sp,"activity":pd.DataFrame(ar,columns=["group","feature","value"])},{"demo":True,"coordinate_unit":"µm","rows_are_cells":True}


def communication_validation():
    comm=pd.DataFrame({"source":["Myeloid","Stromal","Myeloid"],"target":["T","T","Stromal"],"score":[.9,.55,.72],"ligand":["CCL5","CXCL12","TGFB1"],"receptor":["CCR5","CXCR4","TGFBR1"],"pathway":["Inflammation","Chemotaxis","Remodeling"]});sr=[]
    for gene in ["CCL5","CCR5","CXCL12","CXCR4","TGFB1","TGFBR1"]:
        for iy in range(8):
            for ix in range(10):
                val=float(max(0,RNG.normal(1.1 if (gene in {"CCL5","TGFB1"} and ix<5) or (gene in {"CCR5","TGFBR1"} and ix>=5) else .2,.09)));sr.append((f"{gene}_{ix}_{iy}","SecA",ix*45,iy*45,val,gene))
    sp=pd.DataFrame(sr,columns=["id","section","x","y","value","gene"]);con=pd.DataFrame({"pair":["CCL5-CCR5","CXCL12-CXCR4","TGFB1-TGFBR1"],"scrna_score":[.9,.55,.72],"spatial_score":[.83,.48,.69]})
    return {"communication":comm,"spatial":sp,"concordance":con},{"demo":True,"coordinate_unit":"µm"}

FIXTURES={"scrna.normalization_hvg":normalization_hvg,"scrna.integration":integration,"scrna.clustering":clustering,"scrna.velocity_fate":velocity_fate,"scrna.perturbation_prediction":perturbation_prediction,"spatial.normalization_embedding":spatial_normalization_embedding,"spatial.multisection":multisection,"spatial.histology_morphology":histology_morphology,"cross_modal.niche_validation":niche_validation,"cross_modal.communication_validation":communication_validation}
