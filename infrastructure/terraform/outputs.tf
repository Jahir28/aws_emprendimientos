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

