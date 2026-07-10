# Configuracion del proveedor de AWS.
# Las credenciales se deben resolver fuera del codigo, por ejemplo mediante
# variables de entorno, AWS CLI, IAM roles o el mecanismo seguro definido
# para el entorno de trabajo.
provider "aws" {
  region = var.aws_region
}

