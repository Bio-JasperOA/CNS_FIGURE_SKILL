"""Artificial fixtures for software QA only; no biological results are asserted."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from figure_core import (FigureStyle, apply_style, validate_palette, marker_summary,
                         gene_zscore, plot_marker_dot, plot_embedding,
                         affine_coordinates, plot_spatial_values, aggregate_transport,
                         export_figure)
from complex_recipes import (annotated_heatmap, radius_graph_edges,
                             weighted_time_bins, transport_ribbons)

@pytest.fixture(autouse=True)
def close_figures():
    with mpl.rc_context():
        apply_style(FigureStyle(font="DejaVu Sans"))
        yield
    plt.close("all")

@pytest.fixture
def data():
    x = np.array([[0., 2.], [2., 0.], [4., 4.]])
    obs = pd.DataFrame({"cell_type": ["A", "A", "B"],
                        "sample_id": ["D1", "D2", "D1"]}, index=["c1", "c2", "c3"])
    return x, obs

@pytest.fixture
def palette():
    cycle = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    return dict(zip(["A", "B", "X", "Y"], cycle))

def get_summary(data, sparse_input=False, order=None):
    x, obs = data
    xx = sparse.csr_matrix(x) if sparse_input else x
    return marker_summary(xx, xx, obs, ["g1", "g2"], "cell_type", "sample_id", order)

@pytest.mark.parametrize("sparse_input", [False, True])
def test_marker_mean_includes_zeros(data, sparse_input):
    out = get_summary(data, sparse_input)
    a = out.query("group == 'A'")
    np.testing.assert_allclose(a.mean_expression, [1, 1])
    np.testing.assert_allclose(a.fraction_detected, [.5, .5])
    assert a.n_cells.tolist() == [2, 2]
    assert a.n_samples.tolist() == [2, 2]

def test_absent_group_is_missing(data):
    out = get_summary(data, order=["B", "A", "C"])
    missing = out.query("group == 'C'")
    assert missing.mean_expression.isna().all()
    assert missing.fraction_detected.isna().all()
    assert (missing.n_cells == 0).all()
    assert out.group.drop_duplicates().tolist() == ["B", "A", "C"]

def test_no_silent_missing_observed_group(data):
    with pytest.raises(ValueError): get_summary(data, order=["A"])

def test_duplicate_cell_ids_rejected(data):
    x, obs = data; obs.index = ["c", "c", "d"]
    with pytest.raises(ValueError): get_summary((x, obs))

def test_matrix_alignment_shape_rejected(data):
    x, obs = data
    with pytest.raises(ValueError):
        marker_summary(x[:, :1], x, obs, ["g1", "g2"], "cell_type", "sample_id")

def test_residuals_not_detection_counts(data):
    x, obs = data; x[0, 0] = -1
    with pytest.raises(ValueError): get_summary((x, obs))

def test_missing_sample_rejected(data):
    x, obs = data; obs.loc["c1", "sample_id"] = None
    with pytest.raises(ValueError): get_summary((x, obs))

def test_nonfinite_matrix_rejected(data):
    x, obs = data; x[0, 0] = np.nan
    with pytest.raises(ValueError): get_summary((x, obs))

def test_zscore_population_sd_and_missing():
    tab = pd.DataFrame({"gene": ["g", "g", "g", "c", "c"],
                        "mean_expression": [1, 3, np.nan, 2, 2]})
    z = gene_zscore(tab, clip=.5)
    np.testing.assert_allclose(z.z_unclipped.iloc[:2], [-1, 1])
    np.testing.assert_allclose(z.z_display.iloc[:2], [-.5, .5])
    assert np.isnan(z.z_display.iloc[2])
    assert z.z_unclipped.iloc[3:].tolist() == [0, 0]

def test_palette_unknown_and_missing(palette):
    validate_palette(["A", "B"], palette)
    with pytest.raises(ValueError): validate_palette(["Unknown"], palette)
    with pytest.raises(ValueError): validate_palette([None], palette)

def test_dot_area_not_radius(data):
    out = get_summary(data); fig, ax = plt.subplots()
    artist = plot_marker_dot(ax, out, ["A", "B"], ["g1", "g2"],
                             value="mean_expression", norm=Normalize(0, 4),
                             cmap=mpl.colormaps["viridis"], max_area_pt2=40)
    np.testing.assert_allclose(artist.get_sizes(), [20, 20, 40, 40])

def test_dot_does_not_silently_drop_categories(data):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_marker_dot(ax, get_summary(data), ["A"], ["g1", "g2"],
                         value="mean_expression", norm=Normalize(0, 4), cmap="viridis")

def test_embedding_order_reproducible(palette):
    xy = np.arange(12).reshape(6, 2); labels = ["A", "B"] * 3
    fig1, ax1 = plt.subplots(); fig2, ax2 = plt.subplots()
    a = plot_embedding(ax1, xy, labels, palette, seed=4)
    b = plot_embedding(ax2, xy, labels, palette, seed=4)
    np.testing.assert_allclose(a.get_offsets(), b.get_offsets())
    assert a.get_rasterized()

def test_embedding_missing_label_fails(palette):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError): plot_embedding(ax, [[0,0]], [None], palette)

def test_affine_identity_translation_and_reflection():
    xy = np.array([[1, 2], [3, 4.]])
    np.testing.assert_allclose(affine_coordinates(xy, np.eye(3)), xy)
    a = np.array([[2,0,10], [0,-1,5], [0,0,1]])
    np.testing.assert_allclose(affine_coordinates(xy, a), [[12,3],[16,1]])

def test_singular_transform_fails():
    with pytest.raises(ValueError): affine_coordinates([[1,2]], np.zeros((3,3)))

def test_spatial_orientation_is_idempotent():
    fig, ax = plt.subplots(); xy = [[0,0], [1,2]]
    kwargs = dict(section_ids=["S1", "S1"], coordinate_unit="um", y_axis_down=True,
                  norm=Normalize(0,1), cmap="viridis")
    plot_spatial_values(ax, xy, [0,1], **kwargs)
    assert ax.yaxis_inverted()
    plot_spatial_values(ax, xy, [0,1], **kwargs)
    assert ax.yaxis_inverted()
    assert ax.get_aspect() == 1

def test_spatial_mixed_sections_rejected():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_spatial_values(ax, [[0,0],[1,1]], [0,1], section_ids=["S1","S2"],
                             coordinate_unit="um", y_axis_down=False,
                             norm=Normalize(0,1), cmap="viridis")

def test_spatial_uncalibrated_unit_rejected():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_spatial_values(ax, [[0,0]], [0], section_ids=["S1"], coordinate_unit="unknown",
                             y_axis_down=False, norm=Normalize(0,1), cmap="viridis")

def test_spatial_image_needs_registered_extent():
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_spatial_values(ax, [[0,0]], [0], section_ids=["S1"], coordinate_unit="pixel",
                             y_axis_down=False, norm=Normalize(0,1), cmap="viridis",
                             image=np.zeros((2,2)))

@pytest.mark.parametrize("sparse_input", [False, True])
def test_transport_mass_conserved(sparse_input):
    p = np.array([[1,2], [3,4], [5,6.]])
    out = aggregate_transport(sparse.csr_matrix(p) if sparse_input else p,
                               ["A","A","B"], ["X","Y"])
    np.testing.assert_allclose(out, [[4,6], [5,6]])
    assert out.to_numpy().sum() == p.sum()

def test_transport_source_normalization_and_empty_source():
    p = sparse.csr_matrix([[0.,0.], [2.,6.]])
    out = aggregate_transport(p, ["A","B"], ["X","Y"], normalization="source_fraction")
    assert out.loc["A"].isna().all()
    np.testing.assert_allclose(out.loc["B"], [.25,.75])

def test_negative_transport_fails():
    with pytest.raises(ValueError): aggregate_transport(np.array([[-1.]]), ["A"], ["B"])

def test_radius_graph_never_crosses_section():
    xy = [[0,0], [.5,0], [0,0], [.5,0]]
    edges = radius_graph_edges(xy, ["S1","S1","S2","S2"], radius=1)
    assert len(edges) == 2
    assert set(map(tuple, edges[["source_index","target_index"]].to_numpy())) == {(0,1),(2,3)}

def test_radius_graph_budget_checked():
    with pytest.raises(ValueError): radius_graph_edges(np.zeros((20,2)), ["S1"]*20, radius=1, max_edges=10)

def test_radius_graph_no_edges():
    edges = radius_graph_edges([[0,0],[10,0]], ["S1","S1"], radius=1)
    assert edges.empty and "section_id" in edges

def test_weighted_bins_include_final_endpoint():
    out = weighted_time_bins([0,.5,1], [1,3,5], [1,1,2], [0,.5,1])
    np.testing.assert_allclose(out["mean"], [1,13/3])
    assert out.n_cells.tolist() == [1,2]
    assert out.n_eff.iloc[1] == pytest.approx(9/5)

def test_zero_weight_bin_is_missing():
    out = weighted_time_bins([0], [9], [0], [0,1])
    assert np.isnan(out["mean"].iloc[0])
    assert out.n_eff.iloc[0] == 0

def test_out_of_range_time_not_silently_omitted():
    with pytest.raises(ValueError): weighted_time_bins([2], [1], [1], [0,1])

def test_heatmap_shared_indices():
    matrix = pd.DataFrame([[1,2],[3,4]], index=["A","B"], columns=["X","Y"])
    fig = plt.figure(figsize=(7.2,5))
    axes = annotated_heatmap(fig, matrix, column_metric=pd.Series([20,10], index=["Y","X"]),
                             row_metric=pd.Series([6,5], index=["B","A"]),
                             norm=Normalize(0,4), cmap="viridis")
    np.testing.assert_allclose([p.get_height() for p in axes["top"].patches], [10,20])
    np.testing.assert_allclose([p.get_width() for p in axes["right"].patches], [5,6])

def test_heatmap_missing_annotation_fails():
    m = pd.DataFrame([[1]], index=["A"], columns=["X"])
    with pytest.raises(ValueError):
        annotated_heatmap(plt.figure(), m, column_metric=pd.Series([1],index=["Y"]),
                           row_metric=pd.Series([1],index=["A"]), norm=Normalize(0,1), cmap="viridis")

def test_ribbons_preserve_mass(palette):
    mass = pd.DataFrame([[1.,2.],[3.,4.]], index=["A","B"], columns=["X","Y"])
    fig, ax = plt.subplots()
    out = transport_ribbons(ax, mass, palette)
    assert out == {"total_mass":10., "displayed_mass":10., "dropped_mass":0.}
    assert len(ax.patches) == 8

def test_ribbon_no_implicit_link_filter(palette):
    fig, ax = plt.subplots()
    mass = pd.DataFrame([[1.,2.]], index=["A"], columns=["X","Y"])
    with pytest.raises(ValueError): transport_ribbons(ax, mass, palette, max_links=1)

def test_export_provenance_required(tmp_path):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError): export_figure(fig, tmp_path/"x", provenance={})

def test_export_formats_hashes_and_text_restore(tmp_path):
    fig, ax = plt.subplots(); ax.plot([0,1],[0,1]); title=ax.set_title("QA fixture, not biological data")
    out = export_figure(fig, tmp_path/"qa", source_tables={"data":pd.DataFrame({"x":[0,1]})},
                         provenance={"data_source":"artificial software test fixture",
                                     "analysis_unit":"none", "value_definition":"unit test", "seed":0},
                         textless=True, dpi=120)
    assert title.get_visible()
    for path in out.values(): assert Path(path).exists()
    provenance = json.loads(Path(out["provenance"]).read_text())
    for item in provenance["outputs"].values():
        assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert Path(out["labelled_pdf"]).read_bytes().startswith(b"%PDF")
    svg = ET.parse(out["labelled_svg"])
    assert len(svg.findall(".//{http://www.w3.org/2000/svg}text")) > 0
    naked = ET.parse(out["_no_text_svg"])
    assert len(naked.findall(".//{http://www.w3.org/2000/svg}text")) == 0
    assert provenance["size_inches"] == pytest.approx([89/25.4,89/25.4])


def test_heatmap_text_contrasts_with_extreme_fills():
    m = pd.DataFrame([[0.,1.]], index=["A"], columns=["X","Y"])
    axes = annotated_heatmap(plt.figure(), m, column_metric=pd.Series([1,2], index=m.columns),
                             row_metric=pd.Series([1], index=m.index), norm=Normalize(0,1),
                             cmap="Greys", effect_labels=m.astype(str))
    assert [t.get_color() for t in axes["heatmap"].texts] == ["black", "white"]
