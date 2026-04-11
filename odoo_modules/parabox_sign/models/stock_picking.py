from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sign_request_ids = fields.One2many(
        'parabox.sign.request',
        'picking_id',
        string='Demandes de signature',
    )
    sign_count = fields.Integer(
        string='Signatures',
        compute='_compute_sign_count',
    )
    is_signed = fields.Boolean(
        string='Signé',
        compute='_compute_sign_count',
        store=True,
    )

    @api.depends('sign_request_ids.signed')
    def _compute_sign_count(self):
        for picking in self:
            requests = picking.sign_request_ids
            picking.sign_count = len(requests)
            picking.is_signed = any(requests.mapped('signed'))

    def action_create_sign_request(self):
        """Créer une demande de signature pour ce BL."""
        self.ensure_one()
        existing = self.sign_request_ids.filtered(lambda r: r.statut not in ('signed', 'failed'))
        if existing:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'parabox.sign.request',
                'res_id': existing[0].id,
                'view_mode': 'form',
                'target': 'new',
            }
        sign_req = self.env['parabox.sign.request'].create({
            'picking_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'parabox.sign.request',
            'res_id': sign_req.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_sign_requests(self):
        """Voir toutes les signatures de ce BL."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Signatures — %s') % self.name,
            'res_model': 'parabox.sign.request',
            'view_mode': 'tree,form',
            'domain': [('picking_id', '=', self.id)],
        }
