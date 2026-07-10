# Lambda Clientes

Funcion AWS Lambda en Python 3.13 para manejar operaciones CRUD del servicio de Clientes. Usa Amazon DynamoDB mediante `boto3` y esta preparada para eventos de Amazon API Gateway HTTP API v2, manteniendo compatibilidad con REST API v1.

## Proposito

Centralizar las operaciones de Clientes en una unica Lambda que expone rutas CRUD y persiste datos en una tabla DynamoDB configurada mediante la variable de entorno `CLIENTES_TABLE`.

## Estructura

```text
clientes/
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
    ├── update.json
    └── delete.json
```

## Rutas soportadas

- `GET /clientes`
- `POST /clientes`
- `GET /clientes/{id}`
- `PUT /clientes/{id}`
- `DELETE /clientes/{id}`

## Ejecutar pruebas

Desde esta carpeta:

```bash
python3 -m unittest discover tests
```

Las pruebas mockean `boto3`; no se conectan a AWS.

## Ejecutar localmente

Para ejecutar localmente se debe definir `CLIENTES_TABLE` y mockear o configurar credenciales AWS si se desea llamar DynamoDB real.

