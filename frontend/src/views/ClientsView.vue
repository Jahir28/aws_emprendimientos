<template>
  <div class="view-stack">
    <Toast />
    <ConfirmDialog />

    <PageHeader
      eyebrow="Relaciones"
      title="Clientes"
      description="Directorio visual para seguimiento comercial y atención al cliente."
    >
      <template #actions>
        <button class="btn btn-primary" type="button" :disabled="isSaving" @click="openCreateModal">
          <i class="pi pi-user-plus"></i>
          Nuevo cliente
        </button>
      </template>
    </PageHeader>

    <section class="card panel toolbar">
      <input v-model="search" class="input" type="search" placeholder="Buscar cliente" />
      <span class="muted">{{ filteredClients.length }} clientes visibles</span>
    </section>

    <section v-if="errorMessage" class="card panel error-panel">
      <i class="pi pi-exclamation-circle"></i>
      <div>
        <strong>No se pudieron cargar los clientes</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="loadClients">
        Reintentar
      </button>
    </section>

    <section class="card table-card">
      <div v-if="isLoading" class="state-panel">
        <LoadingState label="Cargando clientes desde AWS..." />
      </div>

      <div class="table-wrap">
        <table v-if="!isLoading && filteredClients.length > 0" class="data-table">
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
            <tr v-for="client in filteredClients" :key="client.cliente_id">
              <td>
                <div class="client-name">
                  <span class="avatar">{{ initials(client.nombre) }}</span>
                  <strong>{{ client.nombre }}</strong>
                </div>
              </td>
              <td>{{ client.correo }}</td>
              <td>{{ client.telefono || 'Sin teléfono' }}</td>
              <td>{{ formatDate(client.created_at) }}</td>
              <td>
                <div class="actions">
                  <button
                    class="icon-button"
                    type="button"
                    aria-label="Editar cliente"
                    :disabled="isSaving || deletingId === client.cliente_id"
                    @click="openEditModal(client)"
                  >
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button
                    class="icon-button"
                    type="button"
                    aria-label="Eliminar cliente"
                    :disabled="isSaving || deletingId === client.cliente_id"
                    @click="confirmDelete(client)"
                  >
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <EmptyState
        v-if="!isLoading && !errorMessage && filteredClients.length === 0"
        icon="pi pi-users"
        title="Sin clientes"
        message="No hay clientes registrados o no coinciden con la búsqueda aplicada."
      />
    </section>

    <Dialog
      v-model:visible="isModalVisible"
      modal
      :header="modalTitle"
      class="client-dialog product-dialog"
    >
      <form class="product-form" @submit.prevent="submitClient">
        <label>
          <span>Nombre completo</span>
          <input
            v-model.trim="form.nombre"
            class="input"
            type="text"
            placeholder="Juan Pérez"
            autocomplete="off"
          />
          <small v-if="formErrors.nombre">{{ formErrors.nombre }}</small>
        </label>

        <label>
          <span>Correo</span>
          <input v-model.trim="form.correo" class="input" type="email" autocomplete="off" />
          <small v-if="formErrors.correo">{{ formErrors.correo }}</small>
        </label>

        <label>
          <span>Teléfono</span>
          <input v-model.trim="form.telefono" class="input" type="text" autocomplete="off" />
        </label>

        <label>
          <span>Dirección</span>
          <textarea v-model.trim="form.direccion" class="textarea" rows="3"></textarea>
        </label>

        <div class="modal-actions">
          <button class="btn btn-secondary" type="button" :disabled="isSaving" @click="closeModal">
            Cancelar
          </button>
          <button class="btn btn-primary" type="submit" :disabled="isSaving">
            <i :class="isSaving ? 'pi pi-spin pi-spinner' : 'pi pi-save'"></i>
            {{ isSaving ? 'Guardando...' : 'Guardar cliente' }}
          </button>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import ConfirmDialog from 'primevue/confirmdialog'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

import EmptyState from '../components/common/EmptyState.vue'
import LoadingState from '../components/common/LoadingState.vue'
import PageHeader from '../components/common/PageHeader.vue'
import {
  createClient,
  deleteClient,
  getClients,
  updateClient,
} from '../services/clientsService'

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

const search = ref('')
const clients = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const deletingId = ref('')
const errorMessage = ref('')
const isModalVisible = ref(false)
const editingClientId = ref('')
const toast = useToast()
const confirm = useConfirm()

const emptyForm = () => ({
  nombre: '',
  correo: '',
  telefono: '',
  direccion: '',
})

const form = reactive(emptyForm())
const formErrors = reactive({
  nombre: '',
  correo: '',
})

const modalTitle = computed(() =>
  editingClientId.value ? 'Editar cliente' : 'Nuevo cliente',
)

const filteredClients = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return clients.value

  return clients.value.filter((client) =>
    [client.nombre, client.correo, client.telefono]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(term)),
  )
})

const initials = (name = '') =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

const formatDate = (value) => {
  if (!value) return 'Sin fecha'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('es-PA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

const getErrorMessage = (error) =>
  error?.response?.data?.message || error?.message || 'Ocurrió un error inesperado.'

const loadClients = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    clients.value = await getClients()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
    toast.add({
      severity: 'error',
      summary: 'Error al cargar clientes',
      detail: errorMessage.value,
      life: 4500,
    })
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  Object.assign(form, emptyForm())
  clearFormErrors()
  editingClientId.value = ''
}

const clearFormErrors = () => {
  formErrors.nombre = ''
  formErrors.correo = ''
}

const validateForm = () => {
  clearFormErrors()

  if (!form.nombre) {
    formErrors.nombre = 'El nombre es obligatorio.'
  }

  if (!form.correo) {
    formErrors.correo = 'El correo es obligatorio.'
  } else if (!EMAIL_PATTERN.test(form.correo)) {
    formErrors.correo = 'El correo debe tener un formato válido.'
  }

  return !formErrors.nombre && !formErrors.correo
}

const buildPayload = () => ({
  nombre: form.nombre,
  correo: form.correo,
  telefono: form.telefono,
  direccion: form.direccion,
})

const openCreateModal = () => {
  resetForm()
  isModalVisible.value = true
}

const openEditModal = (client) => {
  clearFormErrors()
  editingClientId.value = client.cliente_id
  form.nombre = client.nombre || ''
  form.correo = client.correo || ''
  form.telefono = client.telefono || ''
  form.direccion = client.direccion || ''
  isModalVisible.value = true
}

const closeModal = () => {
  if (isSaving.value) return
  isModalVisible.value = false
  resetForm()
}

const submitClient = async () => {
  if (isSaving.value || !validateForm()) return

  isSaving.value = true
  try {
    if (editingClientId.value) {
      await updateClient(editingClientId.value, buildPayload())
      toast.add({
        severity: 'success',
        summary: 'Cliente actualizado',
        detail: 'Los cambios se guardaron correctamente.',
        life: 3200,
      })
    } else {
      await createClient(buildPayload())
      toast.add({
        severity: 'success',
        summary: 'Cliente creado',
        detail: 'El cliente se registró correctamente.',
        life: 3200,
      })
    }

    isModalVisible.value = false
    resetForm()
    await loadClients()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo guardar',
      detail: getErrorMessage(error),
      life: 4500,
    })
  } finally {
    isSaving.value = false
  }
}

const confirmDelete = (client) => {
  confirm.require({
    message: `¿Deseas eliminar "${client.nombre}"? Esta acción no se puede deshacer.`,
    header: 'Eliminar cliente',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Eliminar',
    acceptIcon: 'pi pi-trash',
    acceptClass: 'confirm-danger',
    accept: () => removeClient(client),
  })
}

const removeClient = async (client) => {
  if (deletingId.value) return

  deletingId.value = client.cliente_id
  try {
    await deleteClient(client.cliente_id)
    clients.value = clients.value.filter((item) => item.cliente_id !== client.cliente_id)
    toast.add({
      severity: 'success',
      summary: 'Cliente eliminado',
      detail: 'El cliente se eliminó correctamente.',
      life: 3200,
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo eliminar',
      detail: getErrorMessage(error),
      life: 4500,
    })
  } finally {
    deletingId.value = ''
  }
}

onMounted(loadClients)
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

.state-panel {
  min-height: 220px;
  display: grid;
  place-items: center;
}

.error-panel {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  border-color: rgba(189, 52, 52, 0.22);
  background: #fff8f8;
}

.error-panel > i {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: var(--danger);
  background: #fff1f1;
}

.error-panel strong,
.error-panel p {
  display: block;
}

.error-panel p {
  margin: 2px 0 0;
  color: var(--text-muted);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
  transform: none;
}

@media (max-width: 720px) {
  .error-panel {
    grid-template-columns: 1fr;
  }
}
</style>
