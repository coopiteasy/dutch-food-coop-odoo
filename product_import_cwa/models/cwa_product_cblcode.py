from odoo import api, fields, models


class CwaProductCblcode(models.Model):
    _name = "cwa.product.cblcode"
    _description = "Product CBL code"
    _order = "source_value"

    name = fields.Char(related="source_value")
    source_value = fields.Char("CBL Code", size=64, required=True)
    internal_category = fields.Many2one(
        "product.category", "Internal category", required=False
    )
    pos_category = fields.Many2one("pos.category", "POS category", required=False)

    _sql_constraints = [
        (
            "cwa_product_cblcode_unique",
            "unique(source_value)",
            "CBL Code can only have one translation.",
        )
    ]

    @api.model
    def get_translated(self, source):
        return self.search([("source_value", "=ilike", source)], limit=1)
