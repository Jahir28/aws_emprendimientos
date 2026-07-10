<template>
  <span class="status-badge" :class="variantClass">
    <span class="dot"></span>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    default: 'info',
  },
})

const variantClass = computed(() => `is-${props.variant}`)
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 850;
  white-space: nowrap;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.is-success {
  color: #15803d;
  background: #ecfdf3;
}

.is-warning {
  color: #b45309;
  background: #fffbeb;
}

.is-danger {
  color: #b91c1c;
  background: #fef2f2;
}

.is-info {
  color: #1d4ed8;
  background: #eff6ff;
}
</style>
