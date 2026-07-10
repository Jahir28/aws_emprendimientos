<template>
  <div class="view-stack">
    <PageHeader
      eyebrow="Inventario"
      title="Productos"
      description="Consulta y organiza el catálogo de productos del emprendimiento."
    >
      <template #actions>
        <button class="btn btn-primary" type="button">
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

    <section class="card table-card">
      <div class="table-wrap">
        <table class="data-table">
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
            <tr v-for="product in filteredProducts" :key="product.id">
              <td>
                <span class="table-cell-icon">
                  <i class="pi pi-box"></i>
                  <strong>{{ product.name }}</strong>
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-tag"></i>
                  {{ product.category }}
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-dollar"></i>
                  {{ formatCurrency(product.price) }}
                </span>
              </td>
              <td>
                <span class="table-cell-icon muted-icon">
                  <i class="pi pi-warehouse"></i>
                  {{ product.stock }}
                </span>
              </td>
              <td>
                <StatusBadge :label="stockLabel(product.stock)" :variant="stockVariant(product.stock)" />
              </td>
              <td>
                <div class="actions">
                  <button class="icon-button" type="button" aria-label="Editar producto">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="icon-button" type="button" aria-label="Eliminar producto">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-if="filteredProducts.length === 0" />
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import EmptyState from '../components/common/EmptyState.vue'
import PageHeader from '../components/common/PageHeader.vue'
import StatusBadge from '../components/common/StatusBadge.vue'

const search = ref('')
const category = ref('')

const products = [
  { id: 'p-01', name: 'Café artesanal', category: 'Bebidas', price: 12, stock: 3 },
  { id: 'p-02', name: 'Mermelada de piña', category: 'Alimentos', price: 6.5, stock: 5 },
  { id: 'p-03', name: 'Jabón natural', category: 'Cuidado personal', price: 4.75, stock: 24 },
  { id: 'p-04', name: 'Cuaderno ecológico', category: 'Papelería', price: 5, stock: 0 },
  { id: 'p-05', name: 'Chocolate local', category: 'Alimentos', price: 8.25, stock: 18 },
]

const categories = computed(() => [...new Set(products.map((product) => product.category))])

const filteredProducts = computed(() => {
  const term = search.value.trim().toLowerCase()
  return products.filter((product) => {
    const matchesTerm = !term || product.name.toLowerCase().includes(term)
    const matchesCategory = !category.value || product.category === category.value
    return matchesTerm && matchesCategory
  })
})

const formatCurrency = (value) =>
  new Intl.NumberFormat('es-PA', {
    style: 'currency',
    currency: 'USD',
  }).format(value)

const stockVariant = (stock) => {
  if (stock === 0) return 'danger'
  if (stock <= 5) return 'warning'
  return 'success'
}

const stockLabel = (stock) => {
  if (stock === 0) return 'Sin existencias'
  if (stock <= 5) return 'Stock bajo'
  return 'Disponible'
}
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
</style>
