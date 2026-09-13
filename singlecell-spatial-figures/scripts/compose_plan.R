# FigureSpec v2 R backend. This file has NOT been executed in the authoring environment.
# Input: reviewed render_plan.json from the language-neutral planning stage.
# No Python process is invoked from R. Planning CLI is separately implemented in Python.
need <- function(pkgs) {
  missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing)) stop('Missing packages: ', paste(missing, collapse=', '))
}
read_render_plan <- function(path) {
  need('jsonlite')
  plan <- jsonlite::fromJSON(path, simplifyVector=FALSE)
  if (!identical(plan$plan_version, '2.0') ||
      !identical(plan$status, 'preflight_passed_not_reviewed')) stop('Expected a v2 preflight plan.')
  if (is.null(plan$boxes) || is.null(plan$spec$panels)) stop('Incomplete render plan.')
  plan
}
# Each registered renderer returns this object; no eval(parse()) or dynamic source().
figure_panel <- function(object, system=c('ggplot','grob','heatmap'), notes=character()) {
  list(object=object, system=match.arg(system), notes=notes)
}
validate_tables <- function(spec, tables) {
  if (any(!grepl('^[A-Za-z][A-Za-z0-9_-]*$',names(spec$datasets)))) stop('Unsafe data IDs.')
  if (!all(names(spec$datasets) %in% names(tables))) stop('Missing reviewed tables.')
  for (did in names(spec$datasets)) {
    d <- spec$datasets[[did]]; tab <- tables[[did]]; keys <- unlist(d$keys, use.names=FALSE)
    if (!is.data.frame(tab) || !nrow(tab) || anyDuplicated(names(tab))) stop(did, ': invalid table.')
    required <- keys
    for (p in spec$panels) if (p$data_id==did) {
      required <- union(required, unlist(p$channels, use.names=FALSE))
      if (!is.null(p$spatial)) required <- union(required, p$spatial$section_column)
    }
    if (!all(required %in% names(tab))) stop(did, ': missing required columns.')
    if (any(vapply(keys,function(k) any(trimws(as.character(tab[[k]]))=='',na.rm=TRUE),logical(1))) || anyNA(tab[,keys,drop=FALSE]) || anyDuplicated(tab[,keys,drop=FALSE])) stop(did, ': invalid primary key.')
  }
  invisible(TRUE)
}
# This must run on the final-size device. Heatmap capture size is the CONTENT box,
# not the whole Figure, avoiding device-dependent annotation displacement.
draw_panel <- function(result, ctx) {
  if (!is.list(result) || !all(c('object','system') %in% names(result))) stop('Return figure_panel().')
  if (result$system=='ggplot') {
    need('ggplot2')
    styled <- result$object + ggplot2::theme(
      text=ggplot2::element_text(family=ctx$font_family,size=ctx$spec$design$font_pt),
      axis.text=ggplot2::element_text(size=ctx$spec$design$font_pt),
      legend.text=ggplot2::element_text(size=ctx$spec$design$font_pt),
      legend.title=ggplot2::element_text(size=ctx$spec$design$font_pt))
    grid::grid.draw(ggplot2::ggplotGrob(styled))
  } else if (result$system=='grob') {
    if (!grid::is.grob(result$object)) stop('Expected a grid grob.')
    grid::grid.draw(result$object)
  } else if (result$system=='heatmap') {
    need('ComplexHeatmap')
    captured <- grid::grid.grabExpr(
      ComplexHeatmap::draw(result$object, newpage=FALSE),
      width=ctx$width_mm/25.4, height=ctx$height_mm/25.4)
    grid::grid.draw(captured)
  } else stop('Unsupported graphics system.')
}
compose_on_device <- function(plan, tables, registry) {
  spec <- plan$spec; validate_tables(spec,tables)
  panels <- stats::setNames(spec$panels, vapply(spec$panels, `[[`, '', 'id'))
  required <- vapply(spec$panels, `[[`, '', 'renderer')
  if (!all(required %in% names(registry))) stop('Register missing renderers explicitly: ',
    paste(setdiff(required,names(registry)),collapse=', '))
  if (!all(vapply(registry[unique(required)],is.function,logical(1)))) stop('Registry entries must be functions.')
  fw <- spec$figure$width_mm; fh <- spec$figure$height_mm
  grid::grid.newpage(); notes <- list()
  for (pid in unlist(plan$render_order, use.names=FALSE)) {
    p <- panels[[pid]]; b <- as.numeric(unlist(plan$boxes[[pid]]$content_mm));
    outer <- as.numeric(unlist(plan$boxes[[pid]]$outer_mm))
    if (length(b)!=4 || any(!is.finite(b)) || min(b[3:4])<=0) stop('Invalid physical panel box.')
    ctx <- list(panel=p, spec=spec, width_mm=b[3], height_mm=b[4],
                scales=spec$scales, font_family=spec$design$font_family)
    result <- registry[[p$renderer]](ctx, tables[[p$data_id]])
    grid::pushViewport(grid::viewport(x=b[1]/fw,y=1-b[2]/fh,
      width=b[3]/fw,height=b[4]/fh,just=c('left','top'),clip='off'))
    tryCatch(draw_panel(result,ctx), finally=grid::popViewport())
    grid::grid.text(pid,x=outer[1]/fw,y=1-(outer[2]+1)/fh,just=c('left','top'),
      gp=grid::gpar(fontsize=spec$design$tag_pt,fontface='bold',fontfamily=spec$design$font_family))
    notes[[pid]] <- result$notes
  }
  notes
}
export_plan <- function(plan,tables,registry,directory,formats=c('pdf','svg','png')) {
  need('jsonlite')
  if (!all(formats %in% c('pdf','svg','png')) || !length(formats)) stop('Unsupported output format.')
  if ('svg' %in% formats) need('svglite')
  dir.create(directory,recursive=TRUE,showWarnings=FALSE)
  requested_font <- plan$spec$design$font_family
  available <- if (requireNamespace('systemfonts',quietly=TRUE)) unique(systemfonts::system_fonts()$family) else character()
  fallback <- plan$spec$design$fallback_font
  resolved_font <- if (requested_font %in% available) requested_font else if (fallback %in% available) fallback else 'sans'
  if (!identical(resolved_font,requested_font)) warning('Unverified requested font; using ',resolved_font,'. Check the exported font.')
  plan$spec$design$font_family <- resolved_font
  f <- plan$spec$figure; stem <- file.path(directory,f$id); notes <- NULL
  for (fmt in formats) {
    path <- paste0(stem,'.',fmt)
    if (fmt=='pdf') grDevices::cairo_pdf(path,width=f$width_mm/25.4,height=f$height_mm/25.4)
    if (fmt=='svg') svglite::svglite(path,width=f$width_mm/25.4,height=f$height_mm/25.4)
    if (fmt=='png') grDevices::png(path,width=f$width_mm,height=f$height_mm,units='mm',res=300,type='cairo')
    notes <- tryCatch(compose_on_device(plan,tables,registry),finally=grDevices::dev.off())
  }
  for (did in names(tables)) utils::write.csv(tables[[did]],paste0(stem,'_',did,'.csv'),row.names=FALSE)
  writeLines(capture.output(utils::sessionInfo()),file.path(directory,'sessionInfo.txt'))
  outputs <- c(paste0(stem,'.',formats),paste0(stem,'_',names(tables),'.csv'),file.path(directory,'sessionInfo.txt'))
  # MD5 records change detection, not security or publisher compliance.
  hashes <- as.list(tools::md5sum(outputs[!dir.exists(outputs)]))
  record <- list(status='DRAFT',requested_font=requested_font,grid_font=resolved_font,exported_font_review='pending',plan=plan,panel_notes=notes,output_md5=hashes,
    automatic_geometry_review='not_implemented_in_R_backend',
    scientific_review='pending',manual_visual_review='pending',release_ready=FALSE)
  jsonlite::write_json(record,file.path(directory,'provenance_and_qa.json'),pretty=TRUE,auto_unbox=TRUE)
  writeLines(capture.output(utils::sessionInfo()),file.path(directory,'sessionInfo.txt'))
  invisible(record)
}
