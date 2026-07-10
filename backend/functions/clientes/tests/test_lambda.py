"""Pruebas unitarias para la Lambda Clientes con DynamoDB mockeado."""

import json
import os
import sys
import types
import unittest
from decimal import Decimal


os.environ["CLIENTES_TABLE"] = "aws-emprendimientos-dev-clientes"


class FakeDynamoDBError(Exception):
    """Error compatible con el formato basico de botocore ClientError."""

    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class FakeDynamoDBTable:
    """Mock simple de una tabla DynamoDB para pruebas unitarias."""

    def __init__(self):
        self.items = {}
        self.fail_next_operation = False

    def reset(self):
        self.items = {}
        self.fail_next_operation = False

    def fail_next(self):
        self.fail_next_operation = True

    def _raise_if_needed(self):
        if self.fail_next_operation:
            self.fail_next_operation = False
            raise RuntimeError("DynamoDB mock error")

    def scan(self, **kwargs):
        self._raise_if_needed()
        return {"Items": list(self.items.values())}

    def get_item(self, Key):
        self._raise_if_needed()
        item = self.items.get(Key["cliente_id"])
        return {"Item": item} if item else {}

    def put_item(self, Item):
        self._raise_if_needed()
        self.items[Item["cliente_id"]] = Item.copy()
        return {}

    def update_item(
        self,
        Key,
        UpdateExpression,
        ExpressionAttributeNames,
        ExpressionAttributeValues,
        ConditionExpression,
        ReturnValues,
    ):
        self._raise_if_needed()
        client_id = Key["cliente_id"]
        if client_id not in self.items:
            raise FakeDynamoDBError("ConditionalCheckFailedException")

        item = self.items[client_id]
        for name_key, field_name in ExpressionAttributeNames.items():
            index = name_key.replace("#field", "")
            item[field_name] = ExpressionAttributeValues[f":value{index}"]

        return {"Attributes": item.copy()}

    def delete_item(self, Key, ReturnValues):
        self._raise_if_needed()
        item = self.items.pop(Key["cliente_id"], None)
        return {"Attributes": item} if item else {}


class FakeDynamoDBResource:
    """Mock del recurso DynamoDB de boto3."""

    def __init__(self):
        self.table = FakeDynamoDBTable()
        self.table_name = None

    def Table(self, table_name):
        self.table_name = table_name
        return self.table


fake_resource = FakeDynamoDBResource()
fake_boto3 = types.SimpleNamespace(resource=lambda service_name: fake_resource)
sys.modules["boto3"] = fake_boto3

from lambda_function import handler  # noqa: E402


def _event(method, path, body=None, client_id=None, route_key=None):
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

    if client_id:
        event["pathParameters"] = {"id": client_id}

    if body is not None:
        event["body"] = json.dumps(body)

    return event


def _rest_event(method, path, body=None, client_id=None):
    """Construye eventos compatibles con API Gateway REST API v1."""
    event = {
        "httpMethod": method,
        "path": path,
        "pathParameters": {},
        "body": None,
        "isBase64Encoded": False,
    }

    if client_id:
        event["pathParameters"] = {"id": client_id}

    if body is not None:
        event["body"] = json.dumps(body)

    return event


def _raw_body_event(method, path, raw_body, client_id=None):
    """Construye un evento con body sin serializar para casos invalidos."""
    event = _event(method, path, client_id=client_id)
    event["body"] = raw_body
    return event


def _seed_client(client_id="cli-001"):
    """Agrega un cliente directamente al mock de DynamoDB."""
    fake_resource.table.items[client_id] = {
        "cliente_id": client_id,
        "nombre": "Ana Gomez",
        "correo": "ana@example.com",
        "telefono": "555-0101",
        "direccion": "Ciudad de Panama",
        "compras": Decimal("2"),
        "created_at": "2026-07-10T00:00:00+00:00",
        "updated_at": "2026-07-10T00:00:00+00:00",
    }


class TestClientesLambda(unittest.TestCase):
    """Valida rutas CRUD, validaciones y errores de DynamoDB."""

    def setUp(self):
        fake_resource.table.reset()

    def test_uses_clientes_table_environment_variable(self):
        self.assertEqual(fake_resource.table_name, "aws-emprendimientos-dev-clientes")

    def test_list_clients_empty_table(self):
        response = handler(_event("GET", "/clientes"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(body["data"], [])

    def test_list_clients_rest_api_v1(self):
        response = handler(_rest_event("GET", "/clientes"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"], [])

    def test_create_valid_client(self):
        payload = {
            "nombre": "Ana Gomez",
            "correo": "ana@example.com",
            "telefono": "555-0101",
            "direccion": "Ciudad de Panama",
        }

        response = handler(_event("POST", "/clientes", payload), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["data"]["nombre"], "Ana Gomez")
        self.assertEqual(body["data"]["correo"], "ana@example.com")
        self.assertIn(body["data"]["cliente_id"], fake_resource.table.items)

    def test_get_client_by_id(self):
        _seed_client("cli-001")

        response = handler(
            _event("GET", "/clientes/cli-001", client_id="cli-001", route_key="GET /clientes/{id}"),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["cliente_id"], "cli-001")
        self.assertEqual(body["data"]["compras"], 2)

    def test_update_client_partially(self):
        _seed_client("cli-001")

        response = handler(
            _event(
                "PUT",
                "/clientes/cli-001",
                {"telefono": "555-9999"},
                "cli-001",
                "PUT /clientes/{id}",
            ),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["cliente_id"], "cli-001")
        self.assertEqual(body["data"]["telefono"], "555-9999")
        self.assertEqual(body["data"]["nombre"], "Ana Gomez")

    def test_delete_client(self):
        _seed_client("cli-001")

        response = handler(
            _event("DELETE", "/clientes/cli-001", client_id="cli-001", route_key="DELETE /clientes/{id}"),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertTrue(body["data"]["deleted"])
        self.assertNotIn("cli-001", fake_resource.table.items)

    def test_invalid_json_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/clientes", "{invalid-json"), None)

        self.assertEqual(response["statusCode"], 400)

    def test_non_object_json_body_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/clientes", '["no", "objeto"]'), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_name_returns_bad_request(self):
        response = handler(_event("POST", "/clientes", {"correo": "ana@example.com"}), None)

        self.assertEqual(response["statusCode"], 400)

    def test_missing_email_returns_bad_request(self):
        response = handler(_event("POST", "/clientes", {"nombre": "Ana Gomez"}), None)

        self.assertEqual(response["statusCode"], 400)

    def test_invalid_email_returns_bad_request(self):
        payload = {
            "nombre": "Ana Gomez",
            "correo": "correo-invalido",
        }

        response = handler(_event("POST", "/clientes", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_read_only_fields_cannot_be_updated(self):
        _seed_client("cli-001")

        response = handler(
            _event("PUT", "/clientes/cli-001", {"cliente_id": "otro"}, "cli-001", "PUT /clientes/{id}"),
            None,
        )

        self.assertEqual(response["statusCode"], 400)

    def test_missing_client_returns_not_found(self):
        response = handler(
            _event("GET", "/clientes/no-existe", client_id="no-existe", route_key="GET /clientes/{id}"),
            None,
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(body["message"], "Cliente no encontrado.")

    def test_missing_id_for_id_route_returns_bad_request(self):
        response = handler(_event("GET", "/clientes/cli-001", route_key="GET /clientes/{id}"), None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_method_returns_bad_request(self):
        event = _event("GET", "/clientes")
        event["requestContext"]["http"].pop("method")
        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_path_returns_bad_request(self):
        event = _event("GET", "/clientes")
        event.pop("rawPath")
        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_unknown_route_returns_not_found(self):
        response = handler(_event("GET", "/desconocida", route_key="GET /desconocida"), None)

        self.assertEqual(response["statusCode"], 404)

    def test_dynamodb_internal_error_returns_500(self):
        fake_resource.table.fail_next()

        with self.assertLogs("service", level="ERROR"):
            response = handler(_event("GET", "/clientes"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(body["message"], "Ocurrio un error interno al procesar la solicitud.")


if __name__ == "__main__":
    unittest.main()

