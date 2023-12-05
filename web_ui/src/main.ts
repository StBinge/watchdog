import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import'normalize.css/normalize.css'

document.addEventListener('resume',()=>location.reload())
createApp(App).mount('#app')
