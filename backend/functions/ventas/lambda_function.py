"""Punto de entrada de la Lambda Ventas."""

import json
import logging

from responses import bad_request, internal_error, not_found
from service import create_sale, delete_sale, get_sale, list_sales

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _get_method_and_path(event):
    """Extrae metodo y ruta desde API Gateway HTTP API v2 o REST API v1."""
    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})

    method = http_context.get("method")
    path = event.get("rawPath")

    if not method:
        method = event.get("httpMethod")

    if not path:
        path = event.get("path")

    return (method or "").upper(), path or ""


def _get_route_key(event, method, path):
    """Obtiene la ruta declarada por API Gateway o la infiere para REST API."""
    route_key = event.get("routeKey")
    if route_key:
        return route_key

    if path == "/ventas":
        return f"{method} /ventas"

    if path.startswith("/ventas/"):
        return f"{method} /ventas/{{id}}"

    return f"{method} {path}"


def _get_sale_id(event):
    """Extrae el ID publico de la ruta y lo mapea al ID interno de la venta."""
    path_parameters = event.get("pathParameters") or {}
    return path_parameters.get("id") or path_parameters.get("venta_id")


def handler(event, context):
    """Procesa eventos de API Gateway HTTP API y delega al servicio."""
    try:
        method, path = _get_method_and_path(event)
        if not method or not path:
            return bad_request("El evento no contiene metodo HTTP o ruta.")

        route_key = _get_route_key(event, method, path)
        sale_id = _get_sale_id(event)

        body = {}
        if event.get("body"):
            body = json.loads(event["body"])
            if not isinstance(body, dict):
                return bad_request("El cuerpo JSON debe ser un objeto.")

        if route_key == "GET /ventas":
            return list_sales()

        if route_key == "POST /ventas":
            return create_sale(body)

        if route_key == "GET /ventas/{id}":
            if not sale_id:
                return bad_request("El ID de la venta es obligatorio.")
            return get_sale(sale_id)

        if route_key == "DELETE /ventas/{id}":
            if not sale_id:
                return bad_request("El ID de la venta es obligatorio.")
            return delete_sale(sale_id)

        return not_found("Ruta no encontrada.")
    except json.JSONDecodeError:
        return bad_request("El cuerpo de la solicitud no contiene JSON valido.")
    except Exception:
        logger.exception("Error inesperado al procesar la solicitud de Ventas.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")

