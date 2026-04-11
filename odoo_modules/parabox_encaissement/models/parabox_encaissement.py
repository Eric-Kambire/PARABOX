from odoo import models, fields, api, _


class ParaboxEncaissement(models.Model):
    """Plan d'encaissement lié à une facture."""
    _name = 'parabox.encaissement'
    _description = 'Plan d\'encaissement PARABOX'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Facture',
        required=True,
        domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
        ondelete='cascade',
        index=True,
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='invoice_id.partner_id',
        store=True,
        readonly=True,
    )
    montant_total = fields.Monetary(
        string='Montant facture',
        related='invoice_id.amount_total',
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='invoice_id.currency_id',
        readonly=True,
    )
    montant_recu = fields.Monetary(
        string='Montant reçu',
        compute='_compute_montants',
        store=True,
        currency_field='currency_id',
    )
    solde_restant = fields.Monetary(
        string='Solde restant',
        compute='_compute_montants',
        store=True,
        currency_field='currency_id',
    )
    statut = fields.Selection([
        ('attente', 'En attente'),
        ('partiel', 'Partiel'),
        ('solde', 'Soldé'),
    ], string='Statut', compute='_compute_montants', store=True, tracking=True)
    ligne_ids = fields.One2many(
        'parabox.encaissement.ligne',
        'encaissement_id',
        string='Lignes de paiement',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('parabox.encaissement') or _('Nouveau')
        return super().create(vals_list)

    @api.depends('ligne_ids.montant', 'ligne_ids.statut', 'montant_total')
    def _compute_montants(self):
        for enc in self:
            lignes_reçues = enc.ligne_ids.filtered(lambda l: l.statut in ('recu', 'encaisse'))
            enc.montant_recu = sum(lignes_reçues.mapped('montant'))
            enc.solde_restant = enc.montant_total - enc.montant_recu
            if enc.montant_recu <= 0:
                enc.statut = 'attente'
            elif abs(enc.solde_restant) < 0.01:
                enc.statut = 'solde'
            else:
                enc.statut = 'partiel'


class ParaboxEncaissementLigne(models.Model):
    """Ligne de paiement dans un plan d'encaissement."""
    _name = 'parabox.encaissement.ligne'
    _description = 'Ligne d\'encaissement PARABOX'
    _order = 'date asc'

    encaissement_id = fields.Many2one(
        'parabox.encaissement',
        string='Plan d\'encaissement',
        required=True,
        ondelete='cascade',
        index=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    date_echeance = fields.Date(
        string='Date échéance',
        help="Pour les traites et chèques à terme.",
    )
    montant = fields.Monetary(
        string='Montant (DH)',
        required=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='encaissement_id.currency_id',
        readonly=True,
    )
    mode_paiement = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('traite', 'Traite'),
        ('virement', 'Virement'),
    ], string='Mode de paiement', required=True, default='cash')
    reference = fields.Char(
        string='N° chèque / Référence',
        help="Numéro de chèque, référence virement ou traite.",
    )
    statut = fields.Selection([
        ('recu', 'Recu'),
        ('encaisse', 'Encaisse'),
        ('rejete', 'Rejete'),
    ], string='Statut', default='recu', required=True)
    note = fields.Text(string='Remarque')
