"""Pruebas unitarias para la Lambda Alertas con boto3 mockeado."""

import importlib
import json
import os
import sys
import unittest
from decimal import Decimal


class FakeDynamoDBTable:
    """Mock simple de una tabla DynamoDB con soporte de paginacion."""

    def __init__(self):
        self.pages = [{"Items": []}]
        self.scan_calls = []
        self.fail = False

    def reset(self):
        self.pages = [{"Items": []}]
        self.scan_calls = []
        self.fail = False

    def scan(self, **kwargs):
        self.scan_calls.append(kwargs)
        if self.fail:
            raise RuntimeError("DynamoDB mock error")

        page_index = len(self.scan_calls) - 1
        return self.pages[page_index]


class FakeDynamoDBResource:
    """Mock del recurso DynamoDB de boto3."""

    def __init__(self):
        self.table = FakeDynamoDBTable()
        self.table_names = []

    def Table(self, table_name):
        self.table_names.append(table_name)
        return self.table


class FakeSNSClient:
    """Mock del cliente SNS."""

    def __init__(self):
        self.publish_calls = []
        self.fail = False
        self.message_id = "sns-message-001"

    def reset(self):
        self.publish_calls = []
        self.fail = False
        self.message_id = "sns-message-001"

    def publish(self, **kwargs):
        self.publish_calls.append(kwargs)
        if self.fail:
            raise RuntimeError("SNS mock error")
        return {"MessageId": self.message_id}


class FakeBoto3:
    """Mock minimo de boto3 para inyectar recurso DynamoDB y cliente SNS."""

    def __init__(self):
        self.dynamodb = FakeDynamoDBResource()
        self.sns = FakeSNSClient()

    def resource(self, service_name):
        if service_name != "dynamodb":
            raise ValueError(f"Servicio no soportado: {service_name}")
        return self.dynamodb

    def client(self, service_name):
        if service_name != "sns":
            raise ValueError(f"Servicio no soportado: {service_name}")
        return self.sns


fake_boto3 = FakeBoto3()
sys.modules["boto3"] = fake_boto3

import lambda_function  # noqa: E402
import service  # noqa: E402


def _body(response):
    return json.loads(response["body"])


def _product(product_id, nombre, stock):
    return {
        "producto_id": product_id,
        "nombre": nombre,
        "stock": stock,
    }


class TestAlertasLambda(unittest.TestCase):
    """Valida generacion de alertas, paginacion, errores y conversion Decimal."""

    def setUp(self):
        os.environ["PRODUCTOS_TABLE"] = "aws-emprendimientos-dev-productos"
        os.environ["SNS_TOPIC_ARN"] = "arn:aws:sns:us-east-1:123456789012:alertas"
        os.environ.pop("STOCK_MINIMO", None)
        fake_boto3.dynamodb.table.reset()
        fake_boto3.dynamodb.table_names = []
        fake_boto3.sns.reset()
        importlib.reload(service)
        importlib.reload(lambda_function)

    def test_evento_valido_con_productos_de_bajo_stock(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", Decimal("2"))]}
        ]

        response = lambda_function.handler({"source": "aws.events"}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_revisados"], 1)
        self.assertEqual(body["data"]["productos_bajo_stock"], 1)
        self.assertTrue(body["data"]["notificacion_enviada"])
        self.assertEqual(body["data"]["message_id"], "sns-message-001")

    def test_evento_valido_sin_productos_de_bajo_stock(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", Decimal("8"))]}
        ]

        response = lambda_function.handler({"source": "aws.events"}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_revisados"], 1)
        self.assertEqual(body["data"]["productos_bajo_stock"], 0)
        self.assertFalse(body["data"]["notificacion_enviada"])
        self.assertEqual(fake_boto3.sns.publish_calls, [])

    def test_paginacion_de_dynamodb(self):
        fake_boto3.dynamodb.table.pages = [
            {
                "Items": [_product("prod-001", "Cafe", 10)],
                "LastEvaluatedKey": {"producto_id": "prod-001"},
            },
            {"Items": [_product("prod-002", "Miel", 1)]},
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(len(fake_boto3.dynamodb.table.scan_calls), 2)
        self.assertEqual(
            fake_boto3.dynamodb.table.scan_calls[1],
            {"ExclusiveStartKey": {"producto_id": "prod-001"}},
        )
        self.assertEqual(body["data"]["productos_revisados"], 2)
        self.assertEqual(body["data"]["productos_bajo_stock"], 1)

    def test_paginacion_con_multiples_paginas_vacias_y_con_datos(self):
        fake_boto3.dynamodb.table.pages = [
            {
                "Items": [],
                "LastEvaluatedKey": {"producto_id": "page-1"},
            },
            {
                "Items": [_product("prod-001", "Cafe", 8)],
                "LastEvaluatedKey": {"producto_id": "page-2"},
            },
            {"Items": [_product("prod-002", "Miel", 2)]},
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(len(fake_boto3.dynamodb.table.scan_calls), 3)
        self.assertEqual(body["data"]["productos_revisados"], 2)
        self.assertEqual(body["data"]["productos_bajo_stock"], 1)
        self.assertEqual(len(fake_boto3.sns.publish_calls), 1)

    def test_publicacion_correcta_en_sns(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe artesanal", 3)]}
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)
        publish_call = fake_boto3.sns.publish_calls[0]

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["message_id"], "sns-message-001")
        self.assertEqual(
            publish_call["TopicArn"],
            "arn:aws:sns:us-east-1:123456789012:alertas",
        )
        self.assertEqual(
            publish_call["Subject"],
            "Alerta de stock bajo - AWS Emprendimientos",
        )
        self.assertIn("Cafe artesanal", publish_call["Message"])
        self.assertIn("producto_id: prod-001", publish_call["Message"])
        self.assertIn("stock actual: 3", publish_call["Message"])
        self.assertIn("limite: 5", publish_call["Message"])

    def test_producto_con_stock_exactamente_igual_al_limite(self):
        os.environ["STOCK_MINIMO"] = "5"
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", Decimal("5"))]}
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_bajo_stock"], 1)
        self.assertTrue(body["data"]["notificacion_enviada"])

    def test_producto_con_stock_superior_al_limite(self):
        os.environ["STOCK_MINIMO"] = "5"
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", Decimal("6"))]}
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_bajo_stock"], 0)
        self.assertFalse(body["data"]["notificacion_enviada"])

    def test_stock_minimo_invalido(self):
        os.environ["STOCK_MINIMO"] = "5.5"

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("STOCK_MINIMO", body["message"])
        self.assertEqual(fake_boto3.dynamodb.table.scan_calls, [])
        self.assertEqual(fake_boto3.sns.publish_calls, [])

    def test_stock_minimo_negativo(self):
        os.environ["STOCK_MINIMO"] = "-1"

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("entero no negativo", body["message"])
        self.assertEqual(fake_boto3.dynamodb.table.scan_calls, [])
        self.assertEqual(fake_boto3.sns.publish_calls, [])

    def test_producto_sin_stock_se_trata_como_cero(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [{"producto_id": "prod-001", "nombre": "Cafe"}]}
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)
        publish_call = fake_boto3.sns.publish_calls[0]

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_revisados"], 1)
        self.assertEqual(body["data"]["productos_bajo_stock"], 1)
        self.assertIn("stock actual: 0", publish_call["Message"])

    def test_producto_sin_nombre_ni_producto_id_usa_valores_por_defecto(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [{"stock": 1}]}
        ]

        response = lambda_function.handler({}, None)
        publish_call = fake_boto3.sns.publish_calls[0]

        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Sin nombre", publish_call["Message"])
        self.assertIn("producto_id: Sin ID", publish_call["Message"])

    def test_variables_de_entorno_faltantes(self):
        os.environ.pop("PRODUCTOS_TABLE", None)

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("PRODUCTOS_TABLE", body["message"])
        self.assertEqual(fake_boto3.sns.publish_calls, [])

    def test_error_de_dynamodb(self):
        fake_boto3.dynamodb.table.fail = True

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error interno", body["message"].lower())
        self.assertEqual(fake_boto3.sns.publish_calls, [])

    def test_error_de_sns(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", 1)]}
        ]
        fake_boto3.sns.fail = True

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 500)
        self.assertIn("error interno", body["message"].lower())
        self.assertEqual(len(fake_boto3.sns.publish_calls), 1)

    def test_conversion_de_decimal_en_respuesta(self):
        fake_boto3.dynamodb.table.pages = [
            {"Items": [_product("prod-001", "Cafe", Decimal("6"))]}
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_revisados"], 1)
        self.assertEqual(body["data"]["productos_bajo_stock"], 0)

    def test_respuesta_con_cantidades_correctas(self):
        fake_boto3.dynamodb.table.pages = [
            {
                "Items": [
                    _product("prod-001", "Cafe", 1),
                    _product("prod-002", "Miel", 5),
                    _product("prod-003", "Chocolate", 9),
                ]
            }
        ]

        response = lambda_function.handler({}, None)
        body = _body(response)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["productos_revisados"], 3)
        self.assertEqual(body["data"]["productos_bajo_stock"], 2)
        self.assertTrue(body["data"]["notificacion_enviada"])


if __name__ == "__main__":
    unittest.main()
