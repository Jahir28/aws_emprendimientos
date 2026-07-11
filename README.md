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
- Registro, consulta, listado y anulacion segura de ventas.
- Validacion de cliente y producto antes de registrar ventas.
- Descuento transaccional de stock al registrar ventas.
- Devolucion transaccional de stock al anular ventas.
- Dashboard y reportes conectados a la API real con metricas operativas, productos mas vendidos y clientes frecuentes.
- Presentacion clara de ingresos, ventas completadas, ventas anuladas, ticket promedio e inventario.
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

- Rutas: `GET /ventas`, `POST /ventas`, `GET /ventas/{id}`, `POST /ventas/{id}/anular`.
- Tabla DynamoDB: `aws-emprendimientos-dev-ventas`.
- Variables de entorno: `VENTAS_TABLE`, `CLIENTES_TABLE`, `PRODUCTOS_TABLE`.
- No implementa `PUT`, porque una venta registrada no debe modificarse directamente.
- No expone eliminacion fisica desde la interfaz.
- Las ventas nuevas se guardan con `estado = "completada"`.
- Las ventas antiguas sin campo `estado` se interpretan como completadas.
- La anulacion cambia `estado` a `"anulada"`, registra `anulada_at` y devuelve el stock al producto.
- La creacion y la anulacion usan operaciones transaccionales de DynamoDB para evitar cambios parciales entre Ventas y Productos.

### Reportes

- Rutas: `GET /reportes/resumen`, `GET /reportes/productos-mas-vendidos`, `GET /reportes/clientes-frecuentes`.
- Variables de entorno: `PRODUCTOS_TABLE`, `CLIENTES_TABLE`, `VENTAS_TABLE`.
- Acceso de solo lectura a DynamoDB.
- Los ingresos, ventas activas, ticket promedio, productos mas vendidos y clientes frecuentes consideran solo ventas completadas.
- Las ventas anuladas no suman ingresos y pueden reportarse como metrica separada.
- Las ventas antiguas sin `estado` se tratan como completadas para mantener compatibilidad historica.
- El ticket promedio se presenta en frontend como `ingresos_totales / total_ventas`, sin incluir ventas anuladas.

### Alertas

- Ejecucion programada mediante EventBridge.
- Consulta productos con `Scan` paginado.
- Publica una alerta consolidada en SNS cuando hay productos con bajo stock.
- Variables de entorno: `PRODUCTOS_TABLE`, `SNS_TOPIC_ARN`, `STOCK_MINIMO`.

## Frontend

El frontend esta en `frontend/` y contiene la base visual de **ControlPyme**:

- Layout administrativo responsive.
- Sidebar con navegacion principal.
- Dashboard integrado con datos reales de reportes, productos y ventas.
- Tarjetas de metricas con textos descriptivos y tooltips discretos para ingresos, ticket promedio y ventas anuladas.
- Resumen de inventario con productos registrados, stock bajo, unidades vendidas y valor estimado.
- Productos integrado con API real.
- Clientes integrado con API real.
- Ventas integrado con API real, incluyendo registro y anulacion segura.
- Reportes integrados con API real y graficas Chart.js para productos mas vendidos y clientes frecuentes.
- Instancia Axios configurada mediante `VITE_API_BASE_URL`.

Metricas principales mostradas en Dashboard y Reportes:

- `ingresos_totales`: ingresos generados por ventas completadas.
- `total_ventas`: cantidad de ventas completadas.
- `ventas_anuladas`: ventas anuladas que no generan ingresos.
- `ticket_promedio`: ingreso promedio por venta completada.
- `unidades_vendidas`: unidades vendidas, presentada dentro del resumen de inventario.
- `productos_bajo_stock`: productos con stock menor o igual al umbral visual de bajo stock.
- `valor_inventario`: valor estimado del inventario.

Variable de entorno del frontend:

```bash
VITE_API_BASE_URL=https://example.execute-api.us-west-2.amazonaws.com/dev
```

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

Para conservar la suscripcion de alertas ya configurada durante planes posteriores, usar la misma variable `alertas_email`.

No ejecutar `terraform apply` sin revisar antes el plan.

## Seguridad

- No incluir credenciales ni claves de AWS en el repositorio.
- No versionar archivos `.env` reales.
- Usar variables de entorno, perfiles AWS o mecanismos seguros para credenciales.
