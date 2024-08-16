from unittest.mock import Mock, patch

from odoo.addons.product_digi_sync.models.digi_client import DigiClient
from odoo.addons.queue_job.models.base import Base as QueueJobBase

from .digi_sync_base_test_case import DigiSyncBaseTestCase


class TestProductOrigin(DigiSyncBaseTestCase):
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
        product_origin = self.env["product_digi_sync.product_origin"].create(
            {"name": "Nederland"}
        )

        expected_external_digi_id = product_origin.id + 10000

        self.assertEqual(expected_external_digi_id, product_origin.external_digi_id)

    def test_it_sends_the_product_origin_to_digi_when_created(self):
        digi_client = self._create_digi_client()

        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "digi_client_id", digi_client.id
        )
        patched_get_param.start()

        mock_send_product_origin_to_digi = Mock()
        patched_digi_client = patch.object(
            DigiClient, "send_product_origin_to_digi", mock_send_product_origin_to_digi
        )
        patched_digi_client.start()

        origin = self.env["product_digi_sync.product_origin"].create(
            {"name": "Nederland"}
        )

        self.assertEqual(mock_send_product_origin_to_digi.call_args[0][0], origin)
        patched_digi_client.stop()
        patched_get_param.stop()

    def test_it_sends_the_product_origin_to_digi_when_saved(self):
        digi_client = self._create_digi_client()

        patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "digi_client_id", digi_client.id
        )
        patched_get_param.start()

        mock_send_product_origin_to_digi = Mock()
        patched_digi_client = patch.object(
            DigiClient, "send_product_origin_to_digi", mock_send_product_origin_to_digi
        )
        patched_digi_client.start()

        origin = self.env["product_digi_sync.product_origin"].create(
            {"name": "Nederland"}
        )
        origin.write({"name": "Spanje"})

        self.assertEqual(
            mock_send_product_origin_to_digi.call_args_list[1][0][0], origin
        )
        self.assertEqual(mock_send_product_origin_to_digi.call_count, 2)
        patched_digi_client.stop()
        patched_get_param.stop()
