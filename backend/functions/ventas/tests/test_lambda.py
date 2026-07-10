"""Pruebas unitarias para la Lambda Ventas con DynamoDB mockeado."""

import json
import os
import sys
import types
import unittest
from decimal import Decimal


os.environ["VENTAS_TABLE"] = "aws-emprendimientos-dev-ventas"
os.environ["CLIENTES_TABLE"] = "aws-emprendimientos-dev-clientes"
os.environ["PRODUCTOS_TABLE"] = "aws-emprendimientos-dev-productos"


class FakeDynamoDBError(Exception):
    """Error compatible con el formato basico de botocore ClientError."""

    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class FakeDynamoDBTable:
    """Mock simple de una tabla DynamoDB para pruebas unitarias."""

    def __init__(self, key_name):
        self.key_name = key_name
        self.items = {}
        self.fail_next_put = False

    def reset(self):
        self.items = {}
        self.fail_next_put = False

    def fail_next_put_item(self):
        self.fail_next_put = True

    def scan(self, **kwargs):
        return {"Items": list(self.items.values())}

    def get_item(self, Key):
        item = self.items.get(Key[self.key_name])
        return {"Item": item} if item else {}

    def put_item(self, Item):
        if self.fail_next_put:
            self.fail_next_put = False
            raise RuntimeError("DynamoDB put_item mock error")
        self.items[Item[self.key_name]] = Item.copy()
        return {}

    def update_item(
        self,
        Key,
        UpdateExpression,
        ExpressionAttributeNames=None,
        ExpressionAttributeValues=None,
        ConditionExpression=None,
        ReturnValues=None,
    ):
        item_id = Key[self.key_name]
        if item_id not in self.items:
            raise FakeDynamoDBError("ConditionalCheckFailedException")

        item = self.items[item_id]
        stock_name = (ExpressionAttributeNames or {}).get("#stock")
        cantidad = (ExpressionAttributeValues or {}).get(":cantidad")

        if stock_name and "- :cantidad" in UpdateExpression:
            if item.get(stock_name, 0) < cantidad:
                raise FakeDynamoDBError("ConditionalCheckFailedException")
            item[stock_name] -= cantidad

        if stock_name and "+ :cantidad" in UpdateExpression:
            item[stock_name] += cantidad

        return {"Attributes": item.copy()}

    def delete_item(self, Key, ReturnValues):
        item = self.items.pop(Key[self.key_name], None)
        return {"Attributes": item} if item else {}


class FakeDynamoDBResource:
    """Mock del recurso DynamoDB de boto3 con varias tablas."""

    def __init__(self):
        self.tables = {
            os.environ["VENTAS_TABLE"]: FakeDynamoDBTable("venta_id"),
            os.environ["CLIENTES_TABLE"]: FakeDynamoDBTable("cliente_id"),
            os.environ["PRODUCTOS_TABLE"]: FakeDynamoDBTable("producto_id"),
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


def _ventas_table():
    return fake_resource.Table(os.environ["VENTAS_TABLE"])


def _clientes_table():
    return fake_resource.Table(os.environ["CLIENTES_TABLE"])


def _productos_table():
    return fake_resource.Table(os.environ["PRODUCTOS_TABLE"])


def _event(method, path, body=None, sale_id=None, route_key=None):
    """Construye eventos compatibles con API Gateway HTTP API v2."""
    event = {
        "version": "2.0",
        "routeKey": route_key or f"{method} {path}",
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": method,
            }
        },
        "pathParameters": {},
        "body": None,
        "isBase64Encoded": False,
    }

    if sale_id:
        event["pathParameters"] = {"id": sale_id}

    if body is not None:
        event["body"] = json.dumps(body)

    return event


def _raw_body_event(method, path, raw_body, sale_id=None):
    """Construye un evento con body sin serializar para casos invalidos."""
    event = _event(method, path, sale_id=sale_id)
    event["body"] = raw_body
    return event


def _seed_client(client_id="cli-001"):
    _clientes_table().items[client_id] = {
        "cliente_id": client_id,
        "nombre": "Ana Gomez",
    }


def _seed_product(product_id="prod-001", stock=10, price="12.50"):
    _productos_table().items[product_id] = {
        "producto_id": product_id,
        "nombre": "Cafe artesanal",
        "precio": Decimal(price),
        "stock": stock,
    }


def _seed_sale(sale_id="ven-001"):
    _ventas_table().items[sale_id] = {
        "venta_id": sale_id,
        "cliente_id": "cli-001",
        "producto_id": "prod-001",
        "cantidad": 2,
        "precio_unitario": Decimal("12.50"),
        "total": Decimal("25.00"),
        "cliente_nombre": "Ana Gomez",
        "producto_nombre": "Cafe artesanal",
        "fecha": "2026-07-10T00:00:00+00:00",
        "created_at": "2026-07-10T00:00:00+00:00",
    }


def _valid_payload(cantidad=2):
    return {
        "cliente_id": "cli-001",
        "producto_id": "prod-001",
        "cantidad": cantidad,
    }


class TestVentasLambda(unittest.TestCase):
    """Valida rutas CRUD, reglas de negocio y errores de DynamoDB."""

    def setUp(self):
        fake_resource.reset()

    def test_list_sales_empty_table(self):
        response = handler(_event("GET", "/ventas"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(body["data"], [])

    def test_create_valid_sale(self):
        _seed_client()
        _seed_product(stock=10)

        response = handler(_event("POST", "/ventas", _valid_payload()), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["data"]["cliente_id"], "cli-001")
        self.assertEqual(body["data"]["producto_id"], "prod-001")
        self.assertEqual(body["data"]["cantidad"], 2)
        self.assertIn(body["data"]["venta_id"], _ventas_table().items)

    def test_create_sale_calculates_total(self):
        _seed_client()
        _seed_product(stock=10, price="12.50")

        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=3)), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["data"]["precio_unitario"], 12.5)
        self.assertEqual(body["data"]["total"], 37.5)

    def test_get_sale_by_id(self):
        _seed_sale("ven-001")

        response = handler(
            _event("GET", "/ventas/ven-001", sale_id="ven-001", route_key="GET /ventas/{id}"),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["venta_id"], "ven-001")
        self.assertEqual(body["data"]["total"], 25)

    def test_delete_sale(self):
        _seed_sale("ven-001")

        response = handler(
            _event("DELETE", "/ventas/ven-001", sale_id="ven-001", route_key="DELETE /ventas/{id}"),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertTrue(body["data"]["deleted"])
        self.assertNotIn("ven-001", _ventas_table().items)

    def test_invalid_json_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/ventas", "{invalid-json"), None)

        self.assertEqual(response["statusCode"], 400)

    def test_non_object_json_body_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/ventas", '["no", "objeto"]'), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_client_id_returns_bad_request(self):
        payload = {"producto_id": "prod-001", "cantidad": 2}

        response = handler(_event("POST", "/ventas", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_product_id_returns_bad_request(self):
        payload = {"cliente_id": "cli-001", "cantidad": 2}

        response = handler(_event("POST", "/ventas", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_quantity_returns_bad_request(self):
        payload = {"cliente_id": "cli-001", "producto_id": "prod-001"}

        response = handler(_event("POST", "/ventas", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_zero_quantity_returns_bad_request(self):
        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=0)), None)

        self.assertEqual(response["statusCode"], 400)

    def test_negative_quantity_returns_bad_request(self):
        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=-1)), None)

        self.assertEqual(response["statusCode"], 400)

    def test_non_integer_quantity_returns_bad_request(self):
        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=1.5)), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_client_returns_not_found(self):
        _seed_product(stock=10)

        response = handler(_event("POST", "/ventas", _valid_payload()), None)

        self.assertEqual(response["statusCode"], 404)

    def test_missing_product_returns_not_found(self):
        _seed_client()

        response = handler(_event("POST", "/ventas", _valid_payload()), None)

        self.assertEqual(response["statusCode"], 404)

    def test_insufficient_stock_returns_bad_request(self):
        _seed_client()
        _seed_product(stock=1)

        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=2)), None)

        self.assertEqual(response["statusCode"], 400)

    def test_stock_is_discounted_correctly(self):
        _seed_client()
        _seed_product(stock=10)

        response = handler(_event("POST", "/ventas", _valid_payload(cantidad=4)), None)

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(_productos_table().items["prod-001"]["stock"], 6)

    def test_internal_fields_return_bad_request(self):
        payload = _valid_payload()
        payload["total"] = 99

        response = handler(_event("POST", "/ventas", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_sale_returns_not_found(self):
        response = handler(
            _event("GET", "/ventas/no-existe", sale_id="no-existe", route_key="GET /ventas/{id}"),
            None,
        )

        self.assertEqual(response["statusCode"], 404)

    def test_event_without_method_returns_bad_request(self):
        event = _event("GET", "/ventas")
        event["requestContext"]["http"].pop("method")

        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_path_returns_bad_request(self):
        event = _event("GET", "/ventas")
        event.pop("rawPath")

        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_sale_save_error_restores_stock(self):
        _seed_client()
        _seed_product(stock=10)
        _ventas_table().fail_next_put_item()

        with self.assertLogs("service", level="ERROR"):
            response = handler(_event("POST", "/ventas", _valid_payload(cantidad=3)), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(body["message"], "Ocurrio un error interno al procesar la solicitud.")
        self.assertEqual(_productos_table().items["prod-001"]["stock"], 10)
        self.assertEqual(_ventas_table().items, {})


if __name__ == "__main__":
    unittest.main()

