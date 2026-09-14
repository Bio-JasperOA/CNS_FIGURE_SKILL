# R entry point to the shared, tested Python renderer. NOT a native ggplot2 backend.
# Rscript render_from_R.R paired reviewed.csv config.json output/Fig1 advanced
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 4L || length(args) > 5L) stop('Arguments: kind input.csv config.json output_stem [minimal|advanced]')
mode <- if (length(args) == 5L) args[[5]] else 'advanced'
if (!mode %in% c('minimal','advanced')) stop('Unknown mode')
python <- Sys.which('python')
if (!nzchar(python)) python <- Sys.which('python3')
if (!nzchar(python)) stop('Python is required by this shared-renderer entry point')
file_arg <- grep('^--file=', commandArgs(), value=TRUE)
script_dir <- dirname(normalizePath(sub('^--file=', '', file_arg[[1]])))
code <- file.path(script_dir,'render.py')
status <- system2(python, args=shQuote(c(code,'plot','--kind',args[[1]],'--input',normalizePath(args[[2]]),
  '--config',normalizePath(args[[3]]),'--out',args[[4]],'--mode',mode)))
if (status != 0L) stop('Shared renderer failed; inspect its error before editing data or hiding annotations')
