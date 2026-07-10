# Integracion proxy entre API Gateway HTTP API existente y la Lambda Reportes.
resource "aws_apigatewayv2_integration" "reportes_lambda" {
  api_id                 = aws_apigatewayv2_api.productos.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.reportes.invoke_arn
  payload_format_version = "2.0"
}

# Rutas de solo lectura del microservicio de Reportes.
resource "aws_apigatewayv2_route" "reportes_resumen" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /reportes/resumen"
  target    = "integrations/${aws_apigatewayv2_integration.reportes_lambda.id}"
}

resource "aws_apigatewayv2_route" "reportes_productos_mas_vendidos" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /reportes/productos-mas-vendidos"
  target    = "integrations/${aws_apigatewayv2_integration.reportes_lambda.id}"
}

resource "aws_apigatewayv2_route" "reportes_clientes_frecuentes" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /reportes/clientes-frecuentes"
  target    = "integrations/${aws_apigatewayv2_integration.reportes_lambda.id}"
}

# Permite que API Gateway invoque la Lambda Reportes.
resource "aws_lambda_permission" "reportes_api_gateway" {
  statement_id  = "AllowReportesApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reportes.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.productos.execution_arn}/*/*"
}
