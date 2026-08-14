<template>
  <div class="panel player player-retro-dock">
    <!-- Header with LED and Expand Button -->
    <div class="player-top-header">
      <div class="deck-indicator">
        <span class="led-dot" :class="isPlaying ? 'led-green' : 'led-yellow'"></span>
        <span class="deck-title">REPRODUCTOR</span>
      </div>
      <button class="btn-retro-secondary btn-mini-expand" @click="$emit('toggle-expand')" title="Pantalla Completa (⛶)">
        ⛶ EXPANDIR
      </button>
    </div>

    <!-- Album Art & Mini Disc -->
    <div class="album-art" id="albumArt" @click="$emit('toggle-expand')">
      <canvas ref="canvas" id="visualizer"></canvas>
      <img v-if="currentSong && getThumbnail(currentSong)" :src="getThumbnail(currentSong)" id="albumImage">
      <div v-else id="defaultArt">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="48" height="48">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      </div>
      <div class="art-click-hint">CLICK PARA EXPANDIR</div>
    </div>

    <!-- LCD Info Display -->
    <div class="lcd-display mini-lcd">
      <div class="lcd-track-marquee">
        <span class="lcd-text-primary">{{ currentSong ? currentSong.title : 'SIN MÚSICA' }}</span>
      </div>
      <div class="lcd-text-secondary">
        {{ currentSong ? (currentSong.uploader || 'Desconocido') : 'Selecciona una canción' }}
      </div>
    </div>

    <!-- Timeline Progress with Generous Scrub Hitbox -->
    <div class="progress-hitbox" @click="seek">
      <div class="progress-bar-retro">
        <div class="progress-fill-retro" :style="{ width: progress + '%' }"></div>
      </div>
    </div>

    <div class="time-info-retro">
      <span>{{ formatTime(currentTime) }}</span>
      <span>{{ formatTime(duration) }}</span>
    </div>

    <!-- Primary Transport Controls -->
    <div class="controls-retro">
      <button class="btn-retro-secondary btn-transport" @click="$emit('prev')" title="Anterior (P)">
        ⏮
      </button>
      <button class="btn-retro-primary btn-transport-play" @click="togglePlay" title="Reproducir / Pausa (Espacio)">
        {{ isPlaying ? '❚❚' : '▶' }}
      </button>
      <button class="btn-retro-secondary btn-transport" @click="$emit('next')" title="Siguiente (N)">
        ⏭
      </button>
    </div>

    <!-- Secondary Control Rack -->
    <div class="controls-extra-retro">
      <button 
        class="btn-retro-icon btn-action-square" 
        @click="$emit('toggle-queue')" 
        :class="{ active: isQueueOpen }" 
        title="Cola de Reproducción"
      >
        📑
      </button>

      <button 
        class="btn-retro-icon btn-action-square" 
        @click="$emit('toggle-shuffle')" 
        :class="{ active: isShuffle }" 
        title="Aleatorio"
      >
        🔀
      </button>

      <button 
        class="btn-retro-icon btn-action-square" 
        @click="toggleRepeat" 
        :class="{ active: repeatMode !== 'off' }" 
        title="Repetición"
      >
        {{ repeatMode === 'one' ? '🔂' : '🔁' }}
      </button>

      <button 
        class="btn-retro-icon btn-action-square" 
        @click="$emit('toggle-eq')" 
        :class="{ active: isEqOpen }" 
        title="Ecualizador"
      >
        🎚
      </button>

      <!-- Volume Bar -->
      <div class="mini-volume-wrapper">
        <button class="vol-ico-btn" @click="toggleMute" title="Silenciar / Activar audio">
          {{ isMuted ? '🔇' : '🔊' }}
        </button>
        <input 
          type="range" 
          v-model="volume" 
          min="0" 
          max="1" 
          step="0.05" 
          class="retro-range-mini"
          @input="handleVolumeChange"
        />
      </div>
    </div>

    <!-- Embedded Equalizer Module inside Player -->
    <EqualizerPanel :isOpen="isEqOpen" @change-band="$emit('change-band', $event)" />
    
    <audio ref="audio" crossorigin="anonymous" @timeupdate="updateTime" @ended="handleSongEnded"></audio>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import EqualizerPanel from './EqualizerPanel.vue'

const props = defineProps({
  currentSong: Object,
  isPlaying: Boolean,
  isShuffle: Boolean,
  repeatMode: { type: String, default: 'off' }, // 'off', 'all', 'one'
  isQueueOpen: Boolean,
  isEqOpen: Boolean
})

const emit = defineEmits([
  'play', 'pause', 'next', 'prev', 'seek', 'volume-change', 
  'toggle-queue', 'toggle-eq', 'toggle-shuffle', 'toggle-repeat', 
  'toggle-expand', 'ended', 'init-audio', 'time-update', 'change-band'
])

const audio = ref(null)
const canvas = ref(null)
const progress = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const isMuted = ref(false)
let prevVolume = 1

const togglePlay = () => {
  if (props.isPlaying) {
    emit('pause')
    audio.value?.pause()
  } else {
    emit('play')
    audio.value?.play()
  }
}

const toggleRepeat = () => {
  const nextMode = props.repeatMode === 'off' ? 'all' : props.repeatMode === 'all' ? 'one' : 'off'
  emit('toggle-repeat', nextMode)
}

const toggleMute = () => {
  if (isMuted.value) {
    volume.value = prevVolume || 1
    isMuted.value = false
  } else {
    prevVolume = volume.value
    volume.value = 0
    isMuted.value = true
  }
  handleVolumeChange()
}

const handleVolumeChange = () => {
  isMuted.value = volume.value === '0' || volume.value === 0
  emit('volume-change', volume.value)
}

const updateTime = () => {
  if (!audio.value) return
  currentTime.value = audio.value.currentTime
  duration.value = audio.value.duration || 0
  progress.value = (currentTime.value / duration.value) * 100 || 0
  emit('time-update', { currentTime: currentTime.value, duration: duration.value })
}

const seek = (e) => {
  if (!audio.value || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  const targetTime = pos * duration.value
  audio.value.currentTime = targetTime
}

const handleSongEnded = () => {
  if (props.repeatMode === 'one' && audio.value) {
    audio.value.currentTime = 0
    audio.value.play()
  } else {
    emit('ended')
  }
}

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

const getThumbnail = (song) => {
  if (!song) return null
  if (song.thumbnail && song.thumbnail.startsWith('http')) return song.thumbnail
  if (song.thumbnail) return song.thumbnail.startsWith('/') ? song.thumbnail : `/${song.thumbnail}`
  
  const hash = song.title ? song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 1
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

watch(() => props.currentSong, (newSong) => {
  if (newSong && audio.value) {
    if (newSong.url) {
      audio.value.src = newSong.url
    } else if (newSong.path) {
      audio.value.src = newSong.path.startsWith('http') ? newSong.path : (newSong.path.startsWith('/') ? newSong.path : `/${newSong.path}`)
    } else if (newSong.filename) {
      audio.value.src = `/api/stream/${encodeURIComponent(newSong.filename)}`
    }
    if (props.isPlaying) audio.value.play().catch(e => console.log('Auto-play blocked:', e))
  }
})

watch(() => props.isPlaying, (playing) => {
  if (audio.value) {
    if (playing) audio.value.play().catch(e => console.log('Play blocked:', e))
    else audio.value.pause()
  }
})

onMounted(() => {
  emit('init-audio', { audio: audio.value, canvas: canvas.value })
})
</script>

<style scoped>
.player-retro-dock {
  background: #c4c4c4;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #ffffff, inset -1px -1px 0px #666666, 4px 4px 0px #000000;
}

.player-top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid #000000;
}

.deck-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.deck-title {
  font-family: var(--font-pixel);
  font-size: 8px;
  color: #000000;
  letter-spacing: 0.5px;
}

.btn-mini-expand {
  padding: 4px 8px;
  font-size: 8px;
  cursor: pointer;
}

.album-art {
  position: relative;
  cursor: pointer;
  border: 3px solid #000000;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8), 3px 3px 0px #000000;
}

.art-click-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.75);
  color: #00f0ff;
  font-family: var(--font-pixel);
  font-size: 7px;
  text-align: center;
  padding: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}

.album-art:hover .art-click-hint {
  opacity: 1;
}

.mini-lcd {
  margin: 12px 0;
  padding: 8px 10px;
}

.lcd-track-marquee {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-hitbox {
  width: 100%;
  padding: 8px 0;
  cursor: pointer;
}

.progress-bar-retro {
  width: 100%;
  height: 8px;
  background: #111111;
  border: 1.5px solid #000000;
  position: relative;
}

.progress-fill-retro {
  height: 100%;
  background: #00A8E1;
  box-shadow: 0 0 4px #00A8E1;
}

.time-info-retro {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: bold;
  color: #333333;
  margin-bottom: 12px;
}

.controls-retro {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.btn-transport {
  width: 44px;
  height: 44px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.btn-transport-play {
  width: 56px;
  height: 56px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.controls-extra-retro {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #a8a8a8;
  padding: 6px;
  border: 2px solid #000000;
  box-shadow: inset 1px 1px 0px #666666;
}

.btn-action-square {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.mini-volume-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.vol-ico-btn {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vol-ico-btn:hover {
  transform: scale(1.1);
}

.retro-range-mini {
  width: 55px;
  cursor: pointer;
  accent-color: #00A8E1;
}
</style>
