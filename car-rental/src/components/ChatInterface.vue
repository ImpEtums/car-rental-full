<template>
  <div class="chat-interface">
    <div class="chat-header">
      <div class="header-left">
        <div class="chat-title">
          <i class="el-icon-chat-dot-round"></i>
          <h2>在线聊天室</h2>
        </div>
        <div class="status-indicator">
          <span class="status-dot"></span>
          <span class="status-text">已连接</span>
        </div>
      </div>
      <div class="user-info">
        <div class="user-avatar">
          <i class="el-icon-user"></i>
        </div>
        <div class="user-details">
          <span class="username">{{ currentUser.nickname }}</span>
          <span class="user-id">ID: {{ currentUser.id }}</span>
        </div>
        <el-button type="danger" size="small" @click="logout" class="logout-btn">
          <i class="el-icon-switch-button"></i>
          退出登录
        </el-button>
      </div>
    </div>
    
    <div class="chat-content">
      <div class="message-area" ref="messageArea">
        <message-item 
          v-for="(msg, index) in messages" 
          :key="index" 
          :message="msg" 
          :currentUser="currentUser"
        />
        <div v-if="messages.length === 0" class="empty-messages">
          <i class="el-icon-chat-line-round"></i>
          <p>暂无消息，开始聊天吧！</p>
        </div>
      </div>
      
      <div class="input-area">
        <el-tabs v-model="activeTab" type="card" class="chat-tabs">
          <el-tab-pane label="📢 公共消息" name="public">
            <div class="message-input-container">
              <el-input
                v-model="publicMessage"
                placeholder="输入广播消息..."
                @keyup.enter="sendPublicMessage"
                class="message-input"
                size="large"
              >
                <template #prepend>
                  <i class="el-icon-microphone"></i>
                </template>
                <template #append>
                  <el-button @click="sendPublicMessage" type="primary" :disabled="!publicMessage.trim()">
                    <i class="el-icon-position"></i>
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="💬 私人消息" name="private">
            <div class="private-message-container">
              <div class="receiver-input">
                <el-input
                  v-model="receiverId"
                  placeholder="输入对方ID"
                  class="receiver-id-input"
                  size="large"
                >
                  <template #prepend>
                    <i class="el-icon-user"></i>
                  </template>
                </el-input>
              </div>
              <el-input
                v-model="privateMessage"
                placeholder="输入私信内容..."
                @keyup.enter="sendPrivateMessage"
                class="message-input"
                size="large"
              >
                <template #prepend>
                  <i class="el-icon-lock"></i>
                </template>
                <template #append>
                  <el-button @click="sendPrivateMessage" type="success" :disabled="!privateMessage.trim() || !receiverId.trim()">
                    <i class="el-icon-message"></i>
                    发送私信
                  </el-button>
                </template>
              </el-input>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <div class="online-users">
      <div class="users-header">
        <h3>
          <i class="el-icon-user-solid"></i>
          在线用户
        </h3>
        <el-badge :value="onlineUsers.length" class="user-count-badge" type="success" />
      </div>
      <div class="users-list">
        <div
          v-for="user in onlineUsers"
          :key="user.id"
          class="user-item"
          :class="{ 'current-user': user.id === currentUser.id }"
          @click="selectReceiver(user)"
        >
          <div class="user-avatar-small">
            <i class="el-icon-user"></i>
          </div>
          <div class="user-info-small">
            <span class="user-nickname">{{ user.nickname }}</span>
            <span class="user-id-small">{{ user.id }}</span>
          </div>
          <div class="user-status">
            <span class="online-dot"></span>
          </div>
        </div>
        <div v-if="onlineUsers.length === 0" class="no-users">
          <i class="el-icon-warning"></i>
          <p>暂无其他用户在线</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MessageItem from './MessageItem.vue'
import ChatService from '../services/ChatService.js'

export default {
  name: 'ChatInterface',
  components: {
    MessageItem
  },
  props: {
    currentUser: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      messages: [],
      publicMessage: '',
      privateMessage: '',
      receiverId: '',
      onlineUsers: [],
      activeTab: 'public',
      unsubscribe: null
    }
  },
  mounted() {
    // 加入聊天
    this.onlineUsers = ChatService.joinChat(this.currentUser.id, this.currentUser.nickname);
    
    // 从本地存储加载历史消息
    this.messages = ChatService.getChatHistory();
    
    // 订阅消息
    this.unsubscribe = ChatService.addListener(this.handleMessage);
    
    this.$nextTick(() => {
      this.scrollToBottom();
    });
    
    // 添加系统消息
    this.addMessage({
      type: 'system',
      content: '您已加入聊天室',
      timestamp: new Date().toISOString()
    });
  },
  beforeUnmount() {
    // 取消订阅
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    
    // 离开聊天
    ChatService.leaveChat();
  },
  methods: {
    handleMessage(message) {
      // 处理接收到的消息
      switch (message.type) {
        case 'userList':
          this.onlineUsers = message.users;
          break;
        case 'publicMessage':
          this.addMessage(message);
          break;
        case 'privateMessage':
          // 只显示发给自己或自己发出的私信
          if (message.receiverId === this.currentUser.id || message.senderId === this.currentUser.id) {
            this.addMessage(message);
          }
          break;
        case 'userJoined':
          if (message.userId !== this.currentUser.id) {
            this.addMessage({
              type: 'system',
              content: `${message.nickname} (${message.userId}) 加入了聊天室`,
              timestamp: message.timestamp
            });
            // 刷新用户列表
            this.onlineUsers = ChatService.getOnlineUsers();
          }
          break;
        case 'userLeft':
          if (message.userId !== this.currentUser.id) {
            this.addMessage({
              type: 'system',
              content: `${message.nickname} (${message.userId}) 离开了聊天室`,
              timestamp: message.timestamp
            });
            // 刷新用户列表
            this.onlineUsers = ChatService.getOnlineUsers();
          }
          break;
      }
    },
    
    sendPublicMessage() {
      if (!this.publicMessage.trim()) return;
      
      const message = ChatService.sendPublicMessage(this.publicMessage);
      this.addMessage(message);
      this.publicMessage = '';
    },
    
    sendPrivateMessage() {
      if (!this.privateMessage.trim() || !this.receiverId.trim()) return;
      
      const message = ChatService.sendPrivateMessage(this.receiverId, this.privateMessage);
      this.addMessage(message);
      this.privateMessage = '';
    },
    
    addMessage(message) {
      // 避免重复添加相同的消息
      const isDuplicate = this.messages.some(msg => 
        msg.timestamp === message.timestamp && 
        msg.type === message.type && 
        msg.content === message.content &&
        msg.senderId === message.senderId
      );
      
      if (!isDuplicate) {
        this.messages.push(message);
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    scrollToBottom() {
      const messageArea = this.$refs.messageArea;
      if (messageArea) {
        messageArea.scrollTop = messageArea.scrollHeight;
      }
    },
    
    selectReceiver(user) {
      if (user.id !== this.currentUser.id) {
        this.receiverId = user.id;
        this.activeTab = 'private';
      }
    },
    
    logout() {
      ChatService.leaveChat();
      this.$emit('logout');
    }
  }
}
</script>

<style scoped>
.chat-interface {
  display: grid;
  grid-template-rows: auto 1fr;
  grid-template-columns: 1fr 300px;
  grid-template-areas:
    "header header"
    "content users";
  gap: 0;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.chat-header {
  grid-area: header;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.chat-title i {
  font-size: 28px;
  color: #fff;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 45px;
  height: 45px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.user-avatar i {
  font-size: 20px;
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-weight: 600;
  font-size: 16px;
}

.user-id {
  font-size: 12px;
  opacity: 0.8;
}

.logout-btn {
  background: rgba(239, 68, 68, 0.9);
  border: none;
  color: white;
  border-radius: 20px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 1);
  transform: translateY(-2px);
}

.chat-content {
  grid-area: content;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  margin: 20px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(to bottom, #fafafa, #f0f0f0);
}

.empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
}

.empty-messages i {
  font-size: 48px;
  margin-bottom: 10px;
  opacity: 0.5;
}

.input-area {
  background: white;
  border-top: 1px solid #eee;
  padding: 20px;
}

.chat-tabs {
  border-radius: 10px;
  overflow: hidden;
}

.message-input-container,
.private-message-container {
  margin-top: 15px;
}

.receiver-input {
  margin-bottom: 15px;
}

.receiver-id-input {
  max-width: 200px;
}

.message-input {
  border-radius: 25px;
}

.online-users {
  grid-area: users;
  background: white;
  margin: 20px 20px 20px 0;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.users-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.users-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.user-count-badge {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 5px 10px;
}

.users-list {
  padding: 10px;
  max-height: calc(100% - 80px);
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 5px;
}

.user-item:hover {
  background: linear-gradient(135deg, #f0f2ff 0%, #e6e9ff 100%);
  transform: translateX(5px);
}

.user-item.current-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-avatar-small {
  width: 35px;
  height: 35px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-item.current-user .user-avatar-small {
  background: rgba(255, 255, 255, 0.2);
}

.user-info-small {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-nickname {
  font-weight: 600;
  font-size: 14px;
}

.user-id-small {
  font-size: 11px;
  opacity: 0.7;
}

.user-status {
  display: flex;
  align-items: center;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.no-users {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  color: #999;
  text-align: center;
}

.no-users i {
  font-size: 32px;
  margin-bottom: 10px;
  opacity: 0.5;
}

.no-users p {
  margin: 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-interface {
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "content"
      "users";
  }
  
  .chat-header {
    padding: 15px 20px;
  }
  
  .header-left {
    gap: 15px;
  }
  
  .chat-title h2 {
    font-size: 20px;
  }
  
  .user-info {
    gap: 10px;
  }
  
  .online-users {
    margin: 0 20px 20px 20px;
    max-height: 200px;
  }
}
</style>