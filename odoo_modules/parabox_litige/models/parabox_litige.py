from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class ParaboxLitigeStage(models.Model):
    """Étapes du kanban litige."""
    _name = 'parabox.litige.stage'
    _description = 'Étape litige'
    _order = 'sequence, name'

    name = fields.Char(string='Étape', required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Replié dans kanban', default=False)
    is_closed = fields.Boolean(string='Étape finale (clos)', default=False)


class ParaboxLitige(models.Model):
    """Litige PARABOX — lié à une commande, un BL ou une facture."""
    _name = 'parabox.litige'
    _description = 'Litige PARABOX'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_ouverture desc'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(
        string='Référence litige',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
    )
    stage_id = fields.Many2one(
        'parabox.litige.stage',
        string='Étape',
        required=True,
        tracking=True,
        group_expand='_read_group_stage_ids',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        index=True,
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.uid,
        tracking=True,
    )

    # ─── Type et cause ────────────────────────────────────────────────────────
    type_litige = fields.Selection([
        ('ecart_quantite', 'Écart de quantité BC vs BL'),
        ('produit_manquant', 'Produit manquant'),
        ('produit_abime', 'Produit abîmé'),
        ('dlc_proche', 'DLC trop proche'),
        ('substitution_refusee', 'Substitution refusée'),
        ('facture_erreur', 'Erreur facturation'),
        ('avoir_requis', 'Avoir requis'),
        ('autre', 'Autre'),
    ], string='Type de litige', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    montant_litige = fields.Float(
        string='Montant litige (DH)',
        digits=(12, 2),
        tracking=True,
    )

    # ─── Documents liés ────────────────────────────────────────────────────────
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Commande client (BC)',
        index=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Bon de livraison (BL)',
        index=True,
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Facture / Avoir',
        domain=[('move_type', 'in', ['out_invoice', 'out_refund'])],
        index=True,
    )

    # ─── Dates et SLA ─────────────────────────────────────────────────────────
    date_ouverture = fields.Date(
        string='Date ouverture',
        default=fields.Date.today,
        required=True,
        readonly=True,
    )
    date_resolution = fields.Date(string='Date résolution', tracking=True)
    delai_jours = fields.Integer(
        string='Délai (jours)',
        compute='_compute_delai_jours',
        store=True,
    )
    sla_statut = fields.Selection([
        ('ok', 'OK'),
        ('alerte', 'Alerte (>3j)'),
        ('escalade', 'Escalade (>7j)'),
    ], string='SLA', compute='_compute_sla_statut', store=True)

    # ─── Resolution ───────────────────────────────────────────────────────────
    resolution_note = fields.Text(string='Note de résolution', tracking=True)
    avoir_id = fields.Many2one(
        'account.move',
        string='Avoir émis',
        domain=[('move_type', '=', 'out_refund')],
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('parabox.litige') or _('Nouveau')
        return super().create(vals_list)

    @api.depends('date_ouverture', 'date_resolution', 'stage_id')
    def _compute_delai_jours(self):
        today = date.today()
        for litige in self:
            if litige.date_ouverture:
                end = litige.date_resolution or today
                litige.delai_jours = (end - litige.date_ouverture).days
            else:
                litige.delai_jours = 0

    @api.depends('delai_jours', 'stage_id')
    def _compute_sla_statut(self):
        for litige in self:
            if litige.stage_id and litige.stage_id.is_closed:
                litige.sla_statut = 'ok'
            elif litige.delai_jours > 7:
                litige.sla_statut = 'escalade'
            elif litige.delai_jours > 3:
                litige.sla_statut = 'alerte'
            else:
                litige.sla_statut = 'ok'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['parabox.litige.stage'].search([], order=order)

    def action_escalade_direction(self):
        """Escalade vers la direction."""
        self.ensure_one()
        direction_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
        if direction_group:
            for user in direction_group.users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=_("ESCALADE — Litige %s (%d jours)") % (self.name, self.delai_jours),
                    note=_("Ce litige dépasse 7 jours sans résolution. Client: %s. Montant: %.2f DH")
                    % (self.partner_id.name, self.montant_litige),
                )
        return True

    @api.model
    def cron_check_sla(self):
        """Cron quotidien : vérifier les SLA et escalader si besoin."""
        litiges_escalade = self.search([
            ('stage_id.is_closed', '=', False),
            ('delai_jours', '>', 7),
            ('sla_statut', '!=', 'escalade'),
        ])
        for l in litiges_escalade:
            l.action_escalade_direction()
            _logger.warning("Litige %s escaladé vers direction (%d jours)", l.name, l.delai_jours)
