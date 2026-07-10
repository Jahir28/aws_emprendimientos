<template>
  <div class="app-shell">
    <div v-if="sidebarOpen" class="mobile-backdrop" @click="sidebarOpen = false"></div>
    <AppSidebar :open="sidebarOpen" @navigate="sidebarOpen = false" />

    <div class="main-shell">
      <AppTopbar :title="currentTitle" @toggle-menu="sidebarOpen = !sidebarOpen" />
      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'

const route = useRoute()
const sidebarOpen = ref(false)
const currentTitle = computed(() => route.meta.title || 'ControlPyme')
</script>

<style scoped>
.mobile-backdrop {
  position: fixed;
  inset: 0;
  z-index: 25;
  background: rgba(15, 23, 42, 0.42);
}
</style>
