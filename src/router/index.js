// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import AboutView from '../views/AboutView.vue';

const routes = [
  {
    path: '/',
    name: 'About',
    component: AboutView,
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;