import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { VueFlow } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/minimap/dist/style.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

// 注册 Vue Flow 组件
app.component('VueFlow', VueFlow)
app.component('MiniMap', MiniMap)

app.mount('#app') 