<template>
  <div class="view-stack">
    <PageHeader
      eyebrow="Operación"
      title="Ventas"
      description="Seguimiento de transacciones y rendimiento comercial del emprendimiento."
    >
      <template #actions>
        <button class="btn btn-primary" type="button">
          <i class="pi pi-plus-circle"></i>
          Registrar venta
        </button>
      </template>
    </PageHeader>

    <section class="mini-summary">
      <article class="summary-card card">
        <span><i class="pi pi-wallet"></i> Total del día</span>
        <strong>$468.50</strong>
      </article>
      <article class="summary-card card">
        <span><i class="pi pi-check-circle"></i> Ventas completadas</span>
        <strong>18</strong>
      </article>
      <article class="summary-card card">
        <span><i class="pi pi-chart-line"></i> Ticket promedio</span>
        <strong>$26.02</strong>
      </article>
    </section>

    <section class="card table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Total</th>
              <th>Fecha</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in sales" :key="sale.id">
              <td><strong>{{ sale.client }}</strong></td>
              <td>{{ sale.product }}</td>
              <td>{{ sale.quantity }}</td>
              <td>{{ sale.total }}</td>
              <td>{{ sale.date }}</td>
              <td>
                <StatusBadge :label="sale.status" :variant="sale.variant" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import PageHeader from '../components/common/PageHeader.vue'
import StatusBadge from '../components/common/StatusBadge.vue'

const sales = [
  { id: 'v-01', client: 'Cliente mostrador', product: 'Café artesanal', quantity: 3, total: '$36.00', date: '2026-07-10', status: 'Completada', variant: 'success' },
  { id: 'v-02', client: 'María González', product: 'Jabón natural', quantity: 2, total: '$9.50', date: '2026-07-09', status: 'Completada', variant: 'success' },
  { id: 'v-03', client: 'Carlos Pérez', product: 'Mermelada de piña', quantity: 4, total: '$26.00', date: '2026-07-09', status: 'Pendiente', variant: 'warning' },
  { id: 'v-04', client: 'Lucía Torres', product: 'Chocolate local', quantity: 5, total: '$41.25', date: '2026-07-08', status: 'Completada', variant: 'success' },
]
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
</style>
