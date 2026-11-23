# EcoWasteTextile — ML prototype (données synthétiques)

## Important
- Les labels sont simulés, ne proviennent pas de traitements industriels observés.
- Les métriques sont valables uniquement pour le dataset synthétique.
- Les garde-fous du moteur de règles et la décision humaine restent indépendants.
- La prédiction ML se lance sur un rebut **déjà enregistré** et encore Draft / À examiner.

## 1. Dézipper depuis la racine du dépôt

Dans PowerShell, à `D:\ITBS\3BI\ERP\EcoWasteTextile` sur la branche `feature/ml-recovery-prediction`, extraire le ZIP en conservant ses dossiers. Ne pas écraser de fichiers existants. Le ZIP contient `ml/` et deux nouveaux fichiers pour `ecowaste_textile/`.

## 2. Installer les bibliothèques dans l'environnement Python d'Odoo

```powershell
python -m pip install -r requirements-ml.txt
```

⚠ Le Python de ton terminal doit être le même que celui qui lance Odoo. Si le service Odoo utilise un autre environnement, installer aussi les dépendances dans cet environnement.

## 3. Entraîner et tester

```powershell
python ml/generate_dataset.py --rows 3000 --seed 42
python ml/train.py
python ml/predict.py
```

Livrables : `ml/data/textile_waste_synthetic.csv`, `ecowaste_textile/ml_artifacts/model.joblib`, `ecowaste_textile/ml_artifacts/evaluation.json`.

## 4. Enregistrer les nouveaux fichiers dans le module Odoo

Dans `ecowaste_textile/models/__init__.py`, **ajouter** :

```python
from . import ml_prediction
```

Dans `ecowaste_textile/__manifest__.py`, dans la liste existante `data`, **ajouter après** les vues stock scrap :

```python
'views/ml_prediction_views.xml',
```

Ne remplace pas le `stock_scrap.py` existant. Il inclut les corrections T07/T08.

## 5. Redémarrer Odoo et mettre à jour le module

Redémarrer Odoo dans PyCharm, puis Apps > EcoWasteTextile > Upgrade, ou lancer `-u ecowaste_textile -d <ta_base>` depuis le serveur Odoo.

Vérifier sur un rebut **Draft / À examiner** enregistré avec les 7 champs : cliquer « Prédire avec ML », vérifier recommandation, confiance, comparaison et alerte de divergence de sécurité. Une modification d'un critère réinitialise l'ancienne prédiction ML.

## 6. Contrôles de régression

- L'ancienne recommandation par règles doit rester inchangée.
- Le traitement final ne doit jamais être modifié par une prédiction ML.
- Le bouton ML doit être inaccessible sur un traitement validé/réalisé.
- Tester l'absence du modèle, les champs manquants, les désaccords et le niveau de danger élevé.
- Relancer les essais T01–T08 dans Odoo après mise à jour du module.

## 7. Commit

```powershell
git status -sb
git add ml/ ecowaste_textile/models/ml_prediction.py ecowaste_textile/views/ml_prediction_views.xml ecowaste_textile/models/__init__.py ecowaste_textile/__manifest__.py ecowaste_textile/ml_artifacts/ requirements-ml.txt README_ML.md
git commit -m "feat: add synthetic textile ML training and Odoo prediction"
git push -u origin feature/ml-recovery-prediction
```

L'ajout du dataset CSV au commit est facultatif. Éviter de présenter la précision synthétique comme une performance réelle.
