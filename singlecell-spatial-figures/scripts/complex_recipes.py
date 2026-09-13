"""Original compositional recipes. Inputs are reviewed analysis results, not raw claims."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from figure_core import validate_palette


def annotated_heatmap(fig: Figure, matrix: pd.DataFrame, *,
                      column_metric: pd.Series, row_metric: pd.Series,
                      norm: mpl.colors.Normalize, cmap: Any,
                      effect_labels: pd.DataFrame | None = None,
                      value_label: str = "Value") -> dict[str, Axes]:
    """One shared row/column order across heatmap, margins, and effect labels.

    Callers must cluster/order ONCE upstream. The recipe intentionally does not
    independently cluster each layer or run significance tests inside the renderer.
    The central matrix is an image; text/marginal bars remain vector objects.
    """
    if matrix.empty or not matrix.index.is_unique or not matrix.columns.is_unique:
        raise ValueError("Need a nonempty matrix with unique row and column names.")
    if not np.isfinite(matrix.to_numpy(dtype=float)).all():
        raise ValueError("Missing values need an explicit mask/NA legend, not silent zero filling.")
    if not column_metric.index.is_unique or not row_metric.index.is_unique:
        raise ValueError("Annotation identifiers must be unique.")
    cm = column_metric.reindex(matrix.columns)
    rm = row_metric.reindex(matrix.index)
    if cm.isna().any() or rm.isna().any():
        raise ValueError("Annotations are not aligned to all matrix identifiers.")
    if effect_labels is not None:
        effect_labels = effect_labels.reindex(index=matrix.index, columns=matrix.columns)
        if effect_labels.isna().any().any():
            raise ValueError("Effect-label identifiers are incomplete.")
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 5], width_ratios=[5, 1, .22],
                          hspace=.07, wspace=.10)
    heat = fig.add_subplot(gs[1, 0])
    top = fig.add_subplot(gs[0, 0], sharex=heat)
    right = fig.add_subplot(gs[1, 1], sharey=heat)
    cax = fig.add_subplot(gs[1, 2])
    image = heat.imshow(matrix.to_numpy(), norm=norm, cmap=cmap,
                        aspect="auto", interpolation="nearest")
    top.bar(np.arange(matrix.shape[1]), cm.to_numpy())
    right.barh(np.arange(matrix.shape[0]), rm.to_numpy())
    heat.set_xticks(np.arange(matrix.shape[1]), matrix.columns, rotation=45, ha="right")
    heat.set_yticks(np.arange(matrix.shape[0]), matrix.index)
    top.tick_params(axis="x", labelbottom=False, bottom=False)
    right.tick_params(axis="y", labelleft=False, left=False)
    top.set_ylabel(str(cm.name or "Metric"))
    right.set_xlabel(str(rm.name or "Metric"))
    if effect_labels is not None:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text = str(effect_labels.iloc[i, j])
                if text:
                    rgba = np.asarray(image.cmap(image.norm(matrix.iloc[i, j])))
                    rgb = rgba[:3] * rgba[3] + (1 - rgba[3])  # composite on white
                    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
                    luminance = float(np.dot(linear, [.2126, .7152, .0722]))
                    colour = "black" if (luminance + .05) / .05 >= 1.05 / (luminance + .05) else "white"
                    heat.text(j, i, text, ha="center", va="center", color=colour)
    fig.colorbar(image, cax=cax, label=value_label)
    return {"heatmap": heat, "top": top, "right": right, "colorbar": cax}


def radius_graph_edges(coordinates: np.ndarray, section_ids: Sequence[str], *,
                       radius: float, max_edges: int = 1_000_000) -> pd.DataFrame:
    """Sparse radius graph within sections; units are those of the input coordinates.

    Radius proximity alone does not establish direct contact or communication.
    Barriers/tissue holes are NOT automatically handled; filter them upstream.
    The edge budget is checked before materialising pairs for each section.
    """
    xy = np.asarray(coordinates, dtype=float)
    if xy.shape != (len(section_ids), 2) or not np.isfinite(xy).all():
        raise ValueError("Expected finite, aligned n x 2 coordinates.")
    if radius <= 0 or max_edges <= 0 or pd.isna(section_ids).any():
        raise ValueError("Need a positive radius/budget and nonmissing section IDs.")
    samples = np.asarray(section_ids, dtype=str)
    frames, total = [], 0
    for sample in pd.unique(samples):
        ids = np.flatnonzero(samples == sample)
        tree = cKDTree(xy[ids])
        count = (int(tree.count_neighbors(tree, radius)) - len(ids)) // 2
        total += count
        if total > max_edges:
            raise ValueError("Edge budget exceeded; reduce ROI/radius or use a different graph.")
        pairs = tree.query_pairs(radius, output_type="ndarray")
        if len(pairs):
            gi, gj = ids[pairs[:, 0]], ids[pairs[:, 1]]
            frames.append(pd.DataFrame({"source_index": gi, "target_index": gj,
                                        "distance": np.linalg.norm(xy[gi] - xy[gj], axis=1),
                                        "section_id": sample}))
    if not frames:
        return pd.DataFrame(columns=["source_index", "target_index", "distance", "section_id"])
    return pd.concat(frames, ignore_index=True)


def weighted_time_bins(time: Sequence[float], values: Sequence[float],
                       weights: Sequence[float], edges: Sequence[float]) -> pd.DataFrame:
    """Descriptive fate-weighted means in predefined bins; NOT a GAM or CI.

    Last bin includes the final endpoint. n_eff is a weight diagnostic, not the
    biological replicate count. Fit model-based trends/uncertainty separately.
    """
    t, y, w, bins = [np.asarray(x, float) for x in (time, values, weights, edges)]
    if t.ndim != 1 or t.shape != y.shape or t.shape != w.shape:
        raise ValueError("Aligned one-dimensional time, value, and weight arrays required.")
    if len(bins) < 2 or not np.all(np.diff(bins) > 0):
        raise ValueError("At least two strictly increasing bin edges are required.")
    if not all(np.isfinite(x).all() for x in (t, y, w, bins)) or np.any(w < 0):
        raise ValueError("Inputs must be finite, weights nonnegative.")
    if len(t) and (t.min() < bins[0] or t.max() > bins[-1]):
        raise ValueError("Bin edges must cover all observations.")
    rows = []
    for k, (left, right) in enumerate(zip(bins[:-1], bins[1:])):
        mask = (t >= left) & ((t <= right) if k == len(bins) - 2 else (t < right))
        wi, yi = w[mask], y[mask]
        sw = wi.sum()
        rows.append({"left": left, "right": right, "time": (left + right) / 2,
                     "mean": float(np.dot(wi, yi) / sw) if sw > 0 else np.nan,
                     "weight_sum": float(sw), "n_cells": int(mask.sum()),
                     "n_eff": float(sw * sw / np.dot(wi, wi)) if sw > 0 else 0.0})
    return pd.DataFrame(rows)


def transport_ribbons(ax: Axes, mass: pd.DataFrame, palette: Mapping[str, str], *,
                      unit_label: str = "Transport mass", max_links: int = 150,
                      gap_fraction: float = .015) -> dict[str, float]:
    """Two-stage alluvial geometry from an ALREADY aggregated nonnegative mass matrix.

    Widths on both sides use the same denominator. There is no hidden threshold,
    per-source renormalization, or conversion from mass to observed cell counts.
    Curves are layout devices, not physical migration trajectories.
    """
    if mass.empty or not mass.index.is_unique or not mass.columns.is_unique:
        raise ValueError("Unique source and target IDs are required.")
    a = mass.to_numpy(dtype=float)
    if not np.isfinite(a).all() or np.any(a < 0) or a.sum() <= 0:
        raise ValueError("Mass must be finite, nonnegative, and have a positive total.")
    if np.count_nonzero(a) > max_links:
        raise ValueError("Too many links. Predefine and disclose an aggregation/filter policy.")
    if gap_fraction < 0:
        raise ValueError("Gap must be nonnegative.")
    labels = list(map(str, mass.index)) + list(map(str, mass.columns))
    validate_palette(labels, palette)
    total = float(a.sum())
    heights = a / total
    sr, tr = heights.sum(axis=1), heights.sum(axis=0)
    sy = np.r_[0, np.cumsum(sr[:-1])] + np.arange(len(sr)) * gap_fraction
    ty = np.r_[0, np.cumsum(tr[:-1])] + np.arange(len(tr)) * gap_fraction
    left_cursor, right_cursor = sy.copy(), ty.copy()
    for i, source in enumerate(map(str, mass.index)):
        for j in range(len(tr)):
            h = heights[i, j]
            if h <= 0: continue
            lo, ro = left_cursor[i], right_cursor[j]
            vertices = [(0.08, lo), (.40, lo), (.60, ro), (.92, ro),
                        (.92, ro + h), (.60, ro + h), (.40, lo + h), (.08, lo + h), (.08, lo)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                     Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(vertices, codes), facecolor=palette[source],
                                   edgecolor="none", alpha=.55))
            left_cursor[i] += h; right_cursor[j] += h
    for names, starts, hs, x in ((mass.index, sy, sr, 0), (mass.columns, ty, tr, .92)):
        for name, start, height in zip(names, starts, hs):
            ax.add_patch(Rectangle((x, start), .08, height, facecolor=palette[str(name)], linewidth=0))
            ax.text(-.02 if x == 0 else 1.02, start + height / 2,
                    str(name), ha="right" if x == 0 else "left", va="center")
    ymax = 1 + max(len(sr) - 1, len(tr) - 1) * gap_fraction
    ax.set_xlim(-.35, 1.35); ax.set_ylim(ymax + .02, -.02)
    ax.set_axis_off(); ax.set_title(f"{unit_label} (total = {total:g})")
    return {"total_mass": total, "displayed_mass": total, "dropped_mass": 0.0}
