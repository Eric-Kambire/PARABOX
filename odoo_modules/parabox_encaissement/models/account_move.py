from odoo import models, fields, api


class AccountMove(models.Model):
    """Extension account.move : bouton accès plan encaissement PARABOX."""
    _inherit = 'account.move'

    encaissement_count = fields.Integer(
        string='Plans d\'encaissement',
        compute='_compute_encaissement_count',
    )

    def _compute_encaissement_count(self):
        for move in self:
            move.encaissement_count = self.env['parabox.encaissement'].search_count(
                [('invoice_id', '=', move.id)]
            )

    def action_view_encaissement(self):
        """Ouvre les plans d'encaissement liés à cette facture."""
        self.ensure_one()
        plans = self.env['parabox.encaissement'].search(
            [('invoice_id', '=', self.id)]
        )
        action = {
            'name': 'Plans d\'encaissement',
            'type': 'ir.actions.act_window',
            'res_model': 'parabox.encaissement',
            'view_mode': 'list,form',
            'context': {'default_invoice_id': self.id},
        }
        if len(plans) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = plans.id
        else:
            action['domain'] = [('invoice_id', '=', self.id)]
        return action
