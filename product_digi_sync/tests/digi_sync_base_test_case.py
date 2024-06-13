from unittest.mock import patch

from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_config_parameter import IrConfigParameter


class DigiSyncBaseTestCase(TransactionCase):
    def _patch_ir_config_parameter_for_get_param(self, client_id):
        original_get_param = IrConfigParameter.get_param

        def patched_get_param(self, key, default=False):
            if key == "digi_client_id":
                return client_id  # return a specific value for a particular key
            else:
                return original_get_param(self, key, default)

        return patch.object(IrConfigParameter, "get_param", patched_get_param)
