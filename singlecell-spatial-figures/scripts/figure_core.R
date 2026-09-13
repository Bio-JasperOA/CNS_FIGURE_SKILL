# Original utilities, not copied author scripts. Matrices are genes x cells.
# R runtime was not available during authoring: execute tests before project use.

require_packages <- function(packages) {
  absent <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
  if (length(absent)) stop("Install required packages first: ", paste(absent, collapse = ", "))
}

validate_palette <- function(labels, palette) {
  if (is.null(names(palette)) || anyDuplicated(names(palette))) stop("Palette needs unique names.")
  if (anyNA(labels)) stop("Missing category labels require an explicit policy.")
  missing <- setdiff(as.character(labels), names(palette))
  if (length(missing)) stop("Missing palette entries: ", paste(missing, collapse = ", "))
  grDevices::col2rgb(unname(palette[as.character(labels)]))
  invisible(TRUE)
}

resolve_font <- function(requested = "Arial", fallback = "sans") {
  if (requireNamespace("systemfonts", quietly = TRUE)) {
    available <- unique(systemfonts::system_fonts()$family)
    if (requested %in% available) return(requested)
  }
  warning("Requested font not verified; using ", fallback, ". Record actual output font during QA.")
  fallback
}

theme_sc <- function(base_size = 7, base_family = "sans", line_width = 0.22) {
  require_packages("ggplot2")
  # ggplot2 line widths are mm, whereas many other renderers use points.
  ggplot2::theme_classic(base_size = base_size, base_family = base_family) +
    ggplot2::theme(axis.line = ggplot2::element_line(linewidth = line_width),
                   axis.ticks = ggplot2::element_line(linewidth = line_width),
                   plot.title = ggplot2::element_text(size = base_size, face = "plain"),
                   plot.tag = ggplot2::element_text(size = base_size + 1, face = "bold"),
                   legend.title = ggplot2::element_text(size = base_size),
                   legend.key = ggplot2::element_blank(),
                   plot.margin = grid::unit(c(2, 2, 2, 2), "mm"))
}

check_matrix <- function(x, shape, name, nonnegative = FALSE) {
  if (!identical(as.integer(dim(x)), as.integer(shape))) stop(name, ": unexpected dimensions.")
  values <- if (inherits(x, "sparseMatrix")) x@x else as.vector(x)
  if (any(!is.finite(values))) stop(name, ": nonfinite values need an explicit policy.")
  if (nonnegative && any(values < 0)) stop(name, ": residuals are not detection counts.")
}

marker_summary <- function(expression, detection, metadata, group_key, sample_key,
                           group_order = NULL) {
  # The two matrices must carry identical gene and cell names, and metadata must
  # already be in exactly the same cell order. No silent matching or intersection.
  require_packages("Matrix")
  if (is.null(rownames(expression)) || is.null(colnames(expression)) ||
      anyDuplicated(rownames(expression)) || anyDuplicated(colnames(expression))) {
    stop("Expression matrix requires unique gene and cell names.")
  }
  if (!identical(dimnames(expression), dimnames(detection))) stop("Matrix dimnames are not aligned.")
  if (!identical(colnames(expression), rownames(metadata))) stop("Metadata cell order differs.")
  if (!all(c(group_key, sample_key) %in% names(metadata))) stop("Missing group or biological sample key.")
  if (anyNA(metadata[, c(group_key, sample_key), drop = FALSE])) stop("Missing group/sample IDs.")
  if (!nrow(expression) || !ncol(expression)) stop("Empty matrix.")
  check_matrix(expression, dim(detection), "expression", TRUE)
  check_matrix(detection, dim(expression), "detection", TRUE)
  groups <- as.character(metadata[[group_key]])
  if (is.null(group_order)) group_order <- unique(groups)
  if (anyDuplicated(group_order) || !all(groups %in% group_order)) stop("Invalid group_order.")
  ans <- lapply(group_order, function(g) {
    idx <- which(groups == g); n <- length(idx)
    mu <- if (n) Matrix::rowMeans(expression[, idx, drop = FALSE]) else rep(NA_real_, nrow(expression))
    frac <- if (n) Matrix::rowMeans(detection[, idx, drop = FALSE] > 0) else rep(NA_real_, nrow(expression))
    data.frame(group = g, gene = rownames(expression), mean_expression = as.numeric(mu),
               fraction_detected = as.numeric(frac), n_cells = n,
               n_samples = if (n) length(unique(metadata[[sample_key]][idx])) else 0L,
               row.names = NULL, stringsAsFactors = FALSE)
  })
  do.call(rbind, ans)
}

gene_zscore <- function(tab, value = "mean_expression", clip = NULL) {
  if (!is.null(clip) && (length(clip) != 1 || !is.finite(clip) || clip <= 0)) stop("Invalid clip.")
  tab$z_unclipped <- NA_real_
  for (gene in unique(tab$gene)) {
    ii <- which(tab$gene == gene); x <- tab[[value]][ii]; ok <- !is.na(x)
    if (!any(ok)) next
    mu <- mean(x[ok]); sd_pop <- sqrt(mean((x[ok] - mu)^2))
    tab$z_unclipped[ii[ok]] <- if (sd_pop == 0) 0 else (x[ok] - mu) / sd_pop
  }
  tab$z_display <- if (is.null(clip)) tab$z_unclipped else pmax(-clip, pmin(clip, tab$z_unclipped))
  tab
}

plot_marker_dot <- function(tab, group_order, gene_order, value, limits, colours,
                            max_size_mm = 3, value_label = value) {
  require_packages(c("ggplot2", "scales"))
  if (anyDuplicated(tab[, c("group", "gene")])) stop("Duplicate group-gene pairs.")
  if (any(tab$fraction_detected < 0 | tab$fraction_detected > 1, na.rm = TRUE)) stop("Invalid fraction.")
  if (length(limits) != 2 || limits[1] >= limits[2]) stop("Need increasing explicit limits.")
  if (!all(tab$group %in% group_order) || !all(tab$gene %in% gene_order)) stop("Incomplete category order.")
  tab$group <- factor(tab$group, levels = rev(group_order))
  tab$gene <- factor(tab$gene, levels = gene_order)
  tab$.plot_value <- tab[[value]]
  ggplot2::ggplot(tab, ggplot2::aes(x = gene, y = group)) +
    ggplot2::geom_point(ggplot2::aes(size = fraction_detected, colour = .plot_value), na.rm = TRUE) +
    ggplot2::scale_size_area(max_size = max_size_mm, limits = c(0, 1),
                             breaks = c(.25, .5, 1), labels = c("25%", "50%", "100%"),
                             name = "Detected cells") +
    ggplot2::scale_colour_gradientn(colours = colours, limits = limits,
                                    oob = scales::squish, name = value_label) +
    ggplot2::scale_x_discrete(drop = FALSE) + ggplot2::scale_y_discrete(drop = FALSE) +
    ggplot2::labs(x = NULL, y = NULL) + theme_sc() +
    ggplot2::theme(axis.text.x = ggplot2::element_text(angle = 45, hjust = 1),
                   axis.line = ggplot2::element_blank(), axis.ticks = ggplot2::element_blank())
}

affine_coordinates <- function(xy, transform) {
  xy <- as.matrix(xy); transform <- as.matrix(transform)
  if (ncol(xy) != 2 || !identical(dim(transform), c(3L, 3L))) stop("Need n x 2 and 3 x 3 matrices.")
  if (any(!is.finite(xy)) || any(!is.finite(transform))) stop("Nonfinite coordinates/transform.")
  if (!isTRUE(all.equal(as.numeric(transform[3, ]), c(0, 0, 1))) ||
      abs(det(transform[1:2, 1:2])) < .Machine$double.eps) stop("Not an invertible affine transform.")
  (cbind(xy, 1) %*% t(transform))[, 1:2, drop = FALSE]
}

plot_spatial_values <- function(tab, value, limits, colours, coordinate_unit,
                                y_axis_down, point_size_mm = .3, raster = FALSE) {
  require_packages(c("ggplot2", "scales"))
  if (!all(c("x", "y", "section_id", value) %in% names(tab))) stop("Required spatial columns missing.")
  if (anyNA(tab$section_id) || length(unique(tab$section_id)) != 1L) stop("One section per plot is required.")
  if (!coordinate_unit %in% c("um", "pixel")) stop("Declare unit as um or pixel.")
  if (length(limits) != 2 || any(!is.finite(limits)) || limits[1] >= limits[2] ||
      !is.finite(point_size_mm) || point_size_mm <= 0) stop("Invalid scale limits or point size.")
  if (any(!is.finite(as.matrix(tab[, c("x", "y", value), drop = FALSE])))) stop("Nonfinite spatial values.")
  tab$.plot_value <- tab[[value]]
  p <- ggplot2::ggplot(tab, ggplot2::aes(x = x, y = y, colour = .plot_value))
  if (raster) {
    require_packages("ggrastr")
    p <- p + ggrastr::geom_point_rast(size = point_size_mm, raster.dpi = 300)
  } else p <- p + ggplot2::geom_point(size = point_size_mm)
  p <- p + ggplot2::scale_colour_gradientn(colours = colours, limits = limits,
                                           oob = scales::squish, name = value) +
    ggplot2::coord_fixed() + theme_sc() +
    ggplot2::labs(x = paste0("x (", coordinate_unit, ")"), y = paste0("y (", coordinate_unit, ")"))
  if (y_axis_down) p <- p + ggplot2::scale_y_reverse()
  p
}

aggregate_transport <- function(coupling, source_groups, target_groups,
                                normalization = c("mass", "source_fraction")) {
  require_packages("Matrix"); normalization <- match.arg(normalization)
  if (!length(source_groups) || !length(target_groups) || anyNA(source_groups) || anyNA(target_groups)) {
    stop("Nonempty source/target group vectors required.")
  }
  check_matrix(coupling, c(length(source_groups), length(target_groups)), "coupling", TRUE)
  ss <- unique(as.character(source_groups)); tt <- unique(as.character(target_groups))
  a <- Matrix::sparseMatrix(i = seq_along(source_groups), j = match(source_groups, ss), x = 1,
                            dims = c(length(source_groups), length(ss)))
  b <- Matrix::sparseMatrix(i = seq_along(target_groups), j = match(target_groups, tt), x = 1,
                            dims = c(length(target_groups), length(tt)))
  out <- as.matrix(t(a) %*% coupling %*% b) # only small group x group output is dense
  dimnames(out) <- list(ss, tt)
  if (normalization == "source_fraction") {
    totals <- rowSums(out); out <- out / totals; out[totals == 0, ] <- NA_real_
  }
  out
}

export_ggplot <- function(plot, stem, provenance, source_tables = list(),
                          width_mm = 89, height_mm = 89, dpi = 300) {
  require_packages(c("ggplot2", "jsonlite", "svglite"))
  required <- c("data_source", "analysis_unit", "value_definition", "seed")
  if (!all(required %in% names(provenance))) stop("Missing required provenance fields.")
  if (any(c(width_mm, height_mm, dpi) <= 0)) stop("Positive dimensions/dpi required.")
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  pdf_device <- if (capabilities("cairo")) grDevices::cairo_pdf else function(...) grDevices::pdf(..., useDingbats = FALSE)
  ggplot2::ggsave(paste0(stem, ".pdf"), plot, device = pdf_device,
                   width = width_mm, height = height_mm, units = "mm")
  ggplot2::ggsave(paste0(stem, ".svg"), plot, device = svglite::svglite,
                   width = width_mm, height = height_mm, units = "mm")
  ggplot2::ggsave(paste0(stem, ".png"), plot, width = width_mm,
                   height = height_mm, units = "mm", dpi = dpi)
  for (nm in names(source_tables)) {
    if (basename(nm) != nm || nm %in% c("", ".", "..")) stop("Unsafe table name.")
    utils::write.csv(source_tables[[nm]], paste0(stem, "_", nm, ".csv"), row.names = FALSE)
  }
  provenance$session_info <- capture.output(utils::sessionInfo())
  provenance$width_mm <- width_mm; provenance$height_mm <- height_mm; provenance$dpi <- dpi
  provenance$pdf_cairo <- capabilities("cairo")
  jsonlite::write_json(provenance, paste0(stem, "_provenance.json"), pretty = TRUE,
                       auto_unbox = TRUE, null = "null")
  invisible(stem)
}
