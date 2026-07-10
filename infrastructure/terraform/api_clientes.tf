# Integracion proxy entre API Gateway HTTP API existente y la Lambda Clientes.
resource "aws_apigatewayv2_integration" "clientes_lambda" {
  api_id                 = aws_apigatewayv2_api.productos.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.clientes.invoke_arn
  payload_format_version = "2.0"
}

# Rutas CRUD del microservicio de Clientes.
resource "aws_apigatewayv2_route" "clientes_list" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /clientes"
  target    = "integrations/${aws_apigatewayv2_integration.clientes_lambda.id}"
}

resource "aws_apigatewayv2_route" "clientes_create" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "POST /clientes"
  target    = "integrations/${aws_apigatewayv2_integration.clientes_lambda.id}"
}

resource "aws_apigatewayv2_route" "clientes_get" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "GET /clientes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.clientes_lambda.id}"
}

resource "aws_apigatewayv2_route" "clientes_update" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "PUT /clientes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.clientes_lambda.id}"
}

resource "aws_apigatewayv2_route" "clientes_delete" {
  api_id    = aws_apigatewayv2_api.productos.id
  route_key = "DELETE /clientes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.clientes_lambda.id}"
}

# Permite que API Gateway invoque la Lambda Clientes.
resource "aws_lambda_permission" "clientes_api_gateway" {
  statement_id  = "AllowClientesApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.clientes.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.productos.execution_arn}/*/*"
}
