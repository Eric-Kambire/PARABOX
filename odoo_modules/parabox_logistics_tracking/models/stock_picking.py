import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ─── Traçabilité logistique ───────────────────────────────────────────────
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

    # ─── Timestamps T1 / T2 / T3 ─────────────────────────────────────────────
    datetime_t1 = fields.Datetime(
        string='T1 — Préparation terminée',
        readonly=True,
        copy=False,
        help="Auto : magasinier valide PBX/PICK — marchandise déposée en zone expédition.",
    )
    datetime_t2 = fields.Datetime(
        string='T2 — Prise en charge livreur',
        readonly=True,
        copy=False,
        help="Auto : livreur confirme récupération (après scan tous produits).",
    )
    datetime_t3 = fields.Datetime(
        string='T3 — Livraison confirmée (OTP)',
        readonly=True,
        copy=False,
        help="Auto : client valide OTP + signe BIC → BL DONE automatiquement.",
    )
    duree_prise_en_charge = fields.Float(
        string='Délai prise en charge (min)',
        compute='_compute_durees_livraison',
        store=True,
        digits=(10, 1),
        help="T2 − T1 : temps entre fin préparation magasinier et départ livreur.",
    )
    duree_livraison = fields.Float(
        string='Durée livraison (min)',
        compute='_compute_durees_livraison',
        store=True,
        digits=(10, 1),
        help="T3 − T2 : temps de livraison réelle chez le client.",
    )

    @api.depends('datetime_t1', 'datetime_t2', 'datetime_t3')
    def _compute_durees_livraison(self):
        for picking in self:
            if picking.datetime_t1 and picking.datetime_t2:
                delta = picking.datetime_t2 - picking.datetime_t1
                picking.duree_prise_en_charge = delta.total_seconds() / 60.0
            else:
                picking.duree_prise_en_charge = 0.0
            if picking.datetime_t2 and picking.datetime_t3:
                delta = picking.datetime_t3 - picking.datetime_t2
                picking.duree_livraison = delta.total_seconds() / 60.0
            else:
                picking.duree_livraison = 0.0

    @api.depends('logistics_line_ids.has_ecart', 'logistics_line_ids.taux_service')
    def _compute_has_logistics_ecart(self):
        for picking in self:
            lines = picking.logistics_line_ids
            picking.has_logistics_ecart = any(lines.mapped('has_ecart'))
            if lines:
                picking.taux_service_global = sum(lines.mapped('taux_service')) / len(lines)
            else:
                picking.taux_service_global = 100.0

    # ─────────────────────────────────────────────────────────────────────────
    # GARDE-FOU STOCK — Override action_assign()
    # ─────────────────────────────────────────────────────────────────────────
    def action_assign(self):
        """
        Surcharge de 'Vérifier la disponibilité'.
        Après réservation Odoo, on analyse le résultat et on notifie :
          - Stock 0       → alerte rouge dans le chatter + activité urgente
          - Stock partiel → avertissement orange avec détail produit/qté
          - Stock complet → message de confirmation (optionnel)
        Seuls les PBX/PICK (internal) déclenchent les notifications.
        """
        res = super().action_assign()

        for picking in self:
            # On ne gère que les opérations de préparation interne (PBX/PICK)
            if picking.picking_type_code != 'internal':
                continue

            # ── Analyse des manques après réservation ──────────────────
            lines_details = []
            total_demande = 0.0
            total_reserve = 0.0

            for move in picking.move_ids:
                demande = move.product_uom_qty
                # Odoo 17 : reserved_availability → move.quantity
                reserve = getattr(move, 'reserved_availability', None)
                if reserve is None:
                    reserve = move.quantity or 0.0
                total_demande += demande
                total_reserve += reserve

                if reserve < demande:
                    manque = demande - reserve
                    lines_details.append({
                        'produit': move.product_id.display_name,
                        'demande': demande,
                        'reserve': reserve,
                        'manque': manque,
                    })

            # ── Cas 1 : Aucun stock disponible ─────────────────────────
            if picking.state == 'confirmed' and total_reserve == 0:
                detail_html = ''.join([
                    f"<li><b>{l['produit']}</b> : "
                    f"{int(l['demande'])} demandé(s) — "
                    f"<span style='color:red'><b>0 disponible</b></span></li>"
                    for l in lines_details
                ])
                msg = _(
                    "<b>🚫 RUPTURE DE STOCK — Préparation impossible</b><br/>"
                    "Aucune quantité disponible pour ce bon de préparation :<br/>"
                    "<ul>%(detail)s</ul>"
                    "👉 <b>Action requise :</b> Demander un réapprovisionnement au responsable."
                ) % {'detail': detail_html}

                picking.message_post(
                    body=msg,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
                # Activité urgente pour le magasinier
                try:
                    picking.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=_("🚫 Rupture stock — réappro nécessaire"),
                        note=_(
                            "Stock insuffisant pour préparer ce BL. "
                            "Aucune quantité réservée. "
                            "Contactez le responsable pour réapprovisionner."
                        ),
                    )
                except Exception as e:
                    _logger.warning("Impossible de créer l'activité rupture: %s", e)

                # Notifier le commercial lié à la commande
                if picking.sale_id:
                    picking.sale_id.message_post(
                        body=_(
                            "<b>⚠️ Rupture stock</b> : La préparation <b>%(pick)s</b> "
                            "liée à cette commande ne peut pas démarrer.<br/>"
                            "Aucune quantité disponible en stock."
                        ) % {'pick': picking.name},
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                _logger.warning(
                    "PARABOX garde-fou: Rupture totale sur %s — 0/%s unités disponibles",
                    picking.name, total_demande
                )

            # ── Cas 2 : Stock partiel ───────────────────────────────────
            elif picking.state == 'partially_available' or (
                picking.state in ('assigned', 'partially_available') and lines_details
            ):
                detail_html = ''.join([
                    f"<li><b>{l['produit']}</b> : "
                    f"{int(l['reserve'])}/{int(l['demande'])} réservé(s) "
                    f"— <span style='color:orange'><b>manque {int(l['manque'])}</b></span></li>"
                    for l in lines_details
                ])
                msg = _(
                    "<b>⚠️ STOCK PARTIEL — Préparation incomplète possible</b><br/>"
                    "Certains produits ne sont pas entièrement disponibles :<br/>"
                    "<ul>%(detail)s</ul>"
                    "👉 <b>Vous pouvez :</b><br/>"
                    "• Valider partiellement → un reliquat sera créé automatiquement<br/>"
                    "• Attendre le réapprovisionnement pour livrer en une fois"
                ) % {'detail': detail_html}

                picking.message_post(
                    body=msg,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
                if picking.sale_id:
                    picking.sale_id.message_post(
                        body=_(
                            "<b>⚠️ Stock partiel</b> sur <b>%(pick)s</b> : "
                            "%(reserve)g/%(demande)g unité(s) disponible(s)."
                        ) % {
                            'pick': picking.name,
                            'reserve': total_reserve,
                            'demande': total_demande,
                        },
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
                _logger.info(
                    "PARABOX garde-fou: Stock partiel sur %s — %g/%g unités",
                    picking.name, total_reserve, total_demande
                )

        return res

    # ─────────────────────────────────────────────────────────────────────────
    def _action_done(self):
        """
        Surcharge Odoo 17 :
        - Picking INTERNAL validé → enregistre T1 sur le PBX/OUT associé
        - Picking OUTGOING validé → auto-crée les lignes de traçabilité
        """
        res = super()._action_done()

        for picking in self:
            # ── T1 : magasinier valide le PICK (internal) ──────────────
            if picking.picking_type_code == 'internal':
                try:
                    now = fields.Datetime.now()
                    # Les PBX/PICK et PBX/OUT du même SO partagent le même group_id
                    if picking.group_id:
                        related_outs = self.env['stock.picking'].search([
                            ('group_id', '=', picking.group_id.id),
                            ('picking_type_code', '=', 'outgoing'),
                            ('state', 'not in', ('done', 'cancel')),
                            ('datetime_t1', '=', False),
                        ])
                        if related_outs:
                            related_outs.write({'datetime_t1': now})
                            _logger.info(
                                "PARABOX T1: %s → %d BL(s) marqués prêts à [%s]",
                                picking.name, len(related_outs), now
                            )
                except Exception as e:
                    _logger.warning("PARABOX: erreur set T1 depuis %s: %s", picking.name, e)

            # ── Auto-création lignes traçabilité (OUTGOING done) ────────
            if picking.picking_type_code == 'outgoing':
                try:
                    picking._auto_create_logistics_lines()
                except Exception as e:
                    _logger.warning(
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

    # ─────────────────────────────────────────────────────────────────────────
    # CRON — Alerte délai prise en charge livreur (T2 − T1 > 2h)
    # ─────────────────────────────────────────────────────────────────────────
    @api.model
    def cron_check_t2_delay(self):
        """
        Cron horaire : si T1 est set (commande prête) mais T2 absent (livreur
        n'a pas encore confirmé la récupération) depuis plus de 2h → alerte.
        Évite qu'une commande préparée reste en zone expédition sans être prise.
        """
        from datetime import timedelta
        threshold = fields.Datetime.now() - timedelta(hours=2)

        late_pickings = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', '=', 'assigned'),
            ('datetime_t1', '!=', False),
            ('datetime_t1', '<', threshold),
            ('datetime_t2', '=', False),
        ])

        for picking in late_pickings:
            try:
                delay_min = int(
                    (fields.Datetime.now() - picking.datetime_t1).total_seconds() / 60
                )
                picking.message_post(
                    body=_(
                        "<b>⏰ ALERTE — Commande non récupérée par le livreur</b><br/>"
                        "La commande <b>%(name)s</b> est prête en zone expédition "
                        "depuis <b>%(delay)d minutes</b> et n'a pas encore été "
                        "prise en charge.<br/>"
                        "👉 Vérifier si un livreur a été assigné à cette tournée."
                    ) % {'name': picking.name, 'delay': delay_min},
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                )
                picking.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_("⏰ BL en attente de prise en charge — %s") % picking.name,
                    note=_(
                        "La commande %(name)s est prête depuis %(delay)d min. "
                        "Aucun livreur n'a confirmé la récupération. "
                        "Vérifier l'assignation des tournées."
                    ) % {'name': picking.name, 'delay': delay_min},
                )
                _logger.warning(
                    "PARABOX alerte T2: %s en attente depuis %d min", picking.name, delay_min
                )
            except Exception as e:
                _logger.error("PARABOX cron_check_t2_delay picking %s: %s", picking.id, e)
