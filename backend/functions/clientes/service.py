"""Servicio para operaciones CRUD de Clientes en DynamoDB."""

import logging
import os
import re
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import boto3

from models import Client
from responses import bad_request, created, internal_error, not_found, success

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CLIENTES_TABLE = os.environ["CLIENTES_TABLE"]
dynamodb = boto3.resource("dynamodb")
clientes_table = dynamodb.Table(CLIENTES_TABLE)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
READ_ONLY_FIELDS = {"cliente_id", "created_at", "updated_at"}


def _current_timestamp():
    """Genera una fecha ISO 8601 en UTC."""
    return datetime.now(timezone.utc).isoformat()


def _is_blank(value):
    """Indica si un valor string esta vacio o solo tiene espacios."""
    return isinstance(value, str) and not value.strip()


def _validate_text_field(payload, field_name, required=False):
    """Valida campos de texto obligatorios u opcionales."""
    if field_name not in payload:
        if required:
            return None, f"El campo {field_name} es obligatorio."
        return None, None

    value = payload[field_name]
    if not isinstance(value, str) or _is_blank(value):
        if required:
            return None, f"El campo {field_name} es obligatorio."
        return None, f"El campo {field_name} debe ser texto no vacio."

    return value.strip(), None


def _validate_email(value):
    """Valida formato basico de correo electronico."""
    if not EMAIL_PATTERN.match(value):
        return "El campo correo debe tener un formato valido."
    return None


def _validate_client_payload(payload, require_required_fields):
    """Valida datos de entrada para crear o actualizar clientes."""
    forbidden_fields = sorted(READ_ONLY_FIELDS.intersection(payload))
    if forbidden_fields:
        return None, "No se permite actualizar campos internos del cliente."

    normalized = {}

    nombre, error = _validate_text_field(payload, "nombre", require_required_fields)
    if error:
        return None, error
    if nombre is not None:
        normalized["nombre"] = nombre

    correo, error = _validate_text_field(payload, "correo", require_required_fields)
    if error:
        return None, error
    if correo is not None:
        email_error = _validate_email(correo)
        if email_error:
            return None, email_error
        normalized["correo"] = correo

    for field_name in ("telefono", "direccion"):
        if field_name in payload:
            value = payload[field_name]
            if value is None:
                normalized[field_name] = ""
            elif isinstance(value, str):
                normalized[field_name] = value.strip()
            else:
                return None, f"El campo {field_name} debe ser texto."

    return normalized, None


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


def create_client(payload):
    """Crea un cliente en DynamoDB."""
    normalized, error = _validate_client_payload(payload, require_required_fields=True)
    if error:
        return bad_request(error)

    try:
        timestamp = _current_timestamp()
        client = Client(
            cliente_id=str(uuid4()),
            nombre=normalized["nombre"],
            correo=normalized["correo"],
            telefono=normalized.get("telefono", ""),
            direccion=normalized.get("direccion", ""),
            created_at=timestamp,
            updated_at=timestamp,
        )
        item = client.to_dict()

        clientes_table.put_item(Item=item)

        return created(_to_json_compatible(item), "Cliente creado correctamente.")
    except Exception:
        logger.exception("Error al crear cliente en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def get_client(client_id):
    """Consulta un cliente por ID en DynamoDB."""
    try:
        response = clientes_table.get_item(Key={"cliente_id": client_id})
        item = response.get("Item")
        if not item:
            return not_found("Cliente no encontrado.")

        return success(_to_json_compatible(item), "Cliente encontrado.")
    except Exception:
        logger.exception("Error al obtener cliente desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def list_clients():
    """Lista clientes usando Scan en DynamoDB."""
    try:
        items = []
        response = clientes_table.scan()
        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = clientes_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return success(_to_json_compatible(items), "Clientes listados correctamente.")
    except Exception:
        logger.exception("Error al listar clientes desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def update_client(client_id, payload):
    """Actualiza parcialmente un cliente en DynamoDB."""
    normalized, error = _validate_client_payload(payload, require_required_fields=False)
    if error:
        return bad_request(error)

    try:
        if not normalized:
            return bad_request("Debe enviar al menos un campo para actualizar.")

        normalized["updated_at"] = _current_timestamp()
        expression_names = {}
        expression_values = {}
        update_parts = []

        for index, (field_name, value) in enumerate(normalized.items()):
            name_key = f"#field{index}"
            value_key = f":value{index}"
            expression_names[name_key] = field_name
            expression_values[value_key] = value
            update_parts.append(f"{name_key} = {value_key}")

        response = clientes_table.update_item(
            Key={"cliente_id": client_id},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ConditionExpression="attribute_exists(cliente_id)",
            ReturnValues="ALL_NEW",
        )

        return success(
            _to_json_compatible(response.get("Attributes", {})),
            "Cliente actualizado correctamente.",
        )
    except Exception as exc:
        error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if error_code == "ConditionalCheckFailedException":
            return not_found("Cliente no encontrado.")

        logger.exception("Error al actualizar cliente en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def delete_client(client_id):
    """Elimina un cliente en DynamoDB."""
    try:
        response = clientes_table.delete_item(
            Key={"cliente_id": client_id},
            ReturnValues="ALL_OLD",
        )
        if not response.get("Attributes"):
            return not_found("Cliente no encontrado.")

        return success(
            {"cliente_id": client_id, "deleted": True},
            "Cliente eliminado correctamente.",
        )
    except Exception:
        logger.exception("Error al eliminar cliente en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")

