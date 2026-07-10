<template>
  <section class="card panel">
    <div>
      <h3 class="panel-title">Ventas recientes</h3>
      <p class="panel-subtitle">Últimos movimientos registrados</p>
    </div>

    <div class="sales-list">
      <article v-for="sale in sales" :key="sale.id" class="sale-item">
        <div class="sale-avatar">
          <i class="pi pi-shopping-bag"></i>
        </div>
        <div class="sale-info">
          <strong>{{ sale.client }}</strong>
          <span>{{ sale.product }} · {{ sale.date }}</span>
        </div>
        <strong class="sale-total">{{ sale.total }}</strong>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  sales: {
    type: Array,
    required: true,
  },
})
</script>

<style scoped>
.sales-list {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.sale-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.sale-item:last-child {
  border-bottom: 0;
}

.sale-avatar {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: var(--aws-blue);
  background: #eef4fb;
}

.sale-info {
  min-width: 0;
}

.sale-info strong,
.sale-info span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sale-info strong,
.sale-total {
  color: var(--text-main);
}

.sale-info span {
  color: var(--text-muted);
  font-size: 0.86rem;
}
</style>
