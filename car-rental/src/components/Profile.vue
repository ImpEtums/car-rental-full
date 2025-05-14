<template>
  <div class="profile-container">
    <!-- 封面图片 -->
    <div class="cover-image">
      <img src="@/assets/images/profile.jpg" alt="背景图片" />
    </div>

    <!-- 个人信息卡片 -->
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
            <input type="text" v-model="user.real_name" class="form-input disabled" disabled />
          </div>
          <div class="form-group">
            <label>身份证号码</label>
            <input type="text" v-model="user.id_number" class="form-input disabled" disabled />
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

    <!-- 我的订单区域 -->
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
          </div>
        </div>
      </div>
</div>
  </div>
</template>

<script>
import axiosInstance from '@/axios';

export default {
  data() {
    return {
      user: {
        user_id: '',
        username: '',
        email: '',
        real_name: '',
        id_number: '',
        phone: '',
        register_time: '',
      },
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
      ],
      loading: false,
    };
  },
  created() {
    this.fetchUserInfo();
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
        second: '2-digit'
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
        default:
          return '';
      }
    },
    async fetchUserInfo() {
      try {
        const response = await axiosInstance.get('/api/get_user_info', {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.user = response.data.user;
        } else {
          console.error('获取用户信息失败:', response.data.message);
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
      }
    },
    async handleUpdate() {
      try {
        const response = await axiosInstance.put('/api/update_user_info', {
          user_id: this.user.user_id,
          username: this.user.username,
          email: this.user.email,
          phone: this.user.phone,
        }, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          alert('信息更新成功');
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
        const response = await axiosInstance.post('/api/logout', {}, {
          withCredentials: true
        });

        if (response.data.status === 'success') {
          this.$router.push('/login');
        } else {
          alert('退出失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('退出登录失败:', error);
        alert('退出失败');
      }
    },
  },
};
</script>

<style scoped>
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
  box-shadow: 0 0 24px rgba(0,0,0,0.2);
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
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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
}

.order-info {
  text-align: left;
  padding: 10px;
}

.order-info h2 {
  font-size: 1.2rem;
  margin: 0;
  color: #333;
}

.order-info p {
  margin: 5px 0 0;
  color: #555;
}

.status-picked {
  color: #22c55e;
  font-weight: 600;
}

.status-waiting {
  color: #f9a916;
  font-weight: 600;
}

.status-cancelled{
  color: #dc3545;
  font-weight: 600;
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
}
</style>