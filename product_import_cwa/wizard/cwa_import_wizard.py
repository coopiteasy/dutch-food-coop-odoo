from odoo import models


class CwaImportWizard(models.TransientModel):
    _name = "cwa.import.products"
    _description = "CWA Import Products Wizard"

    def to_product(self):
        active_ids = self.env.context.get("active_ids", [])
        cwa_prods = self.env["cwa.product"].search([("id", "in", active_ids)])

        for product in cwa_prods.filtered(lambda p: p.state == "new"):
            product.to_product()
