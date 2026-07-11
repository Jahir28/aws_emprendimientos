import api from './api'

export const getSales = async () => {
  const response = await api.get('/ventas')
  return response.data.data
}

export const getSaleById = async (id) => {
  const response = await api.get(`/ventas/${id}`)
  return response.data.data
}

export const createSale = async (payload) => {
  const response = await api.post('/ventas', payload)
  return response.data.data
}

export const annulSale = async (id) => {
  const response = await api.post(`/ventas/${id}/anular`)
  return response.data.data
}
