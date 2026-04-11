from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_derogation = fields.Boolean(
        string='Dérogation accordée',
        default=False,
        copy=False,
    )
    credit_derogation_by = fields.Many2one(
        'res.users',
        string='Approuvé par',
        copy=False,
        readonly=True,
    )
    credit_derogation_dt = fields.Datetime(
        string='Date dérogation',
        copy=False,
        readonly=True,
    )
    credit_derogation_note = fields.Text(
        string='Raison dérogation',
        copy=False,
    )
    credit_hold_blocked = fields.Boolean(
        string='Bloqué crédit',
        default=False,
        copy=False,
        readonly=True,
    )

    def action_confirm(self):
        """Surcharge : bloquer si limite crédit dépassée."""
        for order in self:
            partner = order.partner_id.commercial_partner_id

            # Vérification compte bloqué
            if partner.credit_hold and not order.credit_derogation:
                self._create_derogation_activity(order)
                order.credit_hold_blocked = True
                raise UserError(_(
                    "Compte client '%s' bloqué (credit_hold).\n"
                    "Une demande de dérogation a été envoyée à l'ADV."
                ) % partner.name)

            # Vérification dépassement limite de crédit
            if not order.credit_derogation and partner.credit_limit > 0:
                encours = partner.encours_actuel
                montant_commande = order.amount_total
                total = encours + montant_commande

                if total > partner.credit_limit:
                    self._create_derogation_activity(order)
                    order.credit_hold_blocked = True
                    raise UserError(_(
                        "Dépassement de limite de crédit pour '%s'.\n"
                        "Encours actuel : %.2f DH\n"
                        "Cette commande : %.2f DH\n"
                        "Total : %.2f DH > Limite : %.2f DH\n\n"
                        "Une demande de dérogation a été envoyée à l'ADV."
                    ) % (
                        partner.name,
                        encours,
                        montant_commande,
                        total,
                        partner.credit_limit,
                    ))

        return super().action_confirm()

    def action_accorder_derogation(self):
        """Action ADV : accorder la dérogation et confirmer la commande."""
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise UserError(_("Seul un responsable commercial (ADV) peut accorder une dérogation."))

        self.write({
            'credit_derogation': True,
            'credit_derogation_by': self.env.uid,
            'credit_derogation_dt': fields.Datetime.now(),
            'credit_hold_blocked': False,
        })
        _logger.info(
            "Dérogation crédit accordée par %s pour la commande %s (client: %s)",
            self.env.user.name, self.name, self.partner_id.name
        )
        # Confirmer la commande après dérogation
        return super(SaleOrder, self).action_confirm()

    def action_refuser_derogation(self):
        """Action ADV : refuser la dérogation."""
        self.ensure_one()
        self.write({'credit_hold_blocked': False})
        return True

    def _create_derogation_activity(self, order):
        """Crée une activité de dérogation pour l'ADV."""
        adv_group = self.env.ref('sales_team.group_sale_manager', raise_if_not_found=False)
        if not adv_group:
            return
        adv_users = adv_group.users
        for user in adv_users:
            try:
                order.with_context(mail_notrack=True).activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=_("Dérogation crédit requise — %s") % order.name,
                    note=_(
                        "La commande %s pour %s nécessite une dérogation.\n"
                        "Montant : %.2f DH | Limite : %.2f DH | Encours : %.2f DH"
                    ) % (
                        order.name,
                        order.partner_id.name,
                        order.amount_total,
                        order.partner_id.commercial_partner_id.credit_limit,
                        order.partner_id.commercial_partner_id.encours_actuel,
                    ),
                )
            except Exception:
                _logger.warning(
                    "Impossible de créer l'activité dérogation pour %s (email non configuré)",
                    order.name
                )
