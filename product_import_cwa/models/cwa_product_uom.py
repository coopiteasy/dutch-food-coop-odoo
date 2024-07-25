# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CwaProductUom(models.Model):
    _name = 'cwa.product.uom'
    _description = 'Product UoM and Purchase UoM'
    _order = "eenheid"

    name = fields.Char(related="eenheid")
    inhoud = fields.Float('Inhoud', size=64, required=True)
    eenheid = fields.Char('Eenheid', size=64, required=True)
    uom_id = fields.Many2one('uom.uom', 'Standard UoM', size=64)
    uom_po_id = fields.Many2one('uom.uom', 'Purchase UoM', size=64)
    target_inhoud = fields.Float('Target Inhoud')
    uos_combo = fields.Char('UoM/UoS Combo')

    @api.model
    def get_translated(self, source):
        return self.search([
            ('eenheid', '=ilike', source)
        ], limit=1)


