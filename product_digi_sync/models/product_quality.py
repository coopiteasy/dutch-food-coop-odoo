from odoo import models, fields, api
from odoo.addons.queue_job.exception import RetryableJobError
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
        for product_quality in records:
            if not product_quality.digi_image_id:
                product_quality.digi_image_id = product_quality.id + EXTERNAL_DIGI_ID_START
            product_quality.send_image()
        return records

    def write(self, vals):
        result = super().write(vals)
        for product_quality in self:
            product_quality.send_image()
        return result

    def send_image(self):
        if self.image:
            self.send_to_digi()

    def send_to_digi_directly(self):
        client = self._get_digi_client()
        if client:
            try:
                client.send_product_quality_image_to_digi(self)
            except Exception as e:
                raise RetryableJobError(str(e), 5) from e




