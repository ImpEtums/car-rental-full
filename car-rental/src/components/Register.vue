<template>
  <div class="register-container">
    <div class="cloud cloud1"></div>
    <div class="cloud cloud2"></div>
    <div class="cloud cloud3"></div>
    <div class="cloud cloud4"></div>
    <div class="cloud cloud5"></div>
    <div class="cloud cloud6"></div>
    <div class="cloud cloud7"></div>
    <div class="sun"></div>
    <div class="road-container">
      <div class="road">
        <div class="car">
          <div class="rear-wheel"></div>
          <div class="front-wheel"></div>
          <div class="headlight"></div>
          <div class="exhaust"></div>
        </div>
        <div class="pink-car">
          <div class="pink-rear-wheel"></div>
          <div class="pink-front-wheel"></div>
          <div class="pink-headlight"></div>
          <div class="pink-exhaust"></div>
        </div>
        <div class="blue-car">
          <div class="blue-rear-wheel"></div>
          <div class="blue-front-wheel"></div>
          <div class="blue-headlight"></div>
          <div class="blue-exhaust"></div>
        </div>
        <div class="green-car">
          <div class="green-rear-wheel"></div>
          <div class="green-front-wheel"></div>
          <div class="green-headlight"></div>
          <div class="green-exhaust"></div>
        </div>
        <div class="line"></div>
      </div>
    </div>
    <div class="buildings-container">
      <div class="building building1"></div>
      <div class="building building2"></div>
      <div class="building building3"></div>
      <div class="building building4"></div>
      <div class="building building5"></div>
      <div class="building building6"></div>
      <div class="building building7"></div>
      <div class="building building8"></div>
      <div class="building building9"></div>
      <div class="building building10"></div>
      <div class="building building11"></div>
      <div class="building building12"></div>
      <div class="building building13"></div>
      <div class="building building14"></div>
      <div class="building building15"></div>
      <div class="building building16"></div>
    </div>
    <div class="form-box">
      <h2 class="form-title">用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <label for="username">用户名</label>
          <input
            type="text"
            v-model="user.username"
            id="username"
            placeholder="请输入用户名"
            required
          />
          <span v-if="usernameError" class="error-message">{{ usernameError }}</span>
        </div>

        <div class="input-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            v-model="user.email"
            id="email"
            placeholder="请输入邮箱"
            required
          />
          <span v-if="emailError" class="error-message">{{ emailError }}</span>
        </div>

        <div class="input-group">
          <label for="password">密码</label>
          <input
            type="password"
            v-model="user.password"
            id="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="input-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            v-model="confirmPassword"
            id="confirmPassword"
            placeholder="请确认密码"
            required
          />
        </div>

        <div class="input-group">
          <label for="real_name">真实姓名</label>
          <input
            type="text"
            v-model="user.real_name"
            id="real_name"
            placeholder="请输入真实姓名"
            required
          />
          <span v-if="realNameError" class="error-message">{{ realNameError }}</span>
        </div>

        <div class="input-group">
          <label for="phone">手机号码</label>
          <input
            type="text"
            v-model="user.phone"
            id="phone"
            placeholder="请输入手机号码"
            required
          />
          <span v-if="phoneError" class="error-message">{{ phoneError }}</span>
        </div>

        <div class="input-group">
          <label for="id_number">身份证号码</label>
          <input
            type="text"
            v-model="user.id_number"
            id="id_number"
            placeholder="请输入身份证号码"
            required
          />
          <span v-if="idNumberError" class="error-message">{{ idNumberError }}</span>
        </div>

        <button type="submit" class="submit-btn">注册</button>
      </form>

      <div class="link-to-login">
        <p>已有账号？ <router-link to="/login">登录</router-link></p>
      </div>

      <div v-if="serverError" class="error-message">
        {{ serverError }}
      </div>
    </div>
  </div>
</template>

<script>
import { nodeApiService } from '@/axios';
import { ElMessage } from 'element-plus'; // 引入 Element Plus 的消息提示

export default {
  name: 'Register', // 建议添加组件名称，便于调试
  data() {
    return {
      user: {
        username: '',
        email: '',
        password: '',
        real_name: '',
        phone: '',
        id_number: ''
      },
      confirmPassword: '',
      usernameError: '',
      emailError: '',
      phoneError: '',
      realNameError: '',
      idNumberError: '',
      serverError: ''
    };
  },
  methods: {
    // 身份证号码校验
    isValidIDCard(id) {
      const idRegex = /^\d{17}(\d|X)$/;
      return idRegex.test(id);
    },

    // 校验手机号格式
    isValidPhone(phone) {
      const phoneRegex = /^[1][3-9][0-9]{9}$/;
      return phoneRegex.test(phone);
    },

    // 校验邮箱格式
    isValidEmail(email) {
      const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
      return emailRegex.test(email);
    },

    // 注册处理函数
    async handleRegister() {
      // 清除之前的错误信息
      this.usernameError = '';
      this.emailError = '';
      this.phoneError = '';
      this.realNameError = '';
      this.idNumberError = '';
      this.serverError = '';

      // 客户端校验：密码一致性
      if (this.user.password !== this.confirmPassword) {
        this.serverError = '密码和确认密码不一致！';
        ElMessage.error(this.serverError);
        return;
      }

      // 客户端校验：身份证号码格式
      if (!this.isValidIDCard(this.user.id_number)) {
        this.idNumberError = '身份证号码无效，请重新输入。';
        ElMessage.error(this.idNumberError);
        return;
      }

      // 客户端校验：手机号码格式
      if (!this.isValidPhone(this.user.phone)) {
        this.phoneError = '手机号码格式无效，请重新输入。';
        ElMessage.error(this.phoneError);
        return;
      }

      // 客户端校验：邮箱格式
      if (!this.isValidEmail(this.user.email)) {
        this.emailError = '邮箱格式无效，请重新输入。';
        ElMessage.error(this.emailError);
        return;
      }

      // 客户端校验：其他字段的空值检查
      if (!this.user.username) {
        this.usernameError = '用户名不能为空！';
        ElMessage.error(this.usernameError);
        return;
      }
      if (!this.user.real_name) {
        this.realNameError = '真实姓名不能为空！';
        ElMessage.error(this.realNameError);
        return;
      }

      try {
        const registerResponse = await nodeApiService.post('/auth/register', {
          username: this.user.username,
          email: this.user.email,
          password: this.user.password,
          real_name: this.user.real_name,
          phone: this.user.phone,
          id_number: this.user.id_number
        });

        // *** 核心修改：根据后端返回的 message 字段判断成功 ***
        if (registerResponse.data && registerResponse.data.message === '用户注册成功') {
          this.serverError = ''; // 清除错误信息

          ElMessage.success('注册成功！即将跳转到登录页。');

          // 注册成功后跳转到登录页
          this.$router.push({ name: 'Login' }); // 使用路由的 name 进行跳转，更稳定
        } else {
          // 后端返回了不符合预期成功的消息，或者其他业务逻辑错误
          this.serverError = registerResponse.data.message || '注册失败，请稍后再试！';
          ElMessage.error(this.serverError);
        }
      } catch (error) {
        console.error('注册请求失败:', error); // 输出详细错误到控制台

        if (error.response) {
          const status = error.response.status;
          const message = error.response.data.message;

          if (status === 400) {
            this.serverError = message || '注册信息无效，请检查输入。';
          } else if (status === 409) { // 假设 409 Conflict 表示用户已存在等冲突
            this.serverError = message || '用户已存在或信息冲突。';
          } else if (status === 500) {
            this.serverError = '服务器内部错误，请稍后再试。';
          } else {
            this.serverError = message || `注册时发生未知错误，状态码: ${status}。`;
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应 (通常是网络问题或后端服务未运行)
          this.serverError = '网络连接失败，请检查您的网络或后端服务是否运行。';
        } else {
          // 其他错误（如请求设置错误）
          this.serverError = '请求设置错误，请联系技术支持。';
        }
        ElMessage.error(this.serverError);
      }
    }
  }
};
</script>

<style scoped>
/* 保持你的所有 CSS 样式不变 */
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: skyblue;
  position: relative;
  overflow: hidden;
}

.road-container {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 120px;
  background: #333;
  transform: translateY(-50%);
  z-index: 0;
}

.road {
  position: relative;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.line {
  position: absolute;
  top: 50%;
  left: 0;
  width: 200%;
  height: 4px;
  background: repeating-linear-gradient(
    to right,
    #fff 0%,
    #fff 10%,
    transparent 10%,
    transparent 20%
  );
  background-size: 20px 100%;
  transform: translateY(-50%);
  animation: moveLine 2s linear infinite;
}

.car {
  position: absolute;
  bottom: 30px;
  left: 0;
  width: 100px;
  height: 50px;
  background: #f4c256;
  border-radius: 10px 10px 0 0;
  animation: moveCar 8s linear infinite;
}

.car:before {
  content: '';
  position: absolute;
  top: -15px;
  left: 15px;
  width: 70px;
  height: 20px;
  background: #f4c256;
  border-radius: 8px 8px 0 0;
}

.car:after {
  content: '';
  position: absolute;
  top: -10px;
  left: 20px;
  width: 30px;
  height: 10px;
  background: rgba(200, 230, 255, 0.7);
  border-radius: 4px 0 0 0;
}

.rear-window {
  position: absolute;
  top: -10px;
  right: 20px;
  width: 30px;
  height: 10px;
  background: rgba(200, 230, 255, 0.7);
  border-radius: 0 4px 0 0;
}

.wheel {
  position: absolute;
  bottom: -10px;
  width: 20px;
  height: 20px;
  background: #333;
  border-radius: 50%;
  border: 3px solid #555;
  animation: rotateWheel 1s linear infinite;
}

.front-wheel {
  right: 10px;
}

.rear-wheel {
  left: 10px;
}

.headlight {
  position: absolute;
  bottom: 10px;
  right: -5px;
  width: 10px;
  height: 5px;
  background: #ffeb3b;
  border-radius: 5px 0 0 5px;
  animation: blink 2s infinite;
}

.exhaust {
  position: absolute;
  bottom: 5px;
  left: -15px;
  width: 15px;
  height: 5px;
  background: #eee;
  border-radius: 5px;
  opacity: 0.7;
  animation: puff 1s linear infinite;
}

/* 粉色小车样式 */
.pink-car {
  position: absolute;
  bottom: 60px; /* 调整垂直位置 */
  left: 0;
  width: 80px;
  height: 30px;
  background: #ff69b4;
  border-radius: 5px 5px 0 0;
  animation: movePinkCar 6s linear infinite; /* 不同的动画时间，实现差速 */
}

.pink-car:before {
  content: '';
  position: absolute;
  top: -10px;
  left: 10px;
  width: 60px;
  height: 10px;
  background: #ff69b4;
  border-radius: 5px 5px 0 0;
}

.pink-car:after {
  content: '';
  position: absolute;
  top: -5px;
  left: 15px;
  width: 20px;
  height: 5px;
  background: rgba(255, 200, 230, 0.7);
  border-radius: 3px 0 0 0;
}

.pink-wheel {
  position: absolute;
  bottom: -8px;
  width: 15px;
  height: 15px;
  background: #333;
  border-radius: 50%;
  border: 2px solid #555;
  animation: rotatePinkWheel 0.75s linear infinite; /* 不同的旋转速度 */
}

.pink-front-wheel {
  right: 8px;
}

.pink-rear-wheel {
  left: 8px;
}

.pink-headlight {
  position: absolute;
  bottom: 8px;
  right: -4px;
  width: 8px;
  height: 4px;
  background: #ffeb3b;
  border-radius: 4px 0 0 4px;
  animation: blink 2s infinite;
}

.pink-exhaust {
  position: absolute;
  bottom: 4px;
  left: -12px;
  width: 12px;
  height: 4px;
  background: #eee;
  border-radius: 4px;
  opacity: 0.7;
  animation: puff 1s linear infinite;
}

/* 蓝色小车样式 */
.blue-car {
  position: absolute;
  bottom: 60px;
  left: 0;
  width: 90px;
  height: 40px;
  background: #6495ed;
  border-radius: 8px 8px 0 0;
  animation: moveBlueCar 7s linear infinite;
}

.blue-car:before {
  content: '';
  position: absolute;
  top: -12px;
  left: 12px;
  width: 66px;
  height: 16px;
  background: #6495ed;
  border-radius: 6px 6px 0 0;
}

.blue-car:after {
  content: '';
  position: absolute;
  top: -8px;
  left: 16px;
  width: 24px;
  height: 8px;
  background: rgba(200, 230, 255, 0.7);
  border-radius: 3px 0 0 0;
}

.blue-wheel {
  position: absolute;
  bottom: -9px;
  width: 18px;
  height: 18px;
  background: #333;
  border-radius: 50%;
  border: 3px solid #555;
  animation: rotateBlueWheel 0.85s linear infinite;
}

.blue-front-wheel {
  right: 9px;
}

.blue-rear-wheel {
  left: 9px;
}

.blue-headlight {
  position: absolute;
  bottom: 9px;
  right: -4.5px;
  width: 9px;
  height: 4.5px;
  background: #ffeb3b;
  border-radius: 4.5px 0 0 4.5px;
  animation: blink 2s infinite;
}

.blue-exhaust {
  position: absolute;
  bottom: 4.5px;
  left: -13.5px;
  width: 13.5px;
  height: 4.5px;
  background: #eee;
  border-radius: 4.5px;
  opacity: 0.7;
  animation: puff 1s linear infinite;
}

/* 绿色小车样式 */
.green-car {
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 70px;
  height: 25px;
  background: #32cd32;
  border-radius: 4px 4px 0 0;
  animation: moveGreenCar 9s linear infinite;
}

.green-car:before {
  content: '';
  position: absolute;
  top: -8px;
  left: 8px;
  width: 54px;
  height: 8px;
  background: #32cd32;
  border-radius: 4px 4px 0 0;
}

.green-car:after {
  content: '';
  position: absolute;
  top: -4px;
  left: 12px;
  width: 16px;
  height: 4px;
  background: rgba(200, 230, 255, 0.7);
  border-radius: 2px 0 0 0;
}

.green-wheel {
  position: absolute;
  bottom: -7px;
  width: 13px;
  height: 13px;
  background: #333;
  border-radius: 50%;
  border: 2px solid #555;
  animation: rotateGreenWheel 0.65s linear infinite;
}

.green-front-wheel {
  right: 7px;
}

.green-rear-wheel {
  left: 7px;
}

.green-headlight {
  position: absolute;
  bottom: 7px;
  right: -3.5px;
  width: 7px;
  height: 3.5px;
  background: #ffeb3b;
  border-radius: 3.5px 0 0 3.5px;
  animation: blink 2s infinite;
}

.green-exhaust {
  position: absolute;
  bottom: 3.5px;
  left: -10.5px;
  width: 10.5px;
  height: 3.5px;
  background: #eee;
  border-radius: 3.5px;
  opacity: 0.7;
  animation: puff 1s linear infinite;
}

@keyframes rotateWheel {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotatePinkWheel {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotateBlueWheel {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotateGreenWheel {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0.5; }
}

@keyframes puff {
  0% { transform: scale(0.5); opacity: 0; }
  50% { transform: scale(1); opacity: 0.7; }
  100% { transform: scale(1.5); opacity: 0; }
}

@keyframes moveLine {
  0% { transform: translateX(0) translateY(-50%); }
  100% { transform: translateX(-50%) translateY(-50%); }
}

@keyframes moveCar {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes movePinkCar {
  0% { transform: translateX(-80px); }
  100% { transform: translateX(calc(100vw + 80px)); }
}

@keyframes moveBlueCar {
  0% { transform: translateX(-90px); }
  100% { transform: translateX(calc(100vw + 90px)); }
}

@keyframes moveGreenCar {
  0% { transform: translateX(-70px); }
  100% { transform: translateX(calc(100vw + 70px)); }
}

.form-box {
  background-color: rgba(255, 255, 255, 0.95);
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  width: 400px;
  z-index: 1;
  position: relative;
}

.form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-size: 24px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #cccccc;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-group input:focus {
  border-color: #f4c256;
  outline: none;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #f4c256;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #f4a256;
}

.link-to-login {
  text-align: center;
  margin-top: 15px;
  color: #666;
}

.link-to-login a {
  color: #f4c256;
  text-decoration: none;
  transition: color 0.3s;
}

.link-to-login a:hover {
  color: #f4a256;
  text-decoration: underline;
}

.error-message {
  color: red;
  font-size: 12px;
  margin-top: 5px;
}

/* 白云样式 */
.cloud {
  position: absolute;
  background: #fff;
  border-radius: 100px;
  opacity: 0.8;
}

.cloud:before,
.cloud:after {
  content: '';
  position: absolute;
  background: #fff;
  border-radius: 100px;
}

.cloud1 {
  top: 10%;
  left: -100px;
  width: 120px;
  height: 40px;
  animation: moveCloud1 20s linear infinite;
}

.cloud1:before {
  width: 60px;
  height: 60px;
  top: -20px;
  left: 10px;
}

.cloud1:after {
  width: 40px;
  height: 40px;
  top: -10px;
  right: 10px;
}

.cloud2 {
  top: 25%;
  left: -100px;
  width: 80px;
  height: 25px;
  animation: moveCloud2 15s linear infinite;
}

.cloud2:before {
  width: 40px;
  height: 40px;
  top: -15px;
  left: 10px;
}

.cloud2:after {
  width: 25px;
  height: 25px;
  top: -10px;
  right: 10px;
}

.cloud3 {
  top: 30%;
  left: -100px;
  width: 150px;
  height: 50px;
  animation: moveCloud3 23s linear infinite;
}

.cloud3:before {
  width: 75px;
  height: 75px;
  top: -25px;
  left: 10px;
}

.cloud3:after {
  width: 50px;
  height: 50px;
  top: -15px;
  right: 10px;
}

/* 新添加的4朵云朵 */
.cloud4 {
  top: 5%;
  left: -100px;
  width: 100px;
  height: 30px;
  animation: moveCloud4 25s linear infinite;
}

.cloud4:before {
  width: 50px;
  height: 50px;
  top: -15px;
  left: 10px;
}

.cloud4:after {
  width: 30px;
  height: 30px;
  top: -10px;
  right: 10px;
}

.cloud5 {
  top: 15%;
  left: -100px;
  width: 90px;
  height: 28px;
  animation: moveCloud5 18s linear infinite;
}

.cloud5:before {
  width: 45px;
  height: 45px;
  top: -13px;
  left: 10px;
}

.cloud5:after {
  width: 28px;
  height: 28px;
  top: -8px;
  right: 10px;
}

.cloud6 {
  top: 20%;
  left: -100px;
  width: 110px;
  height: 35px;
  animation: moveCloud6 22s linear infinite;
}

.cloud6:before {
  width: 55px;
  height: 55px;
  top: -18px;
  left: 10px;
}

.cloud6:after {
  width: 35px;
  height: 35px;
  top: -12px;
  right: 10px;
}

.cloud7 {
  top: 35%;
  left: -100px;
  width: 70px;
  height: 22px;
  animation: moveCloud7 13s linear infinite;
}

.cloud7:before {
  width: 35px;
  height: 35px;
  top: -11px;
  left: 10px;
}

.cloud7:after {
  width: 22px;
  height: 22px;
  top: -7px;
  right: 10px;
}

@keyframes moveCloud1 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud2 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud3 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud4 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud5 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud6 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

@keyframes moveCloud7 {
  0% { transform: translateX(-100px); }
  100% { transform: translateX(calc(100vw + 100px)); }
}

/* 太阳样式 */
.sun {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 80px;
  height: 80px;
  background: #ffd700;
  border-radius: 50%;
  box-shadow: 0 0 30px 10px #ffd700;
  animation: shine 2s ease-in-out infinite alternate;
  z-index: 0;
}

@keyframes shine {
  from {
    box-shadow: 0 0 30px 10px #ffd700;
  }
  to {
    box-shadow: 0 0 50px 20px #ffd700;
  }
}

/* 高楼容器样式 */
.buildings-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%; /* 宽度设置为200%，确保有足够的房子填充 */
  height: calc(50% - 60px); /* 马路以下部分 */
  display: flex;
  justify-content: flex-start; /* 左对齐，消除间距 */
  align-items: flex-end;
  z-index: 0;
  animation: moveBuildings 20s linear infinite; /* 添加动画 */
}

/* 高楼样式 */
.building {
  min-width: 120px; /* 设置最小宽度 */
  background-color: #ccc;
  border-radius: 5px 5px 0 0;
  flex-shrink: 0; /* 防止房子收缩 */
}

.building1 {
  height: 180px;
  background-color: #ff7f50;
}

.building2 {
  height: 360px;
  background-color: #6a5acd;
}

.building3 {
  height: 100px;
  background-color: #32cd32;
}

.building4 {
  height: 240px;
  background-color: #ff69b4;
}

.building5 {
  height: 150px;
  background-color:rgb(0, 119, 255);
}

.building6 {
  height: 230px;
  background-color: #ffa500;
}

.building7 {
  height: 380px;
  background-color: #9370db;
}

.building8 {
  height: 280px;
  background-color: #20b2aa;
}

.building9 {
  height: 210px;
  background-color: #ffd700;
}

.building10 {
  height: 320px;
  background-color:rgb(43, 255, 0);
}

.building11 {
  height: 260px;
  background-color: #8a2be2;
}

.building12 {
  height: 190px;
  background-color: #ff8c00;
}

.building13 {
  height: 330px;
  background-color: #008080;
}

.building14 {
  height: 220px;
  background-color: #da70d6;
}

.building15 {
  height: 270px;
  background-color: #1e90ff;
}
.building16 {
  height: 200px;
  background-color:rgb(219, 145, 7);
}

</style>