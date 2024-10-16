from odoo import models, fields, api

FIELDS_TO_COMPARE = (
    "ingredients",
)


class CwaImportProductChange(models.Model):
    _name = 'cwa.import.product.change'
    _description = 'CWA Import Product Change'

    state = fields.Selection([
        ('new', 'New'),
        ('processed', 'Processed'),
    ], string="State", default='new', required=True)
    affected_product_id = fields.Many2one('product.template', string="Affected Product", required=True)
    source_cwa_product_id = fields.Many2one('cwa.product', string="Source cwa product", required=True)
    current_consumer_price = fields.Float(string="Current Consumer Price", required=True)
    new_consumer_price = fields.Float(string="New Consumer Price", required=True)
    product_supplierinfo_id = fields.Many2one('product.supplierinfo', string="Product Supplierinfo",
                                              compute='_compute_product_supplierinfo', stored=False)

    changed_fields = fields.Char(string="Changed Fields", compute='_compute_changed_fields', store=False)

    @api.depends('source_cwa_product_id')
    def _compute_product_supplierinfo(self):
        for record in self:
            if record.source_cwa_product_id:
                # Replace 'unique_id' with the actual unique_id field of source_cwa_product_id if it's something else.
                supplier_info = self.env['product.supplierinfo'].search(
                    [('unique_id', '=', record.source_cwa_product_id.unique_id)], limit=1)
                record.product_supplierinfo_id = supplier_info.id if supplier_info else False
            else:
                record.product_supplierinfo_id = False


    @api.depends('current_consumer_price', 'new_consumer_price')
    def _compute_changed_fields(self):
        for record in self:

            new_supplier_info = record.product_supplierinfo_id
            changed = []

            if record.current_consumer_price != record.new_consumer_price:
                changed.append('list_price')

            if new_supplier_info:
                for field in FIELDS_TO_COMPARE:
                    if hasattr(record.affected_product_id, field):
                        supplier_value = getattr(new_supplier_info, field)
                        value = getattr(record.affected_product_id, field)
                        if supplier_value != value:
                            changed.append(field)

            record.changed_fields = ', '.join(changed)
