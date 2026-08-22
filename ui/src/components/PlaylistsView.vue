<template>
  <div class="panel playlists-view">
    <!-- View Top Bar -->
    <div class="playlists-header">
      <div class="header-titles">
        <h2>📑 MIS PLAYLISTS</h2>
      </div>
      <div class="header-actions">
        <button class="btn-retro-secondary" @click="openCreateSmartModal">
          ✨ Lista Automática
        </button>
        <button class="btn-retro-primary" @click="openCreateModal">
          ＋ Nueva Playlist
        </button>
      </div>
    </div>

    <!-- Sub Navigation Tabs -->
    <div class="retro-tabs">
      <button 
        class="retro-tab-btn" 
        :class="{ active: activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        Todas ({{ playlists.length }})
      </button>
      <button 
        class="retro-tab-btn" 
        :class="{ active: activeTab === 'smart' }"
        @click="activeTab = 'smart'"
      >
        Automáticas ({{ smartCratesCount }})
      </button>
      <button 
        class="retro-tab-btn" 
        :class="{ active: activeTab === 'custom' }"
        @click="activeTab = 'custom'"
      >
        Creadas ({{ customPlaylistsCount }})
      </button>
    </div>

    <!-- Selected Playlist Detailed View -->
    <div v-if="selectedPlaylist" class="playlist-detail-container">
      <div class="detail-top-bar">
        <button class="btn-retro-secondary" @click="selectedPlaylist = null">
          ← Volver a Playlists
        </button>

        <div class="detail-info">
          <h3>{{ selectedPlaylist.name }}</h3>
          <span v-if="selectedPlaylist.type === 'smart'" class="badge-retro warning pixel">SMART CRATE</span>
          <span v-else class="badge-retro info pixel">PLAYLIST</span>
          <span class="detail-count">{{ getPlaylistSongs(selectedPlaylist).length }} canciones</span>
        </div>

        <div class="detail-actions">
          <button 
            v-if="selectedPlaylist.source_url" 
            class="btn-retro-secondary" 
            @click="syncExternalPlaylist(selectedPlaylist)"
            :disabled="isSyncing"
          >
            {{ isSyncing ? 'Comprobando...' : '🔄 Sincronizar' }}
          </button>
          <button 
            class="btn-retro-primary" 
            @click="playAllPlaylist(selectedPlaylist)"
            :disabled="getPlaylistSongs(selectedPlaylist).length === 0"
          >
            ▶ Reproducir Todo
          </button>
          <button 
            v-if="selectedPlaylist.id !== 'smart-top-spins' && selectedPlaylist.id !== 'smart-recent-vault'" 
            class="btn-retro-danger" 
            @click="deletePlaylist(selectedPlaylist)"
            title="Eliminar Playlist"
          >
            🗑
          </button>
        </div>
      </div>

      <!-- Playlist Songs List Table -->
      <div class="retro-table-container">
        <table class="retro-table">
          <thead>
            <tr>
              <th style="width: 40px;">#</th>
              <th>Título</th>
              <th>Artista</th>
              <th>Carpeta</th>
              <th style="text-align: right; width: 140px;">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="getPlaylistSongs(selectedPlaylist).length === 0">
              <td colspan="5" style="text-align: center; padding: 30px; color: #777;">
                No hay canciones en esta colección.
              </td>
            </tr>
            <tr 
              v-for="(song, idx) in getPlaylistSongs(selectedPlaylist)" 
              :key="song.path || idx"
              @dblclick="playSongAt(idx)"
              @contextmenu.prevent="$emit('context-menu', { event: $event, song })"
            >
              <td>{{ idx + 1 }}</td>
              <td style="font-weight: 600;">{{ song.title }}</td>
              <td>{{ song.uploader || 'Desconocido' }}</td>
              <td><span class="badge-retro neutral">{{ song.folder || 'Archive' }}</span></td>
              <td style="text-align: right;">
                <button class="btn-retro-icon" @click.stop="playSongAt(idx)" title="Reproducir">▶</button>
                <button class="btn-retro-icon" @click.stop="$emit('add-to-queue', song)" title="Agregar a la cola">＋</button>
                <button 
                  v-if="selectedPlaylist.type !== 'smart'" 
                  class="btn-retro-icon" 
                  @click.stop="removeSongFromCurrent(song, idx)" 
                  title="Quitar de playlist"
                >
                  ✕
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Playlists Cards Grid -->
    <div v-else class="playlists-grid">
      <div 
        v-for="pl in displayedPlaylists" 
        :key="pl.id" 
        class="playlist-card"
        :class="{ 'is-smart': pl.type === 'smart' }"
        @click="selectPlaylist(pl)"
      >
        <!-- Crate Header / Type Badge -->
        <div class="crate-top">
          <span v-if="pl.type === 'smart'" class="badge-retro warning pixel">SMART CRATE</span>
          <span v-else class="badge-retro info pixel">PLAYLIST</span>
          <span class="crate-song-counter">{{ getPlaylistSongs(pl).length }} 🎵</span>
        </div>

        <!-- Crate Body / Name -->
        <div class="crate-center">
          <div class="crate-icon">{{ pl.type === 'smart' ? '📦' : '📼' }}</div>
          <div class="crate-name">{{ pl.name }}</div>
          <div class="crate-desc">{{ pl.description || 'Colección de canciones' }}</div>
        </div>

        <!-- Crate Footer -->
        <div class="crate-footer">
          <button class="btn-retro-primary btn-sm" @click.stop="playAllPlaylist(pl)">
            ▶ Play
          </button>
          <button class="btn-retro-secondary btn-sm" @click.stop="selectPlaylist(pl)">
            Ver Lista →
          </button>
        </div>
      </div>
    </div>

    <!-- Create Playlist Modal -->
    <div v-if="showCreateModal" class="retro-modal-overlay" @click="showCreateModal = false">
      <div class="retro-modal-box" @click.stop style="max-width: 440px;">
        <div class="retro-modal-header">
          <h3>＋ NUEVA PLAYLIST</h3>
          <button class="btn-retro-icon" @click="showCreateModal = false">✕</button>
        </div>
        <form @submit.prevent="createPlaylist">
          <div class="input-group">
            <label>Nombre de la Playlist</label>
            <input v-model="newPlName" type="text" class="retro-input" required placeholder="Ej. Favoritas del 2000" />
          </div>
          <div class="input-group">
            <label>Descripción (Opcional)</label>
            <input v-model="newPlDesc" type="text" class="retro-input" placeholder="Breve nota sobre la colección" />
          </div>
          <div class="input-group">
            <label>URL de Origen YouTube (Opcional para sincronización)</label>
            <input v-model="newPlSourceUrl" type="text" class="retro-input" placeholder="https://youtube.com/playlist?list=..." />
          </div>
          <div class="modal-footer-actions">
            <button type="button" class="btn-retro-secondary" @click="showCreateModal = false">Cancelar</button>
            <button type="submit" class="btn-retro-primary">Crear Playlist ✓</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Smart Crate Modal -->
    <div v-if="showSmartModal" class="retro-modal-overlay" @click="showSmartModal = false">
      <div class="retro-modal-box" @click.stop style="max-width: 500px;">
        <div class="retro-modal-header">
          <h3>✨ NUEVA SMART CRATE</h3>
          <button class="btn-retro-icon" @click="showSmartModal = false">✕</button>
        </div>
        <form @submit.prevent="createSmartCrate">
          <div class="input-group">
            <label>Nombre de la Smart Crate</label>
            <input v-model="smartForm.name" type="text" class="retro-input" required placeholder="Ej. Rock Clásico (> 3 plays)" />
          </div>
          <div class="input-group">
            <label>Regla de Selección Dinámica</label>
            <select v-model="smartForm.ruleType" class="retro-select" style="width: 100%; padding: 8px; font-family: var(--font-mono); margin-bottom: 8px;">
              <option value="top_plays">Más reproducidas (Top N)</option>
              <option value="zero_plays">Bóveda (0 reproducciones)</option>
              <option value="min_plays">Mínimo N reproducciones</option>
              <option value="recent_days">Agregadas en los últimos N días</option>
              <option value="artist_match">Filtrar por nombre de Artista</option>
            </select>
          </div>
          <div v-if="smartForm.ruleType === 'top_plays' || smartForm.ruleType === 'min_plays' || smartForm.ruleType === 'recent_days'" class="input-group">
            <label>Valor Numérico (N)</label>
            <input v-model.number="smartForm.numberVal" type="number" min="1" class="retro-input" required />
          </div>
          <div v-if="smartForm.ruleType === 'artist_match'" class="input-group">
            <label>Texto del Artista</label>
            <input v-model="smartForm.textVal" type="text" class="retro-input" required placeholder="Ej. Daft Punk" />
          </div>
          <div class="modal-footer-actions">
            <button type="button" class="btn-retro-secondary" @click="showSmartModal = false">Cancelar</button>
            <button type="submit" class="btn-retro-primary">Crear Smart Crate ✨</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { PlaylistService } from '../services/PlaylistService'

const props = defineProps({
  allSongs: { type: Array, default: () => [] },
  statsData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['play-song', 'add-to-queue', 'context-menu', 'sync-playlist'])

const playlists = ref([])
const activeTab = ref('all')
const selectedPlaylist = ref(null)
const isSyncing = ref(false)

watch([selectedPlaylist, activeTab], () => {
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }
})

// Create Modals
const showCreateModal = ref(false)
const newPlName = ref('')
const newPlDesc = ref('')
const newPlSourceUrl = ref('')

const showSmartModal = ref(false)
const smartForm = ref({
  name: '',
  ruleType: 'top_plays',
  numberVal: 20,
  textVal: ''
})

const loadPlaylists = async () => {
  playlists.value = await PlaylistService.getPlaylists()
}

onMounted(() => {
  loadPlaylists()
})

const smartCratesCount = computed(() => playlists.value.filter(p => p.type === 'smart').length)
const customPlaylistsCount = computed(() => playlists.value.filter(p => p.type !== 'smart').length)

const displayedPlaylists = computed(() => {
  if (activeTab.value === 'smart') {
    return playlists.value.filter(p => p.type === 'smart')
  } else if (activeTab.value === 'custom') {
    return playlists.value.filter(p => p.type !== 'smart')
  }
  return playlists.value
})

const getPlaylistSongs = (pl) => {
  if (!pl) return []
  if (pl.type === 'smart') {
    return PlaylistService.evaluateSmartCrate(pl.rule, props.allSongs, props.statsData)
  }
  return pl.songs || []
}

const selectPlaylist = (pl) => {
  selectedPlaylist.value = pl
}

const playAllPlaylist = (pl) => {
  const songs = getPlaylistSongs(pl)
  if (songs.length > 0) {
    emit('play-song', { song: songs[0], index: 0, list: songs })
  }
}

const playSongAt = (index) => {
  const songs = getPlaylistSongs(selectedPlaylist.value)
  if (songs[index]) {
    emit('play-song', { song: songs[index], index, list: songs })
  }
}

const removeSongFromCurrent = async (song, index) => {
  if (!selectedPlaylist.value || selectedPlaylist.value.type === 'smart') return
  try {
    const updated = await PlaylistService.removeSongFromPlaylist(selectedPlaylist.value.id, song.path, index)
    selectedPlaylist.value = updated
    await loadPlaylists()
  } catch (e) {
    alert(e.message)
  }
}

const deletePlaylist = async (pl) => {
  if (!confirm(`¿Eliminar la playlist "${pl.name}"?`)) return
  try {
    await PlaylistService.deletePlaylist(pl.id)
    selectedPlaylist.value = null
    await loadPlaylists()
  } catch (e) {
    alert(e.message)
  }
}

const openCreateModal = () => {
  newPlName.value = ''
  newPlDesc.value = ''
  newPlSourceUrl.value = ''
  showCreateModal.value = true
}

const createPlaylist = async () => {
  try {
    await PlaylistService.createPlaylist({
      name: newPlName.value,
      description: newPlDesc.value,
      source_url: newPlSourceUrl.value,
      type: 'custom',
      songs: []
    })
    showCreateModal.value = false
    await loadPlaylists()
  } catch (e) {
    alert(e.message)
  }
}

const openCreateSmartModal = () => {
  smartForm.value = {
    name: '',
    ruleType: 'top_plays',
    numberVal: 20,
    textVal: ''
  }
  showSmartModal.value = true
}

const createSmartCrate = async () => {
  let rule = {}
  if (smartForm.value.ruleType === 'top_plays') {
    rule = { field: 'plays', operator: 'top', value: smartForm.value.numberVal }
  } else if (smartForm.value.ruleType === 'zero_plays') {
    rule = { field: 'plays', operator: 'eq', value: 0 }
  } else if (smartForm.value.ruleType === 'min_plays') {
    rule = { field: 'plays', operator: 'gt', value: smartForm.value.numberVal }
  } else if (smartForm.value.ruleType === 'recent_days') {
    rule = { field: 'mtime', operator: 'days_ago', value: smartForm.value.numberVal }
  } else if (smartForm.value.ruleType === 'artist_match') {
    rule = { field: 'artist', operator: 'contains', value: smartForm.value.textVal }
  }

  try {
    await PlaylistService.createPlaylist({
      name: smartForm.value.name,
      description: `Smart Crate: ${smartForm.value.ruleType}`,
      type: 'smart',
      rule
    })
    showSmartModal.value = false
    await loadPlaylists()
  } catch (e) {
    alert(e.message)
  }
}

const syncExternalPlaylist = (pl) => {
  emit('sync-playlist', pl)
}
</script>

<style scoped>
.playlists-view {
  min-height: 520px;
}

.playlists-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-titles h2 {
  font-family: var(--font-pixel);
  font-size: 13px;
  margin: 0;
}

.header-sub {
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #0077b6;
  margin-top: 2px;
  display: block;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  padding: 10px 0;
}

.playlist-card {
  background: #d4d4d4;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #ffffff, inset -1px -1px 0px #777777, 4px 4px 0px #000000;
  padding: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.1s ease;
  min-height: 160px;
}

.playlist-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: inset 1px 1px 0px #ffffff, inset -1px -1px 0px #777777, 6px 6px 0px #000000;
}

.playlist-card.is-smart {
  background: linear-gradient(135deg, #e8e8e8 0%, #d4e0e8 100%);
  border-color: #005588;
}

.crate-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.crate-song-counter {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: bold;
}

.crate-center {
  text-align: center;
  padding: 10px 0;
}

.crate-icon {
  font-size: 28px;
  margin-bottom: 6px;
}

.crate-name {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  color: #111111;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crate-desc {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #555555;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crate-footer {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  border-top: 1px solid #aaaaaa;
  padding-top: 8px;
}

/* Detail View */
.playlist-detail-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #d4d4d4;
  padding: 10px 14px;
  border: 2px solid #000000;
}

.detail-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-info h3 {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: bold;
}

.detail-count {
  font-family: var(--font-mono);
  font-size: 12px;
  color: #555555;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.retro-input {
  width: 100%;
  padding: 8px;
  background: #ffffff;
  border: 2px solid #000000;
  font-family: var(--font-mono);
}

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}
</style>
