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

# Correo electronico que recibira las alertas SNS.
# Si queda vacio, no se crea la suscripcion.
variable "alertas_email" {
  description = "Correo electronico para suscribirse al tema SNS de alertas. Si esta vacio, no se crea suscripcion."
  type        = string
  default     = ""
}

# Limite de stock bajo usado por la Lambda Alertas.
variable "stock_minimo_alerta" {
  description = "Limite entero no negativo para generar alertas de bajo stock."
  type        = number
  default     = 5

  validation {
    condition     = var.stock_minimo_alerta >= 0 && floor(var.stock_minimo_alerta) == var.stock_minimo_alerta
    error_message = "stock_minimo_alerta debe ser un entero no negativo."
  }
}

# Frecuencia de ejecucion programada para la Lambda Alertas.
variable "alertas_schedule_expression" {
  description = "Expresion schedule de EventBridge para ejecutar la Lambda Alertas."
  type        = string
  default     = "rate(1 day)"
}
