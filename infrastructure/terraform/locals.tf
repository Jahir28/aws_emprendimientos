# Valores locales reutilizables para mantener nombres y etiquetas consistentes.
locals {
  # Prefijo comun para futuros recursos AWS.
  common_prefix = "${var.project_name}-${var.environment}"

  # Etiquetas comunes que se aplicaran a los recursos cuando se creen.
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

