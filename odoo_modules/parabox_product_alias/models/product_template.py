from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    alias_ids = fields.One2many(
        'parabox.product.alias',
        'product_id',
        string='Alias / Codes de référence',
    )
