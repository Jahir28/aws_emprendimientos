import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'
import './assets/styles/base.css'
import './assets/styles/theme.css'

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  ripple: true,
})

app.mount('#app')
