<template>
  <header class="topbar">
    <button class="menu-button" type="button" aria-label="Abrir menú" @click="$emit('toggle-menu')">
      <i class="pi pi-bars"></i>
    </button>

    <div>
      <h1>{{ title }}</h1>
      <p>Plataforma de gestión</p>
    </div>

    <div class="connection" :class="connectionClass">
      <span></span>
      {{ connectionLabel }}
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
})

defineEmits(['toggle-menu'])

const connectionStatus = ref('online')

const connectionLabels = {
  online: 'AWS conectado',
  offline: 'API Offline',
  checking: 'Verificando',
}

const connectionLabel = computed(() => connectionLabels[connectionStatus.value])
const connectionClass = computed(() => `is-${connectionStatus.value}`)
</script>

<style scoped>
.topbar {
  min-height: var(--topbar-height);
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: space-between;
  padding: 16px 28px;
  border-bottom: 1px solid var(--border);
  background: rgba(248, 250, 252, 0.88);
  backdrop-filter: blur(16px);
}

.topbar h1 {
  margin: 0;
  color: var(--text-main);
  font-size: 1.25rem;
  font-weight: 850;
}

.topbar p {
  margin: 2px 0 0;
  color: var(--text-muted);
  font-size: 0.88rem;
}

.menu-button {
  width: 42px;
  height: 42px;
  display: none;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--aws-blue);
  background: var(--surface);
}

.connection {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
  border: 1px solid rgba(22, 163, 74, 0.18);
  border-radius: 999px;
  color: #166534;
  background: #ecfdf3;
  font-weight: 800;
  font-size: 0.86rem;
  line-height: 1;
  white-space: nowrap;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.connection span {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--success);
}

.connection.is-online {
  border-color: rgba(47, 143, 91, 0.2);
  color: #17603b;
  background: #edf8f2;
}

.connection.is-offline {
  border-color: rgba(189, 52, 52, 0.2);
  color: #9f2424;
  background: #fff1f1;
}

.connection.is-offline span {
  background: var(--danger);
}

.connection.is-checking {
  border-color: rgba(196, 122, 9, 0.22);
  color: #9a5a05;
  background: #fff7e8;
}

.connection.is-checking span {
  background: var(--warning);
}

@media (max-width: 860px) {
  .topbar {
    padding: 14px 18px;
  }

  .menu-button {
    display: inline-flex;
  }
}

@media (max-width: 520px) {
  .connection {
    display: none;
  }
}
</style>
