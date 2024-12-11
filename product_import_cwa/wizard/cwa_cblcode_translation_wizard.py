from odoo import fields, models


class CwaCblcodeTranslationWizard(models.TransientModel):
    _name = "cwa.cblcode.translation.wizard"
    _description = "CWA CBL Code Translation Wizard"

    source_value = fields.Char(
        "CBL Code",
        size=64,
        required=True,
        default=lambda self: self.env.context.get("default_source_value"),
    )
    internal_category = fields.Many2one(
        "product.category", "Internal category", required=False
    )
    pos_category = fields.Many2one("pos.category", "POS category", required=False)

    def action_create_cwa_product_cblcode(self):
        self.ensure_one()
        self.env["cwa.product.cblcode"].create(
            {
                "source_value": self.source_value,
                "internal_category": self.internal_category.id
                if self.internal_category
                else False,
                "pos_category": self.pos_category.id if self.pos_category else False,
            }
        )
