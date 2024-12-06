from odoo import api, fields, models


class CwaProductQuality(models.Model):
    _name = "cwa.product.quality"
    _description = "Product Quality"
    _order = "source_value"
    _rec_name = "source_value"

    source_value = fields.Char(size=64, required=True)
    destination_value = fields.Char(size=64)
    destination_product_quality_id = fields.Many2one(
        "product_food_fields.product_quality", "Product Quality", required=False
    )

    _sql_constraints = [
        (
            "cwa_product_quality_unique",
            "unique(source_value)",
            "A quality can only have one translation.",
        )
    ]

    @api.model
    def get_translated(self, source):
        return self.search([("source_value", "=ilike", source)], limit=1)

    @api.model
    def get_translated_product_quality(self, source):
        translation = self.get_translated(source)
        if translation:
            return translation.destination_product_quality_id
