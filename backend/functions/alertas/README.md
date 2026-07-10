# Lambda Alertas

Componente de alertas automaticas de bajo stock para AWS Emprendimientos.

La Lambda esta pensada para ejecutarse periodicamente mediante Amazon EventBridge. Consulta todos los productos en DynamoDB, identifica los productos cuyo `stock` sea menor o igual al limite configurado y publica una unica notificacion consolidada en Amazon SNS.

## Flujo

`EventBridge` ejecuta la regla programada, invoca la `Lambda`, la Lambda consulta productos en `DynamoDB` mediante `Scan` con paginacion y, si encuentra productos con bajo stock, publica una alerta consolidada en `SNS`.

## Variables de entorno

- `PRODUCTOS_TABLE`: nombre de la tabla DynamoDB de productos. Obligatoria.
- `SNS_TOPIC_ARN`: ARN del tema SNS donde se publica la alerta. Obligatoria.
- `STOCK_MINIMO`: limite de stock bajo. Opcional, acepta solo enteros no negativos y usa `5` como valor predeterminado.

## Respuesta

La respuesta incluye:

- `productos_revisados`
- `productos_bajo_stock`
- `notificacion_enviada`
- `message_id`, cuando SNS confirma la publicacion

## Pruebas

Desde `backend/functions/alertas`:

```bash
python3 -m unittest discover tests
```
