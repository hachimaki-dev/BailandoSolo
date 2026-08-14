<template>
  <div class="panel library-archive-panel">
    <!-- Header Banner -->
    <div class="archive-hero-header">
      <div class="hero-left">
        <h2>📚 MI BIBLIOTECA</h2>
      </div>

      <div class="archive-metrics-strip">
        <div class="metric-item">
          <span class="metric-val">{{ allSongs.length }}</span>
          <span class="metric-lbl">PISTAS</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">{{ folders.length }}</span>
          <span class="metric-lbl">CASETES</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">{{ formatTotalDuration }}</span>
          <span class="metric-lbl">DURACIÓN</span>
        </div>
        <div class="metric-item">
          <span class="metric-val">{{ formatStorageSize }}</span>
          <span class="metric-lbl">TAMAÑO</span>
        </div>
      </div>
    </div>

    <!-- Shelves (Continuar escuchando & Agregado recientemente) -->
    <div v-if="recentPlayedSongs.length > 0 || newestSongs.length > 0" class="shelves-container">
      <!-- Shelf: Continuar Escuchando -->
      <div v-if="recentPlayedSongs.length > 0" class="shelf-section">
        <div class="shelf-header">
          <span class="shelf-title">🎧 CONTINUAR ESCUCHANDO</span>
        </div>
        <div class="shelf-items-scroll">
          <div 
            v-for="(song, idx) in recentPlayedSongs" 
            :key="song.path || idx" 
            class="shelf-cartridge"
            @click="playSong(song, idx, recentPlayedSongs)"
            @contextmenu.prevent="$emit('context-menu', { event: $event, song })"
          >
            <div class="shelf-art-box">
              <img :src="getThumbnail(song)" />
              <div class="shelf-play-overlay">▶</div>
            </div>
            <div class="shelf-song-name">{{ song.title }}</div>
            <div class="shelf-artist-name">{{ song.uploader || 'Desconocido' }}</div>
          </div>
        </div>
      </div>

      <!-- Shelf: Recientes -->
      <div v-if="newestSongs.length > 0" class="shelf-section">
        <div class="shelf-header">
          <span class="shelf-title">✨ RECIENTES</span>
        </div>
        <div class="shelf-items-scroll">
          <div 
            v-for="(song, idx) in newestSongs" 
            :key="song.path || idx" 
            class="shelf-cartridge"
            @click="playSong(song, idx, newestSongs)"
            @contextmenu.prevent="$emit('context-menu', { event: $event, song })"
          >
            <div class="shelf-art-box">
              <img :src="getThumbnail(song)" />
              <div class="shelf-play-overlay">▶</div>
            </div>
            <div class="shelf-song-name">{{ song.title }}</div>
            <div class="shelf-artist-name">{{ song.uploader || 'Desconocido' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Library Views Controller & Filter Bar -->
    <div class="archive-controls-bar">
      <!-- View Mode Tabs -->
      <div class="retro-tabs no-margin">
        <button 
          class="retro-tab-btn" 
          :class="{ active: viewMode === 'cassettes' }"
          @click="viewMode = 'cassettes'"
        >
          📼 Casetes ({{ folders.length }})
        </button>
        <button 
          class="retro-tab-btn" 
          :class="{ active: viewMode === 'table' }"
          @click="viewMode = 'table'"
        >
          📋 Canciones ({{ filteredSongs.length }})
        </button>
        <button 
          class="retro-tab-btn" 
          :class="{ active: viewMode === 'incomplete' }"
          @click="viewMode = 'incomplete'"
        >
          ⚠️ Sin Artista ({{ incompleteSongs.length }})
        </button>
      </div>

      <!-- Quick Search & Sort Filter -->
      <div class="archive-filter-tools">
        <input 
          v-model="localQuery" 
          type="text" 
          class="retro-input-compact" 
          placeholder="Filtrar colección..."
        />
        <select v-model="sortBy" class="retro-select-compact">
          <option value="name">Ordenar: Nombre</option>
          <option value="recent">Ordenar: Más recientes</option>
          <option value="size">Ordenar: Tamaño</option>
          <option value="artist">Ordenar: Artista</option>
        </select>
      </div>
    </div>

    <!-- VIEW 1: Cassettes Grid (Carpetas) -->
    <div v-if="viewMode === 'cassettes'" class="folder-grid">
      <div 
        v-for="folder in filteredFolders" 
        :key="folder.name" 
        class="cassette-folder" 
        @click="$emit('open-folder', folder.name)"
      >
        <div class="cassette-body" :style="folder.thumbnail ? { backgroundImage: `url(${getThumbnailUrl(folder.thumbnail)})` } : {}">
          <div class="cassette-overlay"></div>
          <div class="cassette-label">
            <div v-if="!folder.thumbnail" class="cassette-art-placeholder">
              <span>{{ folder.name.substring(0, 2).toUpperCase() }}</span>
            </div>
            <div class="cassette-title-strip">
              <span class="cassette-title">{{ folder.name }}</span>
            </div>
          </div>
          <div class="cassette-bottom">
            <div class="cassette-holes">
              <div class="hole left"></div>
              <div class="hole right"></div>
            </div>
            <div class="cassette-trapezoid"></div>
            <span class="cassette-count-tag">{{ folder.song_count || 0 }} 🎵</span>
          </div>
        </div>
      </div>
    </div>

    <!-- VIEW 2 & 3: Table View (Todas las canciones & Metadatos Incompletos) -->
    <div v-else class="retro-table-container archive-table-wrapper">
      <table class="retro-table">
        <thead>
          <tr>
            <th style="width: 36px;">#</th>
            <th style="width: 44px;">Carátula</th>
            <th>Título</th>
            <th>Artista</th>
            <th>Carpeta</th>
            <th style="width: 70px;">Formato</th>
            <th style="width: 90px;">Tamaño</th>
            <th style="text-align: right; width: 140px;">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="displayedSongs.length === 0">
            <td colspan="8" style="text-align: center; padding: 40px; color: #777;">
              No se encontraron canciones con los filtros actuales.
            </td>
          </tr>
          <tr 
            v-for="(song, idx) in displayedSongs" 
            :key="song.path || idx"
            @dblclick="playSong(song, idx, displayedSongs)"
            @contextmenu.prevent="$emit('context-menu', { event: $event, song })"
          >
            <td>{{ idx + 1 }}</td>
            <td>
              <img :src="getThumbnail(song)" class="table-song-thumb" />
            </td>
            <td>
              <div class="table-title-main">{{ song.title }}</div>
              <div v-if="!song.uploader || song.uploader === 'Desconocido'" class="incomplete-warning-pill">
                ⚠️ Sin artista identificado
              </div>
            </td>
            <td>{{ song.uploader || 'Desconocido' }}</td>
            <td><span class="badge-retro neutral">{{ song.folder || 'Archive' }}</span></td>
            <td><span class="badge-retro info pixel">{{ song.ext || 'MP3' }}</span></td>
            <td>{{ formatBytes(song.size) }}</td>
            <td style="text-align: right;" @click.stop>
              <button class="btn-retro-icon" @click="playSong(song, idx, displayedSongs)" title="Reproducir">▶</button>
              <button class="btn-retro-icon" @click="$emit('add-to-queue', song)" title="Agregar a la cola">＋</button>
              <button class="btn-retro-icon" @click="$emit('edit-metadata', song)" title="Editar metadatos">✎</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { LibraryService } from '../services/LibraryService'
import { streamUrl } from '../config'

const props = defineProps({
  folders: { type: Array, default: () => [] },
  allSongs: { type: Array, default: () => [] },
  statsData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['open-folder', 'play-song', 'add-to-queue', 'context-menu', 'edit-metadata'])

const viewMode = ref('cassettes') // 'cassettes', 'table', 'incomplete'
const localQuery = ref('')
const sortBy = ref('name')

const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23cccccc' width='48' height='48'/%3E%3C/svg%3E"

const getThumbnailUrl = (path) => {
  if (!path) return null
  return streamUrl(path)
}

const getThumbnail = (song) => {
  if (!song) return defaultThumb
  if (song.thumbnail) return streamUrl(song.thumbnail)
  const hash = song.title ? song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 1
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 MB'
  const mb = bytes / (1024 * 1024)
  return mb.toFixed(1) + ' MB'
}

const formatTotalDuration = computed(() => {
  // Estimate ~3.5 min per track if duration tag is missing
  const totalMinutes = props.allSongs.length * 3.5
  const hours = Math.floor(totalMinutes / 60)
  const mins = Math.floor(totalMinutes % 60)
  return `${hours}h ${mins}m`
})

const formatStorageSize = computed(() => {
  const totalBytes = props.allSongs.reduce((acc, s) => acc + (s.size || 0), 0)
  if (totalBytes > 1024 * 1024 * 1024) {
    return (totalBytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
  }
  return (totalBytes / (1024 * 1024)).toFixed(0) + ' MB'
})

// Continuar escuchando (Last played)
const recentPlayedSongs = computed(() => {
  const stats = props.statsData || {}
  const played = props.allSongs.filter(s => stats[s.filename]?.last_played)
  played.sort((a, b) => (stats[b.filename]?.last_played || 0) - (stats[a.filename]?.last_played || 0))
  return played.slice(0, 10)
})

// Agregado recientemente (Newest by mtime)
const newestSongs = computed(() => {
  const sorted = [...props.allSongs]
  sorted.sort((a, b) => (b.mtime || 0) - (a.mtime || 0))
  return sorted.slice(0, 10)
})

// Incomplete metadata songs
const incompleteSongs = computed(() => {
  return props.allSongs.filter(s => {
    const noArtist = !s.uploader || s.uploader === 'Desconocido'
    const isGenericTitle = s.title.toLowerCase().startsWith('video') || s.title.toLowerCase().startsWith('track')
    return noArtist || isGenericTitle
  })
})

const filteredFolders = computed(() => {
  const q = localQuery.value.trim().toLowerCase()
  if (!q) return props.folders
  return props.folders.filter(f => f.name.toLowerCase().includes(q))
})

const filteredSongs = computed(() => {
  const q = localQuery.value.trim().toLowerCase()
  let list = [...props.allSongs]

  if (q) {
    list = list.filter(s => (s.title || '').toLowerCase().includes(q) || (s.uploader || '').toLowerCase().includes(q) || (s.folder || '').toLowerCase().includes(q))
  }

  if (sortBy.value === 'name') {
    list.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
  } else if (sortBy.value === 'recent') {
    list.sort((a, b) => (b.mtime || 0) - (a.mtime || 0))
  } else if (sortBy.value === 'size') {
    list.sort((a, b) => (b.size || 0) - (a.size || 0))
  } else if (sortBy.value === 'artist') {
    list.sort((a, b) => (a.uploader || '').localeCompare(b.uploader || ''))
  }

  return list
})

const displayedSongs = computed(() => {
  if (viewMode.value === 'incomplete') {
    return incompleteSongs.value
  }
  return filteredSongs.value
})

const playSong = (song, index, list) => {
  emit('play-song', { song, index, list })
}
</script>

<style scoped>
.library-archive-panel {
  min-height: 540px;
}

.archive-hero-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 3px solid #000000;
}

.hero-left h2 {
  font-family: var(--font-pixel);
  font-size: 13px;
  margin: 0;
}

.hero-sub {
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #0077b6;
  margin-top: 2px;
  display: block;
}

.archive-metrics-strip {
  display: flex;
  gap: 12px;
  background: #d4d4d4;
  border: 2px solid #000000;
  padding: 6px 12px;
  box-shadow: inset 1px 1px 0px #ffffff;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-val {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: #000000;
}

.metric-lbl {
  font-family: var(--font-pixel);
  font-size: 6px;
  color: #555555;
  margin-top: 1px;
}

/* Shelves */
.shelves-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 18px;
}

.shelf-section {
  background: #dedede;
  border: 2px solid #000000;
  padding: 10px;
  box-shadow: inset 1px 1px 0px #ffffff, 2px 2px 0px #000000;
}

.shelf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.shelf-title {
  font-family: var(--font-pixel);
  font-size: 8px;
  color: #1a1a1a;
}

.shelf-items-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 6px;
}

.shelf-cartridge {
  width: 110px;
  flex-shrink: 0;
  background: #ffffff;
  border: 2px solid #000000;
  padding: 6px;
  cursor: pointer;
  box-shadow: 2px 2px 0px #000000;
  transition: transform 0.1s ease;
}

.shelf-cartridge:hover {
  transform: translateY(-3px);
  background: #e0f2fe;
}

.shelf-art-box {
  width: 100%;
  aspect-ratio: 1;
  background: #222222;
  border: 1px solid #000000;
  position: relative;
  overflow: hidden;
  margin-bottom: 4px;
}

.shelf-art-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.shelf-play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  opacity: 0;
  transition: opacity 0.1s;
}

.shelf-cartridge:hover .shelf-play-overlay {
  opacity: 1;
}

.shelf-song-name {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.shelf-artist-name {
  font-family: var(--font-mono);
  font-size: 9px;
  color: #666666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Controls Bar */
.archive-controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.no-margin {
  margin-bottom: 0;
}

.archive-filter-tools {
  display: flex;
  gap: 6px;
}

.retro-input-compact {
  padding: 6px 8px;
  background: #ffffff;
  border: 2px solid #000000;
  font-family: var(--font-mono);
  font-size: 11px;
}

.retro-select-compact {
  padding: 6px 8px;
  background: #ffffff;
  border: 2px solid #000000;
  font-family: var(--font-mono);
  font-size: 11px;
}

/* Cassette Grid & Styling */
.folder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  padding: 8px 0;
}

.cassette-folder {
  cursor: pointer;
  transition: transform 0.2s;
  width: 100%;
  aspect-ratio: 1.6;
  position: relative;
}

.cassette-folder:hover {
  transform: translateY(-4px) scale(1.02);
}

.cassette-body {
  width: 100%;
  height: 100%;
  background-color: #333;
  background-size: cover;
  background-position: center;
  border-radius: 6px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.8), 3px 3px 0px #000000;
  border: 2px solid #000000;
  position: relative;
  overflow: hidden;
}

.cassette-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  pointer-events: none;
  z-index: 1;
}

.cassette-label {
  flex: 1;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2px;
  z-index: 2;
}

.cassette-art-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-pixel);
  font-size: 20px;
  color: #ffffff;
}

.cassette-title-strip {
  position: absolute;
  top: 8px;
  left: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  padding: 3px 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transform: rotate(-1deg);
  border: 1px solid #333;
  z-index: 2;
}

.cassette-title {
  display: block;
  font-family: var(--font-mono);
  font-weight: bold;
  font-size: 10px;
  color: #000;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  text-transform: uppercase;
}

.cassette-bottom {
  height: 28%;
  position: relative;
  margin-top: 4px;
  z-index: 2;
}

.cassette-holes {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  display: flex;
  justify-content: space-between;
  z-index: 3;
}

.hole {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  border: 3px solid #000;
}

.cassette-trapezoid {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 100%;
  background: #2a2a2a;
  clip-path: polygon(10% 0, 90% 0, 100% 100%, 0% 100%);
  z-index: 1;
  border-top: 1px solid #444;
}

.cassette-count-tag {
  position: absolute;
  right: 2px;
  bottom: 2px;
  font-family: var(--font-mono);
  font-size: 8px;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.7);
  padding: 1px 4px;
  border-radius: 2px;
  z-index: 4;
}

/* Table View */
.archive-table-wrapper {
  max-height: 480px;
}

.table-song-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border: 1px solid #000000;
  display: block;
}

.table-title-main {
  font-weight: 700;
  font-size: 12px;
}

.incomplete-warning-pill {
  font-size: 9px;
  color: #b45309;
  font-weight: 600;
  margin-top: 2px;
}

@media (max-width: 800px) {
  .archive-hero-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}
</style>
