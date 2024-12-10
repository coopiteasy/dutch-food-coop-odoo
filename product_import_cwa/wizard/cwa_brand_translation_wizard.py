from odoo import fields, models


class CwaBrandTranslationWizard(models.TransientModel):
    _name = "cwa.brand.translation.wizard"
    _description = "CWA Brand Translation Wizard"

    brand_name = fields.Char(
        required=True,
        default=lambda self: self.env.context.get("default_brand_name"),
    )
    translated_brand = fields.Many2one("product.brand")

    def action_translate_brand(self):
        for this in self:
            values = {
                "source_value": this.brand_name,
                "destination_value": this.translated_brand.id,
            }
            self.env["cwa.product.brands"].create(values)
