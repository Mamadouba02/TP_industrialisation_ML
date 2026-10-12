import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hashlib
import json
import joblib
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from src.config import ROOT, FEATURES, VERSION


def main():
    dataset = ROOT / 'data/raw/churn.csv'
    df = pd.read_csv(dataset)
    x_train, x_test, y_train, y_test = train_test_split(df[FEATURES], df.churn, test_size=.2, random_state=42, stratify=df.churn)
    candidates = {
        'logistic_regression': Pipeline([('scaler', StandardScaler()), ('model', LogisticRegression(max_iter=1000, random_state=42))]),
        'decision_tree': DecisionTreeClassifier(max_depth=5, random_state=42),
        'random_forest': RandomForestClassifier(n_estimators=200, random_state=42),
    }
    results = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        results[name] = {key: float(metric(y_test, pred, **({} if key == 'accuracy' else {'zero_division': 0}))) for key, metric in [('accuracy', accuracy_score), ('precision', precision_score), ('recall', recall_score), ('f1', f1_score)]}
    out = ROOT / 'models'
    out.mkdir(exist_ok=True)
    joblib.dump(candidates['random_forest'], out / 'model.pkl')
    metadata = {'model': 'Random Forest', 'version': VERSION, 'features': FEATURES, 'sklearn_version': sklearn.__version__, 'dataset_sha256': hashlib.sha256(dataset.read_bytes()).hexdigest(), 'model_sha256': hashlib.sha256((out / 'model.pkl').read_bytes()).hexdigest(), 'train_rows': len(x_train), 'test_rows': len(x_test), 'selection_reason': 'Random Forest imposé par la procédure ; comparaison conservée pour discussion.', 'results': results}
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    processed = ROOT / 'data/processed'
    processed.mkdir(parents=True, exist_ok=True)
    x_train.assign(churn=y_train).to_csv(processed / 'train.csv', index=False, lineterminator='\n')
    x_test.assign(churn=y_test).to_csv(processed / 'test.csv', index=False, lineterminator='\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
