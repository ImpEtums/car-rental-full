<template>
  <div class="chat-page">
    <div class="chat-container">
      <login-form v-if="!isChatLoggedIn" @login="handleChatLogin" />
      <chat-interface v-else :currentUser="currentChatUser" @logout="handleChatLogout" />
    </div>
  </div>
</template>

<script>
import LoginForm from './LoginForm.vue';
import ChatInterface from './ChatInterface.vue';

export default {
  name: 'ChatPage',
  components: {
    LoginForm,
    ChatInterface
  },
  data() {
    return {
      isChatLoggedIn: false,
      currentChatUser: null
    }
  },
  created() {
    // 检查本地存储中是否有聊天用户信息
    const savedChatUser = localStorage.getItem('chatUser')
    if (savedChatUser) {
      this.currentChatUser = JSON.parse(savedChatUser)
      this.isChatLoggedIn = true
    }
  },
  methods: {
    handleChatLogin(user) {
      this.currentChatUser = user
      this.isChatLoggedIn = true
      // 保存聊天用户信息到本地存储
      localStorage.setItem('chatUser', JSON.stringify(user))
    },
    handleChatLogout() {
      this.isChatLoggedIn = false
      this.currentChatUser = null
      localStorage.removeItem('chatUser')
    }
  }
};
</script>

<style scoped>
.chat-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 80px);
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
}

.chat-container {
  width: 90%;
  max-width: 1400px;
  height: 85vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.2);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.chat-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .chat-page {
    padding: 20px 10px;
  }
  
  .chat-container {
    width: 95%;
    height: 90vh;
    border-radius: 15px;
  }
}
</style>