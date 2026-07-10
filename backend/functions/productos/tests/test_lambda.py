"""Pruebas unitarias para la Lambda Productos."""

import json
import unittest

from lambda_function import handler


def _event(method, path, body=None, product_id=None):
    """Construye eventos compatibles con API Gateway HTTP API."""
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": method,
                "path": path,
            }
        },
        "pathParameters": {},
        "body": None,
        "isBase64Encoded": False,
    }

    if product_id:
        event["pathParameters"] = {"producto_id": product_id}

    if body is not None:
        event["body"] = json.dumps(body)

    return event


def _raw_body_event(method, path, raw_body, product_id=None):
    """Construye un evento con body sin serializar para casos invalidos."""
    event = _event(method, path, product_id=product_id)
    event["body"] = raw_body
    return event


class TestProductosLambda(unittest.TestCase):
    """Valida rutas CRUD y respuestas HTTP principales."""

    def test_get_list_products(self):
        response = handler(_event("GET", "/productos"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertIsInstance(body["data"], list)

    def test_get_product_by_id(self):
        response = handler(_event("GET", "/productos/prod-001", product_id="prod-001"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["producto_id"], "prod-001")

    def test_post_create_product(self):
        payload = {
            "nombre": "Mermelada artesanal",
            "descripcion": "Producto local de ejemplo.",
            "precio": 4.75,
            "stock": 10,
            "categoria": "Alimentos",
        }
        response = handler(_event("POST", "/productos", payload), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 201)
        self.assertEqual(body["data"]["nombre"], "Mermelada artesanal")

    def test_post_rejects_missing_name(self):
        response = handler(_event("POST", "/productos", {"precio": 4.75}), None)

        self.assertEqual(response["statusCode"], 400)

    def test_post_rejects_negative_price(self):
        payload = {
            "nombre": "Mermelada artesanal",
            "precio": -1,
            "stock": 10,
        }
        response = handler(_event("POST", "/productos", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_post_rejects_negative_stock(self):
        payload = {
            "nombre": "Mermelada artesanal",
            "precio": 4.75,
            "stock": -3,
        }
        response = handler(_event("POST", "/productos", payload), None)

        self.assertEqual(response["statusCode"], 400)

    def test_put_update_product(self):
        payload = {
            "nombre": "Cafe premium",
            "precio": 15.0,
            "stock": 8,
        }
        response = handler(_event("PUT", "/productos/prod-001", payload, "prod-001"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["producto_id"], "prod-001")
        self.assertEqual(body["data"]["nombre"], "Cafe premium")

    def test_put_accepts_valid_partial_update(self):
        response = handler(_event("PUT", "/productos/prod-001", {"stock": 3}, "prod-001"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["data"]["producto_id"], "prod-001")
        self.assertEqual(body["data"]["stock"], 3)
        self.assertEqual(body["data"]["nombre"], "Cafe artesanal")

    def test_delete_product(self):
        response = handler(_event("DELETE", "/productos/prod-001", product_id="prod-001"), None)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertTrue(body["data"]["deleted"])

    def test_unknown_route_returns_not_found(self):
        response = handler(_event("GET", "/no-existe"), None)

        self.assertEqual(response["statusCode"], 404)

    def test_invalid_json_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/productos", "{invalid-json"), None)

        self.assertEqual(response["statusCode"], 400)

    def test_non_object_json_body_returns_bad_request(self):
        response = handler(_raw_body_event("POST", "/productos", '["no", "objeto"]'), None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_method_returns_bad_request(self):
        event = _event("GET", "/productos")
        event["requestContext"]["http"].pop("method")
        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)

    def test_event_without_path_returns_bad_request(self):
        event = _event("GET", "/productos")
        event["requestContext"]["http"].pop("path")
        response = handler(event, None)

        self.assertEqual(response["statusCode"], 400)


if __name__ == "__main__":
    unittest.main()
