from unittest.mock import patch

from odoo.addons.queue_job.models.base import Base as QueueJobBase

from .digi_sync_base_test_case import DigiSyncBaseTestCase

class TestProductQuality(DigiSyncBaseTestCase):
    def setUp(self):
        super().setUp()

        def mock_with_delay(with_delay_self):
            return with_delay_self

        self.patcher = patch.object(QueueJobBase, "with_delay", mock_with_delay)
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_the_external_digi_id_is_based_on_the_id_after_creation(self):
        product_quality = self.env["product_food_fields.product_quality"].create(
            {
                "code": "BD",
                "name": "Biologisch dynamisch"
            }
        )

        expected_digi_image_id = product_quality.id + 100000

        self.assertEqual(expected_digi_image_id, product_quality.digi_image_id)

