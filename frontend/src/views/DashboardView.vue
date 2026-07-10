<template>
  <div class="view-stack">
    <section class="welcome card">
      <div>
        <span>Resumen general</span>
        <h2>Bienvenido a ControlPyme</h2>
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

    <section class="grid dashboard-grid">
      <div class="card panel">
        <div>
          <h3 class="panel-title">Productos más vendidos</h3>
          <p class="panel-subtitle">Ranking de referencia por unidades vendidas</p>
        </div>
        <div class="chart-box">
          <Bar :data="topProductsData" :options="barOptions" />
        </div>
      </div>

      <LowStockPanel :products="lowStockProducts" />
    </section>

    <RecentSalesPanel :sales="recentSales" />
  </div>
</template>

<script setup>
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

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const metrics = [
  { label: 'Ingresos totales', value: '$8,430', detail: '+12% vs. mes anterior', icon: 'pi pi-dollar', color: '#ff9900' },
  { label: 'Ventas realizadas', value: '126', detail: '32 esta semana', icon: 'pi pi-shopping-cart', color: '#4f7fb8' },
  { label: 'Productos registrados', value: '84', detail: '9 categorías activas', icon: 'pi pi-box', color: '#223450' },
  { label: 'Clientes registrados', value: '58', detail: '11 clientes nuevos', icon: 'pi pi-users', color: '#4f9a70' },
  { label: 'Unidades vendidas', value: '412', detail: 'Promedio 3.2 por venta', icon: 'pi pi-chart-line', color: '#7562a8' },
  { label: 'Bajo stock', value: '6', detail: 'Requieren reposición', icon: 'pi pi-exclamation-triangle', color: '#bd4a4a' },
]

const lowStockProducts = [
  { id: 'p-01', name: 'Café artesanal', category: 'Bebidas', stock: 3 },
  { id: 'p-02', name: 'Mermelada de piña', category: 'Alimentos', stock: 5 },
  { id: 'p-03', name: 'Cuaderno ecológico', category: 'Papelería', stock: 0 },
]

const recentSales = [
  { id: 'v-01', client: 'Cliente mostrador', product: 'Café artesanal', date: 'Hoy', total: '$36.00' },
  { id: 'v-02', client: 'María González', product: 'Jabón natural', date: 'Ayer', total: '$18.50' },
  { id: 'v-03', client: 'Carlos Pérez', product: 'Mermelada de piña', date: '08 Jul', total: '$24.00' },
  { id: 'v-04', client: 'Lucía Torres', product: 'Cuaderno ecológico', date: '07 Jul', total: '$15.00' },
]

const topProductsData = {
  labels: ['Café', 'Mermelada', 'Jabón', 'Cuaderno', 'Chocolate'],
  datasets: [
    {
      label: 'Unidades vendidas',
      data: [92, 76, 64, 48, 36],
      backgroundColor: ['#ff9900', '#223450', '#4f7fb8', '#4f9a70', '#7562a8'],
      borderRadius: 8,
    },
  ],
}

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

@media (max-width: 720px) {
  .welcome {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
