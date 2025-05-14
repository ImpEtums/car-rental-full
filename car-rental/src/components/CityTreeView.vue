<template>
  <div class="page-container">
    <nav class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span class="separator">/</span>
      <span>城市树状图</span>
    </nav>

    <div class="tree-container">
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else class="tree-view">
        <!-- 省级列表 -->
        <div class="level-column">
          <div class="level-title">省份</div>
          <div class="nodes-container">
            <div
              v-for="province in treeData"
              :key="province.code"
              class="tree-node"
              :class="{ active: selectedProvince === province }"
              @click="selectProvince(province)"
            >
              <span class="node-name">{{ province.name }}</span>
              <span class="node-count">({{ province.cities.length }})</span>
            </div>
          </div>
        </div>

        <!-- 市级列表 -->
        <div v-if="selectedProvince" class="level-column">
          <div class="connector-line"></div>
          <div class="level-title">城市</div>
          <div class="nodes-container">
            <div
              v-for="city in selectedProvince.cities"
              :key="city.code"
              class="tree-node"
              :class="{ active: selectedCity === city }"
              @click="selectCity(city)"
            >
              <span class="node-name">{{ city.name }}</span>
              <span class="node-count">({{ city.districts.length }})</span>
            </div>
          </div>
        </div>

        <!-- 区级列表 -->
        <div v-if="selectedCity" class="level-column">
          <div class="connector-line"></div>
          <div class="level-title">区县</div>
          <div class="nodes-container">
            <div
              v-for="district in selectedCity.districts"
              :key="district.code"
              class="tree-node"
            >
              <span class="node-name">{{ district.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'CityTreeView',
  setup() {
    const treeData = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const selectedProvince = ref(null);
    const selectedCity = ref(null);

    const selectProvince = (province) => {
      if (selectedProvince.value === province) {
        selectedProvince.value = null;
        selectedCity.value = null;
      } else {
        selectedProvince.value = province;
        selectedCity.value = null;
      }
    };

    const selectCity = (city) => {
      if (selectedCity.value === city) {
        selectedCity.value = null;
      } else {
        selectedCity.value = city;
      }
    };

    const fetchData = async () => {
      try {
        loading.value = true;
        error.value = null;
        const response = await fetch('http://localhost:5000/api/city-tree', {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        
        const data = await response.json();
        treeData.value = data;
      } catch (err) {
        error.value = '数据加载失败，请稍后重试';
        console.error('Error fetching city tree data:', err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchData();
    });

    return {
      treeData,
      loading,
      error,
      selectedProvince,
      selectedCity,
      selectProvince,
      selectCity
    };
  }
};
</script>

<style scoped>
.page-container {
  padding: 20px;
  max-width: 1200px;
  margin: 60px auto 0;
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 14px;
}

.breadcrumb a {
  color: #ffbb00;
  text-decoration: none;
}

.breadcrumb .separator {
  margin: 0 8px;
  color: #666;
}

.tree-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow-x: auto;
}

.tree-view {
  display: flex;
  gap: 40px;
  padding: 20px;
  min-height: 400px;
  position: relative;
}

.level-column {
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  animation: slideIn 0.3s ease-out;
}

.connector-line {
  position: absolute;
  left: -40px;
  top: 50%;
  width: 40px;
  height: 2px;
  background-color: #ddd;
}

.connector-line::before {
  content: '';
  position: absolute;
  left: 0;
  top: -10px;
  height: 20px;
  width: 2px;
  background-color: #ddd;
}

.level-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 10px;
}

.nodes-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tree-node {
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
  border: 1px solid #ddd;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.tree-node:hover {
  background-color: #e8e8e8;
}

.tree-node.active {
  background-color: #ffbb00;
  color: white;
  border-color: #ffbb00;
}

.tree-node.active .node-count {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.node-name {
  font-size: 14px;
}

.node-count {
  font-size: 12px;
  color: #666;
  background-color: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  color: #ff4444;
  text-align: center;
  padding: 20px;
  background-color: #fff5f5;
  border-radius: 4px;
  margin-bottom: 20px;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .tree-container {
    padding: 10px;
  }
  
  .tree-view {
    gap: 20px;
    padding: 10px;
  }
  
  .level-column {
    min-width: 200px;
  }

  .connector-line {
    left: -20px;
    width: 20px;
  }
}
</style>