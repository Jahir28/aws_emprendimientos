"""Servicio para generar alertas automaticas de bajo stock."""

import logging
import os
from decimal import Decimal, InvalidOperation

import boto3

from responses import bad_request, internal_error, success

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_STOCK_MINIMO = Decimal("5")
SNS_SUBJECT = "Alerta de stock bajo - AWS Emprendimientos"


def _get_required_env(name):
    """Obtiene una variable de entorno obligatoria."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"La variable de entorno {name} es obligatoria.")
    return value


def _get_stock_minimo():
    """Obtiene el limite de stock bajo desde el entorno."""
    raw_value = os.environ.get("STOCK_MINIMO")
    if raw_value in (None, ""):
        return DEFAULT_STOCK_MINIMO

    try:
        stock_minimo = Decimal(str(raw_value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            "La variable de entorno STOCK_MINIMO debe ser un entero no negativo."
        ) from exc

    if stock_minimo != stock_minimo.to_integral_value() or stock_minimo < 0:
        raise ValueError("La variable de entorno STOCK_MINIMO debe ser un entero no negativo.")

    return stock_minimo


def _get_productos_table(table_name):
    """Construye la referencia a la tabla de productos."""
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def _get_sns_client():
    """Construye el cliente SNS."""
    return boto3.client("sns")


def _scan_all_products(table):
    """Consulta todos los productos usando Scan con paginacion."""
    products = []
    response = table.scan()
    products.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        products.extend(response.get("Items", []))

    return products


def _to_decimal(value):
    """Convierte valores numericos de DynamoDB a Decimal."""
    if isinstance(value, Decimal):
        return value

    if value in (None, ""):
        return Decimal("0")

    return Decimal(str(value))


def _format_number(value):
    """Formatea numeros para mensajes legibles."""
    decimal_value = _to_decimal(value)
    if decimal_value == decimal_value.to_integral_value():
        return str(int(decimal_value))
    return format(decimal_value.normalize(), "f")


def _build_alert_message(low_stock_products, stock_minimo):
    """Crea un mensaje consolidado para SNS."""
    lines = [
        "Se detectaron productos con stock bajo en AWS Emprendimientos.",
        "",
        f"Limite configurado: {_format_number(stock_minimo)}",
        "",
        "Productos:",
    ]

    for product in low_stock_products:
        lines.append(
            "- "
            f"{product.get('nombre', 'Sin nombre')} "
            f"(producto_id: {product.get('producto_id', 'Sin ID')}) - "
            f"stock actual: {_format_number(product.get('stock'))}, "
            f"limite: {_format_number(stock_minimo)}"
        )

    return "\n".join(lines)


def _build_result(products_checked, low_stock_products, notification_sent, message_id=None):
    """Normaliza la respuesta del proceso de alertas."""
    result = {
        "productos_revisados": products_checked,
        "productos_bajo_stock": len(low_stock_products),
        "notificacion_enviada": notification_sent,
    }

    if message_id:
        result["message_id"] = message_id

    return result


def generate_low_stock_alerts():
    """Genera y publica una alerta consolidada si hay productos con bajo stock."""
    try:
        table_name = _get_required_env("PRODUCTOS_TABLE")
        topic_arn = _get_required_env("SNS_TOPIC_ARN")
        stock_minimo = _get_stock_minimo()
    except ValueError as exc:
        logger.info("Configuracion invalida para alertas: %s", exc)
        return bad_request(str(exc))

    try:
        logger.info("Consultando productos para detectar bajo stock.")
        table = _get_productos_table(table_name)
        products = _scan_all_products(table)
        low_stock_products = [
            product
            for product in products
            if _to_decimal(product.get("stock")) <= stock_minimo
        ]

        if not low_stock_products:
            logger.info("No se encontraron productos con bajo stock.")
            result = _build_result(
                products_checked=len(products),
                low_stock_products=low_stock_products,
                notification_sent=False,
            )
            return success(result, "No se generaron alertas de stock bajo.")

        logger.info(
            "Se encontraron %s productos con bajo stock. Publicando alerta en SNS.",
            len(low_stock_products),
        )
        message = _build_alert_message(low_stock_products, stock_minimo)
        sns_response = _get_sns_client().publish(
            TopicArn=topic_arn,
            Subject=SNS_SUBJECT,
            Message=message,
        )
        message_id = sns_response.get("MessageId")
        result = _build_result(
            products_checked=len(products),
            low_stock_products=low_stock_products,
            notification_sent=True,
            message_id=message_id,
        )

        return success(result, "Alerta de stock bajo enviada correctamente.")
    except Exception:
        logger.exception("Error inesperado al generar alertas de bajo stock.")
        return internal_error("Ocurrio un error interno al generar alertas.")
