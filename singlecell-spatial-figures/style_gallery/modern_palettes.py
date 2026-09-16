"""Low-saturation modern editorial palette routing for the v3.2 gallery/runtime.

The legacy palette library remains available. This module only changes automatic
routing; users can opt out with ``palette_policy='legacy'`` or lock an explicit
preset with ``palette_lock=True``.
"""
from __future__ import annotations
import copy, json
from pathlib import Path
from matplotlib import colors as mc
from chart_core import palette as legacy_palette, cmap as legacy_cmap

ROOT = Path(__file__).resolve().parent
PRESETS = json.loads((ROOT / 'modern_palette_presets_v32.json').read_text(encoding='utf-8'))
CATEGORICAL = PRESETS['categorical']
SEQUENTIAL = PRESETS['sequential']
DIVERGING = PRESETS['diverging']


def snapshots():
    out = {}
    for family, rows in [('categorical', CATEGORICAL), ('sequential', SEQUENTIAL), ('diverging', DIVERGING)]:
        for pid, row in rows.items():
            out[pid] = {'colors': list(row['colors']), 'name': row['name'], 'family': family,
                        'source': {'grade': 'D', 'context': 'Skill-curated low-saturation editorial default; not paper-extracted.'}}
    return out


def _policy(cfg):
    return cfg.get('palette_policy', 'modern_editorial')


def _categorical_id(n):
    if n <= 6: return 'E01'
    if n <= 8: return 'E02'
    if n <= 10: return 'E04'
    if n <= 12: return 'E06'
    if n <= 16: return 'E08'
    if n <= 20: return 'E09'
    return None


def palette(levels, cfg):
    """Route ordinary category plots to light, low-saturation editorial colors."""
    levels = list(levels)
    if _policy(cfg) == 'legacy' or cfg.get('palette_lock'):
        return legacy_palette(levels, cfg)
    if cfg.get('colors') is not None and not cfg.get('demo') and not cfg.get('auto_palette'):
        return legacy_palette(levels, cfg)
    reference = list(cfg.get('palette_order', levels))
    if len(reference) != len(set(reference)) or set(levels) - set(reference):
        raise ValueError('Invalid palette_order')
    requested = cfg.get('categorical_preset')
    pid = requested if requested in CATEGORICAL else _categorical_id(len(reference))
    if pid is None:
        fallback = copy.deepcopy(cfg)
        fallback.pop('colors', None)
        fallback['categorical_preset'] = 'C21'
        return legacy_palette(levels, fallback)
    colors = CATEGORICAL[pid]['colors']
    if len(reference) > len(colors):
        raise ValueError(f'{pid}: categorical palette capacity exceeded')
    full = dict(zip(reference, colors))
    result = {x: full[x] for x in levels}
    if len({mc.to_hex(v) for v in result.values()}) != len(result):
        raise ValueError('Duplicate category colors')
    return result


def _infer_scalar_id(cfg, signed):
    text = ' '.join(str(cfg.get(k, '')) for k in
                    ['title', 'value_label', 'effect_label', 'x_label', 'y_label']).lower()
    if signed:
        if any(x in text for x in ['correlation', ' z-score', 'z score', 'centered']): return 'V02'
        if any(x in text for x in ['residual', 'difference', 'delta', 'change']): return 'V03'
        if any(x in text for x in ['pathway', 'enrichment', 'activity']): return 'V04'
        return 'V01'
    if any(x in text for x in ['pseudotime', 'latent', 'trajectory', 'development']): return 'L03'
    if any(x in text for x in ['fraction', 'abundance', 'probability', 'confidence', 'composition']): return 'L04'
    if any(x in text for x in ['activation', 'score', 'response', 'effect']): return 'L02'
    if any(x in text for x in ['morphology', 'density', 'count']): return 'L05'
    if any(x in text for x in ['risk', 'stress', 'depletion']): return 'L06'
    return 'L01'


def cmap(cfg, signed=False):
    """Smooth low-saturation scalar map with light endpoints and no black endpoint."""
    if _policy(cfg) == 'legacy' or cfg.get('palette_lock'):
        return legacy_cmap(cfg, signed)
    if cfg.get('continuous_colors') is not None and not cfg.get('demo') and not cfg.get('auto_palette'):
        return legacy_cmap(cfg, signed)
    requested = cfg.get('continuous_preset')
    family = DIVERGING if signed else SEQUENTIAL
    pid = requested if requested in family else _infer_scalar_id(cfg, signed)
    colors = family[pid]['colors']
    cm = mc.LinearSegmentedColormap.from_list('editorial_' + pid, colors, N=256)
    if cfg.get('reverse', False):
        cm = cm.reversed()
    cm = cm.copy()
    cm.set_bad(cfg.get('missing_color', '#D8DDDF'))
    cm.set_under(cfg.get('under_color', cm(0.0)))
    cm.set_over(cfg.get('over_color', cm(1.0)))
    return cm
