import hashlib
import random
import string
import base64
import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ParaboxSignRequest(models.Model):
    """Demande de signature BL — 1 enregistrement par BL à signer."""
    _name = 'parabox.sign.request'
    _description = 'Demande de signature PARABOX'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    # ─── Identification ───────────────────────────────────────────────────────
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
    )
    token = fields.Char(
        string='Token URL',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._generate_token(),
    )

    # ─── Documents ────────────────────────────────────────────────────────────
    picking_id = fields.Many2one(
        'stock.picking',
        string='Bon de Livraison',
        required=True,
        ondelete='cascade',
        index=True,
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='picking_id.partner_id',
        store=True,
        readonly=True,
    )
    livreur_id = fields.Many2one(
        'res.users',
        string='Livreur',
        default=lambda self: self.env.uid,
    )

    # ─── OTP ─────────────────────────────────────────────────────────────────
    otp_hash = fields.Char(
        string='OTP hashé (SHA-256)',
        copy=False,
        readonly=True,
        help="Hash SHA-256 de l'OTP envoyé. Ne jamais afficher l'OTP en clair.",
    )
    otp_expiry = fields.Datetime(
        string='Expiration OTP',
        copy=False,
        readonly=True,
    )
    otp_sent = fields.Boolean(
        string='OTP envoyé',
        default=False,
        readonly=True,
    )
    otp_verified = fields.Boolean(
        string='OTP vérifié',
        default=False,
        readonly=True,
        tracking=True,
    )
    otp_attempts = fields.Integer(
        string='Tentatives OTP',
        default=0,
        readonly=True,
    )

    # ─── Signature ────────────────────────────────────────────────────────────
    signed = fields.Boolean(
        string='Signé',
        default=False,
        readonly=True,
        tracking=True,
    )
    signature_image = fields.Binary(
        string='Image signature BIC',
        attachment=True,
        copy=False,
        readonly=True,
    )
    sign_datetime = fields.Datetime(
        string='Date/heure signature',
        copy=False,
        readonly=True,
    )
    sign_ip = fields.Char(
        string='IP du signataire',
        copy=False,
        readonly=True,
    )
    sign_user_agent = fields.Char(
        string='User-Agent',
        copy=False,
        readonly=True,
    )
    sign_gps = fields.Char(
        string='Coordonnées GPS',
        copy=False,
        readonly=True,
    )

    # ─── PDF signé ────────────────────────────────────────────────────────────
    pdf_hash = fields.Char(
        string='Hash SHA-256 du PDF signé',
        copy=False,
        readonly=True,
        index=True,
    )
    pdf_signed = fields.Binary(
        string='PDF signé',
        attachment=True,
        copy=False,
        readonly=True,
    )
    pdf_filename = fields.Char(
        string='Nom du fichier PDF',
        copy=False,
        readonly=True,
    )

    # ─── Mode et statut ───────────────────────────────────────────────────────
    mode = fields.Selection([
        ('otp', 'OTP + Signature'),
        ('degrade', 'Signature sans OTP'),
    ], string='Mode', default='otp', required=True, tracking=True)
    statut = fields.Selection([
        ('draft', 'En attente'),
        ('otp_sent', 'OTP envoye'),
        ('signed', 'Signe'),
        ('failed', 'Echec'),
    ], string='Statut', default='draft', required=True, tracking=True)

    # ─── Méthodes privées ─────────────────────────────────────────────────────

    @staticmethod
    def _generate_token():
        """Génère un token URL sécurisé (32 caractères aléatoires)."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.SystemRandom().choice(chars) for _ in range(32))

    @staticmethod
    def _hash_otp(otp_plain):
        """Hash SHA-256 d'un OTP en clair."""
        return hashlib.sha256(otp_plain.encode('utf-8')).hexdigest()

    def _log(self, action, ip_address='', user_agent='', detail=''):
        """Crée une entrée dans le journal d'audit parabox.sign.log."""
        self.ensure_one()
        try:
            self.env['parabox.sign.log'].sudo().create({
                'sign_request_id': self.id,
                'action': action,
                'ip_address': ip_address or '',
                'user_agent': user_agent or '',
                'detail': detail or '',
            })
        except Exception as e:
            _logger.error("Erreur écriture sign.log (%s, action=%s): %s", self.name, action, e)

    # ─── CRUD ─────────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('parabox.sign.request') or _('Nouveau')
            if not vals.get('token'):
                vals['token'] = self._generate_token()
        return super().create(vals_list)

    # ─── OTP ─────────────────────────────────────────────────────────────────

    def action_send_otp(self):
        """Génère et envoie l'OTP par email au client."""
        self.ensure_one()
        if not self.client_id.email:
            raise UserError(_("Le client '%s' n'a pas d'adresse email.") % self.client_id.name)

        # Générer OTP 6 chiffres
        otp_plain = ''.join([str(random.SystemRandom().randint(0, 9)) for _ in range(6)])
        otp_hash = self._hash_otp(otp_plain)
        expiry = fields.Datetime.now() + timedelta(minutes=30)

        self.write({
            'otp_hash': otp_hash,
            'otp_expiry': expiry,
            'otp_sent': True,
            'otp_attempts': 0,
            'statut': 'otp_sent',
        })

        # ── Journal d'audit ──────────────────────────────────────────────────
        self._log(
            action='otp_sent',
            detail=_("OTP envoyé à %s pour BL %s") % (self.client_id.email, self.picking_id.name),
        )

        # Construire l'URL de signature
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        sign_url = f"{base_url}/parabox/sign/{self.token}"

        # Envoyer l'email
        mail_template = self.env.ref('parabox_sign.email_template_otp', raise_if_not_found=False)
        if mail_template:
            mail_template.with_context(otp_plain=otp_plain, sign_url=sign_url).send_mail(self.id, force_send=True)
        else:
            # Fallback si pas de template
            self.env['mail.mail'].create({
                'subject': _("Code de validation livraison PARABOX — %s") % self.picking_id.name,
                'body_html': _("""
                    <p>Bonjour <strong>%(client)s</strong>,</p>
                    <p>Votre livreur <strong>%(livreur)s</strong> s'apprête à vous remettre
                    le bon de livraison <strong>%(bl)s</strong>.</p>
                    <p>Votre code de validation : <strong style="font-size:24px;color:#e74c3c;">%(otp)s</strong></p>
                    <p>Ce code est valable <strong>30 minutes</strong>.</p>
                    <p>Page de signature : <a href="%(url)s">%(url)s</a></p>
                    <p><em>PARABOX — Ne communiquez ce code qu'au livreur en face de vous.</em></p>
                """) % {
                    'client': self.client_id.name,
                    'livreur': self.livreur_id.name,
                    'bl': self.picking_id.name,
                    'otp': otp_plain,
                    'url': sign_url,
                },
                'email_to': self.client_id.email,
                'auto_delete': True,
            }).send()

        _logger.info("OTP envoyé à %s pour BL %s", self.client_id.email, self.picking_id.name)
        return True

    def verify_otp(self, otp_input, ip_address='', user_agent=''):
        """
        Vérifie l'OTP saisi. Retourne (True, msg) ou (False, msg).
        Écrit systématiquement dans parabox.sign.log.
        """
        self.ensure_one()

        # Limite tentatives
        if self.otp_attempts >= 5:
            self._log(
                action='otp_fail',
                ip_address=ip_address,
                user_agent=user_agent,
                detail=_("Trop de tentatives — OTP bloqué pour %s") % self.picking_id.name,
            )
            return False, _("Trop de tentatives incorrectes. Demandez un nouvel OTP.")

        # Vérification expiration
        if fields.Datetime.now() > self.otp_expiry:
            self._log(
                action='otp_expired',
                ip_address=ip_address,
                user_agent=user_agent,
                detail=_("OTP expiré pour %s") % self.picking_id.name,
            )
            return False, _("L'OTP a expiré. Demandez un nouvel OTP.")

        # Vérification hash
        otp_hash = self._hash_otp(str(otp_input).strip())
        if otp_hash != self.otp_hash:
            self.sudo().write({'otp_attempts': self.otp_attempts + 1})
            remaining = 5 - self.otp_attempts - 1
            self._log(
                action='otp_fail',
                ip_address=ip_address,
                user_agent=user_agent,
                detail=_("OTP incorrect pour %s — tentative %d/5") % (self.picking_id.name, self.otp_attempts),
            )
            return False, _("OTP incorrect. %d tentative(s) restante(s).") % max(0, remaining)

        # ── Succès ───────────────────────────────────────────────────────────
        self.sudo().write({'otp_verified': True})
        self._log(
            action='otp_ok',
            ip_address=ip_address,
            user_agent=user_agent,
            detail=_("OTP validé avec succès pour %s") % self.picking_id.name,
        )
        return True, _("OTP validé avec succès.")

    # ─── Signature ────────────────────────────────────────────────────────────

    def save_signature(self, signature_b64, sign_ip=None, sign_user_agent=None, sign_gps=None, otp_verified=False):
        """
        Enregistre la signature et déclenche la chaîne automatique :
        1. Sauvegarde signature + génération PDF
        2. T3 : timestamp livraison confirmée sur stock.picking
        3. Auto-validation PBX/OUT → DONE
        4. Auto-facturation sur livré réel (si SO configuré 'livraison')
        """
        self.ensure_one()

        now = fields.Datetime.now()
        mode = 'otp' if otp_verified else 'degrade'
        self.sudo().write({
            'signed': True,
            'signature_image': signature_b64,
            'sign_datetime': now,
            'sign_ip': sign_ip or '',
            'sign_user_agent': sign_user_agent or '',
            'sign_gps': sign_gps or '',
            'mode': mode,
            'statut': 'signed',
        })

        # ── Journal d'audit — signature ──────────────────────────────────────
        action_log = 'signed' if mode == 'otp' else 'signed_degrade'
        self._log(
            action=action_log,
            ip_address=sign_ip or '',
            user_agent=sign_user_agent or '',
            detail=_("BL %s signé par %s (mode: %s, GPS: %s)") % (
                self.picking_id.name,
                self.client_id.name,
                mode,
                sign_gps or 'N/A',
            ),
        )

        # Générer le PDF signé
        pdf_ok = False
        try:
            self._generate_signed_pdf()
            pdf_ok = True
        except Exception as e:
            _logger.error("Erreur génération PDF signé: %s", e)

        # ── Journal d'audit — PDF ────────────────────────────────────────────
        if pdf_ok:
            self._log(
                action='pdf_generated',
                detail=_("PDF signé généré — fichier: %s — hash: %s") % (
                    self.pdf_filename or '',
                    (self.pdf_hash or '')[:16] + '...' if self.pdf_hash else '',
                ),
            )

        # Alerte ADV en mode dégradé
        if mode == 'degrade':
            self._alert_adv_degrade()

        # ── T3 : timestamp livraison confirmée (OTP validé) ──────────────────
        if self.picking_id:
            try:
                self.picking_id.sudo().write({'datetime_t3': now})
                _logger.info("PARABOX T3: BL %s livraison confirmée [%s]", self.picking_id.name, now)
            except Exception as e:
                _logger.warning("PARABOX: erreur set T3 sur %s: %s", self.picking_id.name, e)

        # ── Auto-validation PBX/OUT → DONE ───────────────────────────────────
        if self.picking_id and self.picking_id.state not in ('done', 'cancel'):
            try:
                ctx = {
                    'button_validate_picking_ids': [self.picking_id.id],
                    'mail_notrack': True,
                    'tracking_disable': True,
                }
                result = self.picking_id.sudo().with_context(**ctx).button_validate()
                # Gestion du wizard backorder si nécessaire
                if isinstance(result, dict) and result.get('res_model') == 'stock.backorder.confirmation':
                    wiz = self.env['stock.backorder.confirmation'].sudo().with_context(**ctx).create({
                        'pick_ids': [(4, self.picking_id.id)],
                        'show_transfers': False,
                    })
                    wiz.sudo().with_context(**ctx).process()
                _logger.info("PARABOX: PBX/OUT %s → DONE automatiquement après signature", self.picking_id.name)
            except Exception as e:
                _logger.error("PARABOX: erreur auto-validation OUT %s: %s", self.picking_id.name, e)

        # ── Auto-facturation sur livré réel ───────────────────────────────────
        if self.picking_id:
            sale = getattr(self.picking_id, 'sale_id', False)
            if sale and sale.exists():
                try:
                    invoice_status = getattr(sale, 'invoice_status', None)
                    if invoice_status == 'to invoice':
                        invoices = sale._create_invoices()
                        for inv in invoices:
                            try:
                                inv.action_post()
                            except Exception as e_post:
                                _logger.warning(
                                    "PARABOX: erreur confirmation facture %s: %s", inv.name, e_post
                                )
                        _logger.info(
                            "PARABOX: %d facture(s) créée(s) et confirmée(s) pour SO %s",
                            len(invoices), sale.name
                        )
                        self._log(
                            action='invoice_created',
                            detail=_("Facture auto créée après livraison BL %s") % self.picking_id.name,
                        )
                except Exception as e:
                    _logger.error("PARABOX: erreur auto-facturation SO %s: %s", sale.name, e)

        _logger.info("BL %s signé par %s (mode: %s)", self.picking_id.name, self.client_id.name, mode)
        return True

    # ─── PDF ─────────────────────────────────────────────────────────────────

    def _generate_signed_pdf(self):
        """Génère le PDF BL avec la signature incrustée (via reportlab)."""
        try:
            import io
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.utils import ImageReader

            buffer = io.BytesIO()
            c = rl_canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            # En-tête
            c.setFont("Helvetica-Bold", 16)
            c.drawString(2 * cm, height - 2 * cm, "BON DE LIVRAISON PARABOX — SIGNÉ")

            c.setFont("Helvetica", 11)
            c.drawString(2 * cm, height - 3 * cm, f"BL : {self.picking_id.name}")
            c.drawString(2 * cm, height - 3.7 * cm, f"Client : {self.client_id.name}")
            c.drawString(2 * cm, height - 4.4 * cm, f"Livreur : {self.livreur_id.name}")
            c.drawString(2 * cm, height - 5.1 * cm,
                         f"Date signature : {self.sign_datetime.strftime('%d/%m/%Y %H:%M:%S') if self.sign_datetime else '-'}")
            c.drawString(2 * cm, height - 5.8 * cm, f"Mode : {dict(self._fields['mode'].selection).get(self.mode, self.mode)}")
            c.drawString(2 * cm, height - 6.5 * cm, f"IP : {self.sign_ip or '-'}")
            if self.sign_gps:
                c.drawString(2 * cm, height - 7.2 * cm, f"GPS : {self.sign_gps}")

            # Zone signature
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2 * cm, height - 9 * cm, "SIGNATURE DU CLIENT :")

            if self.signature_image:
                sig_data = base64.b64decode(self.signature_image)
                sig_img = ImageReader(io.BytesIO(sig_data))
                c.drawImage(sig_img, 2 * cm, height - 15 * cm, width=10 * cm, height=5 * cm, preserveAspectRatio=True)

            # Ligne de validation
            c.setFont("Helvetica", 9)
            c.drawString(2 * cm, 3 * cm, f"Document généré automatiquement par le système PARABOX.")
            c.drawString(2 * cm, 2.4 * cm, f"Référence signature : {self.name}")
            c.drawString(2 * cm, 1.8 * cm, f"OTP vérifié : {'OUI' if self.otp_verified else 'NON (mode dégradé)'}")

            c.save()

            pdf_bytes = buffer.getvalue()
            pdf_b64 = base64.b64encode(pdf_bytes)
            pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

            self.sudo().write({
                'pdf_signed': pdf_b64,
                'pdf_hash': pdf_hash,
                'pdf_filename': f"BL_SIGNE_{self.picking_id.name}_{self.name}.pdf",
            })
            _logger.info("PDF signé généré — hash: %s", pdf_hash)

        except ImportError:
            _logger.warning("reportlab non installé — PDF non généré. Installer: pip install reportlab")
        except Exception as e:
            _logger.error("Erreur génération PDF: %s", e)
            raise

    # ─── Alertes ─────────────────────────────────────────────────────────────

    def _alert_adv_degrade(self):
        """Alerte l'ADV en cas de signature sans OTP."""
        adv_group = self.env.ref('sales_team.group_sale_manager', raise_if_not_found=False)
        if adv_group:
            for user in adv_group.users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=_("ALERTE Signature sans OTP — BL %s") % self.picking_id.name,
                    note=_("Le BL %s pour %s a été signé en MODE DÉGRADÉ (sans OTP).\nVérifier la livraison.")
                    % (self.picking_id.name, self.client_id.name),
                )

    # ─── Intégrité PDF ───────────────────────────────────────────────────────

    def action_check_pdf_integrity(self):
        """Vérifie que le PDF n'a pas été modifié (hash SHA-256)."""
        self.ensure_one()
        if not self.pdf_signed or not self.pdf_hash:
            raise UserError(_("Pas de PDF signé à vérifier."))
        pdf_bytes = base64.b64decode(self.pdf_signed)
        current_hash = hashlib.sha256(pdf_bytes).hexdigest()

        if current_hash == self.pdf_hash:
            self._log(
                action='integrity_ok',
                detail=_("Intégrité vérifiée — hash: %s") % current_hash[:16] + '...',
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Integrite verifiee'),
                    'message': _("Le PDF n'a pas été modifié. Hash : %s") % current_hash[:16] + '...',
                    'type': 'success',
                }
            }
        else:
            self._log(
                action='integrity_fail',
                detail=_("FRAUDE DETECTEE — hash attendu: %s... — hash actuel: %s...") % (
                    self.pdf_hash[:16], current_hash[:16]),
            )
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('FRAUDE DETECTEE'),
                    'message': _("Le PDF a été modifié ! Hash attendu : %s... Hash actuel : %s...") % (
                        self.pdf_hash[:16], current_hash[:16]),
                    'type': 'danger',
                    'sticky': True,
                }
            }
