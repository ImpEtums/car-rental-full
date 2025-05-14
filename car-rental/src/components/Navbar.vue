<template>
  <nav class="navbar">
    <img src="@/assets/images/logo.png" alt="Logo" class="logo" />
    <ul class="nav-links">
      <li>
        <router-link to="/" :class="{ active: isActive('/') }">首页</router-link>
      </li>
      <li>
        <router-link to="/about" :class="{ active: isActive('/about') }">关于我们</router-link>
      </li>
      <li>
        <router-link to="/car-showcase" :class="{ active: isActive('/car-showcase') }">预定汽车</router-link>
      </li>
      <li>
        <router-link to="/store-search" :class="{ active: isActive('/store-search') }">网点查询</router-link>
      </li>
      <li>
        <router-link to="/city-tree" :class="{ active: isActive('/city-tree') }">城市树状图</router-link>
      </li>
      <li>
        <a href="tel:666666666" class="phone-button">🕿 666-666-666</a>
      </li>
    </ul>

    <div class="auth-buttons">
      <router-link to="/login" class="auth-button">
        {{ isLoggedIn ? '个人中心' : '登录/注册' }}
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const isLoggedIn = ref(false);

const isActive = (path) => {
  return route.path === path;
};

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('user');
});

watch(
  () => route.path,
  () => {
    isLoggedIn.value = !!localStorage.getItem('user');
  }
);
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: black;
  padding: 4px 48px;
  height: 56px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.logo {
  height: 32px;
  margin-right: 15px;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 32px;
  margin: 0;
  padding: 0;
}

.nav-links li {
  margin: 0;
}

.nav-links a,
.nav-links .router-link-active {
  text-decoration: none;
  color: white;
  font-size: 1rem;
  font-weight: bold;
  transition: color 0.3s;
}

.nav-links a:hover,
.nav-links .router-link-active:hover {
  color: #ffbb00;
}

.nav-links .active {
  color: #ffbb00;
}

.profile-button {
  text-decoration: none;
  color: black;
  background-color: #ffbb00;
  padding: 8px 12px;
  border-radius: 5px;
  font-weight: bold;
  transition: background-color 0.3s, color 0.3s;
}

.profile-button:hover {
  color: white;
  background-color: #e69603;
}

.auth-button {
  text-decoration: none;
  color: black;
  background-color: #ffbb00;
  padding: 8px 12px;
  border-radius: 5px;
  font-weight: bold;
  transition: background-color 0.3s, color 0.3s;
}

.auth-button:hover {
  color: white;
  background-color: #e69603;
}
</style>
