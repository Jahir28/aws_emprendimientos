"""Utilidades para respuestas JSON de la Lambda Alertas."""

import json
from decimal import Decimal


DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}


def _to_json_compatible(value):
    """Convierte valores Decimal de DynamoDB a tipos compatibles con JSON."""
    if isinstance(value, list):
        return [_to_json_compatible(item) for item in value]

    if isinstance(value, dict):
        return {key: _to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    return value


def response(status_code, payload):
    """Construye una respuesta serializable como JSON."""
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS.copy(),
        "body": json.dumps(_to_json_compatible(payload), ensure_ascii=False),
    }


def success(data=None, message="Operacion completada correctamente."):
    """Respuesta HTTP 200."""
    return response(200, {"message": message, "data": data})


def bad_request(message="Solicitud invalida."):
    """Respuesta HTTP 400."""
    return response(400, {"message": message})


def internal_error(message="Error interno del servidor."):
    """Respuesta HTTP 500."""
    return response(500, {"message": message})
