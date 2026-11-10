
from odoo import models, fields


class RecoveryRule(models.Model):
    _name = "ecowaste.recovery.rule"
    _description = "Règle de valorisation des déchets textiles"
    _order = "sequence, id"

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
