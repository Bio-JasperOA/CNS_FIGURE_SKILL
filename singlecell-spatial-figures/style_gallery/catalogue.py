"""Compatibility view over the one v3.2 catalogue; no stale parallel 14-kind list."""
import json
from pathlib import Path
CATALOG=json.loads(Path(__file__).with_name('catalogue_v32.json').read_text(encoding='utf-8'))
SOURCES={row['kind']:row['evidence'] for row in CATALOG}
