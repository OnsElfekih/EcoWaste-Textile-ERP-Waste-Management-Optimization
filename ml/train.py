"""Train and evaluate a reproducible model on a synthetic hold-out split."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

FEATURES = ['textile_material', 'waste_origin', 'waste_cause', 'textile_quality',
            'scrap_size', 'textile_condition', 'hazard_level']
TARGET = 'final_treatment'
BASE = Path(__file__).resolve().parent
ARTIFACTS = BASE.parent / 'ecowaste_textile' / 'ml_artifacts'


def build_pipeline(model):
    return Pipeline([
        ('encoding', ColumnTransformer([
            ('categorical', OneHotEncoder(handle_unknown='ignore'), FEATURES)
        ], remainder='drop')),
        ('classifier', model),
    ])


def main():
    source = BASE / 'data' / 'textile_waste_synthetic.csv'
    if not source.exists():
        raise SystemExit('Missing dataset. Run: python ml/generate_dataset.py')
    data = pd.read_csv(source)
    if data[FEATURES + [TARGET]].isna().any().any():
        raise ValueError('Missing values: revise dataset')
    if not set(data[TARGET].unique()).issubset({'reuse', 'recycle', 'disposal'}):
        raise ValueError('Unexpected target classes')
    # Synthetic rows may share combinations. Evaluation only measures this
    # synthetic distribution, not generalization to real industrial sites.
    x_train, x_test, y_train, y_test = train_test_split(
        data[FEATURES], data[TARGET], stratify=data[TARGET], test_size=.2, random_state=42
    )
    candidates = {
        'Dummy majority': DummyClassifier(strategy='most_frequent'),
        'Logistic Regression': LogisticRegression(max_iter=1500, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=7, min_samples_leaf=8, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=12,
                                                min_samples_leaf=3, random_state=42, n_jobs=-1),
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    report = {'dataset': 'synthetic', 'rows': len(data), 'train_rows': len(x_train),
              'test_rows': len(x_test), 'random_state': 42, 'models': {},
              'limitation': 'Results measure performance only on synthetic assumptions.'}
    winner = None
    best = -1.0
    for name, estimator in candidates.items():
        pipe = build_pipeline(estimator)
        pipe.fit(x_train, y_train)
        predictions = pipe.predict(x_test)
        score = f1_score(y_test, predictions, average='macro', zero_division=0)
        report['models'][name] = {
            'accuracy': round(float(accuracy_score(y_test, predictions)), 4),
            'f1_macro': round(float(score), 4),
            'classification_report': classification_report(y_test, predictions, output_dict=True, zero_division=0),
            'confusion_matrix_labels': ['reuse', 'recycle', 'disposal'],
            'confusion_matrix': confusion_matrix(y_test, predictions, labels=['reuse', 'recycle', 'disposal']).tolist(),
        }
        print(f'{name}: accuracy={report["models"][name]["accuracy"]:.4f} f1_macro={score:.4f}')
        if name != 'Dummy majority' and score > best:
            best, winner = score, (name, pipe)
    report['selected_model'] = winner[0]
    # Only load models created by your own code: joblib uses Python pickle.
    joblib.dump({'pipeline': winner[1], 'features': FEATURES,
                 'version': 'synthetic-v1', 'dataset_type': 'synthetic'},
                ARTIFACTS / 'model.joblib')
    (ARTIFACTS / 'evaluation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Selected: {winner[0]}')
    print(f'Model: {ARTIFACTS / "model.joblib"}')
    print(f'Evaluation: {ARTIFACTS / "evaluation.json"}')


if __name__ == '__main__':
    main()
