# ControlPyme Frontend

Frontend administrativo para el proyecto `aws_emprendimientos`, construido con Vue 3 y Vite.

La interfaz se presenta como **ControlPyme**, un panel administrativo responsive para gestionar productos, clientes, ventas y reportes operativos desde la API real del proyecto.

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

Las vistas principales consumen datos reales mediante los servicios ubicados en `src/services/` y la instancia Axios configurada con `VITE_API_BASE_URL`.

## Dashboard y Reportes

El Dashboard y la vista de Reportes muestran metricas calculadas por la API de reportes:

- Ingresos totales: ingresos de ventas completadas.
- Ventas completadas: total de ventas activas usadas para los calculos.
- Ventas anuladas: ventas que no generan ingresos.
- Ticket promedio: `ingresos_totales / total_ventas`.
- Unidades vendidas: presentada dentro del resumen de inventario.
- Productos registrados, stock bajo y valor estimado de inventario.

La presentacion usa tarjetas, tooltips discretos de PrimeVue y graficas Chart.js para facilitar la lectura durante una demostracion sin modificar la logica de calculo del backend.

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
