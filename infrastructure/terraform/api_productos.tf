# HTTP API para exponer el microservicio de Productos.
resource "aws_apigatewayv2_api" "productos" {
  name          = "${local.common_prefix}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
  }

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )
}

# Integracion proxy entre API Gateway HTTP API y la Lambda Productos.
resource "aws_apigatewayv2_integration" "productos_lambda" {
  api_id                 = aws_apigatewayv2_api.productos.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.productos.invoke_arn
  payload_format_version = "2.0"
}

# Rutas CRUD del microservicio de Productos.
resource "aws_apigatewayv2_route" "productos_list" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /productos"
  target    = "integrations/${aws_apigatewayv2_integration.productos_lambda.id}"
}

resource "aws_apigatewayv2_route" "productos_create" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "POST /productos"
  target    = "integrations/${aws_apigatewayv2_integration.productos_lambda.id}"
}

resource "aws_apigatewayv2_route" "productos_get" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /productos/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.productos_lambda.id}"
}

resource "aws_apigatewayv2_route" "productos_update" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "PUT /productos/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.productos_lambda.id}"
}

resource "aws_apigatewayv2_route" "productos_delete" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "DELETE /productos/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.productos_lambda.id}"
}

# Stage de desarrollo con despliegue automatico.
resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.productos.id
  name        = "dev"
  auto_deploy = true

  tags = merge(
    local.common_tags,
    {
      Service = "Productos"
    }
  )
}

# Permite que API Gateway invoque la Lambda Productos.
resource "aws_lambda_permission" "productos_api_gateway" {
  statement_id  = "AllowProductosApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.productos.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.productos.execution_arn}/*/*"
}
