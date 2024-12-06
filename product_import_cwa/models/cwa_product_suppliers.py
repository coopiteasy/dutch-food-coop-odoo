from odoo import fields, models


class CwaProductSuppliers(models.Model):
    _name = "cwa.product.suppliers"
    _description = "Product Suppliers based on Leveranciernummer"
    _order = "leveranciernummer"

    name = fields.Many2one(related="res_partner_id")
    res_partner_id = fields.Many2one("res.partner", "Supplier Name")
    phone = fields.Char(related="res_partner_id.phone")
    ref = fields.Char(related="res_partner_id.ref")
    leveranciernummer = fields.Char(help="Nummer van de leverancier.")

    _sql_constraints = [
        (
            "cwa_product_suppliers_leveranciernummer_unique",
            "unique(leveranciernummer)",
            "This Leveranciernummer already exist.",
        )
    ]
