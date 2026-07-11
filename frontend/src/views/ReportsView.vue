<template>
  <div class="view-stack">
    <PageHeader
      eyebrow="Análisis"
      title="Reportes"
      description="Indicadores para presentar desempeño de ventas, clientes e inventario."
    />

    <section class="grid metrics-grid">
      <MetricCard
        v-for="metric in metrics"
        :key="metric.label"
        v-bind="metric"
      />
    </section>

    <section v-if="errorMessage" class="card panel error-panel">
      <i class="pi pi-exclamation-circle"></i>
      <div>
        <strong>No se pudieron cargar los reportes</strong>
        <p>{{ errorMessage }}</p>
      </div>
      <button class="btn btn-secondary" type="button" :disabled="isLoading" @click="loadReports">
        Reintentar
      </button>
    </section>

    <section v-if="isLoading" class="card panel state-panel">
      <LoadingState label="Cargando reportes desde AWS..." />
    </section>

    <section class="grid reports-grid">
      <article class="card panel">
        <h3 class="panel-title">Productos más vendidos</h3>
        <p class="panel-subtitle">Ranking real por unidades completadas</p>
        <div v-if="topProducts.length > 0" class="chart-box">
          <Bar :data="productsChart" :options="chartOptions" />
        </div>
        <EmptyState
          v-else
          icon="pi pi-chart-bar"
          title="Sin productos vendidos"
          message="El reporte aparecerá cuando existan ventas completadas."
        />
      </article>

      <article class="card panel">
        <h3 class="panel-title">Clientes frecuentes</h3>
        <p class="panel-subtitle">Ranking real por total comprado</p>
        <div v-if="frequentClients.length > 0" class="chart-box">
          <Doughnut :data="clientsChart" :options="doughnutOptions" />
        </div>
        <EmptyState
          v-else
          icon="pi pi-users"
          title="Sin clientes frecuentes"
          message="El reporte aparecerá cuando existan ventas completadas."
        />
      </article>
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
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut } from 'vue-chartjs'

import MetricCard from '../components/dashboard/MetricCard.vue'
import EmptyState from '../components/common/EmptyState.vue'
import LoadingState from '../components/common/LoadingState.vue'
import PageHeader from '../components/common/PageHeader.vue'
import { getReportsOverview } from '../services/reportsService'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const summary = ref({})
const topProducts = ref([])
const frequentClients = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const formatCurrency = (value) =>
  new Intl.NumberFormat('es-PA', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0))

const formatNumber = (value) =>
  new Intl.NumberFormat('es-PA').format(Number(value || 0))

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
    icon: 'pi pi-wallet',
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
    label: 'Clientes registrados',
    value: formatNumber(summary.value.total_clientes),
    detail: `${formatNumber(frequentClients.value.length)} frecuente(s)`,
    icon: 'pi pi-users',
    color: '#4f9a70',
  },
  {
    label: 'Productos registrados',
    value: formatNumber(summary.value.total_productos),
    detail: 'Inventario actual',
    icon: 'pi pi-box',
    color: '#223450',
  },
  {
    label: 'Bajo stock',
    value: formatNumber(summary.value.productos_bajo_stock),
    detail: 'Productos con stock <= 5',
    icon: 'pi pi-exclamation-circle',
    color: '#bd4a4a',
  },
  {
    label: 'Ticket promedio',
    value: formatCurrency(ticketAverage.value),
    detail: 'Promedio por venta completada',
    tooltip: 'Ingreso promedio obtenido por cada venta completada.',
    icon: 'pi pi-chart-line',
    color: '#7562a8',
  },
])

const productsChart = computed(() => ({
  labels: topProducts.value.map((product) => product.producto_nombre),
  datasets: [
    {
      label: 'Unidades',
      data: topProducts.value.map((product) => product.cantidad_vendida),
      backgroundColor: '#ff9900',
      borderRadius: 8,
    },
  ],
}))

const clientsChart = computed(() => ({
  labels: frequentClients.value.map((client) => client.cliente_nombre),
  datasets: [
    {
      data: frequentClients.value.map((client) => client.total_gastado),
      backgroundColor: ['#ff9900', '#223450', '#4f7fb8', '#4f9a70'],
      borderWidth: 0,
    },
  ],
}))

const chartOptions = {
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

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { usePointStyle: true },
    },
  },
}

const loadReports = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const reportsData = await getReportsOverview()
    summary.value = reportsData.summary
    topProducts.value = reportsData.topProducts
    frequentClients.value = reportsData.frequentClients
  } catch (error) {
    errorMessage.value = getErrorMessage(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadReports)
</script>

<style scoped>
.view-stack {
  display: grid;
  gap: 18px;
}

.inventory-summary {
  display: grid;
  gap: 18px;
}

.state-panel {
  min-height: 180px;
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

@media (max-width: 760px) {
  .inventory-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .error-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 460px) {
  .inventory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
