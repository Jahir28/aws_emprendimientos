"""Punto de entrada de la Lambda Productos."""

import json
import logging

from responses import bad_request, internal_error, not_found
from service import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Procesa eventos de API Gateway HTTP API y delega al servicio."""
    try:
        request_context = event.get("requestContext", {})
        http_context = request_context.get("http", {})

        method = http_context.get("method", "").upper()
        path = http_context.get("path", "")
        if not method or not path:
            return bad_request("El evento no contiene metodo HTTP o ruta.")

        path_parameters = event.get("pathParameters") or {}
        product_id = path_parameters.get("producto_id")

        body = {}
        if event.get("body"):
            body = json.loads(event["body"])
            if not isinstance(body, dict):
                return bad_request("El cuerpo JSON debe ser un objeto.")

        if method == "GET" and product_id:
            return get_product(product_id)

        if method == "GET" and path.endswith("/productos"):
            return list_products()

        if method == "POST" and path.endswith("/productos"):
            return create_product(body)

        if method == "PUT" and product_id:
            return update_product(product_id, body)

        if method == "DELETE" and product_id:
            return delete_product(product_id)

        return not_found("Ruta no encontrada.")
    except json.JSONDecodeError:
        return bad_request("El cuerpo de la solicitud no contiene JSON valido.")
    except Exception:
        logger.exception("Error inesperado al procesar la solicitud de Productos.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")
