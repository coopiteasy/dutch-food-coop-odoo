from odoo import api, fields, models

FIELDS_TO_COMPARE = ("ingredients",)


class CwaImportProductChange(models.Model):
    _name = "cwa.import.product.change"
    _description = "CWA Import Product Change"

    state = fields.Selection(
        [
            ("new", "New"),
            ("processed", "Processed"),
        ],
        default="new",
        required=True,
    )
    affected_product_id = fields.Many2one(
        "product.template", string="Affected Product", required=True,
        ondelete="cascade"
    )
    source_cwa_product_id = fields.Many2one(
        "cwa.product", string="Source cwa product", required=True,
        ondelete="cascade"
    )
    current_consumer_price = fields.Float(required=True)
    new_consumer_price = fields.Float(required=True)
    product_supplierinfo_id = fields.Many2one(
        "product.supplierinfo",
        compute="_compute_product_supplierinfo",
        search="_search_product_supplierinfo",
        stored=False,
    )

    changed_fields = fields.Char(compute="_compute_changed_fields", store=False)
    product_supplierinfo_ingredients = fields.Text(
        related="product_supplierinfo_id.ingredients"
    )
    affected_product_id_ingredients = fields.Text(
        related="affected_product_id.ingredients"
    )
    affected_product_id_list_price = fields.Float(
        string="Current Price",
        compute="_compute_affected_product_id_list_price",
        inverse="_inverse_set_affected_product_id_list_price",
        store=True,
    )
    product_supplierinfo_list_price = fields.Float(
        related="product_supplierinfo_id.consumentenprijs"
    )
    product_supplierinfo_cost_price = fields.Float(
        related="product_supplierinfo_id.inkoopprijs"
    )
    product_supplierinfo_supplier = fields.Many2one(
        related="product_supplierinfo_id.partner_id"
    )

    @api.depends("affected_product_id.list_price")
    def _compute_affected_product_id_list_price(self):
        for record in self:
            record.affected_product_id_list_price = (
                record.affected_product_id.list_price
            )

    def _inverse_set_affected_product_id_list_price(self):
        for record in self:
            if record.affected_product_id:
                record.affected_product_id.list_price = (
                    record.affected_product_id_list_price
                )

    @api.depends("source_cwa_product_id")
    def _compute_product_supplierinfo(self):
        for record in self:
            if record.source_cwa_product_id:
                supplier_info = self.env["product.supplierinfo"].search(
                    [("unique_id", "=", record.source_cwa_product_id.unique_id)],
                    limit=1,
                )
                record.product_supplierinfo_id = (
                    supplier_info.id if supplier_info else False
                )
            else:
                record.product_supplierinfo_id = False

    def _search_product_supplierinfo(self, operator, value):
        product_ids = []  # List to accumulate product IDs matching the search criteria

        if self.source_cwa_product_id:
            supplier_info = self.env["product.supplierinfo"].search(
                [("unique_id", "=", self.source_cwa_product_id.unique_id)],
                limit=1,
            )
            if supplier_info:
                product_ids = [supplier_info.id]

        # Craft a domain that links back to the desired records
        domain = [("id", "in", product_ids)]
        return domain

    @api.depends("current_consumer_price", "new_consumer_price")
    def _compute_changed_fields(self):
        for record in self:
            new_supplier_info = record.product_supplierinfo_id
            changed = []

            if record.current_consumer_price != record.new_consumer_price:
                changed.append("list_price")

            if new_supplier_info:
                for field in FIELDS_TO_COMPARE:
                    if hasattr(record.affected_product_id, field):
                        supplier_value = getattr(new_supplier_info, field)
                        value = getattr(record.affected_product_id, field)
                        if supplier_value != value:
                            changed.append(field)

            record.changed_fields = ", ".join(changed)

    @api.model
    def open_form_view(self, record_id):
        if isinstance(record_id, list):
            record_id = record_id[0]  # Take the first id if a list is provided
        return {
            "type": "ir.actions.act_window",
            "name": "Open Form",
            "view_mode": "form",
            "res_model": "cwa.import.product.change",
            "res_id": record_id,
            "view_id": self.env.ref(
                "product_import_cwa.view_cwa_import_product_change_form"
            ).id,
            "target": "new",
        }
