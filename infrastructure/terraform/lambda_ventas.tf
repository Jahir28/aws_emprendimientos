# Empaqueta el codigo local de la Lambda Ventas en un archivo ZIP.
data "archive_file" "ventas_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions/ventas"
  output_path = "${path.module}/build/ventas_lambda.zip"

  # Excluye archivos locales que no deben desplegarse en Lambda.
  excludes = [
    ".gitkeep",
    "__pycache__",
    "__pycache__/*",
    "tests",
    "tests/*",
    "tests/__pycache__",
    "tests/__pycache__/*",
    "events",
    "events/*",
  ]
}

# Politica de confianza para que AWS Lambda pueda asumir el rol.
data "aws_iam_policy_document" "ventas_lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Rol de ejecucion exclusivo para la Lambda Ventas.
resource "aws_iam_role" "ventas_lambda" {
  name               = "${local.common_prefix}-ventas-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.ventas_lambda_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Service = "Ventas"
    }
  )
}

# Grupo de logs dedicado para la Lambda Ventas.
resource "aws_cloudwatch_log_group" "ventas_lambda" {
  name              = "/aws/lambda/${local.common_prefix}-ventas"
  retention_in_days = 14

  tags = merge(
    local.common_tags,
    {
      Service = "Ventas"
    }
  )
}

# Politica minima para logs y acceso especifico a Ventas, Clientes y Productos.
data "aws_iam_policy_document" "ventas_lambda" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.ventas_lambda.arn}:*",
    ]
  }

  statement {
    sid    = "AccessVentasTable"
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]

    resources = [
      module.ventas_table.table_arn,
    ]
  }

  statement {
    sid    = "ReadClientesTable"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
    ]

    resources = [
      module.clientes_table.table_arn,
    ]
  }

  statement {
    sid    = "ReadAndUpdateProductosTable"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
    ]

    resources = [
      module.productos_table.table_arn,
    ]
  }
}

# Adjunta permisos minimos directamente al rol de la Lambda.
resource "aws_iam_role_policy" "ventas_lambda" {
  name   = "${local.common_prefix}-ventas-lambda-policy"
  role   = aws_iam_role.ventas_lambda.id
  policy = data.aws_iam_policy_document.ventas_lambda.json
}

# Funcion Lambda unica para registrar, consultar y eliminar Ventas.
resource "aws_lambda_function" "ventas" {
  function_name    = "${local.common_prefix}-ventas"
  description      = "Lambda CRUD parcial para el servicio de Ventas."
  role             = aws_iam_role.ventas_lambda.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.13"
  filename         = data.archive_file.ventas_lambda.output_path
  source_code_hash = data.archive_file.ventas_lambda.output_base64sha256

  environment {
    variables = {
      VENTAS_TABLE    = module.ventas_table.table_name
      CLIENTES_TABLE  = module.clientes_table.table_name
      PRODUCTOS_TABLE = module.productos_table.table_name
    }
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Ventas"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.ventas_lambda,
    aws_iam_role_policy.ventas_lambda,
  ]
}
