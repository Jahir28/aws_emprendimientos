# aws_emprendimientos

Proyecto universitario para gestionar procesos basicos de pequenos emprendimientos mediante una arquitectura serverless en AWS.

## Descripcion

`aws_emprendimientos` integra una plataforma web administrativa, microservicios backend en AWS Lambda, persistencia en DynamoDB e infraestructura como codigo con Terraform.

La interfaz visual se presenta como **ControlPyme**, un panel administrativo moderno para gestionar productos, clientes, ventas, reportes y alertas operativas.

## Objetivo

Construir una solucion academica con practicas modernas de desarrollo cloud, usando servicios administrados de AWS, separacion por dominios, pruebas unitarias e infraestructura reproducible.

## Funcionalidades

- Panel administrativo web con Vue 3 y Vite.
- Gestion de productos mediante API Gateway, Lambda y DynamoDB.
- Gestion de clientes mediante API Gateway, Lambda y DynamoDB.
- Registro, consulta, listado y eliminacion de ventas.
- Validacion de cliente y producto antes de registrar ventas.
- Descuento condicional de stock al registrar ventas.
- Reportes operativos de resumen, productos mas vendidos y clientes frecuentes.
- Alertas automaticas de bajo stock mediante EventBridge, Lambda y SNS.
- Infraestructura definida con Terraform.

## Arquitectura

```text
Frontend Vue 3
      |
Amazon API Gateway HTTP API
      |
AWS Lambda Python 3.13
      |
Amazon DynamoDB

Amazon EventBridge
      |
Lambda Alertas
      |
DynamoDB Productos
      |
Amazon SNS
      |
Suscripcion por correo
```

Componentes principales:

- Frontend: Vue 3, Vite, Vue Router, PrimeVue, Chart.js y Axios.
- Backend: AWS Lambda con Python 3.13.
- API: Amazon API Gateway HTTP API.
- Base de datos: Amazon DynamoDB.
- Alertas: Amazon EventBridge y Amazon SNS.
- Infraestructura: Terraform.
- Region objetivo: `us-west-2`.

## Microservicios backend

### Productos

- Rutas: `GET /productos`, `POST /productos`, `GET /productos/{id}`, `PUT /productos/{id}`, `DELETE /productos/{id}`.
- Tabla DynamoDB: `aws-emprendimientos-dev-productos`.
- Variable de entorno: `PRODUCTOS_TABLE`.

### Clientes

- Rutas: `GET /clientes`, `POST /clientes`, `GET /clientes/{id}`, `PUT /clientes/{id}`, `DELETE /clientes/{id}`.
- Tabla DynamoDB: `aws-emprendimientos-dev-clientes`.
- Variable de entorno: `CLIENTES_TABLE`.

### Ventas

- Rutas: `GET /ventas`, `POST /ventas`, `GET /ventas/{id}`, `DELETE /ventas/{id}`.
- Tabla DynamoDB: `aws-emprendimientos-dev-ventas`.
- Variables de entorno: `VENTAS_TABLE`, `CLIENTES_TABLE`, `PRODUCTOS_TABLE`.
- No implementa `PUT`, porque una venta registrada no debe modificarse directamente.

### Reportes

- Rutas: `GET /reportes/resumen`, `GET /reportes/productos-mas-vendidos`, `GET /reportes/clientes-frecuentes`.
- Variables de entorno: `PRODUCTOS_TABLE`, `CLIENTES_TABLE`, `VENTAS_TABLE`.
- Acceso de solo lectura a DynamoDB.

### Alertas

- Ejecucion programada mediante EventBridge.
- Consulta productos con `Scan` paginado.
- Publica una alerta consolidada en SNS cuando hay productos con bajo stock.
- Variables de entorno: `PRODUCTOS_TABLE`, `SNS_TOPIC_ARN`, `STOCK_MINIMO`.

## Frontend

El frontend esta en `frontend/` y contiene la base visual de **ControlPyme**:

- Layout administrativo responsive.
- Sidebar con navegacion principal.
- Dashboard con metricas y graficas.
- Vistas de productos, clientes, ventas y reportes con datos simulados.
- Instancia Axios preparada con `VITE_API_BASE_URL`.

Comandos principales:

```bash
cd frontend
npm install
npm run dev
npm run build
```

Archivo de ejemplo de entorno:

```bash
frontend/.env.example
```

## Estructura

```text
aws_emprendimientos/
├── frontend/
├── backend/
│   └── functions/
│       ├── productos/
│       ├── clientes/
│       ├── ventas/
│       ├── reportes/
│       └── alertas/
├── infrastructure/
│   ├── terraform/
│   └── scripts/
├── docs/
├── .github/
│   └── workflows/
├── README.md
└── docker-compose.yml
```

## Pruebas locales

Cada microservicio incluye pruebas con `unittest` y mocks de `boto3`, sin conectarse a AWS:

```bash
cd backend/functions/productos
python3 -m unittest discover tests

cd ../clientes
python3 -m unittest discover tests

cd ../ventas
python3 -m unittest discover tests

cd ../reportes
python3 -m unittest discover tests

cd ../alertas
python3 -m unittest discover tests
```

## Infraestructura

Los archivos Terraform se encuentran en `infrastructure/terraform/`.

Comandos de validacion usados durante el desarrollo:

```bash
cd infrastructure/terraform
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

Para crear la suscripcion por correo de alertas:

```bash
terraform plan -var="alertas_email=correo@example.com" -out=tfplan
```

No ejecutar `terraform apply` sin revisar antes el plan.

## Seguridad

- No incluir credenciales ni claves de AWS en el repositorio.
- No versionar archivos `.env` reales.
- Usar variables de entorno, perfiles AWS o mecanismos seguros para credenciales.
