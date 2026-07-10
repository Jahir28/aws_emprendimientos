"""Servicio para generar reportes de Productos, Clientes y Ventas."""

import logging
import os
from decimal import Decimal

import boto3

from responses import internal_error, success

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PRODUCTOS_TABLE = os.environ["PRODUCTOS_TABLE"]
CLIENTES_TABLE = os.environ["CLIENTES_TABLE"]
VENTAS_TABLE = os.environ["VENTAS_TABLE"]

dynamodb = boto3.resource("dynamodb")
productos_table = dynamodb.Table(PRODUCTOS_TABLE)
clientes_table = dynamodb.Table(CLIENTES_TABLE)
ventas_table = dynamodb.Table(VENTAS_TABLE)


def _scan_all(table):
    """Lee todos los registros de una tabla usando paginacion de Scan."""
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    return items


def _to_decimal(value):
    """Convierte valores numericos a Decimal para calculos consistentes."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value or 0))


def _to_int(value):
    """Convierte valores numericos de DynamoDB a entero."""
    return int(_to_decimal(value))


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


def get_summary_report():
    """Genera un resumen general de productos, clientes y ventas."""
    try:
        productos = _scan_all(productos_table)
        clientes = _scan_all(clientes_table)
        ventas = _scan_all(ventas_table)

        ingresos_totales = sum((_to_decimal(venta.get("total")) for venta in ventas), Decimal("0"))
        unidades_vendidas = sum(_to_int(venta.get("cantidad")) for venta in ventas)
        productos_bajo_stock = sum(1 for producto in productos if _to_int(producto.get("stock")) <= 5)
        valor_inventario = sum(
            _to_decimal(producto.get("precio")) * _to_decimal(producto.get("stock"))
            for producto in productos
        )

        report = {
            "total_productos": len(productos),
            "total_clientes": len(clientes),
            "total_ventas": len(ventas),
            "ingresos_totales": ingresos_totales,
            "unidades_vendidas": unidades_vendidas,
            "productos_bajo_stock": productos_bajo_stock,
            "valor_inventario": valor_inventario,
        }

        return success(_to_json_compatible(report))
    except Exception:
        logger.exception("Error al generar reporte resumen.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def get_top_products_report():
    """Genera el reporte de productos mas vendidos."""
    try:
        ventas = _scan_all(ventas_table)
        grouped = {}

        for venta in ventas:
            producto_id = venta.get("producto_id", "")
            if not producto_id:
                continue

            current = grouped.setdefault(
                producto_id,
                {
                    "producto_id": producto_id,
                    "producto_nombre": venta.get("producto_nombre", ""),
                    "cantidad_vendida": 0,
                    "ingresos": Decimal("0"),
                },
            )
            current["cantidad_vendida"] += _to_int(venta.get("cantidad"))
            current["ingresos"] += _to_decimal(venta.get("total"))

        report = sorted(
            grouped.values(),
            key=lambda item: item["cantidad_vendida"],
            reverse=True,
        )[:10]

        return success(_to_json_compatible(report))
    except Exception:
        logger.exception("Error al generar reporte de productos mas vendidos.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")


def get_frequent_clients_report():
    """Genera el reporte de clientes frecuentes."""
    try:
        ventas = _scan_all(ventas_table)
        grouped = {}

        for venta in ventas:
            cliente_id = venta.get("cliente_id", "")
            if not cliente_id:
                continue

            current = grouped.setdefault(
                cliente_id,
                {
                    "cliente_id": cliente_id,
                    "cliente_nombre": venta.get("cliente_nombre", ""),
                    "cantidad_ventas": 0,
                    "total_gastado": Decimal("0"),
                },
            )
            current["cantidad_ventas"] += 1
            current["total_gastado"] += _to_decimal(venta.get("total"))

        report = sorted(
            grouped.values(),
            key=lambda item: item["total_gastado"],
            reverse=True,
        )[:10]

        return success(_to_json_compatible(report))
    except Exception:
        logger.exception("Error al generar reporte de clientes frecuentes.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")

