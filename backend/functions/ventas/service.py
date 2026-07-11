"""Servicio para operaciones CRUD de Ventas en DynamoDB."""

import logging
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import boto3

from models import Sale
from responses import bad_request, conflict, created, internal_error, not_found, success

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VENTAS_TABLE = os.environ["VENTAS_TABLE"]
CLIENTES_TABLE = os.environ["CLIENTES_TABLE"]
PRODUCTOS_TABLE = os.environ["PRODUCTOS_TABLE"]

dynamodb = boto3.resource("dynamodb")
ddb_client = boto3.client("dynamodb")
ventas_table = dynamodb.Table(VENTAS_TABLE)
clientes_table = dynamodb.Table(CLIENTES_TABLE)
productos_table = dynamodb.Table(PRODUCTOS_TABLE)

READ_ONLY_FIELDS = {
    "venta_id",
    "total",
    "precio_unitario",
    "estado",
    "fecha",
    "created_at",
    "updated_at",
    "anulada_at",
}
COMPLETED_STATUS = "completada"
CANCELED_STATUS = "anulada"


def _current_timestamp():
    """Genera una fecha ISO 8601 en UTC."""
    return datetime.now(timezone.utc).isoformat()


def _is_blank(value):
    """Indica si un valor string esta vacio o solo tiene espacios."""
    return isinstance(value, str) and not value.strip()


def _parse_positive_integer(value, field_name):
    """Valida y convierte enteros mayores que cero."""
    if isinstance(value, bool):
        return None, f"El campo {field_name} debe ser un entero."

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"El campo {field_name} debe ser un entero."

    if number != number.to_integral_value():
        return None, f"El campo {field_name} debe ser un entero."

    if number <= 0:
        return None, f"El campo {field_name} debe ser mayor que cero."

    return int(number), None


def _validate_sale_payload(payload):
    """Valida datos de entrada para registrar una venta."""
    forbidden_fields = sorted(READ_ONLY_FIELDS.intersection(payload))
    if forbidden_fields:
        return None, "No se permite enviar campos internos de la venta."

    normalized = {}

    for field_name in ("cliente_id", "producto_id"):
        value = payload.get(field_name)
        if not isinstance(value, str) or _is_blank(value):
            return None, f"El campo {field_name} es obligatorio."
        normalized[field_name] = value.strip()

    if "cantidad" not in payload:
        return None, "El campo cantidad es obligatorio."

    cantidad, error = _parse_positive_integer(payload["cantidad"], "cantidad")
    if error:
        return None, error
    normalized["cantidad"] = cantidad

    return normalized, None


def _to_decimal(value):
    """Convierte valores numericos a Decimal para DynamoDB."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


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


def _serialize_value(value):
    """Convierte valores Python a AttributeValue de DynamoDB."""
    if isinstance(value, bool):
        return {"BOOL": value}

    if isinstance(value, (int, Decimal)):
        return {"N": str(value)}

    if isinstance(value, float):
        return {"N": str(Decimal(str(value)))}

    return {"S": str(value)}


def _serialize_item(item):
    """Convierte un diccionario plano a formato AttributeValue."""
    return {key: _serialize_value(value) for key, value in item.items()}


def _get_error_code(exc):
    """Extrae codigo de error compatible con ClientError o mocks."""
    return getattr(exc, "response", {}).get("Error", {}).get("Code")


def _get_cliente(cliente_id):
    """Obtiene un cliente desde DynamoDB."""
    response = clientes_table.get_item(Key={"cliente_id": cliente_id})
    return response.get("Item")


def _get_producto(producto_id):
    """Obtiene un producto desde DynamoDB."""
    response = productos_table.get_item(Key={"producto_id": producto_id})
    return response.get("Item")


def _transact_create_sale(item, cantidad):
    """Guarda la venta y descuenta stock atomica y condicionalmente."""
    ddb_client.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": PRODUCTOS_TABLE,
                    "Key": {"producto_id": {"S": item["producto_id"]}},
                    "UpdateExpression": "SET #stock = #stock - :cantidad",
                    "ExpressionAttributeNames": {"#stock": "stock"},
                    "ExpressionAttributeValues": {":cantidad": {"N": str(cantidad)}},
                    "ConditionExpression": "attribute_exists(producto_id) AND #stock >= :cantidad",
                }
            },
            {
                "Put": {
                    "TableName": VENTAS_TABLE,
                    "Item": _serialize_item(item),
                    "ConditionExpression": "attribute_not_exists(venta_id)",
                }
            },
        ]
    )


def _transact_cancel_sale(sale, timestamp):
    """Anula la venta y devuelve stock atomica y condicionalmente."""
    ddb_client.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": VENTAS_TABLE,
                    "Key": {"venta_id": {"S": sale["venta_id"]}},
                    "UpdateExpression": "SET #estado = :anulada, anulada_at = :timestamp, updated_at = :timestamp",
                    "ExpressionAttributeNames": {"#estado": "estado"},
                    "ExpressionAttributeValues": {
                        ":anulada": {"S": CANCELED_STATUS},
                        ":timestamp": {"S": timestamp},
                    },
                    "ConditionExpression": (
                        "attribute_exists(venta_id) AND "
                        "(attribute_not_exists(#estado) OR #estado <> :anulada)"
                    ),
                }
            },
            {
                "Update": {
                    "TableName": PRODUCTOS_TABLE,
                    "Key": {"producto_id": {"S": sale["producto_id"]}},
                    "UpdateExpression": "SET #stock = #stock + :cantidad",
                    "ExpressionAttributeNames": {"#stock": "stock"},
                    "ExpressionAttributeValues": {":cantidad": {"N": str(sale["cantidad"])}},
                    "ConditionExpression": "attribute_exists(producto_id)",
                }
            },
        ]
    )


def create_sale(payload):
    """Registra una venta en DynamoDB."""
    normalized, error = _validate_sale_payload(payload)
    if error:
        return bad_request(error)

    cliente_id = normalized["cliente_id"]
    producto_id = normalized["producto_id"]
    cantidad = normalized["cantidad"]

    try:
        cliente = _get_cliente(cliente_id)
        if not cliente:
            return not_found("Cliente no encontrado.")

        producto = _get_producto(producto_id)
        if not producto:
            return not_found("Producto no encontrado.")

        precio_unitario = _to_decimal(producto.get("precio", 0))
        total = precio_unitario * Decimal(cantidad)

        timestamp = _current_timestamp()
        sale = Sale(
            venta_id=str(uuid4()),
            cliente_id=cliente_id,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            total=total,
            cliente_nombre=cliente.get("nombre", ""),
            producto_nombre=producto.get("nombre", ""),
            estado=COMPLETED_STATUS,
            fecha=timestamp,
            created_at=timestamp,
            updated_at=timestamp,
        )
        item = sale.to_dict()
        item.pop("anulada_at", None)

        try:
            _transact_create_sale(item, cantidad)
        except Exception as exc:
            if _get_error_code(exc) == "TransactionCanceledException":
                return bad_request("Stock insuficiente para registrar la venta.")

            logger.exception("Error al guardar venta y descontar stock en DynamoDB.")
            return internal_error("Ocurrio un error interno al procesar la solicitud.")

        return created(_to_json_compatible(item), "Venta creada correctamente.")
    except Exception:
        logger.exception("Error al crear venta en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def get_sale(sale_id):
    """Consulta una venta por ID en DynamoDB."""
    try:
        response = ventas_table.get_item(Key={"venta_id": sale_id})
        item = response.get("Item")
        if not item:
            return not_found("Venta no encontrada.")

        return success(_to_json_compatible(item), "Venta encontrada.")
    except Exception:
        logger.exception("Error al obtener venta desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def list_sales():
    """Lista ventas usando Scan en DynamoDB."""
    try:
        items = []
        response = ventas_table.scan()
        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = ventas_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        return success(_to_json_compatible(items), "Ventas listadas correctamente.")
    except Exception:
        logger.exception("Error al listar ventas desde DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def delete_sale(sale_id):
    """Deshabilita eliminacion fisica de ventas desde la API."""
    return bad_request("Las ventas deben anularse mediante POST /ventas/{id}/anular.")


def cancel_sale(sale_id):
    """Anula una venta y devuelve stock al producto de forma atomica."""
    try:
        response = ventas_table.get_item(Key={"venta_id": sale_id})
        sale = response.get("Item")
        if not sale:
            return not_found("Venta no encontrada.")

        if sale.get("estado", COMPLETED_STATUS) == CANCELED_STATUS:
            return conflict("La venta ya fue anulada.")

        cantidad, error = _parse_positive_integer(sale.get("cantidad"), "cantidad")
        if error:
            return bad_request("La cantidad original de la venta no es valida.")
        sale["cantidad"] = cantidad

        producto_id = sale.get("producto_id")
        if not producto_id:
            return bad_request("La venta no contiene producto asociado.")

        producto = _get_producto(producto_id)
        if not producto:
            return not_found("Producto no encontrado.")

        timestamp = _current_timestamp()
        try:
            _transact_cancel_sale(sale, timestamp)
        except Exception as exc:
            if _get_error_code(exc) == "TransactionCanceledException":
                return conflict("No se pudo anular la venta por su estado actual.")
            raise

        return success(
            {
                "venta_id": sale_id,
                "estado": CANCELED_STATUS,
                "stock_devuelto": cantidad,
            },
            "Venta anulada correctamente.",
        )
    except Exception:
        logger.exception("Error al anular venta en DynamoDB.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")
