"""Modelos de datos para la Lambda Ventas."""

from dataclasses import asdict, dataclass


@dataclass
class Sale:
    """Representa una venta registrada en el sistema."""

    venta_id: str
    cliente_id: str
    producto_id: str
    cantidad: int
    precio_unitario: object
    total: object
    cliente_nombre: str
    producto_nombre: str
    fecha: str
    created_at: str

    @classmethod
    def from_dict(cls, data):
        """Crea una venta desde un diccionario."""
        return cls(
            venta_id=data.get("venta_id", ""),
            cliente_id=data.get("cliente_id", ""),
            producto_id=data.get("producto_id", ""),
            cantidad=int(data.get("cantidad", 0)),
            precio_unitario=data.get("precio_unitario", 0),
            total=data.get("total", 0),
            cliente_nombre=data.get("cliente_nombre", ""),
            producto_nombre=data.get("producto_nombre", ""),
            fecha=data.get("fecha", ""),
            created_at=data.get("created_at", ""),
        )

    def to_dict(self):
        """Convierte la venta a un diccionario serializable."""
        return asdict(self)

