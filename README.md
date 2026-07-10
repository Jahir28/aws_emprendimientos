# aws_emprendimientos

Proyecto universitario para gestionar procesos basicos de emprendimientos mediante una arquitectura serverless en AWS.

## Descripcion del proyecto

`aws_emprendimientos` es una aplicacion web orientada a la administracion de productos, clientes, ventas, reportes y alertas para pequenos emprendimientos. El proyecto separa el frontend, las funciones backend, la infraestructura como codigo y la automatizacion de CI/CD para facilitar el desarrollo incremental y ordenado.

## Objetivo

Construir una solucion academica con practicas modernas de desarrollo cloud, usando servicios administrados de AWS y una estructura preparada para evolucionar hacia despliegues automatizados, pruebas y documentacion tecnica.

## Funcionalidades previstas

- Gestion de productos.
- Gestion de clientes.
- Registro y consulta de ventas.
- Generacion de reportes.
- Alertas operativas o de negocio.
- Exposicion de servicios mediante API Gateway.
- Persistencia de datos en DynamoDB.

## Arquitectura

La arquitectura prevista esta basada en componentes serverless:

- El frontend sera desarrollado con Vue 3 y Vite.
- La API publica sera expuesta mediante Amazon API Gateway.
- La logica de negocio se implementara en funciones AWS Lambda escritas en Python.
- Los datos se almacenaran en Amazon DynamoDB.
- La infraestructura se definira con Terraform.
- La automatizacion del flujo de trabajo se preparara con GitHub Actions.
- La region AWS objetivo sera `us-west-2`.

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

El repositorio contiene la estructura inicial del proyecto. Aun no se ha inicializado Vue, no se han escrito funciones Lambda, no se ha inicializado Terraform y no se han creado recursos reales en AWS.

