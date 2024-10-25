from odoo import api, fields, models

EXTERNAL_DIGI_ID_START = 100000


class ProductQuality(models.Model):
    _inherit = "product_food_fields.product_quality"

    digi_image_id = fields.Integer(
        string="External digi id for the image", readonly=True
    )

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
        self.update_product_quality_digi_id(records)
        return records


    def write(self, vals):
        res = super().write(vals)
        self.update_product_quality_digi_id(self)
        return res

    @staticmethod
    def update_product_quality_digi_id(records):
        for product_quality in records:
            if not product_quality.digi_image_id:
                product_quality.digi_image_id = (
                    product_quality.id + EXTERNAL_DIGI_ID_START
                )
