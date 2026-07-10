# Outputs no sensibles para confirmar la configuracion base seleccionada.

output "aws_region" {
  description = "Region de AWS configurada para el proyecto."
  value       = var.aws_region
}

output "project_name" {
  description = "Nombre base del proyecto."
  value       = var.project_name
}

output "environment" {
  description = "Ambiente de despliegue configurado."
  value       = var.environment
}

output "common_prefix" {
  description = "Prefijo comun calculado para futuros recursos."
  value       = local.common_prefix
}

output "productos_table_name" {
  description = "Nombre de la tabla DynamoDB de Productos."
  value       = module.productos_table.table_name
}

output "productos_table_arn" {
  description = "ARN de la tabla DynamoDB de Productos."
  value       = module.productos_table.table_arn
}

output "productos_lambda_function_name" {
  description = "Nombre de la funcion Lambda de Productos."
  value       = aws_lambda_function.productos.function_name
}

output "productos_lambda_function_arn" {
  description = "ARN de la funcion Lambda de Productos."
  value       = aws_lambda_function.productos.arn
}

output "productos_lambda_table_name" {
  description = "Nombre de la tabla DynamoDB usada por la Lambda de Productos."
  value       = module.productos_table.table_name
}

output "api_gateway_id" {
  description = "ID de la HTTP API de Productos."
  value       = aws_apigatewayv2_api.productos.id
}

output "api_gateway_endpoint" {
  description = "Endpoint base de la HTTP API de Productos."
  value       = aws_apigatewayv2_api.productos.api_endpoint
}

output "productos_api_base_url" {
  description = "URL base del recurso Productos en el stage dev."
  value       = "${aws_apigatewayv2_stage.dev.invoke_url}/productos"
}
