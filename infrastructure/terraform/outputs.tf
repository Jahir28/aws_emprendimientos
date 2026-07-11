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

output "clientes_table_name" {
  description = "Nombre de la tabla DynamoDB de Clientes."
  value       = module.clientes_table.table_name
}

output "clientes_table_arn" {
  description = "ARN de la tabla DynamoDB de Clientes."
  value       = module.clientes_table.table_arn
}

output "clientes_lambda_name" {
  description = "Nombre de la funcion Lambda de Clientes."
  value       = aws_lambda_function.clientes.function_name
}

output "clientes_lambda_arn" {
  description = "ARN de la funcion Lambda de Clientes."
  value       = aws_lambda_function.clientes.arn
}

output "clientes_api_base_url" {
  description = "URL base del recurso Clientes en el stage dev."
  value       = "${aws_apigatewayv2_stage.dev.invoke_url}/clientes"
}

output "ventas_table_name" {
  description = "Nombre de la tabla DynamoDB de Ventas."
  value       = module.ventas_table.table_name
}

output "ventas_table_arn" {
  description = "ARN de la tabla DynamoDB de Ventas."
  value       = module.ventas_table.table_arn
}

output "ventas_lambda_name" {
  description = "Nombre de la funcion Lambda de Ventas."
  value       = aws_lambda_function.ventas.function_name
}

output "ventas_lambda_arn" {
  description = "ARN de la funcion Lambda de Ventas."
  value       = aws_lambda_function.ventas.arn
}

output "ventas_api_base_url" {
  description = "URL base del recurso Ventas en el stage dev."
  value       = "${aws_apigatewayv2_stage.dev.invoke_url}/ventas"
}

output "reportes_lambda_name" {
  description = "Nombre de la funcion Lambda de Reportes."
  value       = aws_lambda_function.reportes.function_name
}

output "reportes_lambda_arn" {
  description = "ARN de la funcion Lambda de Reportes."
  value       = aws_lambda_function.reportes.arn
}

output "reportes_api_base_url" {
  description = "URL base del recurso Reportes en el stage dev."
  value       = "${aws_apigatewayv2_stage.dev.invoke_url}/reportes"
}

output "alertas_lambda_name" {
  description = "Nombre de la funcion Lambda de Alertas."
  value       = aws_lambda_function.alertas.function_name
}

output "alertas_sns_topic_arn" {
  description = "ARN del tema SNS de Alertas."
  value       = aws_sns_topic.alertas.arn
}

output "alertas_eventbridge_rule_name" {
  description = "Nombre de la regla programada de EventBridge para Alertas."
  value       = aws_cloudwatch_event_rule.alertas_schedule.name
}

output "alertas_email_subscription_status" {
  description = "Estado informativo de la suscripcion por correo a las alertas."
  value       = var.alertas_email != "" ? "Pendiente de confirmacion en el correo configurado." : "No configurada; alertas_email esta vacio."
}

output "frontend_bucket_name" {
  description = "Nombre del bucket S3 privado del frontend."
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_bucket_arn" {
  description = "ARN del bucket S3 privado del frontend."
  value       = aws_s3_bucket.frontend.arn
}

output "frontend_cloudfront_distribution_id" {
  description = "ID de la distribucion CloudFront del frontend."
  value       = aws_cloudfront_distribution.frontend.id
}

output "frontend_cloudfront_domain_name" {
  description = "Dominio de CloudFront para el frontend."
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "frontend_public_url" {
  description = "URL publica HTTPS del frontend."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}
