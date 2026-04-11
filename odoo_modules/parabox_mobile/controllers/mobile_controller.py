import logging
from datetime import date
import pytz

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

TIMEZONE = 'Africa/Casablanca'

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
        """
        today = date.today()

        # BL en cours (à traiter)
        domain_pending = [
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['confirmed', 'assigned']),
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

        user = request.env['res.users'].browse(request.env.uid)
        base_url = _get_base_url()

        return request.render('parabox_mobile.page_livreur_home', {
            'bls_data': bls_data,
            'bls_done_data': bls_done_data,
            'user': user,
            'today': today.strftime('%d/%m/%Y'),
            'base_url': base_url,
            'total_pending': len(bls_data),
        })

    # ── 2. Détail d'un BL ─────────────────────────────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>', type='http', auth='user', website=True)
    def livreur_bl_detail(self, picking_id, **kwargs):
        """
        Affiche le détail d'un BL : infos client, produits, section signature.
        Gère correctement les BL annulés (affiche un message clair).
        """
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

        # Lignes produits — compatible Odoo 17
        # Odoo 17 : stock.move n'a plus quantity_done, c'est 'quantity'
        # On calcule qty_done depuis move_line_ids pour fiabilité
        lignes = []
        for move in bl.move_ids:
            if move.state == 'cancel':
                continue
            try:
                lots = [ml.lot_id.name for ml in move.move_line_ids if ml.lot_id]
                # Odoo 17 : qty_done sur move_line, quantity sur move
                qty_done = 0
                if move.move_line_ids:
                    qty_done = int(sum(
                        ml.qty_done for ml in move.move_line_ids
                        if ml.state != 'cancel'
                    ))
                else:
                    # Fallback : champ quantity du move (Odoo 17)
                    qty_done = int(move.quantity or 0)

                lignes.append({
                    'product_name': move.product_id.display_name,
                    'qty_ordered': int(move.product_uom_qty),
                    'qty_done': qty_done,
                    'lots': lots,
                    'uom': move.product_uom.name if move.product_uom else '',
                    'has_lots': bool(lots),
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
                })

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
        })

    # ── 3. Envoi OTP ──────────────────────────────────────────────────────
    @http.route('/parabox/mobile/livreur/bl/<int:picking_id>/send-otp',
                type='json', auth='user', csrf=False)
    def livreur_send_otp(self, picking_id, **kwargs):
        bl = request.env['stock.picking'].sudo().browse(picking_id)
        if not bl.exists():
            return {'success': False, 'message': "BL introuvable."}
        if bl.state == 'cancel':
            return {'success': False, 'message': "Ce BL a été annulé — impossible d'envoyer un OTP."}
        if not bl.partner_id.email:
            return {'success': False,
                    'message': f"Le client '{bl.partner_id.name}' n'a pas d'adresse email."}

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
                'message': f"OTP envoyé à {bl.partner_id.email}",
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
            # Odoo retourne un wizard backorder si livraison partielle
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
        """Retourne l'état actuel d'un BL — utile pour détecter annulation en temps réel."""
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
        """Trouve un BL depuis un QR code (nom BL, URL, référence origine)."""
        if not code:
            return {'success': False, 'message': 'Code QR vide.'}

        code = code.strip()
        bl = None

        # Cas 1 : URL complète → extraire l'ID
        if '/livreur/bl/' in code:
            try:
                part = code.split('/livreur/bl/')[-1]
                picking_id = int(part.split('/')[0].split('?')[0])
                candidate = request.env['stock.picking'].sudo().browse(picking_id)
                if candidate.exists():
                    bl = candidate
            except (ValueError, IndexError):
                pass

        # Cas 2 : Nom exact du BL (ex: PBX/OUT/00001)
        if not bl:
            bl = request.env['stock.picking'].sudo().search(
                [('name', '=', code), ('picking_type_code', '=', 'outgoing')], limit=1
            )

        # Cas 3 : Référence d'origine (commande client)
        if not bl:
            bl = request.env['stock.picking'].sudo().search(
                [('origin', '=', code), ('picking_type_code', '=', 'outgoing'),
                 ('state', 'not in', ['done', 'cancel'])], limit=1
            )

        # Cas 4 : Recherche partielle sur le nom
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
        """
        Cherche un produit par code-barres (EAN13/EAN8/Code128/réf interne).
        Si picking_id fourni, vérifie si le produit est dans ce BL.
        """
        if not barcode:
            return {'success': False, 'message': 'Code-barres vide.'}

        barcode = barcode.strip()

        # Recherche par barcode Odoo
        product = request.env['product.product'].sudo().search(
            [('barcode', '=', barcode)], limit=1
        )
        # Fallback : référence interne
        if not product:
            product = request.env['product.product'].sudo().search(
                [('default_code', '=', barcode)], limit=1
            )
        # Fallback : recherche dans l'alias PARABOX
        if not product:
            alias = request.env['parabox.product.alias'].sudo().search(
                [('alias_name', '=', barcode)], limit=1
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

        # Vérifier présence dans le BL
        if picking_id:
            try:
                bl = request.env['stock.picking'].sudo().browse(int(picking_id))
                if bl.exists():
                    for move in bl.move_ids:
                        if move.product_id.id == product.id and move.state != 'cancel':
                            result['in_bl'] = True
                            result['qty_ordered'] = int(move.product_uom_qty)
                            result['move_id'] = move.id
                            break
            except Exception:
                pass

        return result
