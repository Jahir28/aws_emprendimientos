"""Punto de entrada de la Lambda Clientes."""

import json
import logging

from responses import bad_request, internal_error, not_found
from service import (
    create_client,
    delete_client,
    get_client,
    list_clients,
    update_client,
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

    if path == "/clientes":
        return f"{method} /clientes"

    if path.startswith("/clientes/"):
        return f"{method} /clientes/{{id}}"

    return f"{method} {path}"


def _get_client_id(event):
    """Extrae el ID publico de la ruta y lo mapea al ID interno del cliente."""
    path_parameters = event.get("pathParameters") or {}
    return path_parameters.get("id") or path_parameters.get("cliente_id")


def handler(event, context):
    """Procesa eventos de API Gateway HTTP API y delega al servicio."""
    try:
        method, path = _get_method_and_path(event)
        if not method or not path:
            return bad_request("El evento no contiene metodo HTTP o ruta.")

        route_key = _get_route_key(event, method, path)
        client_id = _get_client_id(event)

        body = {}
        if event.get("body"):
            body = json.loads(event["body"])
            if not isinstance(body, dict):
                return bad_request("El cuerpo JSON debe ser un objeto.")

        if route_key == "GET /clientes":
            return list_clients()

        if route_key == "POST /clientes":
            return create_client(body)

        if route_key == "GET /clientes/{id}":
            if not client_id:
                return bad_request("El ID del cliente es obligatorio.")
            return get_client(client_id)

        if route_key == "PUT /clientes/{id}":
            if not client_id:
                return bad_request("El ID del cliente es obligatorio.")
            return update_client(client_id, body)

        if route_key == "DELETE /clientes/{id}":
            if not client_id:
                return bad_request("El ID del cliente es obligatorio.")
            return delete_client(client_id)

        return not_found("Ruta no encontrada.")
    except json.JSONDecodeError:
        return bad_request("El cuerpo de la solicitud no contiene JSON valido.")
    except Exception:
        logger.exception("Error inesperado al procesar la solicitud de Clientes.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")

