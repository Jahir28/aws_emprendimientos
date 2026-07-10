# Empaqueta el codigo local de la Lambda Reportes en un archivo ZIP.
data "archive_file" "reportes_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions/reportes"
  output_path = "${path.module}/build/reportes_lambda.zip"

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
data "aws_iam_policy_document" "reportes_lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Rol de ejecucion exclusivo para la Lambda Reportes.
resource "aws_iam_role" "reportes_lambda" {
  name               = "${local.common_prefix}-reportes-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.reportes_lambda_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Service = "Reportes"
    }
  )
}

# Grupo de logs dedicado para la Lambda Reportes.
resource "aws_cloudwatch_log_group" "reportes_lambda" {
  name              = "/aws/lambda/${local.common_prefix}-reportes"
  retention_in_days = 14

  tags = merge(
    local.common_tags,
    {
      Service = "Reportes"
    }
  )
}

# Politica minima de solo lectura para generar reportes.
data "aws_iam_policy_document" "reportes_lambda" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.reportes_lambda.arn}:*",
    ]
  }

  statement {
    sid    = "ScanProductosClientesVentas"
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
    ]

    resources = [
      module.productos_table.table_arn,
      module.clientes_table.table_arn,
      module.ventas_table.table_arn,
    ]
  }
}

# Adjunta permisos minimos directamente al rol de la Lambda.
resource "aws_iam_role_policy" "reportes_lambda" {
  name   = "${local.common_prefix}-reportes-lambda-policy"
  role   = aws_iam_role.reportes_lambda.id
  policy = data.aws_iam_policy_document.reportes_lambda.json
}

# Funcion Lambda para generar reportes de solo lectura.
resource "aws_lambda_function" "reportes" {
  function_name    = "${local.common_prefix}-reportes"
  description      = "Lambda de reportes para Productos, Clientes y Ventas."
  role             = aws_iam_role.reportes_lambda.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.13"
  filename         = data.archive_file.reportes_lambda.output_path
  source_code_hash = data.archive_file.reportes_lambda.output_base64sha256

  environment {
    variables = {
      PRODUCTOS_TABLE = module.productos_table.table_name
      CLIENTES_TABLE  = module.clientes_table.table_name
      VENTAS_TABLE    = module.ventas_table.table_name
    }
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Reportes"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.reportes_lambda,
    aws_iam_role_policy.reportes_lambda,
  ]
}
