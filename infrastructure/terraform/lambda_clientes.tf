# Empaqueta el codigo local de la Lambda Clientes en un archivo ZIP.
data "archive_file" "clientes_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions/clientes"
  output_path = "${path.module}/build/clientes_lambda.zip"

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
data "aws_iam_policy_document" "clientes_lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Rol de ejecucion exclusivo para la Lambda Clientes.
resource "aws_iam_role" "clientes_lambda" {
  name               = "${local.common_prefix}-clientes-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.clientes_lambda_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Service = "Clientes"
    }
  )
}

# Grupo de logs dedicado para la Lambda Clientes.
resource "aws_cloudwatch_log_group" "clientes_lambda" {
  name              = "/aws/lambda/${local.common_prefix}-clientes"
  retention_in_days = 14

  tags = merge(
    local.common_tags,
    {
      Service = "Clientes"
    }
  )
}

# Politica minima para logs y acceso CRUD/consulta a la tabla Clientes.
data "aws_iam_policy_document" "clientes_lambda" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.clientes_lambda.arn}:*",
    ]
  }

  statement {
    sid    = "AccessClientesTable"
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
      module.clientes_table.table_arn,
    ]
  }
}

# Adjunta permisos minimos directamente al rol de la Lambda.
resource "aws_iam_role_policy" "clientes_lambda" {
  name   = "${local.common_prefix}-clientes-lambda-policy"
  role   = aws_iam_role.clientes_lambda.id
  policy = data.aws_iam_policy_document.clientes_lambda.json
}

# Funcion Lambda unica para el CRUD de Clientes.
resource "aws_lambda_function" "clientes" {
  function_name    = "${local.common_prefix}-clientes"
  description      = "Lambda CRUD para el servicio de Clientes."
  role             = aws_iam_role.clientes_lambda.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.13"
  filename         = data.archive_file.clientes_lambda.output_path
  source_code_hash = data.archive_file.clientes_lambda.output_base64sha256

  environment {
    variables = {
      CLIENTES_TABLE = module.clientes_table.table_name
    }
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Clientes"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.clientes_lambda,
    aws_iam_role_policy.clientes_lambda,
  ]
}
