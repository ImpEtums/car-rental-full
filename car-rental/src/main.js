// car-rental/src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js'; // 保持您的路径不变
import VueAMap, {initAMapApiLoader} from '@vuemap/vue-amap';
import '@vuemap/vue-amap/dist/style.css';
import naive from 'naive-ui';
import ElementPlus from 'element-plus'; // 确保这个导入是正确的
import 'element-plus/dist/index.css'; // 【推荐】通常 Element Plus 也需要导入 CSS

// 【新增】从 axios.js 导入两个服务实例
import { flaskApiService, nodeApiService } from './axios';

const app = createApp(App);

// 【新增】将两个 axios 实例挂载到全局属性
app.config.globalProperties.$flaskApi = flaskApiService;
app.config.globalProperties.$nodeApi = nodeApiService;


app
  .use(router)
  .use(naive)
  .use(VueAMap)
  .use(ElementPlus) // 您的 ElementPlus 使用
  .mount('#app');

// 如果您在使用 VueAMap 时需要手动初始化，通常会在这里调用
// initAMapApiLoader({
//   key: '您的高德地图Key', // 替换为您的实际高德地图Key
//   securityJsCode: '您的安全密钥', // 替换为您的安全密钥
// });