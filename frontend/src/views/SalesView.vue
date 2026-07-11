<template>
  <div class="view-stack">
    <Toast />
    <ConfirmDialog />

    <PageHeader
      eyebrow="Operación"
      title="Ventas"
      description="Seguimiento de transacciones y rendimiento comercial del emprendimiento."
    >
      <template #actions>
        <button
          class="btn btn-primary"
          type="button"
          :disabled="isSaving || isLoadingReferences"
          @click="openCreateModal"
        >
          <i class="pi pi-plus-circle"></i>
          Registrar venta
        </button>
      </template>
    </PageHeader>

    <section class="mini-summary">
      <article class="summary-card card">
        <span><i class="pi pi-wallet"></i> Total registrado</span>
        <strong>{{ formatCurrency(totalRevenue) }}</strong>
      </article>
      <article class="summary-card card">
        <span><i class="pi pi-check-circle"></i> Ventas registradas</span>
        <strong>{{ completedSales.length }}</strong>
      </article>
      <article class="summary-card card">
        <span><i class="pi pi-chart-line"></i> Ticket promedio</span>
        <strong>{{ formatCurrency(averageTicket) }}</strong>
      </article>
    </section>

    <section v-if="errorMessage" class="card panel error-panel">
      <i class="pi pi-exclamation-circle"></i>
      <div>
        <strong>No se pudieron cargar las ventas</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="loadInitialData">
        Reintentar
      </button>
    </section>

    <section class="card table-card">
      <div v-if="isLoading" class="state-panel">
        <LoadingState label="Cargando ventas desde AWS..." />
      </div>

      <div class="table-wrap">
        <table v-if="!isLoading && sales.length > 0" class="data-table">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Total</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in sales" :key="sale.venta_id">
              <td><strong>{{ resolveClientName(sale) }}</strong></td>
              <td>{{ resolveProductName(sale) }}</td>
              <td>{{ sale.cantidad }}</td>
              <td>{{ formatCurrency(sale.total) }}</td>
              <td>{{ formatDate(sale.fecha || sale.created_at) }}</td>
              <td>
                <StatusBadge :label="statusLabel(sale)" :variant="statusVariant(sale)" />
              </td>
              <td>
                <button
                  v-if="isCompletedSale(sale)"
                  class="icon-button"
                  type="button"
                  aria-label="Anular venta"
                  :disabled="annullingId === sale.venta_id || isSaving"
                  @click="confirmAnnul(sale)"
                >
                  <i class="pi pi-ban"></i>
                </button>
                <span v-else class="muted">Sin acción</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!isLoading && sales.length > 0" class="history-note">
        <i class="pi pi-history"></i>
        Las ventas registradas se conservan como historial de transacciones.
      </div>

      <EmptyState
        v-if="!isLoading && !errorMessage && sales.length === 0"
        icon="pi pi-shopping-cart"
        title="Sin ventas"
        message="No hay ventas registradas por ahora."
      />
    </section>

    <Dialog
      v-model:visible="isModalVisible"
      modal
      header="Registrar venta"
      class="sale-dialog product-dialog"
    >
      <form class="product-form" @submit.prevent="submitSale">
        <label>
          <span>Cliente</span>
          <select v-model="form.cliente_id" class="select">
            <option value="">Seleccionar cliente</option>
            <option v-for="client in clients" :key="client.cliente_id" :value="client.cliente_id">
              {{ client.nombre }}
            </option>
          </select>
          <small v-if="formErrors.cliente_id">{{ formErrors.cliente_id }}</small>
        </label>

        <label>
          <span>Producto</span>
          <select v-model="form.producto_id" class="select">
            <option value="">Seleccionar producto</option>
            <option
              v-for="product in products"
              :key="product.producto_id"
              :value="product.producto_id"
              :disabled="normalizeStock(product.stock) === 0"
            >
              {{ product.nombre }} - stock: {{ normalizeStock(product.stock) }}
            </option>
          </select>
          <small v-if="formErrors.producto_id">{{ formErrors.producto_id }}</small>
        </label>

        <div v-if="selectedProduct" class="stock-help">
          <i class="pi pi-box"></i>
          Stock disponible: <strong>{{ selectedProductStock }}</strong>
        </div>

        <label>
          <span>Cantidad</span>
          <input v-model="form.cantidad" class="input" type="number" min="1" step="1" />
          <small v-if="formErrors.cantidad">{{ formErrors.cantidad }}</small>
        </label>

        <div class="modal-actions">
          <button class="btn btn-secondary" type="button" :disabled="isSaving" @click="closeModal">
            Cancelar
          </button>
          <button class="btn btn-primary" type="submit" :disabled="isSaving">
            <i :class="isSaving ? 'pi pi-spin pi-spinner' : 'pi pi-save'"></i>
            {{ isSaving ? 'Registrando...' : 'Registrar venta' }}
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
import StatusBadge from '../components/common/StatusBadge.vue'
import { getClients } from '../services/clientsService'
import { getProducts } from '../services/productsService'
import { annulSale, createSale, getSales } from '../services/salesService'

const sales = ref([])
const clients = ref([])
const products = ref([])
const isLoading = ref(false)
const isLoadingReferences = ref(false)
const isSaving = ref(false)
const annullingId = ref('')
const errorMessage = ref('')
const isModalVisible = ref(false)
const toast = useToast()
const confirm = useConfirm()

const emptyForm = () => ({
  cliente_id: '',
  producto_id: '',
  cantidad: 1,
})

const form = reactive(emptyForm())
const formErrors = reactive({
  cliente_id: '',
  producto_id: '',
  cantidad: '',
})

const clientsById = computed(() =>
  clients.value.reduce((acc, client) => {
    acc[client.cliente_id] = client
    return acc
  }, {}),
)

const productsById = computed(() =>
  products.value.reduce((acc, product) => {
    acc[product.producto_id] = product
    return acc
  }, {}),
)

const selectedProduct = computed(() => productsById.value[form.producto_id])
const selectedProductStock = computed(() => normalizeStock(selectedProduct.value?.stock))
const completedSales = computed(() => sales.value.filter((sale) => isCompletedSale(sale)))

const totalRevenue = computed(() =>
  completedSales.value.reduce((total, sale) => total + Number(sale.total || 0), 0),
)

const averageTicket = computed(() =>
  completedSales.value.length > 0 ? totalRevenue.value / completedSales.value.length : 0,
)

const isCompletedSale = (sale) => (sale.estado || 'completada') !== 'anulada'

const statusLabel = (sale) => (isCompletedSale(sale) ? 'Completada' : 'Anulada')

const statusVariant = (sale) => (isCompletedSale(sale) ? 'success' : 'danger')

const normalizeStock = (stock) => Number(stock || 0)

const formatCurrency = (value) =>
  new Intl.NumberFormat('es-PA', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0))

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

const resolveClientName = (sale) =>
  sale.cliente_nombre || clientsById.value[sale.cliente_id]?.nombre || 'Cliente no disponible'

const resolveProductName = (sale) =>
  sale.producto_nombre || productsById.value[sale.producto_id]?.nombre || 'Producto no disponible'

const getErrorMessage = (error) =>
  error?.response?.data?.message || error?.message || 'Ocurrió un error inesperado.'

const loadInitialData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const [salesData, clientsData, productsData] = await Promise.all([
      getSales(),
      getClients(),
      getProducts(),
    ])
    sales.value = salesData
    clients.value = clientsData
    products.value = productsData
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
    toast.add({
      severity: 'error',
      summary: 'Error al cargar ventas',
      detail: errorMessage.value,
      life: 4500,
    })
  } finally {
    isLoading.value = false
  }
}

const refreshProducts = async () => {
  products.value = await getProducts()
}

const resetForm = () => {
  Object.assign(form, emptyForm())
  clearFormErrors()
}

const clearFormErrors = () => {
  formErrors.cliente_id = ''
  formErrors.producto_id = ''
  formErrors.cantidad = ''
}

const validateForm = () => {
  clearFormErrors()
  const quantity = Number(form.cantidad)

  if (!form.cliente_id) {
    formErrors.cliente_id = 'Debes seleccionar un cliente.'
  }

  if (!form.producto_id) {
    formErrors.producto_id = 'Debes seleccionar un producto.'
  }

  if (!Number.isInteger(quantity) || quantity <= 0) {
    formErrors.cantidad = 'La cantidad debe ser un entero mayor que cero.'
  } else if (selectedProduct.value && quantity > selectedProductStock.value) {
    formErrors.cantidad = 'La cantidad no puede superar el stock disponible.'
  }

  return !formErrors.cliente_id && !formErrors.producto_id && !formErrors.cantidad
}

const buildPayload = () => ({
  cliente_id: form.cliente_id,
  producto_id: form.producto_id,
  cantidad: Number(form.cantidad),
})

const openCreateModal = async () => {
  resetForm()
  isLoadingReferences.value = true

  try {
    const [clientsData, productsData] = await Promise.all([getClients(), getProducts()])
    clients.value = clientsData
    products.value = productsData
    isModalVisible.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo preparar la venta',
      detail: getErrorMessage(error),
      life: 4500,
    })
  } finally {
    isLoadingReferences.value = false
  }
}

const closeModal = () => {
  if (isSaving.value) return
  isModalVisible.value = false
  resetForm()
}

const submitSale = async () => {
  if (isSaving.value || !validateForm()) return

  isSaving.value = true
  try {
    await createSale(buildPayload())
    toast.add({
      severity: 'success',
      summary: 'Venta registrada',
      detail: 'La venta se registró correctamente.',
      life: 3200,
    })
    isModalVisible.value = false
    resetForm()

    const [salesData] = await Promise.all([
      getSales(),
      refreshProducts(),
    ])
    sales.value = salesData
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo registrar',
      detail: getErrorMessage(error),
      life: 4500,
    })
  } finally {
    isSaving.value = false
  }
}

const confirmAnnul = (sale) => {
  confirm.require({
    header: 'Anular venta',
    message:
      `¿Deseas anular la venta de ${resolveClientName(sale)} por ` +
      `${sale.cantidad} unidad(es) de ${resolveProductName(sale)}? ` +
      'El stock será devuelto y la anulación no se puede revertir.',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Anular',
    acceptIcon: 'pi pi-ban',
    acceptClass: 'confirm-danger',
    accept: () => cancelSale(sale),
  })
}

const cancelSale = async (sale) => {
  if (annullingId.value) return

  annullingId.value = sale.venta_id
  try {
    await annulSale(sale.venta_id)
    const [salesData] = await Promise.all([
      getSales(),
      refreshProducts(),
    ])
    sales.value = salesData
    toast.add({
      severity: 'success',
      summary: 'Venta anulada',
      detail: 'La venta fue anulada y el stock fue devuelto.',
      life: 3200,
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'No se pudo anular',
      detail: getErrorMessage(error),
      life: 4500,
    })
  } finally {
    annullingId.value = ''
  }
}

onMounted(loadInitialData)
</script>

<style scoped>
.view-stack {
  display: grid;
  gap: 18px;
}

.summary-card span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.summary-card i {
  color: var(--aws-orange);
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

.stock-help {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 0 12px;
  border: 1px solid #d9e2ef;
  border-radius: 10px;
  color: var(--aws-blue);
  background: #f8fafc;
  font-size: 0.9rem;
}

.stock-help i {
  color: var(--aws-orange);
}

.history-note {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 18px 18px;
  padding: 10px 12px;
  border: 1px solid #d9e2ef;
  border-radius: 10px;
  color: var(--text-muted);
  background: #f8fafc;
  font-size: 0.88rem;
}

.history-note i {
  color: var(--aws-orange);
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

  .history-note {
    display: flex;
    align-items: flex-start;
    margin-inline: 14px;
  }
}
</style>
