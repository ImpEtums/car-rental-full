<template>
  <div class="locations-container">
    <h2 class="locations-title">热门租车地点</h2>
    <div class="locations-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="hotLocations.length === 0" class="empty">暂无排行数据</div>
      <div v-else v-for="(location, index) in hotLocations" :key="location.id" class="location-item">
        <div class="rank-badge" :class="{'top-rank': index < 3}">{{ index + 1 }}</div>
        <div class="location-info">
          <div class="location-name">{{ location.name }}</div>
          <div class="location-address">{{ location.address }}</div>
          <div class="rental-count">
            <span class="rental-icon">🚗</span>
            <span>{{ location.rentals }}次租赁</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { flaskApiService } from '../axios'

const hotLocations = ref([])
const loading = ref(true)
const error = ref(null)

// 获取热门租赁地点数据
const fetchHotLocations = async () => {
  try {
    loading.value = true
    const response = await flaskApiService.get('/api/rankings/locations?limit=5')
    hotLocations.value = response.data
    loading.value = false
  } catch (err) {
    console.error('获取热门租赁地点失败:', err)
    error.value = '获取排行榜数据失败'
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchHotLocations()
  // 每60秒刷新一次数据
  const refreshInterval = setInterval(fetchHotLocations, 60000)
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})
</script>

<style scoped>
.locations-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
  max-width: 600px;
}

.locations-title {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
  text-align: center;
}

.location-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rank-badge {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #eee;
  color: #666;
  font-weight: bold;
  margin-right: 15px;
}

.top-rank:nth-child(1) {
  background-color: #ff6b6b;
  color: white;
}

.location-item:nth-child(1) .rank-badge {
  background-color: #ff6b6b;
  color: white;
}

.location-item:nth-child(2) .rank-badge {
  background-color: #ff9e7d;
  color: white;
}

.location-item:nth-child(3) .rank-badge {
  background-color: #ffd082;
  color: white;
}

.location-info {
  flex: 1;
}

.location-name {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 5px;
}

.location-address {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.rental-count {
  display: flex;
  align-items: center;
  color: #888;
  font-size: 0.9rem;
}

.rental-icon {
  margin-right: 5px;
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