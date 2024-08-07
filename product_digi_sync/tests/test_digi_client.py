import base64
import contextlib
import io
import json
from json import JSONDecodeError
from unittest.mock import patch

import requests
from PIL import Image

from odoo.tests import tagged

from odoo.addons.product_digi_sync.models.digi_client import DigiApiException

from .digi_sync_base_test_case import DigiSyncBaseTestCase


class DigiClientTestCase(DigiSyncBaseTestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.digi_client = self.env["product_digi_sync.digi_client"].create(
            {"username": "test_username", "password": "123", "name": "Default"}
        )
        self.patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "weighted_barcode_rule_id", None
        )

    def tearDown(self):
        super().tearDown()
        self.patched_get_param.stop()
        self.patched_get_param = None

    @tagged("post_install", "-at_install")
    def test_it_can_be_instantiated_with_username_and_password(self):
        self.assertEqual(self.digi_client.password, "123")
        self.assertEqual(self.digi_client.username, "test_username")

    @tagged("post_install", "-at_install")
    def test_it_sends_a_product_to_digi_using_the_right_headers_and_url(self):
        product = self.env["product.product"].create({"name": "Test Product"})

        with self.patch_request_post() as post_spy:
            expected_url = "https://fresh.digi.eu:8010/API/V1/ARTICLE.SVC/POST"
            expected_headers = {
                "ApplicationLogIn": json.dumps(
                    {"User": "test_username", "Password": "123"}
                ),
                "Content-Type": "application/json",
            }

            self.digi_client.send_product_to_digi(product)

            self.assertEqual(post_spy.call_args.kwargs["url"], expected_url)
            self.assertEqual(post_spy.call_args.kwargs["headers"], expected_headers)

    @tagged("post_install", "-at_install")
    def test_it_sends_a_product_to_digi_with_the_right_payload(self):
        name = "Test product"
        ingredients = "Noten en zo"
        plu_code = 200
        expected_unit_price = 250
        expected_cost_price = 150
        expected_storage_temp = 6
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 42,
            }
        )

        expected_payload = self._create_expected_product_payload(
            cost_price=expected_cost_price,
            unit_price=expected_unit_price,
            ingredients=ingredients,
            name=name,
            plu_code=plu_code,
            category_id=test_category.external_digi_id,
            show_packed_date_on_label=True,
            storage_temp=expected_storage_temp,

        )

        product = self.env["product.product"].create(
            {
                "name": "Test product",
                "ingredients": ingredients,
                "plu_code": plu_code,
                "categ_id": test_category.id,
                "list_price": 2.5,
                "standard_price": 1.5,
                "show_packed_date_on_label": True,
                "storage_temperature": expected_storage_temp,
            }
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_sends_a_product_to_digi_with_the_right_payload_when_usage_tips_present(self):
        name = "Test product"
        ingredients = "Noten en zo"
        expected_usage_tips = "Gebruikstips"
        plu_code = 200
        expected_unit_price = 250
        expected_cost_price = 150
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 42,
            }
        )

        expected_payload = self._create_expected_product_payload(
            cost_price=expected_cost_price,
            unit_price=expected_unit_price,
            ingredients=ingredients,
            name=name,
            plu_code=plu_code,
            category_id=test_category.external_digi_id,
            show_packed_date_on_label=True,
            usage_tips=expected_usage_tips,
        )

        product = self.env["product.product"].create(
            {
                "name": "Test product",
                "ingredients": ingredients,
                "plu_code": plu_code,
                "categ_id": test_category.id,
                "list_price": 2.5,
                "standard_price": 1.5,
                "show_packed_date_on_label": True,
                "usage_tips": expected_usage_tips
            }
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_sends_a_product_to_digi_with_the_right_payload_with_expiration_dates(self):
        name = "Test product"
        ingredients = "Noten en zo"
        plu_code = 200
        expected_unit_price = 250
        expected_cost_price = 150
        expected_storage_temp = 6
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 42,
            }
        )

        expected_days_until_expiry = 15
        expected_days_until_bad_taste = 7

        expected_payload = self._create_expected_product_payload(
            cost_price=expected_cost_price,
            unit_price=expected_unit_price,
            ingredients=ingredients,
            name=name,
            plu_code=plu_code,
            category_id=test_category.external_digi_id,
            show_packed_date_on_label=True,
            storage_temp=expected_storage_temp,
            days_until_expiry=expected_days_until_expiry,
            days_until_bad_taste=expected_days_until_bad_taste,
        )

        product = self.env["product.product"].create(
            {
                "name": "Test product",
                "ingredients": ingredients,
                "plu_code": plu_code,
                "categ_id": test_category.id,
                "list_price": 2.5,
                "standard_price": 1.5,
                "show_packed_date_on_label": True,
                "storage_temperature": expected_storage_temp,
                "days_until_expiry": expected_days_until_expiry,
                "days_until_bad_taste": expected_days_until_bad_taste
            }
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_does_not_send_empty_fields(self):
        name = "Test product"
        ingredients = "Noten en zo"
        plu_code = 200
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 120,
            }
        )

        product_without_standard_price = self.env["product.product"].create(
            {
                "name": "Test product",
                "ingredients": ingredients,
                "plu_code": plu_code,
                "list_price": 1.0,
                "categ_id": test_category.id,
            }
        )

        expected_payload = self._create_expected_product_payload(
            plu_code=plu_code,
            name=name,
            ingredients=ingredients,
            unit_price=int(product_without_standard_price.list_price * 100),
            category_id=test_category.external_digi_id,
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product_without_standard_price)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_does_not_send_empty_ingredients(self):
        name = "Test product"
        plu_code = 200
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 120,
            }
        )

        product_without_standard_price = self.env["product.product"].create(
            {
                "name": "Test product",
                "plu_code": plu_code,
                "list_price": 1.0,
                "categ_id": test_category.id,
            }
        )

        expected_payload = self._create_expected_product_payload(
            plu_code=plu_code,
            name=name,
            unit_price=int(product_without_standard_price.list_price * 100),
            category_id=test_category.external_digi_id,
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product_without_standard_price)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_sends_status_pieces_article_true_when_article_is_pieces_article(self):
        name = "Test product"
        plu_code = 200
        self.patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "piece_barcode_rule_id", None
        )
        self.patched_get_param.start()

        test_category = self.env["product.category"].create(
            {
                "name": "Test category",
                "external_digi_id": 120,
            }
        )

        product_without_standard_price = self.env["product.product"].create(
            {
                "name": "Test product",
                "plu_code": plu_code,
                "list_price": 1.0,
                "categ_id": test_category.id,
                "send_to_scale": True,
                "is_pieces_article": True,
            }
        )

        expected_payload = self._create_expected_product_payload(
            plu_code=plu_code,
            name=name,
            unit_price=int(product_without_standard_price.list_price * 100),
            category_id=test_category.external_digi_id,
            is_pieces_article=True,
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product_without_standard_price)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    @tagged("post_install", "-at_install")
    def test_it_sends_no_barcode_to_digi_id_if_wrong_format(self):
        barcode_rule = self.env["barcode.rule"].create(
            {
                "name": "Test barcode",
                "encoding": "ean13",
                "type": "price",
                "pattern": ".*",
                "digi_barcode_type_id": 42,
            }
        )

        self.patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "weighted_barcode_rule_id", barcode_rule.id
        )
        self.patched_get_param.start()

        product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            sended_json = post_spy.call_args.kwargs["data"]
            sended_data = json.loads(sended_json)
            self.assertFalse("NormalBarcode1" in sended_data)

    @tagged("post_install", "-at_install")
    def test_it_sends_the_barcode_digi_id_if_present(self):
        barcode_rule = self.env["barcode.rule"].create(
            {
                "name": "Test barcode",
                "encoding": "ean13",
                "type": "price",
                "pattern": "27.*",
                "digi_barcode_type_id": 42,
            }
        )

        self.patched_get_param = self._patch_ir_config_parameter_for_get_param(
            "weighted_barcode_rule_id", barcode_rule.id
        )
        self.patched_get_param.start()

        product = self.env["product.product"].create(
            {
                "name": "Test product",
            }
        )

        expected_data = {
            "NormalBarcode1": {
                "BarcodeDataType": {
                    "Id": 42,
                },
                "Code": 0,
                "DataId": 1,
                "Flag": 27,
                "Type": {
                    "Id": 42,
                },
            }
        }

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            sent_json = post_spy.call_args.kwargs["data"]
            sent_data = json.loads(sent_json)

            compare_data = {key: sent_data[key] for key in expected_data}

            self.assertEqual(expected_data, compare_data)

    @tagged("post_install", "-at_install")
    def test_it_throws_an_exception_when_request_failed(self):
        product = self.env["product.product"].create({"name": "Test product"})
        response_content = """
                    {
          "Result": -99,
          "ResultDescription": "Invalid_UserPassword",
          "DataId": 0,
          "Post": [],
          "Validation": []
        }
                    """

        with self.patch_request_post(
            status_code=200, response_content=response_content
        ):
            with self.assertRaises(DigiApiException):
                self.digi_client.send_product_to_digi(product)

    @tagged("post_install", "-at_install")
    def test_it_sets_the_result_description_and_code_as_exception_message(self):
        product = self.env["product.product"].create({"name": "Test product"})
        response_content = """
                    {
          "Result": -98,
          "ResultDescription": "Number of filter parameters not correct",
          "DataId": 0,
          "Post": [],
          "Validation": []
        }
                    """

        with self.patch_request_post(
            status_code=200, response_content=response_content
        ):
            with self.assertRaises(DigiApiException) as context:
                self.digi_client.send_product_to_digi(product)
        self.assertEqual(
            str(context.exception), "Error -98: Number of filter parameters not correct"
        )

    def test_it_doesnt_catch_other_exceptions(self):
        product = self.env["product.product"].create({"name": "Test product"})

        with self.patch_request_post(response_content="Invalid json {"):
            with self.assertRaises(JSONDecodeError):
                self.digi_client.send_product_to_digi(product)

    def test_it_sends_a_product_image_to_digi_with_the_right_url(self):
        name = "product Name"
        plu_code = 200
        with self.patch_request_post() as post_spy:
            product_with_image = self._create_product_with_image(name, plu_code)

            expected_url = "https://fresh.digi.eu:8010/API/V1/MultiMedia.SVC/POST"

            self.digi_client.send_product_image_to_digi(product_with_image)

            self.assertEqual(post_spy.call_args.kwargs["url"], expected_url)

    def test_it_sends_a_product_image_to_digi_with_the_right_payload(self):
        name = "product Name"
        plu_code = 200

        with self.patch_request_post() as post_spy:
            product_with_image = self._create_product_with_image(name, plu_code)

            expected_image_data = product_with_image.image_1920.decode("utf-8")

            payload = {}
            payload["DataId"] = plu_code
            Linknumber_preset_image = 95
            payload["Links"] = [
                {
                    "DataId": plu_code,
                    "LinkNumber": Linknumber_preset_image,
                    "Type": {
                        "Description": "Article",
                        "Id": 2,
                    },
                }
            ]
            payload["OriginalInput"] = expected_image_data
            payload["Names"] = [
                {
                    "DataId": 1,
                    "Reference": "Nederlands",
                    "Name": "product_name",
                }
            ]
            payload["InputFormat"] = "png"

            expected_payload = json.dumps(payload)

            self.digi_client.send_product_image_to_digi(product_with_image)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    def test_it_sends_a_product_image_to_digi_with_the_right_payload_for_jpeg(self):
        name = "product Name"
        plu_code = 200

        with self.patch_request_post() as post_spy:
            product_with_image = self._create_product_with_image_for_jpeg(
                name, plu_code
            )

            expected_image_data = product_with_image.image_1920.decode("utf-8")

            payload = {}
            payload["DataId"] = plu_code
            linknumber_preset_image = 95
            payload["Links"] = [
                {
                    "DataId": plu_code,
                    "LinkNumber": linknumber_preset_image,
                    "Type": {
                        "Description": "Article",
                        "Id": 2,
                    },
                }
            ]
            payload["OriginalInput"] = expected_image_data
            payload["Names"] = [
                {
                    "DataId": 1,
                    "Reference": "Nederlands",
                    "Name": "product_name",
                }
            ]
            payload["InputFormat"] = "jpg"

            expected_payload = json.dumps(payload)

            self.digi_client.send_product_image_to_digi(product_with_image)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    def test_it_sends_a_product_quality_image_to_digi_with_the_right_payload(self):
        with self.patch_request_post() as post_spy:
            image_id = 1000010
            quality = self.env['product_food_fields.product_quality'].create({
                "code": "BD",
                "name": "Biologisch dynamisch",
                "image": self._create_dummy_image("png"),
                "digi_image_id": image_id,
            })

            plu_code = 200
            product = self.env["product.template"].create(
                {
                    "name": "test product",
                    "plu_code": plu_code,
                    "list_price": 1.0,
                    "product_quality_id": quality.id,
                }
            )

            expected_image_data = quality.image.decode("utf-8")

            payload = {}
            payload["DataId"] = image_id
            payload["OriginalInput"] = expected_image_data
            payload["Names"] = [
                {
                    "DataId": 1,
                    "Reference": "Nederlands",
                    "Name": "biologisch_dynamisch",
                }
            ]
            payload["Links"] = [
                {
                    "DataId": plu_code,
                    "LinkNumber": 1,
                    "Type": {
                        "Description": "Article",
                        "Id": 2,
                    },
                }
            ]
            payload["InputFormat"] = "png"

            expected_payload = json.dumps(payload)

            self.digi_client.send_product_quality_image_to_digi(product)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    def test_it_sends_a_product_category_to_digi_with_the_right_url(self):
        category_name = "Test category"
        digi_id = 2
        category = self.env["product.category"].create(
            {
                "name": category_name,
                "external_digi_id": digi_id,
            }
        )

        with self.patch_request_post() as post_spy:
            expected_url = "https://fresh.digi.eu:8010/API/V1/MAINGROUP.SVC/POST"

            self.digi_client.send_category_to_digi(category)

            self.assertEqual(post_spy.call_args.kwargs["url"], expected_url)

    def test_it_sends_a_category_digi(self):
        category_name = "Test category"
        digi_id = 2
        category = self.env["product.category"].create(
            {
                "name": category_name,
                "external_digi_id": digi_id,
            }
        )

        payload = {
            "DataId": digi_id,
            "DepartmentId": 97,
            "Names": [
                {
                    "Reference": "Nederlands",
                    "Name": category_name,
                }
            ],
        }

        expected_payload = json.dumps(payload)

        with self.patch_request_post() as post_spy:
            self.digi_client.send_category_to_digi(category)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    def test_it_sends_a_product_origin_to_digi_with_the_right_payload(self):
        origin = self.env["product_digi_sync.product_origin"].create(
            {"description": "Spanje"}
        )

        payload = {
            "DataId": origin.external_digi_id,
            "Names": [
                {
                    "Reference": "Nederlands",
                    "DdData": "02000000<span style='font-family:\"DejaVu Sans\";font-size:24px;'>Herkomst:<\/~02000000span><b><span~02000000style='font-family:\"DIN\";font-size:36px;'>Spanje<\/span><\/b>",
                    "Name": "Herkomst Spanje",
                }
            ],
        }

        expected_payload = json.dumps(payload)

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_origin_to_digi(origin)

            self.assertEqual(post_spy.call_args.kwargs["data"], expected_payload)

    def test_it_sends_the_product_origin_to_digi_using_labeltext_with_digi_id(self):
        origin = self.env["product_digi_sync.product_origin"].create(
            {"description": "Spanje"}
        )
        product = self.env["product.product"].create(
            {"name": "Test Origin", "plu_code": 42, "product_origin_id": origin.id}
        )

        expected_labeltext_in_payload = origin.external_digi_id

        with self.patch_request_post() as post_spy:
            self.digi_client.send_product_to_digi(product)

            send_data = json.loads(post_spy.call_args.kwargs["data"])
            self.assertEqual(
                send_data["LabelTextDataId"], expected_labeltext_in_payload
            )

    @contextlib.contextmanager
    def patch_request_post(self, status_code=200, response_content=None):
        if not response_content:
            response_content = json.dumps(
                {
                    "Result": 1,
                    "ResultDescription": "Ok",
                    "DataId": 0,
                    "Post": [],
                    "Validation": [],
                }
            )
        mock_response = requests.Response()
        mock_response.status_code = status_code
        mock_response._content = response_content.encode("utf-8")
        with patch("requests.post", return_value=mock_response) as post_spy:
            yield post_spy

    def _create_product_with_image(self, name, plu_code):
        product_with_image = self.env["product.template"].create(
            {
                "name": name,
                "plu_code": plu_code,
                "list_price": 1.0,
            }
        )
        # Create a 1x1 pixel image
        image = Image.new("RGB", (1, 1))
        output = io.BytesIO()
        image.save(output, format="PNG")
        # Get the binary data of the image
        image_data = base64.b64encode(output.getvalue())
        output.close()
        product_with_image.image_1920 = image_data
        return product_with_image

    def _create_product_with_image_for_jpeg(self, name, plu_code):
        product_with_image = self.env["product.template"].create(
            {
                "name": name,
                "plu_code": plu_code,
                "list_price": 1.0,
            }
        )
        # Create a 1x1 pixel image
        image_data = self._create_dummy_image(format="jpeg")
        product_with_image.image_1920 = image_data
        return product_with_image

    def _create_expected_product_payload(self, **kwargs):
        data = {}
        data["DataId"] = kwargs.get('plu_code')
        data["Names"] = [
            {
                "Reference": "Nederlands",
                "DdFormatCommodity": f"01000000{kwargs.get('name')}",
            }
        ]
        if kwargs.get("ingredients"):
            data["Names"][0]["DdFormatIngredient"] = f"01000000{kwargs.get('ingredients')}"
        if kwargs.get("usage_tips"):
            data["Names"][0]["DdFormatSpecialMessage"] = f"01000000{kwargs.get('usage_tips')}"
        if kwargs.get('unit_price'):
            data["UnitPrice"] = kwargs.get('unit_price')
        if kwargs.get('cost_price'):
            data["CostPrice"] = kwargs.get('cost_price')
        data["MainGroupDataId"] = kwargs.get('category_id')

        data["StatusFields"] = {
            "PiecesArticle": kwargs.get("is_pieces_article") or False,
            "PackedDate": kwargs.get('show_packed_date_on_label') or False
        }
        if kwargs.get('storage_temp'):
            data["MinStorageTemp"] = kwargs.get("storage_temp")
        if kwargs.get("days_until_expiry"):
            data["StatusFields"]["SellByDate"] = True
            data["SellByDateAmount"] = kwargs.get("days_until_expiry")
        if kwargs.get("days_until_bad_taste"):
            data["StatusFields"]["TasteDate"] = True
            data["TasteDateAmount"] = kwargs.get("days_until_bad_taste")
        return json.dumps(data)
