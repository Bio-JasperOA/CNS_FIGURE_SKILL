#!/usr/bin/env python3
"""Build inspectable synthetic examples for every executable pipeline module."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
import run_pipeline
import runtime_fixtures as f1
import runtime_fixtures2 as f2
import runtime_fixtures3 as f3


def all_fixtures():
    out={}
    for mid,fn in f1.FIXTURES.items():
        table,cfg=fn();out[mid]=({"main":table},cfg)
    for pack in (f2,f3):
        for mid,fn in pack.FIXTURES.items():out[mid]=fn()
    return out


def build(root:Path):
    root.mkdir(parents=True,exist_ok=True);rows=[]
    fixtures=all_fixtures()
    missing=set(run_pipeline.IMPLEMENTED["modules"])-set(fixtures)
    extra=set(fixtures)-set(run_pipeline.IMPLEMENTED["modules"])
    if missing:raise ValueError(f"Executable modules lack synthetic gallery fixtures: {sorted(missing)}")
    if extra:raise ValueError(f"Gallery fixtures exist for non-executable modules: {sorted(extra)}")
    for mid in sorted(run_pipeline.IMPLEMENTED["modules"]):
        inputs,cfg=fixtures[mid];folder=root/mid.replace(".","__")
        manifest=run_pipeline.render_module(mid,inputs,cfg,folder)
        targets=[x["target"] for x in manifest["generated"]]
        rows.append({"module_id":mid,"generated":len(targets),"skipped":len(manifest["skipped"]),"targets":targets,"folder":folder.name})
    (root/"gallery_manifest.json").write_text(json.dumps({"data":"synthetic_style_fixture","subtitle_policy":"forbidden","modules":rows},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Pipeline runtime synthetic gallery","","All numbers are deterministic synthetic style fixtures, not biological results.","Standalone PDF/SVG files are the vector examples; contact sheets are review-only raster composites.","","| Module | Generated | Skipped | Folder |","|---|---:|---:|---|"]
    for r in rows:lines.append(f"| `{r['module_id']}` | {r['generated']} | {r['skipped']} | `{r['folder']}/` |")
    (root/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default="build/pipeline_gallery");a=p.parse_args();rows=build(Path(a.out));print(json.dumps({"modules":len(rows),"figures":sum(x['generated'] for x in rows)},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
