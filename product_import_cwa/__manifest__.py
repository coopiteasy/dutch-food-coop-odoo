{
    "name": "Product Import CWA",
    "version": "16.0.1.0.0",
    "author": "Sunflower IT",
    "license": "AGPL-3",
    "category": "Sales",
    "website": "https://github.com/Gedeelde-Weelde/dutch-food-coop-odoo",
    "summary": "",
    "depends": [
        "sale",
        "point_of_sale",
        "l10n_nl",
        "product_brand",
        "uom",
    ],
    "data": [
        "data/res_partner.xml",
        "data/ir_cron.xml",
        "data/pos_categories.xml",
        "data/cwa_product_quality.xml",
        "data/cwa_product_suppliers.xml",
        "data/account_tax.xml",
        "views/cwa_product.xml",
        "views/product_template.xml",
        "views/product_supplierinfo.xml",
        "views/cwa_import_action.xml",
        "views/cwa_product_brands.xml",
        "views/cwa_product_cblcode.xml",
        "views/cwa_product_quality.xml",
        "views/cwa_product_suppliers.xml",
        "views/cwa_product_uom.xml",
        "views/cwa_vat_tax.xml",
        "wizard/cwa_locate_brands_wizard.xml",
        "wizard/cwa_locate_cblcode_wizard.xml",
        "wizard/cwa_locate_uom_wizard.xml",
        "wizard/cwa_vat_tax_wizard.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
