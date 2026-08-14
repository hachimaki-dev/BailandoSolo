<template>
  <div class="panel downloader-console-deck">
    <!-- Top Bar -->
    <div class="deck-top-bar">
      <div class="deck-title-group">
        <span class="led-dot" :class="isDownloadingAny ? 'led-blue' : 'led-green'"></span>
        <h2>⚡ DESCARGAS DE YOUTUBE</h2>
      </div>
      <div class="deck-status-pill">
        <span v-if="isDownloadingAny" class="badge-retro info pixel">DESCARGANDO ({{ activeDownloadsCount }})</span>
        <span v-else class="badge-retro success pixel">LISTO</span>
      </div>
    </div>

    <!-- URL Input & Ripper Console Controls -->
    <div class="ripper-input-chassis">
      <div class="input-primary-row">
        <div class="url-box">
          <label>URL DE YOUTUBE (VIDEO O PLAYLIST)</label>
          <div class="url-input-inner">
            <span class="url-icon">📼</span>
            <input 
              type="text" 
              v-model="url" 
              class="retro-input-main" 
              placeholder="https://www.youtube.com/watch?v=... o playlist"
              :disabled="isAnalyzing"
              @keyup.enter="analyze"
            />
            <button v-if="url" class="btn-clear-url" @click="url = ''" title="Borrar">✕</button>
          </div>
        </div>

        <button 
          class="btn-retro-primary btn-analyze-deck" 
          @click="analyze" 
          :disabled="isAnalyzing || !url.trim()"
        >
          <span v-if="isAnalyzing">⌛ ANALIZANDO...</span>
          <span v-else>🔍 ANALIZAR</span>
        </button>
      </div>

      <!-- Settings & Folder Row -->
      <div class="deck-settings-row">
        <div class="setting-item">
          <label>📁 CARPETA DESTINO</label>
          <input 
            type="text" 
            v-model="folder" 
            class="retro-input-compact" 
            placeholder="Mi Música / Carpeta" 
          />
        </div>

        <div class="setting-item">
          <label>🎚 CALIDAD DE AUDIO</label>
          <select v-model="quality" class="retro-select-compact">
            <option value="192">192 kbps (Estándar)</option>
            <option value="256">256 kbps (Alta Fidelidad)</option>
            <option value="320">320 kbps (Máxima Calidad)</option>
          </select>
        </div>

        <div class="setting-item">
          <label>🏷 PLANTILLA DE NOMBRE</label>
          <select v-model="namingTemplate" class="retro-select-compact">
            <option value="default">{title}.mp3</option>
            <option value="artist_title">{artist} - {title}.mp3</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Phased Loading Feedback -->
    <div v-if="isAnalyzing" class="analysis-feedback-card">
      <div class="spinner-led"></div>
      <div class="phase-info">
        <div class="phase-title">{{ analysisPhaseText }}</div>
        <div class="phase-sub">Obteniendo metadatos y carátulas...</div>
      </div>
    </div>

    <!-- Analyzed Songs / Download Queue View -->
    <div v-if="playlist" class="ripper-results-card">
      <div class="results-header-bar">
        <div class="results-meta">
          <h3>{{ playlist.title }}</h3>
          <div class="results-badges">
            <span class="badge-retro info pixel">{{ playlist.songs.length }} PISTAS</span>
            <span v-if="duplicatesList.length > 0" class="badge-retro warning pixel">
              {{ duplicatesList.length }} EN BIBLIOTECA
            </span>
          </div>
        </div>

        <!-- Big Download Action -->
        <button 
          class="btn-retro-primary btn-download-master" 
          @click="startBatchDownload" 
          :disabled="selectedSongs.length === 0 || isStartingDownload"
        >
          ⬇ DESCARGAR TODO ({{ selectedSongs.length }})
        </button>
      </div>

      <!-- Quick Duplicate Filter Option -->
      <div v-if="duplicatesList.length > 0" class="duplicates-toggle-row">
        <label class="dup-checkbox-label">
          <input 
            type="checkbox" 
            v-model="omitDuplicates" 
            @change="handleDuplicateToggle" 
          />
          <span>Omitir canciones que ya están en mi colección ({{ duplicatesList.length }})</span>
        </label>
      </div>

      <!-- Select All & Summary Line -->
      <div class="selection-action-strip">
        <label class="select-all-box">
          <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
          <span>Seleccionar todas ({{ selectedSongs.length }}/{{ playlist.songs.length }})</span>
        </label>
        <span class="dest-folder-indicator">Destino: <strong>{{ folder || 'Music' }}</strong></span>
      </div>

      <!-- Analyzed Song List / Cartridge Slots -->
      <div class="song-list-ripper">
        <div 
          v-for="song in playlist.songs" 
          :key="song.id" 
          class="ripper-song-slot"
          :class="{ 'is-selected': isSelected(song.id), 'is-duplicate': isDuplicate(song.id), 'is-downloading': song.status === 'downloading', 'is-finished': song.status === 'finished' }"
          @click="toggleSongSelection(song.id)"
        >
          <div class="slot-check" @click.stop>
            <input type="checkbox" :checked="isSelected(song.id)" @change="toggleSongSelection(song.id)" />
          </div>

          <img :src="song.thumbnail || defaultThumb" class="slot-thumb" />

          <div class="slot-details">
            <div class="slot-title">{{ song.title }}</div>
            <div class="slot-artist">{{ song.uploader || 'Desconocido' }}</div>
            <div v-if="isDuplicate(song.id)" class="slot-duplicate-warn">
              📁 Ya descargada en: {{ getDuplicateFolder(song.id) }}
            </div>
          </div>

          <!-- Progress / LED Status -->
          <div class="slot-status-box">
            <div v-if="song.status === 'downloading'" class="slot-progress-wrapper">
              <div class="progress-bar-retro mini">
                <div class="progress-fill-retro" :style="{ width: song.percent + '%' }"></div>
              </div>
              <span class="speed-text">{{ Math.round(song.percent) }}% ({{ formatSpeed(song.speed) }})</span>
            </div>
            <div v-else-if="song.status === 'finished'" class="slot-badge-finish">
              <span class="badge-retro success pixel">✓ DESCARGADO</span>
            </div>
            <div v-else-if="song.status === 'waiting'" class="slot-badge-finish">
              <span class="badge-retro info pixel">⏳ EN COLA</span>
            </div>
            <div v-else-if="song.status === 'error'" class="slot-badge-finish">
              <span class="badge-retro danger pixel">⚠️ ERROR</span>
            </div>
            <div v-else class="slot-badge-finish">
              <span class="badge-retro neutral pixel">LISTA</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Play / Random Cartridges Shelf (Beloved Core Feature) -->
    <div class="quick-play-shelf-section">
      <div class="shelf-header-bar">
        <div class="shelf-title-left">
          <span class="shelf-icon">🎮</span>
          <h3>COLECCIÓN DE CARTUCHOS</h3>
          <span class="shelf-hint">(Pasa el cursor para escuchar 5s · Click para reproducir)</span>
        </div>
        <button class="btn-retro-secondary btn-sm" @click="loadQuickPlay">
          🔄 Barajar Cartuchos
        </button>
      </div>

      <div class="cartridge-grid-deck">
        <div 
          v-for="(song, index) in quickPlaySongs" 
          :key="index" 
          class="cartridge-item"
          @click="playCartridge(song, index)"
          @mouseenter="startPreview(song)"
          @mouseleave="stopPreview"
          @contextmenu.prevent="showContextMenu($event, song)"
        >
          <div class="cartridge-label">
            <img :src="getThumbnail(song)" :alt="song.title" />
            <div class="cartridge-overlay">
              <div class="cartridge-play-btn">▶</div>
            </div>

            <!-- Queue quick button with generous hitbox -->
            <button class="cartridge-queue-btn" @click.stop="addToQueue(song)" title="Agregar a la cola">
              ＋
            </button>

            <!-- Preview Audio Playing Indicator -->
            <div v-if="previewingSong === song" class="preview-playing-indicator">
              <span class="preview-eq-bars"></span>
            </div>
          </div>

          <div class="cartridge-title-tag">
            {{ song.title }}
          </div>
        </div>

        <div v-if="quickPlaySongs.length === 0" class="empty-shelf-message">
          {{ loadingQuickPlay ? 'Cargando cartuchos...' : 'No hay canciones en la biblioteca aún. ¡Pega una URL arriba y descarga tu primera música!' }}
        </div>
      </div>

      <audio ref="previewAudio" crossorigin="anonymous" style="display: none;"></audio>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { LibraryService } from '../services/LibraryService'

const props = defineProps({
  allSongs: { type: Array, default: () => [] }
})

const emit = defineEmits(['download-start', 'play-cartridge', 'add-to-queue', 'context-menu'])

const url = ref('')
const folder = ref('')
const quality = ref('192')
const namingTemplate = ref('default')

const isAnalyzing = ref(false)
const analysisPhaseText = ref('Analizando playlist...')
const playlist = ref(null)
const selectedSongIds = ref(new Set())
const duplicatesList = ref([])
const omitDuplicates = ref(true)
const isStartingDownload = ref(false)

// Quick Play State
const quickPlaySongs = ref([])
const loadingQuickPlay = ref(false)
const previewAudio = ref(null)
const previewingSong = ref(null)
const previewTimeout = ref(null)

let pollInterval = null
const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23cccccc' width='48' height='48'/%3E%3C/svg%3E"

const selectedSongs = computed(() => {
  if (!playlist.value) return []
  return playlist.value.songs.filter(s => selectedSongIds.value.has(s.id))
})

const isAllSelected = computed(() => {
  if (!playlist.value || playlist.value.songs.length === 0) return false
  return selectedSongIds.value.size === playlist.value.songs.length
})

const isDownloadingAny = computed(() => {
  if (!playlist.value) return false
  return playlist.value.songs.some(s => s.status === 'downloading' || s.status === 'waiting')
})

const activeDownloadsCount = computed(() => {
  if (!playlist.value) return 0
  return playlist.value.songs.filter(s => s.status === 'downloading' || s.status === 'waiting').length
})

const isSelected = (id) => selectedSongIds.value.has(id)
const isDuplicate = (id) => duplicatesList.value.some(d => d.id === id)
const getDuplicateFolder = (id) => {
  const match = duplicatesList.value.find(d => d.id === id)
  return match ? match.existing_folder : ''
}

const toggleSongSelection = (id) => {
  if (selectedSongIds.value.has(id)) {
    selectedSongIds.value.delete(id)
  } else {
    selectedSongIds.value.add(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedSongIds.value.clear()
  } else {
    playlist.value.songs.forEach(s => selectedSongIds.value.add(s.id))
  }
}

const handleDuplicateToggle = () => {
  if (!playlist.value) return
  if (omitDuplicates.value) {
    const dupIds = new Set(duplicatesList.value.map(d => d.id))
    selectedSongIds.value = new Set(playlist.value.songs.filter(s => !dupIds.has(s.id)).map(s => s.id))
  } else {
    playlist.value.songs.forEach(s => selectedSongIds.value.add(s.id))
  }
}

const analyze = async () => {
  if (!url.value.trim()) return
  isAnalyzing.value = true
  playlist.value = null
  duplicatesList.value = []

  analysisPhaseText.value = '1/3 Conectando con YouTube...'

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.error || 'Error al analizar URL')
    }

    analysisPhaseText.value = '2/3 Extrayendo metadatos y carátulas...'
    const data = await response.json()

    data.songs = data.songs.map(s => ({
      ...s,
      status: 'idle',
      percent: 0,
      speed: 0
    }))

    if (!folder.value && data.title) {
      folder.value = data.title.replace(/[^a-zA-Z0-9_-]/gi, '_').replace(/_+/g, '_').slice(0, 30)
    }

    analysisPhaseText.value = '3/3 Comprobando duplicados en la biblioteca...'
    const dupCheck = await LibraryService.checkDuplicates(data.songs.map(s => ({
      id: s.id,
      title: s.title,
      uploader: s.uploader
    })))

    duplicatesList.value = dupCheck.duplicates || []

    // Select based on omitDuplicates toggle
    if (omitDuplicates.value && duplicatesList.value.length > 0) {
      const dupSet = new Set(duplicatesList.value.map(d => d.id))
      selectedSongIds.value = new Set(data.songs.filter(s => !dupSet.has(s.id)).map(s => s.id))
      if (selectedSongIds.value.size === 0 && data.songs.length > 0) {
        selectedSongIds.value = new Set(data.songs.map(s => s.id))
      }
    } else {
      selectedSongIds.value = new Set(data.songs.map(s => s.id))
    }

    playlist.value = data
  } catch (e) {
    alert('Error al analizar: ' + e.message)
  } finally {
    isAnalyzing.value = false
  }
}

const startBatchDownload = async () => {
  if (!playlist.value || selectedSongs.value.length === 0) return
  isStartingDownload.value = true

  const idsToDownload = Array.from(selectedSongIds.value)

  playlist.value.songs.forEach(s => {
    if (selectedSongIds.value.has(s.id)) {
      s.status = 'waiting'
    }
  })

  try {
    await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: url.value,
        folder_name: folder.value || 'Music',
        selected_ids: idsToDownload,
        quality: quality.value,
        naming_template: namingTemplate.value
      })
    })

    if (pollInterval) clearInterval(pollInterval)
    pollInterval = setInterval(updateDownloadProgress, 1000)
    emit('download-start')
  } catch (e) {
    alert('Error al iniciar descarga: ' + e.message)
  } finally {
    isStartingDownload.value = false
  }
}

const updateDownloadProgress = async () => {
  try {
    const res = await fetch('/api/status')
    if (!res.ok) return
    const statusMap = await res.json()

    if (playlist.value && playlist.value.songs) {
      playlist.value.songs.forEach(song => {
        const itemStatus = statusMap[song.id]
        if (itemStatus) {
          song.status = itemStatus.status
          song.percent = itemStatus.percent || 0
          song.speed = itemStatus.speed || 0
        }
      })
    }
  } catch (e) {
    console.error('Polling error:', e)
  }
}

const formatSpeed = (speed) => {
  if (!speed) return ''
  if (speed > 1024 * 1024) return (speed / (1024 * 1024)).toFixed(1) + ' MB/s'
  return (speed / 1024).toFixed(0) + ' KB/s'
}

// ─── Quick Play Shelf & Hover Preview ─────────────────────────────────────────

const loadQuickPlay = async () => {
  loadingQuickPlay.value = true
  try {
    const res = await LibraryService.getRandomSongs()
    quickPlaySongs.value = res || []
  } catch (e) {
    console.error('Error loading quick play:', e)
  } finally {
    loadingQuickPlay.value = false
  }
}

const getThumbnail = (song) => {
  if (!song) return defaultThumb
  if (song.thumbnail) return LibraryService.getThumbnailUrl(song.thumbnail)
  const hash = song.title ? song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 1
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const playCartridge = (song, index) => {
  stopPreview()
  emit('play-cartridge', { song, index, list: quickPlaySongs.value })
}

const startPreview = (song) => {
  if (!previewAudio.value || !song) return
  if (previewTimeout.value) clearTimeout(previewTimeout.value)

  previewTimeout.value = setTimeout(() => {
    try {
      let audioUrl = song.url || (song.path ? (song.path.startsWith('/') ? song.path : `/${song.path}`) : `/api/stream/${encodeURIComponent(song.filename)}`)
      const audio = previewAudio.value
      
      audio.onloadedmetadata = () => {
        if (!audio.duration) return
        audio.currentTime = audio.duration / 2
        audio.volume = 0.3
        audio.play().then(() => {
          setTimeout(() => {
            if (previewingSong.value === song) fadeOutAndStop()
          }, 4500)
        }).catch(e => console.log('Preview blocked:', e))
      }

      audio.src = audioUrl
      audio.load()
      previewingSong.value = song
    } catch (e) {
      console.error('Preview error:', e)
    }
  }, 200)
}

const fadeOutAndStop = () => {
  const audio = previewAudio.value
  if (!audio) return
  const fade = setInterval(() => {
    if (audio.volume > 0.05) audio.volume -= 0.05
    else {
      clearInterval(fade)
      stopPreview()
    }
  }, 80)
}

const stopPreview = () => {
  if (previewTimeout.value) {
    clearTimeout(previewTimeout.value)
    previewTimeout.value = null
  }
  if (previewAudio.value) {
    previewAudio.value.pause()
    previewAudio.value.currentTime = 0
  }
  previewingSong.value = null
}

const addToQueue = (song) => {
  emit('add-to-queue', song)
}

const showContextMenu = (event, song) => {
  emit('context-menu', { event, song })
}

onMounted(() => {
  loadQuickPlay()
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  stopPreview()
})
</script>

<style scoped>
.downloader-console-deck {
  background: #c4c4c4;
  border: 4px solid #000000;
  box-shadow: inset 2px 2px 0px #ffffff, inset -2px -2px 0px #666666, 6px 6px 0px #000000;
  padding: 16px;
}

.deck-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 3px solid #000000;
}

.deck-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.deck-title-group h2 {
  font-family: var(--font-pixel);
  font-size: 12px;
  margin: 0;
  color: #000000;
}

/* Ripper Input Chassis */
.ripper-input-chassis {
  background: #dcdcdc;
  border: 3px solid #000000;
  padding: 14px;
  margin-bottom: 16px;
  box-shadow: inset 1px 1px 0px #ffffff, 3px 3px 0px #000000;
}

.input-primary-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  margin-bottom: 12px;
}

.url-box {
  flex: 1;
}

.url-box label {
  display: block;
  font-family: var(--font-pixel);
  font-size: 8px;
  margin-bottom: 6px;
  color: #111111;
}

.url-input-inner {
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 3px solid #000000;
  padding: 2px 8px;
  box-shadow: inset 2px 2px 0px #666666;
}

.url-icon {
  font-size: 16px;
  margin-right: 6px;
}

.retro-input-main {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  color: #000000;
  padding: 8px 0;
  outline: none;
}

.btn-clear-url {
  background: none;
  border: none;
  font-weight: bold;
  cursor: pointer;
  padding: 4px;
}

.btn-analyze-deck {
  height: 44px;
  padding: 0 20px;
  font-size: 11px;
}

.deck-settings-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 10px;
}

.setting-item label {
  display: block;
  font-family: var(--font-pixel);
  font-size: 7px;
  margin-bottom: 4px;
  color: #333333;
}

.retro-input-compact, .retro-select-compact {
  width: 100%;
  padding: 8px;
  background: #ffffff;
  border: 2px solid #000000;
  font-family: var(--font-mono);
  font-size: 11px;
}

/* Analysis Feedback */
.analysis-feedback-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #0b1712;
  border: 3px solid #000000;
  padding: 14px;
  margin-bottom: 16px;
  box-shadow: inset 2px 2px 4px #000000;
}

.spinner-led {
  width: 22px;
  height: 22px;
  border: 3px solid #222222;
  border-top-color: #00f0ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.phase-title {
  font-family: var(--font-pixel);
  font-size: 10px;
  color: #00f0ff;
}

.phase-sub {
  font-family: var(--font-mono);
  font-size: 11px;
  color: #39ff14;
  margin-top: 2px;
}

/* Results Section */
.ripper-results-card {
  background: #e4e4e4;
  border: 3px solid #000000;
  padding: 14px;
  margin-bottom: 20px;
  box-shadow: 4px 4px 0px #000000;
}

.results-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 2px solid #000000;
  margin-bottom: 10px;
}

.results-meta h3 {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.results-badges {
  display: flex;
  gap: 6px;
}

.btn-download-master {
  padding: 12px 20px;
  font-size: 11px;
}

.duplicates-toggle-row {
  background: #fef3c7;
  border: 2px solid #d97706;
  padding: 8px 12px;
  margin-bottom: 10px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.dup-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #92400e;
}

.selection-action-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.select-all-box {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-weight: bold;
}

.song-list-ripper {
  max-height: 320px;
  overflow-y: auto;
  border: 2px solid #000000;
  background: #ffffff;
}

.ripper-song-slot {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background 0.1s ease;
}

.ripper-song-slot:hover {
  background: #e0f2fe;
}

.ripper-song-slot.is-selected {
  background: #f0fdf4;
}

.slot-thumb {
  width: 38px;
  height: 38px;
  object-fit: cover;
  border: 1.5px solid #000000;
}

.slot-details {
  flex: 1;
  min-width: 0;
}

.slot-title {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-artist {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #666666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-duplicate-warn {
  font-family: var(--font-mono);
  font-size: 9px;
  color: #b45309;
  font-weight: 600;
}

.slot-progress-wrapper {
  width: 120px;
}

.speed-text {
  font-family: var(--font-mono);
  font-size: 9px;
  color: #0077b6;
  font-weight: bold;
}

/* Quick Play Shelf */
.quick-play-shelf-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 3px solid #000000;
}

.shelf-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.shelf-title-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.shelf-icon {
  font-size: 18px;
}

.shelf-title-left h3 {
  font-family: var(--font-pixel);
  font-size: 10px;
  margin: 0;
  color: #000000;
}

.shelf-hint {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #555555;
}

.cartridge-grid-deck {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 14px;
  max-height: 380px;
  overflow-y: auto;
  padding: 4px;
}

.cartridge-item {
  background: #dedede;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #ffffff, 3px 3px 0px #000000;
  padding: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.1s ease;
}

.cartridge-item:hover {
  transform: translateY(-4px);
  background: #e0f2fe;
}

.cartridge-label {
  width: 100%;
  aspect-ratio: 1;
  background: #222222;
  border: 2px solid #000000;
  position: relative;
  overflow: hidden;
}

.cartridge-label img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cartridge-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.1s;
}

.cartridge-item:hover .cartridge-overlay {
  opacity: 1;
}

.cartridge-play-btn {
  font-size: 24px;
  color: #ffffff;
}

.cartridge-queue-btn {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 28px;
  height: 28px;
  background: rgba(0, 0, 0, 0.8);
  color: #00f0ff;
  border: 1px solid #00f0ff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 2px;
  opacity: 0;
  transition: opacity 0.1s;
}

.cartridge-item:hover .cartridge-queue-btn {
  opacity: 1;
}

.cartridge-queue-btn:hover {
  background: #0088cc;
  color: #ffffff;
}

.preview-playing-indicator {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.85);
  border: 1px solid #00ff66;
  padding: 2px 4px;
  border-radius: 2px;
  font-family: var(--font-pixel);
  font-size: 6px;
  color: #00ff66;
}

.preview-playing-indicator::after {
  content: '♫ PREVIEW';
}

.cartridge-title-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  text-align: center;
  margin-top: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-shelf-message {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 10px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: #666666;
}
</style>
