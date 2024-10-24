from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ingredients = fields.Text(help="Ingredients in the product")
    ## TODO: GED-11
    origin = fields.Char(help="Land where the product is produced, an ISO 3166 code")
    usage_tips = fields.Char(help="Usage tips")
    use_by_days = fields.Integer(help="Days until use by date is reached")
    best_before_days = fields.Integer(help="Days until best before date is reached")
    storage_temperature = fields.Integer(help="Storage temperature in Celcius")
    ## TODO: GED-13
    product_quality_id = fields.Many2one(
        "product_food_fields.product_quality", string="Product quality"
    )
    product_origin_id = fields.Many2one(
        "product_food_fields.product_origin", string="Product origin"
    )
