"""Utilidades para respuestas compatibles con API Gateway."""

import json


DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}


def _response(status_code, payload):
    """Construye la respuesta estandar para API Gateway."""
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS.copy(),
        "body": json.dumps(payload, ensure_ascii=False),
    }


def success(data=None, message="Operacion completada correctamente."):
    """Respuesta HTTP 200."""
    return _response(200, {"message": message, "data": data})


def created(data=None, message="Recurso creado correctamente."):
    """Respuesta HTTP 201."""
    return _response(201, {"message": message, "data": data})


def bad_request(message="Solicitud invalida."):
    """Respuesta HTTP 400."""
    return _response(400, {"message": message})


def not_found(message="Recurso no encontrado."):
    """Respuesta HTTP 404."""
    return _response(404, {"message": message})


def conflict(message="Conflicto con el estado actual del recurso."):
    """Respuesta HTTP 409."""
    return _response(409, {"message": message})


def internal_error(message="Error interno del servidor."):
    """Respuesta HTTP 500."""
    return _response(500, {"message": message})
