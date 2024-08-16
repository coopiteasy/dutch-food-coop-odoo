from odoo import fields, models


class ProductQuality(models.Model):
    _name = "product_food_fields.product_quality"
    _description = "Product Quality"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    image = fields.Image(max_width=1000, max_height=1000)
