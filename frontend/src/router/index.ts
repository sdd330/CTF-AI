import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import GameContainer from '../components/GameContainer'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: GameContainer
  },
  {
    path: '/demo',
    name: 'MapDemo',
    component: () => import('../components/MapDemo.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

