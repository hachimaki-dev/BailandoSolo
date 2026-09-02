<template>
  <div class="panel plaza-view">
    <!-- Top Console Header -->
    <div class="plaza-console-header">
      <div class="header-left">
        <div class="title-group">
          <span class="led-dot led-blue"></span>
          <h2>🌐 LA PLAZA</h2>
          <span class="p2p-status-pill" :class="{ connected: relayStatus.connected > 0 }">
            <span class="status-indicator-dot"></span>
            NOSTR P2P ({{ relayStatus.connected }}/{{ relayStatus.total }})
          </span>
        </div>
      </div>

      <div class="header-right">
        <!-- Search bar -->
        <div class="plaza-search-wrap">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Buscar playlist, canción o curador..." 
            class="retro-input-compact search-input"
          />
          <button v-if="searchQuery" class="btn-clear" @click="searchQuery = ''">✕</button>
        </div>

        <!-- User Identity Chip -->
        <button class="user-chip-btn" @click="openConfigModal" title="Editar mi alias en La Plaza">
          <span class="chip-avatar" :style="{ backgroundColor: identity.avatarColor }">
            {{ identity.alias.charAt(0).toUpperCase() }}
          </span>
          <span class="chip-name">{{ identity.alias }}</span>
          <span class="chip-edit-icon">✎</span>
        </button>

        <!-- Share Button -->
        <button class="btn-retro-primary btn-publish-header" @click="showShareModal = true">
          ＋ Publicar Playlist
        </button>
      </div>
    </div>

    <!-- Active Peers / Live Community Tape (En Sintonía) -->
    <div class="social-tape-section">
      <div class="tape-label-bar">
        <span class="tape-title">📡 EN SINTONÍA ({{ activeUsers.length }})</span>
        <span class="tape-sub">Comunidad activa en vivo</span>
      </div>

      <div class="social-peers-ribbon">
        <div 
          v-for="user in activeUsers" 
          :key="user.pubkey"
          class="social-peer-card"
          :class="{ 'is-me': user.pubkey === identity.pubkey, 'is-selected': userFilter === user.alias }"
          @click="toggleUserFilter(user.alias)"
          :title="`Filtrar playlists de ${user.alias}`"
        >
          <div class="peer-avatar" :style="{ backgroundColor: user.avatarColor }">
            {{ (user.alias || '?').charAt(0).toUpperCase() }}
            <span class="peer-online-led" :class="{ 'playing': user.isPlaying }"></span>
          </div>

          <div class="peer-details">
            <div class="peer-header-line">
              <span class="peer-handle">{{ user.alias }}</span>
              <span v-if="user.pubkey === identity.pubkey" class="tag-me">TÚ</span>
            </div>

            <!-- Listening status -->
            <div v-if="user.isPlaying && user.currentSong" class="peer-playing-status">
              <span class="mini-eq">
                <span></span><span></span><span></span>
              </span>
              <span class="now-playing-title" :title="`${user.currentSong.title} - ${user.currentSong.artist}`">
                {{ user.currentSong.title }}
              </span>
            </div>
            <div v-else class="peer-idle-status">
              <span>En sintonía</span>
            </div>
          </div>

          <div class="peer-badge-count" title="Playlists compartidas">
            {{ getUserPlaylistsCount(user.alias) }} 📼
          </div>
        </div>
      </div>
    </div>

    <!-- Controls & View Mode Bar -->
    <div class="catalog-controls-bar">
      <!-- Filter Tabs -->
      <div class="retro-tabs">
        <button 
          class="retro-tab-btn" 
          :class="{ active: sortBy === 'popular' && !userFilter && !showOnlyMine }"
          @click="setTab('popular')"
        >
          🔥 Populares
        </button>
        <button 
          class="retro-tab-btn" 
          :class="{ active: sortBy === 'recent' && !userFilter && !showOnlyMine }"
          @click="setTab('recent')"
        >
          ⚡ Recientes
        </button>
        <button 
          class="retro-tab-btn" 
          :class="{ active: sortBy === 'tracks' && !userFilter && !showOnlyMine }"
          @click="setTab('tracks')"
        >
          📼 Más Pistas
        </button>
        <button 
          class="retro-tab-btn" 
          :class="{ active: showOnlyMine }"
          @click="toggleOnlyMine"
        >
          💾 Mis Aportes
        </button>
      </div>

      <!-- Right controls: Density Switcher & Count -->
      <div class="view-mode-controls">
        <span class="catalog-counter">{{ filteredPlaylists.length }} listas</span>
        <div class="density-toggles">
          <button 
            class="btn-density" 
            :class="{ active: viewMode === 'table' }"
            @click="viewMode = 'table'"
            title="Vista Lista Densa (ideal para muchas playlists)"
          >
            ☰ Lista
          </button>
          <button 
            class="btn-density" 
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="Vista Fichas"
          >
            ⊞ Fichas
          </button>
        </div>
      </div>
    </div>

    <!-- Active Filter Notice (if filtering by user) -->
    <div v-if="userFilter" class="active-filter-alert">
      <span>Filtrando curador: <strong>{{ userFilter }}</strong> ({{ filteredPlaylists.length }} encontradas)</span>
      <button class="btn-clear-curator-filter" @click="userFilter = ''">Mostrar todas ✕</button>
    </div>

    <!-- ─── CATALOG: MODE A — DENSE LIST (DEFAULT) ────────────────────────── -->
    <div v-if="viewMode === 'table' && filteredPlaylists.length > 0" class="dense-catalog-container">
      <div 
        v-for="pl in filteredPlaylists" 
        :key="pl.id"
        class="dense-row-wrapper"
        :class="{ expanded: expandedPlaylistId === pl.id }"
      >
        <div class="dense-playlist-row" @click="toggleExpand(pl.id)">
          <!-- Col 1: Expand caret & Title -->
          <div class="col-title-section">
            <span class="expand-caret">{{ expandedPlaylistId === pl.id ? '▼' : '▶' }}</span>
            <div class="title-meta-wrap">
              <span class="dense-playlist-title">{{ pl.title }}</span>
              <span class="dense-yt-url" :title="pl.url">{{ pl.url }}</span>
            </div>
          </div>

          <!-- Col 2: Curator -->
          <div class="col-curator-section" @click.stop="toggleUserFilter(pl.author)">
            <span class="dense-curator-avatar" :style="{ backgroundColor: pl.avatarColor }">
              {{ pl.author.charAt(0).toUpperCase() }}
            </span>
            <span class="dense-curator-name">{{ pl.author }}</span>
          </div>

          <!-- Col 3: Tracks & Downloads stats -->
          <div class="col-stats-section">
            <span class="dense-stat-chip">🎵 {{ pl.songs ? pl.songs.length : 0 }}</span>
            <span class="dense-stat-chip dl">📥 {{ pl.downloads || 0 }}</span>
            <span class="dense-date">{{ formatDate(pl.createdAt) }}</span>
          </div>

          <!-- Col 4: Action Buttons -->
          <div class="col-actions-section" @click.stop>
            <button 
              class="btn-retro-secondary btn-sm btn-icon-dense" 
              @click="copyUrl(pl.url, pl.id)" 
              :title="copiedId === pl.id ? 'Copiada' : 'Copiar URL'"
            >
              {{ copiedId === pl.id ? '✓' : '📋' }}
            </button>
            <button 
              class="btn-retro-primary btn-sm btn-download-dense" 
              @click="triggerDownload(pl)"
              title="Cargar y descargar en Bailando Solo"
            >
              ⚡ Descargar
            </button>
          </div>
        </div>

        <!-- Inline Expandable Tracklist (Accordion) -->
        <div v-if="expandedPlaylistId === pl.id" class="dense-inline-tracks">
          <div class="tracks-inner-header">
            <strong>Pistas de la lista ({{ pl.songs?.length || 0 }} canciones):</strong>
            <button class="btn-retro-secondary btn-sm" @click="copyUrl(pl.url, pl.id)">
              Copiar URL de YouTube
            </button>
          </div>

          <div class="tracks-table-wrap">
            <table class="tracks-table">
              <thead>
                <tr>
                  <th style="width: 36px">#</th>
                  <th>Canción</th>
                  <th>Canal / Artista</th>
                  <th style="width: 70px; text-align: right;">Duración</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(song, sIdx) in pl.songs" :key="sIdx">
                  <td class="idx-col">{{ sIdx + 1 }}</td>
                  <td class="name-col"><strong>{{ song.title }}</strong></td>
                  <td class="uploader-col">{{ song.uploader || 'YouTube' }}</td>
                  <td class="dur-col">{{ formatDuration(song.duration) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── CATALOG: MODE B — RETRO GRID CARDS ───────────────────────────── -->
    <div v-else-if="viewMode === 'grid' && filteredPlaylists.length > 0" class="grid-catalog-container">
      <div 
        v-for="pl in filteredPlaylists" 
        :key="pl.id"
        class="retro-card-item"
      >
        <div class="card-top-meta">
          <div class="curator-badge-clean" @click="toggleUserFilter(pl.author)">
            <span class="curator-dot" :style="{ backgroundColor: pl.avatarColor }"></span>
            <span class="curator-name-label">{{ pl.author }}</span>
          </div>
          <div class="card-counts">
            <span class="card-tag">🎵 {{ pl.songs ? pl.songs.length : 0 }}</span>
            <span class="card-tag dl">📥 {{ pl.downloads || 0 }}</span>
          </div>
        </div>

        <div class="card-main-content">
          <h3 class="card-title" :title="pl.title">{{ pl.title }}</h3>
          <span class="card-date-line">{{ formatDate(pl.createdAt) }}</span>
          
          <div class="card-url-bar" :title="pl.url">
            {{ pl.url }}
          </div>

          <!-- Mini 3-tracks snippet -->
          <div class="card-songs-snippet">
            <div 
              v-for="(s, idx) in (pl.songs || []).slice(0, 3)" 
              :key="idx" 
              class="snippet-row"
            >
              <span class="snippet-num">{{ idx + 1 }}.</span>
              <span class="snippet-title">{{ s.title }}</span>
            </div>
            <div v-if="pl.songs && pl.songs.length > 3" class="snippet-more">
              + {{ pl.songs.length - 3 }} temas más
            </div>
          </div>
        </div>

        <div class="card-action-bar">
          <button 
            class="btn-retro-secondary btn-sm" 
            @click="copyUrl(pl.url, pl.id)"
          >
            {{ copiedId === pl.id ? '✓ Copiada' : '📋 URL' }}
          </button>
          <button 
            class="btn-retro-primary btn-sm btn-dl-card" 
            @click="triggerDownload(pl)"
          >
            ⚡ Descargar
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="catalog-empty-state">
      <div class="empty-cassette-icon">📻</div>
      <h3>La Plaza está vacía</h3>
      <p v-if="searchQuery">Sin resultados para "{{ searchQuery }}".</p>
      <p v-else-if="userFilter">El usuario {{ userFilter }} no tiene listas registradas.</p>
      <p v-else>Aún no hay playlists compartidas por usuarios en la red. Puedes publicar una URL con el botón de arriba o marcar la casilla de compartir al descargar.</p>
      <button class="btn-retro-primary" @click="showShareModal = true">
        ＋ Publicar una Playlist
      </button>
    </div>

    <!-- ─── MODAL: COMPARTIR PLAYLIST MANUALMENTE ──────────────────────────── -->
    <div v-if="showShareModal" class="retro-modal-overlay" @click="showShareModal = false">
      <div class="retro-modal-box plaza-modal-compact" @click.stop>
        <div class="retro-modal-header">
          <div class="header-title-left">
            <span class="led-dot led-green"></span>
            <h3>COMPARTIR PLAYLIST</h3>
          </div>
          <button class="btn-retro-icon btn-close-modal" @click="showShareModal = false">✕</button>
        </div>

        <div class="modal-form-body">
          <div class="form-group">
            <label>TÍTULO DE LA LISTA</label>
            <input 
              type="text" 
              v-model="newPlaylistTitle" 
              placeholder="Ej: Grandes Éxitos Rock 80s" 
              class="retro-input"
            />
          </div>

          <div class="form-group">
            <label>URL DE YOUTUBE (PLAYLIST)</label>
            <input 
              type="text" 
              v-model="newPlaylistUrl" 
              placeholder="https://www.youtube.com/playlist?list=..." 
              class="retro-input"
            />
          </div>

          <div class="form-group">
            <label>CURADOR / ALIAS</label>
            <input 
              type="text" 
              v-model="newPlaylistAuthor" 
              :placeholder="identity.alias" 
              class="retro-input"
            />
          </div>

          <div class="modal-button-footer">
            <button class="btn-retro-secondary" @click="showShareModal = false">Cancelar</button>
            <button 
              class="btn-retro-primary" 
              :disabled="!newPlaylistUrl.trim() || !newPlaylistTitle.trim() || isPublishing"
              @click="handleManualPublish"
            >
              {{ isPublishing ? 'Publicando...' : 'Publicar en La Plaza' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── MODAL: CONFIGURACIÓN DE IDENTIDAD ─────────────────────────────── -->
    <div v-if="showConfigModal" class="retro-modal-overlay" @click="showConfigModal = false">
      <div class="retro-modal-box plaza-modal-compact" @click.stop>
        <div class="retro-modal-header">
          <div class="header-title-left">
            <span class="led-dot led-blue"></span>
            <h3>MI IDENTIDAD EN LA PLAZA</h3>
          </div>
          <button class="btn-retro-icon btn-close-modal" @click="showConfigModal = false">✕</button>
        </div>

        <div class="modal-form-body">
          <div class="form-group">
            <label>ALIAS PÚBLICO</label>
            <div class="alias-action-row">
              <input 
                type="text" 
                v-model="tempAlias" 
                class="retro-input" 
                placeholder="Nombre de usuario"
              />
              <button class="btn-retro-primary btn-sm" @click="saveAlias">Guardar</button>
            </div>
          </div>

          <div class="form-group">
            <label class="clean-checkbox-label">
              <input type="checkbox" v-model="autoShareOption" @change="toggleAutoShare" />
              <span>Compartir automáticamente mis descargas en La Plaza</span>
            </label>
          </div>

          <div class="relays-info-box">
            <span class="relays-info-title">RED NOSTR P2P (RELAYS CONECTADOS):</span>
            <div class="relay-row" v-for="r in PlazaService.relays" :key="r">
              <span class="relay-led">●</span>
              <code>{{ r }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { PlazaService } from '../services/PlazaService'

const emit = defineEmits(['download-playlist', 'navigate'])

// State
const playlists = ref([])
const activeUsers = ref([])
const relayStatus = ref({ connected: 0, total: 4 })
const identity = ref({ alias: 'BailandoDJ', pubkey: '', avatarColor: '#00f0ff' })

const searchQuery = ref('')
const sortBy = ref('popular') // 'popular' | 'recent' | 'tracks'
const userFilter = ref('')
const showOnlyMine = ref(false)
const viewMode = ref('table') // 'table' | 'grid'
const expandedPlaylistId = ref(null)
const copiedId = ref(null)

// Modals
const showShareModal = ref(false)
const showConfigModal = ref(false)
const isPublishing = ref(false)

const newPlaylistTitle = ref('')
const newPlaylistUrl = ref('')
const newPlaylistAuthor = ref('')
const tempAlias = ref('')
const autoShareOption = ref(false)

// Listener unbinders
let unbindPlaylists = null
let unbindPresence = null
let unbindRelays = null

onMounted(async () => {
  await PlazaService.init()

  identity.value = PlazaService.getIdentity()
  tempAlias.value = identity.value.alias
  autoShareOption.value = identity.value.isAutoShareEnabled

  unbindPlaylists = PlazaService.onPlaylists((list) => {
    playlists.value = list
  })

  unbindPresence = PlazaService.onPresence((users) => {
    activeUsers.value = users
  })

  unbindRelays = PlazaService.onRelayStatus((status) => {
    relayStatus.value = status
  })
})

onUnmounted(() => {
  if (unbindPlaylists) unbindPlaylists()
  if (unbindPresence) unbindPresence()
  if (unbindRelays) unbindRelays()
})

// ─── Computed Catalog ────────────────────────────────────────────────────────

const filteredPlaylists = computed(() => {
  let list = [...playlists.value]

  // Filter by user
  if (userFilter.value) {
    list = list.filter(p => (p.author || '').toLowerCase() === userFilter.value.toLowerCase())
  } else if (showOnlyMine.value) {
    list = list.filter(p => (p.author || '').toLowerCase() === identity.value.alias.toLowerCase() || p.pubkey === identity.value.pubkey)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p => {
      const matchTitle = (p.title || '').toLowerCase().includes(q)
      const matchAuthor = (p.author || '').toLowerCase().includes(q)
      const matchSongs = (p.songs || []).some(s => 
        (s.title && s.title.toLowerCase().includes(q)) || 
        (s.uploader && s.uploader.toLowerCase().includes(q))
      )
      return matchTitle || matchAuthor || matchSongs
    })
  }

  // Sorting
  if (sortBy.value === 'popular') {
    list.sort((a, b) => (b.downloads || 0) - (a.downloads || 0))
  } else if (sortBy.value === 'recent') {
    list.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0))
  } else if (sortBy.value === 'tracks') {
    list.sort((a, b) => ((b.songs?.length) || 0) - ((a.songs?.length) || 0))
  }

  return list
})

const getUserPlaylistsCount = (author) => {
  if (!author) return 0
  return playlists.value.filter(p => (p.author || '').toLowerCase() === author.toLowerCase()).length
}

// ─── Actions ─────────────────────────────────────────────────────────────────

const setTab = (sortKey) => {
  sortBy.value = sortKey
  userFilter.value = ''
  showOnlyMine.value = false
}

const toggleOnlyMine = () => {
  showOnlyMine.value = !showOnlyMine.value
  userFilter.value = ''
}

const toggleUserFilter = (author) => {
  if (userFilter.value === author) {
    userFilter.value = ''
  } else {
    userFilter.value = author
    showOnlyMine.value = false
  }
}

const toggleExpand = (plId) => {
  if (expandedPlaylistId.value === plId) {
    expandedPlaylistId.value = null
  } else {
    expandedPlaylistId.value = plId
  }
}

const copyUrl = (url, id) => {
  navigator.clipboard.writeText(url).then(() => {
    copiedId.value = id
    setTimeout(() => {
      if (copiedId.value === id) copiedId.value = null
    }, 2000)
  })
}

const triggerDownload = (pl) => {
  emit('download-playlist', pl)
}

const openConfigModal = () => {
  tempAlias.value = identity.value.alias
  showConfigModal.value = true
}

const saveAlias = () => {
  PlazaService.setAlias(tempAlias.value)
  identity.value = PlazaService.getIdentity()
  showConfigModal.value = false
}

const toggleAutoShare = () => {
  PlazaService.setAutoShare(autoShareOption.value)
  identity.value = PlazaService.getIdentity()
}

const handleManualPublish = async () => {
  if (!newPlaylistUrl.value.trim() || !newPlaylistTitle.value.trim()) return
  isPublishing.value = true

  try {
    await PlazaService.publishPlaylist({
      title: newPlaylistTitle.value.trim(),
      url: newPlaylistUrl.value.trim(),
      author: newPlaylistAuthor.value.trim() || identity.value.alias,
      songs: []
    })

    showShareModal.value = false
    newPlaylistTitle.value = ''
    newPlaylistUrl.value = ''
  } catch (e) {
    alert('Error al publicar: ' + e.message)
  } finally {
    isPublishing.value = false
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

const formatDate = (timestamp) => {
  if (!timestamp) return 'Reciente'
  const diff = Date.now() - timestamp
  const hours = Math.floor(diff / (1000 * 60 * 60))
  if (hours < 1) return 'Reciente'
  if (hours < 24) return `${hours}h`
  const days = Math.floor(hours / 24)
  if (days === 1) return 'Ayer'
  return `${days}d`
}
</script>

<style scoped>
.plaza-view {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.1rem;
  height: 100%;
  overflow-y: auto;
}

/* ─── Header ───────────────────────────────────────────────────────────────── */
.plaza-console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--border-color, #000);
  padding-bottom: 0.75rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.title-group h2 {
  font-family: var(--font-retro, var(--font-pixel, monospace));
  font-size: 1.05rem;
  margin: 0;
  letter-spacing: 0.5px;
}

.p2p-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  font-family: monospace;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color, #888);
  color: var(--text-secondary, #666);
}

.p2p-status-pill.connected {
  color: #00aa44;
  border-color: rgba(0, 170, 68, 0.4);
  background: rgba(0, 170, 68, 0.08);
}

.status-indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00aa44;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.plaza-search-wrap {
  position: relative;
  width: 220px;
}

.search-icon {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  color: #888;
}

.search-input {
  width: 100%;
  padding-left: 1.7rem;
  padding-right: 1.5rem;
  font-size: 0.75rem;
}

.btn-clear {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #888;
  font-size: 0.7rem;
}

.user-chip-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.6rem;
  background: var(--card-bg, #eee);
  border: 1px solid var(--border-color, #999);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: bold;
  color: var(--text-primary, inherit);
}

.user-chip-btn:hover {
  border-color: var(--accent-primary, #00f0ff);
}

.chip-avatar {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 900;
}

.chip-edit-icon {
  font-size: 0.7rem;
  color: #888;
}

.btn-publish-header {
  font-size: 0.75rem;
  padding: 0.35rem 0.75rem;
}

/* ─── Social Ribbon (En Sintonía) ──────────────────────────────────────────── */
.social-tape-section {
  background: var(--card-bg, rgba(0, 0, 0, 0.05));
  border: 1px solid var(--border-color, #bbb);
  border-radius: 5px;
  padding: 0.6rem 0.8rem;
}

.tape-label-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.72rem;
}

.tape-title {
  font-weight: bold;
  font-family: var(--font-retro, monospace);
  color: var(--accent-primary, inherit);
}

.tape-sub {
  color: var(--text-secondary, #777);
  font-size: 0.7rem;
}

.social-peers-ribbon {
  display: flex;
  gap: 0.6rem;
  overflow-x: auto;
  padding-bottom: 0.3rem;
}

.social-peer-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  padding: 0.35rem 0.6rem;
  min-width: 190px;
  max-width: 240px;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.15s ease;
}

.social-peer-card:hover {
  border-color: var(--accent-primary, #00aa44);
  background: rgba(0, 0, 0, 0.1);
}

.social-peer-card.is-me {
  border-color: #f59e0b;
}

.social-peer-card.is-selected {
  border-color: var(--accent-primary, #00f0ff);
  background: rgba(0, 240, 255, 0.12);
}

.peer-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.8rem;
  position: relative;
  flex-shrink: 0;
}

.peer-online-led {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #888;
  border: 1px solid #fff;
}

.peer-online-led.playing {
  background: #00aa44;
}

.peer-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}

.peer-header-line {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  line-height: 1.2;
}

.peer-handle {
  font-size: 0.78rem;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag-me {
  background: #f59e0b;
  color: #000;
  font-size: 0.55rem;
  font-weight: 900;
  padding: 1px 3px;
  border-radius: 2px;
}

.peer-playing-status {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.68rem;
  color: #00aa44;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.now-playing-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-eq {
  display: flex;
  gap: 1.5px;
  align-items: flex-end;
  height: 8px;
  flex-shrink: 0;
}

.mini-eq span {
  width: 2px;
  height: 7px;
  background: #00aa44;
  animation: mini-bounce 0.7s infinite alternate ease-in-out;
}

.mini-eq span:nth-child(2) { animation-delay: 0.2s; }
.mini-eq span:nth-child(3) { animation-delay: 0.4s; }

@keyframes mini-bounce {
  0% { height: 2px; }
  100% { height: 8px; }
}

.peer-idle-status {
  font-size: 0.68rem;
  color: var(--text-secondary, #888);
  margin-top: 2px;
}

.peer-badge-count {
  font-size: 0.68rem;
  font-weight: bold;
  color: var(--text-secondary, #777);
  flex-shrink: 0;
}

/* ─── Controls & Tabs ──────────────────────────────────────────────────────── */
.catalog-controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.view-mode-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.catalog-counter {
  font-size: 0.75rem;
  color: var(--text-secondary, #777);
  font-family: monospace;
}

.density-toggles {
  display: flex;
  border: 1px solid var(--border-color, #999);
  border-radius: 4px;
  overflow: hidden;
}

.btn-density {
  background: var(--card-bg, #eee);
  border: none;
  padding: 0.25rem 0.5rem;
  font-size: 0.72rem;
  cursor: pointer;
  color: var(--text-secondary, #555);
}

.btn-density.active {
  background: var(--accent-primary, #000);
  color: #fff;
  font-weight: bold;
}

.active-filter-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.8rem;
  background: rgba(0, 170, 68, 0.08);
  border: 1px dashed #00aa44;
  border-radius: 4px;
  font-size: 0.78rem;
}

.btn-clear-curator-filter {
  background: none;
  border: 1px solid #00aa44;
  color: #00aa44;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.72rem;
}

/* ─── DENSE LIST VIEW ──────────────────────────────────────────────────────── */
.dense-catalog-container {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.dense-row-wrapper {
  background: var(--card-bg, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.15s ease;
}

.dense-row-wrapper:hover {
  border-color: var(--accent-primary, #00f0ff);
}

.dense-row-wrapper.expanded {
  border-color: var(--accent-primary, #00f0ff);
  background: var(--card-bg, #fff);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dense-playlist-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  gap: 0.75rem;
  cursor: pointer;
}

.col-title-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1.8;
  min-width: 0;
}

.expand-caret {
  font-size: 0.65rem;
  color: var(--accent-primary, #00f0ff);
  width: 12px;
}

.title-meta-wrap {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.dense-playlist-title {
  font-weight: bold;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary, inherit);
}

.dense-yt-url {
  font-size: 0.68rem;
  color: var(--text-secondary, #888);
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-curator-section {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex: 0.9;
  min-width: 0;
  cursor: pointer;
}

.col-curator-section:hover .dense-curator-name {
  text-decoration: underline;
  color: var(--accent-primary, #00aa44);
}

.dense-curator-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.65rem;
  flex-shrink: 0;
}

.dense-curator-name {
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-stats-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.dense-stat-chip {
  font-size: 0.72rem;
  font-family: monospace;
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color, #ccc);
}

.dense-stat-chip.dl {
  color: #00aa44;
  font-weight: bold;
}

.dense-date {
  font-size: 0.7rem;
  color: var(--text-secondary, #888);
  font-family: monospace;
}

.col-actions-section {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}

.btn-icon-dense {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-download-dense {
  font-size: 0.75rem;
  padding: 0.25rem 0.65rem;
}

/* ─── Inline Tracks Accordion ──────────────────────────────────────────────── */
.dense-inline-tracks {
  border-top: 1px dashed var(--border-color, #ccc);
  padding: 0.75rem;
  background: rgba(0, 0, 0, 0.02);
}

.tracks-inner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
}

.tracks-table-wrap {
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 4px;
}

.tracks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.tracks-table th {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.35rem 0.5rem;
  text-align: left;
  font-size: 0.68rem;
  border-bottom: 1px solid var(--border-color, #ccc);
}

.tracks-table td {
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.tracks-table tr:hover {
  background: rgba(0, 0, 0, 0.03);
}

.idx-col {
  color: #888;
  font-family: monospace;
}

.uploader-col {
  color: var(--text-secondary, #666);
}

.dur-col {
  font-family: monospace;
  color: #888;
  text-align: right;
}

/* ─── GRID VIEW ────────────────────────────────────────────────────────────── */
.grid-catalog-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.85rem;
}

.retro-card-item {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #ccc);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.retro-card-item:hover {
  border-color: var(--accent-primary, #00f0ff);
}

.card-top-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.curator-badge-clean {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  cursor: pointer;
}

.curator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.curator-name-label {
  font-size: 0.75rem;
  font-weight: bold;
}

.card-counts {
  display: flex;
  gap: 0.3rem;
}

.card-tag {
  font-size: 0.68rem;
  padding: 1px 4px;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.05);
  font-family: monospace;
}

.card-tag.dl {
  color: #00aa44;
  font-weight: bold;
}

.card-main-content {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex-grow: 1;
}

.card-title {
  font-size: 0.9rem;
  font-weight: bold;
  margin: 0;
  line-height: 1.3;
}

.card-date-line {
  font-size: 0.68rem;
  color: var(--text-secondary, #888);
}

.card-url-bar {
  font-size: 0.68rem;
  font-family: monospace;
  color: var(--text-secondary, #777);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: rgba(0, 0, 0, 0.04);
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.card-songs-snippet {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
  padding: 0.4rem;
  font-size: 0.7rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.snippet-row {
  display: flex;
  gap: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.snippet-num {
  color: #888;
}

.snippet-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

.snippet-more {
  font-size: 0.65rem;
  color: var(--accent-primary, #00aa44);
  font-style: italic;
  text-align: center;
}

.card-action-bar {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.6rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, #eee);
}

.btn-dl-card {
  flex: 1;
}

/* ─── Modals ───────────────────────────────────────────────────────────────── */
.plaza-modal-compact {
  max-width: 440px;
  width: 90%;
}

.modal-form-body {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 0.75rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.72rem;
  font-family: var(--font-retro, monospace);
}

.alias-action-row {
  display: flex;
  gap: 0.5rem;
}

.clean-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  cursor: pointer;
}

.relays-info-box {
  background: rgba(0, 0, 0, 0.04);
  padding: 0.6rem;
  border-radius: 4px;
  border: 1px solid var(--border-color, #ddd);
}

.relays-info-title {
  font-size: 0.68rem;
  font-family: monospace;
  font-weight: bold;
  display: block;
  margin-bottom: 0.3rem;
}

.relay-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.7rem;
  color: #00aa44;
}

.relay-led {
  font-size: 0.55rem;
}

.modal-button-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

/* ─── Empty State ──────────────────────────────────────────────────────────── */
.catalog-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  gap: 0.6rem;
  border: 1px dashed var(--border-color, #ccc);
  border-radius: 6px;
  text-align: center;
}

.empty-cassette-icon {
  font-size: 2.5rem;
}
</style>
