<template>
  <div class="ranking-container">
    <h2 class="ranking-title">热门车型排行榜</h2>
    <div class="ranking-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="hotCars.length === 0" class="empty">暂无排行数据</div>
      <div v-else v-for="(car, index) in hotCars" :key="car.id" class="ranking-item">
        <div class="ranking-number" :class="{'top-rank': index < 3}">{{ index + 1 }}</div>
        <div class="car-info">
          <img :src="car.image || '/assets/images/car-placeholder.png'" :alt="car.name" class="car-image" />
          <div class="car-details">
            <h3>{{ car.name }}</h3>
            <p class="car-model">{{ car.model || '标准款' }}</p>
            <div class="view-count">
              <span class="view-icon">👁️</span>
              <span>{{ car.views }}次浏览</span>
            </div>
          </div>
        </div>
        <div class="car-price">
          <span class="price-symbol">¥</span>
          <span class="price-amount">{{ car.price }}</span>
          <span class="price-period">/天</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { flaskApiService } from '../axios'

const hotCars = ref([])
const loading = ref(true)
const error = ref(null)

// 获取热门车型数据
const fetchHotCars = async () => {
  try {
    loading.value = true
    const response = await flaskApiService.get('/api/rankings/cars?limit=5')
    hotCars.value = response.data
    loading.value = false
  } catch (err) {
    console.error('获取热门车型失败:', err)
    error.value = '获取排行榜数据失败'
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchHotCars()
  // 每60秒刷新一次数据
  const refreshInterval = setInterval(fetchHotCars, 60000)
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})
</script>

<style scoped>
.ranking-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
  max-width: 600px;
}

.ranking-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
  text-align: center;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #999;
  width: 40px;
  text-align: center;
}

.top-rank:nth-child(1) {
  color: #ff6b6b;
}

.ranking-item:nth-child(1) .ranking-number {
  color: #ff6b6b;
}

.ranking-item:nth-child(2) .ranking-number {
  color: #ff9e7d;
}

.ranking-item:nth-child(3) .ranking-number {
  color: #ffd082;
}

.car-info {
  display: flex;
  flex: 1;
  align-items: center;
}

.car-image {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 15px;
}

.car-details h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
}

.car-model {
  color: #666;
  margin: 0 0 5px 0;
  font-size: 0.9rem;
}

.view-count {
  display: flex;
  align-items: center;
  color: #888;
  font-size: 0.9rem;
}

.view-icon {
  margin-right: 5px;
}

.car-price {
  font-weight: bold;
  color: #ff6b6b;
}

.price-symbol {
  font-size: 0.9rem;
  vertical-align: super;
}

.price-amount {
  font-size: 1.3rem;
}

.price-period {
  font-size: 0.8rem;
  color: #999;
}

.loading, .error, .empty {
  text-align: center;
  padding: 20px;
  color: #999;
}

.error {
  color: #ff6b6b;
}
</style>