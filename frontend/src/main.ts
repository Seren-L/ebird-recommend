import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import HotspotDetailView from './views/HotspotDetailView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/',               component: HomeView },
    { path: '/hotspot/:locId', component: HotspotDetailView },
  ],
})

createApp(App).use(router).mount('#app')
