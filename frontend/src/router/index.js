import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '../views/DashboardView.vue'
import ProductsView from '../views/ProductsView.vue'
import ClientsView from '../views/ClientsView.vue'
import SalesView from '../views/SalesView.vue'
import ReportsView from '../views/ReportsView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { title: 'Dashboard' },
  },
  {
    path: '/productos',
    name: 'products',
    component: ProductsView,
    meta: { title: 'Productos' },
  },
  {
    path: '/clientes',
    name: 'clients',
    component: ClientsView,
    meta: { title: 'Clientes' },
  },
  {
    path: '/ventas',
    name: 'sales',
    component: SalesView,
    meta: { title: 'Ventas' },
  },
  {
    path: '/reportes',
    name: 'reports',
    component: ReportsView,
    meta: { title: 'Reportes' },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { title: 'Página no encontrada' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
