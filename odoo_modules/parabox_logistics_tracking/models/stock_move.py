from odoo import models, fields


class StockMove(models.Model):
    """Extension du mouvement de stock — suivi du scan de chargement livreur."""
    _inherit = 'stock.move'

    parabox_scan_confirmed = fields.Boolean(
        string='Scan chargement confirmé',
        default=False,
        help="Coché automatiquement quand le livreur scanne ce produit "
             "en zone expédition. Obligatoire avant confirmation de récupération.",
    )
    parabox_scan_datetime = fields.Datetime(
        string='Date/heure scan livreur',
        readonly=True,
        copy=False,
        help="Timestamp automatique du scan de confirmation par le livreur.",
    )
