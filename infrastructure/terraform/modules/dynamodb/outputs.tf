# Nombre final de la tabla creada por el modulo.
output "table_name" {
  description = "Nombre de la tabla DynamoDB."
  value       = aws_dynamodb_table.this.name
}

# ARN de la tabla, util para permisos IAM y referencias futuras.
output "table_arn" {
  description = "ARN de la tabla DynamoDB."
  value       = aws_dynamodb_table.this.arn
}

# ID de la tabla DynamoDB.
output "table_id" {
  description = "ID de la tabla DynamoDB."
  value       = aws_dynamodb_table.this.id
}

# Clave de particion configurada en la tabla.
output "hash_key" {
  description = "Clave de particion utilizada por la tabla."
  value       = aws_dynamodb_table.this.hash_key
}

