from unittest.mock import patch, Mock

from odoo.addons.product_digi_sync.models.digi_client import DigiClient
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


    def test_the_external_digi_id_is_set_to_desired_value_when_creating_record(self):
        product_quality = self._create_product_quality_with_image()

        expected_digi_image_id = 42

        self.assertEqual(expected_digi_image_id, product_quality.digi_image_id)


    def test_it_sends_the_product_quality_image_to_digi_when_record_is_created_and_the_image_is_set(self):
        digi_client = self._create_digi_client()

        client_id = digi_client.id
        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "digi_client_id", client_id
        )
        patched_get_param.start()
        mock_send_product_quality_image_to_digi = Mock()
        patch.object(
            DigiClient, "send_product_quality_image_to_digi", mock_send_product_quality_image_to_digi
        ).start()

        product_quality = self._create_product_quality_with_image()

        self.assertEqual(mock_send_product_quality_image_to_digi.call_args[0][0], product_quality)
        patched_get_param.stop()

    def test_it_sends_the_product_quality_image_to_digi_when_record_is_saved_and_the_image_is_set(self):
        digi_client = self._create_digi_client()

        client_id = digi_client.id
        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "digi_client_id", client_id
        )
        patched_get_param.start()
        mock_send_product_quality_image_to_digi = Mock()
        patch.object(
            DigiClient, "send_product_quality_image_to_digi", mock_send_product_quality_image_to_digi
        ).start()

        product_quality = self._create_product_quality_without_image()
        product_quality.write({
            "image": self._create_dummy_image("png")
        })

        self.assertEqual(mock_send_product_quality_image_to_digi.call_args[0][0], product_quality)
        patched_get_param.stop()

    def _create_product_quality_with_image(self):
        return self.env["product_food_fields.product_quality"].create(
            {
                "code": "BD",
                "name": "Biologisch dynamisch",
                "image": self._create_dummy_image("png"),
                "digi_image_id": 42
            }
        )


    def _create_product_quality_without_image(self):
        return self.env["product_food_fields.product_quality"].create(
            {
                "code": "BD",
                "name": "Biologisch dynamisch",
                "digi_image_id": 42
            }
        )

