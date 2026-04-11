from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    logistics_line_ids = fields.One2many(
        'parabox.logistics.line',
        'picking_id',
        string='Traçabilité logistique',
    )
    has_logistics_ecart = fields.Boolean(
        string='Écart logistique',
        compute='_compute_has_logistics_ecart',
        store=True,
    )
    taux_service_global = fields.Float(
        string='Taux de service global (%)',
        compute='_compute_has_logistics_ecart',
        store=True,
    )

    @api.depends('logistics_line_ids.has_ecart', 'logistics_line_ids.taux_service')
    def _compute_has_logistics_ecart(self):
        for picking in self:
            lines = picking.logistics_line_ids
            picking.has_logistics_ecart = any(lines.mapped('has_ecart'))
            if lines:
                picking.taux_service_global = sum(lines.mapped('taux_service')) / len(lines)
            else:
                picking.taux_service_global = 100.0

    def _action_done(self):
        """Surcharge Odoo 17 : auto-créer les lignes de traçabilité depuis les move.lines."""
        # Ne pas appeler _message_compute_author ici — laisser super() gérer les emails
        res = super()._action_done()
        for picking in self:
            if picking.picking_type_code == 'outgoing':
                try:
                    picking._auto_create_logistics_lines()
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(
                        "Erreur auto-création lignes traçabilité picking %s: %s", picking.id, e
                    )
        return res

    def _auto_create_logistics_lines(self):
        """Crée automatiquement les lignes de traçabilité depuis les move.lines validées."""
        existing_products = self.logistics_line_ids.mapped('product_id')
        for move in self.move_ids.filtered(lambda m: m.state == 'done'):
            if move.product_id in existing_products:
                continue
            qty_ordered = move.sale_line_id.product_uom_qty if move.sale_line_id else 0.0
            # Odoo 17 : quantity_done renommé en quantity
            try:
                qty_done = float(move.quantity)
            except AttributeError:
                qty_done = float(getattr(move, 'quantity_done', 0.0) or 0.0)
            self.env['parabox.logistics.line'].create({
                'picking_id': self.id,
                'product_id': move.product_id.id,
                'lot_id': move.move_line_ids[:1].lot_id.id if move.move_line_ids else False,
                'qty_ordered': qty_ordered,
                'qty_prepared': qty_done,
                'qty_loaded': qty_done,
                'qty_delivered': qty_done,
            })
