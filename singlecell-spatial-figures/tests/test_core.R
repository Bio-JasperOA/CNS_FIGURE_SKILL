# Artificial software test fixtures; these are NOT biological results.
# This script was supplied but NOT executed during package authoring (no Rscript).
args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_dir <- if (length(file_arg)) dirname(normalizePath(sub("^--file=", "", file_arg[1]))) else "tests"
source(file.path(script_dir, "..", "scripts", "figure_core.R"))
source(file.path(script_dir, "..", "scripts", "complex_recipes.R"))
expect_error <- function(expr) {
  raised <- tryCatch({ force(expr); FALSE }, error = function(e) TRUE)
  stopifnot(raised)
}
require_packages("Matrix")
x <- matrix(c(0,2, 2,0, 4,4), nrow = 2,
            dimnames = list(c("g1", "g2"), c("c1", "c2", "c3")))
md <- data.frame(cell_type=c("A","A","B"), sample_id=c("D1","D2","D1"),
                 row.names=colnames(x))
for (sparse_input in c(FALSE, TRUE)) {
  xx <- if (sparse_input) Matrix::Matrix(x, sparse=TRUE) else x
  tab <- marker_summary(xx, xx, md, "cell_type", "sample_id", c("A","B","C"))
  stopifnot(all(tab$mean_expression[tab$group=="A"] == 1))
  stopifnot(all(tab$fraction_detected[tab$group=="A"] == .5))
  stopifnot(all(tab$n_samples[tab$group=="A"] == 2))
  stopifnot(all(is.na(tab$mean_expression[tab$group=="C"])))
}
expect_error(marker_summary(x, x, md[3:1, ], "cell_type", "sample_id"))
negative <- x; negative[1,1] <- -1
expect_error(marker_summary(negative, x, md, "cell_type", "sample_id"))
z <- gene_zscore(data.frame(gene=c("g","g","c","c"), mean_expression=c(1,3,2,2)))
stopifnot(isTRUE(all.equal(z$z_unclipped, c(-1,1,0,0))))
p <- Matrix::Matrix(matrix(c(1,2,3,4,5,6), nrow=3, byrow=TRUE), sparse=TRUE)
f <- aggregate_transport(p, c("A","A","B"), c("X","Y"))
stopifnot(sum(f)==sum(p), all(f[1, ]==c(4,6)), all(f[2, ]==c(5,6)))
xy <- matrix(c(1,2,3,4), ncol=2, byrow=TRUE)
a <- matrix(c(2,0,10,0,-1,5,0,0,1), nrow=3, byrow=TRUE)
stopifnot(isTRUE(all.equal(unname(affine_coordinates(xy,a)), matrix(c(12,3,16,1),ncol=2,byrow=TRUE))))
props <- matrix(c(.2,.3,.5), nrow=1, dimnames=list("s1",c("A","B","C")))
collapsed <- collapse_proportions(props, "A")
stopifnot(abs(sum(collapsed)-1)<1e-12, collapsed[1,"Other"]==.8)
expect_error(collapse_proportions(props*2, "A"))
cat("Core numerical tests passed in this R session.\n")
cat("These tests do not validate rendering or optional package APIs. Inspect those separately.\n")
print(sessionInfo())
