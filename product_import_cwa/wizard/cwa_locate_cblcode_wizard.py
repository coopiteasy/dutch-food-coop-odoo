from odoo import fields, models


class CwaProductImportCblcode(models.TransientModel):
    _name = "cwa.product.import.cblcode"
    _description = "CBL Codes Translation"

    def _default_cblcode_ids(self):
        cwa_product_ids = list(set(self.env.context.get("active_ids", [])))
        cblcode_ids = []
        cblcodes = []
        show_all = self.env.context.get("show_all")
        for this in self.env["cwa.product"].browse(cwa_product_ids):
            trans = self.env["cwa.product.cblcode"].get_translated(this.cblcode)
            if this.cblcode not in cblcodes and (show_all or not trans):
                cblcodes.append(this.cblcode)
                cblcode_ids.append(
                    (
                        0,
                        0,
                        {
                            "cwa_product_id": this.id,
                            "trans_id": trans.id,
                            "source_value": this.cblcode,
                            "internal_category": trans.internal_category.id,
                            "pos_category": trans.pos_category.id,
                        },
                    )
                )
        return cblcode_ids

    cblcode_ids = fields.One2many(
        "cwa.product.import.cblcode.wizard",
        "wizard_id",
        string="CBL Code",
        default=_default_cblcode_ids,
    )

    def action_apply(self):
        for this in self.cblcode_ids:
            int_cat = this.internal_category.id
            pos_cat = this.pos_category.id
            values = dict(source_value=this.source_value)
            values.update(dict(internal_category=int_cat))
            values.update(dict(pos_category=pos_cat))
            if this.trans_id:
                if int_cat or pos_cat:
                    this.trans_id.write(values)
                else:
                    this.trans_id.unlink()
            elif int_cat or pos_cat:
                this.trans_id = self.env["cwa.product.cblcode"].create(values)
        return {"type": "ir.actions.act_window_close"}


class CwaProductImportCblcodeWizard(models.TransientModel):
    _name = "cwa.product.import.cblcode.wizard"
    _description = "CWA Product CBL Codes Configuration"

    wizard_id = fields.Many2one(
        "cwa.product.import.cblcode", string="Wizard", required=True, ondelete="cascade"
    )
    trans_id = fields.Many2one("cwa.product.cblcode")
    cwa_product_id = fields.Many2one("cwa.product", required=True, ondelete="cascade")
    source_value = fields.Char("CBL Code")
    internal_category = fields.Many2one("product.category", "Internal category")
    pos_category = fields.Many2one("pos.category", "POS category")
