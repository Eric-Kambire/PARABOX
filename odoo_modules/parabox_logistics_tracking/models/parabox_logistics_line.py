from odoo import models, fields, api


class ParaboxLogisticsLine(models.Model):
    """Ligne de traçabilité logistique — 1 ligne par produit par BL."""
    _name = 'parabox.logistics.line'
    _description = 'Traçabilité Logistique PARABOX'
    _rec_name = 'product_id'
    _order = 'picking_id, product_id'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Bon de Livraison',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Commande client',
        related='picking_id.sale_id',
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
        index=True,
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot / N° série',
    )

    # ─── Les 4 états quantitatifs ─────────────────────────────────────────────
    qty_ordered = fields.Float(
        string='Commandé',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité figurant sur la commande client (BC).",
    )
    qty_prepared = fields.Float(
        string='Préparé',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité sortie du stock par le magasinier (picking).",
    )
    qty_loaded = fields.Float(
        string='Chargé',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité chargée sur le véhicule livreur.",
    )
    qty_delivered = fields.Float(
        string='Livré réel',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité effectivement remise au client (validée sur terrain).",
    )

    # ─── Calculs automatiques ────────────────────────────────────────────────
    ecart_preparation = fields.Float(
        string='Écart prépa (commandé−préparé)',
        compute='_compute_ecarts',
        store=True,
        digits='Product Unit of Measure',
    )
    ecart_livraison = fields.Float(
        string='Écart livraison (préparé−livré)',
        compute='_compute_ecarts',
        store=True,
        digits='Product Unit of Measure',
    )
    ecart_total = fields.Float(
        string='Écart total (commandé−livré)',
        compute='_compute_ecarts',
        store=True,
        digits='Product Unit of Measure',
    )
    taux_service = fields.Float(
        string='Taux de service (%)',
        compute='_compute_ecarts',
        store=True,
    )
    has_ecart = fields.Boolean(
        string='Écart détecté',
        compute='_compute_ecarts',
        store=True,
    )

    # ─── Substitution ────────────────────────────────────────────────────────
    substitution = fields.Boolean(
        string='Substitution',
        default=False,
        help="Coché si un produit de remplacement a été livré.",
    )
    product_sub_id = fields.Many2one(
        'product.product',
        string='Produit substitué',
    )
    note_ecart = fields.Text(
        string='Raison écart / commentaire',
    )

    @api.depends('qty_ordered', 'qty_prepared', 'qty_loaded', 'qty_delivered')
    def _compute_ecarts(self):
        for line in self:
            line.ecart_preparation = line.qty_ordered - line.qty_prepared
            line.ecart_livraison = line.qty_prepared - line.qty_delivered
            line.ecart_total = line.qty_ordered - line.qty_delivered
            if line.qty_ordered > 0:
                line.taux_service = (line.qty_delivered / line.qty_ordered) * 100
            else:
                line.taux_service = 100.0
            line.has_ecart = abs(line.ecart_total) > 0.001
