# Assay-aware biological interpretation

These are project interpretation rules, not universal journal requirements or a substitute for the actual method. Use the measured endpoint and experiment design, not the shape of a plot, to select a route. The registry `ASSAY_RULES.json` gives compact machine-readable prompts; the agent supplies biological reasoning. Bibliographic support and access scope are in `LITERATURE_LOGIC.md`.

## Cell identity, abundance and transcriptional response

**Annotation/state discovery.** Ask whether a coherent marker programme distinguishes a reproducible population or a transient state. Inspect positive and negative markers, doublets, contamination, donor recurrence, reference coverage and classification uncertainty. A newly numbered cluster is not a newly discovered cell type. A signature assembled from known markers provides characterization, not independent validation of a marker-defined label. Biological value may be a reproducible state in a previously unresolved context without claiming a novel cell type.

**Composition/differential abundance.** Separate relative proportion, absolute cell number, density per tissue area and sampling yield. Increased fraction may reflect expansion, survival, recruitment or depletion of other populations; identify which alternatives are measured. Read sample-wise variation, capture/dissociation biases, denominator and model. For group-level inference, cells cannot substitute for independent donors/animals/embryos. A fractional shift can be a meaningful comparative result while its mechanism remains unresolved. [P5]

**Cell-type-specific differential expression.** Read contrast direction, assay/layer, effect scale, multiplicity and specimen-aware uncertainty. Determine whether changes occur within the same state or reflect substate mixtures. Identify the genes that distinguish the candidate explanation from generic stress, translation, cycling or damage. A gene's RNA abundance is not equivalent to its protein secretion, binding or enzymatic activity. Repeated enrichment of the same DE set does not add independent evidence. [P5]

**Pathway/gene-programme activity.** Inspect contributing genes, overlap between gene sets, expression coverage and whether the method measures enrichment, inferred activity or per-cell scores. Distinguish a coherent induced programme from a signal dominated by one ubiquitous component. Ask what functional readout should change if the inferred programme is biologically active. Integrate coherent targets, localization and phenotype without relabelling enrichment itself as mechanism. [P1, P5]

**Regulons and chromatin.** Separate expression of a TF, inferred target activity, motif accessibility, occupancy, physical binding and perturbation consequence. A motif can nominate a TF family but not uniquely identify a bound factor. A TF whose activity changes before targets is a candidate regulator; direct regulation needs endpoint-appropriate evidence. A gene-level perturbation may establish a regulatory contribution without proving every inferred edge. [P1, P4]

## Time, state and fate

**Trajectory.** Establish the biological root and measured chronological stages, then evaluate ordering, branch stability, sampling gaps and recurrence. Pseudotime describes an inferred ordering, not elapsed time, lineage identity or cell migration. A cross-sectional state difference is not an observed transition. Link inferred progression to stage, fate tracking, spatial order or perturbations according to the actual claim. [P3]

**Velocity/fate.** Inspect spliced/unspliced provenance, fit, kinetics, uncertainty and sensitivity before interpreting direction. The displayed arrow is a projected model quantity. A fate-probability map is conditional on the fitted model and terminal-state definition. Compare directional predictions with independent fate observations where available. In lineage-tracing studies, examine barcode quality, clone sampling, sister-cell assumptions and culture/transplant context. [P3]

## Tissue context and interaction

**Spatial domains/gradients/niches.** Distinguish cell, nucleus, multicellular spot, bin and molecule observations. Check measured coordinate systems, tissue registration, segmentation, tissue coverage and resolution. A niche interpretation should relate recurring local composition to a molecular or functional programme. Compare enrichment against a null that addresses density and anatomical compartment when appropriate; unstructured shuffling may destroy the very tissue geometry that needs controlling. Distinguish a repeat across serial sections from a repeat across individuals. [P2, P6]

**Mapping/deconvolution.** Separate posterior cell abundance, normalized fraction, label score and calibrated probability. Reference-dependent localization is not independent confirmation of every reference label. Use held-out markers or a separate assay where possible. A small inferred contribution in a mixed spot is not proof of direct cell-cell contact; a gene outside a targeted panel is unmeasured rather than absent. [P1, P2]

**Ligand–receptor/communication.** Connect sender identity and ligand expression to receiver receptor, spatial or exposure feasibility, receiver response, specimen recurrence and candidate mechanism. Distinguish the scoring function from ligand concentration, protein secretion and signaling flux. Secreted and contact-mediated mechanisms have different spatial predictions. Co-localization supports anatomical plausibility, not causal signaling; blocking/reconstitution or another suitable causal design can test a specific edge. [P2, R2]

## Molecular and imaging experiments

**RT-qPCR.** Read the actual normalizer, ΔCt/ΔΔCt or relative-expression definition, reference gene stability, assay efficiency assumptions and biological versus technical replicates. Ct direction and expression direction can be opposite. Describe the quantified RNA response; do not infer protein abundance or biological function without an appropriate readout. A validated perturbation followed by target transcript changes can support a molecular consequence in that system, even when an organismal phenotype remains unresolved. [P1]

**Immunoblot/protein/activity.** Separate total protein, phospho-protein, phospho/total ratio, loading normalization, secreted protein and direct activity assays. Check linearity/saturation, lane/sample identity, loading controls and replicate quantification. A band image without quantitative source data permits a qualitative description, not an invented statistical result. Increased phospho/total can support a pathway-related readout under a validated assay, but must not be conflated with increased total protein.

**Imaging/IF/IHC.** Establish whether the endpoint is intensity, positive fraction, count, area, morphology, colocalization or distance. Check specimen-level sampling, blinded field selection when available, segmentation/gating, common exposure and background treatment. Do not count fields or pixels as independent animals. Colocalization is not direct binding; a representative field cannot establish distribution across all specimens.

**Flow cytometry.** Read parent gate, viability/doublet exclusion, compensation controls, gating consistency and denominator. A percentage within CD45+ cells and a percentage within all viable cells answer different questions. Event counts are not donor counts. Distinguish MFI shift from an increase in the fraction of positive cells and from an increase in absolute population size.

**Functional assays.** Name the actual function measured. A scratch-closure change can involve proliferation, death or motility; an ATP assay is not interchangeable with absolute viable-cell counting. Connect readouts across molecular, cellular and tissue scales only where the experiments test that link. Endpoint disagreements may locate where a mechanism stops rather than invalidate every molecular finding.

The wet-lab checks above are general assay reasoning prompts, not newly reviewed experimental protocols. Consult the study-specific protocol and source data before applying them.

## Perturbation, rescue and prediction

**Loss/gain of function.** Separate successful target engagement, specificity, dose/time, viability and phenotype. Loss of a readout after loss of function may support a required contribution in that context; gain of function addresses a different sufficiency claim. Randomization, independent reagents, matched controls and orthogonal readouts strengthen different parts of the argument, but no single checkbox proves all of them.

**Rescue/epistasis.** Compare baseline, perturbation, rescue and rescue-alone controls as relevant. Rescue towards baseline is not necessarily full normalization, and a non-significant rescue-versus-baseline comparison does not establish equivalence. Separate bypass rescue, on-target rescue and pathway-order claims. Test interaction directly rather than infer epistasis from two unrelated p-values. Do not generate a rescue result because the narrative template contains a rescue slot.

**Model/virtual-cell predictions.** State what was held out and at what independence unit. Inspect matched simple and task-specific baselines, model-versus-baseline effects, uncertainty, per-condition errors, no-change/mean-response behavior, leakage and biological validation. Better global expression correlation need not mean better perturbation-effect prediction. Negative benchmark results can reveal a precise representational or evaluation limitation, not a universal failure of all future models. [P4, P7]

## Minimal versus full interpretation

For one assay, deliver the observation and its immediate biological implication. For a multi-assay study, integrate the molecular source, response, spatial/time context and functional endpoint. Avoid mandatory method stacking. Good interpretation can conclude that only one link is established and that another is not, while preserving the scientific value of the established link.
