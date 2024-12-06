from odoo import api, fields, models


class CwaVatTaxWizard(models.TransientModel):
    _name = "cwa.vat.tax.wizard"
    _description = "Translate BTW to taxes"

    @api.model
    def _default_tax_ids(self):
        cwa_product_ids = list(set(self.env.context.get("active_ids", [])))
        tax_ids = []
        taxes = []
        for this in self.env["cwa.product"].browse(cwa_product_ids):
            trans = self.env["cwa.vat.tax"].get_translated(this.btw)
            if not trans and this.btw not in taxes:
                taxes.append(this.btw)
                tax_ids.append(
                    (
                        0,
                        0,
                        {
                            "cwa_product_id": this.id,
                            "btw": this.btw,
                        },
                    )
                )
        return tax_ids

    tax_ids = fields.One2many(
        "cwa.vat.tax.trans.wizard",
        "wizard_id",
        string="Product Brands",
        default=_default_tax_ids,
    )

    def action_apply(self):
        self.ensure_one()
        self.tax_ids.action_apply()
        return {"type": "ir.actions.act_window_close"}


class CwaVatTransTaxWizard(models.TransientModel):
    _name = "cwa.vat.tax.trans.wizard"
    _description = "CWA Vat Tax Configuration"

    wizard_id = fields.Many2one(
        "cwa.vat.tax.wizard", string="Wizard", required=True, ondelete="cascade"
    )
    cwa_product_id = fields.Many2one("cwa.product", required=True, ondelete="cascade")
    btw = fields.Integer("BTW", readonly=True)
    description = fields.Char()
    sale_tax_ids = fields.Many2one(
        "account.tax",
        domain=[("type_tax_use", "=", "sale")],
        string="Applicable Sale Tax",
    )
    purchase_tax_ids = fields.Many2one(
        "account.tax",
        domain=[("type_tax_use", "=", "purchase")],
        string="Applicable Purchase Tax",
    )

    def action_apply(self):
        for this in self:
            if this.sale_tax_ids and this.purchase_tax_ids:
                btw = this.cwa_product_id.btw
                values = {
                    "btw": btw,
                    "description": this.description
                    if this.description
                    else str(btw) + " %",
                    "sale_tax": [(6, 0, this.sale_tax_ids.ids)],
                    "purchase_tax": [(6, 0, this.purchase_tax_ids.ids)],
                }
                self.env["cwa.vat.tax"].create(values)
