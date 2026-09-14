# v3 R bridge: consume measured geometry and compiled scalar-to-color mappings.
# This implementation does not claim pixel identity with Matplotlib. Run the
# same Python PDF/carrier auditor on its final artifact. Native R execution is
# NOT verified in the authoring environment; see CAPABILITIES.json / QA_REPORT.md.
render_v3_R <- function(plan_path, output) {
  if (!requireNamespace('jsonlite', quietly=TRUE)) stop('Install jsonlite in the project environment.')
  plan <- jsonlite::fromJSON(plan_path, simplifyVector=FALSE)
  if (!identical(plan$version, '3.0')) stop('Expected render_plan_v3.json.')
  root <- normalizePath(dirname(plan_path), mustWork=TRUE)
  spec <- plan$spec; fw <- spec$figure$width_mm; fh <- spec$figure$height_mm
  font <- spec$design$font_family; fontsize <- spec$design$font_pt
  policy <- spec$visual; lineheight <- if (is.null(policy$line_spacing)) 1.15 else policy$line_spacing
  bg <- if (is.null(policy$background)) '#ffffff' else policy$background
  vec <- function(x) unlist(x, use.names=FALSE)
  txt <- function(label,x,y,size=fontsize,just=c('left','top'),...) {
    if (any(grepl('$',label,fixed=TRUE))) stop('TeX math is not translated by the R bridge; use an explicit native plotmath renderer.')
    grid::grid.text(label,x=grid::unit(x,'mm'),y=grid::unit(fh-y,'mm'),just=just,
      gp=grid::gpar(fontfamily=font,fontsize=size,lineheight=lineheight),...)
  }
  rect <- function(x,y,w,h,fill,col=NA) grid::grid.rect(x=grid::unit(x,'mm'),y=grid::unit(fh-y,'mm'),
    width=grid::unit(w,'mm'),height=grid::unit(h,'mm'),just=c('left','top'),gp=grid::gpar(fill=fill,col=col))
  circle <- function(x,y,area,fill,col=NA) grid::grid.circle(x=grid::unit(x,'mm'),y=grid::unit(fh-y,'mm'),
    r=grid::unit(sqrt(area)/2*25.4/72,'mm'),gp=grid::gpar(fill=fill,col=col,lwd=.5))
  read_prepared <- function(pid) {
    path <- normalizePath(file.path(root,plan$prepared[[pid]]),mustWork=TRUE)
    if (!startsWith(path,paste0(root,.Platform$file.sep))) stop('Prepared path escapes plan directory.')
    utils::read.csv(path,stringsAsFactors=FALSE,check.names=FALSE,na.strings='')
  }
  draw_guide <- function(g) {
    b <- vec(g$box_mm);x <- b[1];y <- b[2];w <- b[3];h <- b[4];size <- g$font_pt
    txt(g$title,x,y,size)
    if (g$channel=='color') {
      pal <- plan$palettes[[g$scale_id]];colors <- vec(pal$colors);n <- length(colors)
      y <- y+g$`_title_h`;length <- g$`_length`;th <- g$`_thickness`
      if (g$orientation=='vertical') {
        y <- y+size*25.4/144
        for (j in seq_len(n)) rect(x,y+length*(1-j/n),th,length/n,colors[j])
        for (j in seq_along(g$ticks)) txt(g$labels[[j]],x+th+1,y+length*(1-g$positions[[j]]),size,just=c('left','center'))
      } else {
        x <- x+max(nchar(vec(g$labels)))*size*.08
        for (j in seq_len(n)) rect(x+(j-1)/n*length,y,length/n,th,colors[j])
        for (j in seq_along(g$ticks)) txt(g$labels[[j]],x+length*g$positions[[j]],y+th+1,size,just=c('center','top'))
      }
      if (identical(pal$out_of_range,'extend')) {
        poly <- function(xx,yy,fill) grid::grid.polygon(x=grid::unit(xx,'mm'),y=grid::unit(fh-yy,'mm'),gp=grid::gpar(fill=fill,col=NA))
        if(g$orientation=='vertical') {
          poly(c(x,x+th/2,x+th),c(y,y-1,y),pal$over)
          poly(c(x,x+th/2,x+th),c(y+length,y+length+1,y+length),pal$under)
        } else {
          poly(c(x,x-1,x),c(y,y+th/2,y+th),pal$under)
          poly(c(x+length,x+length+1,x+length),c(y,y+th/2,y+th),pal$over)
        }
      }
      if (isTRUE(g$missing)) {rect(b[1],b[2]+h-3,2,2,pal$bad);txt('Missing / masked',b[1]+3,b[2]+h-3,size)}
    } else {
      for (j in seq_along(g$labels)) {
        row <- (j-1) %/% g$`_ncol`;col <- (j-1) %% g$`_ncol`
        xx <- x+col*g$`_cell_w`;yy <- y+g$`_title_h`+(row+.5)*g$`_line_h`
        area <- if(g$channel=='size') g$max_area_pt2*g$ticks[[j]] else 12
        fill <- if(g$channel=='size') NA else g$colors[[j]]
        circle(xx+1+g$`_symbol_mm`/2,yy,area,fill,if(g$channel=='size') 'black' else NA)
        txt(g$labels[[j]],xx+g$`_symbol_mm`+3,yy,size,just=c('left','center'))
      }
    }
  }
  dir.create(dirname(output),recursive=TRUE,showWarnings=FALSE)
  grDevices::cairo_pdf(output,width=fw/25.4,height=fh/25.4,family=font)
  on.exit(grDevices::dev.off(),add=TRUE)
  grid::grid.newpage();rect(0,0,fw,fh,bg)
  for (p in spec$panels) {
    pid <- p$id;lay <- plan$layouts[[pid]];b <- vec(lay$plot_mm);d <- read_prepared(pid);ch <- p$channels
    tx <- plan$coordinates[[pid]];xl <- vec(tx$xlim);yl <- vec(tx$ylim)
    xpos <- function(x) b[1]+(x-xl[1])/diff(xl)*b[3]
    ypos <- function(y) b[2]+(1-(y-yl[1])/diff(yl))*b[4]
    kind <- p$renderer
    if(!is.null(lay$title) && nzchar(lay$title)) {tt <- vec(lay$title_mm);txt(lay$title,tt[1],tt[2])}
    if (kind %in% c('embedding','spatial')) {
      x <- xpos(d[[ch$x]]);y <- ypos(d[[ch$y]])
      area <- if(!is.null(p$marks$area_pt2)) p$marks$area_pt2 else if(kind=='embedding') 3 else 4
      circle(x,y,area,d[['_v3_color']])
    } else if (kind %in% c('marker_dot','annotated_heatmap')) {
      rows <- unique(d[[ch$y]]);cols <- unique(d[[ch$x]]);nr <- length(rows);nc <- length(cols)
      bad <- plan$palettes[[p$scale_ids$color]]$bad
      size_guide <- NULL
      for (ll in plan$layouts) for(g in ll$guides) if(g$channel=='size' && pid %in% vec(g$panels)) size_guide <- g
      for(i in seq_len(nr)) for(j in seq_len(nc)) {
        idx <- which(d[[ch$y]]==rows[i] & d[[ch$x]]==cols[j])
        fill <- if(length(idx)) d[['_v3_color']][idx] else bad
        xx <- b[1]+(j-.5)/nc*b[3];yy <- b[2]+(i-.5)/nr*b[4]
        if(kind=='annotated_heatmap') {
          rect(b[1]+(j-1)/nc*b[3],b[2]+(i-1)/nr*b[4],b[3]/nc,b[4]/nr,fill)
          if(!is.null(ch$effect) && length(idx) && !is.na(d[[ch$effect]][idx])) {
            # Text contrast selection uses the same simple RGB screening as Python.
            rgb <- grDevices::col2rgb(fill)/255;ink <- if(sum(rgb*c(.2126,.7152,.0722))>.55) 'black' else 'white'
            grid::grid.text(as.character(d[[ch$effect]][idx]),x=grid::unit(xx,'mm'),y=grid::unit(fh-yy,'mm'),
              gp=grid::gpar(fontfamily=font,fontsize=fontsize,col=ink))
          }
        } else {
          fraction <- if(length(idx)) d[[ch$size]][idx] else NA_real_
          missing <- is.na(fraction) || !length(idx) || isTRUE(as.logical(d[['_v3_missing']][idx]))
          area <- size_guide$max_area_pt2*if(missing) .25 else fraction
          circle(xx,yy,area,fill)
          if(missing) txt('x',xx,yy,fontsize,just=c('center','center'))
        }
      }
      for(j in seq_len(nc)) txt(lay$xlabels[[j]],b[1]+(j-.5)/nc*b[3],b[2]+b[4]+1,just=c('center','top'))
      for(i in seq_len(nr)) txt(lay$ylabels[[i]],b[1]-1,b[2]+(i-.5)/nr*b[4],just=c('right','center'))
      if(kind=='annotated_heatmap') {
        # Annotation values/indices were validated upstream. Negative values need
        # a native R adapter rather than this count-track bridge.
        top <- vec(lay$column_track_mm);side <- vec(lay$row_track_mm)
        cm <- vapply(cols,function(c) d[[ch$col_metric]][match(c,d[[ch$x]])],numeric(1))
        rm <- vapply(rows,function(r) d[[ch$row_metric]][match(r,d[[ch$y]])],numeric(1))
        if(any(!is.finite(c(cm,rm))) || any(c(cm,rm)<0)) stop('R bridge annotation tracks require nonnegative finite values.')
        for(j in seq_len(nc)) {hh <- cm[j]/max(c(cm,1))*top[4];rect(top[1]+(j-.9)/nc*top[3],top[2]+top[4]-hh,.8/nc*top[3],hh,'#555555')}
        for(i in seq_len(nr)) rect(side[1],side[2]+(i-.9)/nr*side[4],rm[i]/max(c(rm,1))*side[3],.8/nr*side[4],'#555555')
      }
    } else stop('Renderer is not implemented in the R bridge: ',kind)
    for(g in lay$guides) draw_guide(g)
    outer <- vec(lay$outer_mm);txt(pid,outer[1],outer[2]+1,spec$design$tag_pt)
  }
  invisible(list(status='rendered_unreviewed',pdf=output,next_step='render_v3.py inspect-pdf + carrier + human review'))
}
if(sys.nframe()==0L) {
  args <- commandArgs(trailingOnly=TRUE)
  if(length(args)!=2) stop('Usage: Rscript render_v3.R render_plan_v3.json output.pdf')
  render_v3_R(args[1],args[2])
}
