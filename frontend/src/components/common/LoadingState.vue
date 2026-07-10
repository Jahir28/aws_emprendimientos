<template>
  <div class="loading-state">
    <span class="spinner"></span>
    <span>{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: 'Cargando información...',
  },
})
</script>

<style scoped>
.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-weight: 750;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 3px solid #d8e1ee;
  border-top-color: var(--aws-orange);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
