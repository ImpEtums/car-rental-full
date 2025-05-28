<template>
  <div class="login-container">
    <h2>欢迎使用在线聊天</h2>
    <el-form :model="loginForm" :rules="rules" ref="loginForm">
      <el-form-item prop="nickname">
        <el-input 
          v-model="loginForm.nickname" 
          placeholder="请输入英文昵称"
          prefix-icon="el-icon-user"
          @keyup.enter="submitLogin"
        >
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitLogin" :loading="loading">
          登录聊天室
        </el-button>
      </el-form-item>
    </el-form>
    <div v-if="errorMessage" style="color: red; margin-top: 10px;">{{ errorMessage }}</div>
  </div>
</template>

<script>
// 引入 Node.js 的 Axios 实例
import { nodeApiService } from '@/axios'; // 确保路径正确

export default {
  name: 'LoginForm',
  data() {
    const validateNickname = (rule, value, callback) => {
      if (!value) {
        return callback(new Error('请输入昵称'));
      }
      if (!/^[a-zA-Z0-9_]+$/.test(value)) {
        return callback(new Error('昵称只能包含英文字母、数字和下划线'));
      }
      callback();
    };
    
    return {
      loginForm: {
        nickname: ''
      },
      rules: {
        nickname: [
          { required: true, message: '请输入昵称', trigger: 'blur' },
          { validator: validateNickname, trigger: 'blur' }
        ]
      },
      loading: false,
      errorMessage: '' // 新增错误消息状态
    };
  },
  methods: {
    submitLogin() {
      this.$refs.loginForm.validate(async valid => { // 使用 async/await
        if (valid) {
          this.loading = true;
          this.errorMessage = ''; // 清除之前的错误消息

          try {
            // 调用 Node.js 后端的聊天登录 API
            const response = await nodeApiService.post('/auth/chat-login', {
              nickname: this.loginForm.nickname
            });

            // 登录成功
            if (response.data && response.data.token) {
              // 存储 JWT
              localStorage.setItem('jwt_token', response.data.token);
              console.log('Chat login successful! Token stored:', response.data.token);
              
              // 触发父组件的 'login' 事件，并传递用户数据
              this.$emit('login', { 
                id: response.data.userId, // 从 Node.js 响应获取用户 ID
                nickname: response.data.nickname, // 从 Node.js 响应获取昵称
                loginTime: new Date().toISOString()
              });
            } else {
              this.errorMessage = '登录失败，未收到有效的认证信息。';
            }
          } catch (error) {
            console.error('聊天登录请求失败:', error.response ? error.response.data : error.message);
            this.errorMessage = error.response?.data?.message || '登录请求失败，请检查网络或稍后再试。';
          } finally {
            this.loading = false;
          }
        }
      });
    }
  }
}
</script>

<style scoped>
/* 保持你的样式不变 */
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

h2 {
  margin-bottom: 30px;
  color: #409EFF;
}
</style>