<!-- CarShowcase.vue -->
<template>
  <div class="car-showcase">
    <header class="showcase-header">
      <p>探索我们的精选车型，找到适合您的完美选择。</p>
      <div class="search-bar-container">
        <input type="text" v-model="searchQuery" @keyup.enter="performSearch" placeholder="搜索车型，如：本田、SUV..." class="search-input">
        <button @click="performSearch" class="search-button">搜索</button>
      </div>
    </header>
    <main>
      <div class="content-wrapper">
        <!-- Left Filter Bar -->
        <aside class="filter-bar">
          <h3>筛选条件</h3>
          <div class="filter-section">
            <label>价格区间</label>
            <input type="range" min="0" max="1000" />
          </div>
          <div class="filter-section">
            <label>车辆品牌</label>
            <ul>
              <li><input type="checkbox" id="brand-vw" /> 大众</li>
              <li><input type="checkbox" id="brand-toyota" /> 丰田</li>
              <li><input type="checkbox" id="brand-honda" /> 本田</li>
              <li><input type="checkbox" id="brand-nissan" /> 日产</li>
              <li><input type="checkbox" id="brand-buick" /> 别克</li>
              <li><input type="checkbox" id="brand-hyundai" /> 现代</li>
            </ul>
          </div>
          <div class="filter-section">
            <label>车型类别</label>
            <ul>
              <li><input type="radio" name="type" id="type-economic" /> 经济型</li>
              <li><input type="radio" name="type" id="type-comfort" /> 舒适型</li>
              <li><input type="radio" name="type" id="type-luxury" /> 豪华型</li>
              <li><input type="radio" name="type" id="type-suv" /> SUV</li>
              <li><input type="radio" name="type" id="type-business" /> 商务车</li>
            </ul>
          </div>
          <div class="filter-section">
            <label>变速箱类型</label>
            <ul>
              <li><input type="radio" name="gearbox" id="gear-auto" /> 自动</li>
              <li><input type="radio" name="gearbox" id="gear-manual" /> 手动</li>
            </ul>
          </div>
        </aside>
        <!-- Main Car Showcase -->
        <div class="showcase-grid">
          <div 
            v-for="(car, index) in cars" 
            :key="index" 
            class="car-item"
          >
            <img :src="car.image" :alt="car.name" class="car-image" />
            <div class="car-info">
              <h2>{{ car.name }}</h2>
              <div class="car-features">
                <span>
                  <img 
                    :src="getIconUrl('number-of-seats.png')" 
                    alt="座位数"
                    class="feature-icon"
                  />
                  {{ car.seats }}座
                </span>
                <span>
                  <img 
                    :src="getIconUrl('energy-type.png')" 
                    alt="燃料类型"
                    class="feature-icon"
                  />
                  {{ car.fuelType }}
                </span>
                <span>
                  <img 
                    :src="getIconUrl('gearbox-type.png')" 
                    alt="变速箱类型"
                    class="feature-icon"
                  />
                  {{ car.transmission }}
                </span>
              </div>
              <div class="price-action-row">
                <div class="car-price">
                  <span class="price-symbol">¥</span>
                  <span class="price-amount">{{ car.price }}</span>
                  <span class="price-period">/天</span>
                </div>
                <button class="book-button" @click="handleCarClick(car)">
                  立即预订
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const originalCars = ref([]) // 保存原始车辆数据用于重置或无搜索时显示
const cars = ref([]) // 用于展示的车辆数据，会根据搜索结果更新

const getIconUrl = (iconName) => {
  return new URL(`../assets/images/icons/${iconName}`, import.meta.url).href
}

// 初始化时从Elasticsearch获取所有车辆数据
onMounted(async () => {
  try {
    // 从后端API获取所有车辆数据
    const response = await fetch('http://localhost:5000/api/search_cars?q=');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const allCars = await response.json();
    
    // 处理车辆数据，统一图片URL格式
     const processedCars = allCars.map(mapCarData);
    
    originalCars.value = [...processedCars];
    cars.value = [...processedCars];
  } catch (error) {
    console.error('Failed to load cars from Elasticsearch:', error);
    // 如果加载失败，显示空数组
    originalCars.value = [];
    cars.value = [];
  }
});

// 提取图片处理逻辑为独立函数
const processCarImageUrl = (car_from_es) => {
  let finalImageUrl;
  
  if (car_from_es.image_url) {
    if (car_from_es.image_url.startsWith('http')) {
      // 如果是完整的HTTP URL（MinIO公共URL），直接使用
      finalImageUrl = car_from_es.image_url;
    } else if (car_from_es.image_url.startsWith('cars/')) {
      // 如果是MinIO对象名称，构建MinIO访问URL
      finalImageUrl = `http://localhost:9000/car-images/${car_from_es.image_url}`;
    } else {
      // 如果是本地路径，提取文件名并构建本地URL
      const imageName = car_from_es.image_url.split('/').pop();
      finalImageUrl = new URL(`../assets/images/${imageName}`, import.meta.url).href;
    }
  } else {
    // 使用默认图片
    finalImageUrl = new URL(`../assets/images/car_404.png`, import.meta.url).href;
  }
  
  return finalImageUrl;
};

// 将ES数据转换为前端显示格式
const mapCarData = (car_from_es) => {
  return {
    id: car_from_es.id,
    name: car_from_es.name,
    image: processCarImageUrl(car_from_es),
    seats: car_from_es.seats,
    fuelType: car_from_es.fuel_type,
    transmission: car_from_es.transmission,
    price: car_from_es.price_per_day
  };
};

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    cars.value = [...originalCars.value]; // 如果搜索词为空，显示所有车辆
    return;
  }
  
  try {
    const response = await fetch(`http://localhost:5000/api/search_cars?q=${encodeURIComponent(searchQuery.value)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const searchResults = await response.json();
    
    // 将搜索结果转换为前端显示格式
    cars.value = searchResults.map(mapCarData);
  } catch (error) {
    console.error('Search failed:', error);
    // 搜索失败时保持当前显示
  }
};

const handleCarClick = (car) => {
  router.push({
    name: 'checkout',
    params: { id: car.id },
    query: {
      name: car.name,
      price: car.price,
      seats: car.seats,
      fuelType: car.fuelType,
      transmission: car.transmission,
      image: car.image
    }
  })
}
</script>

<style scoped>
.car-showcase {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  margin-top: 70px;
}

.showcase-header {
  text-align: center;
  margin-bottom: 40px;
}

.showcase-header p {
  font-size: 1.2rem;
  color: #555;
  margin-bottom: 20px; /* 为搜索框腾出空间 */
}

.search-bar-container {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.search-input {
  padding: 10px 15px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px 0 0 4px;
  width: 300px;
  outline: none;
}

.search-input:focus {
  border-color: #007bff;
}

.search-button {
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background-color: #007bff;
  border: 1px solid #007bff;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  outline: none;
}

.search-button:hover {
  background-color: #0056b3;
}

.content-wrapper {
  display: flex;
  gap: 20px;
}

.filter-bar {
  width: 250px;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.filter-bar h3 {
  font-size: 1.5rem;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section label {
  font-size: 1rem;
  display: block;
  margin-bottom: 10px;
}

.filter-section ul {
  list-style: none;
  padding: 0;
}

.filter-section li {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  flex: 1;
}

.car-item {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.car-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.car-info {
  padding: 16px;
}

.car-info h2 {
  font-size: 1.4rem;
  margin: 0 0 12px 0;
  color: #333;
}

.car-features {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.car-features span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 0.9rem;
}

.feature-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.price-action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.car-price {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.price-symbol {
  font-size: 1rem;
  color: #ff6b00;
}

.price-amount {
  font-size: 1.8rem;
  font-weight: bold;
  color: #ff6b00;
}

.price-period {
  color: #666;
  font-size: 0.9rem;
}

.book-button {
  padding: 8px 24px;
  background-color: #fcd057;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  width: auto;
}

.book-button:hover {
  background-color: #ffa500;
}
</style>