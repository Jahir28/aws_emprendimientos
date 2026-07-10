<template>
  <div class="view-stack">
    <PageHeader
      eyebrow="Análisis"
      title="Reportes"
      description="Indicadores simulados para presentar desempeño de ventas, clientes e inventario."
    />

    <section class="grid metrics-grid">
      <MetricCard label="Ingresos del mes" value="$12,840" detail="Proyección estable" icon="pi pi-wallet" color="#ff9900" />
      <MetricCard label="Clientes frecuentes" value="14" detail="Compras recurrentes" icon="pi pi-users" color="#4f9a70" />
      <MetricCard label="Rotación inventario" value="68%" detail="Categorías activas" icon="pi pi-refresh" color="#4f7fb8" />
      <MetricCard label="Margen estimado" value="31%" detail="Dato de referencia" icon="pi pi-percentage" color="#7562a8" />
      <MetricCard label="Bajo stock" value="6" detail="Revisar reposición" icon="pi pi-exclamation-circle" color="#bd4a4a" />
      <MetricCard label="Ventas promedio" value="$28" detail="Por transacción" icon="pi pi-chart-line" color="#223450" />
    </section>

    <section class="grid reports-grid">
      <article class="card panel">
        <h3 class="panel-title">Productos más vendidos</h3>
        <p class="panel-subtitle">Comparativo mensual por unidades</p>
        <div class="chart-box">
          <Bar :data="productsChart" :options="chartOptions" />
        </div>
      </article>

      <article class="card panel">
        <h3 class="panel-title">Clientes frecuentes</h3>
        <p class="panel-subtitle">Ranking por volumen de compras</p>
        <div class="chart-box">
          <Doughnut :data="clientsChart" :options="doughnutOptions" />
        </div>
      </article>
    </section>

    <section class="card panel inventory-summary">
      <div>
        <h3 class="panel-title">Resumen de inventario</h3>
        <p class="panel-subtitle">Estado general de productos registrados</p>
      </div>
      <div class="inventory-grid">
        <div><span>Disponibles</span><strong>72</strong></div>
        <div><span>Stock bajo</span><strong>6</strong></div>
        <div><span>Sin existencias</span><strong>2</strong></div>
        <div><span>Valor estimado</span><strong>$5,420</strong></div>
      </div>
    </section>
  </div>
</template>

<script setup>
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
import PageHeader from '../components/common/PageHeader.vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const productsChart = {
  labels: ['Café', 'Mermelada', 'Jabón', 'Chocolate', 'Cuaderno'],
  datasets: [
    {
      label: 'Unidades',
      data: [122, 96, 84, 72, 51],
      backgroundColor: '#ff9900',
      borderRadius: 8,
    },
  ],
}

const clientsChart = {
  labels: ['María', 'Carlos', 'Lucía', 'Andrés'],
  datasets: [
    {
      data: [34, 27, 22, 17],
      backgroundColor: ['#ff9900', '#223450', '#4f7fb8', '#4f9a70'],
      borderWidth: 0,
    },
  ],
}

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
}

@media (max-width: 460px) {
  .inventory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
