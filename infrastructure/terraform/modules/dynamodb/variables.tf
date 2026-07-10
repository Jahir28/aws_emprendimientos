# Nombre final de la tabla DynamoDB.
variable "table_name" {
  description = "Nombre de la tabla DynamoDB."
  type        = string

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]{3,255}$", var.table_name))
    error_message = "El nombre de la tabla debe tener entre 3 y 255 caracteres y usar letras, numeros, guion, guion bajo o punto."
  }
}

# Clave de particion de la tabla.
variable "hash_key" {
  description = "Nombre de la clave de particion de la tabla."
  type        = string
  default     = "producto_id"

  validation {
    condition     = can(regex("^[A-Za-z][A-Za-z0-9_]*$", var.hash_key))
    error_message = "La clave de particion debe iniciar con una letra y usar letras, numeros o guion bajo."
  }
}

# Activa o desactiva Point-in-Time Recovery.
variable "point_in_time_recovery_enabled" {
  description = "Indica si DynamoDB Point-in-Time Recovery debe estar habilitado."
  type        = bool
  default     = false
}

# Activa o desactiva deletion protection.
variable "deletion_protection_enabled" {
  description = "Indica si la proteccion contra eliminacion de la tabla debe estar habilitada."
  type        = bool
  default     = false
}

# Etiquetas comunes para organizar y rastrear recursos.
variable "tags" {
  description = "Mapa de etiquetas para aplicar a la tabla DynamoDB."
  type        = map(string)
  default     = {}
}

