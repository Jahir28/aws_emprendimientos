import api from './api'

export const getProducts = async () => {
  const response = await api.get('/productos')
  return response.data.data
}

export const getProductById = async (id) => {
  const response = await api.get(`/productos/${id}`)
  return response.data.data
}

export const createProduct = async (payload) => {
  const response = await api.post('/productos', payload)
  return response.data.data
}

export const updateProduct = async (id, payload) => {
  const response = await api.put(`/productos/${id}`, payload)
  return response.data.data
}

export const deleteProduct = async (id) => {
  const response = await api.delete(`/productos/${id}`)
  return response.data.data
}
