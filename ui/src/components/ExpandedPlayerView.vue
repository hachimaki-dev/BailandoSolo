<template>
  <div v-if="isOpen" class="expanded-player-overlay" @click="close">
    <div class="expanded-player-chassis" @click.stop>
      <!-- Top Bar -->
      <div class="expanded-header">
        <div class="header-left">
          <span class="led-dot led-green"></span>
          <span class="player-studio-title">BAILANDO SOLO</span>
        </div>
        <div class="header-right">
          <button class="btn-retro-icon" @click="close" title="Cerrar (Esc)">✕</button>
        </div>
      </div>

      <!-- Main Studio Body -->
      <div class="expanded-body">
        <!-- Left: Big Artwork & Visualizer Display -->
        <div class="artwork-and-visualizer-section">
          <div class="big-artwork-frame" :class="{ 'is-playing': isPlaying }">
            <img v-if="currentSong && getThumbnail(currentSong)" :src="getThumbnail(currentSong)" class="big-cover-art" />
            <div v-else class="big-cover-fallback">
              <div class="fallback-disc">
                <span>♪</span>
              </div>
            </div>
            
            <!-- Vinyl / CRT Groove Overlay -->
            <div class="vinyl-grooves"></div>
            <div class="crt-glow-overlay"></div>
          </div>

          <!-- Real-Time Spectrum Visualizer Canvas -->
          <div class="spectrum-monitor">
            <canvas ref="expandedCanvas" class="spectrum-canvas"></canvas>
          </div>
        </div>

        <!-- Right: LCD Readout, Track Specs, Lyrics & Controls -->
        <div class="controls-and-specs-section">
          <!-- LCD Monitor -->
          <div class="lcd-display expanded-lcd">
            <div class="lcd-track-title">{{ currentSong?.title || 'SIN REPRODUCCIÓN' }}</div>
            <div class="lcd-track-artist">{{ currentSong?.uploader || 'SELECCIONA UNA CANCIÓN' }}</div>
            <div class="lcd-specs-row">
              <span>FORMATO: {{ currentSong?.ext || 'MP3' }}</span>
              <span>CARPETA: {{ currentSong?.folder || 'ARCHIVE' }}</span>
              <span>ESTADO: {{ isPlaying ? 'PLAYING ▶' : 'PAUSED ❚❚' }}</span>
            </div>
          </div>

          <!-- Audio Progress Bar -->
          <div class="timeline-container">
            <div class="progress-bar-retro" @click="seek">
              <div class="progress-fill-retro" :style="{ width: progress + '%' }"></div>
              <div class="progress-handle" :style="{ left: progress + '%' }"></div>
            </div>
            <div class="time-display-row">
              <span class="time-text">{{ formatTime(currentTime) }}</span>
              <span class="time-text">-{{ formatTime(Math.max(0, duration - currentTime)) }}</span>
            </div>
          </div>

          <!-- Main Tactical Control Deck -->
          <div class="tactical-controls-row">
            <button 
              class="btn-retro-secondary btn-icon-lg" 
              :class="{ active: isShuffle }" 
              @click="$emit('toggle-shuffle')"
              title="Modo Aleatorio"
            >
              🔀
            </button>

            <button class="btn-retro-secondary btn-icon-lg" @click="$emit('prev')" title="Anterior (P)">
              ⏮
            </button>

            <button class="btn-retro-primary btn-play-huge" @click="togglePlay" title="Play/Pause (Espacio)">
              {{ isPlaying ? '❚❚' : '▶' }}
            </button>

            <button class="btn-retro-secondary btn-icon-lg" @click="$emit('next')" title="Siguiente (N)">
              ⏭
            </button>

            <button 
              class="btn-retro-secondary btn-icon-lg" 
              :class="{ active: repeatMode !== 'off' }"
              @click="toggleRepeat" 
              title="Modo Repetir"
            >
              {{ repeatMode === 'one' ? '🔂' : '🔁' }}
            </button>
          </div>

          <!-- Secondary Control Sliders (Volume, EQ & Queue Toggle) -->
          <div class="secondary-deck-row">
            <div class="volume-box">
              <span class="vol-icon">🔊</span>
              <input 
                type="range" 
                v-model="volume" 
                min="0" 
                max="1" 
                step="0.05" 
                class="retro-range-slider"
                @input="$emit('volume-change', volume)" 
              />
              <span class="vol-percent">{{ Math.round(volume * 100) }}%</span>
            </div>

            <div class="deck-buttons-group">
              <button 
                class="btn-retro-secondary btn-sm" 
                :class="{ active: isEqOpen }"
                @click="$emit('toggle-eq')"
              >
                🎚 EQ
              </button>
              <button 
                class="btn-retro-secondary btn-sm" 
                :class="{ active: isQueueOpen }"
                @click="$emit('toggle-queue')"
              >
                📑 COLA ({{ queue.length }})
              </button>
            </div>
          </div>

          <!-- Mini Queue Dock in Expanded View -->
          <div class="expanded-queue-dock">
            <div class="queue-dock-header">
              <span>PRÓXIMAS EN LA COLA</span>
              <span class="badge-retro info pixel">{{ queue.length }} PISTAS</span>
            </div>
            <div class="queue-dock-list">
              <div v-if="queue.length === 0" class="empty-queue-hint">
                No hay más canciones en la cola. Arrastra o agrega canciones con click derecho.
              </div>
              <div 
                v-else 
                v-for="(item, idx) in queue.slice(0, 5)" 
                :key="idx" 
                class="queue-dock-item"
                @click="$emit('play-queue-item', idx)"
              >
                <span class="queue-idx">{{ idx + 1 }}</span>
                <span class="queue-title">{{ item.title }}</span>
                <button class="remove-dock-btn" @click.stop="$emit('remove-queue-item', idx)">✕</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { streamUrl } from '../config'

const props = defineProps({
  isOpen: Boolean,
  currentSong: Object,
  isPlaying: Boolean,
  currentTime: Number,
  duration: Number,
  isShuffle: Boolean,
  repeatMode: { type: String, default: 'off' }, // 'off', 'all', 'one'
  isEqOpen: Boolean,
  isQueueOpen: Boolean,
  queue: { type: Array, default: () => [] },
  analyserNode: Object
})

const emit = defineEmits([
  'close', 'play', 'pause', 'prev', 'next', 'seek', 
  'toggle-shuffle', 'toggle-repeat', 'toggle-eq', 'toggle-queue', 
  'volume-change', 'play-queue-item', 'remove-queue-item'
])

const volume = ref(1)
const expandedCanvas = ref(null)
let animId = null

const progress = computed(() => {
  if (!props.duration) return 0
  return (props.currentTime / props.duration) * 100
})

const togglePlay = () => {
  if (props.isPlaying) emit('pause')
  else emit('play')
}

const toggleRepeat = () => {
  const nextMode = props.repeatMode === 'off' ? 'all' : props.repeatMode === 'all' ? 'one' : 'off'
  emit('toggle-repeat', nextMode)
}

const seek = (e) => {
  if (!props.duration) return
  const rect = e.currentTarget.getBoundingClientRect()
  const pos = (e.clientX - rect.left) / rect.width
  emit('seek', pos * props.duration)
}

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

const getThumbnail = (song) => {
  if (!song) return null
  if (song.thumbnail) return streamUrl(song.thumbnail)
  const hash = song.title ? song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 1
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const drawExpandedVisualizer = () => {
  if (!expandedCanvas.value || !props.analyserNode) {
    animId = requestAnimationFrame(drawExpandedVisualizer)
    return
  }

  const canvas = expandedCanvas.value
  const ctx = canvas.getContext('2d')
  const bufferLength = props.analyserNode.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  props.analyserNode.getByteFrequencyData(dataArray)

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const barWidth = (canvas.width / bufferLength) * 2.2
  let x = 0

  for (let i = 0; i < bufferLength; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height

    const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0)
    gradient.addColorStop(0, '#00ff66')
    gradient.addColorStop(0.6, '#00f0ff')
    gradient.addColorStop(1, '#ff3366')

    ctx.fillStyle = gradient
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight)

    x += barWidth
  }

  animId = requestAnimationFrame(drawExpandedVisualizer)
}

watch(() => props.isOpen, (open) => {
  if (open) {
    onMountedVisualizer()
  } else if (animId) {
    cancelAnimationFrame(animId)
  }
})

const onMountedVisualizer = () => {
  if (expandedCanvas.value) {
    expandedCanvas.value.width = 360
    expandedCanvas.value.height = 80
    drawExpandedVisualizer()
  }
}

const close = () => {
  emit('close')
}

// Global hotkeys when expanded view is active
const handleKeydown = (e) => {
  if (!props.isOpen) return
  if (e.key === 'Escape') {
    close()
  } else if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
    e.preventDefault()
    togglePlay()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  if (props.isOpen) onMountedVisualizer()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (animId) cancelAnimationFrame(animId)
})
</script>

<style scoped>
.expanded-player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  animation: fadeIn 0.2s ease;
}

.expanded-player-chassis {
  width: 880px;
  max-width: 95vw;
  background: #c8c8c8;
  border: 4px solid #000000;
  box-shadow: inset 2px 2px 0px #ffffff, inset -2px -2px 0px #555555, 12px 12px 0px #000000;
  padding: 16px;
  position: relative;
}

.expanded-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 10px;
  border-bottom: 3px solid #000000;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.player-studio-title {
  font-family: var(--font-pixel);
  font-size: 11px;
  color: #000000;
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expanded-body {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
}

/* Artwork & Visualizer */
.artwork-and-visualizer-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.big-artwork-frame {
  width: 320px;
  height: 320px;
  background: #111111;
  border: 4px solid #000000;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.9), 4px 4px 0px #000000;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.big-cover-art {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.big-artwork-frame.is-playing .big-cover-art {
  transform: scale(1.02);
}

.big-cover-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, #333333 0%, #111111 100%);
}

.fallback-disc {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 4px solid #555555;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #00f0ff;
}

.vinyl-grooves {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-radial-gradient(circle at center, transparent 0, transparent 4px, rgba(255, 255, 255, 0.03) 5px);
  pointer-events: none;
}

.crt-glow-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(0, 0, 0, 0.3) 100%);
  pointer-events: none;
}

.spectrum-monitor {
  width: 320px;
  background: #0b1712;
  border: 2px solid #000000;
  padding: 6px;
  position: relative;
  box-shadow: inset 1px 1px 4px #000000;
}

.spectrum-canvas {
  width: 100%;
  height: 60px;
  display: block;
}

.spectrum-badge {
  position: absolute;
  bottom: 2px;
  right: 6px;
  font-family: var(--font-pixel);
  font-size: 6px;
  color: #00f0ff;
  opacity: 0.7;
}

/* Controls & Specs */
.controls-and-specs-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.expanded-lcd {
  min-height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.lcd-track-title {
  font-family: var(--font-lcd);
  font-size: 26px;
  color: var(--color-lcd-text);
  text-shadow: 0 0 6px var(--color-lcd-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lcd-track-artist {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: var(--color-lcd-cyan);
  text-shadow: 0 0 4px var(--color-lcd-cyan);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lcd-specs-row {
  display: flex;
  gap: 12px;
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #ffb703;
  opacity: 0.85;
}

/* Timeline */
.timeline-container {
  padding: 4px 0;
}

.progress-bar-retro {
  width: 100%;
  height: 10px;
  background: #111111;
  border: 2px solid #000000;
  position: relative;
  cursor: pointer;
  box-shadow: inset 1px 1px 2px #000000;
}

.progress-fill-retro {
  height: 100%;
  background: #00A8E1;
  box-shadow: 0 0 8px #00A8E1;
}

.progress-handle {
  position: absolute;
  top: -4px;
  width: 8px;
  height: 14px;
  background: #ffffff;
  border: 1px solid #000000;
  transform: translateX(-50%);
}

.time-display-row {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: bold;
  color: #333333;
  margin-top: 4px;
}

/* Tactical Controls */
.tactical-controls-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.btn-icon-lg {
  width: 44px;
  height: 44px;
  font-size: 18px;
}

.btn-play-huge {
  width: 64px;
  height: 64px;
  font-size: 24px;
  border-radius: 4px;
}

/* Secondary Deck */
.secondary-deck-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #bbbbbb;
  padding: 8px 12px;
  border: 2px solid #000000;
}

.volume-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.retro-range-slider {
  width: 100px;
  accent-color: #00A8E1;
}

.vol-percent {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: bold;
}

.deck-buttons-group {
  display: flex;
  gap: 6px;
}

/* Queue Dock */
.expanded-queue-dock {
  background: #dedede;
  border: 2px solid #000000;
  padding: 8px;
  max-height: 150px;
  display: flex;
  flex-direction: column;
}

.queue-dock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-pixel);
  font-size: 8px;
  margin-bottom: 6px;
  color: #222222;
}

.queue-dock-list {
  overflow-y: auto;
  flex: 1;
}

.queue-dock-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  background: #ffffff;
  border: 1px solid #cccccc;
  margin-bottom: 3px;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 11px;
}

.queue-dock-item:hover {
  background: #e0f2fe;
}

.queue-idx {
  font-weight: bold;
  color: #0088cc;
  width: 14px;
}

.queue-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-dock-btn {
  background: none;
  border: none;
  color: #999999;
  cursor: pointer;
  font-weight: bold;
}

.remove-dock-btn:hover {
  color: #c92a2a;
}

.empty-queue-hint {
  padding: 12px;
  text-align: center;
  font-family: var(--font-mono);
  font-size: 11px;
  color: #777777;
}

@media (max-width: 800px) {
  .expanded-body {
    grid-template-columns: 1fr;
  }
  .big-artwork-frame {
    width: 220px;
    height: 220px;
  }
}
</style>
