<template>
  <div class="chat-interface">
    <div class="chat-header">
      <h2>在线聊天室</h2>
      <div class="user-info">
        <span>当前用户: {{ currentUser.nickname }}</span>
        <el-button type="text" @click="logout">退出登录</el-button>
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
      </div>
      
      <div class="input-area">
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane label="公共消息" name="public">
            <div class="message-input-container">
              <el-input
                v-model="publicMessage"
                placeholder="输入广播消息..."
                @keyup.enter="sendPublicMessage"
              >
                <template #append>
                  <el-button @click="sendPublicMessage">发送</el-button>
                </template>
              </el-input>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="私人消息" name="private">
            <div class="private-message-container">
              <el-input
                v-model="receiverId"
                placeholder="输入对方ID"
                style="width: 150px; margin-right: 10px;"
              ></el-input>
              <el-input
                v-model="privateMessage"
                placeholder="输入私信内容..."
                @keyup.enter="sendPrivateMessage"
              >
                <template #append>
                  <el-button @click="sendPrivateMessage">发送私信</el-button>
                </template>
              </el-input>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <div class="online-users">
      <h3>在线用户 ({{ onlineUsers.length }})</h3>
      <el-tag
        v-for="user in onlineUsers"
        :key="user.id"
        effect="plain"
        size="medium"
        :type="user.id === currentUser.id ? 'success' : 'info'"
        class="user-tag"
        @click="selectReceiver(user)"
      >
        {{ user.nickname }}
      </el-tag>
      <div v-if="onlineUsers.length === 0" class="no-users">
        暂无其他用户在线
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
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr 250px;
  grid-template-areas:
    "header header"
    "content users"
    "content users";
  gap: 15px;
  height: 80vh;
}

.chat-header {
  grid-area: header;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.chat-content {
  grid-area: content;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 15px;
}

.input-area {
  margin-top: auto;
}

.message-input-container,
.private-message-container {
  margin-top: 10px;
}

.online-users {
  grid-area: users;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  overflow-y: auto;
}

.user-tag {
  margin: 5px;
  cursor: pointer;
}

.no-users {
  color: #999;
  margin-top: 10px;
  font-style: italic;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>