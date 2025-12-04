<template>
  <div class="parallax-manager">
    <!-- Active Parallax Component -->
    <component 
      :is="activeComponent" 
      v-if="activeComponent"
      :isPlaying="isPlaying"
      :currentSongTime="currentSongTime"
      :songDuration="songDuration"
    />

    <!-- Admin/Settings Button -->
    <button class="parallax-settings-btn" @click="showSettings = true" title="Configurar Parallax">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
    </button>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="parallax-modal-overlay" @click.self="showSettings = false">
      <div class="parallax-modal">
        <h3>Configuración de Parallax</h3>
        <div class="parallax-options">
          <div 
            class="parallax-option" 
            :class="{ active: currentMode === 'default' }"
            @click="setMode('default')"
          >
            <div class="preview default"></div>
            <span>Por Defecto (Tema)</span>
          </div>
          <div 
            class="parallax-option" 
            :class="{ active: currentMode === 'bioclock' }"
            @click="setMode('bioclock')"
          >
            <div class="preview bioclock">
                <span class="preview-text">12:00</span>
            </div>
            <span>BioClock (Tiempo/Latido)</span>
          </div>
        </div>
        <button class="close-btn" @click="showSettings = false">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import BioClockParallax from './BioClockParallax.vue'

const props = defineProps({
  isPlaying: Boolean,
  currentSongTime: Number,
  songDuration: Number
})

const showSettings = ref(false)
const currentMode = ref('default')

const activeComponent = computed(() => {
  switch (currentMode.value) {
    case 'bioclock':
      return BioClockParallax
    case 'default':
    default:
      return null
  }
})

const setMode = (mode) => {
  currentMode.value = mode
  localStorage.setItem('parallax-mode', mode)
}

onMounted(() => {
  const saved = localStorage.getItem('parallax-mode')
  if (saved) {
    currentMode.value = saved
  }
})
</script>

<style scoped>
.parallax-manager {
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
}

.parallax-settings-btn {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1000;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.parallax-settings-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.parallax-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.parallax-modal {
  background: #222;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  border: 1px solid #444;
  color: white;
}

.parallax-modal h3 {
  margin-top: 0;
  margin-bottom: 20px;
  text-align: center;
}

.parallax-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.parallax-option {
  background: #333;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.parallax-option:hover {
  background: #444;
}

.parallax-option.active {
  border-color: #007bff;
  background: #3a3a3a;
}

.preview {
  width: 100%;
  height: 80px;
  border-radius: 4px;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview.default {
  background: linear-gradient(45deg, #333, #555);
}

.preview.bioclock {
  background: #000;
  position: relative;
}

.preview-text {
    color: #00FF00;
    font-family: monospace;
    font-weight: bold;
    transform: rotate(-45deg);
}

.close-btn {
  width: 100%;
  padding: 10px;
  background: #444;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}

.close-btn:hover {
  background: #555;
}
</style>
