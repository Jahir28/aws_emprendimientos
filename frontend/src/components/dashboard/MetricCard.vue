<template>
  <article class="metric-card card">
    <div class="metric-icon" :style="{ '--metric-color': color }">
      <i :class="icon"></i>
    </div>
    <span class="metric-label">
      {{ label }}
      <i
        v-if="tooltip"
        v-tooltip.top="tooltip"
        class="pi pi-info-circle metric-info"
        aria-label="Información"
      ></i>
    </span>
    <strong>{{ value }}</strong>
    <small>{{ detail }}</small>
    <small v-if="secondaryDetail" class="metric-secondary">
      {{ secondaryDetail }}
      <i
        v-if="secondaryTooltip"
        v-tooltip.top="secondaryTooltip"
        class="pi pi-info-circle metric-info"
        aria-label="Información"
      ></i>
    </small>
  </article>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  detail: {
    type: String,
    default: '',
  },
  secondaryDetail: {
    type: String,
    default: '',
  },
  tooltip: {
    type: String,
    default: '',
  },
  secondaryTooltip: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: 'pi pi-chart-line',
  },
  color: {
    type: String,
    default: '#ff9900',
  },
})
</script>

<style scoped>
.metric-card {
  height: 100%;
  min-height: 158px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  min-width: 0;
}

.metric-card::after {
  content: "";
  width: 58px;
  height: 58px;
  position: absolute;
  inset: 14px 14px auto auto;
  border-radius: 999px;
  background: color-mix(in srgb, var(--metric-color) 9%, transparent);
}

.metric-icon {
  position: relative;
  z-index: 1;
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: var(--metric-color);
  background: color-mix(in srgb, var(--metric-color) 14%, white);
}

.metric-label {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 18px;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 750;
}

strong {
  position: relative;
  z-index: 1;
  display: block;
  max-width: 100%;
  margin-top: 5px;
  color: var(--text-main);
  font-size: clamp(1.35rem, 1.7vw, 1.85rem);
  line-height: 1.1;
  white-space: nowrap;
  overflow-wrap: normal;
  word-break: normal;
  font-variant-numeric: tabular-nums;
}

small {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 7px;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.metric-secondary {
  color: var(--text-main);
  font-weight: 750;
}

.metric-info {
  color: var(--text-muted);
  cursor: help;
  font-size: 0.78rem;
}
</style>
