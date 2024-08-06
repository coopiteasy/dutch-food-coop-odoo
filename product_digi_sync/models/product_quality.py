from odoo import models, fields, api
from .digi_sync_base_model import DigiSyncBaseModel

EXTERNAL_DIGI_ID_START = 100000
class ProductQuality(DigiSyncBaseModel, models.Model):
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
        for record in records:
            record.digi_image_id = record.id + EXTERNAL_DIGI_ID_START
        return records

