// 使用WebSocket连接到后端服务
class ChatService {
  constructor() {
    this.connect();
    this.listeners = [];
    this.userId = null;
    this.nickname = null;
    
    // 页面关闭时清理
    window.addEventListener('beforeunload', () => {
      this.leaveChat();
    });
  }
  
  // 连接到WebSocket服务器
  connect() {
    // 连接到后端WebSocket服务
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/`;
    
    // 开发环境下使用固定地址
    this.websocket = new WebSocket('ws://localhost:3005');
    
    this.websocket.onopen = () => {
      console.log('WebSocket连接已建立');
      
      // 如果已登录，发送登录信息
      if (this.userId && this.nickname) {
        this.joinChat(this.userId, this.nickname);
      }
    };
    
    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.notifyListeners(data);
    };
    
    this.websocket.onclose = () => {
      console.log('WebSocket连接已关闭');
      // 尝试重新连接
      setTimeout(() => this.connect(), 3000);
    };
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }
  
  // 添加消息监听器
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }
  
  // 通知所有监听器
  notifyListeners(data) {
    this.listeners.forEach(listener => listener(data));
  }
  
  // 加入聊天
  joinChat(userId, nickname) {
    this.userId = userId;
    this.nickname = nickname;
    
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      // 发送用户登录信息
      this.websocket.send(JSON.stringify({
        type: 'login',
        userId: userId,
        nickname: nickname
      }));
    }
  }
  
  // 离开聊天
  leaveChat() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.close();
    }
    
    this.userId = null;
    this.nickname = null;
  }
  
  // 发送公共消息
  sendPublicMessage(content) {
    if (!this.userId || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) return;
    
    const message = {
      type: 'publicMessage',
      senderId: this.userId,
      senderName: this.nickname,
      content: content,
      timestamp: new Date().toISOString()
    };
    
    this.websocket.send(JSON.stringify(message));
    return message;
  }
  
  // 发送私人消息
  sendPrivateMessage(receiverId, content) {
    if (!this.userId || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) return;
    
    const message = {
      type: 'privateMessage',
      senderId: this.userId,
      senderName: this.nickname,
      receiverId: receiverId,
      content: content,
      timestamp: new Date().toISOString()
    };
    
    this.websocket.send(JSON.stringify(message));
    return message;
  }
  
  // 获取聊天历史记录
  getChatHistory() {
    // 这里可以从localStorage获取缓存的历史记录
    return JSON.parse(localStorage.getItem('chatHistory') || '[]');
  }
}

// 导出单例
export default new ChatService();