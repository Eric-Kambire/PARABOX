import logging
from datetime import date
import pytz

from odoo import http, fields, _
from odoo.http import request

_logger = logging.getLogger(__name__)

TIMEZONE = 'Africa/Casablanca'

# Logins des utilisateurs livreur PARABOX
# Ajoutez ici chaque nouveau livreur créé
LIVREUR_LOGINS = {
    'livreur@parabox.ma',
    'livreur2@parabox.ma',
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _to_local(dt):
    """Convertit un datetime UTC en heure locale Maroc (UTC+1/+0)."""
    if not dt:
        return None
    try:
        utc = pytz.utc.localize(dt.replace(tzinfo=None))
        local_tz = pytz.timezone(TIMEZONE)
        return utc.astimezone(local_tz)
    except Exception:
        return dt


def _get_base_url():
    """Retourne l'URL de base depuis la requête HTTP — supporte WiFi + partage réseau."""
    return request.httprequest.host_url.rstrip('/')


def _state_label(state):
    return {
        'draft':     'Brouillon',
        'confirmed': 'En attente de stock',
        'assigned':  'Prêt à livrer',
        'done':      'Livré',
        'cancel':    'Annulé',
    }.get(state, state)


def _is_livreur(user=None):
    """Retourne True si l'utilisateur courant est un livreur PARABOX."""
    u = user or request.env.user
    return u.login in LIVREUR_LOGINS


# ──────────────────────────────────────────────────────────────────────────────
# Redirection automatique portail → mobile livreur
# ──────────────────────────────────────────────────────────────────────────────

try:
    from odoo.addons.portal.controllers.portal import CustomerPortal

    class ParaboxPortalHome(CustomerPortal):
        """
        Surcharge du portail client : si l'utilisateur connecté est un livreur
        PARABOX, il est redirigé automatiquement vers l'interface mobile.
        Cela évite d'avoir à taper l'URL manuellement après connexion.
        """

        @http.route('/my', type='http', auth='user', website=True)
        def home(self, **kwargs):
            if _is_livreur():
                return request.redirect('/parabox/mobile/livreur')
            return super().home(**kwargs)

        @http.route('/my/home', type='http', auth='user', website=True)
        def my_home(self, **kwargs):
            if _is_livreur():
                return request.redirect('/parabox/mobile/livreur')
            return super().my_home(**kwargs) if hasattr(super(), 'my_home') else request.redirect('/my')

except ImportError:
    _logger.warning("parabox_mobile: module portal non disponible — redirection auto désactivée.")


# ──────────────────────────────────────────────────────────────────────────────
# Contrôleur principal
# ──────────────────────────────────────────────────────────────────────────────

class ParaboxMobileController(http.Controller):
    """Interface mobile PARABOX — Espace Livreur."""

    # ── 1. Page d'accueil livreur — liste des BL ─────────────────────────
    @http.route('/parabox/mobile/livreur', type='http', auth='user', website=True)
    def livreur_home(self, **kwargs):
        """
        Affiche tous les BL de type 'outgoing' en cours
        (states: confirmed, assigned) + les done du jour pour référence.
        Supporte plusieurs livreurs simultanément.
        Accès réservé aux livreurs.
        """
        # ── Contrôle d'accès : seuls les livreurs peuvent voir cette page ──
        if not _is_livreur():
            return request.redirect('/odoo')

        today = date.today()

        # BL en cours (à traiter)
        # État 'assigned' seulement = le magasinier a validé le PICK
        # et déposé la marchandise en zone expédition. Le livreur
        # ne voit un BL que lorsque la marchandise est physiquement prête.
        domain_pending = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['assigned']),
        ]
        bls_pending = request.env['stock.picking'].sudo().search(
            domain_pending, order='scheduled_date asc', limit=100
        )

        # BL validés aujourd'hui
        domain_done = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', '=', 'done'),
            ('date_done', '>=', str(today)),
        ]
        bls_done = request.env['stock.picking'].sudo().search(
            domain_done, order='date_done desc', limit=20
        )

        def enrich(bl):
            sign_req = request.env['parabox.sign.request'].sudo().search(
                [('picking_id', '=', bl.id)], limit=1, order='create_date desc'
            )
            return {
                'bl': bl,
                'sign_req': sign_req,
                'signed': sign_req.signed if sign_req else False,
                'otp_sent': sign_req.otp_sent if sign_req else False,
                'sign_token': sign_req.token if sign_req else None,
                'scheduled_local': _to_local(bl.scheduled_date),
                'state_label': _state_label(bl.state),
            }

        bls_data = [enrich(bl) for bl in bls_pending]
        bls_done_data = [enrich(bl) for bl in bls_done]

        # ── Compteur "Signés" corrigé ─────────────────────────────────────
        # On compte les sign requests signées aujourd'hui (toutes livraisons)
        total_signed = request.env['parabox.sign.request'].sudo().search_count([
            ('signed', '=', True),
            ('sign_datetime', '>=', str(today)),
        ])

        user = request.env['res.users'].browse(request.env.uid)
        base_url = _get_base_url()

        return request.render('parabox_mobile.page_livreur_home', {
            'bls_data': bls_data,
            'bls_done_data': bls_done_data,
            'user': user,
            'today': today.strftime('%d/%m/%Y'),
            'base_url': base_url,
            'total_pending': len(bls_data),
            'total_signed': total_signed,          # ← nouveau: compteur signé correct
        })

    # ── 2. Détail d'un BL ─────────────────────────────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>', type='http', auth='user', website=True)
    def livreur_bl_detail(self, picking_id, **kwargs):
        """
        Affiche le détail d'un BL : infos client, produits, section signature.
        Gère correctement les BL annulés (affiche un message clair).
        Accès réservé aux livreurs.
        """
        if not _is_livreur():
            return request.redirect('/odoo')

        bl = request.env['stock.picking'].sudo().browse(picking_id)
        if not bl.exists():
            return request.render('parabox_mobile.page_erreur', {
                'message': "Ce bon de livraison n'existe pas.",
                'base_url': _get_base_url(),
            })

        # BL annulé → page dédiée
        if bl.state == 'cancel':
            return request.render('parabox_mobile.page_livreur_bl_detail', {
                'bl': bl,
                'lignes': [],
                'sign_req': None,
                'sign_url': None,
                'picking_id': picking_id,
                'scheduled_local': _to_local(bl.scheduled_date),
                'base_url': _get_base_url(),
                'bl_cancelled': True,
                'state_label': 'Annulé',
            })

        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('picking_id', '=', picking_id)], limit=1, order='create_date desc'
        )

        base_url = _get_base_url()
        sign_url = f"{base_url}/parabox/sign/{sign_req.token}" if sign_req else None
        scheduled_local = _to_local(bl.scheduled_date)

        lignes = []
        active_moves = bl.move_ids.filtered(lambda m: m.state != 'cancel')
        for move in active_moves:
            try:
                lots = [ml.lot_id.name for ml in move.move_line_ids if ml.lot_id]
                qty_done = 0
                if move.move_line_ids:
                    qty_done = int(sum(
                        # Odoo 17 : qty_done renommé en quantity sur stock.move.line
                        getattr(ml, 'quantity', None) or getattr(ml, 'qty_done', 0) or 0
                        for ml in move.move_line_ids
                        if ml.state != 'cancel'
                    ))
                else:
                    qty_done = int(move.quantity or 0)

                lignes.append({
                    'product_name': move.product_id.display_name,
                    'qty_ordered': int(move.product_uom_qty),
                    'qty_done': qty_done,
                    'lots': lots,
                    'uom': move.product_uom.name if move.product_uom else '',
                    'has_lots': bool(lots),
                    'scan_confirmed': move.parabox_scan_confirmed,
                    'move_id': move.id,
                })
            except Exception as e:
                _logger.warning("Erreur traitement move %s: %s", move.id, e)
                lignes.append({
                    'product_name': move.product_id.display_name if move.product_id else '—',
                    'qty_ordered': int(move.product_uom_qty or 0),
                    'qty_done': 0,
                    'lots': [],
                    'uom': '',
                    'has_lots': False,
                    'scan_confirmed': False,
                    'move_id': move.id,
                })

        # ── Suivi scan chargement ──────────────────────────────────────────
        total_moves = len(active_moves)
        scanned_moves = len(active_moves.filtered(lambda m: m.parabox_scan_confirmed))
        all_scanned = (total_moves > 0 and scanned_moves >= total_moves)

        return request.render('parabox_mobile.page_livreur_bl_detail', {
            'bl': bl,
            'lignes': lignes,
            'sign_req': sign_req,
            'sign_url': sign_url,
            'picking_id': picking_id,
            'scheduled_local': scheduled_local,
            'base_url': base_url,
            'bl_cancelled': False,
            'state_label': _state_label(bl.state),
            'all_scanned': all_scanned,
            'scan_count': scanned_moves,
            'total_moves': total_moves,
        })

    # ── 3. Confirmation récupération + envoi OTP ─────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>/send-otp',
                type='json', auth='user', csrf=False)
    def livreur_send_otp(self, picking_id, **kwargs):
        """
        Déclenché quand le livreur clique "Je confirme avoir récupéré la commande".
        1. Vérifie que tous les produits ont été scannés (garde-fou)
        2. Enregistre T2 (timestamp prise en charge livreur)
        3. Envoie l'OTP au client en arrière-plan
        """
        if not _is_livreur():
            return {'success': False, 'message': "Accès non autorisé."}
        bl = request.env['stock.picking'].sudo().browse(picking_id)
        if not bl.exists():
            return {'success': False, 'message': "BL introuvable."}
        if bl.state == 'cancel':
            return {'success': False, 'message': "Ce BL a été annulé — impossible de confirmer."}
        if not bl.partner_id.email:
            return {'success': False,
                    'message': f"Le client '{bl.partner_id.name}' n'a pas d'adresse email."}

        # ── Garde-fou : tous les produits doivent être scannés ────────────
        active_moves = bl.move_ids.filtered(lambda m: m.state != 'cancel')
        if active_moves:
            unscanned = active_moves.filtered(lambda m: not m.parabox_scan_confirmed)
            if unscanned:
                names = ', '.join(unscanned[:3].mapped('product_id.display_name'))
                remaining = len(unscanned)
                return {
                    'success': False,
                    'message': (
                        f"⚠️ Scanner obligatoire avant confirmation.\n"
                        f"{remaining} produit(s) non scanné(s) : {names}"
                    ),
                }

        # ── T2 : enregistrer la prise en charge livreur ───────────────────
        if not bl.datetime_t2:
            try:
                bl.sudo().write({'datetime_t2': fields.Datetime.now()})
                _logger.info("PARABOX T2: BL %s pris en charge par livreur", bl.name)
            except Exception as e:
                _logger.warning("PARABOX: erreur set T2 sur %s: %s", bl.name, e)

        # ── Créer ou récupérer la sign request ────────────────────────────
        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('picking_id', '=', picking_id), ('statut', 'not in', ['signed', 'failed'])],
            limit=1
        )
        if not sign_req:
            sign_req = request.env['parabox.sign.request'].sudo().create({
                'picking_id': picking_id,
                'livreur_id': request.env.uid,
            })

        try:
            sign_req.sudo().action_send_otp()
            base_url = _get_base_url()
            sign_url = f"{base_url}/parabox/sign/{sign_req.token}"
            return {
                'success': True,
                'message': (
                    f"✅ Récupération confirmée. "
                    f"Code envoyé à {bl.partner_id.email} — "
                    f"Demandez au client d'entrer le code qu'il a reçu."
                ),
                'sign_url': sign_url,
                'token': sign_req.token,
            }
        except Exception as e:
            _logger.error("Erreur envoi OTP BL %s: %s", picking_id, e)
            return {'success': False, 'message': str(e)}

    # ── 4. Validation BL depuis mobile ────────────────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>/validate',
                type='json', auth='user', csrf=False)
    def livreur_validate_bl(self, picking_id, **kwargs):
        if not _is_livreur():
            return {'success': False, 'message': "Accès non autorisé."}
        bl = request.env['stock.picking'].sudo().browse(picking_id)
        if not bl.exists():
            return {'success': False, 'message': "BL introuvable."}
        if bl.state == 'done':
            return {'success': True, 'message': "Ce BL a déjà été validé."}
        if bl.state == 'cancel':
            return {'success': False, 'message': "Ce BL a été annulé — validation impossible."}

        try:
            ctx_sudo = {
                'button_validate_picking_ids': [picking_id],
                'mail_notrack': True,
                'tracking_disable': True,
            }
            res = bl.sudo().with_context(**ctx_sudo).button_validate()
            if isinstance(res, dict) and res.get('res_model') == 'stock.backorder.confirmation':
                wiz = request.env['stock.backorder.confirmation'].sudo().with_context(**ctx_sudo).create({
                    'pick_ids': [(4, picking_id)],
                    'show_transfers': False,
                })
                wiz.sudo().with_context(**ctx_sudo).process()
                return {'success': True, 'message': f"BL {bl.name} validé avec backorder créé automatiquement."}
            return {'success': True, 'message': f"BL {bl.name} validé avec succès."}
        except Exception as e:
            _logger.error("Erreur validation BL %s: %s", picking_id, e)
            return {'success': False, 'message': str(e)}

    # ── 5. API JSON — état d'un BL (polling) ─────────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>/status',
                type='json', auth='user', csrf=False)
    def livreur_bl_status(self, picking_id, **kwargs):
        if not _is_livreur():
            return {'exists': False, 'error': 'Accès non autorisé.'}
        bl = request.env['stock.picking'].sudo().browse(picking_id)
        if not bl.exists():
            return {'exists': False}
        return {
            'exists': True,
            'state': bl.state,
            'state_label': _state_label(bl.state),
            'cancelled': bl.state == 'cancel',
            'done': bl.state == 'done',
        }

    # ── 6. API JSON — liste des BL ────────────────────────────────────────
    @http.route('/parabox/mobile/livreur/api/bls', type='json', auth='user', csrf=False)
    def api_get_bls(self, **kwargs):
        if not _is_livreur():
            return {'bls': [], 'count': 0, 'error': 'Accès non autorisé.'}
        bls = request.env['stock.picking'].sudo().search([
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['confirmed', 'assigned']),
        ], order='scheduled_date asc', limit=100)

        result = []
        for bl in bls:
            scheduled_local = _to_local(bl.scheduled_date)
            result.append({
                'id': bl.id,
                'name': bl.name,
                'partner': bl.partner_id.name,
                'partner_email': bl.partner_id.email or '',
                'scheduled_date': scheduled_local.strftime('%d/%m %H:%M') if scheduled_local else '—',
                'state': bl.state,
                'state_label': _state_label(bl.state),
                'nb_lignes': len(bl.move_ids),
            })
        return {'bls': result, 'count': len(result)}

    # ── 7. API JSON — recherche BL par QR code ───────────────────────────
    @http.route('/parabox/mobile/livreur/scan/bl', type='json', auth='user', csrf=False)
    def scan_find_bl(self, code=None, **kwargs):
        if not _is_livreur():
            return {'success': False, 'message': 'Accès non autorisé.'}
        if not code:
            return {'success': False, 'message': 'Code QR vide.'}

        code = code.strip()
        bl = None

        if '/livreur/bl/' in code:
            try:
                part = code.split('/livreur/bl/')[-1]
                picking_id = int(part.split('/')[0].split('?')[0])
                candidate = request.env['stock.picking'].sudo().browse(picking_id)
                if candidate.exists():
                    bl = candidate
            except (ValueError, IndexError):
                pass

        if not bl:
            bl = request.env['stock.picking'].sudo().search(
                [('name', '=', code), ('picking_type_code', '=', 'outgoing')], limit=1
            )
        if not bl:
            bl = request.env['stock.picking'].sudo().search(
                [('origin', '=', code), ('picking_type_code', '=', 'outgoing'),
                 ('state', 'not in', ['done', 'cancel'])], limit=1
            )
        if not bl:
            bl = request.env['stock.picking'].sudo().search(
                [('name', 'ilike', code), ('picking_type_code', '=', 'outgoing'),
                 ('state', 'not in', ['done', 'cancel'])], limit=1
            )

        if not bl:
            return {'success': False, 'message': f"Aucun BL trouvé pour : {code}"}

        return {
            'success': True,
            'picking_id': bl.id,
            'name': bl.name,
            'partner': bl.partner_id.name,
            'state': bl.state,
            'state_label': _state_label(bl.state),
            'redirect': f"/parabox/mobile/livreur/bl/{bl.id}",
        }

    # ── 8. API JSON — recherche produit par code-barres ─────────────────
    @http.route('/parabox/mobile/livreur/scan/product', type='json', auth='user', csrf=False)
    def scan_find_product(self, barcode=None, picking_id=None, **kwargs):
        if not _is_livreur():
            return {'success': False, 'message': 'Accès non autorisé.'}
        if not barcode:
            return {'success': False, 'message': 'Code-barres vide.'}

        barcode = barcode.strip()

        product = request.env['product.product'].sudo().search(
            [('barcode', '=', barcode)], limit=1
        )
        if not product:
            product = request.env['product.product'].sudo().search(
                [('default_code', '=', barcode)], limit=1
            )
        if not product:
            # Recherche dans les alias PARABOX (code_parabox, code_fournisseur,
            # code_revendeur ou EAN)
            alias = request.env['parabox.product.alias'].sudo().search(
                ['|', '|', '|',
                 ('code_parabox', '=', barcode),
                 ('code_fournisseur', '=', barcode),
                 ('code_revendeur', '=', barcode),
                 ('ean', '=', barcode)],
                limit=1
            )
            if alias:
                product = alias.product_id

        if not product:
            return {'success': False, 'message': f"Produit introuvable : {barcode}"}

        result = {
            'success': True,
            'product_id': product.id,
            'name': product.display_name,
            'barcode': product.barcode or '',
            'ref': product.default_code or '',
            'in_bl': False,
            'qty_ordered': 0,
            'move_id': None,
        }

        if picking_id:
            try:
                bl = request.env['stock.picking'].sudo().browse(int(picking_id))
                if bl.exists():
                    for move in bl.move_ids:
                        if move.product_id.id == product.id and move.state != 'cancel':
                            result['in_bl'] = True
                            result['qty_ordered'] = int(move.product_uom_qty)
                            result['move_id'] = move.id
                            # ── Confirmation scan auto (produit trouvé dans le BL) ──
                            if not move.parabox_scan_confirmed:
                                move.sudo().write({
                                    'parabox_scan_confirmed': True,
                                    'parabox_scan_datetime': fields.Datetime.now(),
                                })
                                _logger.info(
                                    "PARABOX scan: produit %s confirmé sur BL %s",
                                    product.display_name, bl.name
                                )
                            result['scan_confirmed'] = True
                            break
            except Exception as e:
                _logger.warning("Erreur scan confirm move: %s", e)

        return result
