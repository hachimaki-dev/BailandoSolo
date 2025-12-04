<template>
  <div class="theme-selector">
    <button class="theme-btn" :class="{ active: currentTheme === 'wiiu' }" @click="setTheme('wiiu')" title="Tema Wii U">🎮</button>
    <button class="theme-btn" :class="{ active: currentTheme === 'snes' }" @click="setTheme('snes')" title="Tema SNES">🕹️</button>
    <button class="theme-btn" :class="{ active: currentTheme === 'nature' }" @click="setTheme('nature')" title="Tema Puerto Montt">🌧️</button>
    <button class="theme-btn" :class="{ active: currentTheme === 'ps2' }" @click="setTheme('ps2')" title="Tema PS2">🌌</button>
    <button class="theme-btn" :class="{ active: currentTheme === 'cassette' }" @click="setTheme('cassette')" title="Tema Cassette">📼</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTheme = ref('wiiu')

const setTheme = (theme) => {
  currentTheme.value = theme
  document.body.setAttribute('data-theme', theme)
}

onMounted(() => {
  setTheme('wiiu')
})
</script>
