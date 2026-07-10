"""Modelos de datos para la Lambda Productos."""

from dataclasses import asdict, dataclass


@dataclass
class Product:
    """Representa un producto del sistema."""

    producto_id: str
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data):
        """Crea un producto desde un diccionario."""
        return cls(
            producto_id=data.get("producto_id", ""),
            nombre=data.get("nombre", ""),
            descripcion=data.get("descripcion", ""),
            precio=float(data.get("precio", 0)),
            stock=int(data.get("stock", 0)),
            categoria=data.get("categoria", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def to_dict(self):
        """Convierte el producto a un diccionario serializable."""
        return asdict(self)

