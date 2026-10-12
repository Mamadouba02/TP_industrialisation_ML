"""Check versioned artefacts before training can replace them."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
metadata = json.loads((root / 'models/metadata.json').read_text(encoding='utf-8'))
for relative, field in [('data/raw/churn.csv', 'dataset_sha256'), ('models/model.pkl', 'model_sha256')]:
    actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if actual != metadata[field]:
        raise SystemExit(f'Hash mismatch: {relative}; regenerate and version matching artefacts.')
    print(f'OK: {relative}')
