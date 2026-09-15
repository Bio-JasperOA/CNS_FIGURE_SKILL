"""Foundation-model runtime views with explicit upstream metric semantics."""
from __future__ import annotations
import pandas as pd
import runtime_tranche2 as t2


def render_latent_embedding(inputs,config,out,api):
    d=inputs["main"].copy();api["_validate_contract"](d,"embedding");records=[];skipped=[];base=api["_base_cfg"](config)
    if "group" not in d:raise ValueError("fm.latent_embedding requires group label")
    groups=list(dict.fromkeys(d.group.astype(str)))
    ec=dict(base,title="Foundation-model latent embedding",group_order=groups,categorical_preset=config.get("categorical_preset","C19"),label_groups=groups[:14])
    core=d[["id","x","y","group"]].copy()
    records.append(api["_render_style"]("latent_embedding","embedding",core,ec,"minimal",out))
    records.append(api["_render_style"]("latent_by_label","embedding",core,dict(ec,title="Latent space by biological label"),"advanced",out))
    if "batch" in d:
        b=d[["id","x","y","batch"]].rename(columns={"batch":"group"});bc=dict(base,title="Latent space by batch",group_order=list(dict.fromkeys(b.group.astype(str))),categorical_preset=config.get("batch_preset","C03"))
        records.append(api["_render_style"]("latent_by_batch","embedding",b,bc,"advanced",out))
    else:skipped.append({"target":"latent_by_batch","reason":"batch not supplied."})
    if "confidence" in d:
        records.append(api["_custom_figure"]("neighborhood_consistency",t2._continuous_embedding(d,"confidence","Neighborhood consistency","Supplied consistency score",config,api),out))
    else:skipped.append({"target":"neighborhood_consistency","reason":"No upstream neighborhood-consistency/confidence score supplied; geometry alone is not used to invent one."})
    panel=api["_contact_sheet"]("latent_structure_panel",records,out,2)
    if panel:records.append(panel)
    return records,skipped
