from odoo import api, fields, models


class CwaProductQuality(models.Model):
    _name = "cwa.product.quality"
    _description = "Product Quality"
    _order = "source_value"
    _rec_name = "source_value"

    source_value = fields.Char("Source Value", size=64, required=True)
    destination_value = fields.Char("Destination Value", size=64)

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
