window.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;

import { createApp, ref } from 'vue';
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import installFFmpeg from '@/plugins/installFFmpeg'; // ffmpeg 集成
import * as ElementPlusIconsVue from '@element-plus/icons-vue';

const loadingVisible = ref(false);
const app = createApp(App);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}
app.config.globalProperties.$ElLoading = {
    visible: loadingVisible
};
app.use(router);
app.use(ElementPlus);
app.mount('#app');
app.use(installFFmpeg);