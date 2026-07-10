# Define la version minima de Terraform y los proveedores requeridos.
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    # Proveedor oficial de AWS mantenido por HashiCorp.
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

