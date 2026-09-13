# Declarative inventory. No packages are installed or upgraded by sourcing this file.
cran_core <- c("Matrix", "ggplot2", "scales", "jsonlite", "svglite")
cran_complex <- c("circlize", "scatterpie", "ggalluvial")
bioconductor_complex <- c("ComplexHeatmap")
cran_optional <- c("systemfonts", "patchwork", "cowplot", "ggrastr", "ggnewscale", "ggrepel",
                   "igraph", "ggraph", "sf", "mgcv", "renv")
bioconductor_optional <- c("SingleCellExperiment", "SpatialExperiment", "tradeSeq")
# Use an R/Bioconductor-compatible environment; capture sessionInfo after validation.
