<template>
  <div class="profile-container">
    <div class="cover-image">
      <img src="@/assets/images/profile.jpg" alt="背景图片" />
    </div>

    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-container">
          <div class="avatar">🐰</div>
        </div>
        <div class="profile-info">
          <h2>{{ user.username }}</h2>
          <p class="user-bio">{{ user.email }}</p>
          <button class="edit-profile-btn" @click="handleUpdate">编辑资料</button>
        </div>
      </div>

      <form @submit.prevent="handleUpdate" class="profile-form">
        <div class="form-grid">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" v-model="user.username" class="form-input" required />
          </div>
          <div class="form-group">
            <label>电子邮箱</label>
            <input type="email" v-model="user.email" class="form-input" required />
          </div>
          <div class="form-group">
            <label>真实姓名</label>
            <input type="text" v-model="user.real_name" class="form-input" required />
          </div>
          <div class="form-group">
            <label>身份证号码</label>
            <input type="text" v-model="user.id_number" class="form-input" required />
          </div>
          <div class="form-group">
            <label>手机号码</label>
            <input type="text" v-model="user.phone" class="form-input" required />
          </div>
          <div class="form-group">
            <label>注册时间</label>
            <input
              type="text"
              :value="formatDateTime(user.register_time)"
              class="form-input disabled"
              disabled
            />
          </div>
        </div>

        <div class="button-group">
          <button type="submit" class="primary-btn">保存更改</button>
          <button type="button" @click="logout" class="secondary-btn">退出登录</button>
        </div>
      </form>
    </div>

    <div class="orders-section">
      <h2>我的订单</h2>
      <div class="showcase-grid">
        <div class="order-item" v-for="(order, index) in orders" :key="index">
          <img :src="order.image" :alt="order.name" />
          <div class="order-info">
            <h2>{{ order.name }}</h2>
            <p>状态：<span :class="getStatusClass(order.status_description)">{{ order.status_description }}</span></p>
            <p>租借天数：{{ order.rental_days }}天</p>
            <p>总金额：{{ order.total_amount }}</p>
            <p>押金：{{ order.deposit }}</p>
            <p>下单时间：{{ formatDateTime(order.order_time) }}</p>
            <div class="order-actions">
              <button class="view-btn" @click="viewOrder(order)">查看</button>
              <button 
                class="delete-btn" 
                @click="deleteOrder(order, index)"
                :class="{ disabled: !canDeleteOrder(order) }"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="viewingOrder" class="modal-overlay">
        <div class="modal-content">
          <h2>查看订单</h2>
          <div class="form-group">
            <label>订单名称</label>
            <input type="text" :value="viewingOrder.name" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label>状态</label>
            <input type="text" :value="viewingOrder.status_description" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label>租借天数</label>
            <input type="number" :value="viewingOrder.rental_days" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label>总金额</label>
            <input type="number" :value="viewingOrder.total_amount" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label>押金</label>
            <input type="number" :value="viewingOrder.deposit" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label>下单时间</label>
            <div class="date-inputs">
              <select :value="viewingOrder.year" class="date-select" disabled>
                <option v-for="year in years" :value="year" :key="year">{{ year }}</option>
              </select>
              <select :value="viewingOrder.month" class="date-select" disabled>
                <option v-for="month in months" :value="month" :key="month">{{ month }}</option>
              </select>
              <select :value="viewingOrder.day" class="date-select" disabled>
                <option v-for="day in days" :value="day" :key="day">{{ day }}</option>
              </select>
            </div>
          </div>
          <button class="question-btn" @click="openFeedbackModal">对此订单有疑问</button>
          <div class="modal-actions">
            <button type="button" @click="closeViewModal" class="secondary-btn">关闭</button>
          </div>
        </div>
      </div>

      <div v-if="isFeedbackModalOpen" class="modal-overlay">
        <div class="modal-content">
          <h2>订单反馈</h2>
          <div class="form-group">
            <label>反馈类型</label>
            <div v-for="(option, index) in feedbackOptions" :key="index">
              <input type="radio" :id="option" :value="option" v-model="selectedFeedbackOption" />
              <label :for="option">{{ option }}</label>
            </div>
          </div>
          <div class="form-group">
            <label>详细内容</label>
            <textarea
              v-model="feedbackDetail"
              placeholder="提供疑问的具体内容"
              class="form-input"
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="cancelFeedback" class="secondary-btn">取消</button>
            <button type="button" @click="submitFeedback" class="primary-btn">提交</button>
          </div>
        </div>
      </div>

      <div v-if="showSuccessNotification" class="notification success">
        <p>{{ successMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
// 导入 Node.js 和 Flask 的 Axios 实例
import { flaskApiService, nodeApiService } from '@/axios';
// 如果你需要路由跳转，请确保正确导入 router 实例
// import router from '@/router';

export default {
  data() {
    return {
      user: {
        user_id: '',
        username: '',
        email: '',
        real_name: '', // 映射 Node.js 后端返回的 realName
        id_number: '', // 映射 Node.js 后端返回的 idNumber
        phone: '',
        register_time: '', // 映射 Node.js 后端返回的 createdAt
      },
      // 订单数据，如果未来从 Node.js 后端获取，也需要调整
      orders: [
        {
          order_id: 1,
          user_id: 101,
          car_id: 202,
          pickup_store_id: 301,
          return_store_id: 302,
          order_time: '2023-12-01T10:00:00',
          start_time: '2023-12-05T10:00:00',
          end_time: '2023-12-10T10:00:00',
          actual_start_time: '2023-12-05T10:00:00',
          actual_end_time: null,
          rental_days: 5,
          total_amount: 1000.00,
          deposit: 200.00,
          coupon_id: null,
          discount_amount: 0.00,
          create_time: '2023-12-01T09:00:00',
          update_time: '2023-12-01T09:00:00',
          status: 1,
          image: new URL(`../assets/images/c1.png`, import.meta.url).href,
          name: '订单 001',
          status_description: '已取车',
        },
        {
          order_id: 2,
          user_id: 101,
          car_id: 203,
          pickup_store_id: 301,
          return_store_id: 302,
          order_time: '2023-12-02T10:00:00',
          start_time: '2023-12-06T10:00:00',
          end_time: '2023-12-11T10:00:00',
          actual_start_time: null,
          actual_end_time: null,
          rental_days: 5,
          total_amount: 800.00,
          deposit: 150.00,
          coupon_id: null,
          discount_amount: 0.00,
          create_time: '2023-12-02T09:00:00',
          update_time: '2023-12-02T09:00:00',
          status: 0,
          image: new URL(`../assets/images/c2.png`, import.meta.url).href,
          name: '订单 002',
          status_description: '已取车',
        },
        {
          order_id: 3,
          user_id: 101,
          car_id: 204,
          pickup_store_id: 301,
          return_store_id: 302,
          order_time: '2023-12-03T10:00:00',
          start_time: '2023-12-07T10:00:00',
          end_time: '2023-12-12T10:00:00',
          actual_start_time: '2023-12-07T10:00:00',
          actual_end_time: '2023-12-12T10:00:00',
          rental_days: 5,
          total_amount: 1200.00,
          deposit: 250.00,
          coupon_id: null,
          discount_amount: 0.00,
          create_time: '2023-12-03T09:00:00',
          update_time: '2023-12-03T09:00:00',
          status: 2,
          image: new URL(`../assets/images/c3.png`, import.meta.url).href,
          name: '订单 003',
          status_description: '待取车',
        },
        {
          order_id: 4,
          user_id: 101,
          car_id: 205,
          pickup_store_id: 301,
          return_store_id: 302,
          order_time: '2023-12-04T10:00:00',
          start_time: '2023-12-08T10:00:00',
          end_time: '2023-12-13T10:00:00',
          actual_start_time: null,
          actual_end_time: null,
          rental_days: 5,
          total_amount: 900.00,
          deposit: 180.00,
          coupon_id: null,
          discount_amount: 0.00,
          create_time: '2023-12-04T09:00:00',
          update_time: '2023-12-04T09:00:00',
          status: 0,
          image: new URL(`../assets/images/c4.png`, import.meta.url).href,
          name: '订单 004',
          status_description: '已取消',
        },
        {
          order_id: 5,
          user_id: 101,
          car_id: 206,
          pickup_store_id: 301,
          return_store_id: 302,
          order_time: '2023-12-05T10:00:00',
          start_time: '2023-12-10T10:00:00',
          end_time: '2023-12-15T10:00:00',
          actual_start_time: '2023-12-10T10:00:00',
          actual_end_time: '2023-12-15T10:00:00',
          rental_days: 5,
          total_amount: 1500.00,
          deposit: 300.00,
          coupon_id: null,
          discount_amount: 0.00,
          create_time: '2023-12-05T09:00:00',
          update_time: '2023-12-15T16:30:00',
          status: 3,
          image: new URL(`../assets/images/c4.png`, import.meta.url).href,
          name: '订单 005',
          status_description: '已完成',
        },
      ],
      loading: false,
      viewingOrder: null,
      isFeedbackModalOpen: false,
      feedbackOptions: [
        '金额异常',
        '时间错误',
        '地点偏差',
        '车型不符',
        '车辆状态问题',
        '车辆证件不全',
        '条款模糊或误导',
        '权益限制未明示',
        '服务遗漏或延迟',
        '保险纠纷',
      ],
      selectedFeedbackOption: '',
      feedbackDetail: '',
      years: Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - 5 + i),
      months: Array.from({ length: 12 }, (_, i) => i + 1),
      days: Array.from({ length: 31 }, (_, i) => i + 1),
      showSuccessNotification: false,
      successMessage: '',
    };
  },
  created() {
    this.fetchUserInfo();
    this.fetchUserOrders();
  },
  // 添加路由监听
  watch: {
    '$route'(to, from) {
      // 当路由变化时重新获取数据
      if (to.path === '/profile') {
        this.fetchUserOrders();
      }
    }
  },
  // 或者使用activated生命周期（如果使用了keep-alive）
  activated() {
    this.fetchUserOrders();
  },
  methods: {
    formatDateTime(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    },
    getStatusClass(status) {
      switch (status) {
        case '已取车':
          return 'status-picked';
        case '待取车':
          return 'status-waiting';
        case '已取消':
          return 'status-cancelled';
        case '已完成':
          return 'status-completed';
        default:
          return '';
      }
    },
    async fetchUserInfo() {
      // 首先检查是否有token
      const token = localStorage.getItem('token');
      if (!token) {
        this.$router.push('/login');
        return;
      }
      
      try {
        const response = await nodeApiService.get('/auth/me');
        
        if (response.data && response.data.user) {
          this.user.user_id = response.data.user.userId;
          this.user.username = response.data.user.username;
          this.user.email = response.data.user.email;
          this.user.real_name = response.data.user.realName;
          this.user.id_number = response.data.user.idNumber;
          this.user.phone = response.data.user.phone;
          this.user.register_time = response.data.user.registerTime;
        } else {
          console.error('获取用户信息失败: 响应数据格式不正确', response.data);
          this.error = '无法获取个人中心数据，请检查后端响应。';
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          // 认证失败，清除token并跳转到登录页
          localStorage.removeItem('token');
          this.$router.push('/login');
          return;
        }
        this.error = '获取个人中心数据失败。请检查网络或重新登录。';
      }
    },
    // 注意：handleUpdate 和 logout 如果也要更新/操作 Node.js 后端的用户信息，
    // 也应该修改为使用 nodeApiService，并确保后端有对应的 API 路由。
    async handleUpdate() {
      try {
        // 假设更新用户信息也是通过 Node.js 后端完成
        const response = await nodeApiService.put('/auth/update_profile', { // 假设后端更新用户信息的API是 /api/auth/update_profile
          username: this.user.username,
          email: this.user.email,
          phone: this.user.phone,
          // real_name 和 id_number 通常不允许前端修改，或者在后端进行校验
          // 如果后端允许修改，这里也需要传递它们
        });

        if (response.data.message === 'User profile updated successfully') { // 假设后端成功时返回这样的消息
          alert('信息更新成功');
          // 重新获取用户信息以确保视图同步
          this.fetchUserInfo();
        } else {
          alert('更新失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('更新失败:', error);
        alert('更新失败: ' + (error.response?.data?.message || error.message));
      }
    },
    async logout() {
      try {
        // 清除所有可能的token和用户信息
        localStorage.removeItem('token'); // 主要的token
        localStorage.removeItem('jwt_token'); // 聊天用的token
        localStorage.removeItem('userId'); // 用户ID
        localStorage.removeItem('username'); // 用户名
        localStorage.removeItem('user_id'); // 其他可能的用户ID
        
        // 清空组件的用户数据
        this.user = {
          user_id: '',
          username: '',
          email: '',
          real_name: '',
          id_number: '',
          phone: '',
          register_time: ''
        };
        
        alert('您已成功退出登录。');
        this.$router.push('/login'); // 跳转到登录页面
      } catch (error) {
        console.error('退出登录失败:', error);
        alert('退出失败: ' + (error.message || '未知错误'));
      }
    },
    viewOrder(order) {
      this.viewingOrder = { ...order };
    },
    closeViewModal() {
      this.viewingOrder = null;
    },
    openFeedbackModal() {
      this.isFeedbackModalOpen = true;
    },
    closeFeedbackModal() {
      this.isFeedbackModalOpen = false;
    },
    deleteOrder(order, index) {
      if (!this.canDeleteOrder(order)) {
        alert(`该订单当前尚未结束，不可以删除。`);
        return;
      }
      
      if (confirm('确定要删除此订单吗？')) {
        // In a real app, you would call an API here (可能通过 Flask 或 Node.js 后端)
        this.orders.splice(index, 1);
        this.successMessage = '订单已删除。';
        this.showSuccessNotification = true;
        setTimeout(() => { this.showSuccessNotification = false; }, 3000);
      }
    },
    submitFeedback() {
      if (!this.selectedFeedbackOption || !this.feedbackDetail) {
        alert('请选择反馈类型并填写详细内容');
        return;
      }
      
      if (confirm('确认提交反馈吗？')) {
        // 这里可以添加提交反馈到后端的逻辑 (可能通过 Flask 或 Node.js 后端)
        console.log('反馈已提交：', {
          selectedFeedbackOption: this.selectedFeedbackOption,
          feedbackDetail: this.feedbackDetail,
        });
        
        this.successMessage = '提交成功，后续有结果将联系您解决';
        this.showSuccessNotification = true;
        
        setTimeout(() => {
          this.showSuccessNotification = false;
        }, 3000);
        
        this.isFeedbackModalOpen = false;
        this.selectedFeedbackOption = '';
        this.feedbackDetail = '';
      }
    },
    cancelFeedback() {
      if (this.selectedFeedbackOption || this.feedbackDetail) {
        if (confirm('是否保存此次提交内容？')) {
          console.log('反馈内容已保存：', {
            selectedFeedbackOption: this.selectedFeedbackOption,
            feedbackDetail: this.feedbackDetail,
          });
        }
      }
      this.isFeedbackModalOpen = false;
      this.selectedFeedbackOption = '';
      this.feedbackDetail = '';
    },
    getDaysInMonth(year, month) {
      return new Date(year, month, 0).getDate();
    },
    canDeleteOrder(order) {
      return order.status_description === '已完成' || order.status_description === '已取消';
    },
    // 添加获取订单数据的方法
    async fetchUserOrders() {
      const token = localStorage.getItem('token');
      if (!token) {
        this.$router.push('/login');
        return;
      }
      
      try {
        const response = await fetch('/api/user_orders', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
          this.orders = data.orders.map(order => {
            const date = new Date(order.order_time);
            return {
              ...order,
              year: date.getFullYear(),
              month: date.getMonth() + 1,
              day: date.getDate(),
              image: new URL(`../assets/images/c1.png`, import.meta.url).href
            };
          });
          console.log('订单数据已更新:', this.orders.length, '条订单');
        } else {
          console.error('获取订单失败:', data.message);
          if (response.status === 401) {
            localStorage.removeItem('token');
            this.$router.push('/login');
          }
        }
      } catch (error) {
        console.error('获取订单数据失败:', error);
      }
    },
  },
};
</script>

<style scoped>
/* 你的 CSS 样式保持不变 */
.page-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.cover-image {
  height: 280px;
  overflow: hidden;
  position: relative;
}

.cover-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.2);
}

.profile-card {
  padding: 2rem;
  margin-top: -50px;
  position: relative;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  margin: -50px 2rem 0;
  backdrop-filter: blur(0.3s1px);
}

.profile-header {
  display: flex;
  align-items: flex-end;
  margin-bottom: 2rem;
  justify-content: flex-start;
}

.avatar-container {
  margin-right: 2rem;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #f4ed94;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
  border: 4px solid white;
  margin-top: -40px;
}

.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.profile-info h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
}

.user-bio {
  color: #666;
  margin: 0.5rem 0;
}

.edit-profile-btn {
  padding: 0.5rem 1rem;
  background-color: #f4d05b;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.form-group label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.form-input.disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.primary-btn {
  padding: 0.75rem 2rem;
  background-color: #f8d562;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.secondary-btn {
  padding: 0.75rem 2rem;
  background-color: white;
  color: #dc3545;
  border: 1px solid #dc3545;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.primary-btn:hover {
  background-color: #f9a012;
}

.secondary-btn:hover {
  background-color: #dc3545;
  color: white;
}

.orders-section {
  padding: 2rem;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  margin: 2rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.orders-section h2 {
  margin-bottom: 1rem;
  color: #333;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.order-item {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.order-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

.order-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.order-info {
  text-align: left;
  padding: 15px;
}

.order-info h2 {
  font-size: 1.2rem;
  margin: 0 0 10px 0;
  color: #333;
}

.order-info p {
  margin: 5px 0 0;
  color: #555;
  font-size: 0.9rem;
}

.status-picked {
  color: #22c55e;
  font-weight: 600;
}

.status-waiting {
  color: #f9a916;
  font-weight: 600;
}

.status-cancelled {
  color: #dc3545;
  font-weight: 600;
}

.status-completed {
  color: #22c55e;
  font-weight: 600;
}

.order-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.view-btn, .delete-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.view-btn {
  background-color: #f8d562;
  color: white;
}

.view-btn:hover {
  background-color: #f9a012;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}

.delete-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
  text-align: center;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.date-inputs {
  display: flex;
  gap: 10px;
}

.date-select {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
}

.question-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  background-color: #f8d562;
  color: white;
  margin-top: 15px;
}

.question-btn:hover {
  background-color: #f9a012;
}

/* Success Notification */
.notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 15px 30px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.notification.success {
  background-color: #22c55e;
}

.notification.show {
  opacity: 1;
}

@media (max-width: 768px) {
  .profile-card {
    margin: -50px 1rem 0;
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .avatar-container {
    margin-right: 0;
    margin-bottom: 1rem;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    width: 100%;
  }

  .primary-btn, .secondary-btn {
    width: 100%;
  }

  .showcase-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95%;
    padding: 1rem;
  }

  .date-inputs {
    flex-direction: column;
  }
}</style>
