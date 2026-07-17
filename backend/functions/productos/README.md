# Lambda Productos

Funcion AWS Lambda en Python 3.13 para manejar operaciones CRUD del servicio de Productos. Usa Amazon DynamoDB mediante `boto3` y esta preparada para eventos de Amazon API Gateway HTTP API v2, manteniendo compatibilidad con REST API v1.

## Proposito

Centralizar las operaciones de Productos en una unica Lambda que expone rutas CRUD y persiste datos en una tabla DynamoDB configurada mediante la variable de entorno `PRODUCTOS_TABLE`.

## Estructura

```text
productos/
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

## Responsabilidades

- `lambda_function.py`: recibe el evento de API Gateway, identifica metodo y ruta, y delega al servicio.
- `service.py`: contiene funciones CRUD sobre DynamoDB.
- `models.py`: define el modelo `Product` con `dataclass`.
- `responses.py`: construye respuestas compatibles con API Gateway.
- `events/`: contiene eventos de ejemplo para pruebas locales.
- `tests/`: contiene pruebas unitarias con `unittest`.

## Rutas soportadas

- `GET /productos`
- `POST /productos`
- `GET /productos/{id}`
- `PUT /productos/{id}`
- `DELETE /productos/{id}`

## Ejecutar pruebas

Desde esta carpeta:

```bash
python3 -m unittest discover tests
```

## Ejecutar localmente

Puedes invocar el handler desde Python cargando uno de los eventos de ejemplo:

```bash
python3 -c 'import json; from lambda_function import handler; event=json.load(open("events/list.json")); print(handler(event, None))'
```

Para ejecutar localmente se debe definir `PRODUCTOS_TABLE` y mockear o configurar credenciales AWS si se desea llamar DynamoDB real.
