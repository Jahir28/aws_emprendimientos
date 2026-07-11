# Integracion proxy entre API Gateway HTTP API existente y la Lambda Ventas.
resource "aws_apigatewayv2_integration" "ventas_lambda" {
  api_id                 = aws_apigatewayv2_api.productos.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.ventas.invoke_arn
  payload_format_version = "2.0"
}

# Rutas del microservicio de Ventas. No se expone PUT para ventas.
resource "aws_apigatewayv2_route" "ventas_list" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /ventas"
  target    = "integrations/${aws_apigatewayv2_integration.ventas_lambda.id}"
}

resource "aws_apigatewayv2_route" "ventas_create" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "POST /ventas"
  target    = "integrations/${aws_apigatewayv2_integration.ventas_lambda.id}"
}

resource "aws_apigatewayv2_route" "ventas_get" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /ventas/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.ventas_lambda.id}"
}

resource "aws_apigatewayv2_route" "ventas_cancel" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "POST /ventas/{id}/anular"
  target    = "integrations/${aws_apigatewayv2_integration.ventas_lambda.id}"
}

# Permite que API Gateway invoque la Lambda Ventas.
resource "aws_lambda_permission" "ventas_api_gateway" {
  statement_id  = "AllowVentasApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ventas.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.productos.execution_arn}/*/*"
}
