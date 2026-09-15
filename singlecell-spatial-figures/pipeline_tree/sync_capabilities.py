#!/usr/bin/env python3
"""Synchronize executable pipeline runtime metadata into the canonical capability registry."""
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
SKILL=HERE.parent

def sync():
    impl=json.loads((HERE/"IMPLEMENTED_MODULES.json").read_text(encoding="utf-8"))
    cap_path=SKILL/"CAPABILITIES.json";cap=json.loads(cap_path.read_text(encoding="utf-8"))
    if str(cap.get("version","0")).split(".")[0]!="3":raise ValueError("pipeline runtime must not change the major version")
    cap["pipeline_runtime"]={
      "version":impl["runtime_version"],
      "router":"pipeline_tree/run_pipeline.py",
      "registry":"pipeline_tree/IMPLEMENTED_MODULES.json",
      "roadmap":"pipeline_tree/MODULE_REGISTRY.json",
      "contracts":"pipeline_tree/RESULT_CONTRACTS.json",
      "gallery_builder":"pipeline_tree/build_gallery.py",
      "tests":["pipeline_tree/tests/test_runtime.py","pipeline_tree/tests/test_runtime_tranche2.py","pipeline_tree/tests/test_runtime_tranche3.py","pipeline_tree/tests/test_runtime_registry.py"],
      "subtitle_policy":impl["subtitle_policy"],
      "n_executable_modules":len(impl["modules"]),
      "executable_modules":sorted(impl["modules"]),
      "status":"executable Python pipeline result-to-figure adapters; upstream scientific analysis remains external",
      "limits":[
        "Roadmap-only modules are not executable capabilities",
        "Optional advanced outputs are skipped when their declared upstream evidence is absent",
        "Contact-sheet panels are raster review composites; standalone PDF/SVG outputs are vector publication candidates",
        "Native R pipeline runtime is not implemented or tested",
        "No p-values, intervals, trajectories, spatial boundaries, niche labels, posterior uncertainty or latent metrics are inferred by the plotting runtime"
      ]
    }
    cap_path.write_text(json.dumps(cap,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return cap["pipeline_runtime"]

if __name__=="__main__":print(json.dumps(sync(),indent=2,ensure_ascii=False))
