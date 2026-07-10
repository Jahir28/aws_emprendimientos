"""Pruebas unitarias para la Lambda Reportes con DynamoDB mockeado."""

import json
import os
import sys
import types
import unittest
from decimal import Decimal


os.environ["PRODUCTOS_TABLE"] = "aws-emprendimientos-dev-productos"
os.environ["CLIENTES_TABLE"] = "aws-emprendimientos-dev-clientes"
os.environ["VENTAS_TABLE"] = "aws-emprendimientos-dev-ventas"


class FakeDynamoDBTable:
    """Mock simple de una tabla DynamoDB con soporte de paginacion."""

    def __init__(self):
        self.items = []
        self.pages = None
        self.fail_scan = False
        self.scan_calls = 0

    def reset(self):
        self.items = []
        self.pages = None
        self.fail_scan = False
        self.scan_calls = 0

    def set_pages(self, pages):
        self.pages = pages

    def scan(self, **kwargs):
        self.scan_calls += 1
        if self.fail_scan:
            raise RuntimeError("DynamoDB scan mock error")

        if self.pages is None:
            return {"Items": self.items}

        page_index = int((kwargs.get("ExclusiveStartKey") or {}).get("page", 0))
        response = {"Items": self.pages[page_index]}
        if page_index + 1 < len(self.pages):
            response["LastEvaluatedKey"] = {"page": page_index + 1}
        return response


class FakeDynamoDBResource:
    """Mock del recurso DynamoDB de boto3 con varias tablas."""

    def __init__(self):
        self.tables = {
            os.environ["PRODUCTOS_TABLE"]: FakeDynamoDBTable(),
            os.environ["CLIENTES_TABLE"]: FakeDynamoDBTable(),
            os.environ["VENTAS_TABLE"]: FakeDynamoDBTable(),
        }

    def reset(self):
        for table in self.tables.values():
            table.reset()

    def Table(self, table_name):
        return self.tables[table_name]


fake_resource = FakeDynamoDBResource()
fake_boto3 = types.SimpleNamespace(resource=lambda service_name: fake_resource)
sys.modules["boto3"] = fake_boto3

from lambda_function import handler  # noqa: E402


def _productos_table():
    return fake_resource.Table(os.environ["PRODUCTOS_TABLE"])


def _clientes_table():
    return fake_resource.Table(os.environ["CLIENTES_TABLE"])


def _ventas_table():
    return fake_resource.Table(os.environ["VENTAS_TABLE"])


def _event(method, path, route_key=None):
    """Construye eventos compatibles con API Gateway HTTP API v2."""
    return {
        "version": "2.0",
        "routeKey": route_key or f"{method} {path}",
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": method,
            }
        },
        "isBase64Encoded": False,
    }


def _rest_event(method, path):
    """Construye eventos compatibles con API Gateway REST API v1."""
    return {
        "httpMethod": method,
        "path": path,
        "isBase64Encoded": False,
    }


def _seed_summary_data():
    _productos_table().items = [
        {"producto_id": "prod-1", "nombre": "Cafe", "precio": Decimal("10"), "stock": 3},
        {"producto_id": "prod-2", "nombre": "Te", "precio": Decimal("5.50"), "stock": 8},
    ]
    _clientes_table().items = [
        {"cliente_id": "cli-1", "nombre": "Ana"},
        {"cliente_id": "cli-2", "nombre": "Luis"},
    ]
    _ventas_table().items = [
        {
            "venta_id": "ven-1",
            "producto_id": "prod-1",
            "producto_nombre": "Cafe",
            "cliente_id": "cli-1",
            "cliente_nombre": "Ana",
            "cantidad": 2,
            "total": Decimal("20"),
        },
        {
            "venta_id": "ven-2",
            "producto_id": "prod-2",
            "producto_nombre": "Te",
            "cliente_id": "cli-2",
            "cliente_nombre": "Luis",
            "cantidad": 4,
            "total": Decimal("22"),
        },
    ]


class TestReportesLambda(unittest.TestCase):
    """Valida calculos, rutas y errores de Reportes."""

    def setUp(self):
        fake_resource.reset()

    def test_summary_with_data(self):
        _seed_summary_data()

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["message"], "Reporte generado correctamente.")
        self.assertEqual(body["data"]["total_productos"], 2)
        self.assertEqual(body["data"]["total_clientes"], 2)
        self.assertEqual(body["data"]["total_ventas"], 2)

    def test_summary_with_empty_tables(self):
        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            body["data"],
            {
                "total_productos": 0,
                "total_clientes": 0,
                "total_ventas": 0,
                "ingresos_totales": 0,
                "unidades_vendidas": 0,
                "productos_bajo_stock": 0,
                "valor_inventario": 0,
            },
        )

    def test_summary_calculates_total_income(self):
        _seed_summary_data()

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(body["data"]["ingresos_totales"], 42)

    def test_summary_calculates_units_sold(self):
        _seed_summary_data()

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(body["data"]["unidades_vendidas"], 6)

    def test_summary_calculates_low_stock_products(self):
        _seed_summary_data()

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(body["data"]["productos_bajo_stock"], 1)

    def test_summary_calculates_inventory_value(self):
        _seed_summary_data()

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(body["data"]["valor_inventario"], 74)

    def test_top_products_report(self):
        _ventas_table().items = [
            {"producto_id": "prod-1", "producto_nombre": "Cafe", "cantidad": 2, "total": Decimal("20")},
            {"producto_id": "prod-1", "producto_nombre": "Cafe", "cantidad": 3, "total": Decimal("30")},
            {"producto_id": "prod-2", "producto_nombre": "Te", "cantidad": 1, "total": Decimal("5")},
        ]

        response = handler(_event("GET", "/reportes/productos-mas-vendidos"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"][0]["producto_id"], "prod-1")
        self.assertEqual(body["data"][0]["cantidad_vendida"], 5)
        self.assertEqual(body["data"][0]["ingresos"], 50)

    def test_top_products_descending_order(self):
        _ventas_table().items = [
            {"producto_id": "prod-1", "producto_nombre": "Cafe", "cantidad": 1, "total": Decimal("10")},
            {"producto_id": "prod-2", "producto_nombre": "Te", "cantidad": 4, "total": Decimal("20")},
        ]

        response = handler(_event("GET", "/reportes/productos-mas-vendidos"), None)
        body = json.loads(response["body"])

        self.assertEqual([item["producto_id"] for item in body["data"]], ["prod-2", "prod-1"])

    def test_top_products_limit_10(self):
        _ventas_table().items = [
            {
                "producto_id": f"prod-{index}",
                "producto_nombre": f"Producto {index}",
                "cantidad": index,
                "total": Decimal(index),
            }
            for index in range(1, 13)
        ]

        response = handler(_event("GET", "/reportes/productos-mas-vendidos"), None)
        body = json.loads(response["body"])

        self.assertEqual(len(body["data"]), 10)
        self.assertEqual(body["data"][0]["producto_id"], "prod-12")

    def test_frequent_clients_report(self):
        _ventas_table().items = [
            {"cliente_id": "cli-1", "cliente_nombre": "Ana", "total": Decimal("20")},
            {"cliente_id": "cli-1", "cliente_nombre": "Ana", "total": Decimal("30")},
            {"cliente_id": "cli-2", "cliente_nombre": "Luis", "total": Decimal("15")},
        ]

        response = handler(_event("GET", "/reportes/clientes-frecuentes"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"][0]["cliente_id"], "cli-1")
        self.assertEqual(body["data"][0]["cantidad_ventas"], 2)
        self.assertEqual(body["data"][0]["total_gastado"], 50)

    def test_frequent_clients_descending_order(self):
        _ventas_table().items = [
            {"cliente_id": "cli-1", "cliente_nombre": "Ana", "total": Decimal("20")},
            {"cliente_id": "cli-2", "cliente_nombre": "Luis", "total": Decimal("80")},
        ]

        response = handler(_event("GET", "/reportes/clientes-frecuentes"), None)
        body = json.loads(response["body"])

        self.assertEqual([item["cliente_id"] for item in body["data"]], ["cli-2", "cli-1"])

    def test_frequent_clients_limit_10(self):
        _ventas_table().items = [
            {
                "cliente_id": f"cli-{index}",
                "cliente_nombre": f"Cliente {index}",
                "total": Decimal(index),
            }
            for index in range(1, 13)
        ]

        response = handler(_event("GET", "/reportes/clientes-frecuentes"), None)
        body = json.loads(response["body"])

        self.assertEqual(len(body["data"]), 10)
        self.assertEqual(body["data"][0]["cliente_id"], "cli-12")

    def test_scan_pagination(self):
        _ventas_table().set_pages(
            [
                [{"venta_id": "ven-1", "total": Decimal("5"), "cantidad": 1}],
                [{"venta_id": "ven-2", "total": Decimal("7"), "cantidad": 2}],
            ]
        )

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["total_ventas"], 2)
        self.assertEqual(_ventas_table().scan_calls, 2)

    def test_decimal_values_are_json_serializable(self):
        _productos_table().items = [
            {"producto_id": "prod-1", "precio": Decimal("2.50"), "stock": Decimal("2")}
        ]

        response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["valor_inventario"], 5)

    def test_unknown_route_returns_not_found(self):
        response = handler(_event("GET", "/reportes/no-existe"), None)

        self.assertEqual(response["statusCode"], 404)

    def test_event_without_method_returns_bad_request(self):
        event = _event("GET", "/reportes/resumen")
        event["requestContext"]["http"].pop("method")

        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_path_returns_bad_request(self):
        event = _event("GET", "/reportes/resumen")
        event.pop("rawPath")

        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_internal_dynamodb_error_returns_500(self):
        _ventas_table().fail_scan = True

        with self.assertLogs("service", level="ERROR"):
            response = handler(_event("GET", "/reportes/resumen"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(body["message"], "Ocurrio un error interno al procesar la solicitud.")

    def test_rest_api_v1_route_is_supported(self):
        response = handler(_rest_event("GET", "/reportes/resumen"), None)

        self.assertEqual(response["statusCode"], 200)


if __name__ == "__main__":
    unittest.main()

