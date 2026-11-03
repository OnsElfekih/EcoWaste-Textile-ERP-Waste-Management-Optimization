
from odoo import models, fields, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    textile_material = fields.Selection([
        ('cotton', 'Coton'),
        ('polyester', 'Polyester'),
        ('mixed', 'Mélange')
    ], string='Textile Material')

    waste_origin = fields.Selection([
        ('cutting', 'Découpe'),
        ('sewing', 'Couture'),
        ('quality', 'Contrôle qualité')
    ], string='Waste Origin')

    waste_cause = fields.Selection([
        ('offcut', 'Chute de tissu'),
        ('defect', 'Défaut de qualité'),
        ('error', 'Erreur de production')
    ], string='Waste Cause')

    textile_quality = fields.Selection([
        ('good', 'Bonne'),
        ('medium', 'Moyenne'),
        ('poor', 'Mauvaise')
    ], string='Textile Quality')

    scrap_size = fields.Selection([
        ('large', 'Grande'),
        ('medium', 'Moyenne'),
        ('small', 'Petite')
    ], string='Scrap Size')

    textile_condition = fields.Selection([
        ('clean', 'Propre'),
        ('dirty', 'Sale')
    ], string='Textile Condition')

    hazard_level = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé')
    ], string='Hazard Level')

    recovery_recommendation = fields.Selection([
        ('reuse', 'Réutilisation'),
        ('recycle', 'Recyclage'),
        ('review', 'Évaluation nécessaire'),
        ('disposal', 'Élimination')
    ],
        string='Recovery Recommendation',
        compute='_compute_recovery_recommendation',
        store=True,
        readonly=True
    )

    @api.depends(
        'textile_material',
        'textile_quality',
        'scrap_size',
        'waste_cause',
        'textile_condition',
        'hazard_level'
    )
    def _compute_recovery_recommendation(self):
        for scrap in self:

            if not all([
                scrap.textile_material,
                scrap.textile_quality,
                scrap.scrap_size,
                scrap.waste_cause,
                scrap.textile_condition,
                scrap.hazard_level
            ]):
                scrap.recovery_recommendation = 'review'
                continue

            material = scrap.textile_material
            quality = scrap.textile_quality
            size = scrap.scrap_size
            cause = scrap.waste_cause
            condition = scrap.textile_condition
            hazard = scrap.hazard_level

            if (
                quality == 'poor'
                or condition == 'dirty'
                or hazard == 'high'
            ):
                recommendation = 'disposal'

            elif (
                quality == 'good'
                and condition == 'clean'
                and hazard == 'low'
                and cause == 'offcut'
                and size in ('large', 'medium')
            ):
                recommendation = 'reuse'

            elif (
                material in ('polyester', 'mixed')
                and quality in ('good', 'medium')
                and condition == 'clean'
                and hazard in ('low', 'medium')
                and size in ('large', 'medium')
            ):
                recommendation = 'recycle'

            elif (
                material == 'cotton'
                and quality in ('good', 'medium')
                and condition == 'clean'
                and hazard == 'low'
                and cause in ('offcut', 'defect')
            ):
                recommendation = 'recycle'

            else:
                recommendation = 'review'

            scrap.recovery_recommendation = recommendation

    def action_recommend_recovery(self):
        self._compute_recovery_recommendation()
        return True
