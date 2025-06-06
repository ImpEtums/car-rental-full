<template>
  <div id="app">
    <NavBar />
    <router-view />
    
    <!-- 聊天按钮 -->
    <div class="chat-toggle-btn" @click="goToChatPage">
      <i class="el-icon-chat-dot-round"></i>
      在线交流
    </div>
  </div>
</template>

<script>
import NavBar from './components/Navbar.vue'; // 修改为 Navbar.vue
import Hero from './components/Hero.vue';
import CarRentalSelector from './components/CarRentalSelector.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    Hero,
    CarRentalSelector
  },
  methods: {
    goToChatPage() {
      this.$router.push('/chat-page');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 40px;
  padding: 0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

/* 聊天容器样式 */
.chat-container {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 400px;
  height: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

/* 聊天切换按钮 */
.chat-toggle-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1001;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.chat-toggle-btn i {
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    width: calc(100vw - 40px);
    height: 400px;
    bottom: 70px;
    right: 20px;
    left: 20px;
  }
}
</style>
