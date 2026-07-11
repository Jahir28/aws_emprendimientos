<template>
  <div class="view-stack">
    <section class="welcome card">
      <div>
        <span>Resumen general</span>
        <h2>Te damos la bienvenida a ControlPyme</h2>
        <p>Administra productos, clientes, ventas y reportes desde una experiencia centralizada.</p>
      </div>
      <div class="welcome-badge">
        <i class="pi pi-bolt"></i>
        AWS activo
      </div>
    </section>

    <section class="grid metrics-grid">
      <MetricCard
        v-for="metric in metrics"
        :key="metric.label"
        v-bind="metric"
      />
    </section>

    <section class="card panel inventory-summary">
      <div>
        <h3 class="panel-title">Resumen de inventario</h3>
        <p class="panel-subtitle">Estado general calculado desde DynamoDB</p>
      </div>
      <div class="inventory-grid">
        <div><span>Productos registrados</span><strong>{{ formatNumber(summary.total_productos) }}</strong></div>
        <div><span>Stock bajo</span><strong>{{ formatNumber(summary.productos_bajo_stock) }}</strong></div>
        <div><span>Unidades vendidas</span><strong>{{ formatNumber(summary.unidades_vendidas) }}</strong></div>
        <div><span>Valor estimado</span><strong>{{ formatCurrency(summary.valor_inventario) }}</strong></div>
      </div>
    </section>

    <section v-if="errorMessage" class="card panel error-panel">
      <i class="pi pi-exclamation-circle"></i>
      <div>
        <strong>No se pudo cargar el dashboard</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="loadDashboard">
        Reintentar
      </button>
    </section>

    <section v-if="isLoading" class="card panel state-panel">
      <LoadingState label="Cargando indicadores desde AWS..." />
    </section>

    <section class="grid dashboard-grid">
      <div class="card panel">
        <div>
          <h3 class="panel-title">Productos más vendidos</h3>
          <p class="panel-subtitle">Ranking real por unidades vendidas</p>
        </div>
        <div v-if="hasTopProducts" class="chart-box">
          <Bar :data="topProductsData" :options="barOptions" />
        </div>
        <EmptyState
          v-else
          icon="pi pi-chart-bar"
          title="Sin ventas completadas"
          message="Aún no hay productos vendidos para graficar."
        />
      </div>

      <LowStockPanel :products="lowStockProducts" />
    </section>

    <section class="card panel">
      <div>
        <h3 class="panel-title">Clientes frecuentes</h3>
        <p class="panel-subtitle">Ranking real por total comprado</p>
      </div>
      <div v-if="frequentClients.length > 0" class="frequent-list">
        <article v-for="client in frequentClients" :key="client.cliente_id" class="frequent-item">
          <div>
            <strong>{{ client.cliente_nombre }}</strong>
            <span>{{ client.cantidad_ventas }} venta(s)</span>
          </div>
          <strong>{{ formatCurrency(client.total_gastado) }}</strong>
        </article>
      </div>
      <EmptyState
        v-else
        icon="pi pi-users"
        title="Sin clientes frecuentes"
        message="Los clientes aparecerán cuando existan ventas completadas."
      />
    </section>

    <RecentSalesPanel :sales="recentSales" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar } from 'vue-chartjs'

import MetricCard from '../components/dashboard/MetricCard.vue'
import LowStockPanel from '../components/dashboard/LowStockPanel.vue'
import RecentSalesPanel from '../components/dashboard/RecentSalesPanel.vue'
import EmptyState from '../components/common/EmptyState.vue'
import LoadingState from '../components/common/LoadingState.vue'
import { getProducts } from '../services/productsService'
import { getReportsOverview } from '../services/reportsService'
import { getSales } from '../services/salesService'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const summary = ref({})
const topProducts = ref([])
const frequentClients = ref([])
const products = ref([])
const sales = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const formatCurrency = (value) =>
  new Intl.NumberFormat('es-PA', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0))

const formatNumber = (value) =>
  new Intl.NumberFormat('es-PA').format(Number(value || 0))

const formatDate = (value) => {
  if (!value) return 'Sin fecha'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('es-PA', {
    month: 'short',
    day: '2-digit',
  }).format(date)
}

const getErrorMessage = (error) =>
  error?.response?.data?.message || error?.message || 'Ocurrió un error inesperado.'

const ticketAverage = computed(() =>
  summary.value.total_ventas > 0 ? summary.value.ingresos_totales / summary.value.total_ventas : 0,
)

const metrics = computed(() => [
  {
    label: 'Ingresos totales',
    value: formatCurrency(summary.value.ingresos_totales),
    detail: 'Ingresos de ventas completadas',
    tooltip: 'Total generado por ventas completadas.',
    icon: 'pi pi-dollar',
    color: '#ff9900',
  },
  {
    label: 'Ventas completadas',
    value: formatNumber(summary.value.total_ventas),
    detail: 'Ventas activas',
    secondaryDetail: `Ventas anuladas: ${formatNumber(summary.value.ventas_anuladas)}`,
    secondaryTooltip: 'Ventas anuladas que no generan ingresos.',
    icon: 'pi pi-shopping-cart',
    color: '#4f7fb8',
  },
  {
    label: 'Productos registrados',
    value: formatNumber(summary.value.total_productos),
    detail: 'Inventario actual',
    icon: 'pi pi-box',
    color: '#223450',
  },
  {
    label: 'Clientes registrados',
    value: formatNumber(summary.value.total_clientes),
    detail: `${formatNumber(frequentClients.value.length)} frecuente(s)`,
    icon: 'pi pi-users',
    color: '#4f9a70',
  },
  {
    label: 'Ticket promedio',
    value: formatCurrency(ticketAverage.value),
    detail: 'Promedio por venta completada',
    tooltip: 'Ingreso promedio obtenido por cada venta completada.',
    icon: 'pi pi-chart-line',
    color: '#7562a8',
  },
  {
    label: 'Bajo stock',
    value: formatNumber(summary.value.productos_bajo_stock),
    detail: 'Productos con stock <= 5',
    icon: 'pi pi-exclamation-triangle',
    color: '#bd4a4a',
  },
])

const lowStockProducts = computed(() =>
  products.value
    .filter((product) => Number(product.stock || 0) <= 5)
    .slice(0, 6)
    .map((product) => ({
      id: product.producto_id,
      name: product.nombre || 'Producto sin nombre',
      category: product.categoria || 'Sin categoría',
      stock: Number(product.stock || 0),
    })),
)

const recentSales = computed(() =>
  [...sales.value]
    .sort((first, second) => {
      const firstDate = new Date(first.created_at || first.fecha || 0).getTime()
      const secondDate = new Date(second.created_at || second.fecha || 0).getTime()
      return secondDate - firstDate
    })
    .slice(0, 5)
    .map((sale) => ({
      id: sale.venta_id,
      client: sale.cliente_nombre || 'Cliente no disponible',
      product: sale.producto_nombre || 'Producto no disponible',
      date: formatDate(sale.fecha || sale.created_at),
      total: formatCurrency(sale.total),
    })),
)

const hasTopProducts = computed(() => topProducts.value.length > 0)

const topProductsData = computed(() => ({
  labels: topProducts.value.map((product) => product.producto_nombre),
  datasets: [
    {
      label: 'Unidades vendidas',
      data: topProducts.value.map((product) => product.cantidad_vendida),
      backgroundColor: ['#ff9900', '#223450', '#4f7fb8', '#4f9a70', '#7562a8'],
      borderRadius: 8,
    },
  ],
}))

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#edf2f7' } },
  },
}

const loadDashboard = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const [reportsData, productsData, salesData] = await Promise.all([
      getReportsOverview(),
      getProducts(),
      getSales(),
    ])

    summary.value = reportsData.summary
    topProducts.value = reportsData.topProducts
    frequentClients.value = reportsData.frequentClients
    products.value = productsData
    sales.value = salesData
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadDashboard)
</script>

<style scoped>
.view-stack {
  display: grid;
  gap: 20px;
}

.welcome {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 32px;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(25, 42, 68, 0.96)),
    #0f172a;
  color: #fff;
}

.welcome::after {
  content: "";
  width: 180px;
  height: 180px;
  position: absolute;
  right: -54px;
  bottom: -72px;
  border: 1px solid rgba(255, 153, 0, 0.28);
  border-radius: 50%;
  background: rgba(255, 153, 0, 0.06);
}

.welcome > * {
  position: relative;
  z-index: 1;
}

.welcome span {
  color: var(--aws-orange);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.welcome h2 {
  margin: 10px 0 8px;
  color: #fff;
  font-size: clamp(1.6rem, 3vw, 2.5rem);
  line-height: 1.08;
  letter-spacing: 0;
}

.welcome p {
  max-width: 680px;
  margin: 0;
  color: rgba(255, 255, 255, 0.76);
}

.welcome-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  color: #111827;
  background: var(--aws-orange);
  font-weight: 850;
  box-shadow: 0 12px 28px rgba(255, 153, 0, 0.22);
}

.state-panel {
  min-height: 180px;
  display: grid;
  place-items: center;
}

.inventory-summary {
  display: grid;
  gap: 18px;
}

.inventory-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.inventory-grid div {
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fbfdff;
}

.inventory-grid span,
.inventory-grid strong {
  display: block;
}

.inventory-grid span {
  color: var(--text-muted);
  font-size: 0.86rem;
}

.inventory-grid strong {
  margin-top: 6px;
  color: var(--text-main);
  font-size: 1.35rem;
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

.frequent-list {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.frequent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #fbfdff;
}

.frequent-item strong,
.frequent-item span {
  display: block;
}

.frequent-item strong {
  color: var(--text-main);
}

.frequent-item span {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 0.86rem;
}

@media (max-width: 720px) {
  .welcome {
    align-items: flex-start;
    flex-direction: column;
  }

  .error-panel {
    grid-template-columns: 1fr;
  }

  .inventory-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .frequent-item {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 460px) {
  .inventory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
