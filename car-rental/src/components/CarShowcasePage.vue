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
import { useRouter, useRoute } from 'vue-router'
import { flaskApiService } from '@/axios'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const originalCars = ref([]) // 保存原始车辆数据用于重置或无搜索时显示
const cars = ref([]) // 用于展示的车辆数据，会根据搜索结果更新

// 租车信息
const rentalInfo = {
  pickupLocation: route.query.pickupLocation || '',
  returnLocation: route.query.returnLocation || '',
  pickupDate: route.query.pickupDate || '',
  returnDate: route.query.returnDate || '',
  pickupTime: route.query.pickupTime || '',
  returnTime: route.query.returnTime || '',
  pickupStationId: route.query.pickupStationId || '',
  returnStationId: route.query.returnStationId || '',
  isDifferentLocation: route.query.isDifferentLocation === 'true'
}

// 添加模拟车辆数据作为后备方案
// 更新模拟车辆数据，使用真实的车辆图片
const mockCarData = [
  {
    id: 1,
    name: '大众朗逸 2023款',
    image: new URL('../assets/images/car1.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 150
  },
  {
    id: 2,
    name: '丰田卡罗拉 2023款',
    image: new URL('../assets/images/car2.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 160
  },
  {
    id: 3,
    name: '本田雅阁 2023款',
    image: new URL('../assets/images/car3.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 200
  },
  {
    id: 4,
    name: '日产轩逸 2023款',
    image: new URL('../assets/images/car4.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 140
  },
  {
    id: 5,
    name: '别克英朗 2023款',
    image: new URL('../assets/images/car5.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 170
  },
  {
    id: 6,
    name: '现代伊兰特 2023款',
    image: new URL('../assets/images/car6.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 145
  },
  {
    id: 7,
    name: '大众途观L 2023款',
    image: new URL('../assets/images/car-1.png', import.meta.url).href,
    seats: 7,
    fuelType: '汽油',
    transmission: '自动',
    price: 280
  },
  {
    id: 8,
    name: '丰田汉兰达 2023款',
    image: new URL('../assets/images/car-2.png', import.meta.url).href,
    seats: 7,
    fuelType: '汽油',
    transmission: '自动',
    price: 320
  },
  {
    id: 9,
    name: '奔驰C级 2023款',
    image: new URL('../assets/images/car-3.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 450
  },
  {
    id: 10,
    name: '宝马3系 2023款',
    image: new URL('../assets/images/c1.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 480
  },
  {
    id: 11,
    name: '奥迪A4L 2023款',
    image: new URL('../assets/images/c2.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 460
  },
  {
    id: 12,
    name: '比亚迪秦PLUS DM-i',
    image: new URL('../assets/images/c3.png', import.meta.url).href,
    seats: 5,
    fuelType: '混动',
    transmission: '自动',
    price: 180
  },
  {
    id: 13,
    name: '特斯拉Model 3',
    image: new URL('../assets/images/c4.png', import.meta.url).href,
    seats: 5,
    fuelType: '电动',
    transmission: '自动',
    price: 350
  },
  {
    id: 14,
    name: '凯迪拉克CT5',
    image: new URL('../assets/images/card-1.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 380
  },
  {
    id: 15,
    name: '雷克萨斯ES',
    image: new URL('../assets/images/card-2.png', import.meta.url).href,
    seats: 5,
    fuelType: '汽油',
    transmission: '自动',
    price: 420
  }
];

const getIconUrl = (iconName) => {
  return new URL(`../assets/images/icons/${iconName}`, import.meta.url).href
}

// 初始化时从Elasticsearch获取所有车辆数据
onMounted(async () => {
  try {
    console.log('开始加载车辆数据...');
    // 修复：移除多余的 /api 前缀，因为 flaskApiService 已经配置了 baseURL: '/api'
    const response = await flaskApiService.get('/search_cars?q=');
    console.log('API响应:', response);
    const allCars = response.data;
    
    if (!allCars || allCars.length === 0) {
      console.warn('API没有返回车辆数据，使用模拟数据');
      // 使用模拟数据
      originalCars.value = [...mockCarData];
      cars.value = [...mockCarData];
      console.log('已加载模拟车辆数据，共', cars.value.length, '辆车');
      return;
    }
    
    // 处理车辆数据，统一图片URL格式
    const processedCars = allCars.map(mapCarData);
    console.log('处理后的车辆数据:', processedCars);
    
    originalCars.value = [...processedCars];
    cars.value = [...processedCars];
    console.log('车辆数据加载完成，共', cars.value.length, '辆车');
  } catch (error) {
    console.error('Failed to load cars from Elasticsearch:', error);
    console.error('错误详情:', error.response || error.message);
    // 如果API调用失败，使用模拟数据
    console.log('API调用失败，使用模拟数据');
    originalCars.value = [...mockCarData];
    cars.value = [...mockCarData];
    console.log('已加载模拟车辆数据，共', cars.value.length, '辆车');
  }
});

// 搜索功能
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    // 如果搜索为空，显示所有车辆
    cars.value = [...originalCars.value];
    return;
  }
  
  try {
    // 修复：移除多余的 /api 前缀
    const response = await flaskApiService.get(`/search_cars?q=${encodeURIComponent(searchQuery.value)}`);
    
    // 将搜索结果转换为前端显示格式
    cars.value = response.data.map(mapCarData);
  } catch (error) {
    console.error('搜索失败:', error);
    // 搜索失败时在模拟数据中进行本地搜索
    const query = searchQuery.value.toLowerCase();
    cars.value = mockCarData.filter(car => 
      car.name.toLowerCase().includes(query) ||
      car.fuelType.toLowerCase().includes(query) ||
      car.transmission.toLowerCase().includes(query)
    );
    console.log('使用模拟数据进行本地搜索，找到', cars.value.length, '辆车');
  }
};

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

// 修改 handleCarClick 方法
const handleCarClick = (car) => {
  // 记录车辆浏览
  recordCarView(car.id)
  
  // 导航到结账页面，传递完整的汽车信息
  router.push({
    name: 'checkout',
    params: { id: car.id },
    query: {
      car_id: car.id,
      name: car.name,
      price: car.price,
      seats: car.seats,
      transmission: car.transmission,
      image: car.image  // 关键是传递图片URL
    }
  })
}

// 添加记录浏览的方法
const recordCarView = async (carId) => {
  try {
    await flaskApiService.post('/rankings/car-view', { carId })
    console.log('浏览记录已保存到Redis')
  } catch (error) {
    console.error('记录浏览失败:', error)
  }
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