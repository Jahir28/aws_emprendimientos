# Empaqueta el codigo local de la Lambda Productos en un archivo ZIP.
data "archive_file" "productos_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions/productos"
  output_path = "${path.module}/build/productos_lambda.zip"

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
data "aws_iam_policy_document" "productos_lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Rol de ejecucion exclusivo para la Lambda Productos.
resource "aws_iam_role" "productos_lambda" {
  name               = "${local.common_prefix}-productos-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.productos_lambda_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )
}

# Grupo de logs dedicado para la Lambda Productos.
resource "aws_cloudwatch_log_group" "productos_lambda" {
  name              = "/aws/lambda/${local.common_prefix}-productos"
  retention_in_days = 14

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )
}

# Politica minima para logs y acceso CRUD/consulta a la tabla Productos.
data "aws_iam_policy_document" "productos_lambda" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.productos_lambda.arn}:*",
    ]
  }

  statement {
    sid    = "AccessProductosTable"
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]

    resources = [
      module.productos_table.table_arn,
    ]
  }
}

# Adjunta permisos minimos directamente al rol de la Lambda.
resource "aws_iam_role_policy" "productos_lambda" {
  name   = "${local.common_prefix}-productos-lambda-policy"
  role   = aws_iam_role.productos_lambda.id
  policy = data.aws_iam_policy_document.productos_lambda.json
}

# Funcion Lambda unica para el CRUD de Productos.
resource "aws_lambda_function" "productos" {
  function_name    = "${local.common_prefix}-productos"
  description      = "Lambda CRUD para el servicio de Productos."
  role             = aws_iam_role.productos_lambda.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.13"
  filename         = data.archive_file.productos_lambda.output_path
  source_code_hash = data.archive_file.productos_lambda.output_base64sha256

  environment {
    variables = {
      PRODUCTOS_TABLE = module.productos_table.table_name
    }
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.productos_lambda,
    aws_iam_role_policy.productos_lambda,
  ]
}
