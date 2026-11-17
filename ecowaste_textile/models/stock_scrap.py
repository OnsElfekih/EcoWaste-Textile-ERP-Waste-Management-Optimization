from odoo import api, fields, models
from odoo.exceptions import UserError


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    # SEMAINE 3 : Caractérisation des déchets textiles
    textile_material = fields.Selection([
        ("cotton", "Coton"),
        ("polyester", "Polyester"),
        ("mixed", "Mélange"),
    ], string="Matière textile")

    waste_origin = fields.Selection([
        ("cutting", "Découpe"),
        ("sewing", "Couture"),
        ("quality", "Contrôle qualité"),
    ], string="Origine du déchet")

    waste_cause = fields.Selection([
        ("offcut", "Chute de tissu"),
        ("defect", "Défaut de qualité"),
        ("error", "Erreur de production"),
    ], string="Cause du déchet")

    textile_quality = fields.Selection([
        ("good", "Bonne"),
        ("medium", "Moyenne"),
        ("poor", "Mauvaise"),
    ], string="Qualité textile")

    scrap_size = fields.Selection([
        ("large", "Grande"),
        ("medium", "Moyenne"),
        ("small", "Petite"),
    ], string="Taille du déchet")

    textile_condition = fields.Selection([
        ("clean", "Propre"),
        ("dirty", "Sale"),
    ], string="État du textile")

    hazard_level = fields.Selection([
        ("low", "Faible"),
        ("medium", "Moyen"),
        ("high", "Élevé"),
    ], string="Niveau de risque")

    recovery_recommendation = fields.Selection([
        ("reuse", "Réutilisation"),
        ("recycle", "Recyclage"),
        ("review", "Évaluation nécessaire"),
        ("disposal", "Élimination"),
    ],
        string="Recommandation de valorisation",
        compute="_compute_recovery_recommendation",
        store=True,
        readonly=True,
    )
# SEMAINE 4 : Décision et traçabilité du traitement réel
    final_treatment = fields.Selection([
        ("reuse", "Réutilisation"),
        ("recycle", "Recyclage"),
        ("disposal", "Élimination"),
    ], string="Traitement final", copy=False)

    treatment_status = fields.Selection([
        ("pending", "À examiner"),
        ("validated", "Validé"),
        ("completed", "Réalisé"),
    ],
        string="Statut du traitement",
        default="pending",
        required=True,
        copy=False,
    )

    treatment_responsible_id = fields.Many2one(
        "res.users",
        string="Responsable du traitement",
        copy=False,
    )
    treatment_date = fields.Datetime(
        string="Date de validation du traitement",
        copy=False,
    )

    treatment_justification = fields.Text(
        string="Justification du traitement",
        copy=False,
    )

    # SEMAINE 5 : Recommandation fondée sur des règles configurables
    @api.depends(
        "textile_material",
        "waste_origin",
        "waste_cause",
        "textile_quality",
        "scrap_size",
        "textile_condition",
        "hazard_level",
    )
    def _compute_recovery_recommendation(self):
        criteria = (
            "textile_material",
            "waste_origin",
            "waste_cause",
            "textile_quality",
            "scrap_size",
            "textile_condition",
            "hazard_level",
        )
        # Origine facultative pour rester compatible avec les anciens rebuts.
        required_fields = (
            "textile_material",
            "waste_cause",
            "textile_quality",
            "scrap_size",
            "textile_condition",
            "hazard_level",
        )

        # L'utilisateur de stock peut consulter indirectement les règles,
        # dont la configuration reste réservée à l'administrateur.
        rules = self.env["ecowaste.recovery.rule"].sudo().search(
            [("active", "=", True)],
            order="sequence, id",
        )

        for scrap in self:
            # Garde-fou prioritaire : les règles ne peuvent pas le contourner.
            if (
                scrap.hazard_level == "high"
                or scrap.textile_quality == "poor"
                or scrap.textile_condition == "dirty"
            ):
                scrap.recovery_recommendation = "disposal"
                continue

            if not all(scrap[field] for field in required_fields):
                scrap.recovery_recommendation = "review"
                continue

            recommendation = "review"
            for rule in rules:
                # Un critère vide dans une règle signifie « toute valeur ».
                if all(
                    not rule[field] or rule[field] == scrap[field]
                    for field in criteria
                ):
                    recommendation = rule.recommendation
                    break

            scrap.recovery_recommendation = recommendation

    # Actualisation du formulaire sans enregistrement préalable.
    @api.onchange(
        "textile_material",
        "waste_origin",
        "waste_cause",
        "textile_quality",
        "scrap_size",
        "textile_condition",
        "hazard_level",
    )
    def _onchange_recovery_recommendation(self):
        self._compute_recovery_recommendation()

    # Recalcul facultatif, notamment après un changement de règle.
    def action_recommend_recovery(self):
        self._compute_recovery_recommendation()
        return True

    # SEMAINE 4 : Validation humaine du traitement final
    def action_validate_treatment(self):
        for scrap in self:
            if scrap.treatment_status != "pending":
                raise UserError(
                    "Seul un traitement à examiner peut être validé."
                )

            if not scrap.final_treatment:
                raise UserError(
                    "Veuillez sélectionner le traitement final."
                )

            if not (scrap.treatment_justification or "").strip():
                raise UserError(
                    "Veuillez justifier la décision de traitement."
                )

            scrap.write({
                "treatment_status": "validated",
                "treatment_responsible_id": self.env.user.id,
                "treatment_date": fields.Datetime.now(),
            })
        return True

    # ==========================================
    # SEMAINE 5 : Sécurisation du workflow
    # ==========================================

    def action_complete_treatment(self):
        for scrap in self:

            # Vérifier la validation humaine
            if scrap.treatment_status != "validated":
                raise UserError(
                    "Le traitement doit être validé "
                    "avant sa réalisation."
                )

            # Vérifier la sortie du stock
            if scrap.state != "done":
                raise UserError(
                    "Impossible de terminer le traitement. "
                    "Veuillez d'abord valider le rebut "
                    "dans Inventaire."
                )

            # Clôturer le traitement EcoWaste
            scrap.write({
                "treatment_status": "completed",
            })

        return True
