from itertools import product
from pathlib import Path

import joblib
import pandas as pd

model_path = Path("ecowaste_textile/ml_artifacts/model.joblib")
artifact = joblib.load(model_path)
pipeline = artifact["pipeline"]

features = {
    "textile_material": ["cotton", "polyester", "mixed"],
    "waste_origin": ["cutting", "sewing", "quality"],
    "waste_cause": ["offcut", "defect", "error"],
    "textile_quality": ["good", "medium"],
    "scrap_size": ["large", "medium", "small"],
    "textile_condition": ["clean"],
    "hazard_level": ["low", "medium"],
}

keys = list(features)

rows = [
    dict(zip(keys, values))
    for values in product(*(features[k] for k in keys))
]

df = pd.DataFrame(rows)

predictions = pipeline.predict(df[artifact["features"]])
probabilities = pipeline.predict_proba(df[artifact["features"]])

results = []

for i, row in df.iterrows():
    confidence = float(max(probabilities[i])) * 100

    if confidence >= 80.0:
        results.append({
            **row.to_dict(),
            "ml_prediction": predictions[i],
            "confidence": round(confidence, 2),
        })

results = sorted(
    results,
    key=lambda item: item["confidence"],
    reverse=True,
)

print("Combinaisons sans garde-fou :", len(df))
print("Prédictions ML >= 80 % :", len(results))

if results:
    print(pd.DataFrame(results).head(15).to_string(index=False))
else:
    print("Aucun scénario trouvé avec confiance >= 80 %.")
