import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './components/styles.css'

const app = createApp(App).use(router)
router.isReady().then(() => {
  app.mount('#app')
})
