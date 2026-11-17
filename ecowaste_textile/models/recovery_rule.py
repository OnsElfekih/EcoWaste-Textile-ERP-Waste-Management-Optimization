
from odoo import api, fields, models


class RecoveryRule(models.Model):
    _name = "ecowaste.recovery.rule"
    _description = "Règle de valorisation des déchets textiles"
    _order = "sequence, id"

    # ==========================================
    # Configuration de la règle
    # ==========================================

    name = fields.Char(
        string="Nom de la règle",
        required=True
    )

    active = fields.Boolean(
        string="Active",
        default=True
    )

    sequence = fields.Integer(
        string="Priorité",
        default=10
    )

    # ==========================================
    # Critères de caractérisation textile
    # ==========================================

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

    # ==========================================
    # Résultat de la règle
    # ==========================================

    recommendation = fields.Selection([
        ("reuse", "Réutilisation"),
        ("recycle", "Recyclage"),
        ("review", "Évaluation nécessaire"),
        ("disposal", "Élimination"),
    ],
        string="Recommandation",
        required=True
    )

    description = fields.Text(
        string="Description de la règle"
    )

    # ==========================================
    # SEMAINE 5 - T08
    # Recalcul automatique des recommandations
    # ==========================================

    @api.model
    def _recompute_pending_scraps(self):
        """
        Recalculer les recommandations des rebuts
        encore en brouillon et à examiner.

        Les traitements déjà validés ou réalisés
        ne sont pas modifiés.
        """

        Scrap = self.env["stock.scrap"].sudo()

        scraps = Scrap.search([
            ("state", "=", "draft"),
            ("treatment_status", "=", "pending"),
        ])

        if not scraps:
            return

        field = Scrap._fields["recovery_recommendation"]

        self.env.add_to_compute(field, scraps)
        scraps._recompute_recordset()

    # ==========================================
    # Création d'une règle
    # ==========================================

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        records._recompute_pending_scraps()

        return records

    # ==========================================
    # Modification ou désactivation d'une règle
    # ==========================================

    def write(self, vals):
        relevant_fields = {
            "active",
            "sequence",
            "textile_material",
            "waste_origin",
            "waste_cause",
            "textile_quality",
            "scrap_size",
            "textile_condition",
            "hazard_level",
            "recommendation",
        }

        result = super().write(vals)

        if relevant_fields.intersection(vals.keys()):
            self._recompute_pending_scraps()

        return result

    # ==========================================
    # Suppression d'une règle
    # ==========================================

    def unlink(self):
        result = super().unlink()

        self._recompute_pending_scraps()

        return result
