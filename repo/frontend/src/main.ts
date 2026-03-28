import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createDiscreteApi } from 'naive-ui'

import App from './App.vue'
import router from './router'
import './styles/tokens.css'
import './styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const { message, notification, dialog, loadingBar } = createDiscreteApi(['message', 'notification', 'dialog', 'loadingBar'])

app.provide('message', message)
app.provide('notification', notification)
app.provide('dialog', dialog)
app.provide('loadingBar', loadingBar)

app.mount('#app')
