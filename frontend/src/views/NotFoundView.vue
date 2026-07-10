<template>
  <section class="card not-found">
    <EmptyState
      icon="pi pi-compass"
      title="Página no encontrada"
      message="La sección solicitada no existe en el panel administrativo."
    />
    <RouterLink class="btn btn-primary" to="/">
      <i class="pi pi-home"></i>
      Volver al dashboard
    </RouterLink>
  </section>
</template>

<script setup>
import EmptyState from '../components/common/EmptyState.vue'
</script>

<style scoped>
.not-found {
  display: grid;
  place-items: center;
  min-height: 520px;
  padding: 28px;
}
</style>
