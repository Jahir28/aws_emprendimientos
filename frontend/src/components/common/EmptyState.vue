<template>
  <div class="empty-state">
    <div class="empty-icon">
      <i :class="icon"></i>
    </div>
    <strong>{{ title }}</strong>
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'pi pi-inbox',
  },
  title: {
    type: String,
    default: 'Sin resultados',
  },
  message: {
    type: String,
    default: 'No hay información para mostrar por ahora.',
  },
})
</script>

<style scoped>
.empty-state {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 220px;
  padding: 28px;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  color: var(--aws-orange);
  background: var(--aws-orange-soft);
}

strong {
  color: var(--text-main);
  font-size: 1rem;
}

p {
  max-width: 360px;
  margin: 0;
}
</style>
