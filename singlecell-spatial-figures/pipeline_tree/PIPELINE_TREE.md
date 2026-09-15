# Analysis → figure tree

Every leaf below is a required figure output or an advanced figure target. `A:` marks advanced outputs. No figure in this tree uses a subtitle.

```text
CNS_FIGURE_SKILL
├─ 1. scRNA-seq pipeline
│  ├─ 1.1 QC
│  │  ├─ QC violin / box
│  │  ├─ counts × genes scatter
│  │  ├─ mitochondrial distribution
│  │  ├─ sample QC summary
│  │  └─ A: QC dashboard / density+threshold / before-after filtering / sample QC heatmap
│  ├─ 1.2 Normalization + HVG
│  │  ├─ normalized-value distribution
│  │  ├─ mean–variance / HVG scatter
│  │  ├─ ranked HVGs
│  │  └─ A: before-after normalization / annotated HVG rank / batch HVG overlap
│  ├─ 1.3 PCA + integration
│  │  ├─ PCA scree
│  │  ├─ PCA embedding
│  │  ├─ UMAP by sample / batch / condition
│  │  └─ A: pre-post integration / batch mixing / cell-type preservation / latent QC panel
│  ├─ 1.4 Neighbors + clustering
│  │  ├─ cluster embedding
│  │  ├─ cluster-size plot
│  │  ├─ resolution comparison
│  │  └─ A: centroid labels / density contours / hierarchy / sample composition by cluster
│  ├─ 1.5 Annotation
│  │  ├─ annotated embedding
│  │  ├─ marker dotplot
│  │  ├─ marker heatmap
│  │  ├─ annotation confidence
│  │  └─ A: confidence embedding / hierarchy+markers / grouped marker heatmap / evidence panel
│  ├─ 1.6 Markers + differential expression
│  │  ├─ marker dotplot
│  │  ├─ DE heatmap
│  │  ├─ volcano
│  │  ├─ MA plot
│  │  ├─ ranked effect
│  │  └─ A: annotated volcano / DE forest / top-gene distributions / grouped matrix / evidence panel
│  ├─ 1.7 Composition + differential abundance
│  │  ├─ stacked composition
│  │  ├─ sample composition heatmap
│  │  ├─ fraction distribution
│  │  ├─ DA forest
│  │  ├─ DA lollipop
│  │  └─ A: paired composition / neighborhood DA / effect matrix / composition+DA panel
│  ├─ 1.8 Pathway / TF activity
│  │  ├─ enrichment dotplot
│  │  ├─ enrichment lollipop
│  │  ├─ activity heatmap
│  │  ├─ GSEA running-score plot
│  │  └─ A: signed enrichment / activity atlas / TF-pathway heatmap / leading-edge panel
│  ├─ 1.9 Trajectory + pseudotime
│  │  ├─ pseudotime embedding
│  │  ├─ lineage graph
│  │  ├─ gene trend
│  │  ├─ trajectory heatmap
│  │  ├─ branch expression
│  │  └─ A: lineage probability / trend+interval / branch-program heatmap / transition matrix / development panel
│  ├─ 1.10 RNA velocity + fate
│  │  ├─ velocity embedding
│  │  ├─ velocity stream
│  │  ├─ latent time
│  │  ├─ fate probability
│  │  ├─ terminal states
│  │  └─ A: terminal-fate map / fate matrix / lineage-driver heatmap / velocity+fate panel
│  ├─ 1.11 Cell-cell communication
│  │  ├─ sender-receiver heatmap
│  │  ├─ LR bubble
│  │  ├─ communication network
│  │  ├─ chord / circos
│  │  ├─ pathway ranking
│  │  └─ A: sender-receiver panel / LR evidence / pathway network / communication→target-program panel
│  ├─ 1.12 Regulon / module / topic
│  │  ├─ regulon heatmap
│  │  ├─ module activity embedding
│  │  ├─ gene-loading plot
│  │  ├─ factor × cell-type heatmap
│  │  └─ A: regulon specificity / lineage activity / loading+activity panel / TF-target network
│  └─ 1.13 Perturbation + prediction
│     ├─ response embedding
│     ├─ perturbation effect
│     ├─ observed × predicted
│     ├─ residual
│     └─ A: perturbation landscape / residual heatmap / calibration / response panel
│
├─ 2. Spatial transcriptomics pipeline
│  ├─ 2.1 Spatial QC
│  │  ├─ tissue image
│  │  ├─ spatial counts
│  │  ├─ spatial genes
│  │  ├─ section QC summary
│  │  └─ A: tissue QC dashboard / multi-metric map / section comparison
│  ├─ 2.2 Spatial normalization + latent space
│  │  ├─ normalized distribution
│  │  ├─ HVG/SVG scatter
│  │  ├─ section embedding
│  │  └─ A: section-wise normalization / latent-spatial consistency
│  ├─ 2.3 Spatial domains
│  │  ├─ domain map
│  │  ├─ domain-size plot
│  │  ├─ domain-marker heatmap
│  │  └─ A: boundary overlay / confidence map / domain+marker panel
│  ├─ 2.4 Spatial expression
│  │  ├─ feature map
│  │  ├─ multi-section feature map
│  │  ├─ multi-gene panel
│  │  └─ A: segmentation overlay / contour-hotspot / region zoom / feature+image composite
│  ├─ 2.5 Mapping + deconvolution
│  │  ├─ mapped cell identity
│  │  ├─ composition map
│  │  ├─ spatial pie / donut
│  │  ├─ mapping probability
│  │  ├─ mapping confidence
│  │  └─ A: top-k composition / abundance atlas / region composition heatmap / confidence panel
│  ├─ 2.6 SVG + spatial autocorrelation
│  │  ├─ SVG rank
│  │  ├─ Moran / Geary diagnostic
│  │  ├─ top SVG maps
│  │  ├─ SVG heatmap
│  │  └─ A: SVG evidence panel / ranked autocorrelation / SVG-module atlas
│  ├─ 2.7 Neighborhood + niche
│  │  ├─ neighborhood map
│  │  ├─ niche map
│  │  ├─ co-occurrence heatmap
│  │  ├─ pair enrichment
│  │  └─ A: niche atlas / cell-type×niche heatmap / regional niche comparison / marker-pathway panel
│  ├─ 2.8 Spatial communication
│  │  ├─ spatial network
│  │  ├─ spatial LR map
│  │  ├─ interaction heatmap
│  │  ├─ distance-response curve
│  │  └─ A: ligand+receptor maps / spatial LR evidence / distance dependence / downstream target panel
│  ├─ 2.9 Spatial gradient + trajectory
│  │  ├─ gradient map
│  │  ├─ gene-position curve
│  │  ├─ spatial pseudotime
│  │  ├─ trajectory heatmap
│  │  └─ A: multi-gene gradient / cell-state probability along axis / developmental program / aligned sections
│  ├─ 2.10 Multi-section integration
│  │  ├─ section small multiples
│  │  ├─ aligned feature maps
│  │  ├─ region comparison heatmap
│  │  └─ A: aligned atlas / section variability / cross-sample summary
│  └─ 2.11 Histology + morphology
│     ├─ image overlay
│     ├─ segmentation map
│     ├─ morphology feature map
│     ├─ transcript-image scatter
│     └─ A: image+segmentation+expression composite / morphology-transcript panel / region zoom evidence
│
├─ 3. scRNA + spatial joint analysis
│  ├─ 3.1 Reference mapping
│  │  ├─ reference embedding
│  │  ├─ mapped spatial identity
│  │  ├─ confidence map
│  │  ├─ abundance concordance
│  │  └─ A: reference→space panel / consistency heatmap / uncertainty panel
│  ├─ 3.2 Marker validation
│  │  ├─ scRNA marker dotplot
│  │  ├─ spatial marker map
│  │  ├─ concordance heatmap
│  │  └─ A: marker-validation panel / cross-modal evidence panel
│  ├─ 3.3 Niche validation
│  │  ├─ niche map
│  │  ├─ mapped state abundance
│  │  ├─ state×niche heatmap
│  │  └─ A: niche-state panel / local pathway support
│  └─ 3.4 Communication validation
│     ├─ scRNA communication network
│     ├─ spatial localization
│     ├─ LR concordance
│     └─ A: communication triangulation / pathway-localization evidence
│
├─ 4. Development / embryo
│  ├─ 4.1 Stage composition
│  │  ├─ stage×cell-type heatmap
│  │  ├─ stage composition
│  │  ├─ abundance trends
│  │  └─ A: developmental atlas panel
│  ├─ 4.2 Lineage progression
│  │  ├─ stage embedding
│  │  ├─ lineage tree
│  │  ├─ trajectory heatmap
│  │  ├─ fate matrix
│  │  └─ A: state→lineage→fate→gene panel
│  ├─ 4.3 Spatial embryonic gradient
│  │  ├─ embryo section
│  │  ├─ anatomical-axis gradient
│  │  ├─ gene gradient
│  │  ├─ cell-state along axis
│  │  └─ A: embryo-gradient panel
│  └─ 4.4 Virtual embryo prediction
│     ├─ ground truth
│     ├─ prediction
│     ├─ residual
│     ├─ uncertainty
│     └─ A: truth→prediction→error→uncertainty panel
│
├─ 5. Foundation model / AI evaluation
│  ├─ 5.1 Latent embedding
│  │  ├─ latent embedding
│  │  ├─ label / batch / condition views
│  │  ├─ neighborhood consistency
│  │  └─ A: latent-structure panel
│  ├─ 5.2 Reconstruction / prediction
│  │  ├─ observed×predicted
│  │  ├─ residual
│  │  ├─ error heatmap
│  │  ├─ calibration
│  │  └─ A: truth→prediction→error→uncertainty panel
│  ├─ 5.3 Benchmark
│  │  ├─ score distribution
│  │  ├─ paired benchmark
│  │  ├─ win-rate heatmap
│  │  ├─ rank plot
│  │  └─ A: benchmark evidence panel
│  └─ 5.4 Ablation / scaling
│     ├─ ablation effect
│     ├─ scaling curve
│     ├─ performance×compute
│     ├─ calibration shift
│     └─ A: model-evaluation panel
│
└─ 6. Publication panel templates
   ├─ single-cell atlas: embedding → annotation → markers → composition → DE → pathway
   ├─ development: stage/state → lineage → fate → trend → heatmap → transition
   ├─ spatial atlas: tissue → domains → cell-type map → features → niche → interaction
   ├─ communication: sender/receiver → pathway → LR → target program → validation
   ├─ cross-modal: scRNA reference → spatial mapping → deconvolution → niche → communication → validation
   └─ foundation model: latent space → benchmark → prediction → residual → uncertainty → biology
```

## Completion rule

A process node is not complete merely because an analysis package can compute it. Completion requires:

1. a declared result-table contract;
2. at least one required plot implementation;
3. at least one advanced plot implementation;
4. synthetic fixture and provenance-safe real-data path;
5. tests for required fields, scale semantics and output generation;
6. minimal / advanced examples;
7. a panel-template destination where relevant.

The machine-readable source of truth is `MODULE_REGISTRY.json`.