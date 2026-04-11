import json
import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class ParaboxSignController(http.Controller):
    """Routes HTTP pour la signature BL PARABOX."""

    @http.route('/parabox/sign/<string:token>', type='http', auth='public', website=True, csrf=False)
    def sign_page(self, token, **kwargs):
        """
        Page principale de signature.
        Accessible sans login depuis n'importe quel appareil.
        """
        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('token', '=', token)], limit=1
        )
        if not sign_req:
            return request.render('parabox_sign.page_sign_invalid', {
                'message': _("Lien de signature invalide ou expiré.")
            })
        if sign_req.signed:
            return request.render('parabox_sign.page_sign_already_done', {
                'sign_req': sign_req,
            })
        return request.render('parabox_sign.page_sign_form', {
            'sign_req': sign_req,
            'token': token,
            'otp_required': sign_req.mode == 'otp' and not sign_req.otp_verified,
        })

    @http.route('/parabox/sign/verify-otp', type='json', auth='public', csrf=False)
    def verify_otp(self, token, otp, **kwargs):
        """
        Vérifie l'OTP entré par le client.
        Retourne JSON: {success: bool, message: str}
        """
        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('token', '=', token)], limit=1
        )
        if not sign_req:
            return {'success': False, 'message': _("Demande introuvable.")}

        ok, msg = sign_req.verify_otp(otp)
        return {'success': ok, 'message': msg}

    @http.route('/parabox/sign/submit', type='json', auth='public', csrf=False)
    def submit_signature(self, token, signature_b64, otp_verified=False,
                         gps=None, **kwargs):
        """
        Enregistre la signature et génère le PDF.
        Retourne JSON: {success: bool, message: str, pdf_url: str|None}
        """
        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('token', '=', token)], limit=1
        )
        if not sign_req:
            return {'success': False, 'message': _("Demande introuvable.")}
        if sign_req.signed:
            return {'success': False, 'message': _("Ce BL a déjà été signé.")}

        # Récupération IP et User-Agent
        sign_ip = request.httprequest.remote_addr
        sign_ua = request.httprequest.user_agent.string if request.httprequest.user_agent else ''

        # Enlever le préfixe data:image/... si présent
        if signature_b64 and ',' in signature_b64:
            signature_b64 = signature_b64.split(',', 1)[1]

        sign_req.save_signature(
            signature_b64=signature_b64,
            sign_ip=sign_ip,
            sign_user_agent=sign_ua,
            sign_gps=gps or '',
            otp_verified=otp_verified or sign_req.otp_verified,
        )

        pdf_url = None
        if sign_req.pdf_signed:
            pdf_url = f"/parabox/sign/pdf/{token}"

        return {
            'success': True,
            'message': _("BL signé avec succès. Un email de confirmation vous a été envoyé."),
            'pdf_url': pdf_url,
            'signed': True,
        }

    @http.route('/parabox/sign/pdf/<string:token>', type='http', auth='public')
    def download_signed_pdf(self, token, **kwargs):
        """Télécharge le PDF signé."""
        sign_req = request.env['parabox.sign.request'].sudo().search(
            [('token', '=', token), ('signed', '=', True)], limit=1
        )
        if not sign_req or not sign_req.pdf_signed:
            return request.not_found()

        import base64
        pdf_bytes = base64.b64decode(sign_req.pdf_signed)
        filename = sign_req.pdf_filename or f"BL_SIGNE_{token}.pdf"

        return request.make_response(
            pdf_bytes,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
                ('Content-Length', len(pdf_bytes)),
            ]
        )

    @http.route('/parabox/sign/check-integrity', type='json', auth='user', csrf=False)
    def check_integrity(self, sign_request_id, **kwargs):
        """Vérifie l'intégrité du PDF signé (anti-fraude)."""
        sign_req = request.env['parabox.sign.request'].browse(int(sign_request_id))
        if not sign_req.exists():
            return {'success': False, 'message': _("Demande introuvable.")}
        result = sign_req.action_check_pdf_integrity()
        return {'success': True, 'result': result}
