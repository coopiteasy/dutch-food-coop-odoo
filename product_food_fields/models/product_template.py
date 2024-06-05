from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ingredients = fields.Text(help="Ingredients in the product")
    quality = fields.Char(help="Quality e.g. organic or biodynamic")
    origin = fields.Char(help="Land where the product is produced, an ISO 3166 code")
    usage_tips = fields.Char(help="Usage tips")
    days_until_expiry = fields.Integer(help="Days until expiration")
    storage_temperature = fields.Float(help="Storage temperature in Celcius")
