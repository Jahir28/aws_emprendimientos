"""Modelos de datos para la Lambda Clientes."""

from dataclasses import asdict, dataclass


@dataclass
class Client:
    """Representa un cliente del sistema."""

    cliente_id: str
    nombre: str
    correo: str
    telefono: str
    direccion: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data):
        """Crea un cliente desde un diccionario."""
        return cls(
            cliente_id=data.get("cliente_id", ""),
            nombre=data.get("nombre", ""),
            correo=data.get("correo", ""),
            telefono=data.get("telefono", ""),
            direccion=data.get("direccion", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def to_dict(self):
        """Convierte el cliente a un diccionario serializable."""
        return asdict(self)

