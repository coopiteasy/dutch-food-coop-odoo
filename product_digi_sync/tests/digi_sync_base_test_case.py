from unittest.mock import patch

from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_config_parameter import IrConfigParameter


class DigiSyncBaseTestCase(TransactionCase):
    def _patch_ir_config_parameter_for_get_param(self, key_to_patch, value):
        original_get_param = IrConfigParameter.get_param

        def patched_get_param(self, key, default=False):
            if key == key_to_patch:
                return value  # return a specific value for a particular key
            else:
                return original_get_param(self, key, default)

        return patch.object(IrConfigParameter, "get_param", patched_get_param)

    def _create_digi_client(self):
        digi_client = self.env["product_digi_sync.digi_client"].create(
            {
                "name": "Test Digi Client",
                "username": "user",
                "password": "<PASSWORD>",
            }
        )
        return digi_client
