import datetime
import logging
import os

from odoo.tests.common import TransactionCase


class TestProductImportCwa(TransactionCase):
    def setUp(self):
        super().setUp()
        # Set the logging level to WARNING during deletions
        old_logLevel = logging.getLogger("odoo").level
        logging.getLogger("odoo").setLevel(logging.WARNING)
        self.env["cwa.product"].search([]).unlink()
        self.env["product.supplierinfo"].search([]).unlink()
        logging.getLogger("odoo").setLevel(old_logLevel)

    def reset_translations(self):
        self.env["product.brand"].search([]).unlink()
        self.env["cwa.product.brands"].search([]).unlink()
        self.env["cwa.product.uom"].search([]).unlink()
        self.env["cwa.product.cblcode"].search([]).unlink()
        self.env["cwa.vat.tax"].search([]).unlink()

    def add_translations_for_brand_uom_cblcode_and_tax(self, cwa_prod):
        self.translate_brand(cwa_prod)
        self.translate_uom(cwa_prod)
        self.translate_cblcode(cwa_prod)
        self.translate_tax(cwa_prod)

    def translate_brand(self, prod):
        """Add dummy brand translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.brands"]
        wizard = wizard_obj.with_context(active_ids=prod.ids).create({})
        wizard.action_apply()

    def translate_uom(self, prod):
        """Add dummy UOM translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.uom"]
        wizard = wizard_obj.with_context(active_ids=prod.ids).create({})
        uom = self.env.ref("uom.product_uom_kgm")
        wizard.uom_ids.write(dict(uom_id=uom.id, uom_po_id=uom.id))
        wizard.action_apply()

    def translate_cblcode(self, prod):
        """Add dummy CBL code translation to product using wizards"""
        wizard_obj = self.env["cwa.product.import.cblcode"]
        wizard = wizard_obj.with_context(active_ids=prod.ids).create({})
        pos_categ = self.env["pos.category"].create({"name": "Beverage"})
        categ = self.env["product.category"].create({"name": "Beverage"})
        wizard.cblcode_ids.write(
            dict(pos_category=pos_categ.id, internal_category=categ.id)
        )
        wizard.action_apply()

    def translate_tax(self, prod):
        """Add dummy tax translation to product using wizards"""
        wizard_obj = self.env["cwa.vat.tax.wizard"]
        wizard = wizard_obj.with_context(active_ids=prod.ids).create({})
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

    def import_first_file(self, cwa_product_obj):
        path = os.path.dirname(os.path.realpath(__file__))
        file1 = os.path.join(path, "data/products_test.xml")
        cwa_product_obj.with_context(new_cursor=False).import_xml_products(file1)

    def import_second_file(self, cwa_product_obj):
        path = os.path.dirname(os.path.realpath(__file__))
        file2 = os.path.join(path, "data/products_test_modified.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file2
        )
        return count

    def test_product_import_cwa_imports_all_records(self):
        cwa_product_obj = self.env["cwa.product"]

        # load first batch of cwa.product records
        path = os.path.dirname(os.path.realpath(__file__))
        file1 = os.path.join(path, "data/products_test.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file1
        )
        self.assertEqual(count, 65)

    def test_product_import_cwa_imports_is_correctly_loaded(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod1 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.assertEqual(len(cwa_prod1), 1)

    def test_product_import_cwa_load_modified_file(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        count = self.import_second_file(cwa_product_obj)
        self.assertEqual(count, 1)
        cwa_prod2 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.assertTrue("EEKHOORNS" in cwa_prod2.ingredienten)

    def test_product_import_cwa_translations(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod2 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.reset_translations()
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod2)
        self.assertEqual(self.env["cwa.product.brands"].search_count([]), 1)
        self.assertEqual(self.env["cwa.product.uom"].search_count([]), 1)
        self.assertEqual(self.env["cwa.product.cblcode"].search_count([]), 1)
        self.assertEqual(self.env["cwa.vat.tax"].search_count([]), 1)

    def test_product_import_cwa_product_to_state_imported(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod)
        cwa_prod.to_product()
        self.assertEqual(cwa_prod.state, "imported")

    def test_product_import_cwa_product_import_into_product_template(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod)
        cwa_prod.to_product()

        product_template_object = self.env["product.template"]
        imported_product = product_template_object.search([("name", "=", "BOEKWEIT")])

        expected_product = {
            "unique_id": "1007-1001",
            "weegschaalartikel": False,
            "pluartikel": False,
            "inhoud": "1",
            "eenheid": "KG",
            "verpakkingce": False,
            "herkomst": "CN",
            "ingredients": "INGREDIENTEN: BOEKWEIT",
            "d204": "0",
            "d209": "0",
            "d210": "0",
            "d212": "0",
            "d213": "0",
            "d214": "0",
            "d234": "0",
            "d215": "0",
            "d239": "0",
            "d216": "0",
            "d217": "0",
            "d217b": "0",
            "d220": "0",
            "d221": "0",
            "d221b": "0",
            "d222": "0",
            "d223": "0",
            "d236": "0",
            "d235": "0",
            "d238": "0",
            "d238b": "0",
            "d225": "0",
            "d226": "0",
            "d228": "0",
            "d230": "0",
            "d232": "0",
            "d237": "0",
            "d240": "0",
            "proefdiervrij": "0",
            "vegetarisch": "0",
            "veganistisch": "0",
            "rauwemelk": "0",
        }

        actual_product = {
            key: getattr(imported_product, key, None) for key in expected_product.keys()
        }
        self.maxDiff = None
        self.assertDictEqual(expected_product, actual_product)

    def test_product_import_imports_wichtartikel_in_the_right_way(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod)
        cwa_prod.to_product()

        product_template_object = self.env["product.template"]
        imported_product = product_template_object.search([("name", "=", "BOEKWEIT")])

        expected_product = {
            "to_weight": True,
        }

        actual_product = {
            key: getattr(imported_product, key, None) for key in expected_product.keys()
        }
        self.assertDictEqual(expected_product, actual_product)

    def test_product_import_cwa_supplier_info(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod2 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod2)
        cwa_prod2.to_product()
        supplierinfo_obj = self.env["product.supplierinfo"]
        supp_info1 = supplierinfo_obj.search([("product_name", "=", "BOEKWEIT")])
        self.assertEqual(len(supp_info1), 1)
        self.assertFalse(supp_info1.eancode)
        self.assertEqual(supp_info1.unique_id, "1007-1001")
        _date = datetime.date(2016, 2, 11)
        self.assertEqual(supp_info1.ingangsdatum, _date)
        self.assertEqual(supp_info1.date_start, _date)
        self.assertEqual(supp_info1.eenheid, "KG")
        self.assertEqual(supp_info1.herkomst, "CN")

    def test_product_import_cwa_handle_multiple_suppliers(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_dup1 = cwa_product_obj.search([("eancode", "=", "8711812421205")])
        self.assertNotEqual(
            cwa_dup1[0].leveranciernummer, cwa_dup1[1].leveranciernummer
        )
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_dup1)
        for rec in cwa_dup1:
            rec.to_product()
        prod1 = self.env["product.template"].search([("eancode", "=", "8711812421205")])
        self.assertEqual(len(prod1), 1)
        self.assertEqual(len(prod1.seller_ids), 2)

    def test_product_import_cwa_supplier_not_deleted(self):
        supplierinfo_obj = self.env["product.supplierinfo"]
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        suppliers_before_import = supplierinfo_obj.search_count([])

        self.import_second_file(cwa_product_obj)

        count = self.import_second_file(cwa_product_obj)
        self.assertEqual(count, 0)
        suppliers_after_import = supplierinfo_obj.search_count([])
        self.assertEqual(suppliers_before_import, suppliers_after_import)

    def test_product_import_cwa_removal(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        path = os.path.dirname(os.path.realpath(__file__))
        file3 = os.path.join(path, "data/products_test_removed.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file3
        )
        self.assertEqual(count, 1)
        self.assertEqual(cwa_product_obj.search_count([]), 64)

    def test_product_import_cwa_recovers_from_invalid_characters_in_xml(self):
        cwa_product_obj = self.env["cwa.product"]

        # load first batch of cwa.product records
        path = os.path.dirname(os.path.realpath(__file__))
        file1 = os.path.join(path, "data/products_test_data_faulty.xml")
        count = cwa_product_obj.with_context(new_cursor=False).import_xml_products(
            file1
        )
        self.assertEqual(count, 2)

    def test_product_import_cwa_updetes_supplier_info_when_data_is_changed(self):
        cwa_product_obj = self.env["cwa.product"]
        self.import_first_file(cwa_product_obj)
        cwa_prod2 = cwa_product_obj.search([("omschrijving", "=", "BOEKWEIT")])
        self.add_translations_for_brand_uom_cblcode_and_tax(cwa_prod2)
        cwa_prod2.to_product()

        self.import_second_file(cwa_product_obj)

        supplierinfo_obj = self.env["product.supplierinfo"]
        supp_info1 = supplierinfo_obj.search([("product_name", "=", "BOEKWEIT")])
        self.assertEqual("INGREDIENTENN: BOEKWEIT, EEKHOORNS", supp_info1.ingredients)
