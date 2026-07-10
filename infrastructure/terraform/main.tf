# Tabla DynamoDB para el servicio de Productos.
# Este modulo solo prepara la definicion; el recurso se creara en AWS
# unicamente cuando se ejecute terraform apply.
module "productos_table" {
  source = "./modules/dynamodb"

  table_name = "${local.common_prefix}-productos"
  hash_key   = "producto_id"

  point_in_time_recovery_enabled = var.dynamodb_point_in_time_recovery_enabled
  deletion_protection_enabled    = var.dynamodb_deletion_protection_enabled

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )
}

# Tabla DynamoDB para el servicio de Clientes.
module "clientes_table" {
  source = "./modules/dynamodb"

  table_name = "${local.common_prefix}-clientes"
  hash_key   = "cliente_id"

  point_in_time_recovery_enabled = var.dynamodb_point_in_time_recovery_enabled
  deletion_protection_enabled    = var.dynamodb_deletion_protection_enabled

  tags = merge(
    local.common_tags,
    {
      Service = "Clientes"
    }
  )
}

# Tabla DynamoDB para el servicio de Ventas.
module "ventas_table" {
  source = "./modules/dynamodb"

  table_name = "${local.common_prefix}-ventas"
  hash_key   = "venta_id"

  point_in_time_recovery_enabled = var.dynamodb_point_in_time_recovery_enabled
  deletion_protection_enabled    = var.dynamodb_deletion_protection_enabled

  tags = merge(
    local.common_tags,
    {
      Service = "Ventas"
    }
  )
}

# En futuras iteraciones se agregaran modulos o recursos para:
# - AWS Lambda en Python para la logica backend.
# - Amazon API Gateway para exponer la API.
# - IAM para permisos minimos necesarios.
# - CloudWatch para logs y monitoreo.
# - SNS, EventBridge y posiblemente S3 segun evolucione el proyecto.
