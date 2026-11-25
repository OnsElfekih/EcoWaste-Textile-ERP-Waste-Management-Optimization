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
    "textile_quality": ["good", "medium", "poor"],
    "scrap_size": ["large", "medium", "small"],
    "textile_condition": ["clean", "dirty"],
    "hazard_level": ["low", "medium", "high"],
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
    # Recommandation certaine du moteur métier Odoo
    if (
        row["hazard_level"] == "high"
        or row["textile_quality"] == "poor"
        or row["textile_condition"] == "dirty"
    ):
        if predictions[i] != "disposal":
            results.append({
                **row.to_dict(),
                "rule": "disposal",
                "ml": predictions[i],
                "confidence": round(
                    float(max(probabilities[i])) * 100, 2
                ),
            })

print("Combinaisons testées :", len(df))
print("Désaccords trouvés :", len(results))

if results:
    print(pd.DataFrame(results).head(10).to_string(index=False))
else:
    print("Aucun désaccord détecté avec la règle de sécurité.")
