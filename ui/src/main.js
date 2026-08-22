import { createApp } from 'vue'
import App from './App.vue'

// Import styles
import './assets/styles/base.css'
import './assets/styles/theme-wiiu.css'
import './assets/styles/theme-snes.css'
import './assets/styles/theme-nature.css'
import './assets/styles/theme-ps2.css'
import './assets/styles/theme-cassette.css'
import './assets/styles/theme-karaoke.css'

import { initCassetteThemeObserver } from './assets/js/cassette-theme.js'
import { initConfig } from './config'

initCassetteThemeObserver()

initConfig().finally(() => {
  createApp(App).mount('#app')
})
