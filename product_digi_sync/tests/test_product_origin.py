from odoo.tests import TransactionCase

class TestProductOrigin(TransactionCase):

    def test_the_external_digi_id_is_based_on_the_id_after_creation(self):
        product_origin = self.env['product_digi_sync.product_origin'].create({
            "description": "Nederland"
        })

        expected_external_digi_id = product_origin.id + 10000

        self.assertEqual(expected_external_digi_id, product_origin.external_digi_id)
