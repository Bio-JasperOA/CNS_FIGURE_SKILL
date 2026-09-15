# R wrapper to the same Python implementation. Not a native R plotting backend.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 4L) stop("Usage: Rscript render_from_R.R KIND INPUT CONFIG OUTPUT [MODE]")
file_arg <- grep("^--file=", commandArgs(), value = TRUE)
if (length(file_arg) != 1L) stop("Cannot resolve wrapper path")
here <- dirname(normalizePath(sub("^--file=", "", file_arg)))
python <- Sys.getenv("CNS_PYTHON", unset = "python")
mode <- if (length(args) >= 5L) args[[5]] else "advanced"
call_args <- c(file.path(here, "render.py"), "plot", "--kind", args[[1]],
               "--input", args[[2]], "--config", args[[3]], "--out", args[[4]], "--mode", mode)
status <- system2(python, vapply(call_args, shQuote, character(1)))
if (status != 0L) stop(paste("Python rendering failed, exit code", status))
