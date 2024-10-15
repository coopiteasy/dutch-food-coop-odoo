from odoo import models, fields, api

class CwaImportProductChange(models.Model):
    _name = 'cwa.import.product.change'
    _description = 'CWA Import Product Change'

    state = fields.Selection([
        ('new', 'New'),
        ('processed', 'Processed'),
    ], string="State", default='new', required=True)
    affected_product_id = fields.Many2one('product.template', string="Affected Product", required=True)
    current_consumer_price = fields.Float(string="Current Consumer Price", required=True)
    new_consumer_price = fields.Float(string="New Consumer Price", required=True)
