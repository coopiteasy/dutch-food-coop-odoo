import logging

from odoo import api, fields, models

from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

EXTERNAL_DIGI_ID_START = 10000


class ProductOrigin(models.Model):
    _name = "product_digi_sync.product_origin"
    _description = "Product Origin"

    description = fields.Text(
        help="The origin description. Can be a country, region or producer."
    )
    external_digi_id = fields.Integer(
        string="External Digi identifier",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_digi_id_uniq",
            "unique(external_digi_id)",
            "External digi id must be unique.",
        ),
    ]

    @api.model
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            record.external_digi_id = record.id + EXTERNAL_DIGI_ID_START
        return records

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            record.send_to_digi()
        return result

    def send_to_digi(self):
        self.ensure_one()
        self.with_delay().send_to_digi_directly()

    def send_to_digi_directly(self):
        client = self._get_digi_client()
        if client:
            try:
                client.send_product_origin_to_digi(self)
            except Exception as e:
                raise RetryableJobError(str(e), 5) from e

    def _get_digi_client(self):
        digi_client_id = int(
            self.env["ir.config_parameter"].get_param("digi_client_id")
        )
        client = self.env["product_digi_sync.digi_client"].browse(digi_client_id)
        if not client.exists():
            _logger.warning("Digi client requested, but no client was configured.")
            return False
        return client
