<template>
  <div class="view-stack">
    <Toast />
    <ConfirmDialog />

    <PageHeader
      eyebrow="Inventario"
      title="Productos"
      description="Consulta y organiza el catálogo de productos del emprendimiento."
    >
      <template #actions>
        <button class="btn btn-primary" type="button" :disabled="isSaving" @click="openCreateModal">
          <i class="pi pi-plus"></i>
          Nuevo producto
        </button>
      </template>
    </PageHeader>

    <section class="card panel toolbar">
      <div class="filters">
        <input v-model="search" class="input" type="search" placeholder="Buscar producto" />
        <select v-model="category" class="select">
          <option value="">Todas las categorías</option>
          <option v-for="item in categories" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>
      <span class="muted">{{ filteredProducts.length }} productos visibles</span>
    </section>

    <section v-if="errorMessage" class="card panel error-panel">
      <i class="pi pi-exclamation-circle"></i>
      <div>
        <strong>No se pudieron cargar los productos</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="loadProducts">
        Reintentar
      </button>
    </section>

    <section class="card table-card">
      <div v-if="isLoading" class="state-panel">
        <LoadingState label="Cargando productos desde AWS..." />
      </div>

      <div class="table-wrap">
        <table v-if="!isLoading && filteredProducts.length > 0" class="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Precio</th>
              <th>Stock</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.producto_id">
              <td>
                <span class="table-cell-icon">
                  <i class="pi pi-box"></i>
                  <strong>{{ product.nombre }}</strong>
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-tag"></i>
                  {{ product.categoria || 'Sin categoría' }}
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-dollar"></i>
                  {{ formatCurrency(product.precio) }}
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-warehouse"></i>
                  {{ normalizeStock(product.stock) }}
                </span>
              </td>
              <td>
                <StatusBadge
                  :label="stockLabel(product.stock)"
                  :variant="stockVariant(product.stock)"
                />
              </td>
              <td>
                <div class="actions">
                  <button
                    class="icon-button"
                    type="button"
                    aria-label="Editar producto"
                    :disabled="isSaving || deletingId === product.producto_id"
                    @click="openEditModal(product)"
                  >
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button
                    class="icon-button"
                    type="button"
                    aria-label="Eliminar producto"
                    :disabled="isSaving || deletingId === product.producto_id"
                    @click="confirmDelete(product)"
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
        v-if="!isLoading && !errorMessage && filteredProducts.length === 0"
        title="Sin productos"
        message="No hay productos registrados o no coinciden con los filtros aplicados."
      />
    </section>

    <Dialog
      v-model:visible="isModalVisible"
      modal
      :header="modalTitle"
      class="product-dialog"
    >
      <form class="product-form" @submit.prevent="submitProduct">
        <label>
          <span>Nombre</span>
          <input v-model.trim="form.nombre" class="input" type="text" autocomplete="off" />
          <small v-if="formErrors.nombre">{{ formErrors.nombre }}</small>
        </label>

        <label>
          <span>Descripción</span>
          <textarea v-model.trim="form.descripcion" class="textarea" rows="3"></textarea>
        </label>

        <label>
          <span>Categoría</span>
          <input v-model.trim="form.categoria" class="input" type="text" autocomplete="off" />
        </label>

        <div class="form-grid">
          <label>
            <span>Precio</span>
            <input v-model="form.precio" class="input" type="number" min="0" step="0.01" />
            <small v-if="formErrors.precio">{{ formErrors.precio }}</small>
          </label>

          <label>
            <span>Stock</span>
            <input v-model="form.stock" class="input" type="number" min="0" step="1" />
            <small v-if="formErrors.stock">{{ formErrors.stock }}</small>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn btn-secondary" type="button" :disabled="isSaving" @click="closeModal">
            Cancelar
          </button>
          <button class="btn btn-primary" type="submit" :disabled="isSaving">
            <i :class="isSaving ? 'pi pi-spin pi-spinner' : 'pi pi-save'"></i>
            {{ isSaving ? 'Guardando...' : 'Guardar producto' }}
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
import {
  createProduct,
  deleteProduct,
  getProducts,
  updateProduct,
} from '../services/productsService'

const search = ref('')
const category = ref('')
const products = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const deletingId = ref('')
const errorMessage = ref('')
const isModalVisible = ref(false)
const editingProductId = ref('')
const toast = useToast()
const confirm = useConfirm()

const emptyForm = () => ({
  nombre: '',
  descripcion: '',
  categoria: '',
  precio: 0,
  stock: 0,
})

const form = reactive(emptyForm())
const formErrors = reactive({
  nombre: '',
  precio: '',
  stock: '',
})

const categories = computed(() =>
  [...new Set(products.value.map((product) => product.categoria).filter(Boolean))],
)

const modalTitle = computed(() =>
  editingProductId.value ? 'Editar producto' : 'Nuevo producto',
)

const filteredProducts = computed(() => {
  const term = search.value.trim().toLowerCase()
  return products.value.filter((product) => {
    const productName = product.nombre || ''
    const matchesTerm = !term || productName.toLowerCase().includes(term)
    const matchesCategory = !category.value || product.categoria === category.value
    return matchesTerm && matchesCategory
  })
})

const formatCurrency = (value) =>
  new Intl.NumberFormat('es-PA', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0))

const normalizeStock = (stock) => Number(stock || 0)

const stockVariant = (stock) => {
  const currentStock = normalizeStock(stock)
  if (currentStock === 0) return 'danger'
  if (currentStock <= 5) return 'warning'
  return 'success'
}

const stockLabel = (stock) => {
  const currentStock = normalizeStock(stock)
  if (currentStock === 0) return 'Sin existencias'
  if (currentStock <= 5) return 'Stock bajo'
  return 'Disponible'
}

const getErrorMessage = (error) =>
  error?.response?.data?.message || error?.message || 'Ocurrió un error inesperado.'

const loadProducts = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    products.value = await getProducts()
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
    toast.add({
      severity: 'error',
      summary: 'Error al cargar productos',
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
  editingProductId.value = ''
}

const clearFormErrors = () => {
  formErrors.nombre = ''
  formErrors.precio = ''
  formErrors.stock = ''
}

const validateForm = () => {
  clearFormErrors()
  const price = Number(form.precio)
  const stock = Number(form.stock)

  if (!form.nombre) {
    formErrors.nombre = 'El nombre es obligatorio.'
  }

  if (!Number.isFinite(price) || price < 0) {
    formErrors.precio = 'El precio debe ser numérico y mayor o igual que 0.'
  }

  if (!Number.isInteger(stock) || stock < 0) {
    formErrors.stock = 'El stock debe ser un entero mayor o igual que 0.'
  }

  return !formErrors.nombre && !formErrors.precio && !formErrors.stock
}

const buildPayload = () => ({
  nombre: form.nombre,
  descripcion: form.descripcion,
  categoria: form.categoria,
  precio: Number(form.precio),
  stock: Number(form.stock),
})

const openCreateModal = () => {
  resetForm()
  isModalVisible.value = true
}

const openEditModal = (product) => {
  clearFormErrors()
  editingProductId.value = product.producto_id
  form.nombre = product.nombre || ''
  form.descripcion = product.descripcion || ''
  form.categoria = product.categoria || ''
  form.precio = Number(product.precio || 0)
  form.stock = normalizeStock(product.stock)
  isModalVisible.value = true
}

const closeModal = () => {
  if (isSaving.value) return
  isModalVisible.value = false
  resetForm()
}

const submitProduct = async () => {
  if (isSaving.value || !validateForm()) return

  isSaving.value = true
  try {
    if (editingProductId.value) {
      await updateProduct(editingProductId.value, buildPayload())
      toast.add({
        severity: 'success',
        summary: 'Producto actualizado',
        detail: 'Los cambios se guardaron correctamente.',
        life: 3200,
      })
    } else {
      await createProduct(buildPayload())
      toast.add({
        severity: 'success',
        summary: 'Producto creado',
        detail: 'El producto se registró correctamente.',
        life: 3200,
      })
    }

    isModalVisible.value = false
    resetForm()
    await loadProducts()
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

const confirmDelete = (product) => {
  confirm.require({
    message: `¿Deseas eliminar "${product.nombre}"? Esta acción no se puede deshacer.`,
    header: 'Eliminar producto',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Eliminar',
    acceptIcon: 'pi pi-trash',
    acceptClass: 'confirm-danger',
    accept: () => removeProduct(product),
  })
}

const removeProduct = async (product) => {
  if (deletingId.value) return

  deletingId.value = product.producto_id
  try {
    await deleteProduct(product.producto_id)
    products.value = products.value.filter((item) => item.producto_id !== product.producto_id)
    toast.add({
      severity: 'success',
      summary: 'Producto eliminado',
      detail: 'El producto se eliminó correctamente.',
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

onMounted(loadProducts)
</script>

<style scoped>
.view-stack {
  display: grid;
  gap: 18px;
}

.table-cell-icon {
  display: inline-flex;
  align-items: center;
  gap: 9px;
}

.table-cell-icon i {
  color: var(--aws-orange);
  font-size: 0.9rem;
}

.muted-icon i {
  color: #7b8aa1;
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

.product-form {
  display: grid;
  gap: 16px;
}

.product-form label,
.product-form label > span {
  display: grid;
  gap: 7px;
}

.product-form label > span {
  color: var(--text-main);
  font-size: 0.86rem;
  font-weight: 850;
}

.product-form .input {
  width: 100%;
  min-width: 0;
}

.textarea {
  width: 100%;
  resize: vertical;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--text-main);
  padding: 12px 14px;
  outline: none;
  font: inherit;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.textarea:focus {
  border-color: rgba(255, 153, 0, 0.75);
  box-shadow: 0 0 0 4px rgba(255, 153, 0, 0.14);
}

.product-form small {
  color: var(--danger);
  font-weight: 750;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 8px;
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

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }
}
</style>
