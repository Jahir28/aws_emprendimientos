"""Punto de entrada de la Lambda Reportes."""

import logging

from responses import bad_request, internal_error, not_found
from service import (
    get_frequent_clients_report,
    get_summary_report,
    get_top_products_report,
)

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

    return f"{method} {path}"


def handler(event, context):
    """Procesa eventos de API Gateway HTTP API y delega al servicio."""
    try:
        method, path = _get_method_and_path(event)
        if not method or not path:
            return bad_request("El evento no contiene metodo HTTP o ruta.")

        route_key = _get_route_key(event, method, path)

        if route_key == "GET /reportes/resumen":
            return get_summary_report()

        if route_key == "GET /reportes/productos-mas-vendidos":
            return get_top_products_report()

        if route_key == "GET /reportes/clientes-frecuentes":
            return get_frequent_clients_report()

        return not_found("Ruta no encontrada.")
    except Exception:
        logger.exception("Error inesperado al procesar la solicitud de Reportes.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")

