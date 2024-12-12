from odoo import fields, models


class CwaProductOriginTranslationWizard(models.TransientModel):
    _name = "cwa.product.origin.translation.wizard"
    _description = "Cwa Product Origin Translation Wizard"

    country_code = fields.Char(
        "The ISO 3166 country code",
        default=lambda self: self.env.context.get("default_country_code"),
    )
    name = fields.Text(help="The origin name. Can be a country, region or producer.")

    def action_create_product_origin_translation(self):
        self.ensure_one()
        product_origin_vals = {
            "country_code": self.country_code,
            "name": self.name,
        }
        self.env["product_food_fields.product_origin"].create(product_origin_vals)
