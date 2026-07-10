# Tabla DynamoDB reutilizable para entidades del proyecto.
resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.hash_key

  # Clave de particion principal. Para Productos se usara producto_id.
  attribute {
    name = var.hash_key
    type = "S"
  }

  # Recuperacion a un punto en el tiempo, controlada por variable.
  point_in_time_recovery {
    enabled = var.point_in_time_recovery_enabled
  }

  # Proteccion contra eliminacion accidental, controlada por variable.
  deletion_protection_enabled = var.deletion_protection_enabled

  tags = var.tags
}

