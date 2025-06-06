<template>
  <div class="car-show-3d">
    <canvas ref="canvas" />
    <div class="loading" v-if="loading">加载中...</div>
    <div class="controls">
      <button @click="switchCar" :disabled="loading">
        切换车辆 ({{ currentCarIndex + 1 }}/{{ carModels.length }})
      </button>
      <div class="car-name">{{ currentCarName }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const canvas = ref(null);
const loading = ref(true);
const currentCarIndex = ref(0);
const currentCarName = ref('2018 BMW M5');

const carModels = [
  {
    path: '/models/2018-bmw-m5/source/2018_bmw_m5.glb',
    name: '2018 BMW M5'
  },
  {
    path: '/models/2013-chevrolet-corvette-z06/source/2013_chevrolet_corvette_z06.glb',
    name: '2013 Chevrolet Corvette Z06'
  },
  {
    path: '/models/2018-porsche-718-cayman-gts/source/2018_porsche_718_cayman_gts.glb',
    name: '2018 Porsche 718 Cayman GTS'
  }
];

let scene, camera, renderer, controls;
let currentModel = null;
let animationFrameId;

const init = () => {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x222222);

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(5, 3, 5);

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: canvas.value,
    antialias: true
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // 添加轨道控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 3;
  controls.maxDistance = 10;

  // 添加环境光和平行光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(5, 5, 5);
  directionalLight.castShadow = true;
  scene.add(directionalLight);

  // 添加地面
  const groundGeometry = new THREE.PlaneGeometry(10, 10);
  const groundMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x333333,
    roughness: 0.8,
    metalness: 0.2
  });
  const ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // 加载初始模型
  loadCarModel(carModels[currentCarIndex.value]);

  // 处理窗口大小变化
  window.addEventListener('resize', onWindowResize);
};

const loadCarModel = (carModel) => {
  loading.value = true;
  currentCarName.value = carModel.name;

  const loader = new GLTFLoader();
  loader.load(
    carModel.path,
    (gltf) => {
      if (currentModel) {
        scene.remove(currentModel);
      }

      const model = gltf.scene;
      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
      
      // 调整模型大小和位置
      model.scale.set(250, 250, 250);
      model.position.set(0, 0, 0);
      
      scene.add(model);
      currentModel = model;
      loading.value = false;
    },
    (progress) => {
      console.log('Loading progress:', (progress.loaded / progress.total) * 100 + '%');
    },
    (error) => {
      console.error('Error loading model:', error);
      loading.value = false;
    }
  );
};

const switchCar = () => {
  currentCarIndex.value = (currentCarIndex.value + 1) % carModels.length;
  loadCarModel(carModels[currentCarIndex.value]);
};

const animate = () => {
  animationFrameId = requestAnimationFrame(animate);
  
  if (controls) {
    controls.update();
  }
  
  renderer.render(scene, camera);
};

const onWindowResize = () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
};

onMounted(() => {
  init();
  animate();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize);
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  if (renderer) {
    renderer.dispose();
  }
  if (controls) {
    controls.dispose();
  }
});
</script>

<style scoped>
.car-show-3d {
  position: fixed;
  top: 56px;
  left: 0;
  width: 100%;
  height: calc(100vh - 56px);
  overflow: hidden;
}

canvas {
  display: block;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 24px;
  background: rgba(0, 0, 0, 0.7);
  padding: 20px 40px;
  border-radius: 8px;
}

.controls {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.controls button {
  background-color: #ffbb00;
  color: black;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.controls button:hover {
  background-color: #e69603;
  color: white;
}

.controls button:disabled {
  background-color: #666;
  cursor: not-allowed;
}

.car-name {
  color: white;
  font-size: 18px;
  background: rgba(0, 0, 0, 0.7);
  padding: 8px 16px;
  border-radius: 4px;
}
</style>