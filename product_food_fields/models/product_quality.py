from odoo import fields, models


class ProductQuality(models.Model):
    _name = "product_food_fields.product_quality"
    _description = "Product Quality"

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    image = fields.Image(string="Image", max_width=1000, max_height=1000)
