<template>
  <div class="store-search">
    <!-- 搜索框 -->
    <div class="search-box">
      <n-input
        v-model:value="searchKeyword"
        placeholder="请输入网点名称或地址"
        @keyup.enter="searchKeyWord"
      >
        <template #suffix>
          <n-button @click="searchKeyWord">
            搜索
          </n-button>
        </template>
      </n-input>
    </div>

    <!-- 搜索结果列表 -->
    <div class="search-result" v-if="showSearchResult">
      <ul>
        <li v-for="(item, index) in poiList" 
            :key="index"
            @click="markerResult(item)">
          {{ item.name }}
        </li>
      </ul>
    </div>

    <div class="content-wrapper">
      <!-- 左侧网点列表 -->
      <div class="store-list">
        <div class="section-title">
          <span class="title">网点列表</span>
          <span class="count">{{ stores.length }} 家网点</span>
        </div>
        
        <div class="stores">
          <div v-for="store in stores" 
               :key="store.store_id" 
               class="store-item"
               :class="{ active: selectedStore?.store_id === store.store_id }"
               @click="selectStore(store)">
            <h3>{{ store.store_name }}</h3>
            <p class="address">
              <i class="location-icon">📍</i>
              {{ store.address }}
            </p>
            <p class="business-hours">
              <i class="time-icon">🕒</i>
              营业时间：{{ store.business_hours }}
            </p>
            <p class="phone">
              <i class="phone-icon">📞</i>
              {{ store.phone }}
            </p>
          </div>
        </div>
      </div>

      <!-- 右侧地图容器 -->
      <div id="container" class="map-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { NInput, NButton } from 'naive-ui'
import AMapLoader from '@amap/amap-jsapi-loader'
import axiosInstance from '@/axios'

const searchKeyword = ref('')
const stores = ref([
  {
    store_id: 1,
    store_name: '杭州武林门店',
    address: '杭州市西湖区武林路28号',
    phone: '0571-12345678',
    business_hours: '09:00-18:00',
    longitude: 120.169324,
    latitude: 30.279468
  },
  {
    store_id: 2,
    store_name: '杭州西湖店',
    address: '杭州市西湖区西湖文化广场',
    phone: '0571-87654321',
    business_hours: '09:00-18:00',
    longitude: 120.152832,
    latitude: 30.242841
  },
  {
    store_id: 3,
    store_name: '杭州滨江店',
    address: '杭州市滨江区滨盛路1号',
    phone: '0571-98765432',
    business_hours: '09:00-18:00',
    longitude: 120.211544,
    latitude: 30.208699
  }
])
const selectedStore = ref(null)
const map = ref(null)
const geocoder = ref(null)
const placeSearch = ref(null)
const showSearchResult = ref(false)
const poiList = ref([])
const address = ref('')

// 选择网点并在地图上显示
const selectStore = (store) => {
  selectedStore.value = store
  if (map.value) {
    // 清除之前的标记
    map.value.clearMap()
    
    // 创建新标记
    const marker = new window.AMap.Marker({
      position: [store.longitude, store.latitude],
      title: store.store_name
    })
    
    // 创建信息窗体
    const infoWindow = new window.AMap.InfoWindow({
      content: `
        <div class="info-window">
          <h4>${store.store_name}</h4>
          <p>地址：${store.address}</p>
          <p>营业时间：${store.business_hours}</p>
          <p>电话：${store.phone}</p>
        </div>
      `,
      offset: new window.AMap.Pixel(0, -30)
    })

    // 点击标记时显示信息窗体
    marker.on('click', () => {
      infoWindow.open(map.value, marker.getPosition())
    })

    // 添加标记到地图
    map.value.add(marker)
    
    // 打开信息窗体
    infoWindow.open(map.value, marker.getPosition())
    
    // 设置地图中心点和缩放级别
    map.value.setZoomAndCenter(15, [store.longitude, store.latitude])
  }
}

// 初始化地图时添加所有网点标记
const addAllMarkers = () => {
  if (!map.value) return
  
  map.value.clearMap()
  
  stores.value.forEach(store => {
    const marker = new window.AMap.Marker({
      position: [store.longitude, store.latitude],
      title: store.store_name
    })
    
    const infoWindow = new window.AMap.InfoWindow({
      content: `
        <div class="info-window">
          <h4>${store.store_name}</h4>
          <p>地址：${store.address}</p>
          <p>营业时间：${store.business_hours}</p>
          <p>电话：${store.phone}</p>
        </div>
      `,
      offset: new window.AMap.Pixel(0, -30)
    })

    marker.on('click', () => {
      infoWindow.open(map.value, marker.getPosition())
      selectStore(store)
    })

    map.value.add(marker)
  })
}

// 修改初始化地图函数
const initMap = async () => {
  try {
    window._AMapSecurityConfig = {
      securityJsCode: '0c274f761db40f11426101fe0d5f3c8b'
    }

    const AMap = await AMapLoader.load({
      key: '3bae549ce0395393fa08ef0d3292bb3f',
      version: '2.0',
      plugins: ['AMap.ToolBar', 'AMap.Scale']
    })

    map.value = new AMap.Map('container', {
      viewMode: '2D',
      zoom: 12,
      center: [120.169324, 30.279468], // 杭州市中心
      resizeEnable: true
    })

    map.value.addControl(new AMap.ToolBar())
    map.value.addControl(new AMap.Scale())

    // 添加所有网点标记
    addAllMarkers()

    console.log('地图初始化成功')
  } catch (error) {
    console.error('地图初始化失败:', error)
  }
}

// 获取当前位置
const getCurrentLocation = (AMap) => {
  const geolocation = new AMap.Geolocation({
    timeout: 10000,
    zoomToAccuracy: true
  })

  geolocation.getCurrentPosition((status, result) => {
    if (status === 'complete') {
      const lnglat = result.position
      addMarker(lnglat)
      getAddress(lnglat)
    } else {
      console.error('定位失败')
    }
  })
}

// 添加标记
const addMarker = (position) => {
  map.value.clearMap()
  const marker = new AMap.Marker({
    position: new AMap.LngLat(position[0], position[1])
  })
  map.value.add(marker)
  showInfoWindow(marker)
}

// 显示信息窗体
const showInfoWindow = (marker) => {
  const infoWindow = new AMap.InfoWindow({
    isCustom: true,
    content: `<div class="info-window">地址：${address.value}</div>`,
    offset: new AMap.Pixel(0, -30)
  })
  infoWindow.open(map.value, marker.getPosition())
}

// 搜索关键词
const searchKeyWord = () => {
  if (!searchKeyword.value) return
  
  placeSearch.value.search(searchKeyword.value, (status, result) => {
    if (status === 'complete' && result.info === 'OK') {
      showSearchResult.value = true
      poiList.value = result.poiList.pois
    } else {
      showSearchResult.value = false
      poiList.value = []
    }
  })
}

// 选择搜索结果
const markerResult = (data) => {
  showSearchResult.value = false
  address.value = data.name
  const position = [Number(data.location.lng), Number(data.location.lat)]
  addMarker(position)
  map.value.setCenter(position)
  map.value.setZoom(15)
}

// 获取地址信息
const getAddress = (lnglat) => {
  geocoder.value.getAddress(lnglat, (status, result) => {
    if (status === 'complete' && result.regeocode) {
      address.value = result.regeocode.formattedAddress
    }
  })
}

onMounted(async () => {
  await initMap()
  handleLoad(null)
})
</script>

<style scoped>
.store-search {
  padding: 20px;
  margin-top: 56px;
}

.search-box {
  margin-bottom: 20px;
  max-width: 500px;
  margin: 0 auto 20px;
}

.search-result {
  position: absolute;
  top: 120px;
  left: 50%;
  transform: translateX(-50%);
  width: 500px;
  background: white;
  border: 1px solid #eee;
  border-radius: 4px;
  z-index: 1000;
}

.search-result ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.search-result li {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.search-result li:hover {
  background: #f5f5f5;
}

.content-wrapper {
  display: flex;
  gap: 20px;
  height: calc(100vh - 180px);
}

.store-list {
  flex: 0 0 400px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  overflow-y: auto;
}

.section-title {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.store-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.store-item.active {
  background: #f0f7ff;
  border-left: 4px solid #1890ff;
}

.map-container {
  flex: 1;
  height: 100%;
  border-radius: 4px;
  overflow: hidden;
}

.info-window {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

:deep(.info-window) {
  padding: 10px;
  max-width: 200px;
}

:deep(.info-window h4) {
  margin: 0 0 5px;
  color: #333;
  font-size: 14px;
}

:deep(.info-window p) {
  margin: 5px 0;
  font-size: 12px;
  color: #666;
}
</style>
