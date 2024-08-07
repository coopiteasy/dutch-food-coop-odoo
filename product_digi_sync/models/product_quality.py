from odoo import models, fields, api

EXTERNAL_DIGI_ID_START = 100000
class ProductQuality(models.Model):
    _inherit = "product_food_fields.product_quality"

    digi_image_id = fields.Integer(string="External digi image id", readonly=True)

    _sql_constraints = [
        (
            "digi_image_id_uniq",
            "unique(digi_image_id)",
            "Digi image id must be unique.",
        ),
    ]

    @api.model
    def create(self, vals):
        records = super().create(vals)
        for product_quality in records:
            if not product_quality.digi_image_id:
                product_quality.digi_image_id = product_quality.id + EXTERNAL_DIGI_ID_START
        return records


