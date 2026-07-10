# Region de AWS donde se desplegaran los recursos del proyecto.
variable "aws_region" {
  description = "Region de AWS para desplegar la infraestructura."
  type        = string
  default     = "us-west-2"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]+$", var.aws_region))
    error_message = "La region de AWS debe tener un formato valido, por ejemplo us-west-2."
  }
}

# Nombre base del proyecto usado para nombrar recursos y etiquetas.
variable "project_name" {
  description = "Nombre base del proyecto."
  type        = string
  default     = "aws-emprendimientos"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.project_name))
    error_message = "El nombre del proyecto debe usar minusculas, numeros y guiones, sin iniciar ni terminar con guion."
  }
}

# Ambiente logico de despliegue, por ejemplo dev, staging o prod.
variable "environment" {
  description = "Ambiente de despliegue de la infraestructura."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "El ambiente debe ser uno de estos valores: dev, staging o prod."
  }
}

# Controla Point-in-Time Recovery para tablas DynamoDB.
# En desarrollo queda desactivado para mantener la configuracion simple.
variable "dynamodb_point_in_time_recovery_enabled" {
  description = "Indica si las tablas DynamoDB deben habilitar Point-in-Time Recovery."
  type        = bool
  default     = false
}

# Controla deletion protection para tablas DynamoDB.
# En desarrollo queda desactivado para permitir cambios controlados durante pruebas.
variable "dynamodb_deletion_protection_enabled" {
  description = "Indica si las tablas DynamoDB deben habilitar proteccion contra eliminacion."
  type        = bool
  default     = false
}
