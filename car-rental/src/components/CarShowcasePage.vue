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

// 初始化时，将静态数据赋值给 originalCars 和 cars
onMounted(() => {
  // 模拟从API获取或直接使用静态数据
  const staticCars = [
    {
      id: 1,
      name: '本田雅阁',
      image: new URL(`../assets/images/car1.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 358
    },
    {
      id: 2,
      name: '本田思域',
      image: new URL(`../assets/images/car2.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 328
    },
    {
      id: 3,
      name: '丰田凯美瑞',
      image: new URL(`../assets/images/car3.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 368
    },
    {
      id: 4,
      name: '大众帕萨特',
      image: new URL(`../assets/images/car4.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 348
    },
    {
      id: 5,
      name: '现代索纳塔',
      image: new URL(`../assets/images/car5.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 338
    },
    {
      id: 6,
      name: '夺命双头车',
      image: new URL(`../assets/images/car6.png`, import.meta.url).href,
      seats: 5,
      fuelType: '汽油',
      transmission: '自动',
      price: 114514
    },
  ];
  originalCars.value = [...staticCars];
  cars.value = [...staticCars];
});

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    cars.value = [...originalCars.value]; // 如果搜索词为空，显示所有车辆
    return;
  }
  
    // 注意：这里的URL需要根据你的实际后端API地址进行调整
    const response = await fetch(`http://localhost:5000/api/search_cars?q=${encodeURIComponent(searchQuery.value)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const searchResults = await response.json();
    console.log('Raw search results from ES:', searchResults); // 新增日志
    // 将搜索结果更新到 cars ref
    // ES 返回的数据结构可能与前端静态数据结构略有不同，需要适配
    cars.value = searchResults.map(car_from_es => {
      console.log('Processing car_from_es:', car_from_es); // 新增日志
      console.log('car_from_es.image_url:', car_from_es.image_url); // 新增日志
      const imageName = car_from_es.image_url ? car_from_es.image_url.split('/').pop() : 'default.png'; // 处理 image_url 可能为空的情况
      console.log('Extracted image name:', imageName); // 新增日志
      const finalImageUrl = new URL(`../assets/images/${imageName}`, import.meta.url).href;
      console.log('Final image URL for template:', finalImageUrl); // 新增日志
      return {
        id: car_from_es.id,
        name: car_from_es.name,
        image: finalImageUrl,
        seats: car_from_es.seats,
        fuelType: car_from_es.fuel_type,
        transmission: car_from_es.transmission,
        price: car_from_es.price_per_day
      };
    });
    console.log('Mapped cars for display:', cars.value); // 新增日志
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