# Optional native R helper. No implicit install, interpolation or color recycling.
# Palette tables are the SAME RGB8 data used by Python. Native execution not verified here.
.cns_palette_dir <- local({
  source_file <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (is.null(source_file)) stop("Load palette_presets.R with source() so its assets can be found.")
  normalizePath(file.path(dirname(source_file), "..", "assets", "palettes"), mustWork = TRUE)
})

cns_palette_entry <- function(id, assets = .cns_palette_dir) {
  if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Install jsonlite in the project environment first.")
  if (length(id) != 1L || is.na(id) || !grepl("^[CMSDY][0-9]{2}(\\.[a-z]+)?$", id)) stop("Invalid palette ID.")
  catalog <- jsonlite::fromJSON(file.path(assets, "index.json"), simplifyVector = FALSE)
  found <- Filter(function(p) identical(p$id, sub("\\..*$", "", id)), catalog$presets)
  if (length(found) != 1L) stop("Unknown palette ID.")
  p <- found[[1L]]
  if (!is.null(p$variants)) {
    v <- Filter(function(x) identical(x$id, id), p$variants)
    if (length(v) != 1L) stop("Select C06.green, C06.orange, C06.purple or C06.blue explicitly.")
    for (key in names(v[[1L]])) p[[key]] <- v[[1L]][[key]]
  } else if (!identical(id, p$id)) stop("This preset has no variants.")
  if (!grepl("^(categorical|sequential_single|[MDY][0-9]{2})\\.json$", p$file)) stop("Invalid palette table path.")
  table <- jsonlite::fromJSON(file.path(assets, p$file), simplifyVector = FALSE)
  rgb <- table[[id]]
  if (!is.null(rgb) && startsWith(rgb, "gz-delta8:")) {
    delta <- as.integer(memDecompress(jsonlite::base64_dec(substring(rgb, 11L)), type = "gzip"))
    if (length(delta) != 3L * p$n_colors) stop("Wrong decoded RGB8 length.")
    if (length(delta) > 3L) for (i in seq.int(4L, length(delta))) delta[i] <- (delta[i] + delta[i - 3L]) %% 256L
    rgb <- paste(sprintf("%02X", delta), collapse = "")
  }
  if (is.null(rgb) || !grepl("^([0-9A-F]{6})+$", rgb) || nchar(rgb) != 6L * p$n_colors) stop("Malformed RGB8 table.")
  starts <- seq.int(1L, nchar(rgb), by = 6L)
  p$colors <- paste0("#", substring(rgb, starts, starts + 5L))
  if (p$family == "categorical" && anyDuplicated(p$colors)) stop("Category palette repeats colors.")
  p
}

cns_palette <- function(id, n = NULL, assets = .cns_palette_dir) {
  p <- cns_palette_entry(id, assets)
  if (is.null(n)) return(p$colors)
  if (!is.numeric(n) || length(n) != 1L || !is.finite(n) || n != floor(n) || n < 1) stop("n must be a positive integer.")
  if (p$family == "categorical") {
    if (n > length(p$colors)) stop("Preset capacity exceeded; do not recycle or interpolate colors.")
    return(p$colors[seq_len(n)])
  }
  if (n < 2) stop("Scalar colors require at least two sample positions.")
  indices <- pmin(length(p$colors) - 1L, floor((seq_len(n) - 1L) * length(p$colors) / (n - 1L))) + 1L
  p$colors[indices]
}

cns_color_map <- function(id, reference_levels, existing = NULL, assets = .cns_palette_dir) {
  p <- cns_palette_entry(id, assets)
  if (p$family != "categorical") stop("Use a categorical preset.")
  valid_levels <- function(x) is.character(x) && length(x) > 0L && !anyNA(x) && all(nzchar(trimws(x))) && !anyDuplicated(x)
  if (!valid_levels(reference_levels)) stop("Reference levels must be unique nonempty strings.")
  result <- existing
  if (is.null(result)) result <- setNames(character(), character())
  if (length(result) && (!valid_levels(names(result)) || anyNA(result) || anyDuplicated(toupper(result)) || !all(toupper(result) %in% p$colors))) stop("Invalid existing mapping for this preset.")
  available <- p$colors[!p$colors %in% toupper(result)]
  new <- reference_levels[!reference_levels %in% names(result)]
  if (length(new) > length(available)) stop("Insufficient unused colors.")
  if (length(new)) result <- c(result, setNames(available[seq_along(new)], new))
  result
}
