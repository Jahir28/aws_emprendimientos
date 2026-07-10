# ControlPyme Frontend

Frontend administrativo para el proyecto `aws_emprendimientos`, construido con Vue 3 y Vite.

## Tecnologias

- Vue 3
- Vite
- Vue Router
- Axios
- PrimeVue
- PrimeIcons
- Chart.js
- vue-chartjs

## Vistas

- Dashboard
- Productos
- Clientes
- Ventas
- Reportes
- Pagina 404

Las vistas usan datos simulados temporalmente. La conexion real con API Gateway queda preparada mediante Axios, pero aun no esta integrada en las pantallas.

## Variables de entorno

Crear un archivo `.env` local basado en `.env.example`:

```bash
VITE_API_BASE_URL=https://example.execute-api.us-west-2.amazonaws.com/dev
```

## Comandos

```bash
npm install
npm run dev
npm run build
npm run preview
```

## Estructura principal

```text
src/
├── assets/styles/
├── components/
│   ├── common/
│   ├── dashboard/
│   └── layout/
├── router/
├── services/
└── views/
```

## Estado

La base visual esta implementada con identidad inspirada en AWS: azul oscuro, acento naranja, fondo claro, tarjetas blancas, graficas y layout responsive.
