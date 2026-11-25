from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss

BASE = Path("ml")
MODEL = Path("ecowaste_textile/ml_artifacts/model.joblib")

artifact = joblib.load(MODEL)
pipeline = artifact["pipeline"]
features = artifact["features"]

data = pd.read_csv(BASE / "data/textile_waste_synthetic.csv")

X = data[features]
y = data["final_treatment"]

_, X_test, _, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

predictions = pipeline.predict(X_test)
probabilities = pipeline.predict_proba(X_test)

confidence = probabilities.max(axis=1)
correct = np.asarray(predictions == y_test)

print("MODELE :", artifact["version"])
print("OBSERVATIONS :", len(y_test))
print("LOG LOSS :", round(log_loss(
    y_test, probabilities,
    labels=pipeline.classes_
), 4))

print("\nCALIBRATION PAR INTERVALLE")
for low in np.arange(0, 1, 0.1):
    high = low + 0.1
    mask = (confidence >= low) & (confidence < high)
    if high >= 1:
        mask = confidence >= low
    if mask.sum():
        print(
            f"{low*100:.0f}-{high*100:.0f}% | "
            f"N={mask.sum()} | "
            f"Confiance moyenne={confidence[mask].mean()*100:.1f}% | "
            f"Accuracy={correct[mask].mean()*100:.1f}%"
        )

print("\nCOMPARAISON DES SEUILS")
for threshold in [0.60, 0.70, 0.80, 0.90]:
    mask = confidence >= threshold
    count = int(mask.sum())
    coverage = count / len(y_test) * 100
    accuracy = correct[mask].mean() * 100 if count else float("nan")

    print(
        f"Seuil={threshold*100:.0f}% | "
        f"Retenus={count} | "
        f"Couverture={coverage:.2f}% | "
        f"Accuracy={accuracy:.2f}%"
    )
