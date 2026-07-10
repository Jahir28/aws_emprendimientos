"""Punto de entrada de la Lambda Alertas."""

import logging

from responses import internal_error
from service import generate_low_stock_alerts

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """Procesa eventos programados de EventBridge y genera alertas de stock."""
    try:
        logger.info("Iniciando revision automatica de stock bajo.")
        return generate_low_stock_alerts()
    except Exception:
        logger.exception("Error inesperado al procesar la Lambda Alertas.")
        return internal_error("Ocurrio un error interno al procesar la solicitud.")
