import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';
import VueAMap, {initAMapApiLoader} from '@vuemap/vue-amap';
import '@vuemap/vue-amap/dist/style.css';
import naive from 'naive-ui';



createApp(App)
  .use(router)
  .use(naive)
  .use(VueAMap)
  .mount('#app');
