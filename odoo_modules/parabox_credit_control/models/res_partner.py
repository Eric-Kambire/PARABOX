from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string='Limite crédit (DH)',
        default=10000.0,
        help="Montant maximum d'encours autorisé pour ce client."
    )
    credit_hold = fields.Boolean(
        string='Compte bloqué',
        default=False,
        help="Si coché, toute nouvelle commande est bloquée automatiquement."
    )
    encours_actuel = fields.Float(
        string='Encours actuel (DH)',
        compute='_compute_encours_actuel',
        store=False,
        help="Somme des factures ouvertes non payées."
    )
    taux_utilisation_credit = fields.Float(
        string='Utilisation crédit (%)',
        compute='_compute_encours_actuel',
        store=False,
    )

    @api.depends('invoice_ids.amount_residual', 'invoice_ids.state', 'invoice_ids.move_type')
    def _compute_encours_actuel(self):
        for partner in self:
            domain = [
                ('partner_id', 'child_of', partner.id),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'not in', ['paid', 'reversed']),
            ]
            invoices = self.env['account.move'].search(domain)
            encours = sum(invoices.mapped('amount_residual'))
            partner.encours_actuel = encours
            if partner.credit_limit > 0:
                partner.taux_utilisation_credit = (encours / partner.credit_limit) * 100
            else:
                partner.taux_utilisation_credit = 0.0
