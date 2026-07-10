<template>
  <article class="metric-card card">
    <div class="metric-icon" :style="{ '--metric-color': color }">
      <i :class="icon"></i>
    </div>
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <small>{{ detail }}</small>
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
  min-height: 158px;
  padding: 18px;
  position: relative;
  overflow: hidden;
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

span {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 18px;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 750;
}

strong {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 5px;
  color: var(--text-main);
  font-size: 1.55rem;
  line-height: 1.1;
}

small {
  position: relative;
  z-index: 1;
  display: block;
  margin-top: 7px;
  color: var(--text-muted);
  font-size: 0.78rem;
}
</style>
