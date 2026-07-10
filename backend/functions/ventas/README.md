# Lambda Ventas

Funcion AWS Lambda en Python 3.13 para registrar y consultar ventas. Usa Amazon DynamoDB mediante `boto3` y esta preparada para eventos de Amazon API Gateway HTTP API v2, manteniendo compatibilidad con REST API v1.

## Proposito

Registrar ventas validando la existencia del cliente y producto, descontando stock de forma condicional y guardando la venta resultante.

## Variables de entorno

- `VENTAS_TABLE`
- `CLIENTES_TABLE`
- `PRODUCTOS_TABLE`

## Rutas soportadas

- `GET /ventas`
- `POST /ventas`
- `GET /ventas/{id}`
- `DELETE /ventas/{id}`

No se implementa `PUT /ventas/{id}` porque una venta registrada no debe modificarse directamente.

## Estructura

```text
ventas/
├── lambda_function.py
├── models.py
├── responses.py
├── service.py
├── requirements.txt
├── tests/
│   ├── __init__.py
│   └── test_lambda.py
└── events/
    ├── create.json
    ├── get.json
    ├── list.json
    └── delete.json
```

## Ejecutar pruebas

Desde esta carpeta:

```bash
python3 -m unittest discover tests
```

Las pruebas mockean `boto3`; no se conectan a AWS.

