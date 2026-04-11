from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ParaboxProductAlias(models.Model):
    """Table de correspondance codes produits multi-canaux."""
    _name = 'parabox.product.alias'
    _description = 'Alias produit PARABOX'
    _rec_name = 'code_parabox'
    _order = 'product_id, fournisseur_id'

    product_id = fields.Many2one(
        'product.template',
        string='Produit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    fournisseur_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
        domain=[('supplier_rank', '>', 0)],
        index=True,
    )
    code_parabox = fields.Char(
        string='Code PARABOX',
        help="Code interne PARABOX (ex: P001, P002...)",
    )
    code_fournisseur = fields.Char(
        string='Code fournisseur',
        help="Code utilisé par le fournisseur dans ses BL et factures.",
    )
    code_revendeur = fields.Char(
        string='Code revendeur',
        help="Code utilisé par le revendeur dans ses commandes.",
    )
    ean = fields.Char(
        string='Code-barres EAN',
        size=13,
        help="Code EAN-13 du produit.",
    )
    actif = fields.Boolean(
        string='Actif',
        default=True,
    )
    note = fields.Text(string='Remarques')

    @api.constrains('ean')
    def _check_ean(self):
        for rec in self:
            if rec.ean and len(rec.ean) not in (8, 13):
                raise ValidationError(_("Le code EAN doit faire 8 ou 13 caractères. Valeur actuelle : '%s'") % rec.ean)

    @api.depends('code_parabox', 'code_fournisseur', 'product_id')
    def _compute_display_name(self):
        for rec in self:
            name = rec.code_parabox or rec.code_fournisseur or str(rec.id)
            if rec.product_id:
                name = f"[{name}] {rec.product_id.name}"
            rec.display_name = name
