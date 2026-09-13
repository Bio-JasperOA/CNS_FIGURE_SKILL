# Original complex-figure recipes. Source figure_core.R before using these helpers.

annotated_enrichment_heatmap <- function(neg_log10_q, effect_labels,
                                         row_gene_counts, column_gene_counts,
                                         colour_function, value_label = "-log10(q)",
                                         row_split = NULL, font_pt = 7) {
  require_packages(c("ComplexHeatmap", "circlize"))
  m <- as.matrix(neg_log10_q); labels <- as.matrix(effect_labels)
  if (is.null(rownames(m)) || is.null(colnames(m)) || anyDuplicated(rownames(m)) ||
      anyDuplicated(colnames(m))) stop("Heatmap requires unique row/column identifiers.")
  if (!identical(dimnames(m), dimnames(labels))) stop("Effect labels must match heatmap dimnames.")
  if (any(!is.finite(m)) || any(m < 0)) stop("Supply finite nonnegative -log10(q), with clipping disclosed.")
  if (is.null(names(row_gene_counts)) || is.null(names(column_gene_counts)) ||
      !all(rownames(m) %in% names(row_gene_counts)) ||
      !all(colnames(m) %in% names(column_gene_counts))) stop("Missing annotation IDs.")
  r <- row_gene_counts[rownames(m)]; column_counts <- column_gene_counts[colnames(m)]
  if (anyNA(r) || anyNA(column_counts) || any(r < 0) || any(column_counts < 0)) stop("Invalid annotation counts.")
  if (!is.null(row_split) && length(row_split) != nrow(m)) stop("row_split is not aligned.")
  # Values encode significance; printed labels encode effects. They are distinct.
  top <- ComplexHeatmap::HeatmapAnnotation(
    `n genes` = ComplexHeatmap::anno_barplot(column_counts),
    annotation_name_gp = grid::gpar(fontsize = font_pt))
  side <- ComplexHeatmap::rowAnnotation(
    `n genes` = ComplexHeatmap::anno_barplot(r),
    annotation_name_gp = grid::gpar(fontsize = font_pt))
  ComplexHeatmap::Heatmap(m, name = value_label, col = colour_function,
    cluster_rows = FALSE, cluster_columns = FALSE, cluster_row_slices = FALSE,
    row_split = row_split, top_annotation = top, right_annotation = side,
    row_names_gp = grid::gpar(fontsize = font_pt),
    column_names_gp = grid::gpar(fontsize = font_pt),
    layer_fun = function(j, i, x, y, width, height, fill) {
      text <- labels[cbind(i, j)]
      keep <- !is.na(text) & nzchar(text)
      rgba <- grDevices::col2rgb(fill, alpha = TRUE) / 255
      rgb <- sweep(rgba[1:3, , drop = FALSE], 2, rgba[4, ], `*`)
      rgb <- sweep(rgb, 2, 1 - rgba[4, ], `+`)
      linear <- ifelse(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055)^2.4)
      luminance <- as.numeric(c(.2126, .7152, .0722) %*% linear)
      text_colour <- ifelse((luminance + .05) / .05 >= 1.05 / (luminance + .05), "black", "white")
      grid::grid.text(text[keep], x[keep], y[keep],
                      gp = grid::gpar(fontsize = font_pt, col = text_colour[keep]))
    })
}

export_heatmap <- function(heatmap, stem, provenance, width_mm = 183, height_mm = 150,
                           dpi = 300) {
  require_packages(c("ComplexHeatmap", "svglite", "jsonlite"))
  required <- c("data_source", "analysis_unit", "value_definition", "seed")
  if (!all(required %in% names(provenance))) stop("Missing required provenance fields.")
  if (any(c(width_mm, height_mm, dpi) <= 0)) stop("Positive dimensions/dpi required.")
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  # Draw independently on equally sized devices; do not assume the Heatmap object
  # is a ggplot or rasterise the whole assembled figure to solve an alignment bug.
  render <- function(open_device) {
    open_device(); on.exit(grDevices::dev.off(), add = TRUE)
    ComplexHeatmap::draw(heatmap, merge_legends = TRUE,
                         padding = grid::unit(c(3, 3, 3, 3), "mm"))
  }
  render(function() {
    if (capabilities("cairo")) grDevices::cairo_pdf(paste0(stem, ".pdf"), width_mm/25.4, height_mm/25.4)
    else grDevices::pdf(paste0(stem, ".pdf"), width = width_mm/25.4, height = height_mm/25.4, useDingbats = FALSE)
  })
  render(function() svglite::svglite(paste0(stem, ".svg"), width = width_mm/25.4, height = height_mm/25.4))
  render(function() grDevices::png(paste0(stem, ".png"), width = width_mm, height = height_mm,
                                   units = "mm", res = dpi))
  provenance$session_info <- capture.output(utils::sessionInfo())
  provenance$width_mm <- width_mm; provenance$height_mm <- height_mm
  jsonlite::write_json(provenance, paste0(stem, "_provenance.json"), pretty = TRUE, auto_unbox = TRUE)
  invisible(stem)
}

collapse_proportions <- function(proportions, retain_types, tolerance = 1e-6) {
  # Preserve all omitted mass as Other. NEVER replace the largest fractions by 1s
  # and then label the resulting equal-width pie slices as cell proportions.
  m <- as.matrix(proportions)
  if (is.null(colnames(m)) || anyDuplicated(colnames(m)) || anyNA(m) ||
      any(!is.finite(m)) || any(m < 0)) stop("Invalid proportion matrix.")
  if (!all(abs(rowSums(m) - 1) <= tolerance)) stop("Rows must already be proportions summing to one.")
  if (anyDuplicated(retain_types) || !all(retain_types %in% colnames(m)) || "Other" %in% colnames(m)) {
    stop("Invalid retain_types or reserved Other column.")
  }
  keep <- m[, retain_types, drop = FALSE]
  cbind(keep, Other = rowSums(m[, setdiff(colnames(m), retain_types), drop = FALSE]))
}

plot_spatial_pies <- function(tab, component_columns, palette, radius_units,
                              coordinate_unit, y_axis_down = TRUE) {
  require_packages(c("ggplot2", "scatterpie"))
  if (!all(c("x", "y", "section_id", component_columns) %in% names(tab))) stop("Missing spatial/pie fields.")
  if (anyNA(tab$section_id) || length(unique(tab$section_id)) != 1) stop("One section per plot required.")
  if (!coordinate_unit %in% c("um", "pixel") || length(radius_units) != 1 ||
      !is.finite(radius_units) || radius_units <= 0) stop("Declare positive radius and physical/pixel unit.")
  if (any(!is.finite(as.matrix(tab[, c("x", "y"), drop = FALSE])))) stop("Nonfinite coordinates.")
  m <- as.matrix(tab[, component_columns, drop = FALSE])
  if (any(!is.finite(m)) || any(m < 0) || any(abs(rowSums(m) - 1) > 1e-6)) stop("Invalid proportions.")
  validate_palette(component_columns, palette)
  tab$.radius <- radius_units
  p <- ggplot2::ggplot(tab) +
    scatterpie::geom_scatterpie(ggplot2::aes(x = x, y = y, r = .radius),
                                cols = component_columns, colour = NA) +
    ggplot2::scale_fill_manual(values = palette[component_columns], drop = FALSE) +
    ggplot2::coord_equal() + theme_sc() +
    ggplot2::labs(x = paste0("x (", coordinate_unit, ")"),
                   y = paste0("y (", coordinate_unit, ")"), fill = "Cell fraction")
  if (y_axis_down) p <- p + ggplot2::scale_y_reverse()
  p
}

plot_transport_alluvial <- function(mass, palette, unit_label = "Transport mass") {
  require_packages(c("ggplot2", "ggalluvial"))
  m <- as.matrix(mass)
  if (is.null(rownames(m)) || is.null(colnames(m)) || any(!is.finite(m)) ||
      any(m < 0) || sum(m) <= 0) stop("Nonnegative, named mass matrix required.")
  tab <- as.data.frame(as.table(m), responseName = "mass", stringsAsFactors = FALSE)
  names(tab)[1:2] <- c("source", "target")
  tab <- tab[tab$mass > 0, , drop = FALSE]
  if (nrow(tab) > 150) stop("Too many links; aggregate or use a declared filter first.")
  validate_palette(tab$source, palette)
  ggplot2::ggplot(tab, ggplot2::aes(y = mass, axis1 = source, axis2 = target)) +
    ggalluvial::geom_alluvium(ggplot2::aes(fill = source), width = 1/12) +
    ggalluvial::geom_stratum(width = 1/12) +
    ggplot2::geom_text(stat = "stratum", ggplot2::aes(label = ggplot2::after_stat(stratum)), size = 2.5) +
    ggplot2::scale_x_discrete(limits = c("Source", "Target"), expand = c(.05, .05)) +
    ggplot2::scale_fill_manual(values = palette) +
    ggplot2::labs(x = NULL, y = unit_label) + theme_sc()
}
