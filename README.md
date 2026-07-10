# aws_emprendimientos

Proyecto universitario para gestionar procesos basicos de emprendimientos mediante una arquitectura serverless en AWS.

## Descripcion del proyecto

`aws_emprendimientos` es una aplicacion web orientada a la administracion de productos, clientes y ventas para pequenos emprendimientos. El proyecto separa el frontend, las funciones backend, la infraestructura como codigo y la automatizacion de CI/CD para facilitar el desarrollo incremental y ordenado.

## Objetivo

Construir una solucion academica con practicas modernas de desarrollo cloud, usando servicios administrados de AWS y una estructura preparada para evolucionar hacia despliegues automatizados, pruebas y documentacion tecnica.

## Funcionalidades

- Gestion de productos mediante una Lambda CRUD conectada a DynamoDB.
- Gestion de clientes mediante una Lambda CRUD conectada a DynamoDB.
- Registro, consulta, listado y eliminacion de ventas.
- Validacion de cliente y producto antes de registrar una venta.
- Descuento condicional de stock al registrar ventas.
- Exposicion de servicios mediante Amazon API Gateway HTTP API.
- Persistencia de datos en tablas Amazon DynamoDB independientes por dominio.
- Reportes y alertas se mantienen como modulos previstos para futuras iteraciones.

## Arquitectura

La arquitectura esta basada en componentes serverless:

- El frontend sera desarrollado con Vue 3 y Vite.
- La API publica se expone mediante Amazon API Gateway HTTP API.
- La logica de negocio se implementa en funciones AWS Lambda escritas en Python 3.13.
- Los datos se almacenan en Amazon DynamoDB.
- Cada microservicio usa su propia tabla DynamoDB y su propio rol IAM de ejecucion.
- La infraestructura se define con Terraform.
- La automatizacion del flujo de trabajo se preparara con GitHub Actions.
- La region AWS objetivo sera `us-west-2`.

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

## Tecnologias

- Vue 3
- Vite
- Python
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Terraform
- GitHub Actions
- Docker Compose para apoyo futuro en desarrollo local
- Ubuntu en WSL

## Estructura de carpetas

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
│   │   └── modules/
│   └── scripts/
├── docs/
├── .github/
│   └── workflows/
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Estado actual del proyecto

El repositorio ya contiene los microservicios backend de Productos, Clientes y Ventas con pruebas unitarias y acceso a DynamoDB mediante `boto3`. La infraestructura Terraform incluye tablas DynamoDB, funciones Lambda, roles IAM, grupos de logs e integracion con API Gateway HTTP API para esos microservicios.

El frontend con Vue 3 + Vite aun no ha sido inicializado. Los modulos de Reportes y Alertas siguen pendientes para futuras iteraciones.

## Pruebas locales

Cada microservicio incluye pruebas con `unittest` y mocks de `boto3`, sin conectarse a AWS:

```bash
cd backend/functions/productos
python3 -m unittest discover tests

cd ../clientes
python3 -m unittest discover tests

cd ../ventas
python3 -m unittest discover tests
```

## Infraestructura

Los archivos Terraform se encuentran en `infrastructure/terraform/`.

Comandos de validacion usados durante el desarrollo:

```bash
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

No se deben incluir credenciales, claves de AWS ni archivos sensibles en el repositorio.
