"""Generate a reproducible *synthetic* textile-waste classification dataset.
Labels come from documented probabilistic assumptions, NOT Odoo's rule engine
or observed industrial outcomes. Do not claim real-world predictive validity.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

FEATURES = {
    'textile_material': ['cotton', 'polyester', 'mixed'],
    'waste_origin': ['cutting', 'sewing', 'quality'],
    'waste_cause': ['offcut', 'defect', 'error'],
    'textile_quality': ['good', 'medium', 'poor'],
    'scrap_size': ['large', 'medium', 'small'],
    'textile_condition': ['clean', 'dirty'],
    'hazard_level': ['low', 'medium', 'high'],
}
LABELS = np.array(['reuse', 'recycle', 'disposal'])


def generate(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sampling = {
        'textile_material': [.45, .35, .20],
        'waste_origin': [.45, .30, .25],
        'waste_cause': [.48, .36, .16],
        'textile_quality': [.44, .37, .19],
        'scrap_size': [.35, .40, .25],
        'textile_condition': [.83, .17],
        'hazard_level': [.68, .24, .08],
    }
    frame = pd.DataFrame({k: rng.choice(v, size=n, p=sampling[k]) for k, v in FEATURES.items()})
    # Probabilistic preferences simulate heterogeneity among treatment decisions.
    # Important: not the Odoo rule-engine label function.
    reuse = np.zeros(n, dtype=float)
    recycle = np.zeros(n, dtype=float)
    disposal = np.full(n, -0.6)
    reuse += np.select([frame.textile_quality == 'good', frame.textile_quality == 'medium'], [2.0, .2], default=-1.6)
    recycle += np.select([frame.textile_quality == 'medium', frame.textile_quality == 'good'], [1.2, .2], default=-.1)
    disposal += np.where(frame.textile_quality == 'poor', 2.0, 0)
    reuse += np.where(frame.scrap_size == 'large', .8, np.where(frame.scrap_size == 'small', -.5, 0))
    recycle += np.where(frame.scrap_size == 'small', .55, 0)
    reuse += np.where(frame.textile_material == 'cotton', .55, 0)
    recycle += np.where(frame.textile_material == 'polyester', .75, 0)
    recycle += np.where(frame.textile_material == 'mixed', .25, 0)
    reuse += np.where(frame.waste_cause == 'offcut', .7, 0)
    recycle += np.where(frame.waste_cause == 'defect', .3, 0)
    reuse += np.where(frame.waste_origin == 'cutting', .25, 0)
    disposal += np.where(frame.textile_condition == 'dirty', 2.7, 0)
    reuse -= np.where(frame.textile_condition == 'dirty', 2.2, 0)
    disposal += np.select([frame.hazard_level == 'high', frame.hazard_level == 'medium'], [4.5, .9], default=0)
    reuse -= np.where(frame.hazard_level == 'high', 4.0, 0)
    recycle -= np.where(frame.hazard_level == 'high', 2.8, 0)
    # Enforce a simulated safety policy in training labels for high-risk samples.
    scores = np.column_stack([reuse, recycle, disposal]) / 0.65
    scores -= scores.max(axis=1, keepdims=True)
    probabilities = np.exp(scores)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    random_draw = rng.random(n)
    labels = LABELS[(random_draw[:, None] > probabilities.cumsum(axis=1)).sum(axis=1)]
    labels[frame.hazard_level.eq('high').to_numpy()] = 'disposal'
    frame['final_treatment'] = labels
    return frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.rows < 300:
        parser.error('--rows must be at least 300 for a meaningful demonstration split')
    output = Path(__file__).resolve().parent / 'data' / 'textile_waste_synthetic.csv'
    output.parent.mkdir(parents=True, exist_ok=True)
    data = generate(args.rows, args.seed)
    data.to_csv(output, index=False)
    print(f'Dataset: {output} ({len(data)} rows, seed={args.seed})')
    print(data.final_treatment.value_counts().to_string())


if __name__ == '__main__':
    main()
