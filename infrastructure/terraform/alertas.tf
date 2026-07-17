# Empaqueta el codigo local de la Lambda Alertas en un archivo ZIP.
data "archive_file" "alertas_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/functions/alertas"
  output_path = "${path.module}/build/alertas_lambda.zip"

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

# Tema SNS para notificaciones de alertas automaticas.
resource "aws_sns_topic" "alertas" {
  name = "${local.common_prefix}-alertas"

  tags = merge(
    local.common_tags,
    {
      Service = "Alertas"
    }
  )
}

# Suscripcion por correo para recibir alertas, creada solo si se configura email.
resource "aws_sns_topic_subscription" "alertas_email" {
  count = var.alertas_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alertas.arn
  protocol  = "email"
  endpoint  = var.alertas_email
}

# Politica de confianza para que AWS Lambda pueda asumir el rol.
data "aws_iam_policy_document" "alertas_lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Rol de ejecucion exclusivo para la Lambda Alertas.
resource "aws_iam_role" "alertas_lambda" {
  name               = "${local.common_prefix}-alertas-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.alertas_lambda_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Service = "Alertas"
    }
  )
}

# Grupo de logs dedicado para la Lambda Alertas.
resource "aws_cloudwatch_log_group" "alertas_lambda" {
  name              = "/aws/lambda/${local.common_prefix}-alertas"
  retention_in_days = 14

  tags = merge(
    local.common_tags,
    {
      Service = "Alertas"
    }
  )
}

# Politica minima para logs, lectura de Productos y publicacion en SNS.
data "aws_iam_policy_document" "alertas_lambda" {
  statement {
    sid    = "WriteCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.alertas_lambda.arn}:*",
    ]
  }

  statement {
    sid    = "ScanProductosTable"
    effect = "Allow"

    actions = [
      "dynamodb:Scan",
    ]

    resources = [
      module.productos_table.table_arn,
    ]
  }

  statement {
    sid    = "PublishAlertasTopic"
    effect = "Allow"

    actions = [
      "sns:Publish",
    ]

    resources = [
      aws_sns_topic.alertas.arn,
    ]
  }
}

# Adjunta permisos minimos directamente al rol de la Lambda.
resource "aws_iam_role_policy" "alertas_lambda" {
  name   = "${local.common_prefix}-alertas-lambda-policy"
  role   = aws_iam_role.alertas_lambda.id
  policy = data.aws_iam_policy_document.alertas_lambda.json
}

# Funcion Lambda para generar alertas automaticas de bajo stock.
resource "aws_lambda_function" "alertas" {
  function_name    = "${local.common_prefix}-alertas"
  description      = "Lambda de alertas automaticas de bajo stock."
  role             = aws_iam_role.alertas_lambda.arn
  handler          = "lambda_function.handler"
  runtime          = "python3.13"
  filename         = data.archive_file.alertas_lambda.output_path
  source_code_hash = data.archive_file.alertas_lambda.output_base64sha256
  timeout          = 15
  memory_size      = 256

  environment {
    variables = {
      PRODUCTOS_TABLE = module.productos_table.table_name
      SNS_TOPIC_ARN   = aws_sns_topic.alertas.arn
      STOCK_MINIMO    = tostring(var.stock_minimo_alerta)
    }
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Alertas"
    }
  )

  depends_on = [
    aws_cloudwatch_log_group.alertas_lambda,
    aws_iam_role_policy.alertas_lambda,
  ]
}

# Regla programada de EventBridge para ejecutar la Lambda Alertas.
resource "aws_cloudwatch_event_rule" "alertas_schedule" {
  name                = "${local.common_prefix}-alertas-schedule"
  description         = "Ejecucion programada de alertas automaticas de bajo stock."
  schedule_expression = var.alertas_schedule_expression
  state               = "ENABLED"

  tags = merge(
    local.common_tags,
    {
      Service = "Alertas"
    }
  )
}

# Target de EventBridge hacia la Lambda Alertas.
resource "aws_cloudwatch_event_target" "alertas_lambda" {
  rule      = aws_cloudwatch_event_rule.alertas_schedule.name
  target_id = "${local.common_prefix}-alertas-lambda"
  arn       = aws_lambda_function.alertas.arn
}

# Permite que EventBridge invoque la Lambda Alertas.
resource "aws_lambda_permission" "allow_eventbridge_alertas" {
  statement_id  = "AllowExecutionFromEventBridgeAlertas"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.alertas.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.alertas_schedule.arn
}
