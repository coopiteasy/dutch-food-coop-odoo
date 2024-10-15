from odoo import models, fields


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    ingredients = fields.Text(help="Beschrijving van de ingredienten.")
    usage_tips = fields.Char(help="Usage tips")
