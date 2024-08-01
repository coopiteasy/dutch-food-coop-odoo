from odoo import api, fields, models

EXTERNAL_DIGI_ID_START = 10000


class ProductOrigin(models.Model):
    _name = "product_digi_sync.product_origin"
    _description = "Product Origin"

    description = fields.Text(help="The origin description. Can be a country, region or producer.")
    external_digi_id = fields.Integer(
        string="External Digi identifier",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_digi_id_uniq",
            "unique(external_digi_id)",
            "External digi idmust be unique.",
        ),
    ]

    @api.model
    def create(self, vals):
        records = super(ProductOrigin, self).create(vals)
        for record in records:
            record.external_digi_id = record.id + EXTERNAL_DIGI_ID_START
        return records
