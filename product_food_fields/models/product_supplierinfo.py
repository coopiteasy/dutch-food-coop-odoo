from odoo import models, fields


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    ingredients = fields.Text(help="Beschrijving van de ingredienten.")
    usage_tips = fields.Char(help="Usage tips")
    use_by_days = fields.Integer(help="Days until use by date is reached")
    storage_temperature = fields.Integer(help="Storage temperature in Celcius")
