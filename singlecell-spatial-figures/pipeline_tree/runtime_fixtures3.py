"""Deterministic fixtures for cross-modal / lineage / FM / spatial-communication runtime tranche."""
from __future__ import annotations
import numpy as np
import pandas as pd
RNG=np.random.default_rng(3152609)


def reference_mapping():
    groups=["Epithelial","Stromal","Immune"];centers={"Epithelial":(-1.8,.8),"Stromal":(1.4,.9),"Immune":(.3,-1.7)};rr=[]
    for g in groups:
        for i in range(100):
            cx,cy=centers[g];rr.append((f"{g}_{i}",RNG.normal(cx,.45),RNG.normal(cy,.4),g))
    ref=pd.DataFrame(rr,columns=["id","x","y","group"])
    sr=[]
    for iy in range(10):
        for ix in range(12):
            raw=np.array([1.4*np.exp(-((ix-3)**2+(iy-4)**2)/16)+.1,1.1*np.exp(-((ix-8)**2+(iy-5)**2)/20)+.1,.35+.08*iy]);raw/=raw.sum()
            for g,f in zip(groups,raw):sr.append((f"p{ix}_{iy}","SecA",ix*45,iy*45,g,float(f)))
    sp=pd.DataFrame(sr,columns=["id","section","x","y","group","fraction"])
    return {"reference":ref,"spatial":sp},{"demo":True,"coordinate_unit":"µm","categorical_preset":"C19"}


def marker_validation():
    groups=["Epithelial","Stromal","Immune"];genes=["EPCAM","KRT8","COL1A1","VIM","PTPRC","LST1"];pref={"Epithelial":{"EPCAM","KRT8"},"Stromal":{"COL1A1","VIM"},"Immune":{"PTPRC","LST1"}};mr=[]
    for g in groups:
        for gene in genes:mr.append((g,gene,float(RNG.normal(2 if gene in pref[g] else .2,.08)),float(np.clip(RNG.normal(.82 if gene in pref[g] else .1,.04),.01,.99))))
    markers=pd.DataFrame(mr,columns=["group","feature","value","fraction"])
    sr=[]
    for gene in genes:
        for iy in range(9):
            for ix in range(12):
                g=groups[0] if ix<4 else groups[1] if ix<8 else groups[2];val=float(RNG.normal(1.8 if gene in pref[g] else .18,.09));sr.append((f"{gene}_{ix}_{iy}","SecA",ix*42,iy*42,val,g,gene))
    sp=pd.DataFrame(sr,columns=["id","section","x","y","value","group","gene"])
    return {"markers":markers,"spatial":sp},{"demo":True,"coordinate_unit":"µm","max_spatial_markers":6,"categorical_preset":"C19"}


def lineage_progression():
    times=np.linspace(0,1,16);rows=[]
    for lin in ["A","B"]:
        for t in times:
            state="Root" if t<.3 else lin;prob=.5+.4*t if lin=="A" else .45+.38*t
            for gi,gene in enumerate(["SOX2","T","GATA6","MKI67"]):
                val=np.cos((t+gi*.15)*np.pi)*(1 if lin=="A" else .75)+gi*.2;rows.append((state,float(t),lin,float(prob),gene,float(val)))
    main=pd.DataFrame(rows,columns=["state","time","lineage","probability","feature","value"])
    er=[]
    for g,c in [("Root",(0,0)),("A",(2.4,1.3)),("B",(2.2,-1.4))]:
        for i in range(80):er.append((f"{g}_{i}",RNG.normal(c[0],.42),RNG.normal(c[1],.38),g))
    emb=pd.DataFrame(er,columns=["id","x","y","group"])
    cfg={"demo":True,"categorical_preset":"C19","abstract_edges":[{"source":"Root","target":"A","weight":.6,"directed":True},{"source":"Root","target":"B","weight":.4,"directed":True}],"edge_definition":"Supplied developmental lineage"}
    return {"main":main,"embedding":emb},cfg


def latent_embedding():
    groups=["StateA","StateB","StateC","StateD"];rows=[]
    for j,g in enumerate(groups):
        angle=j*np.pi/2;cx=2*np.cos(angle);cy=2*np.sin(angle)
        for i in range(90):rows.append((f"{g}_{i}",RNG.normal(cx,.55),RNG.normal(cy,.5),g,"Batch1" if i%2==0 else "Batch2",float(RNG.uniform(.72,.98))))
    d=pd.DataFrame(rows,columns=["id","x","y","group","batch","confidence"])
    return {"main":d},{"demo":True,"categorical_preset":"C19","batch_preset":"C03"}


def ablation_scaling():
    methods=["Full","No-context","No-pretrain","Baseline"];datasets=["D1","D2","D3","D4"];rows=[]
    computes={"Full":100,"No-context":75,"No-pretrain":55,"Baseline":25};offsets={"Full":.12,"No-context":.07,"No-pretrain":.03,"Baseline":0}
    for ds_i,ds in enumerate(datasets):
        for m in methods:
            for seed in range(3):
                acc=.68+offsets[m]+.015*np.sin(ds_i)+RNG.normal(0,.009);ece=.12-offsets[m]*.45+RNG.normal(0,.006)
                rows.append((ds,m,"Accuracy",float(acc),seed,computes[m]));rows.append((ds,m,"ECE",float(max(.005,ece)),seed,computes[m]))
    d=pd.DataFrame(rows,columns=["dataset","method","metric","value","seed","compute"])
    return {"main":d},{"demo":True,"metric":"Accuracy","calibration_metric":"ECE","baseline_method":"Baseline","compute_label":"Relative compute","compute_scale":"log"}


def spatial_communication():
    groups=["Myeloid","T","Stromal"];genes=["CCL5","CCR5","TGFB1","TGFBR1"];sr=[]
    for gene in genes:
        for iy in range(10):
            for ix in range(12):
                g=groups[0] if ix<4 else groups[1] if ix<8 else groups[2];hot=(gene in {"CCL5","TGFB1"} and g=="Myeloid") or (gene in {"CCR5"} and g=="T") or (gene=="TGFBR1" and g=="Stromal");val=float(max(0,RNG.normal(1.5 if hot else .18,.12)));sr.append((f"p{ix}_{iy}","SecA",ix*45,iy*45,val,g,gene))
    spatial=pd.DataFrame(sr,columns=["id","section","x","y","value","group","gene"])
    ir=[]
    defs=[("Myeloid","T","CCL5","CCR5","Inflammation"),("Myeloid","Stromal","TGFB1","TGFBR1","Remodeling"),("Stromal","T","CCL5","CCR5","Inflammation")]
    for i,(s,t,l,r,p) in enumerate(defs):
        for rep in range(8):ir.append((s,t,float(RNG.uniform(.45,1.2)),l,r,p,float(30+rep*20),"Activation" if t=="T" else "Matrix"))
    inter=pd.DataFrame(ir,columns=["source","target","score","ligand","receptor","pathway","distance","target_program"])
    return {"spatial":spatial,"interaction":inter},{"demo":True,"coordinate_unit":"µm","score_label":"Interaction score","distance_label":"Distance (µm)","categorical_preset":"C19"}

FIXTURES={"cross_modal.reference_mapping":reference_mapping,"cross_modal.marker_validation":marker_validation,"development.lineage_progression":lineage_progression,"fm.latent_embedding":latent_embedding,"fm.ablation_scaling":ablation_scaling,"spatial.communication":spatial_communication}
