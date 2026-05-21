<template>
  <div class="panel">
    <div class="input-group">
      <label>YouTube URL</label>
      <input type="text" v-model="url" placeholder="https://youtube.com/...">
    </div>
    <div class="input-group">
      <label>Carpeta</label>
      <input type="text" v-model="folder" placeholder="Mi Música">
    </div>
    <button class="primary" @click="analyze" :disabled="isAnalyzing">
      {{ isAnalyzing ? 'Analizando...' : 'Analizar Playlist' }}
    </button>

    <div v-if="playlist" class="results-container" style="margin-top: 24px;">
      <h3 style="margin-bottom: 8px;">{{ playlist.title }} ({{ playlist.count }} canciones)</h3>
      <button class="primary" @click="download" style="margin-bottom: 16px;">Descargar Todo</button>
      <div class="song-list">
        <div v-for="song in playlist.songs" :key="song.id" class="song-item" :class="{ downloading: song.status === 'downloading', finished: song.status === 'finished' }">
          <img :src="song.thumbnail || defaultThumb" class="song-thumb">
          <div class="song-info">
            <div class="song-title">{{ song.title }}</div>
            <div class="song-artist">{{ song.uploader || 'Desconocido' }}</div>
          </div>
          <div class="song-progress-bar" :style="{ width: song.percent + '%' }"></div>
          <div class="song-status">{{ song.statusText || 'Esperando...' }}</div>
        </div>
      </div>
    </div>
    
    <!-- Quick Play Section -->
     <div style="margin-top: 40px;">
        <h3 style="margin-bottom: 16px; opacity: 0.8;">Juego Rápido (Biblioteca)</h3>
        <div class="cartridge-grid">
            <div v-for="(song, index) in quickPlaySongs" 
                 :key="index" 
                 class="cartridge-item" 
                 @click="playCartridge(song, index)"
                 @mouseenter="startPreview(song)"
                 @mouseleave="stopPreview"
                 @contextmenu.prevent="showContextMenu($event, song)">
                <div class="cartridge-label">
                    <img :src="getThumbnail(song)" :alt="song.title">
                    <div class="cartridge-overlay">
                        <div class="cartridge-play-btn">▶</div>
                    </div>
                    <button class="cartridge-queue-btn" @click.stop="addToQueue(song)" title="Agregar a la cola">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
                    <div v-if="previewingSong === song" class="preview-indicator">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
                        </svg>
                    </div>
                </div>
                <div style="font-size: 10px; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; font-weight: bold; opacity: 0.7;">
                    {{ song.title }}
                </div>
            </div>
             <div v-if="quickPlaySongs.length === 0" style="padding: 20px; text-align: center; color: #999;">
                {{ loadingQuickPlay ? 'Cargando...' : 'No hay canciones en la biblioteca aún' }}
            </div>
        </div>
        <audio ref="previewAudio" crossorigin="anonymous" style="display: none;"></audio>
    </div>
    
    <!-- Context Menu -->
    <div v-if="contextMenu.show" 
         class="context-menu" 
         :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
         @click="hideContextMenu">
        <div class="context-menu-item" @click="addToQueue(contextMenu.song)">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Agregar a la cola
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from 'vue'

const url = ref('')
const folder = ref('')
const isAnalyzing = ref(false)
const playlist = ref(null)
const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23e5e7eb' width='48' height='48'/%3E%3C/svg%3E"
let pollInterval = null

const quickPlaySongs = ref([])
const loadingQuickPlay = ref(false)
const previewAudio = ref(null)
const previewingSong = ref(null)
const previewTimeout = ref(null)
const contextMenu = ref({ show: false, x: 0, y: 0, song: null })
const emit = defineEmits(['download-start', 'play-cartridge', 'add-to-queue'])

const loadQuickPlay = async () => {
    loadingQuickPlay.value = true
    try {
        const response = await fetch('http://localhost:5001/api/library/random');
        if (response.ok) {
            quickPlaySongs.value = await response.json();
        }
    } catch (e) {
        console.error("Error loading quick play:", e);
    } finally {
        loadingQuickPlay.value = false
    }
}

const getThumbnail = (song) => {
    if (song.thumbnail) return 'http://localhost:5001' + song.thumbnail
    // Deterministic random cover
    const hash = song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const coverNum = (hash % 9) + 1;
    return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const playCartridge = (song, index) => {
    emit('play-cartridge', { song, index, list: quickPlaySongs.value })
}

const startPreview = (song) => {
    if (!previewAudio.value || !song) return
    
    // Clear any existing timeout
    if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
    }
    
    // Set a small delay before starting preview (500ms)
    previewTimeout.value = setTimeout(() => {
        try {
            // Determine the audio source URL
            let audioUrl = ''
            if (song.url) {
                audioUrl = song.url
            } else if (song.path) {
                audioUrl = 'http://localhost:5001' + song.path
            } else if (song.filename) {
                audioUrl = `http://localhost:5001/api/stream/${encodeURIComponent(song.filename)}`
            }
            
            console.log('Starting preview for:', song.title, 'URL:', audioUrl)
            
            if (audioUrl) {
                const audio = previewAudio.value
                
                // Clean up any previous event listeners
                audio.onloadeddata = null
                audio.onerror = null
                
                // Set up event listener for when audio is ready
                audio.onloadeddata = () => {
                    console.log('Audio loaded, starting playback')
                    audio.play().catch(err => {
                        console.error('Preview playback error:', err)
                    })
                }
                
                audio.onerror = (e) => {
                    console.error('Audio loading error:', e)
                }
                
                audio.src = audioUrl
                audio.volume = 0.3 // Lower volume for preview
                audio.load()
                
                previewingSong.value = song
                
                // Auto-stop after 30 seconds of preview
                setTimeout(() => {
                    if (previewingSong.value === song) {
                        stopPreview()
                    }
                }, 30000)
            }
        } catch (error) {
            console.error('Error starting preview:', error)
        }
    }, 200) // Reduced delay
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

const showContextMenu = (event, song) => {
    contextMenu.value = {
        show: true,
        x: event.clientX,
        y: event.clientY,
        song: song
    }
}

const hideContextMenu = () => {
    contextMenu.value.show = false
}

const addToQueue = (song) => {
    emit('add-to-queue', song)
    hideContextMenu()
}

onMounted(() => {
    loadQuickPlay()
})


const analyze = async () => {
  if (!url.value) return
  isAnalyzing.value = true
  try {
    const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.value })
    });
    const data = await response.json();
    // Add status fields to songs
    data.songs = data.songs.map(s => ({ ...s, status: 'waiting', percent: 0, statusText: 'Esperando...' }))
    playlist.value = data
    if (!folder.value && data.title) {
        folder.value = data.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    }
  } catch (e) {
    alert('Error: ' + e.message)
  } finally {
    isAnalyzing.value = false
  }
}

const download = async () => {
    if (!playlist.value) return;
    try {
        await fetch('http://localhost:5001/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url.value,
                folder_name: folder.value,
                selected_ids: playlist.value.songs.map(s => s.id)
            })
        });
        
        // Start polling
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(updateDownloadProgress, 1000);
        
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

const updateDownloadProgress = async () => {
    try {
        const res = await fetch('http://localhost:5001/api/status');
        const statusMap = await res.json();
        
        if (playlist.value && playlist.value.songs) {
            playlist.value.songs.forEach(song => {
                const status = statusMap[song.id];
                if (status) {
                    if (status.status === 'downloading') {
                        song.percent = status.percent;
                        song.statusText = Math.round(status.percent) + '%';
                        song.status = 'downloading';
                    } else if (status.status === 'finished') {
                        song.percent = 100;
                        song.statusText = '✓ Listo';
                        song.status = 'finished';
                    }
                }
            });
        }
    } catch (e) {
        console.error("Polling error:", e);
    }
}

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
    stopPreview()
})
</script>

<style scoped>
.cartridge-item {
    position: relative;
}

.preview-indicator {
    position: absolute;
    top: 8px;
    right: 8px;
    color: #00A8E1;
    background: rgba(0, 0, 0, 0.7);
    border-radius: 50%;
    padding: 4px;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.context-menu {
    position: fixed;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 180px;
    padding: 4px 0;
}

.context-menu-item {
    padding: 10px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    transition: background 0.2s;
}

.context-menu-item:hover {
    background: #f5f5f5;
}

.context-menu-item svg {
    color: #00A8E1;
}

.cartridge-queue-btn {
    position: absolute;
    top: 8px;
    left: 8px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.6);
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    transition: all 0.2s;
    z-index: 10;
}

.cartridge-item:hover .cartridge-queue-btn {
    opacity: 1;
}

.cartridge-queue-btn:hover {
    background: #00A8E1;
    transform: scale(1.1);
}
</style>
