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
            <div class="spec-item">
              <span class="label">姓名：</span>
              <span>{{ userInfo.real_name || '未填写' }}</span>
            </div>
            <div class="spec-item">
              <span class="label">手机号：</span>
              <span>{{ userInfo.phone || '未填写' }}</span>
            </div>
            <div class="spec-item">
              <span class="label">身份证号：</span>
              <span>{{ userInfo.id_number || '未填写' }}</span>
            </div>
            <div class="spec-item">
              <span class="label">邮箱：</span>
              <span>{{ userInfo.email || '未填写' }}</span>
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
                <div class="value">浙江省杭州市西湖区武林门店</div>
                <div class="time">2024-12-21 08:00</div>
              </div>
            </div>
            <div class="location-item">
              <img src="../assets/images/icons/location.png" alt="location" class="location-icon" />
              <div class="info">
                <div class="type">还车地点</div>
                <div class="value">浙江省杭州市西湖区西湖风景区店</div>
                <div class="time">2024-12-25 20:00</div>
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
  name: route.query.name || '',
  price: Number(route.query.price) || 0,
  seats: route.query.seats || 5,
  transmission: route.query.transmission || '自动',
  image: route.query.image || ''
})

// 车辆租赁天数
const rentalDays = computed(() => {
  return 3  // 目前写死为3天
})

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

// 提交订单
const handleSubmit = () => {
  router.push('/payment')
}

// 添加用户信息状态
const userInfo = ref({})

// 获取用户信息的函数
const fetchUserInfo = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/get_user_info', {
      credentials: 'include'
    })
    const data = await response.json()
    if (data.status === 'success') {
      userInfo.value = data.user
    } else {
      console.error('获取用户信息失败:', data.message)
    }
  } catch (error) {
    console.error('获取用户信息出错:', error)
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
onMounted(() => {
  fetchUserInfo()
  initChart()
})
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
</style>

