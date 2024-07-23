from odoo.tests import  tagged

from .digi_sync_base_test_case import DigiSyncBaseTestCase

class ProductTemplateBarcodeFromPluTestCase(DigiSyncBaseTestCase):
    @tagged("post_install", "-at_install")
    def test_setting_plu_sets_updates_barcode_for_weighted_product(self):

        barcode_rule_weighted = self.env["barcode.rule"].create(
            {
                "name": "Test barcode",
                "encoding": "ean13",
                "type": "price",
                "pattern": "23.....{NNNDD}",
                "digi_barcode_type_id": 42,
            }
        )

        patched_get_param = self._patch_ir_config_parameter_for_get_param("weighted_barcode_rule_id", barcode_rule_weighted.id)
        patched_get_param.start()
        digi_client = self._create_digi_client()

        # Test case code here
        product_template = self.env["product.template"].create(
            {"name": "dummy_name", "plu_code": 100}
        )

        self.assertEqual(product_template.barcode, "2300100000008")
        patched_get_param.stop()
