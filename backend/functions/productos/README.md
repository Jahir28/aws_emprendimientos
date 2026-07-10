# Lambda Productos

Funcion AWS Lambda en Python 3.13 para manejar operaciones CRUD del servicio de Productos. Esta version es local y utiliza respuestas simuladas; todavia no se conecta a Amazon DynamoDB ni se despliega en AWS.

## Proposito

Centralizar las operaciones de Productos en una unica Lambda que posteriormente sera integrada con Amazon API Gateway HTTP API y Amazon DynamoDB.

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
- `service.py`: contiene funciones CRUD con datos simulados.
- `models.py`: define el modelo `Product` con `dataclass`.
- `responses.py`: construye respuestas compatibles con API Gateway.
- `events/`: contiene eventos de ejemplo para pruebas locales.
- `tests/`: contiene pruebas unitarias con `unittest`.

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

Esta Lambda no usa variables de entorno, no accede a DynamoDB y no requiere credenciales AWS para ejecutarse localmente.

