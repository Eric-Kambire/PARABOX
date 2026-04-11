from odoo import models, api, fields
from datetime import date, timedelta
from calendar import monthrange
import logging

_logger = logging.getLogger(__name__)


class ParaboxDashboardData(models.TransientModel):
    """Modèle transient — calcule tous les KPIs du dashboard Direction PARABOX."""
    _name = 'parabox.dashboard.data'
    _description = 'Données Dashboard PARABOX'

    @api.model
    def get_kpis(self):
        """
        Point d'entrée unique appelé par le JS via RPC toutes les 60 secondes.
        Retourne finance + logistique + charts + alertes + timestamp.
        """
        today = date.today()
        first_day_month = today.replace(day=1)
        last_month_end = first_day_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        finance = self._get_finance_kpis(today, first_day_month, last_month_start, last_month_end)
        logistique = self._get_logistique_kpis(today)
        charts = self._get_chart_data(today)
        alertes = self._build_alertes(finance, logistique)

        return {
            'finance': finance,
            'logistique': logistique,
            'charts': charts,
            'alertes': alertes,
            'timestamp': fields.Datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Finance KPIs
    # ──────────────────────────────────────────────────────────────────────────

    def _get_finance_kpis(self, today, first_day_month, last_month_start, last_month_end):
        env = self.env

        # 1. CA du mois en cours
        ca_mois_moves = env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', first_day_month.strftime('%Y-%m-%d')),
            ('invoice_date', '<=', today.strftime('%Y-%m-%d')),
        ])
        ca_mois_total = sum(ca_mois_moves.mapped('amount_untaxed'))

        ca_last_moves = env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', last_month_start.strftime('%Y-%m-%d')),
            ('invoice_date', '<=', last_month_end.strftime('%Y-%m-%d')),
        ])
        ca_last_total = sum(ca_last_moves.mapped('amount_untaxed'))
        ca_evolution = round(((ca_mois_total - ca_last_total) / ca_last_total * 100), 1) if ca_last_total else 0.0

        # 2. Encours clients
        invoices_open = env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'reversed']),
        ])
        encours_total = sum(invoices_open.mapped('amount_residual'))

        # 3. DSO (Days Sales Outstanding) = Encours / (CA 90j / 90)
        date_90j = today - timedelta(days=90)
        ca_90j_moves = env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', date_90j.strftime('%Y-%m-%d')),
        ])
        ca_90j_total = sum(ca_90j_moves.mapped('amount_untaxed'))
        dso = round((encours_total / ca_90j_total * 90), 1) if ca_90j_total else 0.0

        # 4. Litiges ouverts — guard: parabox_litige peut ne pas être installé
        if 'parabox.litige' in self.env.registry:
            try:
                litiges_open = env['parabox.litige'].search_read(
                    [('stage_id.is_closed', '=', False)],
                    ['montant_litige']
                )
                montant_litiges = sum(l['montant_litige'] for l in litiges_open if l.get('montant_litige'))
                nb_litiges = len(litiges_open)
            except Exception:
                montant_litiges = 0.0
                nb_litiges = 0
        else:
            montant_litiges = 0.0
            nb_litiges = 0

        # 5. Factures en retard
        factures_retard = env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ['paid', 'reversed']),
            ('invoice_date_due', '<', today.strftime('%Y-%m-%d')),
        ])
        montant_retard = sum(factures_retard.mapped('amount_residual'))
        nb_retard = len(factures_retard)

        return {
            'ca_mois': {
                'value': round(ca_mois_total, 2),
                'evolution': ca_evolution,
                'label': 'CA Mois en cours',
            },
            'encours': {
                'value': round(encours_total, 2),
                'nb': len(invoices_open),
                'label': 'Encours clients',
                'alert': encours_total > 500000,
            },
            'dso': {
                'value': dso,
                'label': 'DSO (jours)',
                'alert': dso > 45,
            },
            'litiges': {
                'value': round(montant_litiges, 2),
                'nb': nb_litiges,
                'label': 'Litiges ouverts',
                'alert': montant_litiges > 50000,
            },
            'retard': {
                'value': round(montant_retard, 2),
                'nb': nb_retard,
                'label': 'Factures en retard',
                'alert': nb_retard > 5,
            },
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Logistique KPIs
    # ──────────────────────────────────────────────────────────────────────────

    def _get_logistique_kpis(self, today):
        env = self.env
        date_30j = today - timedelta(days=30)

        bls_done = env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', '=', 'done'),
            ('date_done', '>=', fields.Datetime.from_string(f'{date_30j} 00:00:00')),
        ])

        # 6. OTIF
        total_bl = len(bls_done)
        on_time = sum(
            1 for bl in bls_done
            if bl.date_done and bl.scheduled_date
            and bl.date_done.date() <= bl.scheduled_date.date()
        )
        otif = round((on_time / total_bl * 100), 1) if total_bl else 100.0

        # 7. Fill Rate — Odoo 17 : champ 'quantity' sur stock.move
        total_lignes = 0
        lignes_ok = 0
        for bl in bls_done:
            for m in bl.move_ids:
                if m.state == 'cancel':
                    continue
                total_lignes += 1
                try:
                    qty = m.quantity
                except AttributeError:
                    qty = getattr(m, 'quantity_done', 0) or 0
                if qty >= m.product_uom_qty:
                    lignes_ok += 1
        fill_rate = round((lignes_ok / total_lignes * 100), 1) if total_lignes else 100.0

        # 8. Ruptures stock
        ruptures = env['product.product'].search([
            ('type', '=', 'product'),
            ('active', '=', True),
            ('qty_available', '<=', 0),
        ])
        nb_ruptures = len(ruptures)
        rupture_names = ruptures.mapped('name')[:5]

        # 9. BL en cours
        bls_en_cours = env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['confirmed', 'assigned', 'waiting']),
        ])
        nb_bl_en_cours = len(bls_en_cours)

        # Répartition statuts pour graphique
        nb_confirmes = sum(1 for b in bls_en_cours if b.state == 'confirmed')
        nb_assigned = sum(1 for b in bls_en_cours if b.state == 'assigned')

        # 10. Reliquats
        reliquats = env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['confirmed', 'assigned', 'waiting']),
            ('backorder_id', '!=', False),
        ])
        nb_reliquats = len(reliquats)

        return {
            'otif': {
                'value': otif,
                'label': 'OTIF (%)',
                'alert': otif < 90,
                'target': 95,
                'on_time': on_time,
                'total': total_bl,
            },
            'fill_rate': {
                'value': fill_rate,
                'label': 'Fill Rate (%)',
                'alert': fill_rate < 85,
                'target': 95,
            },
            'ruptures': {
                'value': nb_ruptures,
                'label': 'Ruptures stock',
                'alert': nb_ruptures > 0,
                'produits': rupture_names,
            },
            'bl_en_cours': {
                'value': nb_bl_en_cours,
                'label': 'BL en cours',
                'confirmes': nb_confirmes,
                'assigned': nb_assigned,
            },
            'reliquats': {
                'value': nb_reliquats,
                'label': 'Reliquats ouverts',
                'alert': nb_reliquats > 3,
            },
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Chart data
    # ──────────────────────────────────────────────────────────────────────────

    def _get_chart_data(self, today):
        env = self.env

        # ── Graphique 1 : CA 6 derniers mois ──
        ca_by_month = []
        labels_months = []
        for i in range(5, -1, -1):
            # Calcul exact du 1er et dernier jour du mois
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            _, last_day = monthrange(year, month)
            start = date(year, month, 1)
            end = date(year, month, last_day)
            moves = env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', end.strftime('%Y-%m-%d')),
            ])
            ca_by_month.append(round(sum(moves.mapped('amount_untaxed')), 2))
            labels_months.append(start.strftime('%b %Y'))

        # ── Graphique 2 : Litiges par type — guard: parabox_litige peut ne pas être installé ──
        litige_types = {}
        if 'parabox.litige' in self.env.registry:
            try:
                litiges = env['parabox.litige'].search([('stage_id.is_closed', '=', False)])
                selection = dict(env['parabox.litige']._fields.get('type_litige', {}).selection or [])
                for litige in litiges:
                    t = selection.get(litige.type_litige, litige.type_litige or 'Autre')
                    litige_types[t] = litige_types.get(t, 0) + 1
            except Exception:
                pass

        # ── Graphique 3 : Top 5 clients encours ──
        partners = env['res.partner'].search([('customer_rank', '>', 0)], limit=50)
        partner_encours = []
        for p in partners:
            domain = [
                ('partner_id', 'child_of', p.id),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'not in', ['paid', 'reversed']),
                ('state', '=', 'posted'),
            ]
            encours = sum(env['account.move'].search(domain).mapped('amount_residual'))
            if encours > 0:
                partner_encours.append({'name': p.name[:22], 'encours': round(encours, 2)})
        partner_encours.sort(key=lambda x: x['encours'], reverse=True)
        top5 = partner_encours[:5]

        # ── Graphique 4 : BL statuts 30 derniers jours ──
        bls_30j = env['stock.picking'].search([
            ('picking_type_code', '=', 'outgoing'),
            ('create_date', '>=', fields.Datetime.from_string(
                f'{today - timedelta(days=30)} 00:00:00'
            )),
        ])
        statuts_bl = {
            'Livré': sum(1 for b in bls_30j if b.state == 'done'),
            'En attente': sum(1 for b in bls_30j if b.state == 'confirmed'),
            'Prêt': sum(1 for b in bls_30j if b.state == 'assigned'),
            'Annulé': sum(1 for b in bls_30j if b.state == 'cancel'),
        }
        statuts_bl = {k: v for k, v in statuts_bl.items() if v > 0}

        return {
            'ca_mensuel': {
                'labels': labels_months,
                'data': ca_by_month,
            },
            'litiges_par_type': {
                'labels': list(litige_types.keys()),
                'data': list(litige_types.values()),
            },
            'top5_encours': {
                'labels': [p['name'] for p in top5],
                'data': [p['encours'] for p in top5],
            },
            'statuts_bl': {
                'labels': list(statuts_bl.keys()),
                'data': list(statuts_bl.values()),
            },
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Alertes
    # ──────────────────────────────────────────────────────────────────────────

    def _build_alertes(self, finance, logistique):
        """Construit la liste des alertes actives pour le bandeau top."""
        alertes = []
        f = finance
        lg = logistique

        if f['retard']['alert']:
            alertes.append({
                'level': 'danger',
                'message': f"{f['retard']['nb']} factures en retard -- {self._fmt(f['retard']['value'])} DH",
            })
        if f['dso']['alert']:
            alertes.append({
                'level': 'warning',
                'message': f"DSO eleve : {f['dso']['value']} jours (objectif < 45j)",
            })
        if f['litiges']['alert']:
            alertes.append({
                'level': 'danger',
                'message': f"Litiges : {self._fmt(f['litiges']['value'])} DH ({f['litiges']['nb']} ouverts)",
            })
        if lg['otif']['alert']:
            alertes.append({
                'level': 'danger',
                'message': f"OTIF critique : {lg['otif']['value']}% (cible >= 95%)",
            })
        if lg['ruptures']['alert']:
            alertes.append({
                'level': 'warning',
                'message': f"{lg['ruptures']['value']} produit(s) en rupture de stock",
            })
        if lg['reliquats']['alert']:
            alertes.append({
                'level': 'warning',
                'message': f"{lg['reliquats']['value']} reliquat(s) ouvert(s)",
            })
        return alertes

    @staticmethod
    def _fmt(val):
        if val >= 1_000_000:
            return f"{val/1_000_000:.1f}M"
        if val >= 1_000:
            return f"{val/1_000:.0f}k"
        return f"{val:.0f}"
