# SOFTWARE QA ONLY. Run from the sc-figure-r skill directory.
# This smoke test has NOT been executed during authoring (Rscript unavailable).
source('scripts/compose_plan.R')
need(c('jsonlite','ggplot2','svglite'))
plan <- read_render_plan('assets/atlas.render_plan.json')
plan$spec$figure$id <- 'SOFTWARE_QA_ONLY'
plan$spec$figure$main_message <- 'NO BIOLOGICAL RESULT'
plan$spec$design$font_family <- 'sans'
for (i in seq_along(plan$spec$panels)) {
  plan$spec$panels[[i]]$renderer <- 'fixture'
  plan$spec$panels[[i]]$channels <- list(x='x',y='y')
  plan$spec$panels[[i]]$scale_ids <- list()
  plan$spec$panels[[i]]$spatial <- NULL
}
tables <- stats::setNames(lapply(plan$spec$datasets, function(d) {
  data.frame(id=c('TEST1','TEST2','TEST3'),x=c(1,2,3),y=c(0,1,0))
}), names(plan$spec$datasets))
registry <- list(fixture=function(ctx,tab) {
  p <- ggplot2::ggplot(tab,ggplot2::aes(x=x,y=y))+ggplot2::geom_point()+
    ggplot2::labs(x='Software test x',y='Software test y')+ggplot2::theme_classic(base_size=7)
  figure_panel(p,'ggplot')
})
out <- tempfile('figure-framework-qa-');dir.create(out)
record <- export_plan(plan,tables,registry,out)
stopifnot(!record$release_ready, file.exists(file.path(out,'SOFTWARE_QA_ONLY.pdf')))
cat('R composer smoke test passed; inspect exported files manually:',out,'\n')
