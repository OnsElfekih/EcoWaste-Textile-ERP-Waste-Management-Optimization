import joblib
import pandas as pd
from itertools import product

artifact = joblib.load(
    "ecowaste_textile/ml_artifacts/model.joblib"
)
pipeline = artifact["pipeline"]

rows = []

for origin, cause, size in product(
    ["cutting", "sewing", "quality"],
    ["offcut", "defect", "error"],
    ["large", "medium", "small"],
):
    rows.append({
        "textile_material": "polyester",
        "waste_origin": origin,
        "waste_cause": cause,
        "textile_quality": "medium",
        "scrap_size": size,
        "textile_condition": "clean",
        "hazard_level": "low",
    })

df = pd.DataFrame(rows)

predictions = pipeline.predict(df[artifact["features"]])
probabilities = pipeline.predict_proba(
    df[artifact["features"]]
)

results = []

for i, row in df.iterrows():
    confidence = max(probabilities[i]) * 100

    if predictions[i] != "recycle" and confidence >= 80:
        results.append({
            **row.to_dict(),
            "ml_prediction": predictions[i],
            "confidence": round(float(confidence), 2),
        })

print("Combinaisons examinées :", len(df))
print("Candidats RT08-C :", len(results))

if results:
    print(pd.DataFrame(results).to_string(index=False))
else:
    print("Aucun candidat trouvé.")
