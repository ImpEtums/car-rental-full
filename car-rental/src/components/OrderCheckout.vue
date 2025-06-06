<template>
  <div class="checkout-page">
    <h1 class="page-title"> </h1>
    
    <div class="checkout-container">
      <!-- 左侧车辆信息 -->
      <div class="car-info-section">
        <img :src="carData.image" :alt="carData.name" class="car-image"/>
        <div class="car-details">
          <h2>{{ carData.name }}</h2>
          <div class="car-specs">
            <div class="spec-item">
              <span class="label">车牌号码：</span>
              <span>沪A 88888</span>
            </div>
            <div class="spec-item">
              <span class="label">车辆等级：</span>
              <span>豪华型</span>
            </div>
            <div class="spec-item">
              <span class="label">座位数：</span>
              <span>{{ carData.seats }}座</span>
            </div>
            <div class="spec-item">
              <span class="label">变速箱：</span>
              <span>{{ carData.transmission }}</span>
            </div>
          </div>

          <!-- 个人信息 -->
          <div class="personal-info">
            <h3>个人信息</h3>
            
            <!-- 显示模式 -->
            <div v-if="!isEditingPersonalInfo" class="info-display">
              <div class="info-item">
                <span class="label">姓名：</span>
                <span class="value">{{ userInfo.real_name || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">手机号：</span>
                <span class="value">{{ userInfo.phone || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">身份证号：</span>
                <span class="value">{{ userInfo.id_number || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱：</span>
                <span class="value">{{ userInfo.email || '未填写' }}</span>
              </div>
              <button type="button" @click="startEditPersonalInfo" class="edit-info-btn">
                {{ hasCompleteInfo ? '修改信息' : '完善信息' }}
              </button>
            </div>
            
            <!-- 编辑模式 -->
            <div v-else class="info-edit">
              <div class="form-group">
                <label>姓名：</label>
                <input 
                  type="text" 
                  v-model="editingUserInfo.real_name" 
                  placeholder="请输入真实姓名"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>手机号：</label>
                <input 
                  type="tel" 
                  v-model="editingUserInfo.phone" 
                  placeholder="请输入手机号码"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>身份证号：</label>
                <input 
                  type="text" 
                  v-model="editingUserInfo.id_number" 
                  placeholder="请输入身份证号码"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>邮箱：</label>
                <input 
                  type="email" 
                  v-model="editingUserInfo.email" 
                  placeholder="请输入邮箱地址"
                  class="form-input"
                />
              </div>
              <div class="button-group">
                <button type="button" @click="saveUserInfo" class="save-info-btn">保存</button>
                <button type="button" @click="cancelEditPersonalInfo" class="cancel-info-btn">取消</button>
              </div>
            </div>
          </div>
          <div class="rental-trend-chart">
            <h3>近期租赁趋势</h3>
            <div ref="chartContainer" style="width: 100%; height: 250px;"></div>
            </div>
        </div>
      </div>

      <!-- 右侧订单信息 -->
      <div class="order-info-section">
        <div class="pickup-return-info">
          <div class="location-time">
            <h3>取还车信息</h3>
            <div class="location-item">
              <img src="../assets/images/icons/location.png" alt="location" class="location-icon" />
              <div class="info">
                <div class="type">取车地点</div>
                <div class="value">{{ rentalInfo.pickupLocation }}</div>
                <div class="time">{{ formatDateTime(rentalInfo.pickupTime) }}</div>
              </div>
            </div>
            <div class="location-item">
              <img src="../assets/images/icons/location.png" alt="location" class="location-icon" />
              <div class="info">
                <div class="type">还车地点</div>
                <div class="value">{{ rentalInfo.returnLocation }}</div>
                <div class="time">{{ formatDateTime(rentalInfo.returnTime) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="insurance-options">
          <h3>保险方案选择</h3>
          <div class="insurance-item" :class="{ 'selected': selectedInsurance === 'full' }" @click="selectInsurance('full')">
            <div class="insurance-header">
              <div class="insurance-title">
                <span class="shield-icon">🛡️</span>
                全面保障型
                <span class="recommend-tag">推荐</span>
              </div>
              <div class="insurance-price">¥300/天</div>
            </div>
            <div class="insurance-details">
              <div class="detail-item">✓ 车辆损失险（免赔额1000元）</div>
              <div class="detail-item">✓ 第三者责任险（300万元）</div>
              <div class="detail-item">✓ 车上人员责任险（100万元）</div>
              <div class="detail-item">✓ 全车盗抢险</div>
              <div class="detail-item">✓ 玻璃保障险</div>
            </div>
          </div>

          <div class="insurance-item" :class="{ 'selected': selectedInsurance === 'basic' }" @click="selectInsurance('basic')">
            <div class="insurance-header">
              <div class="insurance-title">
                <span class="shield-icon">🛡️</span>
                基础保障型
              </div>
              <div class="insurance-price">¥150/天</div>
            </div>
            <div class="insurance-details">
              <div class="detail-item">✓ 车辆损失险（免赔额3000元）</div>
              <div class="detail-item">✓ 第三者责任险（100万元）</div>
              <div class="detail-item">✓ 车上人员责任险（50万元）</div>
            </div>
          </div>
        </div>

        <div class="coupon-section">
          <h3>优惠券选择</h3>
          <select v-model="selectedCoupon" class="coupon-select">
            <option value="">无优惠券</option>
            <option v-for="coupon in availableCoupons" 
                    :key="coupon.id" 
                    :value="coupon.id">
              {{ coupon.name }} (优惠 ¥{{ coupon.amount }})
            </option>
          </select>
        </div>

        <div class="price-summary">
          <div class="price-item">
            <span>车辆租赁费</span>
            <span>¥{{ rentalFee }}</span>
          </div>
          <div class="price-item">
            <span>保险费用</span>
            <span>¥{{ insurancePrice }}</span>
          </div>
          <div class="price-item">
            <span>车辆押金</span>
            <span>¥150</span>
          </div>
          <div class="price-item discount">
            <span>优惠金额</span>
            <span>-¥{{ discountAmount }}</span>
          </div>
          <div class="price-item total">
            <span>应付总额</span>
            <span>¥{{ totalPrice }}</span>
          </div>
        </div>

        <div class="payment-methods">
          <h3>支付方式</h3>
          <div class="payment-options">
            <div class="payment-option" :class="{ 'selected': selectedPayment === 'alipay' }" @click="selectPayment('alipay')">
              <img src="../assets/images/icons/alipay.png" alt="支付宝" />
              <span>支付宝</span>
            </div>
            <div class="payment-option" :class="{ 'selected': selectedPayment === 'wechat' }" @click="selectPayment('wechat')">
              <img src="../assets/images/icons/wechat.png" alt="微信支付" />
              <span>微信支付</span>
            </div>
            <div class="payment-option" :class="{ 'selected': selectedPayment === 'card' }" @click="selectPayment('card')">
              <img src="../assets/images/icons/card.png" alt="银行卡" />
              <span>银行卡</span>
            </div>
          </div>
        </div>

        <button class="submit-button" @click="handleSubmit">确认支付</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Highcharts from 'highcharts'

const route = useRoute()
const router = useRouter()

// 从路由参数获取车辆数据
const carData = ref({
  car_id: Number(route.query.car_id) || Number(route.params.id) || 1,
  name: route.query.name || '',
  price: Number(route.query.price) || 0,
  seats: route.query.seats || 5,
  transmission: route.query.transmission || '自动',
  image: route.query.image || ''
})

// 从路由参数获取租车信息
const rentalInfo = ref({
  pickupLocation: route.query.pickupLocation || '浙江省杭州市西湖区武林门店',
  returnLocation: route.query.returnLocation || '浙江省杭州市西湖区西湖风景区店',
  pickupTime: route.query.pickupTime ? new Date(Number(route.query.pickupTime)) : new Date(),
  returnTime: route.query.returnTime ? new Date(Number(route.query.returnTime)) : new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
  pickupStationId: route.query.pickupStationId || 301,
  returnStationId: route.query.returnStationId || 302
})

// 根据实际选择的时间计算租赁天数
const rentalDays = computed(() => {
  const diffTime = rentalInfo.value.returnTime.getTime() - rentalInfo.value.pickupTime.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return Math.max(1, diffDays) // 至少1天
})

// 格式化日期时间显示
const formatDateTime = (date) => {
  if (!date) return ''
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算车辆租金
const rentalFee = computed(() => {
  return carData.value.price * rentalDays.value
})

const selectedInsurance = ref('full')
const selectedPayment = ref('alipay')
const selectedCoupon = ref('')

// 可用优惠券列表
const availableCoupons = ref([
  { id: '1', name: '新用户优惠券', amount: 300 },
  { id: '2', name: '周末特惠券', amount: 200 },
  { id: '3', name: '节日优惠券', amount: 500 }
])

// 计算优惠金额
const discountAmount = computed(() => {
  if (!selectedCoupon.value) return 0
  const coupon = availableCoupons.value.find(c => c.id === selectedCoupon.value)
  return coupon ? coupon.amount : 0
})

// 计算保险费用
const insurancePrice = computed(() => {
  return selectedInsurance.value === 'full' ? 300 : 150
})

// 计算总价
const totalPrice = computed(() => {
  return rentalFee.value + insurancePrice.value + 150 - discountAmount.value
})

// 选择保险方案
const selectInsurance = (type) => {
  selectedInsurance.value = type
}

// 选择支付方式
const selectPayment = (method) => {
  selectedPayment.value = method
}

// 修改提交订单方法
const handleSubmit = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('请先登录');
      router.push('/login');
      return;
    }

    // 验证必要信息
    if (!userInfo.value.real_name || !userInfo.value.phone || !userInfo.value.id_number) {
      alert('请先完善个人信息（姓名、手机号、身份证号）')
      startEditPersonalInfo()
      return
    }
    
    if (!selectedPayment.value) {
      alert('请选择支付方式')
      return
    }
    
    // 准备订单数据
    const orderData = {
      car_id: carData.value.car_id || 1,
      pickup_store_id: rentalInfo.value.pickupStationId,
      return_store_id: rentalInfo.value.returnStationId,
      start_time: rentalInfo.value.pickupTime.toISOString(),
      end_time: rentalInfo.value.returnTime.toISOString(),
      rental_days: rentalDays.value,
      total_amount: totalPrice.value,
      deposit: 150.00,
      coupon_id: selectedCoupon.value || null,
      discount_amount: discountAmount.value,
      insurance_type: selectedInsurance.value,
      payment_method: selectedPayment.value
    }
    
    // 调用Flask后端的创建订单API，添加JWT认证
    const response = await fetch('/api/create_order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(orderData)
    })
    
    if (response.status === 401) {
      alert('登录已过期，请重新登录');
      localStorage.removeItem('token');
      router.push('/login');
      return;
    }

    const result = await response.json()
    
    if (result.status === 'success') {
      alert('订单创建成功！')
      router.push('/orders')
    } else {
      alert('订单创建失败: ' + result.message)
    }
    
  } catch (error) {
    console.error('创建订单失败:', error)
    alert('创建订单失败，请稍后重试')
  }
}

// 添加用户信息状态
const userInfo = ref({})

// 获取用户信息的函数
const fetchUserInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('未找到登录token');
      alert('请先登录');
      router.push('/login');
      return;
    }

    const response = await fetch('/api/get_user_info', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      console.log('认证失败，可能是token过期');
      alert('登录已过期，请重新登录');
      localStorage.removeItem('token');
      router.push('/login');
      return;
    }

    if (response.ok) {
      const data = await response.json();
      if (data.status === 'success') {
        userInfo.value = data.user_info;
        console.log('用户信息获取成功:', userInfo.value);
      } else {
        console.error('获取用户信息失败:', data.message);
        alert('获取用户信息失败: ' + data.message);
      }
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('网络错误:', error);
    alert('网络连接失败，请检查网络连接');
  }
}
// 新增的图表相关代码
const chartContainer = ref(null)

// 模拟30天内该车型的租赁数据
const generateChartData = () => {
  const data = []
  for (let i = 1; i <= 30; i++) {
    // 基础值 + 随机波动
    const baseValue = 5 + Math.floor(Math.random() * 5)
    data.push({
      day: i,
      rentals: baseValue + Math.floor(Math.random() * 3)
    })
  }
  return data
}

// 初始化图表
const initChart = () => {
  const chartData = generateChartData()
  
  Highcharts.chart(chartContainer.value, {
    chart: {
      type: 'line',
      height: 250,
      backgroundColor: 'transparent'
    },
    title: {
      text: null
    },
    xAxis: {
      title: {
        text: '天数'
      },
      categories: chartData.map(item => `第${item.day}天`)
    },
    yAxis: {
      title: {
        text: '成交次数'
      },
      min: 0
    },
    legend: {
      enabled: false
    },
    tooltip: {
      formatter: function() {
        return `<b>第${this.x + 1}天</b><br/>成交次数: ${this.y}次`
      }
    },
    series: [{
      name: '租赁次数',
      data: chartData.map(item => item.rentals),
      color: '#4CAF50',
      lineWidth: 2,
      marker: {
        radius: 3
      }
    }],
    plotOptions: {
      series: {
        animation: {
          duration: 1000
        }
      }
    },
    credits: {
      enabled: false
    }
  })
}

// 在组件挂载时初始化图表
onMounted(async () => {
  await fetchUserInfo()
  
  // 如果用户信息不完整，自动进入编辑模式
  if (!hasCompleteInfo.value) {
    startEditPersonalInfo()
  }
  
  initChart()
})

// 保存用户信息的函数
// 个人信息编辑状态
const isEditingPersonalInfo = ref(false)
const editingUserInfo = ref({})

// 检查是否有完整的个人信息
const hasCompleteInfo = computed(() => {
  return userInfo.value.real_name && 
         userInfo.value.phone && 
         userInfo.value.id_number && 
         userInfo.value.email
})

// 开始编辑个人信息
const startEditPersonalInfo = () => {
  // 复制当前用户信息到编辑对象
  editingUserInfo.value = {
    real_name: userInfo.value.real_name || '',
    phone: userInfo.value.phone || '',
    id_number: userInfo.value.id_number || '',
    email: userInfo.value.email || ''
  }
  isEditingPersonalInfo.value = true
}

// 取消编辑个人信息
const cancelEditPersonalInfo = () => {
  isEditingPersonalInfo.value = false
  editingUserInfo.value = {}
}

// 保存用户信息的函数
const saveUserInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('请先登录');
      router.push('/login');
      return;
    }

    const response = await fetch('/api/update_user_info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(editingUserInfo.value)
    });

    if (response.status === 401) {
      alert('登录已过期，请重新登录');
      localStorage.removeItem('token');
      router.push('/login');
      return;
    }

    const result = await response.json();
    if (result.status === 'success') {
      userInfo.value = { ...editingUserInfo.value };
      isEditingPersonalInfo.value = false;
      alert('个人信息保存成功');
    } else {
      alert('保存失败: ' + result.message);
    }
  } catch (error) {
    console.error('保存用户信息失败:', error);
    alert('保存失败，请稍后重试');
  }
}
</script>

<style scoped>
.checkout-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  margin-top: 70px;
}

.page-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.checkout-container {
  display: flex;
  gap: 30px;
}

.car-info-section {
  flex: 0 0 400px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.car-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 20px;
}

.car-details h2 {
  color: #333;
  margin-bottom: 20px;
}

.car-specs {
  display: grid;
  gap: 15px;
}

.spec-item {
  display: flex;
  gap: 10px;
}

.spec-item .label {
  color: #666;
}

.order-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pickup-return-info,
.insurance-options,
.price-summary,
.payment-methods {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.location-time h3 {
  margin-bottom: 20px;
}

.location-container {
  display: flex;
  gap: 20px;
}

.location-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-start;
  flex: 1;
}

.location-item .info {
    flex: 1;
    margin-right: 40px;
}

.location-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.info .type {
  font-weight: bold;
  margin-bottom: 5px;
}

.info .time {
  color: #666;
  font-size: 0.9em;
  margin-top: 5px;
}

.info .value {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.insurance-item {
  border: 2px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.insurance-item.selected {
  border-color: #fcd057;
  background-color: #fff9e6;
}

.insurance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.insurance-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.recommend-tag {
  background-color: #ff6b00;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.insurance-details {
  color: #666;
  font-size: 0.9em;
}

.detail-item {
  margin: 5px 0;
}

.coupon-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.coupon-section h3 {
  margin-bottom: 15px;
  color: #333;
}

.coupon-select {
  width: 100%;
  padding: 12px;
  border: 2px solid #eee;
  border-radius: 8px;
  font-size: 1em;
  color: #333;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.coupon-select:hover {
  border-color: #fcd057;
}

.coupon-select:focus {
  outline: none;
  border-color: #fcd057;
  box-shadow: 0 0 0 2px rgba(252, 208, 87, 0.2);
}

.price-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.price-item.discount {
  color: #ff6b00;
}

.price-item.total {
  border-top: 1px solid #eee;
  padding-top: 15px;
  font-weight: bold;
  font-size: 1.2em;
}

.payment-options {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.payment-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-option.selected {
  border-color: #fcd057;
  background-color: #fff9e6;
}

.payment-option img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.submit-button {
  width: 100%;
  padding: 15px;
  background-color: #fcd057;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #ffa500;
}

.shield-icon {
  font-size: 20px;
}

.payment-methods h3 {
  margin-bottom: 15px;
  color: #333;
}

.info .value {
  color: #333;
  line-height: 1.4;
}

.personal-info {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.personal-info h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1em;
}
/* 新增的图表样式 */
.rental-trend-chart {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.rental-trend-chart h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.1em;
}
/* 个人信息区域样式 */
.personal-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.personal-info h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

/* 信息显示模式样式 */
.personal-info .info-display .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e9ecef;
}

.personal-info .info-display .info-item:last-child {
  border-bottom: none;
}

.personal-info .info-display .label {
  font-weight: 500;
  color: #495057;
  min-width: 80px;
}

.personal-info .info-display .value {
  color: #6c757d;
  flex: 1;
  text-align: right;
}

/* 完善信息/修改信息按钮样式 */
.edit-info-btn {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  margin-top: 20px;
  width: 100%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.edit-info-btn:hover {
  background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
}

.edit-info-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.3);
}

.edit-info-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.edit-info-btn:hover::before {
  left: 100%;
}

/* 编辑模式表单样式 */
.personal-info .info-edit .form-group {
  margin-bottom: 20px;
}

.personal-info .info-edit .form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.personal-info .info-edit .form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: white;
}

.personal-info .info-edit .form-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  background-color: #f8f9ff;
}

.personal-info .info-edit .form-input:hover {
  border-color: #ced4da;
}

/* 按钮组样式 */
.personal-info .button-group {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}

/* 保存按钮样式 */
.save-info-btn {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  flex: 1;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
  position: relative;
  overflow: hidden;
}

.save-info-btn:hover {
  background: linear-gradient(135deg, #218838 0%, #1e7e34 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.save-info-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3);
}

.save-info-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.save-info-btn:hover::before {
  left: 100%;
}

/* 取消按钮样式 */
.cancel-info-btn {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  flex: 1;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(108, 117, 125, 0.3);
  position: relative;
  overflow: hidden;
}

.cancel-info-btn:hover {
  background: linear-gradient(135deg, #545b62 0%, #343a40 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.4);
}

.cancel-info-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(108, 117, 125, 0.3);
}

.cancel-info-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.cancel-info-btn:hover::before {
  left: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .personal-info .button-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .save-info-btn,
  .cancel-info-btn {
    width: 100%;
  }
  
  .edit-info-btn {
    font-size: 16px;
    padding: 14px 24px;
  }
}

/* 按钮禁用状态 */
.save-info-btn:disabled,
.cancel-info-btn:disabled,
.edit-info-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.save-info-btn:disabled:hover,
.cancel-info-btn:disabled:hover,
.edit-info-btn:disabled:hover {
  transform: none;
  box-shadow: none;
}
</style>
