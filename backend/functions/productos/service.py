"""Servicio mock para operaciones CRUD de Productos."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from models import Product
from responses import bad_request, created, success


def _current_timestamp():
    """Genera una fecha ISO 8601 en UTC para datos simulados."""
    return datetime.now(timezone.utc).isoformat()


def _mock_product(product_id="prod-001"):
    """Devuelve un producto de ejemplo sin consultar DynamoDB."""
    timestamp = "2026-07-10T00:00:00+00:00"
    return Product(
        producto_id=product_id,
        nombre="Cafe artesanal",
        descripcion="Producto de ejemplo para emprendimientos.",
        precio=12.5,
        stock=25,
        categoria="Bebidas",
        created_at=timestamp,
        updated_at=timestamp,
    )


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

    return float(number), None


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


def create_product(payload):
    """Simula la creacion de un producto."""
    normalized, error = _validate_product_payload(payload, require_name=True)
    if error:
        return bad_request(error)

    timestamp = _current_timestamp()
    product = Product(
        producto_id=str(uuid4()),
        nombre=normalized["nombre"],
        descripcion=normalized.get("descripcion", "Descripcion simulada."),
        precio=normalized.get("precio", 0),
        stock=normalized.get("stock", 0),
        categoria=normalized.get("categoria", "General"),
        created_at=timestamp,
        updated_at=timestamp,
    )
    return created(product.to_dict(), "Producto creado correctamente.")


def get_product(product_id):
    """Simula la consulta de un producto por ID."""
    return success(_mock_product(product_id).to_dict(), "Producto encontrado.")


def list_products():
    """Simula el listado de productos."""
    products = [
        _mock_product("prod-001").to_dict(),
        _mock_product("prod-002").to_dict(),
    ]
    return success(products, "Productos listados correctamente.")


def update_product(product_id, payload):
    """Simula la actualizacion de un producto."""
    normalized, error = _validate_product_payload(payload, require_name=False)
    if error:
        return bad_request(error)

    current = _mock_product(product_id).to_dict()
    current.update(
        {
            "nombre": normalized.get("nombre", current["nombre"]),
            "descripcion": normalized.get("descripcion", current["descripcion"]),
            "precio": normalized.get("precio", current["precio"]),
            "stock": normalized.get("stock", current["stock"]),
            "categoria": normalized.get("categoria", current["categoria"]),
            "updated_at": _current_timestamp(),
        }
    )
    return success(current, "Producto actualizado correctamente.")


def delete_product(product_id):
    """Simula la eliminacion de un producto."""
    return success(
        {"producto_id": product_id, "deleted": True},
        "Producto eliminado correctamente.",
    )
