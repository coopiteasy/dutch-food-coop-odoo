import logging

from odoo import api, fields, models

class ProductOrigin(models.Model):
    _name = "product_food_fields.product_origin"
    _description = "Product Origin"

    name = fields.Text(help="The origin name. Can be a country, region or producer.")
    country_code = fields.Char("The ISO 3166 country code")
