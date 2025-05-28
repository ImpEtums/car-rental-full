<template>
  <div class="car-management">
    <header class="management-header">
      <h1>车辆管理</h1>
      <p>管理车辆信息和图片</p>
    </header>
    
    <div class="management-content">
      <!-- 车辆列表 -->
      <div class="car-list-section">
        <h2>车辆列表</h2>
        <div class="car-grid">
          <div 
            v-for="car in cars" 
            :key="car.id" 
            class="car-card"
            :class="{ 'selected': selectedCar?.id === car.id }"
            @click="selectCar(car)"
          >
            <div class="car-image-container">
              <img :src="car.image" :alt="car.name" class="car-image" />
              <div class="car-status" :class="car.availability ? 'available' : 'unavailable'">
                {{ car.availability ? '可用' : '不可用' }}
              </div>
            </div>
            <div class="car-info">
              <h3>{{ car.name }}</h3>
              <p class="car-details">{{ car.seats }}座 | {{ car.fuelType }} | {{ car.transmission }}</p>
              <p class="car-price">¥{{ car.price }}/天</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 车辆详情和图片管理 -->
      <div v-if="selectedCar" class="car-details-section">
        <h2>车辆详情</h2>
        <div class="details-content">
          <div class="car-info-panel">
            <h3>{{ selectedCar.name }}</h3>
            <div class="info-grid">
              <div class="info-item">
                <label>车辆ID:</label>
                <span>{{ selectedCar.id }}</span>
              </div>
              <div class="info-item">
                <label>座位数:</label>
                <span>{{ selectedCar.seats }}</span>
              </div>
              <div class="info-item">
                <label>燃料类型:</label>
                <span>{{ selectedCar.fuelType }}</span>
              </div>
              <div class="info-item">
                <label>变速箱:</label>
                <span>{{ selectedCar.transmission }}</span>
              </div>
              <div class="info-item">
                <label>日租金:</label>
                <span>¥{{ selectedCar.price }}</span>
              </div>
              <div class="info-item">
                <label>状态:</label>
                <span :class="selectedCar.availability ? 'status-available' : 'status-unavailable'">
                  {{ selectedCar.availability ? '可用' : '不可用' }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="image-management-panel">
            <h3>图片管理</h3>
            <div class="current-image">
              <h4>当前图片:</h4>
              <img :src="selectedCar.image" :alt="selectedCar.name" class="current-car-image" />
            </div>
            
            <div class="upload-section">
              <h4>上传新图片:</h4>
              <ImageUpload 
                :car-id="selectedCar.id" 
                :initial-image="selectedCar.image"
                @upload-success="handleUploadSuccess"
                @upload-error="handleUploadError"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- 操作结果提示 -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import ImageUpload from './ImageUpload.vue'

const cars = ref([])
const selectedCar = ref(null)
const message = ref('')
const messageType = ref('success')

const selectCar = (car) => {
  selectedCar.value = car
}

const loadCars = async () => {
  try {
    // 获取所有车辆数据（通过搜索空字符串获取所有结果）
    const response = await axios.get('/api/search_cars?q=*')
    
    if (Array.isArray(response.data)) {
      cars.value = response.data.map(car => ({
        id: car.id,
        name: car.name,
        image: car.image_url || '/assets/images/car_404.png',
        seats: car.seats || 5,
        fuelType: car.fuel_type || '汽油',
        transmission: car.transmission || '自动',
        price: car.price_per_day || 300,
        availability: car.availability !== false
      }))
    } else {
      console.error('Unexpected response format:', response.data)
      cars.value = []
    }
  } catch (error) {
    console.error('加载车辆数据失败:', error)
    showMessage('加载车辆数据失败', 'error')
    cars.value = []
  }
}

const handleUploadSuccess = (uploadData) => {
  showMessage('图片上传成功！', 'success')
  
  // 更新选中车辆的图片
  if (selectedCar.value) {
    selectedCar.value.image = uploadData.fileUrl
    
    // 更新车辆列表中对应的车辆
    const carIndex = cars.value.findIndex(car => car.id === selectedCar.value.id)
    if (carIndex !== -1) {
      cars.value[carIndex].image = uploadData.fileUrl
    }
  }
  
  // 重新加载车辆数据以确保同步
  setTimeout(() => {
    loadCars()
  }, 1000)
}

const handleUploadError = (error) => {
  showMessage(`图片上传失败: ${error}`, 'error')
}

const showMessage = (text, type = 'success') => {
  message.value = text
  messageType.value = type
  
  // 3秒后自动清除消息
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

onMounted(() => {
  loadCars()
})
</script>

<style scoped>
.car-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.management-header {
  text-align: center;
  margin-bottom: 30px;
}

.management-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.management-header p {
  color: #666;
  font-size: 16px;
}

.management-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.car-list-section h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.car-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.car-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.car-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.car-card.selected {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.car-image-container {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.car-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.car-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.car-status.available {
  background-color: #28a745;
  color: white;
}

.car-status.unavailable {
  background-color: #dc3545;
  color: white;
}

.car-info {
  padding: 15px;
}

.car-info h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.car-details {
  color: #666;
  font-size: 14px;
  margin: 0 0 8px 0;
}

.car-price {
  color: #007bff;
  font-weight: bold;
  font-size: 16px;
  margin: 0;
}

.car-details-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.car-details-section h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.details-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.car-info-panel h3 {
  color: #333;
  margin-bottom: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.info-item label {
  font-weight: bold;
  color: #555;
}

.status-available {
  color: #28a745;
  font-weight: bold;
}

.status-unavailable {
  color: #dc3545;
  font-weight: bold;
}

.image-management-panel h3 {
  color: #333;
  margin-bottom: 15px;
}

.current-image h4 {
  color: #555;
  margin-bottom: 10px;
}

.current-car-image {
  width: 100%;
  max-width: 300px;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.upload-section {
  margin-top: 20px;
}

.upload-section h4 {
  color: #555;
  margin-bottom: 10px;
}

.message {
  padding: 12px 16px;
  border-radius: 4px;
  margin-top: 20px;
  font-weight: bold;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .details-content {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .car-grid {
    grid-template-columns: 1fr;
  }
}
</style>