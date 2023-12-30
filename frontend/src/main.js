import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import VueCookies from "vue-cookies";



import './assets/main.css'
import "../src/tailwind.css";


const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueCookies, { expires: '5d' });


app.mount('#app')
