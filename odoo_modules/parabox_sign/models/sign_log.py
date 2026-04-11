from odoo import models, fields


class ParaboxSignLog(models.Model):
    """Journal d'audit de toutes les actions de signature."""
    _name = 'parabox.sign.log'
    _description = 'Journal signature PARABOX'
    _order = 'create_date desc'
    _rec_name = 'action'

    sign_request_id = fields.Many2one(
        'parabox.sign.request',
        string='Demande de signature',
        required=True,
        ondelete='cascade',
        index=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='BL',
        related='sign_request_id.picking_id',
        store=True,
        readonly=True,
    )
    action = fields.Selection([
        ('otp_sent', 'OTP envoye'),
        ('otp_ok', 'OTP valide'),
        ('otp_fail', 'OTP echoue'),
        ('otp_expired', 'OTP expire'),
        ('signed', 'BL signe'),
        ('signed_degrade', 'Signe sans OTP'),
        ('pdf_generated', 'PDF genere'),
        ('integrity_ok', 'Integrite OK'),
        ('integrity_fail', 'Fraude detectee'),
    ], string='Action', required=True)
    ip_address = fields.Char(string='Adresse IP')
    user_agent = fields.Char(string='User-Agent')
    detail = fields.Text(string='Détail')
    create_date = fields.Datetime(string='Date', readonly=True)
