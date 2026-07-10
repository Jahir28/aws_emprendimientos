<template>
  <aside class="sidebar" :class="{ 'is-open': open }" aria-label="Navegación principal">
    <div class="brand">
      <div class="brand-mark">
        <i class="pi pi-cloud"></i>
      </div>
      <div>
        <strong>ControlPyme</strong>
        <span>Panel administrativo</span>
      </div>
    </div>

    <nav class="nav-list">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-link"
        active-class="is-active"
        @click="$emit('navigate')"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <span class="status-dot"></span>
      <div>
        <strong>Ambiente demo</strong>
        <span>Datos simulados</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['navigate'])

const items = [
  { label: 'Dashboard', to: '/', icon: 'pi pi-chart-line' },
  { label: 'Productos', to: '/productos', icon: 'pi pi-box' },
  { label: 'Clientes', to: '/clientes', icon: 'pi pi-users' },
  { label: 'Ventas', to: '/ventas', icon: 'pi pi-shopping-cart' },
  { label: 'Reportes', to: '/reportes', icon: 'pi pi-chart-bar' },
]
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 30;
  display: flex;
  flex-direction: column;
  padding: 22px;
  color: #fff;
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(12, 19, 34, 0.99)),
    #0f172a;
  box-shadow: 18px 0 48px rgba(15, 23, 42, 0.26);
}

.brand {
  display: flex;
  gap: 13px;
  align-items: center;
  min-height: 58px;
}

.brand-mark {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  color: #111827;
  background: var(--aws-orange);
  box-shadow: 0 12px 28px rgba(255, 153, 0, 0.22);
}

.brand strong,
.brand span,
.sidebar-footer strong,
.sidebar-footer span {
  display: block;
}

.brand strong {
  line-height: 1.15;
  font-size: 0.98rem;
}

.brand span,
.sidebar-footer span {
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.8rem;
}

.nav-list {
  display: grid;
  gap: 8px;
  margin-top: 34px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.78);
  font-weight: 750;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.nav-link:hover {
  color: #fff;
  background: rgba(51, 65, 85, 0.44);
}

.nav-link.is-active {
  color: #fff;
  background: rgba(51, 65, 85, 0.68);
  box-shadow: inset 4px 0 0 var(--aws-orange);
}

.nav-link:hover {
  transform: translateX(2px);
}

.nav-link i {
  color: var(--aws-orange);
}

.sidebar-footer {
  display: flex;
  gap: 11px;
  align-items: center;
  margin-top: auto;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.07);
  transition:
    background 0.2s ease,
    border-color 0.2s ease;
}

.sidebar-footer:hover {
  border-color: rgba(255, 153, 0, 0.2);
  background: rgba(255, 255, 255, 0.09);
}

.status-dot {
  width: 10px;
  height: 10px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.14);
}

@media (max-width: 860px) {
  .sidebar {
    transform: translateX(-105%);
    transition: transform 0.25s ease;
  }

  .sidebar.is-open {
    transform: translateX(0);
  }
}
</style>
