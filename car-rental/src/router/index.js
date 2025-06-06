import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', component: () => import('../components/HomePage.vue') },
  { path: '/about', component: () => import('../components/About.vue') },
  { path: '/contact', component: () => import('../components/Contact.vue') },
  { path: '/login', name: 'Login', component: () => import('../components/Login.vue') },
  { path: '/register', component: () => import('../components/Register.vue') },
  { 
    path: '/profile', 
    name: 'Profile', 
    component: () => import('../components/Profile.vue'),
    meta: { requiresAuth: true }
  },
  // 添加订单列表页面路由
  { 
    path: '/orders', 
    name: 'OrderList', 
    component: () => import('../components/OrderListPage.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/car-showcase', name: 'showcase', component: () => import('../components/CarShowcasePage.vue') },
  { path: '/showcase', name: 'showcase', component: () => import('../components/CarShowcasePage.vue') },
  { path: '/checkout/:id', name: 'checkout', component: () => import('../components/OrderCheckout.vue') },
  { path: '/payment', name:'payment', component: () => import('../components/PaymentPage.vue') },
  { path: '/city-tree', name: 'CityTree', component: () => import('@/components/CityTreeView.vue') },
  { path: '/store-search', name: 'StoreSearch', component: () => import('@/components/StoreSearch.vue') },
  { path: '/car-management', name: 'CarManagement', component: () => import('@/components/CarManagement.vue') },
  // 添加聊天路由
  { path: '/chat', name: 'Chat', component: () => import('../components/ChatInterface.vue') },
  // 新增聊天页面路由
  { path: '/chat-page', name: 'ChatPage', component: () => import('../components/ChatPage.vue') },
  { path: '/car-show-3d', name: 'CarShow3D', component: () => import('../views/CarShow3D.vue') },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  
  if (to.meta.requiresAuth && !token) {
    // 需要认证但没有token，跳转到登录页
    next('/login');
  } else {
    next();
  }
});

export default router;