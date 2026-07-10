# Lambda Reportes

Funcion AWS Lambda en Python 3.13 para generar reportes de Productos, Clientes y Ventas. Usa Amazon DynamoDB mediante `boto3` y esta preparada para eventos de Amazon API Gateway HTTP API v2, manteniendo compatibilidad con REST API v1.

## Variables de entorno

- `PRODUCTOS_TABLE`
- `CLIENTES_TABLE`
- `VENTAS_TABLE`

## Rutas soportadas

- `GET /reportes/resumen`
- `GET /reportes/productos-mas-vendidos`
- `GET /reportes/clientes-frecuentes`

No se implementan `POST`, `PUT` ni `DELETE`. El servicio solo lee datos.

## Reportes

- `resumen`: totales generales, ingresos, unidades vendidas, productos con bajo stock y valor de inventario.
- `productos-mas-vendidos`: agrega ventas por producto y devuelve los 10 primeros por cantidad vendida.
- `clientes-frecuentes`: agrega ventas por cliente y devuelve los 10 primeros por total gastado.

## Ejecutar pruebas

Desde esta carpeta:

```bash
python3 -m unittest discover tests
```

Las pruebas mockean `boto3`; no se conectan a AWS.

