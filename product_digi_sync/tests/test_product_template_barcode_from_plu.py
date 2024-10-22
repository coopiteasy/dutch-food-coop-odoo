from odoo.tests import tagged

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

        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "weighted_barcode_rule_id", barcode_rule_weighted.id
        )
        patched_get_param.start()

        # Test case code here
        product_template = self.env["product.template"].create(
            {"name": "dummy_name", "shop_plucode": 100}
        )

        self.assertEqual(product_template.barcode, "2300100000008")
        patched_get_param.stop()

    @tagged("post_install", "-at_install")
    def test_setting_plu_sets_updates_barcode_for_pieces_product(self):
        barcode_rule_piece = self.env["barcode.rule"].create(
            {
                "name": "Test barcode",
                "encoding": "ean13",
                "type": "price",
                "pattern": "31.....{NNNDD}",
                "digi_barcode_type_id": 42,
            }
        )

        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "piece_barcode_rule_id", barcode_rule_piece.id
        )
        patched_get_param.start()

        # Test case code here
        product_template = self.env["product.template"].create(
            {"name": "dummy_name", "shop_plucode": 100, "is_weighted_article": False}
        )

        self.assertEqual(product_template.barcode, "3100100000003")
        patched_get_param.stop()
