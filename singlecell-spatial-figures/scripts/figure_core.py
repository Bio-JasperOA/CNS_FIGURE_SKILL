"""Original, evidence-informed figure utilities; not a reproduction of any paper.

Matrices are cells x genes. Never pass integrated residuals as detection counts.
All plotting functions accept an Axes and return artists; they do not run analysis.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
from typing import Any, Mapping, Sequence
import warnings

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Text
import numpy as np
import pandas as pd
from scipy import sparse


@dataclass(frozen=True)
class FigureStyle:
    # House defaults, NOT universal publisher specifications.
    font: str = "Arial"
    fallback_font: str = "DejaVu Sans"
    font_pt: float = 7.0
    label_pt: float = 8.0
    line_pt: float = 0.6
    width_mm: float = 89.0
    height_mm: float = 89.0
    dpi: int = 300


def apply_style(style: FigureStyle = FigureStyle()) -> str:
    """Set typography/export defaults and report the font actually available."""
    if min(style.font_pt, style.line_pt, style.width_mm, style.height_mm, style.dpi) <= 0:
        raise ValueError("Font, line width, dimensions and dpi must be positive.")
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = style.font if style.font in available else style.fallback_font
    if chosen not in available:
        raise ValueError(f"Neither requested nor fallback font is installed: {style}")
    if chosen != style.font:
        warnings.warn(f"{style.font} is unavailable; using {chosen}. Record this in provenance.")
    mpl.rcParams.update({
        "font.family": chosen, "font.size": style.font_pt,
        "axes.labelsize": style.font_pt, "axes.titlesize": style.font_pt,
        "xtick.labelsize": style.font_pt, "ytick.labelsize": style.font_pt,
        "legend.fontsize": style.font_pt, "axes.linewidth": style.line_pt,
        "lines.linewidth": style.line_pt, "xtick.major.width": style.line_pt,
        "ytick.major.width": style.line_pt, "pdf.fonttype": 42,
        "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.dpi": style.dpi,
        "figure.figsize": (style.width_mm / 25.4, style.height_mm / 25.4),
    })
    return chosen


def validate_palette(labels: Sequence[str], palette: Mapping[str, str]) -> None:
    """A category missing a registered colour is an error, not a new default."""
    if pd.isna(labels).any():
        raise ValueError("Missing category labels require an explicit policy.")
    missing = sorted(set(map(str, labels)) - set(palette))
    if missing:
        raise ValueError(f"Missing palette entries: {missing}")
    for name in set(map(str, labels)):
        if not mpl.colors.is_color_like(palette[name]):
            raise ValueError(f"Invalid colour for {name}: {palette[name]}")


def _check_matrix(matrix: Any, shape: tuple[int, int], name: str,
                  nonnegative: bool = False) -> None:
    if getattr(matrix, "shape", None) != shape:
        raise ValueError(f"{name}: expected {shape}, got {getattr(matrix, 'shape', None)}")
    values = matrix.data if sparse.issparse(matrix) else np.asarray(matrix)
    if not np.isfinite(values).all():
        raise ValueError(f"{name} contains missing/infinite values; resolve explicitly.")
    if nonnegative and (values < 0).any():
        raise ValueError(f"{name} must be nonnegative; residuals are not detection counts.")


def marker_summary(expression: Any, detection: Any, obs: pd.DataFrame,
                   gene_names: Sequence[str], group_key: str,
                   sample_key: str, group_order: Sequence[str] | None = None) -> pd.DataFrame:
    """Cell-weighted descriptive mean + detection fraction, including zeros.

    expression: declared nonnegative normalised expression (e.g. log1p).
    detection: aligned raw counts or other explicitly justified detection matrix.
    obs: same row order as BOTH matrices. sample_key is a biological replicate ID.
    Unobserved requested groups are returned as NA, not zero.
    These summaries are NOT a donor-level hypothesis test.
    """
    genes = list(map(str, gene_names))
    if not obs.index.is_unique or not pd.Index(genes).is_unique:
        raise ValueError("Cell IDs and gene names must be unique.")
    if len(obs) == 0 or not genes:
        raise ValueError("Input must contain cells and genes.")
    if group_key not in obs or sample_key not in obs:
        raise KeyError("Both group and biological sample columns are required.")
    if obs[[group_key, sample_key]].isna().any().any():
        raise ValueError("Missing group/sample IDs require an explicit handling policy.")
    shape = (len(obs), len(genes))
    _check_matrix(expression, shape, "expression", nonnegative=True)
    _check_matrix(detection, shape, "detection", nonnegative=True)
    expression = expression.tocsr() if sparse.issparse(expression) else np.asarray(expression)
    detection = detection.tocsr() if sparse.issparse(detection) else np.asarray(detection)
    labels = obs[group_key].astype(str).to_numpy()
    order = list(map(str, group_order)) if group_order is not None else list(pd.unique(labels))
    if len(set(order)) != len(order) or not set(labels).issubset(order):
        raise ValueError("group_order must be unique and include every observed group.")
    parts = []
    for group in order:
        mask = labels == group
        n = int(mask.sum())
        if n:
            means = np.asarray(expression[mask].mean(axis=0)).ravel()
            fractions = np.asarray((detection[mask] > 0).mean(axis=0)).ravel()
            ns = int(obs.loc[mask, sample_key].nunique())
        else:
            means = fractions = np.full(len(genes), np.nan)
            ns = 0
        parts.append(pd.DataFrame({"group": group, "gene": genes,
                                   "mean_expression": means, "fraction_detected": fractions,
                                   "n_cells": n, "n_samples": ns}))
    return pd.concat(parts, ignore_index=True)


def gene_zscore(summary: pd.DataFrame, value: str = "mean_expression",
                clip: float | None = None) -> pd.DataFrame:
    """Z-score across observed groups within each gene; population SD (ddof=0).

    Constant genes -> zero; absent groups -> NA. Keep z_unclipped for source data.
    """
    if clip is not None and clip <= 0:
        raise ValueError("clip must be positive.")
    out = summary.copy()
    def zscore(s: pd.Series) -> pd.Series:
        sd = s.std(ddof=0)
        if not np.isfinite(sd) or sd == 0:
            return pd.Series(np.where(s.notna(), 0.0, np.nan), index=s.index)
        return (s - s.mean()) / sd
    out["z_unclipped"] = out.groupby("gene", sort=False)[value].transform(zscore)
    out["z_display"] = out["z_unclipped"].clip(-clip, clip) if clip is not None else out["z_unclipped"]
    return out


def plot_marker_dot(ax: Axes, summary: pd.DataFrame, group_order: Sequence[str],
                    gene_order: Sequence[str], *, value: str,
                    norm: mpl.colors.Normalize, cmap: Any,
                    max_area_pt2: float = 45.0):
    """Dot AREA is proportional to detection fraction; colour scale is explicit.

    NA/absent groups and zero detection create no dot; annotate absence separately.
    The caller must add the returned mappable's colourbar and an area legend.
    """
    if (not len(group_order) or not len(gene_order) or
            len(set(group_order)) != len(group_order) or len(set(gene_order)) != len(gene_order)):
        raise ValueError("Group/gene orders must be nonempty and unique.")
    if (not set(summary["group"]).issubset(group_order) or
            not set(summary["gene"]).issubset(gene_order)):
        raise ValueError("Plot orders must include all supplied groups and genes.")
    if summary.duplicated(["group", "gene"]).any():
        raise ValueError("Each group-gene pair must be unique.")
    if max_area_pt2 <= 0:
        raise ValueError("max_area_pt2 must be positive.")
    index = pd.MultiIndex.from_product([group_order, gene_order], names=["group", "gene"])
    table = summary.set_index(["group", "gene"]).reindex(index)
    frac = table.fraction_detected.to_numpy(dtype=float)
    if np.any((frac < 0) | (frac > 1)):
        raise ValueError("Detection fractions must be in [0,1].")
    vals = table[value].to_numpy(dtype=float)
    x = np.tile(np.arange(len(gene_order)), len(group_order))
    y = np.repeat(np.arange(len(group_order)), len(gene_order))
    good = np.isfinite(vals) & np.isfinite(frac)
    artist = ax.scatter(x[good], y[good], s=max_area_pt2 * frac[good],
                        c=vals[good], norm=norm, cmap=cmap, linewidths=0)
    ax.set_xticks(np.arange(len(gene_order)), gene_order, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(group_order)), group_order)
    ax.set_xlim(-0.6, len(gene_order) - 0.4)
    ax.set_ylim(len(group_order) - 0.4, -0.6)
    ax.tick_params(length=0)
    return artist


def plot_embedding(ax: Axes, coordinates: np.ndarray, labels: Sequence[str],
                   palette: Mapping[str, str], *, seed: int = 0, size: float = 1.5):
    """Deterministic random draw order; use the SAME embedding across comparisons."""
    xy = np.asarray(coordinates, dtype=float)
    if pd.isna(labels).any() or size <= 0:
        raise ValueError("Nonmissing labels and positive point size are required.")
    labels = np.asarray(labels, dtype=str)
    if xy.shape != (len(labels), 2) or not np.isfinite(xy).all():
        raise ValueError("Expected finite n x 2 coordinates aligned to labels.")
    validate_palette(labels, palette)
    order = np.random.default_rng(seed).permutation(len(labels))
    artist = ax.scatter(xy[order, 0], xy[order, 1], s=size,
                        c=[palette[x] for x in labels[order]],
                        linewidths=0, rasterized=True)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("UMAP 1"); ax.set_ylabel("UMAP 2")
    return artist


def affine_coordinates(coordinates: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Map column-vector homogeneous [x,y,1] using a declared affine matrix.

    For row-stored coordinates, calculation is points @ transform.T.
    Supports scale/rotation/translation/reflection, not deformable warps.
    """
    xy, a = np.asarray(coordinates, float), np.asarray(transform, float)
    if xy.ndim != 2 or xy.shape[1] != 2 or a.shape != (3, 3):
        raise ValueError("Need n x 2 coordinates and a 3 x 3 affine matrix.")
    if not np.isfinite(xy).all() or not np.isfinite(a).all():
        raise ValueError("Coordinates and affine matrix must be finite.")
    if not np.allclose(a[2], [0, 0, 1]) or np.isclose(np.linalg.det(a[:2, :2]), 0):
        raise ValueError("Expected an invertible affine matrix, not a projective transform.")
    return (np.column_stack([xy, np.ones(len(xy))]) @ a.T)[:, :2]


def plot_spatial_values(ax: Axes, xy: np.ndarray, values: Sequence[float], *,
                        section_ids: Sequence[str], coordinate_unit: str,
                        y_axis_down: bool, norm: mpl.colors.Normalize, cmap: Any,
                        spot_area_pt2: float = 3.0,
                        image: np.ndarray | None = None,
                        image_extent: tuple[float, float, float, float] | None = None):
    """One section per Axes, equal geometry, declared orientation and shared norm.

    Point size is display area, NOT physical cell radius. For physical segmentation
    use polygons. Histology must already be resampled/aligned to this coordinate frame.
    image_extent=(left,right,bottom,top), with origin chosen by y_axis_down.
    """
    xy = np.asarray(xy, float); values = np.asarray(values, float)
    if xy.shape != (len(values), 2) or not np.isfinite(xy).all():
        raise ValueError("Spatial coordinates must be finite and aligned to values.")
    if len(section_ids) != len(values) or pd.isna(section_ids).any() or len(set(section_ids)) != 1:
        raise ValueError("A spatial Axes must contain exactly one declared sample/section.")
    if spot_area_pt2 <= 0:
        raise ValueError("Point display area must be positive.")
    if coordinate_unit not in {"um", "pixel"}:
        raise ValueError("coordinate_unit must be 'um' or 'pixel'.")
    if not np.isfinite(values).all():
        raise ValueError("Missing expression must be handled explicitly, not painted as zero.")
    if image is not None:
        if image_extent is None:
            raise ValueError("A registered image_extent is required for a histology overlay.")
        ax.imshow(image, extent=image_extent, origin="upper" if y_axis_down else "lower")
    artist = ax.scatter(xy[:, 0], xy[:, 1], c=values, s=spot_area_pt2,
                        norm=norm, cmap=cmap, linewidths=0, rasterized=True)
    # Set orientation idempotently; never blindly invert repeatedly.
    bottom, top = sorted(ax.get_ylim())
    ax.set_ylim((top, bottom) if y_axis_down else (bottom, top))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(f"x ({coordinate_unit})"); ax.set_ylabel(f"y ({coordinate_unit})")
    return artist


def aggregate_transport(coupling: Any, source_groups: Sequence[str],
                        target_groups: Sequence[str], *,
                        normalization: str = "mass") -> pd.DataFrame:
    """A.T @ coupling @ B without densifying the cell x cell coupling.

    'mass' preserves input total; 'source_fraction' normalizes AFTER aggregation.
    A coupling is not an observed lineage tree. Unbalanced OT need not sum to one.
    """
    src, tgt = np.asarray(source_groups, str), np.asarray(target_groups, str)
    if len(src) == 0 or len(tgt) == 0 or pd.isna(source_groups).any() or pd.isna(target_groups).any():
        raise ValueError("Nonempty, nonmissing source and target labels are required.")
    _check_matrix(coupling, (len(src), len(tgt)), "coupling", nonnegative=True)
    source_order, target_order = list(pd.unique(src)), list(pd.unique(tgt))
    scodes = pd.Categorical(src, categories=source_order).codes
    tcodes = pd.Categorical(tgt, categories=target_order).codes
    a = sparse.csr_matrix((np.ones(len(src)), (np.arange(len(src)), scodes)),
                          shape=(len(src), len(source_order)))
    b = sparse.csr_matrix((np.ones(len(tgt)), (np.arange(len(tgt)), tcodes)),
                          shape=(len(tgt), len(target_order)))
    out = a.T @ sparse.csr_matrix(coupling) @ b
    values = out.toarray()  # Only the small group x group matrix is made dense.
    if normalization == "source_fraction":
        totals = values.sum(axis=1, keepdims=True)
        values = np.divide(values, totals, out=np.full_like(values, np.nan), where=totals > 0)
    elif normalization != "mass":
        raise ValueError("normalization must be 'mass' or 'source_fraction'.")
    return pd.DataFrame(values, index=source_order, columns=target_order)


@contextmanager
def _hide_text(fig: Figure):
    texts = fig.findobj(match=Text)
    before = [t.get_visible() for t in texts]
    try:
        for t in texts: t.set_visible(False)
        yield
    finally:
        for t, state in zip(texts, before): t.set_visible(state)


def export_figure(fig: Figure, stem: str | Path, *, provenance: Mapping[str, Any],
                  source_tables: Mapping[str, pd.DataFrame] | None = None,
                  dpi: int = 300, textless: bool = False) -> dict[str, str]:
    """Export fixed-canvas PDF/SVG/PNG + source tables + provenance/hashes.

    No bbox_inches='tight': this preserves the designed physical canvas size.
    Caller must verify that labels fit. Textless files are assembly assets, never
    standalone final scientific figures. No font files are distributed.
    """
    required = {"data_source", "analysis_unit", "value_definition", "seed"}
    missing = required - provenance.keys()
    if missing:
        raise ValueError(f"Missing provenance fields: {sorted(missing)}")
    if dpi <= 0:
        raise ValueError("dpi must be positive.")
    stem = Path(stem); stem.parent.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    def render(suffix: str = ""):
        for ext in ("pdf", "svg", "png"):
            path = stem.parent / f"{stem.name}{suffix}.{ext}"
            fig.savefig(path, dpi=dpi)
            files[f"{suffix or 'labelled'}_{ext}"] = str(path)
    fig.canvas.draw()
    render()
    if textless:
        with _hide_text(fig): render("_no_text")
    for name, df in (source_tables or {}).items():
        if Path(name).name != name or name in {"", ".", ".."}:
            raise ValueError("Source table names must be simple filenames without directories.")
        path = stem.parent / f"{stem.name}_{name}.csv"
        df.to_csv(path, index=False)
        files[f"source_{name}"] = str(path)
    versions = {}
    for package in ("numpy", "pandas", "scipy", "matplotlib"):
        versions[package] = importlib.metadata.version(package)
    record = dict(provenance)
    record.update({"export_time_utc": datetime.now(timezone.utc).isoformat(),
                   "python": platform.python_version(), "versions": versions,
                   "font_family": mpl.rcParams["font.family"],
                   "size_inches": fig.get_size_inches().tolist(), "dpi": dpi,
                   "textless_is_assembly_asset": bool(textless),
                   "outputs": {k: {"path": v, "sha256": hashlib.sha256(Path(v).read_bytes()).hexdigest()}
                               for k, v in files.items()}})
    path = stem.parent / f"{stem.name}_provenance.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    files["provenance"] = str(path)
    return files
