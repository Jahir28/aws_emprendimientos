<template>
  <div class="view-stack">
    <PageHeader
      eyebrow="Relaciones"
      title="Clientes"
      description="Directorio visual para seguimiento comercial y atención al cliente."
    >
      <template #actions>
        <button class="btn btn-primary" type="button">
          <i class="pi pi-user-plus"></i>
          Nuevo cliente
        </button>
      </template>
    </PageHeader>

    <section class="card panel toolbar">
      <input v-model="search" class="input" type="search" placeholder="Buscar cliente" />
      <span class="muted">{{ filteredClients.length }} clientes visibles</span>
    </section>

    <section class="card table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Teléfono</th>
              <th>Fecha de registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in filteredClients" :key="client.id">
              <td>
                <div class="client-name">
                  <span class="avatar">{{ initials(client.name) }}</span>
                  <strong>{{ client.name }}</strong>
                </div>
              </td>
              <td>{{ client.email }}</td>
              <td>{{ client.phone }}</td>
              <td>{{ client.registeredAt }}</td>
              <td>
                <div class="actions">
                  <button class="icon-button" type="button" aria-label="Editar cliente">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="icon-button" type="button" aria-label="Eliminar cliente">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-if="filteredClients.length === 0" icon="pi pi-users" />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import EmptyState from '../components/common/EmptyState.vue'
import PageHeader from '../components/common/PageHeader.vue'

const search = ref('')

const clients = [
  { id: 'c-01', name: 'María González', email: 'cliente1@example.com', phone: '+507 6000-1001', registeredAt: '2026-07-01' },
  { id: 'c-02', name: 'Carlos Pérez', email: 'cliente2@example.com', phone: '+507 6000-1002', registeredAt: '2026-07-03' },
  { id: 'c-03', name: 'Lucía Torres', email: 'cliente3@example.com', phone: '+507 6000-1003', registeredAt: '2026-07-05' },
  { id: 'c-04', name: 'Andrés Molina', email: 'cliente4@example.com', phone: '+507 6000-1004', registeredAt: '2026-07-08' },
]

const filteredClients = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return clients
  return clients.filter((client) =>
    [client.name, client.email, client.phone].some((value) => value.toLowerCase().includes(term)),
  )
})

const initials = (name) =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
</script>

<style scoped>
.view-stack {
  display: grid;
  gap: 18px;
}

.client-name {
  display: inline-flex;
  align-items: center;
  gap: 11px;
}

.avatar {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 50%;
  color: #fff;
  background: #20314f;
  font-size: 0.78rem;
  font-weight: 900;
  box-shadow: inset 0 -10px 18px rgba(255, 153, 0, 0.14);
}
</style>
