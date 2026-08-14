<template>
  <div v-if="isOpen" class="retro-modal-overlay" @click="close">
    <div class="retro-modal-box search-modal" @click.stop>
      <!-- Search Header -->
      <div class="search-header">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            ref="searchInput"
            v-model="query" 
            type="text" 
            class="global-search-input" 
            placeholder="Buscar por canción, artista, carpeta o playlist..."
            @keydown.down.prevent="navigateResults(1)"
            @keydown.up.prevent="navigateResults(-1)"
            @keydown.enter.prevent="selectHighlighted"
            @keydown.esc.prevent="close"
          />
          <button v-if="query" class="clear-search-btn" @click="query = ''">✕</button>
        </div>
        <button class="btn-retro-icon" @click="close" title="Cerrar (Esc)">✕</button>
      </div>

      <!-- Filter Categories -->
      <div class="search-category-tabs">
        <button 
          class="cat-tab" 
          :class="{ active: activeCategory === 'all' }"
          @click="activeCategory = 'all'"
        >
          Todo ({{ filteredItems.length }})
        </button>
        <button 
          class="cat-tab" 
          :class="{ active: activeCategory === 'songs' }"
          @click="activeCategory = 'songs'"
        >
          Canciones ({{ songCount }})
        </button>
        <button 
          class="cat-tab" 
          :class="{ active: activeCategory === 'artists' }"
          @click="activeCategory = 'artists'"
        >
          Artistas ({{ artistCount }})
        </button>
        <button 
          class="cat-tab" 
          :class="{ active: activeCategory === 'folders' }"
          @click="activeCategory = 'folders'"
        >
          Carpetas ({{ folderCount }})
        </button>
      </div>

      <!-- Search Results List -->
      <div class="search-results-list" ref="resultsList">
        <div v-if="filteredItems.length === 0" class="empty-search-state">
          <div class="empty-icon">📻</div>
          <p v-if="query">No se encontraron resultados para "{{ query }}"</p>
          <p v-else>Escribe algo para buscar en tu archivo musical...</p>
        </div>

        <div 
          v-else 
          v-for="(item, idx) in displayedItems" 
          :key="item.id || item.path || idx"
          class="search-result-row"
          :class="{ 'highlighted': idx === selectedIndex }"
          @mouseenter="selectedIndex = idx"
          @click="handleSelect(item)"
        >
          <!-- Thumbnail / Icon -->
          <div class="item-thumb-wrapper">
            <img v-if="item.thumbnail" :src="item.thumbnail" class="result-thumb" />
            <div v-else class="result-thumb-placeholder">
              {{ item.type === 'folder' ? '📁' : item.type === 'artist' ? '👤' : '🎵' }}
            </div>
          </div>

          <!-- Info -->
          <div class="result-main-info">
            <div class="result-title">{{ item.title || item.name }}</div>
            <div class="result-subtitle">
              <span v-if="item.type === 'folder'" class="badge-retro info pixel">CARPETA</span>
              <span v-else-if="item.type === 'artist'" class="badge-retro warning pixel">ARTISTA</span>
              <span v-else class="badge-retro neutral pixel">{{ item.ext || 'AUDIO' }}</span>
              <span class="sub-text">{{ item.uploader || item.folder || (item.song_count ? `${item.song_count} canciones` : '') }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="result-actions">
            <button 
              v-if="item.type !== 'folder' && item.type !== 'artist'"
              class="btn-retro-secondary btn-sm"
              @click.stop="$emit('add-to-queue', item)"
              title="Agregar a la cola"
            >
              ＋ Cola
            </button>
            <button class="btn-retro-primary btn-sm" @click.stop="handleSelect(item)">
              {{ item.type === 'folder' ? 'Abrir' : 'Reproducir' }} ▶
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Hints -->
      <div class="search-footer-hints">
        <span><kbd>↑</kbd><kbd>↓</kbd> Navegar</span>
        <span><kbd>Enter</kbd> Seleccionar</span>
        <span><kbd>Esc</kbd> Cerrar</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  allSongs: { type: Array, default: () => [] },
  folders: { type: Array, default: () => [] },
  playlists: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'play-song', 'open-folder', 'add-to-queue'])

const query = ref('')
const activeCategory = ref('all')
const selectedIndex = ref(0)
const searchInput = ref(null)
const resultsList = ref(null)

// Focus search input on open
watch(() => props.isOpen, (open) => {
  if (open) {
    query.value = ''
    selectedIndex.value = 0
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})

// Build indexed search items
const allSearchItems = computed(() => {
  const list = []

  // Add folders
  props.folders.forEach(f => {
    list.push({
      type: 'folder',
      id: `folder-${f.name}`,
      name: f.name,
      title: f.name,
      thumbnail: f.thumbnail,
      song_count: f.song_count
    })
  })

  // Extract unique artists
  const artistsMap = new Map()
  props.allSongs.forEach(s => {
    if (s.uploader && s.uploader !== 'Desconocido') {
      artistsMap.set(s.uploader, (artistsMap.get(s.uploader) || 0) + 1)
    }
  })
  artistsMap.forEach((count, artistName) => {
    list.push({
      type: 'artist',
      id: `artist-${artistName}`,
      name: artistName,
      title: artistName,
      uploader: `${count} canciones`
    })
  })

  // Add songs
  props.allSongs.forEach(s => {
    list.push({
      ...s,
      type: 'song',
      id: s.path || s.filename
    })
  })

  return list
})

const filteredItems = computed(() => {
  const q = query.value.trim().toLowerCase()
  let items = allSearchItems.value

  if (q) {
    items = items.filter(item => {
      const matchTitle = (item.title || item.name || '').toLowerCase().includes(q)
      const matchArtist = (item.uploader || '').toLowerCase().includes(q)
      const matchFolder = (item.folder || '').toLowerCase().includes(q)
      return matchTitle || matchArtist || matchFolder
    })
  }

  if (activeCategory.value === 'songs') {
    return items.filter(i => i.type === 'song')
  } else if (activeCategory.value === 'artists') {
    return items.filter(i => i.type === 'artist')
  } else if (activeCategory.value === 'folders') {
    return items.filter(i => i.type === 'folder')
  }

  return items
})

const songCount = computed(() => allSearchItems.value.filter(i => i.type === 'song').length)
const artistCount = computed(() => allSearchItems.value.filter(i => i.type === 'artist').length)
const folderCount = computed(() => allSearchItems.value.filter(i => i.type === 'folder').length)

const displayedItems = computed(() => filteredItems.value.slice(0, 100))

const navigateResults = (direction) => {
  const max = displayedItems.value.length - 1
  if (max < 0) return
  selectedIndex.value = Math.max(0, Math.min(max, selectedIndex.value + direction))
  
  // Auto scroll highlighted into view
  nextTick(() => {
    const el = resultsList.value?.children[selectedIndex.value]
    if (el) {
      el.scrollIntoView({ block: 'nearest' })
    }
  })
}

const selectHighlighted = () => {
  if (displayedItems.value[selectedIndex.value]) {
    handleSelect(displayedItems.value[selectedIndex.value])
  }
}

const handleSelect = (item) => {
  if (item.type === 'folder') {
    emit('open-folder', item.name)
    close()
  } else if (item.type === 'artist') {
    query.value = item.name
    activeCategory.value = 'songs'
  } else {
    emit('play-song', { song: item, list: props.allSongs })
    close()
  }
}

const close = () => {
  emit('close')
}

// Global hotkey handler for Ctrl+K / Cmd+K
const handleGlobalKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault()
    if (props.isOpen) {
      close()
    } else {
      emit('close') // handled in App.vue to toggle
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style scoped>
.search-modal {
  max-width: 680px;
  width: 95%;
  padding: 16px;
  background: #e4e4e4;
  border: 4px solid #000000;
  box-shadow: inset 2px 2px 0px #ffffff, inset -2px -2px 0px #7c7c7c, 10px 10px 0px #000000;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 3px solid #000000;
  padding: 8px 12px;
  box-shadow: inset 2px 2px 0px #666666;
}

.search-icon {
  font-size: 16px;
}

.global-search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  color: #000000;
  outline: none;
}

.clear-search-btn {
  background: none;
  border: none;
  color: #666666;
  font-weight: bold;
  cursor: pointer;
}

.search-category-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  border-bottom: 2px solid #000000;
  padding-bottom: 6px;
}

.cat-tab {
  padding: 4px 10px;
  background: #d4d4d4;
  border: 2px solid #000000;
  font-family: var(--font-pixel);
  font-size: 8px;
  cursor: pointer;
  box-shadow: inset 1px 1px 0px #ffffff;
}

.cat-tab.active {
  background: #0088cc;
  color: #ffffff;
  box-shadow: inset 1px 1px 0px rgba(0, 0, 0, 0.4);
}

.search-results-list {
  max-height: 420px;
  min-height: 200px;
  overflow-y: auto;
  border: 2px solid #000000;
  background: #ffffff;
  box-shadow: inset 1px 1px 0px #333333;
}

.empty-search-state {
  padding: 40px 20px;
  text-align: center;
  color: #666666;
  font-family: var(--font-mono);
  font-size: 12px;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.search-result-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-bottom: 1px solid #eeeeee;
  cursor: pointer;
  transition: background 0.05s ease;
}

.search-result-row:hover,
.search-result-row.highlighted {
  background: #e0f2fe;
}

.search-result-row.highlighted {
  border-left: 4px solid #0088cc;
}

.item-thumb-wrapper {
  width: 36px;
  height: 36px;
  border: 1.5px solid #000000;
  background: #222222;
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.result-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-thumb-placeholder {
  font-size: 16px;
}

.result-main-info {
  flex: 1;
  min-width: 0;
}

.result-title {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 12px;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-subtitle {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: #666666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sub-text {
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 8px;
}

.search-footer-hints {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: #555555;
}

kbd {
  background: #ffffff;
  border: 1.5px solid #000000;
  padding: 1px 4px;
  border-radius: 2px;
  box-shadow: 1px 1px 0px #000000;
  font-weight: bold;
  margin-right: 2px;
}
</style>
