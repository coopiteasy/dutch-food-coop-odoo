import base64
import io
import json
import re

from PIL import Image


class ProductTransformer:
    @classmethod
    def transform_product_to_payload(self, product):
        data = {}
        data["DataId"] = product.plu_code
        data["Names"] = [
            {
                "Reference": "Nederlands",
                "DdFormatCommodity": f"01000000{product.name}",
            }
        ]
        if product.ingredients:
            data["Names"][0]["DdFormatIngredient"] = f"01000000{product.ingredients}"
        if product.usage_tips:
            data["Names"][0]["DdFormatSpecialMessage"] = f"01000000{product.usage_tips}"
        if product.list_price:
            data["UnitPrice"] = int(product.list_price * 100)
        if product.standard_price:
            data["CostPrice"] = int(product.standard_price * 100)
        if product.categ_id.id:
            data["MainGroupDataId"] = product.categ_id.external_digi_id
        if product.product_origin_id:
            data["LabelTextDataId"] = product.product_origin_id.external_digi_id
        data["StatusFields"] = {
            "PiecesArticle": product.is_pieces_article,
            "PackedDate": product.show_packed_date_on_label
        }
        if product.storage_temperature != 0:
            data["MinStorageTemp"] = product.storage_temperature
        if product.days_until_expiry != 0:
            data["StatusFields"]["SellByDate"] = True
            data["SellByDateAmount"] = product.days_until_expiry
        if product.days_until_bad_taste != 0:
            data["StatusFields"]["TasteDate"] = True
            data["TasteDateAmount"] = product.days_until_bad_taste
        if product and product.get_current_barcode_rule() is not None:
            barcode_rule = product.get_current_barcode_rule()
            matches = re.match(r"^(\d{2}).*", barcode_rule.pattern)

            if matches:
                flag = matches.group(1)
                if flag.isnumeric():
                    barcode_id = barcode_rule.digi_barcode_type_id
                    data["NormalBarcode1"] = {
                        "BarcodeDataType": {
                            "Id": barcode_id,
                        },
                        "Code": 0,
                        "DataId": 1,
                        "Flag": int(flag),
                        "Type": {
                            "Id": barcode_id,
                        },
                    }

        return json.dumps(data)

    @classmethod
    def transform_product_to_image_payload(cls, product):
        image_name = product.name.lower().replace(" ", "_")
        payload = {"DataId": product.plu_code}
        image_data = base64.b64decode(product.image_1920)
        image = Image.open(io.BytesIO(image_data))
        image_format = image.format.lower().replace("jpeg", "jpg")
        payload["Links"] = [
            {
                "DataId": product.plu_code,
                "LinkNumber": 95,
                "Type": {
                    "Description": "Article",
                    "Id": 2,
                },
            }
        ]
        payload["OriginalInput"] = product.image_1920.decode("utf-8")
        payload["Names"] = [
            {
                "DataId": 1,
                "Reference": "Nederlands",
                "Name": image_name,
            }
        ]
        payload["InputFormat"] = image_format
        return json.dumps(payload)

    @classmethod
    def transform_product_category_to_payload(cls, product_category):
        payload = {
            "DataId": product_category.external_digi_id,
            "DepartmentId": 97,
            "Names": [
                {
                    "Reference": "Nederlands",
                    "Name": product_category.name,
                }
            ],
        }
        return json.dumps(payload)

    @classmethod
    def transform_product_origin_to_payload(cls, product_origin):
        payload = {
            "DataId": product_origin.external_digi_id,
            "Names": [
                {
                    "Reference": "Nederlands",
                    "DdData": f"02000000<span style='font-family:\"DejaVu Sans\";font-size:24px;'>"
                    f"Herkomst:"
                    f"<\/~02000000span><b><span~02000000style='font-family:\"DIN\";font-size:36px;'>"
                    f"{product_origin.description}"
                    f"<\/span><\/b>",
                    "Name": f"Herkomst {product_origin.description}",
                }
            ],
        }

        return json.dumps(payload)

    @classmethod
    def transform_product_quality_to_image_payload(cls, product):
        product_quality = product.product_quality_id
        image_name = product_quality.name.lower().replace(" ", "_")
        payload = {"DataId": product_quality.digi_image_id}
        image_data = base64.b64decode(product_quality.image)
        image = Image.open(io.BytesIO(image_data))
        image_format = image.format.lower().replace("jpeg", "jpg")
        payload["OriginalInput"] = product_quality.image.decode("utf-8")
        payload["Names"] = [
            {
                "DataId": 1,
                "Reference": "Nederlands",
                "Name": image_name,
            }
        ]
        payload["Links"] = [
            {
                "DataId": product.plu_code,
                "LinkNumber": 1,
                "Type": {
                    "Description": "Article",
                    "Id": 2,
                },
            }
        ]
        payload["InputFormat"] = image_format
        return json.dumps(payload)

