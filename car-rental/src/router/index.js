// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', component: () => import('../components/HomePage.vue') }, // 首页
  { path: '/about', component: () => import('../components/About.vue') }, // 关于我们
  { path: '/contact', component: () => import('../components/Contact.vue') }, // 联系我们
  { path: '/login', name: 'Login', component: () => import('../components/Login.vue') }, // 登录页面
  { path: '/register', component: () => import('../components/Register.vue') }, // 注册页面
  { path: '/profile', name: 'Profile', component: () => import('../components/Profile.vue') }, // 个人信息页面，确保这里有 name: 'Profile'
  { path: '/car-showcase', name: 'showcase', component: () => import('../components/CarShowcasePage.vue') }, // 汽车展示页面
  { path: '/checkout/:id', name: 'checkout', component: () => import('../components/OrderCheckout.vue') }, // 订单结算页面
  { path: '/payment', name:'payment', component: () => import('../components/PaymentPage.vue') }, //收款页面
  { path: '/city-tree', name: 'CityTree', component: () => import('@/components/CityTreeView.vue') }, //树状结构展示页面
  { path: '/store-search', name: 'StoreSearch', component: () => import('@/components/StoreSearch.vue') },
  { path: '/car-management', name: 'CarManagement', component: () => import('@/components/CarManagement.vue') }, // 车辆管理页面
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;