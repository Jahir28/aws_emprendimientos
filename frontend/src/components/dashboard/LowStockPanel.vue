<template>
  <section class="card panel">
    <div class="panel-heading">
      <div>
        <h3 class="panel-title">Productos con bajo stock</h3>
        <p class="panel-subtitle">Alertas simuladas para inventario crítico</p>
      </div>
      <i class="pi pi-exclamation-triangle"></i>
    </div>

    <div class="stock-list">
      <article v-for="item in products" :key="item.id" class="stock-item">
        <div>
          <strong>{{ item.name }}</strong>
          <span>{{ item.category }}</span>
        </div>
        <StatusBadge :label="`${item.stock} unidades`" :variant="item.stock === 0 ? 'danger' : 'warning'" />
      </article>
    </div>
  </section>
</template>

<script setup>
import StatusBadge from '../common/StatusBadge.vue'

defineProps({
  products: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.panel-heading > i {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: #b45309;
  background: #fffbeb;
}

.stock-list {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.stock-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fbfdff;
}

.stock-item strong,
.stock-item span {
  display: block;
}

.stock-item strong {
  color: var(--text-main);
}

.stock-item span {
  color: var(--text-muted);
  font-size: 0.86rem;
}
</style>
