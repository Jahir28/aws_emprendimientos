import api from './api'

const extractData = (response, fallback) => response?.data?.data ?? fallback

const normalizeSummary = (summary = {}) => ({
  total_productos: Number(summary.total_productos || 0),
  total_clientes: Number(summary.total_clientes || 0),
  total_ventas: Number(summary.total_ventas || 0),
  ventas_anuladas: Number(summary.ventas_anuladas || 0),
  ingresos_totales: Number(summary.ingresos_totales || 0),
  unidades_vendidas: Number(summary.unidades_vendidas || 0),
  productos_bajo_stock: Number(summary.productos_bajo_stock || 0),
  valor_inventario: Number(summary.valor_inventario || 0),
})

const normalizeTopProduct = (product = {}) => ({
  producto_id: product.producto_id || '',
  producto_nombre: product.producto_nombre || 'Producto sin nombre',
  cantidad_vendida: Number(product.cantidad_vendida || 0),
  ingresos: Number(product.ingresos || 0),
})

const normalizeFrequentClient = (client = {}) => ({
  cliente_id: client.cliente_id || '',
  cliente_nombre: client.cliente_nombre || 'Cliente sin nombre',
  cantidad_ventas: Number(client.cantidad_ventas || 0),
  total_gastado: Number(client.total_gastado || 0),
})

export const getSummaryReport = async () => {
  const response = await api.get('/reportes/resumen')
  return normalizeSummary(extractData(response, {}))
}

export const getTopProductsReport = async () => {
  const response = await api.get('/reportes/productos-mas-vendidos')
  return extractData(response, []).map(normalizeTopProduct)
}

export const getFrequentClientsReport = async () => {
  const response = await api.get('/reportes/clientes-frecuentes')
  return extractData(response, []).map(normalizeFrequentClient)
}

export const getReportsOverview = async () => {
  const [summary, topProducts, frequentClients] = await Promise.all([
    getSummaryReport(),
    getTopProductsReport(),
    getFrequentClientsReport(),
  ])

  return {
    summary,
    topProducts,
    frequentClients,
  }
}
