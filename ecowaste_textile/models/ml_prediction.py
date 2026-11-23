"""EcoWaste ML integration: separate from rules and from human decisions."""
from pathlib import Path
from odoo import api, fields, models
from odoo.exceptions import UserError

ML_FEATURES = (
    'textile_material', 'waste_origin', 'waste_cause', 'textile_quality',
    'scrap_size', 'textile_condition', 'hazard_level',
)


class StockScrapML(models.Model):
    _inherit = 'stock.scrap'

    ml_recommendation = fields.Selection([
        ('reuse', 'Réutilisation'), ('recycle', 'Recyclage'),
        ('disposal', 'Élimination'),
    ], string='Prédiction Machine Learning', readonly=True, copy=False)
    ml_confidence = fields.Float(string='Confiance ML (%)', readonly=True, copy=False,
                                 digits=(5, 1))
    ml_model_version = fields.Char(string='Version du modèle ML', readonly=True, copy=False)
    ml_predicted_at = fields.Datetime(string='Date de prédiction ML', readonly=True, copy=False)
    ml_comparison = fields.Selection([
        ('agreement', 'Accord'), ('divergence', 'Divergence'),
        ('review', 'Règles : examen manuel'), ('unavailable', 'Comparaison indisponible'),
    ], string='Comparaison règles / ML', compute='_compute_ml_comparison')
    ml_safety_alert = fields.Boolean(string='Divergence avec garde-fou métier',
                                     compute='_compute_ml_safety_alert')

    @api.depends('ml_recommendation', 'recovery_recommendation')
    def _compute_ml_comparison(self):
        for scrap in self:
            if not scrap.ml_recommendation or not scrap.recovery_recommendation:
                scrap.ml_comparison = 'unavailable'
            elif scrap.recovery_recommendation == 'review':
                scrap.ml_comparison = 'review'
            else:
                scrap.ml_comparison = ('agreement' if scrap.ml_recommendation == scrap.recovery_recommendation
                                       else 'divergence')

    @api.depends('ml_recommendation', 'hazard_level', 'textile_condition', 'textile_quality')
    def _compute_ml_safety_alert(self):
        for scrap in self:
            guarded = (scrap.hazard_level == 'high' or scrap.textile_quality == 'poor'
                       or scrap.textile_condition == 'dirty')
            scrap.ml_safety_alert = bool(guarded and scrap.ml_recommendation and
                                         scrap.ml_recommendation != 'disposal')

    def action_predict_ml(self):
        """Explicit opt-in prediction. Never changes recommendation or final treatment."""
        try:
            import joblib
            import pandas as pd
        except ImportError as exc:
            raise UserError('Installer pandas, scikit-learn et joblib dans le Python du serveur Odoo.') from exc
        path = Path(__file__).resolve().parents[1] / 'ml_artifacts' / 'model.joblib'
        if not path.exists():
            raise UserError('Modèle ML absent. Exécutez python ml/train.py puis redémarrez Odoo.')
        try:
            artifact = joblib.load(path)  # Load only trusted locally generated artifact.
            pipeline = artifact['pipeline']
            expected = artifact['features']
        except Exception as exc:
            raise UserError('Impossible de charger le modèle ML local.') from exc
        if list(expected) != list(ML_FEATURES):
            raise UserError('La version du modèle ML ne correspond pas aux champs Odoo.')
        for scrap in self:
            if scrap.state != 'draft' or scrap.treatment_status != 'pending':
                raise UserError('La prédiction ML est réservée aux rebuts Draft / À examiner.')
            row = {field: scrap[field] for field in ML_FEATURES}
            if not all(row.values()):
                raise UserError('Renseignez les sept caractéristiques textiles avant de prédire.')
            try:
                frame = pd.DataFrame([row], columns=ML_FEATURES)
                prediction = str(pipeline.predict(frame)[0])
                confidence = float(max(pipeline.predict_proba(frame)[0])) * 100
            except Exception as exc:
                raise UserError('La prédiction ML a échoué. Vérifiez la compatibilité du modèle.') from exc
            if prediction not in ('reuse', 'recycle', 'disposal'):
                raise UserError('Classe prédite inconnue.')
            scrap.write({
                'ml_recommendation': prediction,
                'ml_confidence': confidence,
                'ml_model_version': artifact.get('version', 'synthetic-v1'),
                'ml_predicted_at': fields.Datetime.now(),
            })
        return True

    def write(self, vals):
        """A changed input invalidates only the ML prediction on pending scraps."""
        if set(vals).intersection(ML_FEATURES):
            eligible = self.filtered(lambda s: s.state == 'draft' and s.treatment_status == 'pending')
            result = super().write(vals)
            if eligible:
                super(StockScrapML, eligible).write({
                    'ml_recommendation': False, 'ml_confidence': 0.0,
                    'ml_model_version': False, 'ml_predicted_at': False,
                })
            return result
        return super().write(vals)
