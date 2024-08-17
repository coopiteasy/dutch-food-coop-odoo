import datetime
import os

from odoo.tests.common import TransactionCase


class TestProductImportCwa(TransactionCase):
    def reset_translations(self):
        self.env["product.brand"].search([]).unlink()
        self.env["cwa.product.brands"].search([]).unlink()
        self.env["cwa.product.uom"].search([]).unlink()
        self.env["cwa.product.cblcode"].search([]).unlink()
        self.env["cwa.vat.tax"].search([]).unlink()

    def translate_brand(self, prod):
        """Add dummy brand translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.brands"]
        wizard = wizard_obj.with_context({"active_ids": prod.ids}).create({})
        wizard.action_apply()

    def translate_uom(self, prod):
        """Add dummy UOM translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.uom"]
        wizard = wizard_obj.with_context({"active_ids": prod.ids}).create({})
        uom = self.env.ref("uom.product_uom_kgm")
        wizard.uom_ids.write(dict(uom_id=uom.id, uom_po_id=uom.id))
        wizard.action_apply()

    def translate_cblcode(self, prod):
        """Add dummy CBL code translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.cblcode"]
        wizard = wizard_obj.with_context({"active_ids": prod.ids}).create({})
        pos_categ = self.env["pos.category"].create({"name": "Beverage"})
        categ = self.env["product.category"].create({"name": "Beverage"})
        wizard.cblcode_ids.write(
            dict(pos_category=pos_categ.id, internal_category=categ.id)
        )
        wizard.action_apply()

    def translate_tax(self, prod):
        """Add dummy tax translation to product using wizards"""
        wizard_obj = self.env["cwa.vat.tax.wizard"]
        wizard = wizard_obj.with_context({"active_ids": prod.ids}).create({})
        account_tax = self.env["account.tax"].create(
            {
                "name": "6 percent",
                "amount": 0.06,
                "amount_type": "percent",
            }
        )
        wizard.tax_ids.write(
            {
                "sale_tax_ids": (6, False, account_tax.ids),
                "purchase_tax_ids": (6, False, account_tax.ids),
            }
        )
        wizard.action_apply()

    def test_product_import_cwa(self):
        prod_tmpl_object = self.env["product.template"]
        cwa_product_obj = self.env["cwa.product"]

        # load first batch of cwa.product records
        path = os.path.dirname(os.path.realpath(__file__))
        file1 = os.path.join(path, "data/products_test.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file1
        )
        self.assertEqual(count, 65)

        # test if cwa.product records correctly loaded
        # find "Boekweit"
        cwa_prod1 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.assertEqual(len(cwa_prod1), 1)

        # decide to load the file that is changed a bit
        # check if Boekweit record has changed
        file2 = os.path.join(path, "data/products_test_modified.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file2
        )
        self.assertEqual(count, 1)
        count = cwa_product_obj.search_count([])
        self.assertEqual(count, 65)
        cwa_prod2 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.assertEqual(len(cwa_prod2), 1)
        self.assertTrue("EEKHOORNS" in cwa_prod2.ingredienten)

        # translate unknown stuff
        self.reset_translations()
        self.translate_brand(cwa_prod2)
        self.translate_uom(cwa_prod2)
        self.translate_cblcode(cwa_prod2)
        self.translate_tax(cwa_prod2)
        self.assertEqual(self.env["cwa.product.brands"].search_count([]), 1)
        self.assertEqual(self.env["cwa.product.uom"].search_count([]), 1)
        self.assertEqual(self.env["cwa.product.cblcode"].search_count([]), 1)
        self.assertEqual(self.env["cwa.vat.tax"].search_count([]), 1)

        # FROM HERE WE HAVE A PROBLEM!
        # Import the Boekweit product into the system,
        # both product and supplier details
        cwa_prod2.to_product()
        self.assertEqual(cwa_prod2.state, "imported")

        # test if product.supplier record correctly loaded
        supplierinfo_obj = self.env["product.supplierinfo"]
        supp_info1 = supplierinfo_obj.search([("product_name", "=", "BOEKWEIT")])
        self.assertEqual(len(supp_info1), 1)
        # test if empty EAN code results in eancode = False
        self.assertFalse(supp_info1.eancode)
        # test Unique_id correctly generated (1007-1001)
        self.assertEqual(supp_info1.unique_id, "1007-1001")
        # test if ingangsdatum is correctly loaded (2016-02-11)
        _date = datetime.date(2016, 2, 11)
        self.assertEqual(supp_info1.ingangsdatum, _date)
        self.assertEqual(supp_info1.date_start, _date)

        # Test if products with multiple suppliers are handled correctly
        # eg. Mango Met Gember, Prinsessen Droom, Sprookjes Rood

        # Prinsessen Droom, eancode: 8711812421205
        cwa_dup1 = cwa_product_obj.search([("eancode", "=", "8711812421205")])

        # Should have separate supplier numbers
        self.assertNotEqual(
            cwa_dup1[0].leveranciernummer, cwa_dup1[1].leveranciernummer
        )

        # Import product and the two suppliers
        self.translate_brand(cwa_dup1)
        self.translate_uom(cwa_dup1)
        self.translate_cblcode(cwa_dup1)
        for rec in cwa_dup1:
            rec.to_product()
        prod1 = prod_tmpl_object.search([("eancode", "=", "8711812421205")])

        # Should be 1 product and 2 suppliers
        self.assertEqual(len(prod1), 1)
        self.assertEqual(len(prod1.seller_ids), 2)

        # Do the import again, suppliers should not be deleted
        suppliers_before_import = supplierinfo_obj.search_count([])
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file2
        )
        self.assertEqual(count, 0)
        suppliers_after_import = supplierinfo_obj.search_count([])
        self.assertEqual(suppliers_before_import, suppliers_after_import)

        # If some items have been removed from the file, check if they are deleted
        file3 = os.path.join(path, "data/products_test_removed.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file3
        )
        self.assertEqual(count, 1)
        self.assertEqual(cwa_product_obj.search_count([]), 64)
