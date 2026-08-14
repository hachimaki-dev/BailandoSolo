<template>
  <div class="theme-selector">
    <button v-if="showExperimental" class="theme-btn" :class="{ active: currentTheme === 'wiiu' }" @click="setTheme('wiiu')" title="Tema Wii U">🎮</button>
    <button class="theme-btn" :class="{ active: currentTheme === 'snes' }" @click="setTheme('snes')" title="Tema SNES">🕹️</button>
    <button v-if="showExperimental" class="theme-btn" :class="{ active: currentTheme === 'nature' }" @click="setTheme('nature')" title="Tema Puerto Montt">🌧️</button>
    <button v-if="showExperimental" class="theme-btn" :class="{ active: currentTheme === 'ps2' }" @click="setTheme('ps2')" title="Tema PS2">🌌</button>
    <button v-if="showExperimental" class="theme-btn" :class="{ active: currentTheme === 'cassette' }" @click="setTheme('cassette')" title="Tema Cassette">📼</button>
    <div class="separator"></div>
    <button class="theme-btn" @click="$emit('open-stats')" title="Estadísticas">📊</button>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  showExperimental: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['theme-change', 'open-stats'])

const currentTheme = ref('snes')

const setTheme = (theme) => {
  currentTheme.value = theme
  document.body.setAttribute('data-theme', theme)
  emit('theme-change', theme)
}

// If experimental mode is turned off and we are on an experimental theme, switch to SNES
watch(() => props.showExperimental, (newValue) => {
  if (!newValue && currentTheme.value !== 'snes') {
    setTheme('snes')
  }
})

onMounted(() => {
  setTheme('snes')
})
</script>

<style scoped>
.separator {
  width: 1px;
  background: var(--border-color);
  margin: 0 4px;
  opacity: 0.5;
}
</style>

