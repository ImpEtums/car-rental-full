import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import VueAMap, {initAMapApiLoader} from '@vuemap/vue-amap';
import '@vuemap/vue-amap/dist/style.css';
import naive from 'naive-ui';
// 加了一个引入element-plus
import ElementPlus from 'element-plus'


//加了一个.use(ElementPlus)
createApp(App)
  .use(router)
  .use(naive)
  .use(VueAMap)
  .use(ElementPlus)
  .mount('#app');
