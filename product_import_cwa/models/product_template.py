import logging

from odoo import api, fields, models
from odoo.addons.product_import_cwa.models.utils import YESNO_SELECTION, PRESENCE_SELECTION

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    eancode = fields.Char(help="Eancode.")
    kwaliteit = fields.Many2one("cwa.product.quality", help="Kwaliteitsaanduiding.")
    unique_id = fields.Char("Unique ID.")

    # From suppliers
    preferred_supplier_id = fields.Many2one(
        "product.supplierinfo",
        compute="_compute_preferred_supplier",
        search="_search_preferred_supplier",
        string="Preferred Supplier",
    )
    inhoud = fields.Char(help="Inhoud van de verpakking.")
    eenheid = fields.Char(help="Eenheid van de inhoud.")
    statiegeld = fields.Float(help="Statiegeldbedrag.")
    weegschaalartikel = fields.Boolean()
    pluartikel = fields.Boolean()
    herkomst = fields.Char(help="Land van herkomst in vorm ISO 3166 code.")
    proefdiervrij = fields.Selection(YESNO_SELECTION)
    vegetarisch = fields.Selection(YESNO_SELECTION)
    veganistisch = fields.Selection(YESNO_SELECTION)
    rauwemelk = fields.Selection(YESNO_SELECTION)
    plucode = fields.Char(help="4-cijferige plucode.")
    d204 = fields.Selection(PRESENCE_SELECTION, help="Cacao.")
    d209 = fields.Selection(PRESENCE_SELECTION, help="Glutamaat.")
    d210 = fields.Selection(PRESENCE_SELECTION, help="Gluten.")
    d212 = fields.Selection(PRESENCE_SELECTION, help="Ei.")
    d213 = fields.Selection(PRESENCE_SELECTION, help="Kip.")
    d214 = fields.Selection(PRESENCE_SELECTION, help="Melk.")
    d234 = fields.Selection(PRESENCE_SELECTION, help="Koriander.")
    d215 = fields.Selection(PRESENCE_SELECTION, help="Lactose.")
    d239 = fields.Selection(PRESENCE_SELECTION, help="Lupine.")
    d216 = fields.Selection(PRESENCE_SELECTION, help="Mais.")
    d217 = fields.Selection(PRESENCE_SELECTION, help="Noten.")
    d217b = fields.Selection(PRESENCE_SELECTION, help="Notenolie.")
    d220 = fields.Selection(PRESENCE_SELECTION, help="Peulvruchten.")
    d221 = fields.Selection(PRESENCE_SELECTION, help="Pinda.")
    d221b = fields.Selection(PRESENCE_SELECTION, help="Pindaolie.")
    d222 = fields.Selection(PRESENCE_SELECTION, help="Rogge.")
    d223 = fields.Selection(PRESENCE_SELECTION, help="Rundvlees.")
    d236 = fields.Selection(PRESENCE_SELECTION, help="Schaaldieren.")
    d235 = fields.Selection(PRESENCE_SELECTION, help="Selderij.")
    d238 = fields.Selection(PRESENCE_SELECTION, help="Sesam.")
    d238b = fields.Selection(PRESENCE_SELECTION, help="Sesamolie.")
    d225 = fields.Selection(PRESENCE_SELECTION, help="Soja.")
    d226 = fields.Selection(PRESENCE_SELECTION, help="Soja-olie.")
    d228 = fields.Selection(PRESENCE_SELECTION, help="Sulfiet.")
    d230 = fields.Selection(PRESENCE_SELECTION, help="Tarwe.")
    d232 = fields.Selection(PRESENCE_SELECTION, help="Varkensvlees.")
    d237 = fields.Selection(PRESENCE_SELECTION, help="Vis.")
    d240 = fields.Selection(PRESENCE_SELECTION, help="Wortel.")
    d241 = fields.Selection(PRESENCE_SELECTION, help="Mosterd.")
    d242 = fields.Selection(PRESENCE_SELECTION, help="Weekdieren.")
    verpakkingce = fields.Char(help="Verpakking van consumenteneenheid.")
    price_per_standard_unit = fields.Float(
        "Price per Standard Unit", compute="_compute_price_per_su"
    )
    has_new_price = fields.Boolean()

    @api.depends("uom_id", "uom_po_id", "list_price")
    def _compute_price_per_su(self):
        for this in self:
            uom_type = this.uom_id.uom_type
            price = this.list_price
            if this.uom_id != this.uom_po_id:
                if uom_type == "smaller":
                    this.price_per_standard_unit = this.uom_id.factor * price
                elif uom_type == "bigger":
                    this.price_per_standard_unit = this.uom_id.factor_inv * price
                else:
                    this.price_per_standard_unit = this.uom_po_id.factor_inv * price
            else:
                this.price_per_standard_unit = this.list_price

    @api.depends("seller_ids")
    def _compute_preferred_supplier(self):
        for this in self:
            if this.seller_ids:
                this.preferred_supplier_id = this.seller_ids[0].id
            else:
                this.preferred_supplier_id = None

    @api.depends("seller_ids")
    def _search_preferred_supplier(self, operator, value):
        for this in self:
            if this.seller_ids:
                this.preferred_supplier_id = this.seller_ids[0].id

    def unlink(self):
        for prod in self:
            cwa = self.env["cwa.product"].search([("unique_id", "=", prod.unique_id)])
            cwa.write(
                {
                    "state": "new",
                }
            )
        return super().unlink()
