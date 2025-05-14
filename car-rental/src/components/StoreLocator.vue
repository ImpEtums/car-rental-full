<template>
  <section class="store-locator">
    <h2 class="section-title">营业网点</h2>
    <p class="section-desc">全国3500+服务网点为您提供安全出行服务</p>
    
    <div class="map-container">
      <el-amap 
        ref="map" 
        :center="mapCenter"
        :zoom="12"
        :amap-manager="amapManager"
        class="amap-box"
      >
        <el-amap-marker
          v-for="marker in markers"
          :key="marker.id"
          :position="marker.position"
          :label="{ 
            content: marker.name,
            direction: 'top'
          }"
        >
        </el-amap-marker>
      </el-amap>
    </div>

    <div class="store-info">
      <div class="store-type">
        <span class="type-item">
          <i class="dot blue"></i>
          自助点
        </span>
        <span class="type-item">
          <i class="dot orange"></i>
          服务点
        </span>
      </div>
    </div>
  </section>
</template>

<script>
import { AMapManager } from '@vuemap/vue-amap';

const amapManager = new AMapManager();

export default {
  name: 'StoreLocator',
  data() {
    return {
      amapManager,
      mapCenter: [120.015721, 30.291308], // 默认中心点
      markers: [
        {
          id: 1,
          position: [120.015721, 30.291308],
          name: '杭州师范大学营业点',
          type: 'service' // service 或 self
        }
      ]
    }
  }
}
</script>

<style scoped>
.store-locator {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 24px;
  text-align: center;
  margin-bottom: 10px;
}

.section-desc {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.map-container {
  width: 100%;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.amap-box {
  width: 100%;
  height: 100%;
}

.store-info {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.store-type {
  display: flex;
  gap: 20px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.blue {
  background-color: #409EFF;
}

.dot.orange {
  background-color: #FF9900;
}
</style>
