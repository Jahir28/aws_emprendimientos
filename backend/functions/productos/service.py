"""Servicio para operaciones CRUD de Productos en DynamoDB."""

import logging
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import boto3

from models import Product
from responses import bad_request, created, internal_error, not_found, success

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PRODUCTOS_TABLE = os.environ["PRODUCTOS_TABLE"]
dynamodb = boto3.resource("dynamodb")
productos_table = dynamodb.Table(PRODUCTOS_TABLE)


def _current_timestamp():
    """Genera una fecha ISO 8601 en UTC para auditoria de registros."""
    return datetime.now(timezone.utc).isoformat()


def _is_blank(value):
    """Indica si un valor string esta vacio o solo tiene espacios."""
    return isinstance(value, str) and not value.strip()


def _parse_non_negative_number(value, field_name):
    """Valida y convierte numeros mayores o iguales a cero."""
    if isinstance(value, bool):
        return None, f"El campo {field_name} debe ser numerico."

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"El campo {field_name} debe ser numerico."

    if number < 0:
        return None, f"El campo {field_name} debe ser mayor o igual a cero."

    return number, None


def _parse_non_negative_integer(value, field_name):
    """Valida y convierte enteros mayores o iguales a cero."""
    if isinstance(value, bool):
        return None, f"El campo {field_name} debe ser un entero."

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"El campo {field_name} debe ser un entero."

    if number != number.to_integral_value():
        return None, f"El campo {field_name} debe ser un entero."

    if number < 0:
        return None, f"El campo {field_name} debe ser mayor o igual a cero."

    return int(number), None


def _validate_product_payload(payload, require_name):
    """Valida datos de entrada para crear o actualizar productos."""
    if require_name and _is_blank(payload.get("nombre", "")):
        return None, "El campo nombre es obligatorio."

    normalized = {}

    if "nombre" in payload:
        if not isinstance(payload["nombre"], str) or _is_blank(payload["nombre"]):
            return None, "El campo nombre debe ser un texto no vacio."
        normalized["nombre"] = payload["nombre"].strip()

    if "precio" in payload:
        precio, error = _parse_non_negative_number(payload["precio"], "precio")
        if error:
            return None, error
        normalized["precio"] = precio

    if "stock" in payload:
        stock, error = _parse_non_negative_integer(payload["stock"], "stock")
        if error:
            return None, error
        normalized["stock"] = stock

    for field_name in ("descripcion", "categoria"):
        if field_name in payload:
            if not isinstance(payload[field_name], str):
                return None, f"El campo {field_name} debe ser texto."
            normalized[field_name] = payload[field_name]

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


def create_product(payload):
    """Crea un producto en DynamoDB."""
    normalized, error = _validate_product_payload(payload, require_name=True)
    if error:
        return bad_request(error)

    try:
        timestamp = _current_timestamp()
        product = Product(
            producto_id=str(uuid4()),
            nombre=normalized["nombre"],
            descripcion=normalized.get("descripcion", ""),
            precio=normalized.get("precio", Decimal("0")),
            stock=normalized.get("stock", 0),
            categoria=normalized.get("categoria", ""),
            created_at=timestamp,
            updated_at=timestamp,
        )
        item = product.to_dict()
        item["precio"] = normalized.get("precio", Decimal("0"))

        productos_table.put_item(Item=item)

        return created(_to_json_compatible(item), "Producto creado correctamente.")
    except Exception:
        logger.exception("Error al crear producto en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def get_product(product_id):
    """Consulta un producto por ID en DynamoDB."""
    try:
        response = productos_table.get_item(Key={"producto_id": product_id})
        item = response.get("Item")
        if not item:
            return not_found("Producto no encontrado.")

        return success(_to_json_compatible(item), "Producto encontrado.")
    except Exception:
        logger.exception("Error al obtener producto desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def list_products():
    """Lista productos usando Scan en DynamoDB."""
    try:
        items = []
        response = productos_table.scan()
        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = productos_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return success(_to_json_compatible(items), "Productos listados correctamente.")
    except Exception:
        logger.exception("Error al listar productos desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def update_product(product_id, payload):
    """Actualiza parcialmente un producto en DynamoDB."""
    normalized, error = _validate_product_payload(payload, require_name=False)
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

        response = productos_table.update_item(
            Key={"producto_id": product_id},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ConditionExpression="attribute_exists(producto_id)",
            ReturnValues="ALL_NEW",
        )

        return success(
            _to_json_compatible(response.get("Attributes", {})),
            "Producto actualizado correctamente.",
        )
    except Exception as exc:
        error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if error_code == "ConditionalCheckFailedException":
            return not_found("Producto no encontrado.")

        logger.exception("Error al actualizar producto en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def delete_product(product_id):
    """Elimina un producto en DynamoDB."""
    try:
        response = productos_table.delete_item(
            Key={"producto_id": product_id},
            ReturnValues="ALL_OLD",
        )
        if not response.get("Attributes"):
            return not_found("Producto no encontrado.")

        return success(
            {"producto_id": product_id, "deleted": True},
            "Producto eliminado correctamente.",
        )
    except Exception:
        logger.exception("Error al eliminar producto en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")
