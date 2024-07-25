import logging

from odoo import api, fields, models

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
        string="Preferred Supplier",
    )
    inhoud = fields.Char(related="preferred_supplier_id.inhoud")
    eenheid = fields.Char(related="preferred_supplier_id.eenheid")
    statiegeld = fields.Float(related="preferred_supplier_id.statiegeld")
    weegschaalartikel = fields.Boolean(
        related="preferred_supplier_id.weegschaalartikel"
    )
    pluartikel = fields.Boolean(related="preferred_supplier_id.pluartikel")
    herkomst = fields.Char(related="preferred_supplier_id.herkomst")
    ingredienten = fields.Text(
        help="Beschrijving van de ingredienten.",
        related="preferred_supplier_id.ingredienten",
    )
    proefdiervrij = fields.Selection(related="preferred_supplier_id.proefdiervrij")
    vegetarisch = fields.Selection(related="preferred_supplier_id.vegetarisch")
    veganistisch = fields.Selection(related="preferred_supplier_id.veganistisch")
    rauwemelk = fields.Selection(related="preferred_supplier_id.rauwemelk")
    plucode = fields.Char(
        related="preferred_supplier_id.plucode", help="4-cijferige plucode."
    )
    d204 = fields.Selection(related="preferred_supplier_id.d204", help="Cacao.")
    d209 = fields.Selection(related="preferred_supplier_id.d209", help="Glutamaat.")
    d210 = fields.Selection(related="preferred_supplier_id.d210", help="Gluten.")
    d212 = fields.Selection(related="preferred_supplier_id.d212", help="Ei.")
    d213 = fields.Selection(related="preferred_supplier_id.d213", help="Kip.")
    d214 = fields.Selection(related="preferred_supplier_id.d214", help="Melk.")
    d234 = fields.Selection(related="preferred_supplier_id.d234", help="Koriander.")
    d215 = fields.Selection(related="preferred_supplier_id.d215", help="Lactose.")
    d239 = fields.Selection(related="preferred_supplier_id.d239", help="Lupine.")
    d216 = fields.Selection(related="preferred_supplier_id.d216", help="Mais.")
    d217 = fields.Selection(related="preferred_supplier_id.d217", help="Noten.")
    d217b = fields.Selection(related="preferred_supplier_id.d217b", help="Notenolie.")
    d220 = fields.Selection(related="preferred_supplier_id.d220", help="Peulvruchten.")
    d221 = fields.Selection(related="preferred_supplier_id.d221", help="Pinda.")
    d221b = fields.Selection(related="preferred_supplier_id.d221b", help="Pindaolie.")
    d222 = fields.Selection(related="preferred_supplier_id.d222", help="Rogge.")
    d223 = fields.Selection(related="preferred_supplier_id.d223", help="Rundvlees.")
    d236 = fields.Selection(related="preferred_supplier_id.d236", help="Schaaldieren.")
    d235 = fields.Selection(related="preferred_supplier_id.d235", help="Selderij.")
    d238 = fields.Selection(related="preferred_supplier_id.d238", help="Sesam.")
    d238b = fields.Selection(related="preferred_supplier_id.d238b", help="Sesamolie.")
    d225 = fields.Selection(related="preferred_supplier_id.d225", help="Soja.")
    d226 = fields.Selection(related="preferred_supplier_id.d226", help="Soja-olie.")
    d228 = fields.Selection(related="preferred_supplier_id.d228", help="Sulfiet.")
    d230 = fields.Selection(related="preferred_supplier_id.d230", help="Tarwe.")
    d232 = fields.Selection(related="preferred_supplier_id.d232", help="Varkensvlees.")
    d237 = fields.Selection(related="preferred_supplier_id.d237", help="Vis.")
    d240 = fields.Selection(related="preferred_supplier_id.d240", help="Wortel.")
    d241 = fields.Selection(related="preferred_supplier_id.d241", help="Mosterd.")
    d242 = fields.Selection(related="preferred_supplier_id.d242", help="Weekdieren.")
    aantaldagenhoudbaar = fields.Char(
        related="preferred_supplier_id.aantaldagenhoudbaar",
        help="Aantal dagen houdbaar.",
    )
    bewaartemperatuur = fields.Char(
        related="preferred_supplier_id.bewaartemperatuur", help="Bewaartemperatuur."
    )
    gebruikstips = fields.Char(
        related="preferred_supplier_id.gebruikstips", help="Gebruikstips."
    )
    verpakkingce = fields.Char(
        related="preferred_supplier_id.verpakkingce",
        help="Verpakking van consumenteneenheid.",
    )
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

    def unlink(self):
        for prod in self:
            cwa = self.env["cwa.product"].search([("unique_id", "=", prod.unique_id)])
            cwa.write(
                {
                    "state": "new",
                }
            )
        return super(ProductTemplate, self).unlink()
