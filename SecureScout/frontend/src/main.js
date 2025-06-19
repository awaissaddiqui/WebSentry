import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import en from 'element-plus/es/locale/lang/en'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './assets/main.css'
// Tailwind CSS styles are processed directly via PostCSS
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Register Pinia
app.use(createPinia())

// Register route
app.use(router)

// Register for Element Plus
app.use(ElementPlus, {
  locale: en
})

// Mount application
app.mount('#app') 