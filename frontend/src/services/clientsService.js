import api from './api'

export const getClients = async () => {
  const response = await api.get('/clientes')
  return response.data.data
}

export const getClientById = async (id) => {
  const response = await api.get(`/clientes/${id}`)
  return response.data.data
}

export const createClient = async (payload) => {
  const response = await api.post('/clientes', payload)
  return response.data.data
}

export const updateClient = async (id, payload) => {
  const response = await api.put(`/clientes/${id}`, payload)
  return response.data.data
}

export const deleteClient = async (id) => {
  const response = await api.delete(`/clientes/${id}`)
  return response.data.data
}
