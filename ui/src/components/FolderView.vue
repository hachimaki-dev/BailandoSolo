<template>
  <div class="panel folder-view-panel">
    <!-- Top Action & Info Bar -->
    <div class="folder-header-bar">
      <div class="header-left">
        <button class="btn-retro-secondary" @click="$emit('back')">
          ← Volver al Archivo
        </button>
        <div class="folder-title-box">
          <h2>📁 {{ folderName }}</h2>
          <span class="folder-meta-pill">{{ songs.length }} CANCIONES · {{ folderTotalSize }}</span>
        </div>
      </div>

      <div class="header-right">
        <button 
          class="btn-retro-primary" 
          @click="playAll" 
          :disabled="songs.length === 0"
        >
          ▶ REPRODUCIR TODO
        </button>
      </div>
    </div>

    <!-- Filter within folder -->
    <div class="folder-filter-row">
      <input 
        v-model="query" 
        type="text" 
        class="retro-input" 
        placeholder="Filtrar canciones en esta carpeta..."
        style="max-width: 320px;"
      />
    </div>

    <!-- Songs Table -->
    <div class="retro-table-container folder-songs-container">
      <table class="retro-table">
        <thead>
          <tr>
            <th style="width: 36px;">#</th>
            <th style="width: 44px;">Carátula</th>
            <th>Título</th>
            <th>Artista</th>
            <th style="width: 70px;">Formato</th>
            <th style="width: 80px;">Tamaño</th>
            <th style="text-align: right; width: 140px;">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredSongs.length === 0">
            <td colspan="7" style="text-align: center; padding: 40px; color: #777;">
              {{ query ? 'No hay canciones que coincidan con la búsqueda' : 'Esta carpeta está vacía' }}
            </td>
          </tr>
          <tr 
            v-for="(song, index) in filteredSongs" 
            :key="song.path || index" 
            class="folder-song-row"
            @dblclick="playSong(song, index)"
            @contextmenu.prevent="$emit('context-menu', { event: $event, song })"
          >
            <td>{{ index + 1 }}</td>
            <td>
              <img :src="getThumbnail(song)" class="folder-thumb" />
            </td>
            <td style="font-weight: 700;">{{ song.title }}</td>
            <td>{{ song.uploader || 'Desconocido' }}</td>
            <td><span class="badge-retro info pixel">{{ song.ext || 'MP3' }}</span></td>
            <td>{{ formatBytes(song.size) }}</td>
            <td style="text-align: right;" @click.stop>
              <button class="btn-retro-icon" @click="playSong(song, index)" title="Reproducir">▶</button>
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
import { ref, computed, watch, onMounted } from 'vue'
import { LibraryService } from '../services/LibraryService'

const props = defineProps({
  folderName: String
})

const emit = defineEmits(['back', 'play-song', 'add-to-queue', 'context-menu', 'edit-metadata'])

const songs = ref([])
const query = ref('')
const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23cccccc' width='48' height='48'/%3E%3C/svg%3E"

const loadFolder = async () => {
  if (!props.folderName) return
  songs.value = await LibraryService.getFolderSongs(props.folderName)
}

const getThumbnail = (song) => {
  if (!song) return defaultThumb
  if (song.thumbnail) return LibraryService.getThumbnailUrl(song.thumbnail)
  const hash = song.title ? song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 1
  const coverNum = (hash % 9) + 1
  return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 MB'
  const mb = bytes / (1024 * 1024)
  return mb.toFixed(1) + ' MB'
}

const folderTotalSize = computed(() => {
  const total = songs.value.reduce((acc, s) => acc + (s.size || 0), 0)
  return formatBytes(total)
})

const filteredSongs = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return songs.value
  return songs.value.filter(s => (s.title || '').toLowerCase().includes(q) || (s.uploader || '').toLowerCase().includes(q))
})

const playSong = (song, index) => {
  emit('play-song', { song, index, list: filteredSongs.value })
}

const playAll = () => {
  if (filteredSongs.value.length > 0) {
    emit('play-song', { song: filteredSongs.value[0], index: 0, list: filteredSongs.value })
  }
}

watch(() => props.folderName, loadFolder)
onMounted(loadFolder)
</script>

<style scoped>
.folder-view-panel {
  min-height: 520px;
}

.folder-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 3px solid #000000;
  flex-wrap: wrap;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.folder-title-box h2 {
  font-family: var(--font-pixel);
  font-size: 13px;
  margin: 0;
}

.folder-meta-pill {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #0077b6;
  font-weight: 700;
  margin-top: 2px;
  display: block;
}

.folder-filter-row {
  margin-bottom: 12px;
}

.folder-songs-container {
  max-height: 480px;
}

.folder-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border: 1px solid #000000;
  display: block;
}
</style>
